from kira.security.sensitive import detect, is_valid_tckn, luhn_ok


def test_valid_tckn_detected():
    assert is_valid_tckn("10000000146")
    assert "tckn" in detect("kimlik numaram 10000000146").categories


def test_random_11_digits_not_tckn():
    assert not is_valid_tckn("12345678901")


def test_card_luhn():
    assert luhn_ok("4111111111111111")
    assert "card" in detect("kartım 4111 1111 1111 1111").categories


def test_iban_phone_email():
    r = detect("IBAN TR33 0006 1005 1978 6457 8413 26, tel 0532 123 45 67, a@b.com")
    assert {"iban", "phone", "email"} <= set(r.categories)


def test_keywords_turkish_case():
    assert "password" in detect("Wi-Fi ŞİFRESİ kedi123").categories
    assert "health" in detect("Diyabet ilacımı sabah alıyorum").categories


def test_plain_preference_not_sensitive():
    assert not detect("Kahvemi şekersiz içerim").is_sensitive
    assert not detect("En sevdiğim renk mavi").is_sensitive
