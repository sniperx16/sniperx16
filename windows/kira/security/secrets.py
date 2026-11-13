"""API anahtarlarının güvenli saklanması.

Anahtarlar Windows Kimlik Bilgisi Yöneticisi'nde (keyring) tutulur.
Kaynak koda, config.toml'a veya git'e asla yazılmaz.
Geliştirme için ortam değişkeni (ör. ANTHROPIC_API_KEY) de okunur.
"""

from __future__ import annotations

import os

SERVICE_NAME = "KIRA-AI-PRO"

# sağlayıcı adı -> ortam değişkeni
ENV_VARS = {
    "anthropic": "ANTHROPIC_API_KEY",
}


def _keyring():
    try:
        import keyring
    except ImportError:  # pragma: no cover - keyring bağımlılıkta var
        return None
    return keyring


def get_secret(name: str) -> str | None:
    kr = _keyring()
    if kr is not None:
        try:
            value = kr.get_password(SERVICE_NAME, name)
        except Exception:
            value = None
        if value:
            return value
    env = ENV_VARS.get(name)
    return os.environ.get(env) if env else None


def set_secret(name: str, value: str) -> None:
    kr = _keyring()
    if kr is None:
        raise RuntimeError("keyring kurulu değil: pip install keyring")
    if not value.strip():
        raise ValueError("Boş anahtar kaydedilemez")
    kr.set_password(SERVICE_NAME, name, value.strip())


def delete_secret(name: str) -> bool:
    kr = _keyring()
    if kr is None:
        return False
    try:
        kr.delete_password(SERVICE_NAME, name)
        return True
    except Exception:
        return False


def mask(value: str | None) -> str:
    if not value:
        return "(yok)"
    return value[:4] + "…" + value[-2:] if len(value) > 8 else "****"
