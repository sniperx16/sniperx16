"""KIRA ayarları.

Ayarlar `%APPDATA%/KIRA/config.toml` (Windows) veya `~/.config/kira/config.toml`
dosyasından okunur. Dosya yoksa güvenli varsayılanlar kullanılır.
API anahtarları BURADA TUTULMAZ — bkz. kira.security.secrets.
"""

from __future__ import annotations

import os
import sys
import tomllib
from dataclasses import dataclass, field, fields, replace
from pathlib import Path


def default_data_dir() -> Path:
    override = os.environ.get("KIRA_DATA_DIR")
    if override:
        return Path(override)
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
        return base / "KIRA"
    return Path.home() / ".config" / "kira"


@dataclass(frozen=True)
class LocalAISettings:
    enabled: bool = True
    base_url: str = "http://127.0.0.1:11434"
    chat_model: str = "qwen2.5:7b"
    vision_model: str = "qwen2.5vl:7b"
    timeout_s: float = 60.0


@dataclass(frozen=True)
class CloudAISettings:
    enabled: bool = True
    provider: str = "anthropic"
    model: str = "claude-opus-5-5"
    # Sohbet için düşük efor = hızlı cevap; karmaşık görevlerde yükseltilir.
    chat_effort: str = "low"
    complex_effort: str = "high"
    max_tokens: int = 16000
    # Görüntülerin buluta gönderilmesi harici veri gönderimidir; varsayılan kapalı.
    allow_images: bool = False


@dataclass(frozen=True)
class MemorySettings:
    # Hassas bilgi tespit edilirse kullanıcıya sormadan kaydetme.
    require_consent_for_sensitive: bool = True
    max_context_facts: int = 12
    max_history_messages: int = 12


@dataclass(frozen=True)
class Settings:
    data_dir: Path = field(default_factory=default_data_dir)
    user_name: str = ""
    local_ai: LocalAISettings = field(default_factory=LocalAISettings)
    cloud_ai: CloudAISettings = field(default_factory=CloudAISettings)
    memory: MemorySettings = field(default_factory=MemorySettings)

    @property
    def db_path(self) -> Path:
        return self.data_dir / "kira_memory.sqlite"

    @property
    def backup_dir(self) -> Path:
        return self.data_dir / "backups"


def _merge(dc, values: dict):
    known = {f.name: f for f in fields(dc)}
    updates = {}
    for key, value in values.items():
        if key not in known:
            raise ValueError(f"Bilinmeyen ayar: {key}")
        current = getattr(dc, key)
        if hasattr(current, "__dataclass_fields__") and isinstance(value, dict):
            updates[key] = _merge(current, value)
        elif isinstance(current, Path):
            updates[key] = Path(value)
        else:
            updates[key] = value
    return replace(dc, **updates)


def _has_secret_key(data: dict) -> bool:
    for key, value in data.items():
        if any(s in key.lower() for s in ("api_key", "apikey", "secret", "password", "auth_token", "access_token")):
            return True
        if isinstance(value, dict) and _has_secret_key(value):
            return True
    return False


def load_settings(path: Path | None = None) -> Settings:
    settings = Settings()
    path = path or settings.data_dir / "config.toml"
    if path.exists():
        with path.open("rb") as fh:
            data = tomllib.load(fh)
        if _has_secret_key(data):
            raise ValueError(
                "config.toml içinde API anahtarı bulunmamalı. "
                "Anahtarı `python -m kira key set anthropic` ile kaydedin."
            )
        settings = _merge(settings, data)
    return settings
