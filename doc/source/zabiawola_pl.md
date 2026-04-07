# Gmina Żabia Wola

Support for schedules provided by [Gmina Żabia Wola](https://www.zabiawola.pl/971,harmonogram-odbioru-odpadow), Poland.

## Configuration via configuration.yaml

```yaml
waste_collection_schedule:
  sources:
    - name: zabiawola_pl
      args:
        city: CITY
        street: STREET
```

### Configuration Variables

**city** *(string) (required)*
Name of the locality (miejscowość), e.g. `"Żabia Wola"`, `"Musuły"`, `"Słubica Wieś"`. See the full list below.

**street** *(string) (optional)*
Street name without the `ul.` prefix, e.g. `"Księżycowa"`, `"Al. Dębowa"`. Required for localities that are split across multiple collection groups depending on the street. When omitted, the default group for the locality is used (where applicable).

**url** *(string) (optional)*
Direct URL to the PDF schedule file. When provided, the automatic URL discovery is skipped. Useful for testing or when the auto-discovery fails.

## Examples

### Żabia Wola (remaining streets — default group E)
```yaml
waste_collection_schedule:
  sources:
    - name: zabiawola_pl
      args:
        city: "Żabia Wola"
```

### Żabia Wola, ul. Księżycowa (group A)
```yaml
waste_collection_schedule:
  sources:
    - name: zabiawola_pl
      args:
        city: "Żabia Wola"
        street: "Księżycowa"
```

### Musuły, ul. Akacjowa (group A)
```yaml
waste_collection_schedule:
  sources:
    - name: zabiawola_pl
      args:
        city: "Musuły"
        street: "Akacjowa"
```

### Musuły, Al. Dębowa (group B)
```yaml
waste_collection_schedule:
  sources:
    - name: zabiawola_pl
      args:
        city: "Musuły"
        street: "Al. Dębowa"
```

### Słubica Wieś (whole locality, group D)
```yaml
waste_collection_schedule:
  sources:
    - name: zabiawola_pl
      args:
        city: "Słubica Wieś"
```

## How to get the source arguments

The collection schedule is divided into five groups (A–E) corresponding to weekdays (Monday–Friday). Your group is determined by your locality and, for some localities, your street.

### Locality list by group

**Group A — Monday**
Bieniewiec, Grzymek, Przeszkoda, Stara Bukówka, Władysławów, Zalesie;
Musuły ul.: Akacjowa, Brzozowa, Dębowa, Familijna, Graniczna, Grodziska, Huberta, Jaśminowa, Jutrzenki, Miła, Modrzewiowa, Piękna, Pogodna, Relaksowa, Rusałki, Szałwiowa, Świerkowa;
Nowa Bukówka ul.: Gajowa, Zielony Gaj;
Siestrzeń (except ul. Baśniowa, Graniczna, Koniecpolska);
Żabia Wola ul.: Księżycowa, Przejazdowa 19, Przejazdowa 21, Przejazdowa 23, Przejazdowa 25, Przejazdowa 35.

**Group B — Tuesday**
Józefina, Osowiec, Wycinki Osowskie;
Musuły ul.: Al. Dębowa, Folwarczna, Ku Słońcu, Łowicka, Mazowiecka, Pod Dębami, Przyjazna, Rodzinna, Stokłosy, Szumiących Traw, Wrzosowa, Zdrojowa;
Huta Żabiowolska ul.: Dobra, Mazowiecka, Przy Trasie, Rydzowa, Brzozowa.

**Group C — Wednesday**
Jastrzębnik, Lisówek, Ojrzanów, Ojrzanów Towarzystwo, Pieńki Zarębskie, Zaręby, Żelechów;
Kaleń ul.: Jaśminowa;
Kaleń Towarzystwo ul.: Fiołkowa;
Siestrzeń ul.: Baśniowa, Graniczna, Koniecpolska;
Żabia Wola ul.: Ziołowa.

**Group D — Thursday**
Bartoszówka, Bolesławek, Grzegorzewice, Grzmiąca, Lasek, Oddział, Petrykozy, Pieńki Słubickie, Piotrkowice, Redlanka, Rumianka, Skuły, Słubica A, Słubica B, Słubica Dobra, Słubica Wieś;
Kaleń ul.: Forsycji;
Nowa Bukówka ul.: Dzikiej Róży, Rumiankowa, Skulska, Warszawska.

**Group E — Friday**
Ciepłe, Ciepłe A;
Huta Żabiowolska (except ul. Dobrej, Mazowieckiej, Przy Trasie, Rydzowej, Brzozowej);
Kaleń (except ul. Forsycji, Jaśminowej);
Kaleń Towarzystwo (except ul. Fiołkowej);
Żabia Wola (except ul. Księżycowej, Przejazdowej 19/21/23/25/35, Ziołowej).

You can also check the current schedule PDF at the [gmina website](https://www.zabiawola.pl/971,harmonogram-odbioru-odpadow). The source automatically discovers the current year's PDF URL — no manual updates needed when a new schedule is published.
