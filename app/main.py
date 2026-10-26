import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlsplit(self.path).path

        if path == "/health":
            status, body = 200, {"status": "healthy"}
        elif path == "/version":
            status, body = 200, {
                "version": os.getenv("APP_VERSION", "0.1.0-dev"),
                "commit": os.getenv("GIT_SHA", "local"),
            }
        else:
            status, body = 404, {"error": "not found"}

        payload = json.dumps(body).encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))

    server = ThreadingHTTPServer((host, port), Handler)
    print(f"API listening on http://{host}:{port}", flush=True)
    server.serve_forever()