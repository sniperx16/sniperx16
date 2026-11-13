"""KIRA komut satırı.

    python -m kira                    # yazılı sohbet
    python -m kira status             # yerel/bulut AI durumu
    python -m kira key set anthropic  # API anahtarını Windows Kimlik Bilgisi Yöneticisi'ne kaydet
    python -m kira key delete anthropic
    python -m kira memory list | search <metin> | forget <id> | backup | export <dosya.json>
"""

from __future__ import annotations

import argparse
import getpass
import sys
from pathlib import Path

from kira.ai.anthropic_provider import AnthropicProvider
from kira.ai.ollama_provider import OllamaProvider
from kira.ai.router import Connectivity, HybridRouter
from kira.core.assistant import Assistant
from kira.core.config import Settings, load_settings
from kira.memory.store import MemoryStore
from kira.security import secrets


def build(settings: Settings) -> tuple[Assistant, OllamaProvider, AnthropicProvider, Connectivity]:
    memory = MemoryStore(settings.db_path, require_consent=settings.memory.require_consent_for_sensitive)
    local = OllamaProvider(settings.local_ai)
    cloud = AnthropicProvider(settings.cloud_ai)
    conn = Connectivity()
    router = HybridRouter(local, cloud, conn, allow_cloud_images=settings.cloud_ai.allow_images)
    return Assistant(settings, memory, router), local, cloud, conn


def cmd_chat(settings: Settings) -> int:
    assistant, *_ = build(settings)
    print("KIRA hazır. Çıkmak için 'çık' yaz.\n")
    while True:
        try:
            text = input("Sen: ")
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if text.strip().lower() in {"çık", "cik", "exit", "quit"}:
            return 0
        reply = assistant.handle(text)
        tag = f" [{reply.engine or reply.route.value}]"
        print(f"KIRA{tag}: {reply.text}\n")


def cmd_status(settings: Settings) -> int:
    _, local, cloud, conn = build(settings)
    print(f"Veri klasörü : {settings.data_dir}")
    print(f"İnternet     : {'var' if conn.online() else 'YOK'}")
    if local.available():
        print(f"Yerel AI     : çalışıyor ({', '.join(local.installed_models()) or 'model yok'})")
    else:
        print("Yerel AI     : ulaşılamıyor (Ollama kurulu ve açık mı?)")
    print(f"Bulut AI     : {settings.cloud_ai.provider} / {settings.cloud_ai.model}, "
          f"anahtar {secrets.mask(secrets.get_secret('anthropic'))}")
    return 0


def cmd_key(args) -> int:
    if args.action == "set":
        value = getpass.getpass(f"{args.provider} API anahtarı (ekranda görünmez): ")
        secrets.set_secret(args.provider, value)
        print("Kaydedildi (Windows Kimlik Bilgisi Yöneticisi).")
    else:
        print("Silindi." if secrets.delete_secret(args.provider) else "Kayıt bulunamadı.")
    return 0


def cmd_memory(settings: Settings, args) -> int:
    mem = MemoryStore(settings.db_path)
    if args.action == "list":
        for f in mem.list_facts():
            flag = " (hassas)" if f.sensitive else ""
            print(f"[{f.id}] {f.category}: {f.content}{flag}")
    elif args.action == "search":
        for f in mem.search_facts(" ".join(args.rest)):
            print(f"[{f.id}] {f.content}")
    elif args.action == "forget":
        ok = mem.forget(int(args.rest[0]))
        print("Silindi." if ok else "Bulunamadı.")
    elif args.action == "backup":
        print(f"Yedek: {mem.backup(settings.backup_dir)}")
    elif args.action == "export":
        target = Path(args.rest[0]) if args.rest else settings.data_dir / "kira_export.json"
        print(f"Dışa aktarıldı (hassas kayıtlar hariç): {mem.export_json(target)}")
    return 0


def main(argv: list[str] | None = None) -> int:
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(prog="kira")
    parser.add_argument("--config", type=Path)
    sub = parser.add_subparsers(dest="cmd")
    sub.add_parser("chat")
    sub.add_parser("status")
    k = sub.add_parser("key")
    k.add_argument("action", choices=["set", "delete"])
    k.add_argument("provider", choices=list(secrets.ENV_VARS))
    m = sub.add_parser("memory")
    m.add_argument("action", choices=["list", "search", "forget", "backup", "export"])
    m.add_argument("rest", nargs="*")
    args = parser.parse_args(argv)

    if args.cmd == "key":
        return cmd_key(args)
    settings = load_settings(args.config)
    if args.cmd == "status":
        return cmd_status(settings)
    if args.cmd == "memory":
        return cmd_memory(settings, args)
    return cmd_chat(settings)


if __name__ == "__main__":
    raise SystemExit(main())
