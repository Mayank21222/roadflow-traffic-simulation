# Validation record

## Automated checks

Run from the project directory:

```bash
python3 -m unittest discover -v
PYTHONPYCACHEPREFIX=/private/tmp/roadflow-pycache python3 -m compileall -q app tests
```

At the latest verification, the unit suite passed **21/21** tests:

- baseline 80-tick regression;
- connected and prohibited routing;
- vehicle movement/completion;
- red signal waiting;
- capacity-induced queue;
- baseline flyover grade separation;
- active-flyover ramp routing, node separation, and ground-junction flow;
- active-flyover vehicle movement across the elevated crossing;
- capacity-comparison metrics;
- scenario catalog and deterministic execution;
- API execution for every catalog scenario;
- metrics creation and destination-road queue exclusion;
- fixed-seed repeatability;
- API tick clamp;
- invalid network, signal, malformed optional collections, demand, tick, and payload rejection.

A deterministic 80-tick baseline run still reports 83 generated, 76 completed, 7 active, 6.14 average travel ticks, 1.14 average waiting ticks, and a maximum queue of 4. These are a reproducibility smoke-check for the current engine version, not benchmark or validation figures.

The two added scenarios were also run for 80 ticks:

- **Active Flyover Crossing:** 113 generated, 103 completed, 10 active, 7.06 average travel ticks, 0.74 average waiting ticks, maximum queue 6. Both elevated-road segments and both ramps had non-zero utilisation.
- **Road Capacity Comparison:** 120 generated, 111 completed, 9 active, 6.23 average travel ticks, 1.23 average waiting ticks, maximum queue 3. The narrow road reached 84% utilisation versus 24% for the wide road; the narrow exit reached 96% versus 31% for the wide exit.

## Manual/browser verification status

The original Codex build session could not expose a browser surface or bind a local socket, so it recorded browser and wire-level checks as unverified. A later verification session on macOS started `python3 -m app.server` and used headless Chrome 156 through the Chrome DevTools Protocol. It verified:

- `GET /` and all static assets return 200 with correct content types; unknown paths return 404.
- `POST /api/run` returns 200 for valid payloads and 400 for malformed JSON or scenarios; tick values are clamped.
- The baseline network renders 5 roads, 7 nodes, 1 signal, and 1 dashed flyover.
- Changing seed/demand/ticks and running updates all metrics and the road table; both JSON exports download and parse.
- Reset clears results, disables results export, and restores the demo controls.
- The scenario selector lists all three scenarios. Selecting one updates the description, network, demand controls, seed, and ticks.
- **Active Flyover Crossing** renders 8 roads (4 at-grade, 2 elevated, 2 ramp), 1 elevated node, and 2 ramp nodes. `junction` and `fly_cross` share map coordinates `(330, 225)` but remain separate graph nodes. The 80-tick run displays 113 generated, 103 completed, 10 active, 7.06 travel, 0.74 waiting, maximum queue 6, and non-zero utilisation on both elevated segments and both ramps.
- **Road Capacity Comparison** renders 4 at-grade roads. The 80-tick run displays 120 generated, 111 completed, 9 active, 6.23 travel, 1.23 waiting, maximum queue 3, and clearly higher utilisation on the narrow corridor.
- Reset restores the selected scenario's defaults, clears results, and disables results export.
- Scenario and results JSON downloads parse for all three scenarios; results exports are paired with the scenario and metrics that produced them.
- The layout is single-column below 800px with no horizontal overflow at 360–1024px; a 1px table overflow was observed at 320px.
- No browser console errors were observed.

Screenshots were captured but not visually inspected because the verification model cannot read image input. This is a headless/DOM check, not a human visual review.

After the slider step was corrected from `.05` to `.01`, the default browser run reproduces the documented demo figures (83 generated, 76 completed, 7 active, 6.14 average travel, 1.14 average waiting, maximum queue 4), and Reset restores demand `0.62`/`0.42`.

To reproduce manually, start `python3 -m app.server`, open `http://127.0.0.1:8000`, choose each scenario, adjust its demand sliders and seed, run/reset, and use both export buttons.

## Hosted deployment verification

The live deployment is <https://roadflow-traffic-simulation.vercel.app>, built from the repository's Vercel configuration. Vercel's free Hobby plan runs `app/wsgi.py` as a Python WSGI function; no paid features are used. Render and Railway were not used because no Render credentials were available and the Railway token had expired.

Verified against the public URL:

- `GET /`, `/app.js`, `/style.css`, and `/status.css` returned 200 with the expected HTML/CSS/JavaScript content types.
- `GET /api/scenario` returned 200 with the built-in synthetic scenario.
- `POST /api/run` with `{"ticks":80}` returned 200 with 83 generated, 76 completed, 7 active, 6.14 average travel, 1.14 average waiting, and maximum queue 4.
- Malformed JSON returned 400, an unknown path returned 404, and an unsupported method returned 405.
- Headless Chrome 156 through the Chrome DevTools Protocol loaded the public page, found the initial `0.62`/`0.42` demand and 80 ticks, ran the simulation, displayed “Completed 80 ticks: 76 vehicles completed.” with all six metrics and five road rows, enabled results export, and restored the controls/cleared results on Reset.
- No browser console errors remained after adding an inline empty favicon to suppress the browser's automatic `/favicon.ico` request.
- Vercel runtime logs recorded the function invocations. Serverless cold starts can add latency; the verified run completed successfully.

## Model validation status

No real-world calibration or observational validation has been performed. The tests validate implementation rules, not predictive validity.
