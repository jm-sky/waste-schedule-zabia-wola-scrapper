"""
Źródło harmonogramu wywozu odpadów dla Gminy Żabia Wola (Polska).

Docelowa lokalizacja w repozytorium HACS:
  custom_components/waste_collection_schedule/waste_collection_schedule/source/zabiawola_pl.py
"""

from __future__ import annotations

import io
import re
import urllib.request
from datetime import date
from typing import Any

import pdfplumber

# ---------------------------------------------------------------------------
# Metadane wymagane przez hacs_waste_collection_schedule
# ---------------------------------------------------------------------------

TITLE = "Gmina Żabia Wola"
DESCRIPTION = "Waste collection schedule for Gmina Żabia Wola, Poland"
URL = "https://www.zabiawola.pl/971,harmonogram-odbioru-odpadow"
TEST_CASES: dict[str, dict[str, Any]] = {
    "Żabia Wola (reszta)": {"city": "Żabia Wola"},
    "Żabia Wola ul. Księżycowa": {"city": "Żabia Wola", "street": "Księżycowa"},
    "Musuły ul. Akacjowa": {"city": "Musuły", "street": "Akacjowa"},
    "Musuły ul. Al. Dębowa": {"city": "Musuły", "street": "Al. Dębowa"},
    "Słubica Wieś": {"city": "Słubica Wieś"},
}
ICON_MAP = {
    "Papier i tektura": "mdi:newspaper-variant-outline",
    "Tworzywa sztuczne i metal": "mdi:recycle",
    "Szkło": "mdi:bottle-wine-outline",
    "Bioodpady ogrodowe": "mdi:leaf",
    "Bioodpady kuchenne": "mdi:food-apple-outline",
    "Zmieszane odpady komunalne": "mdi:trash-can",
    "Popiół z palenisk domowych": "mdi:fireplace",
}

# ---------------------------------------------------------------------------
# Stałe parsera PDF
# ---------------------------------------------------------------------------

_BASE_URL = "https://www.zabiawola.pl"
_LIST_URL = f"{_BASE_URL}/971,harmonogram-odbioru-odpadow"

# Granice kolumn (x0) wyznaczone empirycznie.
# Grupy A–E odpowiadają dniom: A=Pn, B=Wt, C=Śr, D=Cz, E=Pt.
_COLUMN_BOUNDS: dict[str, tuple[float, float]] = {
    "A": (0.0, 170.0),
    "B": (170.0, 340.0),
    "C": (340.0, 493.0),
    "D": (493.0, 660.0),
    "E": (660.0, 9999.0),
}

# Granice sekcji (y) wyznaczone empirycznie.
_SECTION_BOUNDS: dict[str, tuple[float, float]] = {
    "Papier i tektura": (175.0, 237.0),
    "Tworzywa sztuczne i metal": (175.0, 237.0),
    "Szkło": (237.0, 264.0),
    "Bioodpady ogrodowe": (264.0, 326.0),
    "Bioodpady kuchenne": (326.0, 386.0),
    "Zmieszane odpady komunalne": (326.0, 386.0),
    "Popiół z palenisk domowych": (386.0, 428.0),
    # TODO: Gabaryty i elektroodpady — parser miesza daty odbioru z terminami zgłoszeń;
    # wymaga osobnej logiki rozdzielającej pary (zgłoszenie, odbiór).
}

_CID_RE = re.compile(r"\(cid:\d+\)")
_DATE_RE = re.compile(r"^(\d{1,2})\.(\d{2})$")
_PDF_HREF_RE = re.compile(r"plik,\d+,[^\"']+\.pdf")

# ---------------------------------------------------------------------------
# Mapa miejscowość/ulica → grupa (A–E)
#
# Format wpisów:
#   ("MIEJSCOWOŚĆ",)                → cała miejscowość w danej grupie
#   ("MIEJSCOWOŚĆ", "ulica")        → tylko ta ulica
#   ("MIEJSCOWOŚĆ", "!ulica")       → cała miejscowość OPRÓCZ tej ulicy
#   ("MIEJSCOWOŚĆ", "!ulica1,ulica2,...") → cała miejscowość OPRÓCZ tych ulic
#
# Wpisy są sprawdzane w kolejności — używaj bardziej szczegółowych reguł PRZED ogólnymi.
# ---------------------------------------------------------------------------

_LOCALITY_RULES: dict[str, list[tuple[str, ...]]] = {
    "A": [
        ("BIENIEWIEC",),
        ("GRZYMEK",),
        ("MUSUŁY", "Akacjowa"),
        ("MUSUŁY", "Brzozowa"),
        ("MUSUŁY", "Dębowa"),
        ("MUSUŁY", "Familijna"),
        ("MUSUŁY", "Graniczna"),
        ("MUSUŁY", "Grodziska"),
        ("MUSUŁY", "Huberta"),
        ("MUSUŁY", "Jaśminowa"),
        ("MUSUŁY", "Jutrzenki"),
        ("MUSUŁY", "Miła"),
        ("MUSUŁY", "Modrzewiowa"),
        ("MUSUŁY", "Piękna"),
        ("MUSUŁY", "Pogodna"),
        ("MUSUŁY", "Relaksowa"),
        ("MUSUŁY", "Rusałki"),
        ("MUSUŁY", "Szałwiowa"),
        ("MUSUŁY", "Świerkowa"),
        ("NOWA BUKÓWKA", "Gajowa"),
        ("NOWA BUKÓWKA", "Zielony Gaj"),
        ("SIESTRZEŃ", "!Baśniowa,Graniczna,Koniecpolska"),
        ("PRZESZKODA",),
        ("STARA BUKÓWKA",),
        ("WŁADYSŁAWÓW",),
        ("ZALESIE",),
        ("ŻABIA WOLA", "Księżycowa"),
        ("ŻABIA WOLA", "Przejazdowa 19"),
        ("ŻABIA WOLA", "Przejazdowa 21"),
        ("ŻABIA WOLA", "Przejazdowa 23"),
        ("ŻABIA WOLA", "Przejazdowa 25"),
        ("ŻABIA WOLA", "Przejazdowa 35"),
    ],
    "B": [
        ("JÓZEFINA",),
        ("MUSUŁY", "Al. Dębowa"),
        ("MUSUŁY", "Folwarczna"),
        ("MUSUŁY", "Ku Słońcu"),
        ("MUSUŁY", "Łowicka"),
        ("MUSUŁY", "Mazowiecka"),
        ("MUSUŁY", "Pod Dębami"),
        ("MUSUŁY", "Przyjazna"),
        ("MUSUŁY", "Rodzinna"),
        ("MUSUŁY", "Stokłosy"),
        ("MUSUŁY", "Szumiących Traw"),
        ("MUSUŁY", "Wrzosowa"),
        ("MUSUŁY", "Zdrojowa"),
        ("HUTA ŻABIOWOLSKA", "Dobra"),
        ("HUTA ŻABIOWOLSKA", "Mazowiecka"),
        ("HUTA ŻABIOWOLSKA", "Przy Trasie"),
        ("HUTA ŻABIOWOLSKA", "Rydzowa"),
        ("HUTA ŻABIOWOLSKA", "Brzozowa"),
        ("OSOWIEC",),
        ("WYCINKI OSOWSKIE",),
    ],
    "C": [
        ("JASTRZĘBNIK",),
        ("LISÓWEK",),
        ("KALEŃ", "Jaśminowa"),
        ("KALEŃ TOWARZYSTWO", "Fiołkowa"),
        ("OJRZANÓW",),
        ("OJRZANÓW TOWARZYSTWO",),
        ("PIEŃKI ZARĘBSKIE",),
        ("SIESTRZEŃ", "Baśniowa"),
        ("SIESTRZEŃ", "Graniczna"),
        ("SIESTRZEŃ", "Koniecpolska"),
        ("ZARĘBY",),
        ("ŻELECHÓW",),
        ("ŻABIA WOLA", "Ziołowa"),
    ],
    "D": [
        ("BARTOSZÓWKA",),
        ("BOLESŁAWEK",),
        ("GRZEGORZEWICE",),
        ("GRZMIĄCA",),
        ("KALEŃ", "Forsycji"),
        ("LASEK",),
        ("NOWA BUKÓWKA", "Dzikiej Róży"),
        ("NOWA BUKÓWKA", "Rumiankowa"),
        ("NOWA BUKÓWKA", "Skulska"),
        ("NOWA BUKÓWKA", "Warszawska"),
        ("ODDZIAŁ",),
        ("PETRYKOZY",),
        ("PIEŃKI SŁUBICKIE",),
        ("PIOTRKOWICE",),
        ("REDLANKA",),
        ("RUMIANKA",),
        ("SKUŁY",),
        ("SŁUBICA A",),
        ("SŁUBICA B",),
        ("SŁUBICA DOBRA",),
        ("SŁUBICA WIEŚ",),
    ],
    "E": [
        ("CIEPŁE",),
        ("CIEPŁE A",),
        ("HUTA ŻABIOWOLSKA", "!Dobrej,Mazowieckiej,Przy Trasie,Rydzowej,Brzozowej"),
        ("KALEŃ TOWARZYSTWO", "!Fiołkowej"),
        ("KALEŃ", "!Forsycji,Jaśminowej"),
        ("ŻABIA WOLA", "!Księżycowej,Przejazdowej 19,Przejazdowej 21,Przejazdowej 23,Przejazdowej 25,Przejazdowej 35,Ziołowej"),
    ],
}


# ---------------------------------------------------------------------------
# Wyznaczanie grupy na podstawie miejscowości i ulicy
# ---------------------------------------------------------------------------

def _normalize(text: str) -> str:
    return text.strip().upper()


def get_group(city: str, street: str = "") -> str:
    """
    Zwraca grupę (A–E) dla podanej miejscowości i opcjonalnej ulicy.
    Rzuca ValueError jeśli nie można jednoznacznie ustalić grupy.
    """
    city_norm = _normalize(city)
    street_norm = _normalize(street)

    for group, rules in _LOCALITY_RULES.items():
        for rule in rules:
            rule_city = _normalize(rule[0])
            if rule_city != city_norm:
                continue

            if len(rule) == 1:
                # Cała miejscowość w tej grupie
                return group

            rule_street = rule[1]

            if rule_street.startswith("!"):
                # Cała miejscowość OPRÓCZ wymienionych ulic
                excluded = [_normalize(s) for s in rule_street[1:].split(",")]
                if street_norm not in excluded:
                    return group
            else:
                # Konkretna ulica
                if street_norm == _normalize(rule_street):
                    return group

    raise ValueError(
        f"Nie znaleziono grupy dla: city={city!r}, street={street!r}. "
        f"Sprawdź docs/03-mapa-miejscowosci.md po listę obsługiwanych miejscowości."
    )


# ---------------------------------------------------------------------------
# Scraper URL PDF
# ---------------------------------------------------------------------------

def _make_request(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req, timeout=30).read()


def scrape_pdf_url(year: int) -> str:
    """
    Automatycznie znajduje URL PDF harmonogramu dla podanego roku.
    Scrapuje stronę gminy, szuka linka z rokiem w tekście, pobiera podstronę
    i wyciąga href do pliku PDF.
    """
    html = _make_request(_LIST_URL).decode("utf-8", errors="replace")

    # Znajdź linki ?tresc=XXXXX z rokiem w otaczającym kontekście
    tresc_re = re.compile(
        rf"(?:tresc|redir[^\"']*)\?tresc=(\d+)[^>]*>[^<]*{year}",
        re.IGNORECASE,
    )
    # Szerszy pattern — szukaj wszystkich tresc= i sprawdź kontekst ±200 znaków
    all_tresc = re.findall(r"tresc=(\d+)", html)
    year_tresc = None
    for tresc_id in all_tresc:
        idx = html.find(f"tresc={tresc_id}")
        context = html[max(0, idx - 200) : idx + 200]
        if (
            str(year) in context
            and "harmonogram" in context.lower()
            and "utrudniony" not in context.lower()
        ):
            year_tresc = tresc_id
            break

    if not year_tresc:
        raise RuntimeError(
            f"Nie znaleziono linku z harmonogramem na rok {year} na stronie {_LIST_URL}"
        )

    # Pobierz podstronę z linkiem do PDF
    sub_url = f"{_LIST_URL}?tresc={year_tresc}"
    sub_html = _make_request(sub_url).decode("utf-8", errors="replace")

    # Wyciągnij href do pliku PDF
    m = _PDF_HREF_RE.search(sub_html)
    if not m:
        raise RuntimeError(
            f"Nie znaleziono linku do PDF na stronie {sub_url}"
        )

    return f"{_BASE_URL}/{m.group(0)}"


# ---------------------------------------------------------------------------
# Parser PDF
# ---------------------------------------------------------------------------

def _strip_cid(text: str) -> str:
    return _CID_RE.sub("", text)


def _assign_group_by_x(x0: float) -> str | None:
    for group, (xmin, xmax) in _COLUMN_BOUNDS.items():
        if xmin <= x0 < xmax:
            return group
    return None


def _assign_waste_types_by_y(top: float) -> list[str]:
    return [
        wtype
        for wtype, (ymin, ymax) in _SECTION_BOUNDS.items()
        if ymin <= top < ymax
    ]


def parse_schedule(pdf_data: bytes, year: int) -> dict[str, dict[str, list[date]]]:
    """
    Parsuje PDF i zwraca słownik {typ_odpadu: {grupa: [date, ...]}}.
    """
    result: dict[str, dict[str, list[date]]] = {}

    with pdfplumber.open(io.BytesIO(pdf_data)) as pdf:
        words = pdf.pages[0].extract_words(
            keep_blank_chars=False, x_tolerance=3, y_tolerance=3
        )

    for w in words:
        text = _strip_cid(w["text"]).rstrip(",")
        m = _DATE_RE.match(text)
        if not m:
            continue

        day, month = int(m.group(1)), int(m.group(2))
        try:
            d = date(year, month, day)
        except ValueError:
            continue

        group = _assign_group_by_x(w["x0"])
        waste_types = _assign_waste_types_by_y(w["top"])
        if not group or not waste_types:
            continue

        for wtype in waste_types:
            result.setdefault(wtype, {}).setdefault(group, [])
            if d not in result[wtype][group]:
                result[wtype][group].append(d)

    for wtype in result:
        for group in result[wtype]:
            result[wtype][group].sort()

    return result


# ---------------------------------------------------------------------------
# Klasa Source (punkt wejścia dla hacs_waste_collection_schedule)
# ---------------------------------------------------------------------------

class Source:
    def __init__(self, city: str, street: str = "", url: str = "") -> None:
        self._group = get_group(city, street)
        self._url = url  # opcjonalny override URL PDF

    def fetch(self) -> list[Any]:
        # Import wewnątrz metody — dostępny tylko w środowisku HA
        from waste_collection_schedule import Collection  # type: ignore[import]

        year = date.today().year
        pdf_url = self._url or scrape_pdf_url(year)
        pdf_data = _make_request(pdf_url)
        schedule = parse_schedule(pdf_data, year)

        entries = []
        for waste_type, groups in schedule.items():
            for d in groups.get(self._group, []):
                entries.append(
                    Collection(
                        date=d,
                        t=waste_type,
                        icon=ICON_MAP.get(waste_type),
                    )
                )
        return entries
