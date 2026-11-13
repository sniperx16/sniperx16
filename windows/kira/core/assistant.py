"""KIRA ana akışı: kullanıcı mesajı -> hızlı komut / hafıza / hibrit AI -> cevap.

Ses, kamera ve cihaz bağlantısı sonraki aşamalarda bu sınıfa bağlanacak.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable

from kira.ai.base import ChatMessage, ChatRequest, ImageInput
from kira.ai.router import HybridRouter, Intent, NoEngineAvailable, Route, detect_intent, is_complex
from kira.core.config import Settings
from kira.core.persona import DeviceStatus, build_system_prompt, format_datetime_tr
from kira.memory.store import ConsentRequired, MemoryStore


@dataclass
class Reply:
    text: str
    route: Route
    engine: str = ""
    # Cihaza/ara yüze iletilecek eylem (ör. "camera_off"); bu aşamada yalnızca bildirilir.
    action: str | None = None
    needs_consent: bool = False


@dataclass
class _PendingConsent:
    content: str
    category: str = "genel"


@dataclass
class Assistant:
    settings: Settings
    memory: MemoryStore
    router: HybridRouter
    device_status: Callable[[], DeviceStatus] = field(default=DeviceStatus)
    clock: Callable[[], datetime] = field(default=lambda: datetime.now().astimezone())
    conversation_id: int | None = None
    _pending: _PendingConsent | None = None

    def __post_init__(self) -> None:
        if self.conversation_id is None:
            self.conversation_id = self.memory.start_conversation()

    # ---- genel giriş noktası ----
    def handle(self, text: str, *, images: tuple[ImageInput, ...] = (), source: str = "text") -> Reply:
        text = text.strip()
        if not text and not images:
            return Reply("Seni duyamadım, tekrar söyler misin?", Route.RULE)
        user_msg_id = self.memory.add_message(self.conversation_id, "user", text or "[görüntü]", source=source)

        reply = self._handle_pending_consent(text)
        if reply is None and not images:
            intent = detect_intent(text)
            if intent:
                reply = self._handle_intent(intent, user_msg_id)
        if reply is None:
            reply = self._ask_ai(text, images)

        self.memory.add_message(self.conversation_id, "assistant", reply.text, source=source, engine=reply.engine)
        return reply

    # ---- hassas bilgi onayı ----
    def _handle_pending_consent(self, text: str) -> Reply | None:
        if self._pending is None:
            return None
        pending, self._pending = self._pending, None
        low = text.lower()
        if any(w in low for w in ("evet", "olur", "kaydet", "tamam")):
            self.memory.remember(pending.content, category=pending.category, consent=True)
            return Reply("Tamam, kaydettim. İstediğin zaman sildirebilirsin.", Route.RULE)
        if any(w in low for w in ("hayır", "kaydetme", "istemiyorum", "vazgeç")):
            return Reply("Anlaştık, kaydetmedim.", Route.RULE)
        return None  # konu değişti; onay sorusu düşer

    # ---- hızlı komutlar ----
    def _handle_intent(self, intent: Intent, user_msg_id: int) -> Reply | None:
        now = self.clock()
        if intent.name == "time":
            return Reply(f"Saat {now:%H:%M}.", Route.RULE)
        if intent.name == "date":
            return Reply(f"Bugün {format_datetime_tr(now).split(', saat')[0]}.", Route.RULE)
        if intent.name == "remember" and intent.argument:
            try:
                self.memory.remember(intent.argument, source_message_id=user_msg_id)
            except ConsentRequired as exc:
                self._pending = _PendingConsent(intent.argument)
                return Reply(
                    f"Bu bilgi {exc.result.describe_tr()} içeriyor gibi görünüyor. Yine de hafızama kaydetmemi ister misin?",
                    Route.RULE,
                    needs_consent=True,
                )
            return Reply("Tamam, aklımda.", Route.RULE)
        if intent.name == "forget" and intent.argument:
            removed = self.memory.forget_matching(intent.argument)
            if not removed:
                return Reply("Hafızamda bununla ilgili bir şey bulamadım.", Route.RULE)
            return Reply(f"Tamam, {len(removed)} kaydı sildim.", Route.RULE)
        if intent.name == "list_memory":
            facts = self.memory.list_facts()
            if not facts:
                return Reply("Henüz senin hakkında kaydettiğim bir bilgi yok.", Route.RULE)
            shown = facts[:5]
            summary = "; ".join(f.content for f in shown)
            more = f" Toplam {len(facts)} kayıt var, hepsini kontrol panelinden görebilirsin." if len(facts) > 5 else ""
            return Reply(f"Hatırladıklarımdan bazıları: {summary}.{more}", Route.RULE)
        if intent.name == "status":
            return Reply(self._status_text(), Route.RULE)
        if intent.name in {"camera_on", "camera_off", "mic_off", "volume_up", "volume_down"}:
            if not self.device_status().connected:
                return Reply("Robot gövdem şu an bilgisayara bağlı değil, bu komutu uygulayamıyorum.", Route.RULE)
            labels = {
                "camera_on": "Kamerayı açıyorum.",
                "camera_off": "Kamerayı kapatıyorum.",
                "mic_off": "Mikrofonu kapatıyorum.",
                "volume_up": "Sesi açıyorum.",
                "volume_down": "Sesi kısıyorum.",
            }
            return Reply(labels[intent.name], Route.RULE, action=intent.name)
        return None

    def _status_text(self) -> str:
        dev = self.device_status()
        if not dev.connected:
            return "Şu an sadece bilgisayarda çalışıyorum; robot gövdem bağlı değil, o yüzden kamera, mikrofon ve hoparlörüm kullanılamıyor."
        def st(v, on="çalışıyor", off="çalışmıyor"):
            return "durumu bilinmiyor" if v is None else (on if v else off)
        return (
            f"Gövdem bağlı. Kamera {st(dev.camera_on, 'açık', 'kapalı')}, mikrofon {st(dev.microphone_available)}, "
            f"hoparlör {st(dev.speaker_available)}."
        )

    # ---- AI ----
    def _ask_ai(self, text: str, images: tuple[ImageInput, ...]) -> Reply:
        mem = self.settings.memory
        facts = self.memory.search_facts(text, limit=mem.max_context_facts) if text else []
        history = self.memory.recent_messages(self.conversation_id, limit=mem.max_history_messages + 1)
        # Son kullanıcı mesajı zaten history'nin sonunda; görüntü eklemek için yeniden kuruyoruz.
        msgs = [ChatMessage(m.role, m.content) for m in history[:-1]]
        msgs = _normalize_turns(msgs)
        msgs.append(ChatMessage("user", text or "Bu görüntüde ne var?", images=images))
        request = ChatRequest(
            system=build_system_prompt(
                now=self.clock(), device=self.device_status(), facts=facts, user_name=self.settings.user_name
            ),
            messages=tuple(msgs),
            complex_task=is_complex(text, has_images=bool(images)),
        )
        try:
            routed = self.router.chat(request)
        except NoEngineAvailable as exc:
            return Reply(f"Şu an düşünemiyorum: {exc}", Route.RULE)
        text_out = routed.response.text
        if routed.note:
            text_out = f"{routed.note} {text_out}"
        return Reply(text_out, routed.route, engine=routed.response.engine)


def _normalize_turns(msgs: list[ChatMessage]) -> list[ChatMessage]:
    """API'ler için: ilk mesaj kullanıcıdan olmalı, ardışık aynı roller birleştirilir."""
    out: list[ChatMessage] = []
    for m in msgs:
        if not out and m.role != "user":
            continue
        if out and out[-1].role == m.role:
            out[-1] = ChatMessage(m.role, out[-1].content + "\n" + m.content)
        else:
            out.append(m)
    # Cevapsız kalmış son kullanıcı mesajı, yeni mesajla art arda iki "user" olmasın diye atılır.
    if out and out[-1].role == "user":
        out.pop()
    return out
