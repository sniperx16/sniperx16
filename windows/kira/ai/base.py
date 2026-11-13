"""AI sağlayıcıları için ortak tipler.

Her sağlayıcı (yerel Ollama, bulut Anthropic, ileride başkaları) aynı
`ChatProvider` arayüzünü uygular; böylece ayarlardan değiştirilebilir.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Protocol, runtime_checkable

Role = Literal["user", "assistant"]


@dataclass(frozen=True)
class ImageInput:
    data: bytes
    media_type: str = "image/jpeg"


@dataclass(frozen=True)
class ChatMessage:
    role: Role
    content: str
    images: tuple[ImageInput, ...] = ()


@dataclass(frozen=True)
class ChatRequest:
    system: str
    messages: tuple[ChatMessage, ...]
    complex_task: bool = False


@dataclass(frozen=True)
class ChatResponse:
    text: str
    engine: str  # "local:<model>" / "cloud:<model>"
    stop_reason: str | None = None
    meta: dict = field(default_factory=dict)


class ProviderError(Exception):
    """Sağlayıcı isteği başarısız oldu."""

    def __init__(self, message: str, *, retryable: bool = True):
        super().__init__(message)
        self.retryable = retryable


class ProviderUnavailable(ProviderError):
    """Sağlayıcıya ulaşılamıyor (servis kapalı, internet yok, anahtar yok)."""


@runtime_checkable
class ChatProvider(Protocol):
    name: str
    is_local: bool
    supports_images: bool

    def available(self) -> bool: ...

    def chat(self, request: ChatRequest) -> ChatResponse: ...
