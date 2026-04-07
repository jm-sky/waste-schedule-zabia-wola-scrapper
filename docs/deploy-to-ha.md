# Instrukcja wdrożenia zabiawola_pl do Home Assistant

## Cel

Zainstalować plik źródłowy `zabiawola_pl.py` w integracji `waste_collection_schedule` działającej w Home Assistant (Docker) i zweryfikować poprawność działania.

## Krok 1: Zlokalizuj katalog source integracji

Uruchom:

```bash
find / -path "*/custom_components/waste_collection_schedule/waste_collection_schedule/source" -type d 2>/dev/null
```

Oczekiwany wynik (przykład):

```
/config/custom_components/waste_collection_schedule/waste_collection_schedule/source
```

Zapamiętaj tę ścieżkę — będzie potrzebna w kolejnych krokach. Oznaczamy ją jako `SOURCE_DIR`.

## Krok 2: Wgraj plik zabiawola_pl.py

Plik `zabiawola_pl.py` powinien trafić do `SOURCE_DIR`. Pobierz go bezpośrednio z tego repozytorium:

```bash
curl -o SOURCE_DIR/zabiawola_pl.py \
  https://raw.githubusercontent.com/jm-sky/waste-schedule-zabia-wola-scrapper/main/src/zabiawola_pl.py
```

> Zastąp `SOURCE_DIR` faktyczną ścieżką z Kroku 1.

Zweryfikuj, że plik istnieje:

```bash
ls -la SOURCE_DIR/zabiawola_pl.py
```

## Krok 3: Dodaj konfigurację do configuration.yaml

Otwórz `/config/configuration.yaml` i dodaj (lub uzupełnij istniejącą sekcję `waste_collection_schedule`):

```yaml
waste_collection_schedule:
  sources:
    - name: zabiawola_pl
      args:
        city: "Żabia Wola"
        street: "Księżycowa"
```

Dostosuj `city` i `street` do swojego adresu (patrz lista miejscowości w `doc/source/zabiawola_pl.md`).

## Krok 4: Zweryfikuj składnię YAML

```bash
docker exec homeassistant python3 -c "import yaml; yaml.safe_load(open('/config/configuration.yaml'))" && echo "OK"
```

Jeśli polecenie wypisuje `OK` — składnia jest poprawna. W przeciwnym razie popraw błędy przed restartem.

## Krok 5: Zrestartuj Home Assistant

```bash
docker restart homeassistant
```

> Zastąp `homeassistant` faktyczną nazwą kontenera HA. Możesz ją sprawdzić przez `docker ps`.

Odczekaj ~60 sekund na pełny restart.

## Krok 6: Sprawdź logi

```bash
docker logs homeassistant --tail 100 | grep -i "zabiawola\|waste_collection\|error" 
```

Brak błędów związanych z `zabiawola` = integracja załadowana poprawnie.

## Krok 7: Zweryfikuj encje w HA

W Home Assistant przejdź do:
**Settings → Devices & Services → Entities**

Wyszukaj `waste` lub `zabia`. Powinny pojawić się encje dla każdego typu odpadu, np.:

- `sensor.waste_collection_papier_i_tektura`
- `sensor.waste_collection_szklo`
- `sensor.waste_collection_zmieszane_odpady_komunalne`
- itd.

Każda encja powinna wyświetlać datę następnego odbioru.

## Rozwiązywanie problemów

**Błąd `ModuleNotFoundError: pdfplumber`**

Integracja wymaga biblioteki `pdfplumber`. Sprawdź czy jest zainstalowana w kontenerze HA. Jeśli nie — waste_collection_schedule powinien ją mieć jako zależność. Jeśli brakuje, zgłoś to.

**Błąd `ValueError: Nie znaleziono grupy`**

Podana kombinacja `city`/`street` nie jest obsługiwana. Sprawdź listę miejscowości w `doc/source/zabiawola_pl.md`.

**Encje nie pojawiają się po restarcie**

Sprawdź logi szczegółowo:

```bash
docker logs homeassistant 2>&1 | grep -A5 "zabiawola\|waste_collection_schedule"
```
