from __future__ import annotations

import json
import threading
import webbrowser
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from core.store import DatasetStore, organ_info


ROOT_DIR = Path(__file__).resolve().parents[1]
STATIC_DIR = ROOT_DIR / "app" / "static"
EXPLAINER_IMAGE_DIR = ROOT_DIR / "data" / "image"
EXPLAINER_IMAGES = {"axial.png", "coronal.png", "sagittal.png"}
# Keep the app on the lightweight teaching sample by default.
DATA_DIR = ROOT_DIR / "data" / "sample_data"
HOST = "127.0.0.1"
PORT = 8765
STORE = DatasetStore(DATA_DIR)


class ReusableThreadingHTTPServer(ThreadingHTTPServer):
    allow_reuse_address = True


class LiverAppHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def log_message(self, format: str, *args: Any) -> None:
        return

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path.startswith("/api/"):
            self.handle_api_get(parsed)
            return
        if parsed.path.startswith("/explainers/"):
            self.handle_explainer_image(parsed)
            return
        if parsed.path == "/":
            self.path = "/index.html"
        super().do_GET()

    def handle_explainer_image(self, parsed: Any) -> None:
        filename = Path(parsed.path).name
        if filename not in EXPLAINER_IMAGES:
            self.send_error(HTTPStatus.NOT_FOUND, "Unknown explainer image")
            return
        image_path = EXPLAINER_IMAGE_DIR / filename
        if not image_path.exists():
            self.send_error(HTTPStatus.NOT_FOUND, "Explainer image not found")
            return
        body = image_path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "image/png")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if not parsed.path.startswith("/api/"):
            self.send_error(HTTPStatus.NOT_FOUND, "Unknown endpoint")
            return
        self.handle_api_post(parsed)

    def handle_api_get(self, parsed: Any) -> None:
        query = parse_qs(parsed.query)
        try:
            if parsed.path == "/api/cases":
                self.send_json({"cases": STORE.list_cases(), "organs": organ_info(), "defaultOrgan": "liver"})
                return
            if parsed.path == "/api/case":
                self.send_json(STORE.get_case_detail(query["patient"][0], query["sequence"][0]))
                return
            if parsed.path == "/api/slice":
                organ_key = query.get("organ", ["liver"])[0]
                self.send_json(STORE.get_slice_payload(query["patient"][0], query["sequence"][0], int(query["index"][0]), organ_key))
                return
            if parsed.path == "/api/volume":
                organ_key = query.get("organ", ["liver"])[0]
                self.send_json(STORE.get_volume_payload(query["patient"][0], query["sequence"][0], organ_key))
                return
            if parsed.path == "/api/orthogonal":
                organ_key = query.get("organ", ["liver"])[0]
                coronal_index = int(query["coronal"][0]) if "coronal" in query else None
                sagittal_index = int(query["sagittal"][0]) if "sagittal" in query else None
                self.send_json(
                    STORE.get_orthogonal_payload(
                        query["patient"][0],
                        query["sequence"][0],
                        int(query["index"][0]),
                        coronal_index,
                        sagittal_index,
                        organ_key,
                    )
                )
                return
        except (KeyError, IndexError, ValueError) as exc:
            self.send_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return
        self.send_json({"error": "Unknown endpoint"}, status=HTTPStatus.NOT_FOUND)

    def handle_api_post(self, parsed: Any) -> None:
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(content_length).decode("utf-8"))
        except json.JSONDecodeError:
            self.send_json({"error": "Invalid JSON body."}, status=HTTPStatus.BAD_REQUEST)
            return

        try:
            if parsed.path == "/api/evaluate":
                result = STORE.evaluate(
                    str(payload["patient"]),
                    str(payload["sequence"]),
                    int(payload["index"]),
                    payload["points"],
                    str(payload.get("organ", "liver")),
                )
                self.send_json(result, status=HTTPStatus.OK if result.get("ok") else HTTPStatus.BAD_REQUEST)
                return
            if parsed.path == "/api/segmentation/start":
                result = STORE.start_segmentation_session(
                    str(payload["patient"]),
                    str(payload.get("organ", "liver")),
                    int(payload.get("count", 10)),
                    int(payload.get("minArea", 500)),
                )
                self.send_json(result)
                return
            if parsed.path == "/api/segmentation/evaluate":
                result = STORE.evaluate_segmentation_session(
                    str(payload["patient"]),
                    str(payload["sequence"]),
                    str(payload.get("organ", "liver")),
                    payload["submissions"],
                )
                self.send_json(result, status=HTTPStatus.OK if result.get("ok") else HTTPStatus.BAD_REQUEST)
                return
        except (KeyError, ValueError, TypeError) as exc:
            self.send_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return
        self.send_json({"error": "Unknown endpoint"}, status=HTTPStatus.NOT_FOUND)

    def send_json(self, payload: dict[str, Any], status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def open_browser() -> None:
    webbrowser.open(f"http://{HOST}:{PORT}")


def main() -> None:
    server = ReusableThreadingHTTPServer((HOST, PORT), LiverAppHandler)
    print(f"Liver segmentation app running at http://{HOST}:{PORT}")
    threading.Timer(1.0, open_browser).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
