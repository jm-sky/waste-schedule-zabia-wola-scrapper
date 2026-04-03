"""
Parser harmonogramu wywozu odpadów Gminy Żabia Wola z pliku PDF.

Wyciąga daty dla każdego typu odpadu per grupę (A–E) na podstawie
współrzędnych słów (podejście coordinate-based, nie table-extraction).

Użycie:
    python src/parse_pdf.py
"""

from __future__ import annotations

import io
import re
import urllib.request
from dataclasses import dataclass, field
from datetime import date

import pdfplumber

PDF_URL = "https://www.zabiawola.pl/plik,5464,harmonogram-harmonogram-odbioru-odpadow-2026r.pdf"

# Granice kolumn (x0) wyznaczone empirycznie na podstawie pozycji dat w sekcji Papier.
# Klucz = nazwa grupy, wartość = (x_min, x_max).
# Grupy odpowiadają dniom tygodnia: A=Pn, B=Wt, C=Śr, D=Cz, E=Pt.
COLUMN_BOUNDS: dict[str, tuple[float, float]] = {
    "A": (0.0, 170.0),    # x: 14–152
    "B": (170.0, 340.0),  # x: 177–315
    "C": (340.0, 495.0),  # x: 345–474
    "D": (495.0, 660.0),  # x: 506–634
    "E": (660.0, 9999.0), # x: 670–803
}

# Granice sekcji (top/y) wyznaczone empirycznie na podstawie etykiet typów odpadów.
# Klucz = typ odpadu, wartość = (y_min, y_max).
SECTION_BOUNDS: dict[str, tuple[float, float]] = {
    "Papier i tektura":                 (175.0, 237.0),  # daty y: 192, 202, 211
    "Tworzywa sztuczne i metal":        (175.0, 237.0),  # te same daty co papier
    "Szkło":                            (237.0, 264.0),  # daty y: 251, 252
    "Bioodpady ogrodowe":               (264.0, 326.0),  # daty y: 282, 310
    "Bioodpady kuchenne":               (326.0, 386.0),  # daty y: 350, 359, 369
    "Zmieszane odpady komunalne":       (326.0, 386.0),  # te same daty co kuchenne
    "Popiół z palenisk domowych":       (386.0, 428.0),  # daty y: 410
    # TODO: Gabaryty i elektroodpady — parser miesza daty odbioru z terminami zgłoszeń;
    # wymaga osobnej logiki rozdzielającej pary (zgłoszenie, odbiór).
}

DATE_RE = re.compile(r"^(\d{1,2})\.(\d{2})$")
CID_RE = re.compile(r"\(cid:\d+\)")


@dataclass
class GroupSchedule:
    group: str
    waste_type: str
    dates: list[date] = field(default_factory=list)


def strip_cid(text: str) -> str:
    """Usuwa sekwencje (cid:XX) z tekstu."""
    return CID_RE.sub("", text)


def fetch_pdf(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req).read()


def assign_group(x0: float) -> str | None:
    for group, (xmin, xmax) in COLUMN_BOUNDS.items():
        if xmin <= x0 < xmax:
            return group
    return None


def assign_waste_type(top: float) -> list[str]:
    types = []
    for wtype, (ymin, ymax) in SECTION_BOUNDS.items():
        if ymin <= top < ymax:
            types.append(wtype)
    return types


def parse_dates(data: bytes, year: int = 2026) -> dict[str, dict[str, list[date]]]:
    """
    Zwraca słownik: {typ_odpadu: {grupa: [date, ...]}}
    """
    result: dict[str, dict[str, list[date]]] = {}

    with pdfplumber.open(io.BytesIO(data)) as pdf:
        page = pdf.pages[0]
        words = page.extract_words(keep_blank_chars=False, x_tolerance=3, y_tolerance=3)

    for w in words:
        # Stripuj CID przed dopasowaniem — cyfry w niektórych komórkach są CID-encoded
        text = strip_cid(w["text"]).rstrip(",")
        m = DATE_RE.match(text)
        if not m:
            continue

        day, month = int(m.group(1)), int(m.group(2))
        try:
            d = date(year, month, day)
        except ValueError:
            continue

        group = assign_group(w["x0"])
        waste_types = assign_waste_type(w["top"])

        if not group or not waste_types:
            continue

        for wtype in waste_types:
            result.setdefault(wtype, {}).setdefault(group, [])
            if d not in result[wtype][group]:
                result[wtype][group].append(d)

    # Posortuj daty
    for wtype in result:
        for group in result[wtype]:
            result[wtype][group].sort()

    return result


def main() -> None:
    print(f"Pobieranie PDF…\n")
    data = fetch_pdf(PDF_URL)
    schedule = parse_dates(data)

    for wtype, groups in schedule.items():
        print(f"{'─' * 60}")
        print(f"  {wtype}")
        print(f"{'─' * 60}")
        for group in sorted(groups):
            dates = groups[group]
            print(f"  Grupa {group} ({len(dates)} terminów):")
            # Pokaż po 8 dat w wierszu
            for i in range(0, len(dates), 8):
                chunk = [d.strftime("%-d.%-m") for d in dates[i:i + 8]]
                print(f"    {', '.join(chunk)}")
        print()


if __name__ == "__main__":
    main()
