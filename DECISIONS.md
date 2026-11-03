# Engineering decisions

| Decision | Why | Trade-off |
| --- | --- | --- |
| Python standard library server | Works locally with no package installation; easy to inspect and test | No production web framework features |
| Vanilla HTML/CSS/JS UI | Keeps setup and export behaviour simple | Less component structure than a larger frontend framework |
| Engine separate from HTTP/UI | Makes routing and traffic rules directly testable and reusable | Requires explicit JSON adapters |
| Synthetic network/data | Meets demo needs without claiming data provenance or calibration | Results are illustrative only |
| Directed-road graph | Makes connectivity and flyover separation unambiguous | Bidirectional streets require two explicit roads |
| BFS by road count | Deterministic, explainable valid routing | Does not optimize travel time or adapt to congestion |
| Per-tick Bernoulli demand with fixed seed | Reproducible stochastic arrivals | Not a demand calibration model |
| Aggregate capacity `lanes × 6` | Visible, documented capacity difference with simple tuning | Not a physical storage/flow model |
| Structural signal movement validation | Prevents an impossible movement from being routed or silently simulated | Scenarios need to list permitted movements deliberately |
| Local JSON export | Lets users save scenario/results without persistence or external transfer | No import, scenario library, or durable storage |

## Rejected scope

Lane-level simulation, live map data, real-world calibration, multi-user persistence, cloud deployment, and adaptive control were intentionally omitted. They would increase apparent sophistication without being supportable by the synthetic, unvalidated model.
