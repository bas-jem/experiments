# Floriday Magic Wand

Een eenvoudige Python-tool om:
1. Een productafbeelding vrijstaand te maken (achtergrond verwijderen), en
2. Het resultaat te uploaden naar de Floriday Suppliers media library.

Daarnaast zit er nu een **web UI** bij met twee tabs:
- **Upload & Vrijstaand**: upload een afbeelding, verwijder achtergrond, upload naar Floriday.
- **Beeldbank**: bekijk media-items uit Floriday via de API.

## Installatie

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuratie

Zet deze environment variables:

```bash
export FLORIDAY_TOKEN="<jouw_api_token>"
export FLORIDAY_BASE_URL="https://api.floriday.io"
# Optioneel als endpoint wijzigt:
# export FLORIDAY_MEDIA_ENDPOINT="/suppliers/v1/media"
```

## CLI gebruik

```bash
PYTHONPATH=src python -m floriday_magic_wand.cli ./images/roos.jpg --title "Roos vrijstaand"
```

Alleen vrijstaand maken zonder upload:

```bash
PYTHONPATH=src python -m floriday_magic_wand.cli ./images/roos.jpg --dry-run
```

## Web UI starten

```bash
PYTHONPATH=src python -m floriday_magic_wand.web
```

Open daarna:

```text
http://localhost:8080
```

## Hoe kun je het testen?

### 1) Unit tests draaien

```bash
PYTHONPATH=src python -m pytest -q
```

Wat je hiermee controleert:
- URL-opbouw richting Floriday endpoint.
- Multipart payload voor upload.
- Dat upload via HTTP-client wordt aangeroepen.
- Dat media listing (`list_media`) werkt met `items` payload.
- Dat de CLI bij `--dry-run` geen upload probeert.
- Dat er een nette fout komt als inputbestand ontbreekt.
- Dat de web UI HTML beide tabs bevat.

### 2) Lokale smoke test UI

```bash
PYTHONPATH=src python -m floriday_magic_wand.web
```

Ga naar `http://localhost:8080`:
- Tab **Upload & Vrijstaand**: upload een afbeelding.
- Tab **Beeldbank**: klik op **Vernieuw beeldbank**.

### 3) Echte upload test naar Floriday

Zorg dat `FLORIDAY_TOKEN` gezet is en upload via de web UI of via CLI.

## Opmerkingen

- Deze tool gebruikt `rembg` voor background removal.
- Het Floriday media endpoint kan per implementatie verschillen; pas `FLORIDAY_MEDIA_ENDPOINT` aan op jouw tenant/API-versie.

## Merge conflicts oplossen

Als je bij mergen/rebasen conflicts krijgt, volg deze stappen:

```bash
# 1) Haal laatste refs op
git fetch origin

# 2) Ga naar je feature branch
git checkout work

# 3) Rebase op target branch (bijv. main)
git rebase origin/main
```

Bij conflicts:

```bash
# Bekijk conflicterende bestanden
git status

# Los markers op in bestanden (<<<<<<, ======, >>>>>>)
# Daarna per bestand:
git add <bestand>

# Ga verder met rebase
git rebase --continue
```

Als je wilt stoppen:

```bash
git rebase --abort
```

Na een succesvolle rebase:

```bash
# Force-push met lease (veiligste variant na rebase)
git push --force-with-lease
```

Tip: als conflict vooral in `README.md` of tests zit, kies eerst één versie als basis en voeg daarna handmatig de juiste delen samen.
