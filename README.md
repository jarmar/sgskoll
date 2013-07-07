# README

### Introduktion

Ett python-"API" till SGS' lediga objekt. Lär utökas med möjligheter till bevakning med automatiska mejl etc.

### Hurusom använda

Placera en fil som heter `Momentum-API-KEY.secret` i samma mapp, innehållandes dylik API-nyckel. Detta krav lär försvinna inom mycket kort.

Än så länge är programmet inte så användbart. Hav förtröstan.

### TODO

Själva databehandlingen är simpel. Lite `filter` liksom.

* Konfigformat för att specificera sökprofil
* Notifiering enligt sökprofil

### Dataformat

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


Andra spännande fält:

| Fält | Typ   | Beskrivning | Exempel |
| ---- | :---: | ----------: | ------: |
| ObjectTypeDescription | sträng | lägenhetstyp | "Enkelrum med kokskåp" |
| ObjectSubDescription | sträng | lägenhetstyp (kort) | "Enkelrum" |
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
| Properties | lista med objekt | saker som "Hiss", "El ingår", "10-månadershyra" | |
