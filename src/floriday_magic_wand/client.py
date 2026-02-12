from __future__ import annotations

import json
import mimetypes
import os
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request, urlopen


@dataclass
class FloridayConfig:
    """Configuration for Floriday Supplier API integration."""

    base_url: str = os.getenv("FLORIDAY_BASE_URL", "https://api.floriday.io")
    token: str = os.getenv("FLORIDAY_TOKEN", "")
    media_endpoint: str = os.getenv("FLORIDAY_MEDIA_ENDPOINT", "/suppliers/v1/media")
    timeout_seconds: int = int(os.getenv("FLORIDAY_TIMEOUT_SECONDS", "30"))


class FloridayClient:
    """Simple Floriday Supplier API client for media upload and listing."""

    def __init__(self, config: FloridayConfig | None = None) -> None:
        self.config = config or FloridayConfig()
        if not self.config.token:
            raise ValueError("FLORIDAY_TOKEN ontbreekt. Zet een geldige API token in je omgeving.")

    def _url(self) -> str:
        return f"{self.config.base_url.rstrip('/')}{self.config.media_endpoint}"

    def _build_multipart_body(
        self,
        file_path: Path,
        *,
        title: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> tuple[bytes, str]:
        boundary = f"----FloridayMagicWand{uuid.uuid4().hex}"
        lines: list[bytes] = []

        form_fields: dict[str, Any] = {}
        if title:
            form_fields["title"] = title
        if metadata:
            form_fields.update(metadata)

        for key, value in form_fields.items():
            lines.extend(
                [
                    f"--{boundary}".encode(),
                    f'Content-Disposition: form-data; name="{key}"'.encode(),
                    b"",
                    str(value).encode(),
                ]
            )

        mime_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
        file_bytes = file_path.read_bytes()
        lines.extend(
            [
                f"--{boundary}".encode(),
                f'Content-Disposition: form-data; name="file"; filename="{file_path.name}"'.encode(),
                f"Content-Type: {mime_type}".encode(),
                b"",
                file_bytes,
                f"--{boundary}--".encode(),
                b"",
            ]
        )

        body = b"\r\n".join(lines)
        content_type = f"multipart/form-data; boundary={boundary}"
        return body, content_type

    def _request_json(self, request: Request) -> dict[str, Any] | list[Any]:
        try:
            with urlopen(request, timeout=self.config.timeout_seconds) as response:
                raw = response.read().decode("utf-8")
        except HTTPError as error:
            detail = error.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"Floriday request mislukt ({error.code}): {detail}") from error

        if not raw:
            return {}
        return json.loads(raw)

    def upload_media(
        self,
        image_path: str | Path,
        *,
        title: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Upload an image file to Floriday media library."""
        file_path = Path(image_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Bestand niet gevonden: {file_path}")

        body, content_type = self._build_multipart_body(file_path, title=title, metadata=metadata)
        request = Request(
            self._url(),
            data=body,
            method="POST",
            headers={
                "Authorization": f"Bearer {self.config.token}",
                "Accept": "application/json",
                "Content-Type": content_type,
            },
        )

        payload = self._request_json(request)
        return payload if isinstance(payload, dict) else {"items": payload}

    def list_media(self) -> list[dict[str, Any]]:
        """List media items from Floriday media library endpoint."""
        request = Request(
            self._url(),
            method="GET",
            headers={
                "Authorization": f"Bearer {self.config.token}",
                "Accept": "application/json",
            },
        )
        payload = self._request_json(request)
        if isinstance(payload, list):
            return [item for item in payload if isinstance(item, dict)]
        if isinstance(payload, dict):
            items = payload.get("items", [])
            if isinstance(items, list):
                return [item for item in items if isinstance(item, dict)]
        return []
