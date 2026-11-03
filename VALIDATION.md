# Validation record

## Automated checks

Run from the project directory:

```bash
python3 -m unittest discover -v
PYTHONPYCACHEPREFIX=/private/tmp/roadflow-pycache python3 -m compileall -q app tests
```

At the latest verification in this session, the unit suite passed **13/13** tests:

- connected and prohibited routing;
- vehicle movement/completion;
- red signal waiting;
- capacity-induced queue;
- flyover grade separation;
- metrics creation and destination-road queue exclusion;
- fixed-seed repeatability;
- API tick clamp;
- invalid network, signal, malformed optional collections, demand, tick, and payload rejection.

A deterministic 80-tick demo run was also executed in this session. With seed 42 and the built-in demand, it reported 83 generated, 76 completed, 7 active, 6.14 average travel ticks, 1.14 average waiting ticks, and a maximum queue of 4. These are a reproducibility smoke-check for the current engine version, not benchmark or validation figures.

## Manual/browser verification status

The HTML, CSS, and JavaScript were reviewed for the scenario controls, API path, rendering, reset, and download flows. This execution environment does not expose a browser surface and denies local socket binding, so an interactive browser run and wire-level HTTP test could not be performed here. They remain unverified in this session.

On a normal local machine, start `python3 -m app.server`, open `http://127.0.0.1:8000`, adjust both demand sliders and seed, run/reset, and use both export buttons. Confirm that results change with demand, reset restores demo controls, and downloaded JSON contains the selected inputs/results.

## Model validation status

No real-world calibration or observational validation has been performed. The tests validate implementation rules, not predictive validity.
