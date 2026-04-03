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

### Znane pliki PDF (2026)

| Opis | URL |
|------|-----|
| Harmonogram główny 2026 | `https://www.zabiawola.pl/plik,5464,harmonogram-harmonogram-odbioru-odpadow-2026r.pdf` |
| Posesje z utrudnionym dojazdem 2026 | `https://www.zabiawola.pl/plik,5489,utrudniony-dojazd-harmonogram-2026.pdf` |

### Wzorzec URL-i historycznych

- `?tresc=14313` → 2024 główny
- `?tresc=15780` → 2025 główny
- `?tresc=17010` → 2026 główny

Co roku pojawia się nowy parametr `tresc`. Automatyczne wykrywanie wymaga scrapowania strony.

---

## Analiza pliku PDF

### Metadane

- Rozmiar: ~2 MB
- Wymiary: 297 × 210 mm (A4 poziomo)
- Narzędzie: Adobe Illustrator (eksport PDF)
- Data utworzenia: 2025-12-16
- Czcionki: Lato Bold, Lato Black, Lato Regular (osadzone)

### Charakter dokumentu

PDF został wygenerowany z Adobe Illustrator. Istnieją dwa scenariusze:

1. **Tekst jako ścieżki (outline)** — litery skonwertowane do krzywych, brak warstwy tekstowej → wymagane OCR
2. **Tekst z osadzonymi czcionkami** — `pdftotext` powinien działać bezpośrednio

Czcionki Lato są wymienione w metadanych jako osadzone, co sugeruje scenariusz 2 (tekst selectable). Wymaga weryfikacji.

### Przewidywana struktura treści

Na podstawie harmonogramów podobnych gmin PDF prawdopodobnie zawiera tabelę z kolumnami:
- Miejscowość / ulica
- Typ odpadu (zmieszane, bio, plastik/metal/papier, szkło, gabaryty)
- Daty odbioru (lista lub kalendarz)

---

## Wyzwania

| Problem | Opis | Prawdopodobne rozwiązanie |
|---------|------|--------------------------|
| Format PDF | Brak gwarancji warstwy tekstowej | `pdftotext` → fallback OCR (`tesseract`) |
| Zmiana URL co roku | Nowy `?tresc=` co rok | Scrapowanie strony głównej |
| Zmiana numeru pliku | `plik,5464,...` zmienia się | Wyciąganie URL z treści podstrony |
| Brak API | Tylko PDF | Parsowanie lokalne |
| Wiele adresów | Każda ulica może mieć inny harmonogram | Parametr `street` w source |

---

## Następne kroki

1. Pobrać PDF i sprawdzić czy `pdftotext` wyciąga tekst
2. Ustalić dokładną strukturę tabeli w PDF
3. Zaprojektować parser
4. Zaprojektować scraper URL-a (auto-wykrywanie)

→ Szczegóły: [02-plan-implementacji.md](02-plan-implementacji.md)
