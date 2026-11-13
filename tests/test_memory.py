import json
from datetime import datetime, timedelta, timezone

import pytest

from kira.memory.store import ConsentRequired, MemoryStore


@pytest.fixture
def mem(tmp_path):
    m = MemoryStore(tmp_path / "m.sqlite")
    yield m
    m.close()


def test_remember_and_search_turkish_suffixes(mem):
    mem.remember("Kullanıcı kahvesini şekersiz içer", category="tercih")
    mem.remember("KIRA projesinde kamera yuvası tasarlanıyor", category="proje")
    hits = mem.search_facts("kahve nasıl içiyorum?")
    assert [h.content for h in hits] == ["Kullanıcı kahvesini şekersiz içer"]
    assert mem.search_facts("kameralar")[0].category == "proje"


def test_duplicate_fact_not_inserted_twice(mem):
    a = mem.remember("Mavi seviyor")
    b = mem.remember("Mavi seviyor")
    assert a == b and len(mem.list_facts()) == 1


def test_sensitive_requires_consent(mem):
    with pytest.raises(ConsentRequired):
        mem.remember("Wi-Fi şifrem kedi123")
    assert mem.list_facts() == []
    fid = mem.remember("Wi-Fi şifrem kedi123", consent=True)
    fact = mem.list_facts()[0]
    assert fact.id == fid and fact.sensitive
    # Hassas içerik denetim günlüğüne yazılmaz
    assert all("kedi123" not in e["detail"] for e in mem.audit_entries())


def test_forget_matching_and_fts_sync(mem):
    mem.remember("Doğum günüm 5 Mart")
    removed = mem.forget_matching("doğum günü")
    assert len(removed) == 1
    assert mem.search_facts("doğum") == []
    assert mem.audit_entries()[0]["action"] == "fact.delete_matching"


def test_update_fact_reindexes(mem):
    fid = mem.remember("Sevdiği renk kırmızı")
    mem.update_fact(fid, "Sevdiği renk yeşil")
    assert mem.search_facts("yeşil")[0].id == fid
    assert mem.search_facts("kırmızı") == []


def test_conversations_and_message_search(mem):
    cid = mem.start_conversation()
    mem.add_message(cid, "user", "Yarın toplantı var")
    mem.add_message(cid, "assistant", "Not aldım")
    assert [m.role for m in mem.recent_messages(cid)] == ["user", "assistant"]
    assert mem.search_messages("toplantıya")[0].content == "Yarın toplantı var"
    mem.delete_conversation(cid)
    assert mem.recent_messages(cid) == []


def test_tasks_projects_reminders(mem):
    pid = mem.upsert_project("KIRA AI PRO", "kamera yuvası")
    tid = mem.add_task("Kamera ölç", pid)
    assert mem.open_tasks()[0]["title"] == "Kamera ölç"
    mem.complete_task(tid)
    assert mem.open_tasks() == []
    now = datetime.now(timezone.utc)
    rid = mem.add_reminder("Su iç", now - timedelta(minutes=1))
    mem.add_reminder("Sonra", now + timedelta(hours=1))
    due = mem.due_reminders(now)
    assert [r["id"] for r in due] == [rid]
    mem.mark_reminder_delivered(rid)
    assert mem.due_reminders(now) == []


def test_device_settings(mem):
    mem.set_device_setting("volume", 40)
    assert mem.get_device_setting("volume") == 40
    assert mem.get_device_setting("yok", "x") == "x"


def test_backup_and_export_excludes_sensitive(mem, tmp_path):
    mem.remember("Mavi seviyor")
    mem.remember("Şifrem 1234", consent=True)
    backup = mem.backup(tmp_path / "b")
    assert backup.exists()
    restored = MemoryStore(backup)
    assert len(restored.list_facts()) == 2
    restored.close()
    out = mem.export_json(tmp_path / "e.json")
    data = json.loads(out.read_text(encoding="utf-8"))
    assert [f["content"] for f in data["facts"]] == ["Mavi seviyor"]
