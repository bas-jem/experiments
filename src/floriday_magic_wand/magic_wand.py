from __future__ import annotations

from pathlib import Path


def remove_background(input_image: str | Path, output_image: str | Path) -> Path:
    """Remove the background from an image and save it as PNG."""
    source = Path(input_image)
    destination = Path(output_image)

    if not source.exists():
        raise FileNotFoundError(f"Inputbestand bestaat niet: {source}")

    destination.parent.mkdir(parents=True, exist_ok=True)

    # Lazy import keeps unit tests lightweight and gives a clear runtime error.
    try:
        from rembg import remove
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError(
            "Dependency 'rembg' ontbreekt. Installeer requirements.txt of gebruik --dry-run tests."
        ) from exc

    input_bytes = source.read_bytes()
    output_bytes = remove(input_bytes)
    destination.write_bytes(output_bytes)

    return destination
