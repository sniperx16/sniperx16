from datetime import datetime

import pytest

from kira.ai.base import ChatResponse
from kira.ai.router import HybridRouter, Route
from kira.core.assistant import Assistant
from kira.core.config import Settings
from kira.core.persona import DeviceStatus, build_system_prompt
from kira.memory.store import MemoryStore


class RecordingProvider:
    name, is_local, supports_images = "local:test", True, True

    def __init__(self):
        self.requests = []

    def available(self):
        return True

    def chat(self, request):
        self.requests.append(request)
        return ChatResponse("Tamam.", "local:test")


class Net:
    def online(self):
        return False

    def mark_offline(self):
        pass


@pytest.fixture
def setup(tmp_path):
    mem = MemoryStore(tmp_path / "m.sqlite")
    prov = RecordingProvider()
    a = Assistant(
        Settings(data_dir=tmp_path), mem, HybridRouter(prov, None, Net()),
        clock=lambda: datetime(2026, 11, 13, 14, 5),
    )
    return a, mem, prov


def test_time_rule_no_ai(setup):
    a, _, prov = setup
    r = a.handle("KIRA saat kaç?")
    assert r.text == "Saat 14:05." and r.route is Route.RULE and prov.requests == []


def test_date_turkish(setup):
    a, *_ = setup
    assert a.handle("bugün günlerden ne").text == "Bugün 13 Kasım 2026 Cuma."


def test_remember_then_used_in_prompt(setup):
    a, mem, prov = setup
    assert a.handle("Bunu hatırla: kahvemi şekersiz içerim").text == "Tamam, aklımda."
    a.handle("Bana kahve önerir misin?")
    assert "kahvemi şekersiz içerim" in prov.requests[-1].system


def test_sensitive_consent_flow(setup):
    a, mem, _ = setup
    r = a.handle("Bunu hatırla: wifi şifrem kedi123")
    assert r.needs_consent and mem.list_facts() == []
    assert a.handle("hayır").text == "Anlaştık, kaydetmedim."
    assert mem.list_facts() == []
    a.handle("Bunu hatırla: wifi şifrem kedi123")
    a.handle("evet kaydet")
    assert mem.list_facts()[0].sensitive


def test_forget(setup):
    a, mem, _ = setup
    a.handle("Bunu hatırla: annemin doğum günü 5 Mart")
    assert "1 kaydı sildim" in a.handle("annemin doğum günü bilgisini unut").text
    assert mem.list_facts() == []


def test_device_commands_honest_when_disconnected(setup):
    a, *_ = setup
    r = a.handle("kamerayı kapat")
    assert r.action is None and "bağlı değil" in r.text


def test_device_commands_when_connected(setup):
    a, *_ = setup
    a.device_status = lambda: DeviceStatus(connected=True, camera_on=True)
    assert a.handle("kamerayı kapat").action == "camera_off"


def test_history_passed_with_alternating_roles(setup):
    a, _, prov = setup
    a.handle("Merhaba")
    a.handle("Nasılsın")
    msgs = prov.requests[-1].messages
    assert [m.role for m in msgs] == ["user", "assistant", "user"]
    assert msgs[-1].content == "Nasılsın"


def test_persona_states_disconnected_hardware():
    p = build_system_prompt(now=datetime(2026, 11, 13, 9, 0), device=DeviceStatus())
    assert "bağlı değil" in p and "uydurmazsın" in p
    p2 = build_system_prompt(now=datetime(2026, 11, 13, 9, 0), device=DeviceStatus(connected=True))
    assert "Mikrofon: bilinmiyor" in p2
