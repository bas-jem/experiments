# Floriday Magic Wand

Een eenvoudige Python-tool om:
1. Een productafbeelding vrijstaand te maken (achtergrond verwijderen), en
2. Het resultaat te uploaden naar de Floriday Suppliers media library.

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

## Gebruik

```bash
PYTHONPATH=src python -m floriday_magic_wand.cli ./images/roos.jpg --title "Roos vrijstaand"
```

Alleen vrijstaand maken zonder upload:

```bash
PYTHONPATH=src python -m floriday_magic_wand.cli ./images/roos.jpg --dry-run
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
- Dat de CLI bij `--dry-run` geen upload probeert.
- Dat er een nette fout komt als inputbestand ontbreekt.

### 2) Lokale smoke test (zonder upload)

Maak eerst een testafbeelding in `./images/` en voer uit:

```bash
PYTHONPATH=src python -m floriday_magic_wand.cli ./images/roos.jpg --dry-run
```

Verwacht resultaat:
- Er wordt een transparante PNG aangemaakt in `output/`.
- Geen call naar Floriday API.

### 3) Echte upload test naar Floriday

Zorg dat `FLORIDAY_TOKEN` gezet is en voer uit:

```bash
PYTHONPATH=src python -m floriday_magic_wand.cli ./images/roos.jpg --title "Roos vrijstaand"
```

Verwacht resultaat:
- Console toont `Upload succesvol.`
- Response bevat media-informatie vanuit Floriday.

## Opmerkingen

- Deze tool gebruikt `rembg` voor background removal.
- Het Floriday media endpoint kan per implementatie verschillen; pas `FLORIDAY_MEDIA_ENDPOINT` aan op jouw tenant/API-versie.
