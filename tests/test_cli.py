from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from floriday_magic_wand import cli


def test_cli_dry_run_skips_upload(tmp_path: Path) -> None:
    input_file = tmp_path / "rose.jpg"
    input_file.write_bytes(b"jpg")
    output_file = tmp_path / "output" / "rose-transparent.png"

    args = SimpleNamespace(
        input_image=str(input_file),
        output_dir=str(tmp_path / "output"),
        title="Demo",
        dry_run=True,
    )

    with patch("floriday_magic_wand.cli.parse_args", return_value=args), patch(
        "floriday_magic_wand.cli.remove_background", return_value=output_file
    ) as remove_mock, patch("floriday_magic_wand.cli.FloridayClient") as client_mock:
        cli.main()

    remove_mock.assert_called_once()
    client_mock.assert_not_called()
