"""WSGI entrypoint for serverless hosting."""
from __future__ import annotations

import json
from http import HTTPStatus
from pathlib import Path
from urllib.parse import unquote

from .demo import DEMO_SCENARIO
from .server import run_payload

WEB = Path(__file__).resolve().parent.parent / "web"
CONTENT_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".json": "application/json",
    ".svg": "image/svg+xml",
    ".png": "image/png",
    ".ico": "image/x-icon",
}


def _response(start_response, status, body, content_type):
    start_response(
        f"{status.value} {status.phrase}",
        [("Content-Type", content_type), ("Content-Length", str(len(body)))],
    )
    return [body]


def _json(start_response, data, status=HTTPStatus.OK):
    return _response(start_response, status, json.dumps(data).encode(), "application/json")


def _static(start_response, path):
    relative = unquote(path).lstrip("/") or "index.html"
    candidate = (WEB / relative).resolve()
    if candidate != WEB and WEB not in candidate.parents:
        return _json(start_response, {"error": "Not found"}, HTTPStatus.NOT_FOUND)
    if not candidate.is_file():
        return _json(start_response, {"error": "Not found"}, HTTPStatus.NOT_FOUND)
    return _response(
        start_response,
        HTTPStatus.OK,
        candidate.read_bytes(),
        CONTENT_TYPES.get(candidate.suffix, "application/octet-stream"),
    )


def app(environ, start_response):
    method = environ.get("REQUEST_METHOD", "GET").upper()
    path = environ.get("PATH_INFO", "/")

    if path == "/api/scenario":
        if method != "GET":
            return _json(start_response, {"error": "Method not allowed"}, HTTPStatus.METHOD_NOT_ALLOWED)
        return _json(start_response, DEMO_SCENARIO)

    if path == "/api/run":
        if method != "POST":
            return _json(start_response, {"error": "Method not allowed"}, HTTPStatus.METHOD_NOT_ALLOWED)
        try:
            length = int(environ.get("CONTENT_LENGTH") or 0)
            payload = json.loads(environ["wsgi.input"].read(length) or b"{}")
            return _json(start_response, run_payload(payload))
        except (ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
            return _json(start_response, {"error": f"Invalid scenario: {exc}"}, HTTPStatus.BAD_REQUEST)

    if method != "GET":
        return _json(start_response, {"error": "Method not allowed"}, HTTPStatus.METHOD_NOT_ALLOWED)
    return _static(start_response, path)
