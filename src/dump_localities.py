"""
Wyciąga czytelne fragmenty nazw miejscowości z PDF harmonogramu.
Służy do ręcznego uzupełnienia mapy miejscowość → grupa (A–E).

Użycie:
    python src/dump_localities.py
"""

import io
import re
import urllib.request

import pdfplumber

PDF_URL = "https://www.zabiawola.pl/plik,5464,harmonogram-harmonogram-odbioru-odpadow-2026r.pdf"

# Kolumny pdfplumber odpowiadające grupom A–E
GROUP_COLS = {
    "A": 0,
    "B": 1,
    "C": 2,
    "D": 4,
    "E": 5,
}


def clean(text: str) -> str:
    """Usuwa sekwencje CID i normalizuje białe znaki."""
    text = re.sub(r"\(cid:\d+\)", "", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n+", "\n", text)
    return text.strip()


def main() -> None:
    print(f"Pobieranie PDF: {PDF_URL}\n")
    req = urllib.request.Request(PDF_URL, headers={"User-Agent": "Mozilla/5.0"})
    data = urllib.request.urlopen(req).read()

    with pdfplumber.open(io.BytesIO(data)) as pdf:
        page = pdf.pages[0]
        table = page.extract_tables()[0]

    # Wiersze 0 i 1 zawierają nazwy miejscowości
    locality_rows = table[0:2]

    for group, col in GROUP_COLS.items():
        print(f"{'='*60}")
        print(f"GRUPA {group} (kolumna {col})")
        print(f"{'='*60}")
        for row_idx, row in enumerate(locality_rows):
            cell = row[col] if col < len(row) else None
            if cell:
                print(f"[wiersz {row_idx}]:\n{clean(cell)}\n")
        print()


if __name__ == "__main__":
    main()
