# PROJ-432 File Manifest

> Generated during project init from the Codex consult finding.
> Used by `/proj-parallel` for conflict detection.
> Update if implementation discovers additional files.

## Files

### Production — modified (Phase 1)

| File | Type | Notes |
|------|------|-------|
| `game/strategy/engine/turn_state_snapshot.py` | Production | Add the two missing wiring blocks inside `TurnStateSnapshot.restore()`: `empire.set_galaxy(session.galaxy)` (PROJ-219 back-reference) and pursuer-tracker rebuild for `MOVE_TO_FLEET` / `JOIN_FLEET` orders (PROJ-222 invariant). Mirrors `SessionPersistenceAdapter.rehydrate_state()` step ordering. |

### Production — read-only references

| File | Type | Notes |
|------|------|-------|
| `game/strategy/engine/session/persistence_adapter.py` | Production (read-only) | Canonical rehydrate path; lines 171-198 are the reference wiring sequence Phase 1 mirrors. Do not edit. |

### Tests — modified (Phase 0 + Phase 1)

| File | Type | Notes |
|------|------|-------|
| `tests/unit/strategy/turn_engine/test_turn_state_snapshot.py` | Test | Phase 0: add focused tests that assert today's missing invariants (`empire._galaxy is session.galaxy` post-restore; pursuer-tracker membership for `MOVE_TO_FLEET` / `JOIN_FLEET` orders post-restore). Mirror assertion shape from `test_rehydrate_wires_galaxy_back_refs` and `test_rehydrate_rebuilds_pursuer_trackers`. Phase 1: tests now pass. |

### Tests — read-only references

| File | Type | Notes |
|------|------|-------|
| `tests/unit/strategy/engine/session/test_persistence_adapter.py` | Test (read-only) | Reference for the assertion shape used by the new snapshot tests. Do not edit. |

### Docs — modified (Phase 2)

| File | Type | Notes |
|------|------|-------|
| `docs/systems/strategy_layer.md` | Doc | Add a short note that `TurnStateSnapshot.restore()` now mirrors `SessionPersistenceAdapter.rehydrate_state()` for the four post-deserialize wiring steps (galaxy back-references, fleet registration, order-reference resolution, pursuer-tracker rebuild). |
