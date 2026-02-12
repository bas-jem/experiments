from __future__ import annotations

import argparse
from pathlib import Path

from .client import FloridayClient
from .magic_wand import remove_background


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Magic wand: afbeelding vrijstaand maken en uploaden naar Floriday media library."
    )
    parser.add_argument("input_image", help="Pad naar de bronafbeelding")
    parser.add_argument(
        "--output-dir",
        default="output",
        help="Output map voor vrijstaande PNG (default: output)",
    )
    parser.add_argument("--title", default=None, help="Optionele titel voor Floriday media")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Voer alleen background removal uit en sla upload over",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source = Path(args.input_image)
    output_path = Path(args.output_dir) / f"{source.stem}-transparent.png"

    cleaned = remove_background(source, output_path)
    print(f"Vrijstaande afbeelding opgeslagen: {cleaned}")

    if args.dry_run:
        print("Dry run actief: upload overgeslagen.")
        return

    client = FloridayClient()
    response = client.upload_media(cleaned, title=args.title)
    print("Upload succesvol.")
    print(response)


if __name__ == "__main__":
    main()
