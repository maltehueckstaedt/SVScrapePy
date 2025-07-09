# SVScrapePy

## Beschreibung  
`SVScrapePy` ist Selenium-Wrapper zum Scrapen von HISone-Seiten, die voraussichtlich ab Ende 2025 mehr als 50 % der Vorlesungsverzeichnisse staatlicher deutscher Universitäten bereitstellen werden. Mit `SVScrapePy` sollten diese Universitäten mit nur wenigen Anpassungen von CSS-Selektoren problemlos gescraped werden können.

Der Vorteil von `SVScrapePy` gegenüber `SVscrapeR` liegt in deutlich höherer Stabilität und Geschwindigkeit: Während `SVscrapeR` für das Scrapen eines Semesters rund 12 Stunden mit Unterbrechungen benötigt, schafft `SVScrapePy` dies unterbrechungsfrei in etwa 6 Stunden – und kann bei Bedarf auch mehrere Semester am Stück verarbeiten.

## Installation

`SVScrapePy` kann folgendermaßen installiert werden:

```py
pip install --no-cache-dir --force-reinstall git+https://github.com/maltehueckstaedt/SVScrapePy.git
```

## Vorgehen des Paketes

Das Paket geht folgendermaßen im Rahmen des Scrapings vor:

1. Der Remote-Driver wird gestartet.
2. Die Basiswebsite wird aufgerufen und das zu scrapende Semester wird ausgewählt und aufgerufen.
3. Es werden die Base-Informationen gescrapet, d.h. alle Informationen, die auf den Übersichtsseiten der Semester angezeigt werden. 
4. Insbesondere der Titel wird aufbereitet, um über die Suchmaske von HisOne die entsprechenden Kurse zu suchen und zu finden. 
5. Das Scraping wird vorgenommen. Für jeden Kurs wird die Suchmaske aufgesucht, das Semester ausgewählt, der Kurstitel und die Kursnummer in die Maske eingegeben und der Kurs gesucht. Anschließend werden die relevaten Daten des Kurses erhoben. Die gewonnen Informationen werden Zeilenweise zusammengefügt.
6. Alle 100 Kurse erneuert sich der Chromedriver, um höchstmögliche Stabilität zu gewährleisten.
7. Die gewonnenen Daten werden als `.pkl` exportiert. 

## Nutzung

Siehe für eine beispielhafte Anwendung [diese](LINKHERE) Vignette. (ToDo)

## Support

Bei Problemen oder Anregungen bitte das Issue-System des Repos nutzen. Bei akuten Problemen gern zusätzlich an Malte Hückstädt oder (Backup) Eike Schröder wenden. 

