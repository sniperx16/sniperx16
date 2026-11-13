"""Hassas bilgi tespiti.

Hafızaya bir şey yazılmadan önce çağrılır. Hassas veri bulunursa KIRA
kaydetmeden önce kullanıcıdan izin ister. Amaç kesin sınıflandırma değil,
"emin değilsen sor" ilkesidir.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_TR_LOWER = str.maketrans("IİÇĞÖŞÜ", "ıiçğöşü")


def tr_lower(text: str) -> str:
    return text.translate(_TR_LOWER).lower()


def _digits(s: str) -> str:
    return re.sub(r"\D", "", s)


def is_valid_tckn(number: str) -> bool:
    d = [int(c) for c in number]
    if len(d) != 11 or d[0] == 0:
        return False
    if ((sum(d[0:9:2]) * 7) - sum(d[1:8:2])) % 10 != d[9]:
        return False
    return sum(d[:10]) % 10 == d[10]


def luhn_ok(number: str) -> bool:
    total = 0
    for i, ch in enumerate(reversed(number)):
        n = int(ch)
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        total += n
    return total % 10 == 0


_PATTERNS: dict[str, re.Pattern[str]] = {
    "iban": re.compile(r"\bTR\s?\d{2}(?:\s?\d{4}){5}\s?\d{2}\b", re.IGNORECASE),
    "email": re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b"),
    "phone": re.compile(r"(?<!\d)(?:\+?90[\s-]?)?0?5\d{2}[\s-]?\d{3}[\s-]?\d{2}[\s-]?\d{2}(?!\d)"),
}

_KEYWORDS: dict[str, tuple[str, ...]] = {
    "password": ("şifre", "parola", "password", "pin kodu", "pin kodum", "api key", "api anahtar"),
    "health": ("hastalı", "teşhis", "ilaç", "tedavi", "ameliyat", "depresyon", "kanser", "diyabet"),
    "finance": ("maaş", "kredi kartı", "banka hesab", "borcum", "iban"),
    "address": ("ev adresim", "adresim", "oturduğum yer", "mahallesi", "sokak no"),
    "identity": ("tc kimlik", "kimlik numara", "pasaport", "ehliyet no"),
}


@dataclass(frozen=True)
class SensitivityResult:
    categories: tuple[str, ...]

    @property
    def is_sensitive(self) -> bool:
        return bool(self.categories)

    def describe_tr(self) -> str:
        names = {
            "tckn": "T.C. kimlik numarası",
            "card": "kart numarası",
            "iban": "IBAN",
            "email": "e-posta adresi",
            "phone": "telefon numarası",
            "password": "şifre/gizli anahtar",
            "health": "sağlık bilgisi",
            "finance": "finansal bilgi",
            "address": "adres",
            "identity": "kimlik bilgisi",
        }
        return ", ".join(names.get(c, c) for c in self.categories)


def detect(text: str) -> SensitivityResult:
    found: list[str] = []
    for m in re.finditer(r"(?<!\d)\d{11}(?!\d)", text):
        if is_valid_tckn(m.group()):
            found.append("tckn")
            break
    for m in re.finditer(r"(?<!\d)(?:\d[ -]?){13,19}(?!\d)", text):
        digits = _digits(m.group())
        if 13 <= len(digits) <= 19 and luhn_ok(digits):
            found.append("card")
            break
    for name, pattern in _PATTERNS.items():
        if pattern.search(text):
            found.append(name)
    low = tr_lower(text)
    for name, words in _KEYWORDS.items():
        if name not in found and any(w in low for w in words):
            found.append(name)
    return SensitivityResult(tuple(dict.fromkeys(found)))
