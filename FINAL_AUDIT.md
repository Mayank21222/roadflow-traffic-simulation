# Final audit

**Status:** complete. No Critical code defects remain. One Critical process/provenance finding remains: the project's preferred single-session workflow was not followed throughout. It is disclosed here and in the verification records.

## Published state

- Audit implementation commit: `235d14e` (`Harden audit findings and record final verification`).
- Audit record commit at verification time: `784feff` (`Record final live audit verification`).
- Live application: <https://roadflow-traffic-simulation.vercel.app/>
- Automated tests: **24/24 passed**.
- Python compilation checks: passed.
- Last verified bundle before this documentation update: SHA-256 `2e97fce60f0b7a47fca730911a778fd2ddaefccde4e850b6f791bc448e745eed` for `784feff`. The bundle is regenerated after the final documentation commit; its current checksum is in the ignored `roadflow-history.bundle.sha256` file. The bundle is not tracked or uploaded.

## Results

- Deterministic 80-tick results were unchanged:
  - Baseline: 83 generated, 76 completed, 7 active, 6.14 travel, 1.14 waiting, maximum queue 4.
  - Active Flyover Crossing: 113 generated, 103 completed, 10 active, 7.06 travel, 0.74 waiting, maximum queue 6; 34 of 103 completions used elevated segments.
  - Road Capacity Comparison: 120 generated, 111 completed, 9 active, 6.23 travel, 1.23 waiting, maximum queue 3; narrow road 84% and exit 96%, wide road 24% and exit 31%.
- High demand produced 177 generated, 167 completed, 10 active, and maximum queue 5. Zero-demand and empty runs reconciled to zero; a stepped audit found no capacity overflow.
- Local HTTP, direct WSGI, and live API checks passed for all three scenarios. Malformed JSON/scenarios returned 400; unknown paths returned 404; WSGI unsupported methods returned 405; tick values were clamped to 1–5000.
- Browser checks passed for all three scenarios, exact metrics, network classes, export pairing, reset, and the stale-response race. Accessibility checks covered labels, `aria-live`, SVG role/label, headings, and viewport. No horizontal overflow was observed at 320–1440px and no console errors were observed.
- The final Git history bundle was regenerated and clone-verified: the clone's HEAD matched the published commit and the checksum verified.

## Fixed findings

- `seed: null` no longer produces nondeterministic output; it is rejected.
- Lane counts and explicit capacities must be integers. Numeric strings such as `"2"` are accepted and normalized; fractional values are rejected.
- `movements: null` is rejected as a scenario error instead of raising `TypeError`.
- A UI run token prevents a delayed `/api/run` response from overwriting newer scenario/control state.
- Results exports remain paired with the scenario and metrics that produced them; scenario exports remain paired with the current controls.
- Documentation/accessibility fixes: explicit SVG `role="img"`, "Synthetic simulation" badge, demand-rate wording, RNG/arrival-pairing note, dependency wording, transfer-tick assumption, and relative checksum command.

## Provenance

The project began in Codex; later verification and auditing used OpenCode. The preferred single-session workflow was not followed throughout, and this is not claimed.

- Original Codex session ID: `01a19f99-911d-7c92-8709-2d7a7534f0b9`
- Archived original Codex snapshot SHA-256: `2372fc7407dec75186ebb2ebc83ddf9116dcac9842ea351110b42bb775e62e26`
- Unlisted Codex snapshot: <https://gist.github.com/Mayank21222/f2b649a86d0dff0254900449223f1105>
- The local Codex runtime file was later appended by Codex and may differ; it is not the archived provenance artifact. This project did not edit it.
- OpenCode history is stored separately in its own local database/log format and is not published.
- Git author metadata was not rewritten. It reads `Codex <codex@local>` for all commits because of local Git configuration; commits after `e9982ef` are OpenCode work.

The archived original Codex snapshot and the unlisted Gist were not modified by this project, reconstructed, fabricated, or merged.

## Remaining limitations

- No real-world calibration or observational validation; outputs are synthetic.
- The local development server returns 404 for some unsupported methods while the WSGI entrypoint returns 405; WSGI `HEAD /` returns 405.
- Google Fonts are an external stylesheet dependency with local fallbacks.
- Capacity-comparison arrivals share an RNG stream but are not paired.
- Browser verification is headless/DOM-based, not a human visual review.
- Earlier commits still contain development-environment path references in documentation. The current tree removes them, and history was not rewritten per the preservation requirement.

## Detailed records

- [Validation](VALIDATION.md): automated, API, browser, responsive, and deployment evidence.
- [OpenCode record](OPENCODE_VERIFICATION.md): later verification/audit history and provenance.
- [Git history](GIT_HISTORY.md): optional bundle restoration and checksum workflow.
- [Model](MODEL.md): assumptions and metric definitions.
- [Decisions](DECISIONS.md): engineering choices and rejected scope.
