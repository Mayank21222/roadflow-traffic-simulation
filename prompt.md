Project 2: Traffic Simulation — Coding-Agent Prompt

1. ROLE
You are my full-stack engineering agent for this project. Take responsibility for turning the requirements into a working, maintainable application. Make practical engineering decisions, explain important trade-offs briefly, and verify your work instead of assuming generated code is correct. Be honest about what works, what is approximate, and what remains unfinished.
2. TASK
Build an end-to-end web application for an agent-based traffic simulation on a road network. A user should be able to create or choose a scenario, configure traffic conditions, run the simulation, and inspect the results.

The simulation must represent:
- A road network with connected roads that can have different widths, lane counts, directions, speed limits, and capacities.
- Junctions, including a signal-controlled intersection.
- Flyovers or other grade-separated crossings. Roads that simply cross at different levels must not connect unless a ramp or connector is explicitly defined.
- Individual vehicle agents that travel from origins to destinations using valid routes and respond to road capacity, traffic signals, congestion, and queues.
The application should include a clear road-network view, scenario controls, simulation controls, useful charts or metrics, and a way to save or export scenarios and results. Keep the simulation engine separate from the UI so it can be tested independently.

First inspect the repository, installed tools, and existing project structure. Reuse what is sensible; do not replace working code or choose a new stack without a reason. Then state a short implementation plan and start building. Prioritise a complete basic workflow over optional features.

Use synthetic data for the demo unless suitable real road/traffic data is readily available and its source and usage rights can be established. Label synthetic inputs and simulated outputs clearly. Describe the model as a prototype unless it has genuinely been calibrated and validated against appropriate real-world observations.

Include tests for connectivity and routing, vehicle movement, signals, road capacity and queues, flyover separation, metric calculations, and repeatability with a fixed random seed. Provide a demo scenario and instructions to run the application locally. Deploy it only if this can be done reliably within the time limit; report the actual deployment status.
3. CONSTRAINTS
Follow these application rules exactly:
- Complete all development in one single Claude Code or Codex session. Choose one agent and remain in that same session. Do not use another coding agent, another session, or work created outside the session.
- Finish within 72 hours of this first prompt, including the final Git commit. Track the start time and deadline.
- This application line must be the literal first line of the first prompt. Before sending this prompt, replace [your name] and [date] with my real name and the actual date. Do not put any text, heading, or code fence before that line.
- Run development commands, tests, and Git operations from inside this same session. Make the commits here so the Git history aligns with the session log.
- Commit in small, meaningful steps. Inspect the diff and repository status before committing. Preserve existing user work; do not overwrite unrelated files, rewrite history, or fake commit timestamps.
- Preserve the raw session log exactly as generated. Do not edit, summarise, or reconstruct it. At the end, identify its location so it can be submitted unedited.
- Do not fabricate data, results, benchmark figures, validation, citations, or deployment success. Do not expose secrets. Keep the implementation and dependencies as simple as the requirements allow.
4. OUTPUT FORMAT
Work in the following order and keep progress updates concise:
1. Inspect: report the repository structure, available runtime/tooling, and any existing code worth keeping.
2. Plan: describe the proposed architecture, simulation approach, key assumptions, and implementation steps. Then proceed unless a decision genuinely requires my input.
3. Build: implement the simulation engine, application/API, scenario workflow, visualisations, and save/export capability. Keep core logic modular and testable.
4. Verify: run automated tests and the demo scenario; check edge cases, inspect the UI, review errors, and fix issues found. State exactly which checks were run and their outcomes.
5. Finish: update the README and make the final Git commit from this session before the 72-hour deadline.
The repository should contain, at minimum:
- The working application and simulation engine.
- A demo network and scenario that can be run without external data.
- Scenario configuration and controls to start/reset a simulation.
- Result displays for useful measures such as vehicles generated/completed, average travel and waiting time, queue lengths, and road utilisation. Define each metric and how it is calculated.
- Tests for the key behaviours listed above.
- A README covering setup, local execution, architecture, model assumptions, demo use, data provenance or synthetic-data status, and known limitations.
- Scenario/result export, plus deployment instructions and actual deployment status if deployment is achieved.
For progress updates, use this compact format: Completed | Current decision | Checks run and result | Next step. In your final response, summarise what works, how to run it, tests and results, known limitations, deployment status, final commit, Git status, and the raw session-log location. Do not claim an item is complete unless you have verified it.
5. ZERO-SHOT / FEW-SHOT EXAMPLES
Use the following examples as behavioural requirements. Implement automated tests where practical, and document any manual checks. Exact numerical outputs may differ; do not invent target benchmark values.

Example 1 — Ordinary junction
Two roads meet at a normal junction. A vehicle with a valid route can move from one road to the connected road. It cannot turn onto a road that is not connected or where that movement is prohibited.

Example 2 — Signalised junction
Vehicles arrive at a signal-controlled intersection. Vehicles facing red wait; vehicles with a permitted green movement proceed. If arrivals exceed the junction's ability to serve them, queues form and are reflected in the results.

Example 3 — Flyover crossing
Two roads cross on the map, but one passes over the other on a flyover. Vehicles continue on their own road; the crossing does not create an at-grade junction or allow turns between roads. Connectivity exists only where an explicit ramp or connector is provided.

Example 4 — Different road capacities
Run comparable traffic demand on a narrow road and a wider or multi-lane road. Given sensible, documented capacity assumptions, the higher-capacity road should generally accommodate more flow before queues build. Keep other scenario conditions the same and use a fixed random seed for a fair comparison.

For all examples, check that the outcome follows from the model's rules. If the simulation uses simplifications—for example, discrete time steps, simplified car-following, or no lane-changing—state them clearly in the README and in the application where appropriate.
6. LAST FALLBACK
If the complete scope cannot be delivered reliably within 72 hours, reduce the scope immediately and finish a working local MVP. The fallback must still include a small road network, valid routing, moving vehicle agents, one signalised junction, a flyover with correct grade separation, basic congestion/queue behaviour, a few clearly defined metrics, and a simple interface to run and view a scenario.

Drop advanced features before compromising correctness. Use a built-in synthetic demo if data or external services become a blocker. Make the app runnable, add the essential tests and README, document what is missing, and make the final commit before the deadline. Do not switch sessions or agents, do not build anything outside this session, and do not alter the raw session log. A small, tested, transparent application is the priority; never make an unfinished or unverified feature appear complete.