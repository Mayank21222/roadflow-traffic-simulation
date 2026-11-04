# OpenCode verification record

This is a human-readable record of the later OpenCode verification and fix session. It is not the raw session log. The original Codex build session log remains untouched at:

`/Users/mayankkashyap/.codex/sessions/2026/11/03/rollout-2026-11-03T09-40-03-01a19f99-911d-7c92-8709-2d7a7534f0b9.jsonl`

OpenCode's own session data remains under `/Users/mayankkashyap/.local/share/opencode/` (`opencode.db`, `log/opencode.log`); it was not edited.

## Scope

Read-only verification first, followed by two approved bug fixes, deployment support, documentation updates, and a final scenario enhancement. The simulation engine was not changed. The baseline scenario data and its 83/76 result were preserved; the new scenarios were added alongside it. No Git-history rewrite.

## Verified before changes

- `python3 -m unittest discover -v`: 14/14 passed.
- `python3 -m compileall -q app tests`: exit 0.
- Deterministic 80-tick demo: 83 generated, 76 completed, 7 active, 6.14 average travel, 1.14 average waiting, maximum queue 4.
- HTTP: static assets 200, `/api/scenario` 200, valid `/api/run` 200, malformed JSON/scenario 400, unknown path 404, tick clamping.
- Headless Chrome 156 through the Chrome DevTools Protocol: initial network (5 roads, 7 nodes, 1 signal, 1 flyover), run, reset, both exports, no console errors, no horizontal overflow at 360–1024px.
- Git bundle cloned; bundle HEAD matched active HEAD; working tree matched HEAD.

## Issues found and fixed

1. Demand sliders used `step=".05"`, so `0.62`/`0.42` were snapped to `0.6`/`0.4`. The default UI run therefore produced 82/75, not the documented 83/76, and Reset restored the wrong values. Fixed by using `step=".01"` in `web/index.html`.
2. Results export paired the current controls with the last run's results. Fixed by storing the scenario used in `run()` and exporting that with `lastResults` in `web/app.js`; Reset clears it.
3. Documentation updated: `README.md` records the deployment status and the flyover limitation; `VALIDATION.md` records the later browser and hosted-deployment checks and the corrected demo figures.
4. Deployment support added: `app/server.py` reads `HOST`/`PORT`, and `app/wsgi.py` plus `pyproject.toml`/`vercel.json` provide a Vercel WSGI entrypoint. The first Vercel build used the project's “Other” preset and served 404s; the explicit `vercel.json` build/routes fixed it. An automatic `/favicon.ico` request produced the only remaining console error, suppressed with an inline empty favicon.

## Verified after changes

- 14/14 tests and compilation pass.
- Fresh server/API smoke: 83 generated, 76 completed, 7 active, 6.14 travel, 1.14 waiting, maximum queue 4.
- Fresh headless Chrome: initial 0.62/0.42, default run 83/76, results export remains paired with the run scenario after controls change, Reset restores 0.62/0.42 and clears results, no console errors, no horizontal overflow at 390px.
- Public Vercel deployment verified at <https://roadflow-traffic-simulation.vercel.app>: static assets 200, `/api/scenario` 200, valid `/api/run` 200 with 83/76/7 and the documented metrics, malformed JSON 400, unknown path 404, unsupported method 405, and a full headless-Chrome run/reset with no console errors.
- The final bundle is regenerated after the commits, cloned successfully, and checked against the active HEAD and checksum file.

## Scenario enhancement

The final requested enhancement added a functional scenario selector and two new scenarios while retaining the baseline:

- **Synthetic Central Flyover** remains unchanged and still produces 83 generated / 76 completed at 80 ticks.
- **Active Flyover Crossing** adds connected entry/exit ramps, two elevated road segments, a separate `fly_cross` node at the same coordinates as the ground `junction`, and ground-level turning demand. The junction signal omits the direct north-to-south ground movement, so that demand routes over the flyover. There is no edge between `junction` and `fly_cross`.
- **Road Capacity Comparison** runs two parallel corridors under the same demand, with explicit narrow capacities 4/1 and wide capacities 12/6.

`GET /api/scenarios` was added for the catalog; `GET /api/scenario` remains for compatibility. The browser now builds demand sliders from the selected scenario, updates the network view, and distinguishes at-grade, elevated, and ramp roads. The engine, API payload contract, and local JSON export flow were retained.

Verified after the enhancement:

- `python3 -m unittest discover -v`: **21/21** passed; `compileall` passed.
- Baseline 80-tick result unchanged: 83 generated, 76 completed, 7 active, 6.14 travel, 1.14 waiting, maximum queue 4.
- Active Flyover Crossing: 113 generated, 103 completed, 10 active, 7.06 travel, 0.74 waiting, maximum queue 6; both elevated segments and both ramps had non-zero utilisation. Routing and separation tests pass.
- Road Capacity Comparison: 120 generated, 111 completed, 9 active, 6.23 travel, 1.23 waiting, maximum queue 3; narrow road 84% vs wide road 24%, narrow exit 96% vs wide exit 31%.
- Local and live headless Chrome runs: all three scenarios selected and ran; descriptions, networks, demand controls, seed, and ticks updated; Reset cleared results and restored scenario defaults; both JSON exports parsed; no console errors; no horizontal overflow at 390px.
- The existing Vercel project was redeployed and the public URL was verified: `/api/scenarios` returned 200, each scenario returned the expected 80-tick result, and the live browser workflow passed.

## Limitations

- Browser checks were headless/DOM checks; screenshots were captured but not visually inspected because the verification model cannot read image input.
- The live deployment is serverless on Vercel's free Hobby plan, not the preferred Render web service; no Render credentials were available and the Railway token had expired. Serverless cold starts may add latency.
- The original Codex JSONL was shared as an unlisted gist; it is not in this repository. The repository itself contains no credentials.
- No real-world calibration or validation was added.
