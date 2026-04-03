# Analiza źródła danych — Gmina Żabia Wola

## Strona gminy

URL bazowy: `https://www.zabiawola.pl/971,harmonogram-odbioru-odpadow`

### Struktura nawigacji (2026)

```
/971,harmonogram-odbioru-odpadow
  └── ?tresc=17010   → link do PDF głównego harmonogramu
  └── ?tresc=17131   → link do PDF posesji z utrudnionym dojazdem
```

Linki do PDF-ów są osadzone w treści podstrony — nie są bezpośrednio widoczne na liście głównej.

### Znane pliki PDF

| Rok | Opis | tresc | URL pliku |
|-----|------|-------|-----------|
| 2024 | Główny | 14313 | `plik,4805,...` (bezpośredni link) |
| 2025 | Główny | 15780 | (do ustalenia) |
| 2026 | Główny | 17010 | `plik,5464,harmonogram-harmonogram-odbioru-odpadow-2026r.pdf` |
| 2026 | Posesje z utrudnionym dojazdem | 17131 | `plik,5489,utrudniony-dojazd-harmonogram-2026.pdf` |

### Wzorzec URL-i

Co roku pojawia się nowy parametr `?tresc=`. Automatyczne wykrywanie wymaga scrapowania strony głównej.

Algorytm:
1. Pobierz `https://www.zabiawola.pl/971,harmonogram-odbioru-odpadow`
2. Znajdź link `?tresc=XXXXX` z aktualnym rokiem w treści (lub najnowszy)
3. Pobierz podstronę `?tresc=XXXXX`
4. Wyciągnij href do pliku `.pdf` (wzorzec `plik,\d+,.+\.pdf`)
5. Skonstruuj pełny URL: `https://www.zabiawola.pl/{href}`

---

## Analiza pliku PDF (zweryfikowana empirycznie)

### Metadane

- Rozmiar: ~2 MB
- Stron: **2**
- Wymiary: 297 × 210 mm (A4 poziomo)
- Narzędzie: Adobe Illustrator (eksport PDF, 2025-12-16)
- Czcionki: Lato Bold, Lato Black, Lato Regular (**osadzone — tekst jest selectable!**)

### Warstwa tekstowa

**`pdfplumber` wyciąga tekst** — OCR nie jest potrzebne. ✓

Problem: Adobe Illustrator używa niestandardowego kodowania znaków. Polskie litery ze znakami diakrytycznymi są kodowane jako sekwencje `(cid:XX)`, np. `(cid:15)` zamiast `ó`. Znaki ASCII (cyfry, daty, litery bez diakrytyków) są czytelne bez problemu.

**Strona 1:** Tabela harmonogramu (główna zawartość)  
**Strona 2:** Tekst informacyjny o zmianach w 2026 (czytelny, polskie znaki w normie)

### Struktura strony 1 — tabela

Tabela: **26 wierszy × 7 kolumn**, lecz faktycznie **5 grup** (kolumny A–E, kolumny 3 i 6 to artefakty merged cells).

#### Grupy odbioru (kolumny)

| Grupa | Kolumna pdfplumber | Miejscowości (czytelne fragmenty) |
|-------|--------------------|----------------------------------|
| A | 0 | BIENIEWICE, GRZYMEK, JÓZEFINA, MUSUŁY (część ulic) |
| B | 1 | JÓZEFINA (cd.), MUSUŁY (inne ulice) |
| C | 2 | JASTRZĘBNIK, LISÓWEK, KALEŃ (ul. Jaśminowa), KALEŃ TOWARZYSTWO (ul. Fiołkowa), OJRZANÓW, PIEŃKI ZARĘBSKIE, SIESTRZE[Ń]... |
| D | 4 | BARTOSZÓWKA, BOLESŁAWEK, GRZEGORZEWICE, GRZMIĄCA, KALEŃ (ul. Forsycji), LASEK, NOWA BUKÓWKA... |
| E | 5 | CIEPŁE, CIEPŁE A, KALEŃ TOWARZYSTWO (bez ul. Fiołkowej), HUTA ŻABIOWOLSKA... |

#### Typy odpadów i wiersze tabeli

| Wiersze | Zawartość |
|---------|-----------|
| 0–1 | Nazwy miejscowości/ulic dla każdej grupy |
| 2 | Etykiety: PAPIER/TEKTURA, TWORZYWA SZTUCZNE/METAL |
| 3–5 | Daty odbioru papieru i tworzyw sztucznych (co 2 tygodnie) |
| 6 | Etykieta: SZKŁO |
| 7 | Daty szkła (raz na kwartał, 4 daty) |
| 8–10 | BIOODPADY OGRODOWE + daty |
| 12–15 | BIOODPADY KUCHENNE + daty; ZMIESZANE ODPADY KOMUNALNE + daty |
| 16–17 | POPIÓŁ Z PALENISK DOMOWYCH + daty (raz na miesiąc) |
| 18–20 | GABARYTY, ZUŻYTY SPRZĘT, ELEKTROŚMIECI, TEKSTYLIA + daty (ze zgłoszeniem) |
| 21–23 | GRUZ, OPONY, LEKI, AKUMULATORY |
| 25 | Dane kontaktowe firmy (EKO-HETMAN) |

#### Przykładowe daty odbioru papieru/tworzyw (2026)

| Grupa | Pierwsze daty |
|-------|---------------|
| A | 5.01, 19.01, 2.02, 16.02, 2.03, 16.03, 30.03… |
| B | 6.01, 20.01, 3.02, 17.02, 3.03, 17.03, 31.03… |
| C | 7.01, 21.01, 4.02, 18.02, 4.03, 18.03, 1.04… |
| D | 8.01, 22.01, 5.02, 19.02, 5.03, 19.03, 2.04… |
| E | 9.01, 23.01, 6.02, 20.02, 6.03, 20.03, 3.04… |

---

## Wyzwania techniczne

| Problem | Status | Rozwiązanie |
|---------|--------|-------------|
| Warstwa tekstowa w PDF | ✓ Rozwiązane | `pdfplumber` działa |
| Polskie znaki (CID encoding) | ⚠ Częściowy problem | Nazwy miejscowości częściowo zakodowane; daty i etykiety typów odpadów czytelne |
| Wykrywanie kolumn tabeli | ⚠ Problematyczne | Merged cells powodują, że daty z różnych grup wpadają do jednej komórki |
| Zmiana URL co roku | 🔲 Do zrobienia | Scrapowanie strony głównej |

### Kluczowy problem: CID encoding

Nazwy miejscowości zawierają `(cid:XX)` zamiast polskich znaków. Możliwe podejścia:
1. **Twarda mapa CID → znak** — wymaga analizy fontu z PDF (np. `pdfminer` low-level API)
2. **Rozmyta identyfikacja** — porównanie fragmentów czytelnych z bazą znanych miejscowości gminy
3. **Hardkodowana mapa miejscowości → grupa** — stabilna rok do roku (gmina nie zmienia granic), wymaga jednorazowej ręcznej weryfikacji

Podejście 3 jest najrobustne dla integracji HACS (brak zależności od jakości PDF).

---

→ Plan implementacji: [02-plan-implementacji.md](02-plan-implementacji.md)
