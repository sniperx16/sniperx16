"""Yerel AI: Ollama (http://127.0.0.1:11434).

İnternet gerektirmez. Görüntülü istekler `vision_model` ile çalışır.
"""

from __future__ import annotations

import base64

import httpx

from kira.ai.base import ChatRequest, ChatResponse, ProviderError, ProviderUnavailable
from kira.core.config import LocalAISettings


class OllamaProvider:
    is_local = True
    supports_images = True

    def __init__(self, settings: LocalAISettings, client: httpx.Client | None = None):
        self.settings = settings
        self.name = f"local:{settings.chat_model}"
        self._client = client or httpx.Client(base_url=settings.base_url, timeout=settings.timeout_s)

    def available(self) -> bool:
        if not self.settings.enabled:
            return False
        try:
            return self._client.get("/api/tags", timeout=2.0).status_code == 200
        except httpx.HTTPError:
            return False

    def installed_models(self) -> list[str]:
        try:
            resp = self._client.get("/api/tags", timeout=5.0)
            resp.raise_for_status()
        except httpx.HTTPError as exc:
            raise ProviderUnavailable(f"Ollama'ya ulaşılamadı: {exc}") from exc
        return [m["name"] for m in resp.json().get("models", [])]

    def chat(self, request: ChatRequest) -> ChatResponse:
        has_images = any(m.images for m in request.messages)
        model = self.settings.vision_model if has_images else self.settings.chat_model
        messages: list[dict] = [{"role": "system", "content": request.system}]
        for m in request.messages:
            item: dict = {"role": m.role, "content": m.content}
            if m.images:
                item["images"] = [base64.b64encode(img.data).decode("ascii") for img in m.images]
            messages.append(item)
        try:
            resp = self._client.post(
                "/api/chat",
                json={"model": model, "messages": messages, "stream": False},
            )
        except httpx.ConnectError as exc:
            raise ProviderUnavailable("Ollama çalışmıyor (127.0.0.1:11434)") from exc
        except httpx.HTTPError as exc:
            raise ProviderError(f"Ollama isteği başarısız: {exc}") from exc
        if resp.status_code == 404:
            raise ProviderUnavailable(
                f"Ollama modeli yüklü değil: {model} (ollama pull {model})", retryable=False
            )
        if resp.status_code >= 400:
            raise ProviderError(f"Ollama hata {resp.status_code}: {resp.text[:200]}")
        data = resp.json()
        text = (data.get("message") or {}).get("content", "").strip()
        if not text:
            raise ProviderError("Ollama boş cevap döndürdü")
        return ChatResponse(text=text, engine=f"local:{model}", stop_reason=data.get("done_reason"))
