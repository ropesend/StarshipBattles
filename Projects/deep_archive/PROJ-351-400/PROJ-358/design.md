# PROJ-358: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source Review
- **Review:** [2026-05-04_211026_tech-debt_realtime-combat-layer-maintainability-extensibilit](../../../Reviews/results/2026-05-04_211026_tech-debt_realtime-combat-layer-maintainability-extensibilit/)
- **Type:** Technical Debt Review
- **Date:** 2026-05-04
- **Report:** [View Full Report](../../../Reviews/results/2026-05-04_211026_tech-debt_realtime-combat-layer-maintainability-extensibilit/report.md)
- **Source finding:** #7 — "Battle runner silently accepts component drift" (P2, hidden failure mode)

## Initial Analysis

### Bug location
`game/simulation/battle_runner.py:580-619` — `_apply_spec_components_to_ship`. The docstring (lines 583-591) explicitly documents the silent-ignore: "Components in the spec that don't map to any Ship component are silently ignored (design drift)." Line 611-612 implements it: `if spec_entry is None: continue`.

This is the boundary where strategy data, designs, and realtime combat meet. A spec component that doesn't map indicates one of:
- Stale strategy spec referencing a component the design no longer has
- Design materialization bug (Ship constructor produced different component layout)
- Compiler emitting components for the wrong design id
- A real bug worth knowing about

Today all four cases are silent.

### Per-AGENTS.md
"Root Cause Fixes" rule: do not add compatibility shims, fallback systems, or duplicate logic. Old saves are disposable. The silent path is exactly this kind of shim and should be removed.

### Architecture
- Caller is `run_battle` / `start_engine_from_spec` (same file) which materializes ships from a `BattleSpec` then applies per-instance HP from `ShipSpec.components`.
- Spec compilers that emit `ShipSpec.components`:
  - `game/strategy/combat/spec_compiler.py` — strategy battle spec
  - `game/ui/screens/battle_setup/spec_compiler.py` — Battle Setup spec

If the validation surfaces a real production drift, the fix belongs in the compiler that emitted the bad entry.

## Key Patterns to Reuse
- **`ValidationException`** (`game/core/exceptions.py`) — already used by `BattleService` for spec/state errors. Extend, don't introduce a parallel exception type.
- **Spec validation timing** — fail before engine construction (consistent with how `BattleSpec.boundary` and other typed fields fail at materialization).

## Dependencies & Risks
1. **Existing tests may rely on the silent-ignore** — if so, those tests are encoding the bug. Surface to user; do not weaken the new validation to make them pass.
2. **Production drift may exist today** — running the validation against real specs may uncover a pre-existing compiler bug. That's the point; treat any first failure as a real signal and triage with the user before deciding to gate or fix forward.
3. **Test fixtures that fabricate `ShipSpec.components` ad hoc** may break — they should be updated to construct valid specs.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
