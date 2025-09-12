# NFL PickEm App

Eine Fantasy Football Challenge App mit persistenter Datenspeicherung.

## Features

- **Dashboard** mit Punktestand, Rang und eliminierten Teams
- **Picks** für jede Woche der NFL-Saison
- **Leaderboard** mit korrekter Ex-aequo Rangfolge (1,1,1,4)
- **Alle Picks** mit Privacy-Feature (aktuelle Woche verstecken)
- **Persistente Datenspeicherung** mit automatischem Backup-System
- **Automatischer Neustart** bei Server-Neustarts

## Datenpersistenz

Diese Version der NFL PickEm App verwendet ein **automatisches SQLite-Backup-System**, das:

1. Die Datenbank regelmäßig sichert (alle 5 Minuten)
2. Bei Neustart automatisch die letzte Sicherung wiederherstellt
3. Mehrere Sicherungen vorhält (die letzten 5)
4. Alle Daten dauerhaft speichert, auch wenn der Server neu startet

## Installation auf Render.com

### 1. GitHub Repository erstellen

1. Gehe zu [GitHub](https://github.com) und logge dich ein
2. Klicke auf "New" um ein neues Repository zu erstellen
3. Name: `nfl-pickem-2025` (oder ein anderer Name deiner Wahl)
4. Wähle "Public" oder "Private"
5. Klicke auf "Create repository"
6. Entpacke die ZIP-Datei `nfl-pickem-sqlite-backup.zip` auf deinem Computer
7. Lade alle Dateien in das GitHub Repository hoch (entweder per Drag & Drop oder über Git)

### 2. Render.com App deployen

1. Gehe zu [Render.com](https://render.com) und erstelle einen Account (oder logge dich ein)
2. Klicke auf "New" → "Web Service"
3. Verbinde mit GitHub und wähle dein `nfl-pickem-2025` Repository
4. Gib folgende Einstellungen ein:
   - **Name**: `nfl-pickem-2025` (oder ein anderer Name deiner Wahl)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app_launcher.py`
5. Klicke auf "Create Web Service"

### 3. Erste Nutzung

1. Warte bis die App deployed ist (kann einige Minuten dauern)
2. Öffne die App-URL (z.B. `https://nfl-pickem-2025.onrender.com`)
3. Die Datenbank wird automatisch initialisiert und mit Beispieldaten gefüllt
4. Logge dich mit einem der Benutzerkonten ein:
   - Manuel / Manuel1
   - Daniel / Daniel1
   - Raff / Raff1
   - Haunschi / Haunschi1

## Wichtige Hinweise

- **Render.com Free Tier**: Der Server schläft nach Inaktivität ein, aber alle Daten bleiben dank des Backup-Systems erhalten
- **Erste Anfrage nach Inaktivität**: Kann 30-60 Sekunden dauern, bis der Server aufwacht
- **Datenbank-Backups**: Werden automatisch im `db_backups` Verzeichnis gespeichert

## Fehlerbehebung

- **App startet nicht**: Überprüfe die Logs in Render.com unter "Logs"
- **Datenbank-Probleme**: Die App versucht automatisch, die letzte funktionierende Sicherung wiederherzustellen
- **Verlorene Daten**: Überprüfe das `db_backups` Verzeichnis für verfügbare Sicherungen

## Updates und Änderungen

Um Änderungen an der App vorzunehmen:
1. Aktualisiere die Dateien in deinem GitHub Repository
2. Render.com wird automatisch ein neues Deployment starten
3. Die Datenbank bleibt dank des Backup-Systems erhalten

## Lokale Entwicklung

1. Klone das Repository: `git clone https://github.com/dein-username/nfl-pickem-2025.git`
2. Installiere die Abhängigkeiten: `pip install -r requirements.txt`
3. Starte die App: `python app_launcher.py`
4. Öffne im Browser: `http://localhost:5000`

## Dateien und Struktur

- `app.py`: Hauptanwendung (Flask)
- `app_launcher.py`: Starter mit Backup-System
- `db_backup.py`: Datenbank-Backup-Funktionen
- `static/`: Frontend-Dateien (HTML, CSS, JavaScript)
- `instance/`: SQLite-Datenbank
- `db_backups/`: Automatische Datenbank-Sicherungen

Viel Spaß mit deiner NFL PickEm App! 🏈
