from pathlib import Path
from unittest.mock import MagicMock, patch

from floriday_magic_wand.client import FloridayClient, FloridayConfig


def test_build_url() -> None:
    client = FloridayClient(
        FloridayConfig(
            base_url="https://api.floriday.io/",
            token="abc",
            media_endpoint="/suppliers/v1/media",
        )
    )
    assert client._url() == "https://api.floriday.io/suppliers/v1/media"


def test_multipart_contains_title_and_file(tmp_path: Path) -> None:
    image = tmp_path / "image.png"
    image.write_bytes(b"png")

    client = FloridayClient(FloridayConfig(base_url="https://example.com", token="abc"))
    body, content_type = client._build_multipart_body(image, title="Demo")

    assert b'name="title"' in body
    assert b"Demo" in body
    assert b'filename="image.png"' in body
    assert b"png" in body
    assert "multipart/form-data; boundary=" in content_type


def test_upload_media_calls_urlopen(tmp_path: Path) -> None:
    image = tmp_path / "image.png"
    image.write_bytes(b"png")

    client = FloridayClient(FloridayConfig(base_url="https://example.com", token="abc"))

    fake_response = MagicMock()
    fake_response.read.return_value = b'{"id":"media-1"}'
    fake_response.__enter__.return_value = fake_response

    with patch("floriday_magic_wand.client.urlopen", return_value=fake_response) as mock_open:
        result = client.upload_media(image, title="Demo")

    assert result == {"id": "media-1"}
    assert mock_open.call_count == 1


def test_list_media_supports_items_payload() -> None:
    client = FloridayClient(FloridayConfig(base_url="https://example.com", token="abc"))

    fake_response = MagicMock()
    fake_response.read.return_value = b'{"items":[{"id":"1","title":"Rose"}]}'
    fake_response.__enter__.return_value = fake_response

    with patch("floriday_magic_wand.client.urlopen", return_value=fake_response):
        result = client.list_media()

    assert result == [{"id": "1", "title": "Rose"}]
