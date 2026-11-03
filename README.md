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

`app/engine.py` holds routing, signals, capacity, movement and metrics. `app/demo.py` holds the synthetic scenario. `app/server.py` provides `GET /api/scenario` and `POST /api/run`; `web/` is a dependency-free browser client. The browser exports JSON locally, without storing data remotely.

## Verification

`tests/test_engine.py` covers valid/disconnected routing, vehicle completion, signal waiting, road capacity queues, flyover separation, metric creation, and fixed-seed repeatability. Run the command above before changing the model. The browser workflow was also checked with headless Chrome; see `VALIDATION.md` for the exact checks and their limits.

## Known limitations

The model is deliberately aggregate: no lane changing, vehicle classes, turning geometry, collision avoidance, dynamic route choice, pedestrian phases, spillback beyond exit queues, or real-world calibration. Map geometry is a schematic and does not represent a surveyed road layout. The demo flyover is isolated and carries no demand, so it shows 0% utilisation; its grade separation is covered by the routing test rather than by visible traffic.

## Deployment

Status: **not deployed**. The application is local-only by default: `app/server.py` binds to `127.0.0.1:8000` and has no authentication or rate limiting.

A free deployment is practical on [Render](https://render.com/) as a Python web service, but the current server must first be made deployment-aware:

1. In `app/server.py`, bind to `0.0.0.0` and read the port from the environment, for example `host = os.environ.get("HOST", "127.0.0.1")` and `port = int(os.environ.get("PORT", "8000"))`, then pass both to `ThreadingHTTPServer`.
2. Push the repository to GitHub and create a Render **Web Service** with the Python runtime.
3. Set the start command to `python3 -m app.server` and the environment variable `HOST=0.0.0.0`. Render supplies `PORT` (default 10000).
4. Use the free instance plan. Free services spin down after 15 minutes of inactivity and take about a minute to wake.

No deployment was performed in this session, so no public URL is claimed. Hugging Face Docker Spaces now require a paid plan; GitHub Pages cannot run the Python API; PythonAnywhere's free tier would need a WSGI adapter. A tunnel to the local server can provide a temporary share, but it is not a durable deployment.
