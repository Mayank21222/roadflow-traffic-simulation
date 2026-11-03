"""Small local HTTP server for the traffic-simulation prototype."""
from __future__ import annotations

import json
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from .demo import DEMO_SCENARIO
from .engine import Simulation

ROOT = Path(__file__).resolve().parent.parent


def run_payload(payload):
    """Validate and execute a JSON API payload; separated for API-level testing."""
    if not isinstance(payload, dict):
        raise ValueError("request body must be a JSON object")
    scenario = payload.get("scenario", DEMO_SCENARIO)
    ticks = max(1, min(int(payload.get("ticks", 60)), 5000))
    engine = Simulation(scenario)
    return {"scenario": scenario, "results": engine.run(ticks)}


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT / "web"), **kwargs)

    def _json(self, data, status=HTTPStatus.OK):
        encoded = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self):
        if self.path == "/api/scenario":
            return self._json(DEMO_SCENARIO)
        return super().do_GET()

    def do_POST(self):
        if self.path != "/api/run":
            return self._json({"error": "Not found"}, HTTPStatus.NOT_FOUND)
        try:
            length = int(self.headers.get("Content-Length", 0))
            payload = json.loads(self.rfile.read(length) or b"{}")
            self._json(run_payload(payload))
        except (ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
            self._json({"error": f"Invalid scenario: {exc}"}, HTTPStatus.BAD_REQUEST)


def main():
    server = ThreadingHTTPServer(("127.0.0.1", 8000), Handler)
    print("Traffic simulation running at http://127.0.0.1:8000")
    server.serve_forever()


if __name__ == "__main__":
    main()
