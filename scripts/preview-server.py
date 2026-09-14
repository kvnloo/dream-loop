#!/usr/bin/env python3
"""Local demo server with a fixed PNG capture endpoint for visual review."""
import argparse
from datetime import datetime, timezone
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from urllib.parse import unquote, urlparse


COMPARE_HTML = Path(__file__).resolve().parent / "compare.html"


class Handler(SimpleHTTPRequestHandler):
    def _root(self):
        return Path(self.directory).resolve()

    def _denied(self):
        raw = unquote(urlparse(self.path).path)
        if raw.rstrip("/") == "/__compare" or raw == "/__capture":
            return False
        translated = Path(self.translate_path(raw)).resolve()
        root = self._root()
        try:
            rel = translated.relative_to(root)
        except ValueError:
            return True
        return any(part.startswith(".") and part != ".dream-loop" for part in rel.parts)

    def _serve_bytes(self, data, content_type, status=200):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(data)

    def do_GET(self):
        if urlparse(self.path).path.rstrip("/") == "/__compare":
            self._serve_bytes(COMPARE_HTML.read_bytes(), "text/html; charset=utf-8")
            return
        if self._denied():
            self.send_error(404)
            return
        return SimpleHTTPRequestHandler.do_GET(self)

    def do_HEAD(self):
        if urlparse(self.path).path.rstrip("/") == "/__compare":
            data = COMPARE_HTML.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            return
        if self._denied():
            self.send_error(404)
            return
        return SimpleHTTPRequestHandler.do_HEAD(self)

    def do_POST(self):
        if urlparse(self.path).path != "/__capture":
            self.send_error(404)
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 8 <= size <= 20_000_000:
                raise ValueError("Capture must be a PNG under 20 MB")
            data = self.rfile.read(size)
            if len(data) != size or data[:8] != b"\x89PNG\r\n\x1a\n":
                raise ValueError("Invalid PNG capture")
            folder = Path(self.directory) / ".dream-loop" / "captures"
            folder.mkdir(parents=True, exist_ok=True)
            stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-%f")
            capture = folder / f"frame-{stamp}.png"
            capture.write_bytes(data)
            latest = folder / "latest.png"
            part = folder / f"latest.{stamp}.part"
            part.write_bytes(data)
            part.replace(latest)
            payload = json.dumps({"path": str(capture), "latest": str(latest)}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
        except (ValueError, OSError) as error:
            self.send_error(400, str(error))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", default=str(Path.cwd()), help="Workspace to serve (default: current directory)")
    parser.add_argument("--port", type=int, default=4172)
    args = parser.parse_args()
    handler = partial(Handler, directory=str(Path(args.directory).resolve()))
    print(f"Preview http://127.0.0.1:{args.port}; POST PNG to /__capture; compare /__compare", flush=True)
    ThreadingHTTPServer(("127.0.0.1", args.port), handler).serve_forever()
