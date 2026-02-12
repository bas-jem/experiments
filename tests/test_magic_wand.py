from pathlib import Path

import pytest

from floriday_magic_wand.magic_wand import remove_background


def test_remove_background_missing_input(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        remove_background(tmp_path / "missing.jpg", tmp_path / "out.png")
