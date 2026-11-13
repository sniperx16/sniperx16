"""Hibrit AI yönlendirici.

Sıra:
1. Kural tabanlı hızlı komutlar (AI çağrısı yok): saat, tarih, hatırla, unut,
   hafızayı göster, kamera/ses komutları.
2. Basit sohbet -> yerel AI (Ollama). Yerel yoksa bulut.
3. Karmaşık soru / uzun görev -> bulut AI. Bulut yoksa (internet kesik vb.)
   yerel AI ile devam edilir ve kullanıcıya söylenir.
4. Görüntülü soru -> yerel görsel model; ayarlarda izin verilmişse ve
   detay isteniyorsa bulut.
"""

from __future__ import annotations

import re
import socket
import time
from dataclasses import dataclass
from enum import Enum

from kira.ai.base import ChatProvider, ChatRequest, ChatResponse, ProviderError, ProviderUnavailable
from kira.security.sensitive import tr_lower


class Route(str, Enum):
    RULE = "rule"
    LOCAL = "local"
    CLOUD = "cloud"


@dataclass(frozen=True)
class Intent:
    name: str
    argument: str = ""


# (desen, niyet adı). Desenler küçük harfe çevrilmiş (Türkçe) metne uygulanır.
_INTENT_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"^(?:kira[, ]+)?(?:bunu |şunu )?(?:hatırla|aklında tut|unutma)[:, ]+(?P<arg>.+)$"), "remember"),
    (re.compile(r"^(?:kira[, ]+)?(?P<arg>.+?)[, ]+(?:bunu )?(?:hatırla|aklında tut|unutma)[.!]?$"), "remember"),
    (re.compile(r"^(?:kira[, ]+)?(?P<arg>.+?)[, ]+(?:bilgisini |bunu )?unut[.!]?$"), "forget"),
    (re.compile(r"^(?:kira[, ]+)?unut[:, ]+(?P<arg>.+)$"), "forget"),
    (re.compile(r"(?:hafızanda|hafızanı|neleri? hatırlıyorsun|ne biliyorsun benim hakkımda)"), "list_memory"),
    (re.compile(r"(?:saat kaç|saati söyle)"), "time"),
    (re.compile(r"(?:bugün (?:günlerden ne|ayın kaçı|tarih)|tarih ne|hangi gündeyiz)"), "date"),
    (re.compile(r"kamera(?:yı|y[iı])? (?:kapat|durdur)"), "camera_off"),
    (re.compile(r"kamera(?:yı|y[iı])? (?:aç|başlat)"), "camera_on"),
    (re.compile(r"(?:mikrofon(?:u)? kapat|dinlemeyi (?:bırak|durdur))"), "mic_off"),
    (re.compile(r"ses(?:i)? (?:aç|yükselt|artır)"), "volume_up"),
    (re.compile(r"ses(?:i)? (?:kıs|azalt|düşür)"), "volume_down"),
    (re.compile(r"(?:durumun ne|donanım durumu|sistem durumu|nasıl çalışıyorsun)"), "status"),
]

_COMPLEX_HINTS = (
    "analiz et", "karşılaştır", "detaylı", "ayrıntılı", "adım adım", "plan hazırla", "planla",
    "kod yaz", "hata ayıkla", "debug", "rapor", "özetle", "makale", "neden", "araştır",
    "hesapla", "strateji", "değerlendir", "çevir",
)


def detect_intent(text: str) -> Intent | None:
    low = tr_lower(text.strip())
    for pattern, name in _INTENT_PATTERNS:
        m = pattern.search(low)
        if m:
            arg = m.groupdict().get("arg") or ""
            if arg:
                # Orijinal yazımı koru (büyük harf, özel adlar)
                start, end = m.span("arg")
                arg = text.strip()[start:end]
            return Intent(name, arg.strip(" .,!"))
    return None


def is_complex(text: str, *, has_images: bool = False) -> bool:
    low = tr_lower(text)
    if any(h in low for h in _COMPLEX_HINTS):
        return True
    words = len(low.split())
    return words > 40 or (has_images and any(w in low for w in ("detay", "ayrıntı", "oku", "yazıyı")))


class Connectivity:
    """İnternet kontrolü (sonuç kısa süre önbelleğe alınır)."""

    def __init__(self, host: str = "api.anthropic.com", port: int = 443, ttl_s: float = 20.0):
        self.host, self.port, self.ttl_s = host, port, ttl_s
        self._cache: tuple[float, bool] | None = None

    def online(self) -> bool:
        now = time.monotonic()
        if self._cache and now - self._cache[0] < self.ttl_s:
            return self._cache[1]
        try:
            with socket.create_connection((self.host, self.port), timeout=2.0):
                ok = True
        except OSError:
            ok = False
        self._cache = (now, ok)
        return ok

    def mark_offline(self) -> None:
        self._cache = (time.monotonic(), False)


@dataclass(frozen=True)
class RoutedResponse:
    response: ChatResponse
    route: Route
    fell_back: bool = False
    note: str = ""


class NoEngineAvailable(Exception):
    pass


class HybridRouter:
    def __init__(
        self,
        local: ChatProvider | None,
        cloud: ChatProvider | None,
        connectivity: Connectivity | None = None,
        *,
        allow_cloud_images: bool = False,
    ):
        self.local = local
        self.cloud = cloud
        self.connectivity = connectivity or Connectivity()
        self.allow_cloud_images = allow_cloud_images

    def _cloud_ok(self, request: ChatRequest) -> bool:
        if self.cloud is None or not self.cloud.available():
            return False
        if any(m.images for m in request.messages) and not self.allow_cloud_images:
            return False
        return self.connectivity.online()

    def _local_ok(self) -> bool:
        return self.local is not None and self.local.available()

    def choose(self, request: ChatRequest) -> list[tuple[Route, ChatProvider]]:
        """Denenecek sağlayıcıları öncelik sırasıyla döndürür."""
        order: list[tuple[Route, ChatProvider]] = []
        cloud_ok = self._cloud_ok(request)
        local_ok = self._local_ok()
        prefer_cloud = request.complex_task
        if prefer_cloud and cloud_ok:
            order.append((Route.CLOUD, self.cloud))
        if local_ok:
            order.append((Route.LOCAL, self.local))
        if not prefer_cloud and cloud_ok:
            order.append((Route.CLOUD, self.cloud))
        return order

    def _why_unavailable(self, request: ChatRequest) -> str:
        reasons = []
        if self.local is None:
            reasons.append("yerel AI ayarlı değil")
        else:
            reasons.append("yerel AI'a (Ollama) ulaşılamıyor")
        if self.cloud is None:
            reasons.append("bulut AI ayarlı değil")
        elif not self.cloud.available():
            reasons.append("bulut AI kapalı ya da API anahtarı yok")
        elif any(m.images for m in request.messages) and not self.allow_cloud_images:
            reasons.append("görüntülerin buluta gönderilmesine izin verilmemiş")
        else:
            reasons.append("internet bağlantısı yok")
        return "Kullanılabilir AI motoru yok: " + ", ".join(reasons) + "."

    def chat(self, request: ChatRequest) -> RoutedResponse:
        candidates = self.choose(request)
        if not candidates:
            raise NoEngineAvailable(self._why_unavailable(request))
        errors: list[str] = []
        for i, (route, provider) in enumerate(candidates):
            try:
                resp = provider.chat(request)
            except ProviderError as exc:
                errors.append(f"{provider.name}: {exc}")
                if route is Route.CLOUD and isinstance(exc, ProviderUnavailable) and exc.retryable:
                    self.connectivity.mark_offline()
                continue
            fell_back = i > 0 or (request.complex_task and route is Route.LOCAL)
            note = ""
            if fell_back and route is Route.LOCAL and request.complex_task:
                note = "Bulut AI'a ulaşamadım, yerel modelle cevaplıyorum; cevap daha sınırlı olabilir."
            return RoutedResponse(resp, route, fell_back=fell_back, note=note)
        raise NoEngineAvailable("Tüm AI motorları başarısız oldu: " + " | ".join(errors))
