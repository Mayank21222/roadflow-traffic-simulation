# Roadflow traffic simulation prototype

[Live application](https://roadflow-traffic-simulation.vercel.app/) · [Repository](https://github.com/Mayank21222/roadflow-traffic-simulation) · [Final audit](FINAL_AUDIT.md)

Roadflow is a small web application for exploring an agent-based traffic simulation on a synthetic road network. It demonstrates how road capacity, signals, route connectivity, and grade separation affect throughput, travel and waiting time, queues, and road utilisation. Reviewers can compare a baseline junction, an active grade-separated flyover, and two corridors with different capacities under the same demand rate.

> **Synthetic output, not real-world measurement.** Demand, capacities, coordinates, speeds, and results are invented for demonstration. Roadflow is not calibrated and must not be used for operational, safety, or policy decisions.

## Documentation

| Document | Purpose |
| --- | --- |
| [Final audit](FINAL_AUDIT.md) | Results, fixed findings, provenance, and remaining limitations |
| [Architecture](ARCHITECTURE.md) | Components, API contract, and data flow |
| [Model](MODEL.md) | Agents, ticks, routing, signals, capacity, and metrics |
| [Decisions](DECISIONS.md) | Engineering choices and rejected scope |
| [Validation](VALIDATION.md) | Tests, browser checks, API checks, and deployment verification |
| [OpenCode record](OPENCODE_VERIFICATION.md) | Later verification/audit history and provenance |
| [Git history](GIT_HISTORY.md) | Optional bundle restoration and checksum workflow |

## Quick start

Requires Python 3.9+ and no third-party Python packages.

```bash
python3 -m unittest discover -v
python3 -m compileall -q app tests
python3 -m app.server
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000), choose a scenario, adjust its demand and seed, run it, and download either the scenario JSON or scenario-plus-results JSON.

## Scenarios

| Scenario | What it demonstrates | 80-tick check |
| --- | --- | --- |
| **Synthetic Central Flyover** | Signalised at-grade junction with an intentionally isolated flyover that carries no demand | 83 generated, 76 completed, 7 active |
| **Active Flyover Crossing** | Connected ramps and elevated crossing; at-grade turning traffic stays on the junction | 113 generated, 103 completed, 10 active; 34 of 103 completions used elevated segments |
| **Road Capacity Comparison** | Narrow 4/1 corridors versus wide 12/6 corridors under the same demand rate and seed | 120 generated, 111 completed, 9 active; higher utilisation on the narrow corridor |

Only explicitly connected road endpoints create routes. The baseline flyover crosses the drawing without a junction node, so it cannot be used to turn onto the at-grade network. The active scenario adds usable entry and exit ramps; its ground junction and elevated crossing remain separate graph nodes at the same map coordinates.

## How it works

- The engine is independent of the HTTP/UI layer and uses seeded, discrete time ticks.
- Roads are directed graph edges. Routing is breadth-first by number of roads, and signalised movements must be declared in a green phase.
- Each demand entry performs one seeded Bernoulli arrival attempt per tick. A generated vehicle stores its route, current road, progress, entry tick, and waiting time.
- Each vehicle performs at most one action per tick. It transfers only when its movement is green and the downstream road has spare capacity; otherwise it waits.
- Capacity is an explicit road value or `lanes × 6` agents. Metrics include generated/completed vehicles, average travel and waiting time, maximum exit queue, and per-road utilisation.
- Scenario validation rejects malformed networks, null seeds, non-integer lanes/capacities, and malformed signal movements.

See [MODEL.md](MODEL.md) for the exact rules and [ARCHITECTURE.md](ARCHITECTURE.md) for the API and component boundaries.

## Verification

The final audit passed **24/24** automated tests and Python compilation checks. All three scenarios passed deterministic repeatability checks, and the baseline 80-tick result remained unchanged. Local API, live API, browser, export, stale-response, and responsive checks passed. See [FINAL_AUDIT.md](FINAL_AUDIT.md) for the summary and [VALIDATION.md](VALIDATION.md) for detailed evidence and limits.

## Development provenance

The project began in Codex, and later verification and auditing used OpenCode. The preferred single-session workflow was therefore not followed throughout. This is disclosed rather than hidden.

The original Codex session ID is `01a19f99-911d-7c92-8709-2d7a7534f0b9`; the original JSONL SHA-256 is `2372fc7407dec75186ebb2ebc83ddf9116dcac9842ea351110b42bb775e62e26`; the unlisted log is at <https://gist.github.com/Mayank21222/f2b649a86d0dff0254900449223f1105>. OpenCode history is stored separately in its own local database/log format and is not published. Git author metadata was not rewritten. See [OPENCODE_VERIFICATION.md](OPENCODE_VERIFICATION.md) for the later work record.

## Deployment

Live application: <https://roadflow-traffic-simulation.vercel.app/>

The app is deployed on Vercel's free Hobby plan using the Python runtime. Vercel runs `app/wsgi.py` as a WSGI function; `vercel.json` routes all requests to it, and `pyproject.toml` selects Python 3.12. The function serves the static client and the API endpoints. This is a serverless deployment: there is no persistent process, and cold starts may add latency.

For a persistent web-service deployment such as [Render](https://render.com/), `app/server.py` reads `HOST` and `PORT`:

- `HOST` defaults to `127.0.0.1`; set `HOST=0.0.0.0` on the host.
- `PORT` defaults to `8000`; the host-provided port is used when set.
- Start command: `python3 -m app.server`.

The deployment is unauthenticated and has no rate limiting; it uses only synthetic demo data.

## Limitations

See [MODEL.md](MODEL.md) and [DECISIONS.md](DECISIONS.md) for the full assumptions. The model has no lane changing, vehicle classes, turning geometry, collision avoidance, dynamic route choice, pedestrian phases, spillback beyond exit queues, or real-world calibration. Map geometry is schematic, grade separation is represented by graph connectivity rather than physical 3D geometry, and capacity-comparison arrivals share an RNG stream but are not paired. Browser verification is headless/DOM-based, not a human visual review.
