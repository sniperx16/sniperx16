"""KIRA uzun süreli hafızası (SQLite + FTS5).

Saklananlar: konuşmalar, kullanıcı bilgileri/tercihleri, projeler, görevler,
hatırlatmalar, cihaz ayarları. Her değişiklik `audit_log`'a yazılır.
Hassas bilgiler kullanıcı onayı olmadan kaydedilmez (ConsentRequired).
"""

from __future__ import annotations

import json
import re
import sqlite3
from contextlib import closing
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from kira.security.sensitive import SensitivityResult, detect, tr_lower

SCHEMA_VERSION = 1

_SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);

CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY,
    started_at TEXT NOT NULL,
    title TEXT
);

CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    source TEXT NOT NULL DEFAULT 'text',
    engine TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS facts (
    id INTEGER PRIMARY KEY,
    category TEXT NOT NULL DEFAULT 'genel',
    content TEXT NOT NULL,
    sensitive INTEGER NOT NULL DEFAULT 0,
    source_message_id INTEGER REFERENCES messages(id) ON DELETE SET NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    notes TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'aktif',
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    project_id INTEGER REFERENCES projects(id) ON DELETE SET NULL,
    done INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    done_at TEXT
);

CREATE TABLE IF NOT EXISTS reminders (
    id INTEGER PRIMARY KEY,
    text TEXT NOT NULL,
    due_at TEXT NOT NULL,
    delivered INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS device_settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY,
    at TEXT NOT NULL,
    action TEXT NOT NULL,
    detail TEXT NOT NULL
);

CREATE VIRTUAL TABLE IF NOT EXISTS facts_fts USING fts5(
    content, category, content='facts', content_rowid='id', tokenize='unicode61 remove_diacritics 2'
);
CREATE TRIGGER IF NOT EXISTS facts_ai AFTER INSERT ON facts BEGIN
    INSERT INTO facts_fts(rowid, content, category) VALUES (new.id, new.content, new.category);
END;
CREATE TRIGGER IF NOT EXISTS facts_ad AFTER DELETE ON facts BEGIN
    INSERT INTO facts_fts(facts_fts, rowid, content, category) VALUES ('delete', old.id, old.content, old.category);
END;
CREATE TRIGGER IF NOT EXISTS facts_au AFTER UPDATE ON facts BEGIN
    INSERT INTO facts_fts(facts_fts, rowid, content, category) VALUES ('delete', old.id, old.content, old.category);
    INSERT INTO facts_fts(rowid, content, category) VALUES (new.id, new.content, new.category);
END;

CREATE VIRTUAL TABLE IF NOT EXISTS messages_fts USING fts5(
    content, content='messages', content_rowid='id', tokenize='unicode61 remove_diacritics 2'
);
CREATE TRIGGER IF NOT EXISTS messages_ai AFTER INSERT ON messages BEGIN
    INSERT INTO messages_fts(rowid, content) VALUES (new.id, new.content);
END;
CREATE TRIGGER IF NOT EXISTS messages_ad AFTER DELETE ON messages BEGIN
    INSERT INTO messages_fts(messages_fts, rowid, content) VALUES ('delete', old.id, old.content);
END;
"""


class ConsentRequired(Exception):
    """Hassas bilgi kaydı için kullanıcı onayı gerekiyor."""

    def __init__(self, result: SensitivityResult):
        self.result = result
        super().__init__(f"Hassas bilgi içeriyor: {result.describe_tr()}")


@dataclass(frozen=True)
class Fact:
    id: int
    category: str
    content: str
    sensitive: bool
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class Message:
    id: int
    conversation_id: int
    role: str
    content: str
    created_at: str


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _fts_query(text: str) -> str:
    """Serbest metni güvenli bir FTS5 sorgusuna çevirir (OR + önek eşleşme)."""
    words = [w for w in re.findall(r"\w+", tr_lower(text)) if len(w) >= 2]
    # Türkçe ekler için kelime kökü yaklaşımı: ilk 5 harf + önek araması
    terms = sorted({(w[:5] if len(w) > 5 else w) for w in words})
    return " OR ".join(f'"{t}"*' for t in terms)


class MemoryStore:
    def __init__(self, path: Path | str, *, require_consent: bool = True):
        self.path = Path(path) if str(path) != ":memory:" else path
        if isinstance(self.path, Path):
            self.path.parent.mkdir(parents=True, exist_ok=True)
        self.require_consent = require_consent
        self.conn = sqlite3.connect(str(self.path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(_SCHEMA)
        self.conn.execute(
            "INSERT OR IGNORE INTO meta(key, value) VALUES ('schema_version', ?)", (str(SCHEMA_VERSION),)
        )
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

    # ---- denetim ----
    def _audit(self, action: str, detail: dict) -> None:
        self.conn.execute(
            "INSERT INTO audit_log(at, action, detail) VALUES (?, ?, ?)",
            (_now(), action, json.dumps(detail, ensure_ascii=False)),
        )

    def audit_entries(self, limit: int = 50) -> list[dict]:
        rows = self.conn.execute("SELECT * FROM audit_log ORDER BY id DESC LIMIT ?", (limit,))
        return [dict(r) for r in rows]

    # ---- konuşmalar ----
    def start_conversation(self, title: str | None = None) -> int:
        cur = self.conn.execute(
            "INSERT INTO conversations(started_at, title) VALUES (?, ?)", (_now(), title)
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def add_message(
        self, conversation_id: int, role: str, content: str, *, source: str = "text", engine: str | None = None
    ) -> int:
        cur = self.conn.execute(
            "INSERT INTO messages(conversation_id, role, content, source, engine, created_at) VALUES (?,?,?,?,?,?)",
            (conversation_id, role, content, source, engine, _now()),
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def recent_messages(self, conversation_id: int, limit: int = 12) -> list[Message]:
        rows = self.conn.execute(
            "SELECT id, conversation_id, role, content, created_at FROM messages "
            "WHERE conversation_id = ? ORDER BY id DESC LIMIT ?",
            (conversation_id, limit),
        ).fetchall()
        return [Message(**dict(r)) for r in reversed(rows)]

    def search_messages(self, query: str, limit: int = 10) -> list[Message]:
        q = _fts_query(query)
        if not q:
            return []
        rows = self.conn.execute(
            "SELECT m.id, m.conversation_id, m.role, m.content, m.created_at FROM messages_fts f "
            "JOIN messages m ON m.id = f.rowid WHERE messages_fts MATCH ? ORDER BY rank LIMIT ?",
            (q, limit),
        ).fetchall()
        return [Message(**dict(r)) for r in rows]

    def delete_conversation(self, conversation_id: int) -> bool:
        cur = self.conn.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))
        self._audit("conversation.delete", {"id": conversation_id})
        self.conn.commit()
        return cur.rowcount > 0

    # ---- bilgiler (facts) ----
    def remember(
        self,
        content: str,
        *,
        category: str = "genel",
        consent: bool = False,
        source_message_id: int | None = None,
    ) -> int:
        content = content.strip()
        if not content:
            raise ValueError("Boş bilgi kaydedilemez")
        result = detect(content)
        if result.is_sensitive and self.require_consent and not consent:
            raise ConsentRequired(result)
        now = _now()
        existing = self.conn.execute(
            "SELECT id FROM facts WHERE content = ? AND category = ?", (content, category)
        ).fetchone()
        if existing:
            self.conn.execute("UPDATE facts SET updated_at = ? WHERE id = ?", (now, existing["id"]))
            self.conn.commit()
            return int(existing["id"])
        cur = self.conn.execute(
            "INSERT INTO facts(category, content, sensitive, source_message_id, created_at, updated_at) "
            "VALUES (?,?,?,?,?,?)",
            (category, content, int(result.is_sensitive), source_message_id, now, now),
        )
        # Hassas içeriğin kendisi denetim günlüğüne yazılmaz.
        self._audit(
            "fact.add",
            {"id": cur.lastrowid, "category": category, "sensitive": result.is_sensitive},
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def update_fact(self, fact_id: int, content: str, *, consent: bool = False) -> bool:
        result = detect(content)
        if result.is_sensitive and self.require_consent and not consent:
            raise ConsentRequired(result)
        cur = self.conn.execute(
            "UPDATE facts SET content = ?, sensitive = ?, updated_at = ? WHERE id = ?",
            (content.strip(), int(result.is_sensitive), _now(), fact_id),
        )
        self._audit("fact.update", {"id": fact_id})
        self.conn.commit()
        return cur.rowcount > 0

    def forget(self, fact_id: int) -> bool:
        cur = self.conn.execute("DELETE FROM facts WHERE id = ?", (fact_id,))
        self._audit("fact.delete", {"id": fact_id})
        self.conn.commit()
        return cur.rowcount > 0

    def forget_matching(self, query: str) -> list[Fact]:
        """Sorguya uyan bilgileri siler ve silinenleri döndürür."""
        matches = self.search_facts(query, limit=50)
        for f in matches:
            self.conn.execute("DELETE FROM facts WHERE id = ?", (f.id,))
        if matches:
            self._audit("fact.delete_matching", {"ids": [f.id for f in matches]})
        self.conn.commit()
        return matches

    def list_facts(self, category: str | None = None) -> list[Fact]:
        if category:
            rows = self.conn.execute("SELECT * FROM facts WHERE category = ? ORDER BY updated_at DESC", (category,))
        else:
            rows = self.conn.execute("SELECT * FROM facts ORDER BY updated_at DESC")
        return [self._fact(r) for r in rows]

    def search_facts(self, query: str, limit: int = 10) -> list[Fact]:
        q = _fts_query(query)
        if not q:
            return []
        rows = self.conn.execute(
            "SELECT f.* FROM facts_fts JOIN facts f ON f.id = facts_fts.rowid "
            "WHERE facts_fts MATCH ? ORDER BY rank LIMIT ?",
            (q, limit),
        )
        return [self._fact(r) for r in rows]

    @staticmethod
    def _fact(row: sqlite3.Row) -> Fact:
        return Fact(
            id=row["id"],
            category=row["category"],
            content=row["content"],
            sensitive=bool(row["sensitive"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    # ---- projeler ve görevler ----
    def upsert_project(self, name: str, notes: str = "", status: str = "aktif") -> int:
        self.conn.execute(
            "INSERT INTO projects(name, notes, status, updated_at) VALUES (?,?,?,?) "
            "ON CONFLICT(name) DO UPDATE SET notes = excluded.notes, status = excluded.status, "
            "updated_at = excluded.updated_at",
            (name, notes, status, _now()),
        )
        self.conn.commit()
        return int(self.conn.execute("SELECT id FROM projects WHERE name = ?", (name,)).fetchone()["id"])

    def list_projects(self, status: str | None = "aktif") -> list[dict]:
        if status:
            rows = self.conn.execute("SELECT * FROM projects WHERE status = ? ORDER BY updated_at DESC", (status,))
        else:
            rows = self.conn.execute("SELECT * FROM projects ORDER BY updated_at DESC")
        return [dict(r) for r in rows]

    def add_task(self, title: str, project_id: int | None = None) -> int:
        cur = self.conn.execute(
            "INSERT INTO tasks(title, project_id, created_at) VALUES (?,?,?)", (title, project_id, _now())
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def complete_task(self, task_id: int) -> bool:
        cur = self.conn.execute("UPDATE tasks SET done = 1, done_at = ? WHERE id = ?", (_now(), task_id))
        self.conn.commit()
        return cur.rowcount > 0

    def open_tasks(self) -> list[dict]:
        return [dict(r) for r in self.conn.execute("SELECT * FROM tasks WHERE done = 0 ORDER BY id")]

    # ---- hatırlatmalar ----
    def add_reminder(self, text: str, due_at: datetime) -> int:
        if due_at.tzinfo is None:
            due_at = due_at.astimezone()
        cur = self.conn.execute(
            "INSERT INTO reminders(text, due_at) VALUES (?, ?)",
            (text, due_at.astimezone(timezone.utc).isoformat(timespec="seconds")),
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def due_reminders(self, now: datetime | None = None) -> list[dict]:
        now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
        rows = self.conn.execute(
            "SELECT * FROM reminders WHERE delivered = 0 AND due_at <= ? ORDER BY due_at",
            (now.isoformat(timespec="seconds"),),
        )
        return [dict(r) for r in rows]

    def mark_reminder_delivered(self, reminder_id: int) -> None:
        self.conn.execute("UPDATE reminders SET delivered = 1 WHERE id = ?", (reminder_id,))
        self.conn.commit()

    # ---- cihaz ayarları ----
    def set_device_setting(self, key: str, value) -> None:
        self.conn.execute(
            "INSERT INTO device_settings(key, value, updated_at) VALUES (?,?,?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at",
            (key, json.dumps(value), _now()),
        )
        self._audit("device_setting.set", {"key": key})
        self.conn.commit()

    def get_device_setting(self, key: str, default=None):
        row = self.conn.execute("SELECT value FROM device_settings WHERE key = ?", (key,)).fetchone()
        return json.loads(row["value"]) if row else default

    # ---- yedek / dışa aktarma ----
    def backup(self, backup_dir: Path) -> Path:
        backup_dir.mkdir(parents=True, exist_ok=True)
        target = backup_dir / f"kira_memory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sqlite"
        with closing(sqlite3.connect(str(target))) as dst:
            self.conn.backup(dst)
        self._audit("backup", {"path": str(target)})
        self.conn.commit()
        return target

    def export_json(self, path: Path, *, include_sensitive: bool = False) -> Path:
        facts = [f.__dict__ for f in self.list_facts() if include_sensitive or not f.sensitive]
        data = {
            "exported_at": _now(),
            "schema_version": SCHEMA_VERSION,
            "facts": facts,
            "projects": self.list_projects(status=None),
            "tasks": [dict(r) for r in self.conn.execute("SELECT * FROM tasks")],
            "reminders": [dict(r) for r in self.conn.execute("SELECT * FROM reminders")],
            "conversations": [
                {
                    **dict(c),
                    "messages": [
                        dict(m)
                        for m in self.conn.execute(
                            "SELECT role, content, source, engine, created_at FROM messages "
                            "WHERE conversation_id = ? ORDER BY id",
                            (c["id"],),
                        )
                    ],
                }
                for c in self.conn.execute("SELECT * FROM conversations ORDER BY id")
            ],
        }
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        self._audit("export", {"path": str(path), "include_sensitive": include_sensitive})
        self.conn.commit()
        return path
