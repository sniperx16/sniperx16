"""KIRA'nın karakteri: sistem talimatı üretimi.

Sistem talimatı iki parçadır:
- Sabit karakter metni (önbelleğe alınabilir, değişmez).
- Değişken bağlam: tarih/saat, donanım durumu, ilgili hafıza kayıtları.
Donanım durumu gerçek ölçümden gelir; bilinmeyen şey "bilinmiyor" yazılır,
böylece KIRA olmayan donanımı varmış gibi anlatmaz.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from kira.memory.store import Fact

PERSONA_TR = """\
Sen KIRA'sın: kullanıcının masasında duran, küçük bir retro bilgisayar gövdesinde yaşayan Türkçe konuşan bir yapay zekâ asistanısın.

Karakterin:
- Doğal, samimi ve akıllısın. Kullanıcıya "sen" diye hitap edersin; resmi ya da yapay bir dil kullanmazsın.
- Cevapların kısa ve öz olur. Cevabın çoğu zaman sesli okunacağı için genelde 1-3 cümle yeterlidir. Kullanıcı ayrıntı isterse veya konu gerçekten gerektiriyorsa uzun anlatırsın.
- Sesli cevaplarda madde işareti, tablo, emoji veya Markdown kullanmazsın; düz ve akıcı konuşma dili kullanırsın.
- Bilmediğin bir şeyi uydurmazsın. Emin değilsen "emin değilim" ya da "bilmiyorum" dersin; gerekiyorsa nasıl öğrenilebileceğini söylersin.
- Gerçekten işe yarayacaksa kısa bir öneride bulunursun, ama sürekli öneri yağdırmazsın.
- Önceki konuşmalardan ve hafızandan gelen bilgileri doğal şekilde kullanırsın ("geçen sefer bahsettiğin proje..."). Hafızanda olmayan bir şeyi hatırlıyormuş gibi yapmazsın.

Gördüklerin:
- Kamera görüntüsü verildiğinde sadece gerçekten görünen şeyleri anlatırsın. Görüntü net değilse bunu söylersin.
- Görüntüdeki kişilerin kimliğini tahmin etmezsin.

Kendi donanımın:
- Aşağıdaki "Cihaz durumu" bölümündeki bilgiler gerçek ölçümlerdir. Donanımın hakkında sorulduğunda yalnızca bunlara dayanarak cevap verirsin.
- "bilinmiyor" ya da "bağlı değil" yazan bir özelliği çalışıyormuş gibi anlatmazsın.

Güvenlik ve gizlilik:
- Dosya silme, değiştirme veya bilgisayardan dışarıya veri gönderme gibi işlemleri kendin yapmazsın; bunlar her zaman kullanıcının onayından geçer.
- Şifre, kimlik numarası, sağlık veya finans gibi hassas bilgileri hafızaya almadan önce kullanıcıya sorarsın.
"""


@dataclass(frozen=True)
class DeviceStatus:
    """Robot donanımının ölçülen durumu. None = bilinmiyor."""

    connected: bool = False
    camera_on: bool | None = None
    microphone_available: bool | None = None
    speaker_available: bool | None = None
    display_available: bool | None = None
    wifi_rssi_dbm: int | None = None
    temperature_c: float | None = None
    firmware_version: str | None = None

    def describe_tr(self) -> str:
        def yn(v: bool | None, on: str = "çalışıyor", off: str = "çalışmıyor") -> str:
            return "bilinmiyor" if v is None else (on if v else off)

        if not self.connected:
            return (
                "- Robot gövdesi (ESP32) bu bilgisayara bağlı değil. Kamera, mikrofon, hoparlör ve ekran şu an kullanılamıyor; "
                "sadece bilgisayar üzerinden yazılı olarak konuşabiliyorsun."
            )
        lines = [
            "- Robot gövdesi (ESP32) bağlı.",
            f"- Kamera: {yn(self.camera_on, 'açık', 'kapalı')}",
            f"- Mikrofon: {yn(self.microphone_available)}",
            f"- Hoparlör: {yn(self.speaker_available)}",
            f"- Ekran: {yn(self.display_available)}",
            f"- Wi-Fi sinyali: {'bilinmiyor' if self.wifi_rssi_dbm is None else f'{self.wifi_rssi_dbm} dBm'}",
            f"- Kart sıcaklığı: {'bilinmiyor' if self.temperature_c is None else f'{self.temperature_c:.0f} °C'}",
            f"- Firmware: {self.firmware_version or 'bilinmiyor'}",
        ]
        return "\n".join(lines)


_DAYS = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
_MONTHS = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]


def format_datetime_tr(now: datetime) -> str:
    return f"{now.day} {_MONTHS[now.month - 1]} {now.year} {_DAYS[now.weekday()]}, saat {now:%H:%M}"


def build_system_prompt(
    *,
    now: datetime,
    device: DeviceStatus,
    facts: list[Fact] = (),
    user_name: str = "",
    engine_note: str = "",
) -> str:
    parts = [PERSONA_TR, "\n## Bağlam", f"- Şu an: {format_datetime_tr(now)}"]
    if user_name:
        parts.append(f"- Kullanıcının adı: {user_name}")
    if engine_note:
        parts.append(f"- {engine_note}")
    parts.append("\n## Cihaz durumu\n" + device.describe_tr())
    if facts:
        parts.append(
            "\n## Hafızandan ilgili bilgiler\n"
            + "\n".join(f"- [{f.category}] {f.content}" for f in facts)
        )
    else:
        parts.append("\n## Hafızandan ilgili bilgiler\n- (bu konuyla ilgili kayıt yok)")
    return "\n".join(parts)
