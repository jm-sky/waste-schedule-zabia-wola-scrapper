# Plan implementacji — źródło hacs_waste_collection_schedule

## Cel

Stworzyć plik `zabiawola_pl.py` jako źródło (`source`) dla integracji
[hacs_waste_collection_schedule](https://github.com/mampfes/hacs_waste_collection_schedule).

---

## Architektura rozwiązania

```
zabiawola_pl.py
├── discover_pdf_url()     # Scrapuje stronę gminy → zwraca aktualny URL PDF
├── download_pdf()         # Pobiera PDF do pamięci
├── extract_text()         # pdftotext lub OCR (tesseract)
├── parse_schedule()       # Parsuje tekst → {ulica: [(data, typ), ...]}
└── Source.fetch()         # Główny punkt wejścia → lista Collection
```

---

## Etapy

### Etap 1 — Rozpoznanie PDF ✓ ZAKOŃCZONE

**Wynik:** `pdfplumber` wyciąga tekst poprawnie. OCR niepotrzebne.

**Problem:** Polskie znaki diakrytyczne zakodowane jako `(cid:XX)` (artefakt Adobe Illustrator).  
**Decyzja:** Hardkodowana mapa `miejscowość → grupa (A–E)` — stabilna rok do roku, nie zależy od jakości kodowania PDF. Daty są w pełni czytelne (ASCII).

### Etap 2 — Scraper URL PDF

```python
import requests
from bs4 import BeautifulSoup

BASE = "https://www.zabiawola.pl"
LIST_URL = f"{BASE}/971,harmonogram-odbioru-odpadow"

def discover_pdf_url(year: int) -> str:
    # 1. Pobierz stronę listową
    # 2. Znajdź link ?tresc=XXXXX dla danego roku
    # 3. Pobierz podstronę
    # 4. Wyciągnij href do pliku .pdf
    # 5. Zwróć pełny URL
    ...
```

### Etap 3 — Parser PDF

Zależy od wyniku Etapu 1. Docelowa struktura danych:

```python
# Słownik: klucz = nazwa ulicy/miejscowości, wartość = lista kolekcji
schedule: dict[str, list[Collection]] = {}
```

### Etap 4 — Klasa Source

```python
TITLE = "Gmina Żabia Wola"
DESCRIPTION = "Waste collection schedule for Gmina Żabia Wola, Poland"
URL = "https://www.zabiawola.pl/971,harmonogram-odbioru-odpadow"
TEST_CASES = [
    {"street": "Żabia Wola"},  # wypełnić po poznaniu struktury PDF
]

class Source:
    def __init__(self, street: str):
        self._street = street

    def fetch(self) -> list[Collection]:
        pdf_url = discover_pdf_url(year=datetime.date.today().year)
        text = extract_text(download_pdf(pdf_url))
        schedule = parse_schedule(text)
        return schedule.get(self._street, [])
```

### Etap 5 — Pliki dla HACS PR

| Plik | Lokalizacja w repo HACS |
|------|------------------------|
| `zabiawola_pl.py` | `custom_components/waste_collection_schedule/waste_collection_schedule/source/` |
| `zabiawola_pl.md` | `doc/source/` |
| `test_zabiawola_pl.py` | `tests/` |

---

## Zależności Python

### Minimalne (preferowane dla HACS)

| Biblioteka | Zastosowanie |
|-----------|--------------|
| `requests` | HTTP (już w HA) |
| `beautifulsoup4` | Scraping strony |
| `pdfminer.six` | Ekstrakcja tekstu z PDF |

### Fallback (jeśli PDF jest graficzny)

| Biblioteka | Problem |
|-----------|---------|
| `pdf2image` | Wymaga Poppler (system) |
| `pytesseract` | Wymaga Tesseract (system) |

Jeśli tekst w PDF jest graficzny → konieczne przemyślenie podejścia lub zgłoszenie do HACS z niestandardowymi zależnościami.

---

## Harmonogram prac

1. [x] Pobrać PDF i zweryfikować ekstrakcję tekstu (`pdfplumber`)
2. [x] Zrozumieć strukturę tabeli w PDF (5 grup A–E, typy odpadów, wiersze z datami)
3. [ ] Ręcznie przypisać wszystkie miejscowości/ulice do grup A–E (weryfikacja danych w PDF)
4. [ ] Napisać scraper URL PDF (scrapowanie strony gminy)
5. [ ] Napisać parser dat z tabeli PDF
6. [ ] Napisać klasę `Source` + `TEST_CASES`
7. [ ] Napisać dokumentację `zabiawola_pl.md`
8. [ ] Napisać testy `test_zabiawola_pl.py`
9. [ ] Fork + PR do `mampfes/hacs_waste_collection_schedule`
