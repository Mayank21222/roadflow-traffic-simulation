# Validation record

## Automated checks

Run from the project directory:

```bash
python3 -m unittest discover -v
PYTHONPYCACHEPREFIX="$(mktemp -d)" python3 -m compileall -q app tests
```

At the latest verification, the unit suite passed **24/24** tests:

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
- integer lane/capacity handling, including numeric strings and rejection of fractional values;
- null seed and null signal-movement rejection;
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
- The layout is single-column below 800px. The final audit observed no horizontal overflow at 320, 360, 390, 768, 1024, or 1440px; the earlier 1px table overflow at 320px was not reproduced.
- No browser console errors were observed. The final audit also added an explicit `role="img"` to the network SVG and verified the accessible label.

Screenshots were captured but not visually inspected because the verification model cannot read image input. This is a headless/DOM check, not a human visual review.

After the slider step was corrected from `.05` to `.01`, the default browser run reproduces the documented demo figures (83 generated, 76 completed, 7 active, 6.14 average travel, 1.14 average waiting, maximum queue 4), and Reset restores demand `0.62`/`0.42`.

To reproduce manually, start `python3 -m app.server`, open `http://127.0.0.1:8000`, choose each scenario, adjust its demand sliders and seed, run/reset, and use both export buttons.

## Hosted deployment verification

The live deployment is <https://roadflow-traffic-simulation.vercel.app>, built from the repository's Vercel configuration. Vercel's free Hobby plan runs `app/wsgi.py` as a Python WSGI function; no paid features are used. Render and Railway were not used because no Render credentials were available and the Railway token had expired.

The final audit build (commit `235d14e`) was redeployed to the same production alias and re-verified against the public URL:

- `GET /`, `/app.js`, `/style.css`, and `/status.css` returned 200 with the expected HTML/CSS/JavaScript content types.
- `GET /api/scenario` returned 200 with the baseline synthetic scenario.
- `GET /api/scenarios` returned 200 with all three catalog scenarios.
- `POST /api/run` with `{"ticks":80}` returned 200 with the baseline result: 83 generated, 76 completed, 7 active, 6.14 average travel, 1.14 average waiting, and maximum queue 4.
- `POST /api/run` returned the expected 80-tick results for the added scenarios: Active Flyover Crossing 113/103/10 with 7.06 travel, 0.74 waiting, and maximum queue 6; Road Capacity Comparison 120/111/9 with 6.23 travel, 1.23 waiting, and maximum queue 3.
- Malformed JSON returned 400, an unknown path returned 404, and an unsupported method returned 405.
- Headless Chrome 156 through the Chrome DevTools Protocol loaded the public page, found all three scenarios, and ran each one. The baseline displayed 83/76/7; Active Flyover Crossing displayed 113/103/10 with non-zero utilisation on both elevated segments and both ramps; Road Capacity Comparison displayed 120/111/9 with higher utilisation on the narrow corridor. Reset and both JSON exports worked, and there were no console errors or horizontal overflow at 390px.
- No browser console errors remained after adding an inline empty favicon to suppress the browser's automatic `/favicon.ico` request.
- The final build returned 400 for `seed: null`, fractional lanes/capacities, and null signal movements; accepted numeric-string lanes; and returned 405 for `GET /api/run`. A path-traversal probe returned 400 (no file disclosure), while local/WSGI returned 404.
- Vercel runtime logs recorded the function invocations. Serverless cold starts can add latency; the verified runs completed successfully.

## Final independent audit (2026-11-04)

A final audit inspected the engine, scenarios, API, UI, tests, documentation, deployment configuration, Git history, and session records. It added validation guards and a UI stale-run guard without changing baseline simulation results. A concise public summary is in [FINAL_AUDIT.md](FINAL_AUDIT.md).

- `python3 -m unittest discover -v`: **24/24** passed; `compileall` passed.
- Deterministic 80-tick results were unchanged: baseline 83/76/7, 6.14 travel, 1.14 waiting, maximum queue 4; Active Flyover Crossing 113/103/10, 7.06 travel, 0.74 waiting, maximum queue 6; Road Capacity Comparison 120/111/9, 6.23 travel, 1.23 waiting, maximum queue 3.
- High demand produced 177 generated, 167 completed, 10 active, and maximum queue 5. Zero-demand and empty runs reconciled to zero; a stepped audit found no capacity overflow.
- Local HTTP and direct WSGI checks returned 200 for the page, assets, scenario catalog, and all three scenario runs; malformed JSON/scenarios returned 400, unknown paths and path traversal returned 404, WSGI unsupported methods returned 405, and tick values were clamped to 1–5000.
- Headless Chrome loaded all three scenarios, verified the exact metrics and network classes, checked that results exports remain paired after controls change, delayed a run and changed scenario mid-flight to confirm the stale response is discarded, and exercised reset. Accessibility checks covered labels, `aria-live`, SVG role/label, headings, and viewport. No horizontal overflow was observed at 320–1440px and no console errors were observed.
- Provenance: the archived original Codex snapshot (503 lines) remains unchanged. Its session ID is `01a19f99-911d-7c92-8709-2d7a7534f0b9`; its SHA-256 is `2372fc7407dec75186ebb2ebc83ddf9116dcac9842ea351110b42bb775e62e26`; it matches the unlisted Gist at <https://gist.github.com/Mayank21222/f2b649a86d0dff0254900449223f1105>. The local Codex runtime file was later appended by Codex and is not the archived artifact. Later work used OpenCode; OpenCode history is stored separately in its own local database/log format and is not published. Commit author metadata reads `Codex <codex@local>` for all commits because of local Git configuration; the later commits are OpenCode work. The tracked `prompt.md` asks for a single Codex/Claude session, so using OpenCode later is a Critical process/provenance finding that cannot be corrected without falsifying history; it is disclosed instead.
- Remaining limitations: no real-world calibration; the local development server returns 404 for some unsupported methods while the WSGI entrypoint returns 405; WSGI `HEAD /` returns 405; Google Fonts are an external stylesheet dependency with local fallbacks; capacity-comparison arrivals share an RNG stream but are not paired; browser checks are headless/DOM checks, not human visual review.

## Model validation status

No real-world calibration or observational validation has been performed. The tests validate implementation rules, not predictive validity.
