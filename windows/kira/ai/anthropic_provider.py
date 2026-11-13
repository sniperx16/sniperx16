"""Bulut AI: Anthropic Claude (Messages API, resmi `anthropic` SDK).

- Model ve efor ayarlardan gelir (varsayılan claude-opus-5-5; sohbet için
  düşük efor = hızlı cevap, karmaşık görevlerde yüksek efor).
- Sunucu tarafı yedek model (server-side fallback) açıktır: model bir isteği
  güvenlik nedeniyle reddederse API aynı isteği uygun bir modelle tekrar dener.
- Anahtar Windows Kimlik Bilgisi Yöneticisi'nden okunur.
"""

from __future__ import annotations

import base64

import anthropic

from kira.ai.base import ChatRequest, ChatResponse, ProviderError, ProviderUnavailable
from kira.core.config import CloudAISettings
from kira.security.secrets import get_secret

FALLBACK_BETA = "server-side-fallback-2026-07-01"


class AnthropicProvider:
    is_local = False
    supports_images = True

    def __init__(self, settings: CloudAISettings, client: anthropic.Anthropic | None = None):
        self.settings = settings
        self.name = f"cloud:{settings.model}"
        self._client = client

    def _get_client(self) -> anthropic.Anthropic:
        if self._client is None:
            key = get_secret("anthropic")
            if not key:
                raise ProviderUnavailable(
                    "Anthropic API anahtarı yok. `python -m kira key set anthropic` ile ekleyin.",
                    retryable=False,
                )
            self._client = anthropic.Anthropic(api_key=key, max_retries=2, timeout=120.0)
        return self._client

    def available(self) -> bool:
        if not self.settings.enabled:
            return False
        return self._client is not None or bool(get_secret("anthropic"))

    @staticmethod
    def _to_api_messages(request: ChatRequest) -> list[dict]:
        out: list[dict] = []
        for m in request.messages:
            if m.images:
                content: list[dict] = [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": img.media_type,
                            "data": base64.standard_b64encode(img.data).decode("ascii"),
                        },
                    }
                    for img in m.images
                ]
                content.append({"type": "text", "text": m.content})
                out.append({"role": m.role, "content": content})
            else:
                out.append({"role": m.role, "content": m.content})
        return out

    def chat(self, request: ChatRequest) -> ChatResponse:
        client = self._get_client()
        effort = self.settings.complex_effort if request.complex_task else self.settings.chat_effort
        try:
            response = client.beta.messages.create(
                model=self.settings.model,
                max_tokens=self.settings.max_tokens,
                system=request.system,
                messages=self._to_api_messages(request),
                output_config={"effort": effort},
                betas=[FALLBACK_BETA],
                fallbacks="default",
            )
        except anthropic.AuthenticationError as exc:
            raise ProviderUnavailable("Anthropic API anahtarı geçersiz", retryable=False) from exc
        except anthropic.PermissionDeniedError as exc:
            raise ProviderError("Anthropic anahtarının bu modele izni yok", retryable=False) from exc
        except anthropic.NotFoundError as exc:
            raise ProviderError(f"Model bulunamadı: {self.settings.model}", retryable=False) from exc
        except anthropic.BadRequestError as exc:
            raise ProviderError(f"Geçersiz istek: {exc.message}", retryable=False) from exc
        except anthropic.RateLimitError as exc:
            raise ProviderError("Bulut AI kullanım sınırına ulaşıldı, biraz sonra tekrar dene") from exc
        except anthropic.APIStatusError as exc:
            raise ProviderError(f"Bulut AI sunucu hatası ({exc.status_code})") from exc
        except anthropic.APIConnectionError as exc:
            raise ProviderUnavailable("Bulut AI'a bağlanılamadı (internet?)") from exc

        if response.stop_reason == "refusal":
            raise ProviderError("Bulut AI bu isteği yanıtlamadı", retryable=False)
        text = "".join(b.text for b in response.content if b.type == "text").strip()
        if not text:
            raise ProviderError("Bulut AI boş cevap döndürdü")
        return ChatResponse(
            text=text,
            engine=f"cloud:{response.model}",
            stop_reason=response.stop_reason,
            meta={"request_id": getattr(response, "_request_id", None)},
        )
