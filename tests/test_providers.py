import base64
import json
from types import SimpleNamespace

import anthropic
import httpx
import pytest

from kira.ai.anthropic_provider import FALLBACK_BETA, AnthropicProvider
from kira.ai.base import ChatMessage, ChatRequest, ImageInput, ProviderError, ProviderUnavailable
from kira.ai.ollama_provider import OllamaProvider
from kira.core.config import CloudAISettings, LocalAISettings


def make_request(images=(), complex_task=False):
    return ChatRequest(
        system="sistem",
        messages=(ChatMessage("user", "selam"), ChatMessage("assistant", "merhaba"),
                  ChatMessage("user", "bu ne?", images=images)),
        complex_task=complex_task,
    )


# ---- Ollama ----
def ollama_with(handler):
    client = httpx.Client(transport=httpx.MockTransport(handler), base_url="http://ollama")
    settings = LocalAISettings(chat_model="qwen2.5:7b", vision_model="qwen2.5vl:7b")
    return OllamaProvider(settings, client=client)


def test_ollama_text_and_vision_model_selection():
    seen = []

    def handler(request):
        body = json.loads(request.content)
        seen.append(body)
        return httpx.Response(200, json={"message": {"content": " Merhaba! "}, "done_reason": "stop"})

    p = ollama_with(handler)
    r = p.chat(make_request())
    assert r.text == "Merhaba!" and r.engine == "local:qwen2.5:7b"
    assert seen[0]["messages"][0] == {"role": "system", "content": "sistem"}
    p.chat(make_request(images=(ImageInput(b"\xff\xd8jpeg"),)))
    assert seen[1]["model"] == "qwen2.5vl:7b"
    assert seen[1]["messages"][-1]["images"] == [base64.b64encode(b"\xff\xd8jpeg").decode()]


def test_ollama_missing_model_and_down():
    p = ollama_with(lambda r: httpx.Response(404, json={"error": "model not found"}))
    with pytest.raises(ProviderUnavailable):
        p.chat(make_request())

    def down(request):
        raise httpx.ConnectError("refused")

    p = ollama_with(down)
    assert not p.available()
    with pytest.raises(ProviderUnavailable):
        p.chat(make_request())


# ---- Anthropic (ağ çağrısı yok, sahte istemci) ----
class FakeMessages:
    def __init__(self, response=None, error=None):
        self.response, self.error, self.kwargs = response, error, None

    def create(self, **kwargs):
        self.kwargs = kwargs
        if self.error:
            raise self.error
        return self.response


def fake_client(messages):
    return SimpleNamespace(beta=SimpleNamespace(messages=messages))


def ok_response(text="Selam!", stop="end_turn"):
    return SimpleNamespace(
        content=[SimpleNamespace(type="thinking", thinking=""), SimpleNamespace(type="text", text=text)],
        stop_reason=stop,
        model="claude-opus-5-5",
    )


def test_anthropic_request_shape():
    msgs = FakeMessages(ok_response())
    p = AnthropicProvider(CloudAISettings(), client=fake_client(msgs))
    r = p.chat(make_request(images=(ImageInput(b"img", "image/png"),)))
    assert r.text == "Selam!" and r.engine == "cloud:claude-opus-5-5"
    kw = msgs.kwargs
    assert kw["model"] == "claude-opus-5-5"
    assert kw["system"] == "sistem"
    assert kw["output_config"] == {"effort": "low"}
    assert kw["betas"] == [FALLBACK_BETA] and kw["fallbacks"] == "default"
    last = kw["messages"][-1]["content"]
    assert last[0]["type"] == "image" and last[0]["source"]["media_type"] == "image/png"
    assert last[1] == {"type": "text", "text": "bu ne?"}


def test_anthropic_complex_effort_and_refusal():
    msgs = FakeMessages(ok_response(stop="refusal", text=""))
    p = AnthropicProvider(CloudAISettings(), client=fake_client(msgs))
    with pytest.raises(ProviderError):
        p.chat(make_request(complex_task=True))
    assert msgs.kwargs["output_config"] == {"effort": "high"}


def test_anthropic_connection_error_is_unavailable():
    req = httpx.Request("POST", "https://api.anthropic.com/v1/messages")
    msgs = FakeMessages(error=anthropic.APIConnectionError(request=req))
    p = AnthropicProvider(CloudAISettings(), client=fake_client(msgs))
    with pytest.raises(ProviderUnavailable):
        p.chat(make_request())


def test_anthropic_without_key(monkeypatch):
    monkeypatch.setattr("kira.ai.anthropic_provider.get_secret", lambda name: None)
    p = AnthropicProvider(CloudAISettings())
    assert not p.available()
    with pytest.raises(ProviderUnavailable):
        p.chat(make_request())


def test_anthropic_real_sdk_serialization():
    """Gerçek SDK ile istek gövdesini ve cevap ayrıştırmayı doğrular (ağ yok, sahte transport)."""
    captured = {}

    def handler(request):
        captured["body"] = json.loads(request.content)
        captured["beta"] = request.headers.get("anthropic-beta")
        return httpx.Response(200, json={
            "id": "msg_1", "type": "message", "role": "assistant", "model": "claude-opus-5-5",
            "content": [{"type": "text", "text": "Merhaba!"}],
            "stop_reason": "end_turn", "stop_sequence": None,
            "usage": {"input_tokens": 10, "output_tokens": 3},
        })

    httpx2 = pytest.importorskip("httpx2")  # anthropic SDK 2.x httpx2 kullanır
    client = anthropic.Anthropic(
        api_key="test",
        http_client=httpx2.Client(transport=httpx2.MockTransport(lambda r: _to_httpx2(httpx2, handler(r)))),
    )
    r = AnthropicProvider(CloudAISettings(), client=client).chat(make_request())
    assert r.text == "Merhaba!"
    assert captured["body"]["fallbacks"] == "default"
    assert captured["body"]["output_config"] == {"effort": "low"}
    assert FALLBACK_BETA in captured["beta"]


def _to_httpx2(httpx2, resp):
    return httpx2.Response(resp.status_code, content=resp.content, headers=dict(resp.headers))


def test_robot_default_has_no_vision_and_pc_label():
    from kira.core.config import PCAISettings
    p = OllamaProvider(LocalAISettings())
    assert p.supports_images is False and p.name == "local:qwen2.5:3b"
    pc = OllamaProvider(PCAISettings(), label="pc")
    assert pc.supports_images and pc.name.startswith("pc:")
