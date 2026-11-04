# Architecture

```text
Browser UI (web/)
  ├─ GET /api/scenarios ─────> app/demo.py
  ├─ GET /api/scenario ──────> app/demo.py (baseline compatibility)
  ├─ POST /api/run ──────────> app/server.py → app/engine.py
  └─ JSON downloads locally <─ scenario and response results

Tests (tests/test_engine.py) ─> engine and API payload boundary
```

## Components

- `app/demo.py`: the built-in synthetic scenario catalog: baseline, active flyover, and capacity comparison.
- `app/engine.py`: schema validation, topology/routing, agent state, signal checking, capacity and metric calculation. It has no HTTP or UI dependency.
- `app/server.py`: standard-library HTTP adapter. It serves static UI assets, provides the scenario catalog, parses JSON, and invokes the testable `run_payload` boundary.
- `web/index.html`, `web/style.css`, `web/app.js`: dependency-free single-page client. It selects a scenario, edits seed/demand/ticks, calls the API, draws the schematic network with at-grade/elevated/ramp classes, presents metrics, and generates local JSON downloads.
- `tests/test_engine.py`: standard-library `unittest` coverage for the engine and API payload boundary.

## API contract

### `GET /api/scenario`

Returns the baseline synthetic scenario JSON. This remains for compatibility.

### `GET /api/scenarios`

Returns the ordered catalog of built-in scenario JSON objects.

### `POST /api/run`

Accepts an object such as:

```json
{"scenario": {"...": "scenario schema"}, "ticks": 80}
```

`scenario` is optional and defaults to the demo. `ticks` defaults to 60 and is clamped to 1–5000 at the API boundary. A successful response is `{ "scenario": ..., "results": ... }`. Invalid JSON/schema/payloads return HTTP 400 with an error message.

## Local operation and boundaries

The application keeps state only for the duration of one request. The UI's “Reset” restores in-browser controls; “Export scenario” and “Export results” download JSON rather than sending user data anywhere. There is no database, identity layer, cloud service, or external traffic-data dependency.

The local server binds to `127.0.0.1` by default; `HOST` and `PORT` can override this for a hosted web service. The Vercel deployment uses `app/wsgi.py` instead of the local socket server.
