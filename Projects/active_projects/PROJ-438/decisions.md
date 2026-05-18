# PROJ-438: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-18 | Project initialized | Starting point for Strategy State Surface and Intent Lifecycle Consolidation |
| 2026-05-18 | **Assume PROJ-436 and PROJ-437 land as designed before implementation starts** | Explicit user instruction for this planning task. This project is chartered as **post-container** work and must not reopen storage or transfer-UI scope. |
| 2026-05-18 | **Leave original concern #2 (temporal scheduler / 100-tick model) out entirely** | Explicit user instruction. The temporal-model rethink remains a future project and does not belong in PROJ-438. |
| 2026-05-18 | **PROJ-438 is a combined residual-#1 + residual-#3 project, not two sibling projects** | After PROJ-423/424/425/429 and the assumed 436/437 outcomes, the remaining work is tightly coupled: persistence-shaped state surfaces and strategic intent lifecycle seams touch the same protocols, DTOs, façade surfaces, and tests. Splitting would create avoidable overlap. |
| 2026-05-18 | **Do not chase the 910-caller `ShipInstance` entry-point shim sweep here** | The retained thin shims were an intentional cost-control choice in PROJ-425. PROJ-438 may narrow `ShipInstance` further where it directly affects residual state surfaces, but it should not expand into a wholesale caller-sweep unless that falls out naturally from a narrower change. |
| 2026-05-18 | **Planet strategic intents are the primary residual #3 target** | The remaining order/intent fracture is no longer the command metadata stack. It is the stringly `IssuePlanetOrderCommand` path, the separate `PlanetActionEngine` lifecycle, and the planet-FMS/private-dispatch graft. That is the highest-value residual to clean up. |
| 2026-05-18 | **Verification gate decision is Phase 0 work** | Because `tests/unit/strategy/data/` may still be invisible to the canonical full suite, the project must explicitly decide whether to fix the collection gate or to budget direct-run verification commands. Do not assume the sharded runner alone protects this area. |
| 2026-05-18 | **No worktrees** | Standing user preference. Serial execution in the main checkout. |

## Deferred questions to resolve in Phase 0

### D1: Verification gate strategy

Problem:
- `pytest.ini` currently excludes any directory named `data`, which may hide high-signal ratchets under `tests/unit/strategy/data/`.

Options:
- **(a) Fix collection** so the canonical full suite includes those tests.
- **(b) Keep collection behavior and document an explicit supplemental verification matrix for PROJ-438.**

Default:
- **(a)**. Fix collection so the canonical suite actually sees the high-signal `tests/unit/strategy/data/` ratchets. Only fall back to a supplemental direct-run matrix if the collection fix proves materially riskier than expected.

### D2: `ShipInstance` persistence boundary target

Problem:
- After PROJ-436 lands, `ShipInstance` still likely embeds broad `design_data` plus serializer/bridge shims.

Options:
- **(a) Narrow the public/protocol/serializer surface but keep inline `design_data` as durable state for now.**
- **(b) Push further toward design lookup by id plus runtime delta state.**

Default:
- **(a)** for this project. It reduces surface area without forcing another huge caller and save-shape sweep.

### D3: `JOIN_FLEET` and mission decomposition

Problem:
- These may still be explicit lifecycle special cases after the higher-value planet-intent cleanup.

Options:
- **(a) Treat them as acceptable specialized behavior if contract boundaries are otherwise clean.**
- **(b) Pull them into deeper lifecycle convergence in Phase 7.**

Default:
- **(a)** unless the implementation audit shows they still leak across contracts in a way that blocks the main cleanup.

### Bounded scope reminder for Phase 4

Phase 4 is intentionally limited to:
- `Planet` save-schema breadth and directly-owned adjunct state,
- `Fleet` / `Empire` persistence-facing aggregate behavior,
- matching read-contract cleanup in `galaxy_protocols.py`.

If the Phase 0 audit shows no meaningful high-ROI extractions beyond that list, Phase 4 should shrink rather than expanding into a generic entity-polish pass.
