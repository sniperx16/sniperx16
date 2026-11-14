import pytest

from kira.ai.base import ChatMessage, ChatRequest, ChatResponse, ImageInput, ProviderError, ProviderUnavailable
from kira.ai.router import HybridRouter, NoEngineAvailable, Route, detect_intent, is_complex


class FakeProvider:
    def __init__(self, name, is_local, ok=True, error=None):
        self.name, self.is_local, self.ok, self.error = name, is_local, ok, error
        self.supports_images = True
        self.calls = 0

    def available(self):
        return self.ok

    def chat(self, request):
        self.calls += 1
        if self.error:
            raise self.error
        return ChatResponse(f"{self.name} cevap", self.name)


class FakeNet:
    def __init__(self, up=True):
        self.up = up

    def online(self):
        return self.up

    def mark_offline(self):
        self.up = False


def req(text="merhaba", complex_task=False, images=()):
    return ChatRequest("sys", (ChatMessage("user", text, images=images),), complex_task=complex_task)


@pytest.mark.parametrize(
    "text,name,arg",
    [
        ("KIRA saat kaç?", "time", ""),
        ("Bunu hatırla: Kahvemi şekersiz içerim", "remember", "Kahvemi şekersiz içerim"),
        ("Annemin doğum günü 5 Mart, bunu unutma", "remember", "Annemin doğum günü 5 Mart"),
        ("doğum günü bilgisini unut", "forget", "doğum günü"),
        ("Kamerayı kapat", "camera_off", ""),
        ("KAMERAYI AÇ", "camera_on", ""),
        ("benim hakkımda neleri hatırlıyorsun", "list_memory", ""),
    ],
)
def test_intents(text, name, arg):
    intent = detect_intent(text)
    assert intent is not None and intent.name == name and intent.argument == arg


def test_no_intent_for_chat():
    assert detect_intent("Bugün çok yoruldum") is None


def test_complexity():
    assert is_complex("Bu iki işlemciyi karşılaştır")
    assert not is_complex("Nasılsın?")


def test_simple_goes_local_first():
    local, cloud = FakeProvider("local", True), FakeProvider("cloud", False)
    r = HybridRouter(local, cloud, FakeNet()).chat(req())
    assert r.route is Route.LOCAL and cloud.calls == 0


def test_complex_goes_cloud_first():
    local, cloud = FakeProvider("local", True), FakeProvider("cloud", False)
    r = HybridRouter(local, cloud, FakeNet()).chat(req(complex_task=True))
    assert r.route is Route.CLOUD and local.calls == 0


def test_offline_complex_falls_back_to_local_with_note():
    local, cloud = FakeProvider("local", True), FakeProvider("cloud", False)
    r = HybridRouter(local, cloud, FakeNet(up=False)).chat(req(complex_task=True))
    assert r.route is Route.LOCAL and r.fell_back and "kendi beynimle" in r.note
    assert cloud.calls == 0


def test_cloud_error_falls_back_and_marks_offline():
    net = FakeNet()
    local = FakeProvider("local", True)
    cloud = FakeProvider("cloud", False, error=ProviderUnavailable("bağlanılamadı"))
    r = HybridRouter(local, cloud, net).chat(req(complex_task=True))
    assert r.route is Route.LOCAL and net.up is False


def test_local_down_uses_cloud():
    local, cloud = FakeProvider("local", True, ok=False), FakeProvider("cloud", False)
    assert HybridRouter(local, cloud, FakeNet()).chat(req()).route is Route.CLOUD


def test_images_not_sent_to_cloud_without_permission():
    local, cloud = FakeProvider("local", True, ok=False), FakeProvider("cloud", False)
    router = HybridRouter(local, cloud, FakeNet(), allow_cloud_images=False)
    with pytest.raises(NoEngineAvailable):
        router.chat(req(images=(ImageInput(b"x"),)))
    assert cloud.calls == 0
    router.allow_cloud_images = True
    assert router.chat(req(images=(ImageInput(b"x"),))).route is Route.CLOUD


def test_all_fail():
    local = FakeProvider("local", True, error=ProviderError("x"))
    cloud = FakeProvider("cloud", False, error=ProviderError("y"))
    with pytest.raises(NoEngineAvailable):
        HybridRouter(local, cloud, FakeNet()).chat(req())


def test_simple_order_robot_then_pc_then_cloud():
    local, pc, cloud = FakeProvider("local", True), FakeProvider("pc", True), FakeProvider("cloud", False)
    router = HybridRouter(local, cloud, FakeNet(), pc=pc)
    assert [r for r, _ in router.choose(req())] == [Route.LOCAL, Route.PC, Route.CLOUD]
    assert [r for r, _ in router.choose(req(complex_task=True))] == [Route.CLOUD, Route.PC, Route.LOCAL]


def test_complex_offline_uses_pc_before_robot_brain():
    local, pc, cloud = FakeProvider("local", True), FakeProvider("pc", True), FakeProvider("cloud", False)
    r = HybridRouter(local, cloud, FakeNet(up=False), pc=pc).chat(req(complex_task=True))
    assert r.route is Route.PC and r.note == ""


def test_no_pc_no_internet_robot_still_talks():
    local = FakeProvider("local", True)
    pc = FakeProvider("pc", True, ok=False)
    cloud = FakeProvider("cloud", False)
    r = HybridRouter(local, cloud, FakeNet(up=False), pc=pc).chat(req())
    assert r.route is Route.LOCAL and r.response.text == "local cevap"


def test_images_skip_providers_without_vision():
    local = FakeProvider("local", True)
    local.supports_images = False
    pc = FakeProvider("pc", True)
    router = HybridRouter(local, None, FakeNet(up=False), pc=pc)
    assert router.chat(req(images=(ImageInput(b"x"),))).route is Route.PC
