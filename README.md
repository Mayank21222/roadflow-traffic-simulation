# Roadflow traffic simulation prototype

Roadflow is a small, local web application for exploring an agent-based traffic simulation on a synthetic road network. It is a prototype: its inputs are invented for demonstration and its outputs are simulated, not calibrated forecasts.

## Run locally

Requires Python 3.9+ and no third-party packages.

```bash
python3 -m unittest discover -v
python3 -m app.server
```

Then open [http://127.0.0.1:8000](http://127.0.0.1:8000). Use the scenario controls to adjust demand and seed, run it, and download either the scenario JSON or scenario-plus-results JSON.

## Demo scenario

`Synthetic Central Flyover` contains a one-lane west approach and two-lane east departure, a north/south approach, a signal-controlled at-grade junction, and a separate two-lane flyover. The flyover crosses the drawing without a junction node, so it cannot be used to turn onto the at-grade network; only explicitly connected road endpoints create routes.

## Model and metrics

The engine (`app/engine.py`) is independent of the HTTP/UI layer. It uses a seeded random number generator and discrete time ticks. Each vehicle is an individual agent with an origin, destination, shortest valid road route, current road, progress, and waiting time.

- **Capacity:** each road holds `lanes × 6` agents unless it declares an explicit capacity.
- **Travel time:** `ceil(length / speed_limit)` ticks; length and speed units are synthetic, relative model values.
- **Signals:** a configured movement is permitted only during its green phase. An agent waits at its current road exit for red or when the downstream road is full.
- **Vehicles generated/completed:** respectively admitted to their origin road and fully exited their destination road.
- **Average travel time:** completion tick minus entry tick, averaged over completed agents.
- **Average waiting time:** ticks spent queued at a road exit, averaged over completed agents.
- **Maximum queue:** largest count of agents waiting at any road exit during the run.
- **Road utilisation:** mean occupancy divided by capacity, sampled each tick.

## Architecture

`app/engine.py` holds routing, signals, capacity, movement and metrics. `app/demo.py` holds the synthetic scenario. `app/server.py` provides `GET /api/scenario` and `POST /api/run`; `app/wsgi.py` exposes the same app as a WSGI entrypoint for serverless hosting; `web/` is a dependency-free browser client. The browser exports JSON locally, without storing data remotely.

## Verification

`tests/test_engine.py` covers valid/disconnected routing, vehicle completion, signal waiting, road capacity queues, flyover separation, metric creation, and fixed-seed repeatability. Run the command above before changing the model. The browser workflow was also checked with headless Chrome; see `VALIDATION.md` for the exact checks and their limits.

## Known limitations

The model is deliberately aggregate: no lane changing, vehicle classes, turning geometry, collision avoidance, dynamic route choice, pedestrian phases, spillback beyond exit queues, or real-world calibration. Map geometry is a schematic and does not represent a surveyed road layout. The demo flyover is isolated and carries no demand, so it shows 0% utilisation; its grade separation is covered by the routing test rather than by visible traffic.

## Deployment

Live application: <https://roadflow-traffic-simulation.vercel.app>

The app is deployed on Vercel's free Hobby plan using the Python runtime. Vercel runs `app/wsgi.py` as a WSGI function; `vercel.json` routes all requests to it, and `pyproject.toml` selects Python 3.12. The function serves both the static client and the two API endpoints. This is a serverless deployment: there is no persistent process, and cold starts may add latency.

For a persistent web-service deployment such as [Render](https://render.com/), `app/server.py` now reads `HOST` and `PORT`:

- `HOST` defaults to `127.0.0.1`; set `HOST=0.0.0.0` on the host.
- `PORT` defaults to `8000`; the host-provided port is used when set.
- Start command: `python3 -m app.server`.

Render's free web service remains suitable, but no Render credentials were available in this environment, so the live deployment uses Vercel. The deployment is unauthenticated and has no rate limiting; it uses only synthetic demo data.
