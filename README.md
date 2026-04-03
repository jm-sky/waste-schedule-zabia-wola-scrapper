# waste-schedule-zabia-wola-scrapper

Narzędzie do pobierania i parsowania harmonogramu wywozu odpadów Gminy Żabia Wola, przygotowane z myślą o integracji z [hacs_waste_collection_schedule](https://github.com/mampfes/hacs_waste_collection_schedule) dla Home Assistant.

## Cel

Gmina Żabia Wola publikuje harmonogram odbioru odpadów jako plik PDF (tworzony w Adobe Illustrator — brak warstwy tekstowej, dane zawarte jako grafika). Celem projektu jest:

1. Automatyczne wykrywanie aktualnego URL-a PDF na stronie gminy
2. Ekstrakcja danych z PDF (OCR lub inna metoda)
3. Parsowanie do postaci strukturalnej (adresy, typy odpadów, daty)
4. Udostępnienie jako źródło (`source`) dla `hacs_waste_collection_schedule`

## Strona gminy

- Lista harmonogramów: `https://www.zabiawola.pl/971,harmonogram-odbioru-odpadow`
- Harmonogram 2026: `https://www.zabiawola.pl/plik,5464,harmonogram-harmonogram-odbioru-odpadow-2026r.pdf`
- Harmonogram 2026 (posesje z utrudnionym dojazdem): `https://www.zabiawola.pl/plik,5489,utrudniony-dojazd-harmonogram-2026.pdf`

## Struktura projektu

```
docs/           # Analizy i plany
src/            # Kod źródłowy
.venv/          # Wirtualne środowisko Python 3
```

## Środowisko

```bash
source .venv/bin/activate
```

## Dokumentacja

Szczegółowe analizy i plan implementacji: [`docs/`](docs/)
