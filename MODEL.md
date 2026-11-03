# Simulation model

Roadflow is a deterministic, discrete-time, agent-based traffic prototype. It uses synthetic data only. It is not a calibrated transport model and must not be used to make real-world operational, safety, or policy decisions.

## Network and connectivity

A scenario contains directed roads and named nodes. A road connects only its explicit `from` and `to` nodes. Two lines crossing in the drawn map do not create an edge: the demo flyover is level 1 and has separate endpoints from the level-0 junction. A ramp/connector must be a road to make a grade-separated connection usable.

Routing is breadth-first by number of roads. At a signalised node, a movement must occur in at least one declared phase to be routable; this represents permanently prohibited turns. A non-signalised node permits each geometrically connected outgoing road.

## Vehicle agents and ticks

Each generated vehicle stores an ID, route, current route index, progress, entry tick, and accumulated waiting time. Each tick proceeds as follows:

1. Each demand entry performs one seeded Bernoulli draw; success attempts to create an agent.
2. An agent advances one unit of progress on its current road until it has consumed that road's travel time.
3. At a road exit, it transfers only if its signal movement is green and the downstream road has spare capacity. Otherwise it waits and adds one waiting tick.
4. An agent leaving its final road is recorded as completed.
5. Occupancy/utilisation and exit queues are sampled.

Processing order is ascending vehicle ID. This is a simplification: when multiple agents target the final downstream slot in one tick, the lower-ID agent receives it.

## Parameters and assumptions

| Property | Rule |
| --- | --- |
| Capacity | explicit `capacity`, otherwise `lanes × 6` agents |
| Travel time | `ceil(length / speed_limit)`, minimum one tick |
| Demand rate | probability from 0 to 1 for one arrival attempt per tick |
| Signal timing | each phase lasts `phase_ticks`; phases repeat in declared order |
| Road width | stored/displayed network metadata; it does not independently affect capacity |

Lengths, speed limits, capacities, map coordinates, and demand rates in the demo are synthetic relative values, not real-world units.

## Metrics

- **Generated:** agents admitted to their first road. Attempts rejected because that origin road is full are not generated.
- **Completed:** agents that exit the final road of their route.
- **Average travel time:** `(completion tick − entry tick)` averaged across completed agents.
- **Average waiting time:** ticks spent at a non-final road exit while blocked by a red signal or full downstream road, averaged across completed agents.
- **Maximum queue length:** largest sampled count of blocked, non-final-road agents at a single road exit.
- **Road utilisation:** mean of `occupancy / capacity`, sampled once per tick. It can be read as a fraction and is displayed as a percentage.

## Exclusions

There is no lane changing, acceleration, car following, merging, vehicle class, pedestrian phase, incident model, adaptive signal control, dynamic rerouting, parking, or calibration/validation against field measurements. A complete road movement is aggregate rather than physical vehicle geometry.
