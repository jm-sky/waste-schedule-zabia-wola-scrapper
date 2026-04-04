"""
Testy dla zabiawola_pl.py — źródła hacs_waste_collection_schedule.

Uruchomienie:
    pytest tests/test_zabiawola_pl.py
    pytest tests/test_zabiawola_pl.py -m integration  # tylko testy sieciowe
"""

from __future__ import annotations

import sys
import types
from datetime import date
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Mock waste_collection_schedule (dostępny tylko w środowisku HA)
# ---------------------------------------------------------------------------

_wcs = types.ModuleType("waste_collection_schedule")


class _Collection:
    def __init__(self, date: date, t: str, icon: str | None = None) -> None:
        self.date = date
        self.type = t
        self.icon = icon


_wcs.Collection = _Collection  # type: ignore[attr-defined]
sys.modules["waste_collection_schedule"] = _wcs

# ---------------------------------------------------------------------------
# Import modułu pod testem
# ---------------------------------------------------------------------------

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from zabiawola_pl import (  # noqa: E402
    DESCRIPTION,
    ICON_MAP,
    TEST_CASES,
    TITLE,
    URL,
    Source,
    get_group,
    parse_schedule,
    scrape_pdf_url,
)


# ---------------------------------------------------------------------------
# Stałe pomocnicze
# ---------------------------------------------------------------------------

_PDF_URL_2026 = "https://www.zabiawola.pl/plik,5464,harmonogram-harmonogram-odbioru-odpadow-2026r.pdf"
_YEAR = 2026

_ALL_WASTE_TYPES = {
    "Papier i tektura",
    "Tworzywa sztuczne i metal",
    "Szkło",
    "Bioodpady ogrodowe",
    "Bioodpady kuchenne",
    "Zmieszane odpady komunalne",
    "Popiół z palenisk domowych",
}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def real_pdf() -> bytes:
    """Pobiera prawdziwy PDF raz na całą sesję testów (wymaga sieci)."""
    import urllib.request

    req = urllib.request.Request(_PDF_URL_2026, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req, timeout=30).read()


@pytest.fixture(scope="session")
def parsed_schedule(real_pdf: bytes) -> dict:
    return parse_schedule(real_pdf, _YEAR)


# ---------------------------------------------------------------------------
# Testy metadanych modułu
# ---------------------------------------------------------------------------


def test_module_metadata() -> None:
    assert isinstance(TITLE, str) and TITLE
    assert isinstance(DESCRIPTION, str) and DESCRIPTION
    assert isinstance(URL, str) and URL.startswith("http")


def test_test_cases_format() -> None:
    assert isinstance(TEST_CASES, dict)
    assert len(TEST_CASES) > 0
    for name, params in TEST_CASES.items():
        assert isinstance(name, str)
        assert isinstance(params, dict)
        assert "city" in params


def test_icon_map_covers_all_waste_types() -> None:
    for wtype in _ALL_WASTE_TYPES:
        assert wtype in ICON_MAP, f"Brak ikony dla: {wtype}"
        assert ICON_MAP[wtype].startswith("mdi:")


# ---------------------------------------------------------------------------
# Testy get_group()
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("city,street,expected", [
    # Proste miejscowości — cała w jednej grupie
    ("Bieniewiec", "", "A"),
    ("Grzymek", "", "A"),
    ("Przeszkoda", "", "A"),
    ("Stara Bukówka", "", "A"),
    ("Władysławów", "", "A"),
    ("Zalesie", "", "A"),
    ("Józefina", "", "B"),
    ("Osowiec", "", "B"),
    ("Wycinki Osowskie", "", "B"),
    ("Jastrzębnik", "", "C"),
    ("Lisówek", "", "C"),
    ("Ojrzanów", "", "C"),
    ("Ojrzanów Towarzystwo", "", "C"),
    ("Pieńki Zarębskie", "", "C"),
    ("Zaręby", "", "C"),
    ("Żelechów", "", "C"),
    ("Bartoszówka", "", "D"),
    ("Bolesławek", "", "D"),
    ("Grzegorzewice", "", "D"),
    ("Grzmiąca", "", "D"),
    ("Lasek", "", "D"),
    ("Oddział", "", "D"),
    ("Petrykozy", "", "D"),
    ("Pieńki Słubickie", "", "D"),
    ("Piotrkowice", "", "D"),
    ("Redlanka", "", "D"),
    ("Rumianka", "", "D"),
    ("Skuły", "", "D"),
    ("Słubica A", "", "D"),
    ("Słubica B", "", "D"),
    ("Słubica Dobra", "", "D"),
    ("Słubica Wieś", "", "D"),
    ("Ciepłe", "", "E"),
    ("Ciepłe A", "", "E"),
    # Musuły — podział po ulicach
    ("Musuły", "Akacjowa", "A"),
    ("Musuły", "Brzozowa", "A"),
    ("Musuły", "Świerkowa", "A"),
    ("Musuły", "Al. Dębowa", "B"),
    ("Musuły", "Folwarczna", "B"),
    ("Musuły", "Zdrojowa", "B"),
    # Huta Żabiowolska — podział po ulicach
    ("Huta Żabiowolska", "Dobra", "B"),
    ("Huta Żabiowolska", "Mazowiecka", "B"),
    ("Huta Żabiowolska", "Przy Trasie", "B"),
    ("Huta Żabiowolska", "Rydzowa", "B"),
    ("Huta Żabiowolska", "Brzozowa", "B"),
    ("Huta Żabiowolska", "Polna", "E"),       # każda inna ulica → E
    ("Huta Żabiowolska", "Leśna", "E"),
    # Siestrzeń — podział po ulicach
    ("Siestrzeń", "Baśniowa", "C"),
    ("Siestrzeń", "Graniczna", "C"),
    ("Siestrzeń", "Koniecpolska", "C"),
    ("Siestrzeń", "Leśna", "A"),              # każda inna ulica → A
    ("Siestrzeń", "Polna", "A"),
    # Kaleń — podział po ulicach
    ("Kaleń", "Jaśminowa", "C"),
    ("Kaleń", "Forsycji", "D"),
    ("Kaleń", "Różana", "E"),                 # każda inna ulica → E
    # Kaleń Towarzystwo
    ("Kaleń Towarzystwo", "Fiołkowa", "C"),
    ("Kaleń Towarzystwo", "Słoneczna", "E"),  # każda inna ulica → E
    # Nowa Bukówka — podział po ulicach
    ("Nowa Bukówka", "Gajowa", "A"),
    ("Nowa Bukówka", "Zielony Gaj", "A"),
    ("Nowa Bukówka", "Dzikiej Róży", "D"),
    ("Nowa Bukówka", "Rumiankowa", "D"),
    ("Nowa Bukówka", "Skulska", "D"),
    ("Nowa Bukówka", "Warszawska", "D"),
    # Żabia Wola — podział po ulicach
    ("Żabia Wola", "Księżycowa", "A"),
    ("Żabia Wola", "Przejazdowa 19", "A"),
    ("Żabia Wola", "Przejazdowa 35", "A"),
    ("Żabia Wola", "Ziołowa", "C"),
    ("Żabia Wola", "Różana", "E"),            # każda inna ulica → E
    ("Żabia Wola", "", "E"),                  # bez ulicy → E (reszta)
])
def test_get_group(city: str, street: str, expected: str) -> None:
    assert get_group(city, street) == expected


def test_get_group_unknown_city_raises() -> None:
    with pytest.raises(ValueError, match="Nie znaleziono grupy"):
        get_group("Nieistniejące Miasto")


def test_get_group_case_insensitive() -> None:
    assert get_group("żabia wola", "księżycowa") == "A"
    assert get_group("ŻABIA WOLA", "KSIĘŻYCOWA") == "A"
    assert get_group("Żabia Wola", "Księżycowa") == "A"


# ---------------------------------------------------------------------------
# Testy parse_schedule() — wymagają pobrania PDF
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_parse_schedule_has_all_waste_types(parsed_schedule: dict) -> None:
    assert set(parsed_schedule.keys()) == _ALL_WASTE_TYPES


@pytest.mark.integration
def test_parse_schedule_has_all_groups(parsed_schedule: dict) -> None:
    for wtype in _ALL_WASTE_TYPES:
        groups = set(parsed_schedule[wtype].keys())
        missing = {"A", "B", "C", "D", "E"} - groups
        assert not missing, f"{wtype}: brakuje grup {missing}"


@pytest.mark.integration
@pytest.mark.parametrize("waste_type,expected_count", [
    ("Papier i tektura", 26),
    ("Tworzywa sztuczne i metal", 26),
    ("Szkło", 4),
])
def test_parse_schedule_date_counts(
    parsed_schedule: dict,
    waste_type: str,
    expected_count: int,
) -> None:
    for group in "ABCDE":
        dates = parsed_schedule[waste_type][group]
        assert abs(len(dates) - expected_count) <= 1, (
            f"{waste_type} / Grupa {group}: {len(dates)} terminów, oczekiwano ~{expected_count}"
        )


@pytest.mark.integration
def test_parse_schedule_dates_in_correct_year(parsed_schedule: dict) -> None:
    for wtype, groups in parsed_schedule.items():
        for group, dates in groups.items():
            for d in dates:
                assert d.year == _YEAR, (
                    f"{wtype} / Grupa {group}: data {d} poza rokiem {_YEAR}"
                )


@pytest.mark.integration
def test_parse_schedule_dates_sorted(parsed_schedule: dict) -> None:
    for wtype, groups in parsed_schedule.items():
        for group, dates in groups.items():
            assert dates == sorted(dates), (
                f"{wtype} / Grupa {group}: daty nie są posortowane"
            )


@pytest.mark.integration
def test_parse_schedule_szklo_quarterly(parsed_schedule: dict) -> None:
    """Szkło odbierane raz na kwartał — daty powinny być rozłożone w całym roku."""
    for group in "ABCDE":
        dates = parsed_schedule["Szkło"][group]
        months = {d.month for d in dates}
        # Powinny być miesiące z różnych kwartałów
        assert len(months) >= 3, f"Szkło Grupa {group}: za mało różnych miesięcy {months}"


@pytest.mark.integration
def test_parse_schedule_papier_biweekly(parsed_schedule: dict) -> None:
    """Papier odbierany co 2 tygodnie — odstęp między datami ~14 dni."""
    for group in "ABCDE":
        dates = parsed_schedule["Papier i tektura"][group]
        for a, b in zip(dates, dates[1:]):
            gap = (b - a).days
            assert 10 <= gap <= 18, (
                f"Papier Grupa {group}: nieoczekiwany odstęp {gap} dni między {a} a {b}"
            )


# ---------------------------------------------------------------------------
# Testy scrape_pdf_url() — wymagają sieci
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_scrape_pdf_url_returns_correct_url() -> None:
    url = scrape_pdf_url(_YEAR)
    assert url == _PDF_URL_2026


@pytest.mark.integration
def test_scrape_pdf_url_excludes_utrudniony() -> None:
    url = scrape_pdf_url(_YEAR)
    assert "utrudniony" not in url


def test_scrape_pdf_url_unknown_year_raises() -> None:
    with pytest.raises(RuntimeError, match="Nie znaleziono linku"):
        scrape_pdf_url(1900)


# ---------------------------------------------------------------------------
# Testy Source — end-to-end (wymagają sieci)
# ---------------------------------------------------------------------------


@pytest.mark.integration
@pytest.mark.parametrize("name,params", TEST_CASES.items())
def test_source_fetch_test_cases(name: str, params: dict) -> None:
    src = Source(**params)
    entries = src.fetch()
    assert len(entries) > 0, f"{name}: fetch() zwróciło pustą listę"
    for e in entries:
        assert isinstance(e.date, date)
        assert isinstance(e.type, str)
        assert e.type in _ALL_WASTE_TYPES


@pytest.mark.integration
def test_source_fetch_url_override() -> None:
    """Parametr url= powinien pominąć scraper strony gminy."""
    src = Source(city="Żabia Wola", url=_PDF_URL_2026)
    entries = src.fetch()
    assert len(entries) > 0


def test_source_fetch_uses_url_override_not_scraper(real_pdf: bytes) -> None:
    """Gdy podano url=, scrape_pdf_url nie powinno być wywoływane."""
    with patch("zabiawola_pl.scrape_pdf_url") as mock_scrape, \
         patch("zabiawola_pl._make_request", return_value=real_pdf):
        src = Source(city="Żabia Wola", url=_PDF_URL_2026)
        entries = src.fetch()
        mock_scrape.assert_not_called()
    assert len(entries) > 0
