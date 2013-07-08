# README

### Introduktion

Ett python-"API" till SGS' lediga objekt. Lär utökas med möjligheter till bevakning med automatiska mejl etc.

### Hurusom använda

Placera önskade sökområden i `desired_areas.conf`. En per rad, se exempel.
Övriga önskemål (hyra, area, lägenhetstyp) specificeras i `sgskoll.conf`.
Kör `sgskoll.py` så bör programmet presentera för tillfället tillgängliga
objekt som passar in på sökkriterierna.

### TODO

* Fler önskemål i sökprofil (hiss etc) baserat på `Properties`
* Notifiering på lämpligt vis
* Generering av default-configs
* Lämpligt sätt att cachea resultatet från API:t (för tillfället måste `sampledata` raderas manuellt för att programmet ska hämta ny info vid körning)
* När notifiering finns: hålla koll på redan sedda poster (tuple av objektid och slutdatum t.ex., kan rensas baserat på passerat slutdatum)
* Hämta och visa info om genomsnittlig kötid på träffar (måste crawla alla områden, behöver alltså cachas)
* Omstrukturering av alltihopet!

### Dataformat

Andra spännande fält:

| Fält | Typ   | Beskrivning | Exempel |
| ---- | :---: | ----------: | ------: |
| ObjectTypeDescription | sträng | lägenhetstyp | "Enkelrum med kokskåp" |
| ObjectSubDescription | sträng | lägenhetstyp (kort) | "Enkelrum" |
| ObjectSubGroup | nummer | lägenhetstyp (id) | se nedan. |
| ObjectArea | sträng | yta | "20" |
| ObjectAreaSort | nummer | yta | 20.0 |
| ObjectFloor | sträng | våning (alltid tre tecken bred) | "3  ", "BV " |
| RentPerMonth | sträng | månadshyra | "2478", "5484" |
| RentPerMonthSort | nummer | månadshyra | 2478, 5484 |
| SeekAreaNo | nummer | id för området (Olofshöjd, Rotary etc.) | ids ej, använd SeekAreaDescription |
| SeekAreaDescription | sträng | område | "Olofshöjd", "Ostkupan", "Postgatan" |
| StreetName | sträng | gatunamn | "Dr Lindhs Gata", "Uppstigen" |
| StreetNo | nummer | gatnummer (utan bokstav) | 6, 464 |
| StreetChar | sträng | lägenhetsnummer (även gatnummerbokstav) | "Läg 1117:02", "Rum 34", "B Rum 114" |
| Street | sträng | adress | "Gamla Ceresgatan 9 Läg 3:4" |
| PlaceName | sträng | "Göteborg". Bra att veta! | "Göteborg" |
| CountInterest | nummer | antal intresseanmälningar (!) | 56, 88 |
| EndPeriodMP | sträng | sista ansökningstidpunkt | "2013-07-07T23:59:59" |
| EndPeriodMPDateString | sträng | sista ansökningsdag | "2013-07-07" |
| FreeFrom | sträng | ledig från | "2013-10-01 |
| DesiredFreeFrom | sträng | ja, ni fattar. | "2013-08-31T00:00:00" |
| DesiredFreeFromString | sträng | se ovan. | "2013-08-31" |
| Properties | lista med objekt | saker som "Hiss", "El ingår", "10-månadershyra" | se nedan. |

`ObjectSubGroupNo` anger lägenhetstyp. Kök/kokskåp/kokvrå måste läsas från `ObjectTypeDescription`.

| Värde | Typ              |
| ----: | ---------------: |
| 1     | 1 rum            |
| 2     | 2 rum            |
| 3     | 3 rum            |
| 4     | 4 rum            |
| 5     | Enkelrum         |
| 6     | Dubbelrum        |
| 7     | 3 rum och kokvrå |
| 8     | 4 rum och kokvrå |

`Properties` har följande intressanta fält:

| Fält | Typ   | Beskrivning | Exempel |
| ---- | :---: | ----------: | ------: |
| PropertyDescription | sträng | beskrivning | "10-månadershyra", "Omöblerat" |
| PropertyUrl | sträng | URL till info om property i fråga | ids int |
| SyndicatePropertyNo | nummer | numeriskt id på property | 5, 31 |

Några värden på `SyndicatePropertyNo` (likartade properties tycks dela nummer och kan ej skiljas åt på annat vis än namn):

| Värde | Betydelse        |
| ----: | ---------------: |
| 0 | Öppen planlösning |
| 1 | Balkong, Inglasad balkong |
| 3 | Hiss |
| 5 | 10-månadershyra |
| 6 | El ingår |
| 7 | IT-uppkoppling ingår |
| 8 | Markplan |
| 9 | Möblerat |
| 10 | Preliminär debiterad el ingår |
| 18 | Preliminär debiterad varmvatten ingår [sic] |
| 21 | Badkar |
| 30 | Persienner ingår |
| 31 | Omöblerat |
| 32 | Säkerhetsdörr |
