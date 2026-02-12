from __future__ import annotations

import cgi
import json
import shutil
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from tempfile import NamedTemporaryFile

from .client import FloridayClient
from .magic_wand import remove_background


def render_index_html(message: str = "") -> str:
    return f"""<!doctype html>
<html lang=\"nl\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Floriday Magic Wand UI</title>
  <style>
    body {{ font-family: sans-serif; margin: 2rem; max-width: 900px; }}
    .tabs {{ display: flex; gap: .5rem; margin-bottom: 1rem; }}
    .tab {{ padding: .6rem 1rem; border: 1px solid #999; border-radius: .4rem; cursor: pointer; }}
    .tab.active {{ background: #1f6feb; color: white; border-color: #1f6feb; }}
    .panel {{ display:none; border:1px solid #ddd; padding:1rem; border-radius:.5rem; }}
    .panel.active {{ display:block; }}
    .msg {{ margin-bottom: 1rem; padding:.6rem; background:#f6f8fa; border:1px solid #d0d7de; border-radius:.4rem; }}
    .media-item {{ border-bottom:1px solid #eee; padding:.5rem 0; }}
    pre {{ white-space: pre-wrap; word-break: break-word; }}
  </style>
</head>
<body>
  <h1>Floriday Magic Wand</h1>
  {f'<div class="msg">{message}</div>' if message else ''}

  <div class=\"tabs\">
    <button class=\"tab active\" data-target=\"upload-panel\">Upload & Vrijstaand</button>
    <button class=\"tab\" data-target=\"media-panel\">Beeldbank</button>
  </div>

  <section id=\"upload-panel\" class=\"panel active\">
    <form action=\"/upload\" method=\"post\" enctype=\"multipart/form-data\">
      <p><label>Afbeelding: <input type=\"file\" name=\"image\" accept=\"image/*\" required /></label></p>
      <p><label>Titel (optioneel): <input type=\"text\" name=\"title\" /></label></p>
      <p><button type=\"submit\">Vrijstaand maken + uploaden</button></p>
    </form>
  </section>

  <section id=\"media-panel\" class=\"panel\">
    <p><button id=\"refresh-media\">Vernieuw beeldbank</button></p>
    <div id=\"media-list\">Nog niet geladen.</div>
  </section>

<script>
const tabs = document.querySelectorAll('.tab');
for (const tab of tabs) {{
  tab.addEventListener('click', () => {{
    tabs.forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
    tab.classList.add('active');
    document.getElementById(tab.dataset.target).classList.add('active');
  }});
}}

document.getElementById('refresh-media').addEventListener('click', async () => {{
  const list = document.getElementById('media-list');
  list.textContent = 'Laden...';
  try {{
    const response = await fetch('/api/media');
    const data = await response.json();
    if (!Array.isArray(data) || data.length === 0) {{
      list.textContent = 'Geen media gevonden.';
      return;
    }}
    list.innerHTML = data.map(item => `
      <div class=\"media-item\">
        <strong>${{item.title || item.name || 'Zonder titel'}}</strong>
        <pre>${{JSON.stringify(item, null, 2)}}</pre>
      </div>
    `).join('');
  }} catch (error) {{
    list.textContent = 'Kon beeldbank niet laden: ' + error;
  }}
}});
</script>
</body>
</html>
"""


class MagicWandHandler(BaseHTTPRequestHandler):
    def _send_html(self, html: str, status: HTTPStatus = HTTPStatus.OK) -> None:
        payload = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _send_json(self, payload: object, status: HTTPStatus = HTTPStatus.OK) -> None:
        encoded = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/":
            self._send_html(render_index_html())
            return
        if self.path == "/api/media":
            try:
                items = FloridayClient().list_media()
                self._send_json(items)
            except Exception as exc:
                self._send_json({"error": str(exc)}, status=HTTPStatus.BAD_GATEWAY)
            return

        self._send_json({"error": "Not found"}, status=HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/upload":
            self._send_json({"error": "Not found"}, status=HTTPStatus.NOT_FOUND)
            return

        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={
                "REQUEST_METHOD": "POST",
                "CONTENT_TYPE": self.headers.get("Content-Type", ""),
            },
        )

        if "image" not in form or not getattr(form["image"], "file", None):
            self._send_html(render_index_html("Geen afbeelding geüpload."), status=HTTPStatus.BAD_REQUEST)
            return

        image_field = form["image"]
        title_field = form.getvalue("title")
        title = title_field if isinstance(title_field, str) and title_field.strip() else None

        with NamedTemporaryFile(delete=False, suffix=".upload") as temp_input:
            shutil.copyfileobj(image_field.file, temp_input)
            temp_input_path = Path(temp_input.name)

        processed_path = Path("output") / f"{temp_input_path.stem}-transparent.png"

        try:
            cleaned = remove_background(temp_input_path, processed_path)
            result = FloridayClient().upload_media(cleaned, title=title)
        except Exception as exc:
            self._send_html(render_index_html(f"Upload mislukt: {exc}"), status=HTTPStatus.BAD_GATEWAY)
            return
        finally:
            if temp_input_path.exists():
                temp_input_path.unlink()

        self._send_html(render_index_html(f"Upload succesvol: {result}"))


def run_server(host: str = "0.0.0.0", port: int = 8080) -> None:
    httpd = ThreadingHTTPServer((host, port), MagicWandHandler)
    print(f"UI gestart op http://{host}:{port}")
    httpd.serve_forever()


if __name__ == "__main__":
    run_server()
