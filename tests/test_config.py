import pytest

from kira.core.config import load_settings


def test_defaults(tmp_path):
    s = load_settings(tmp_path / "yok.toml")
    assert s.cloud_ai.model == "claude-opus-5-5" and s.cloud_ai.allow_images is False


def test_override(tmp_path):
    p = tmp_path / "c.toml"
    p.write_text('user_name = "Ayşe"\n[local_ai]\nchat_model = "gemma3:4b"\n[cloud_ai]\nmax_tokens = 8000\n', encoding="utf-8")
    s = load_settings(p)
    assert s.user_name == "Ayşe" and s.local_ai.chat_model == "gemma3:4b" and s.cloud_ai.max_tokens == 8000


def test_rejects_api_key_in_config(tmp_path):
    p = tmp_path / "c.toml"
    p.write_text('[cloud_ai]\napi_key = "sk-xxx"\n', encoding="utf-8")
    with pytest.raises(ValueError):
        load_settings(p)


def test_unknown_key(tmp_path):
    p = tmp_path / "c.toml"
    p.write_text('bilinmeyen = 1\n', encoding="utf-8")
    with pytest.raises(ValueError):
        load_settings(p)
