# PROJ-432: TurnStateSnapshot rehydrate alignment

**Execution Protocol:** 03c-phase-aware-execution

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-432` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-432 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 0. Characterization — pin current restore() behavior with focused tests | Complete | [phase_0_checklist.md](phase_0_checklist.md) |
| 1. Mirror `SessionPersistenceAdapter.rehydrate_state()` wiring inside `TurnStateSnapshot.restore()` | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Docs + final verification | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |

## Current State
**Last Updated:** 2026-05-17
**Active Phase:** Phase 1 (ready)
**Last Action:** Phase 0 complete. Two new characterization tests added in `TestTurnStateSnapshotRestore` — `test_restore_wires_galaxy_back_refs` and `test_restore_rebuilds_pursuer_trackers`. Both observed failing against today's `restore()` (suite: 2 failed, 11 passed).
**Next Action:** Begin Phase 1 — add `empire.set_galaxy(...)` and pursuer-tracker rebuild wiring blocks inside `TurnStateSnapshot.restore()` to make the Phase 0 tests pass.
**Blockers:** None. Predecessor PROJ-423 is complete on `proj/PROJ-423/main`.

## Overview
There are two rehydrate paths inside the strategy layer that walk identical data structures but execute different wiring steps:

- `SessionPersistenceAdapter.rehydrate_state()` (`game/strategy/engine/session/persistence_adapter.py:171-198`) is the canonical save-load path. After deserializing the galaxy and empires, it (a) calls `empire.set_galaxy(galaxy)` on each empire (PROJ-219 back-references), (b) registers each fleet with the galaxy fleet registry, (c) resolves fleet-order marker dicts back to live object references, and (d) rebuilds each target fleet's `pursuer_tracker` from the resolved orders (PROJ-222).
- `TurnStateSnapshot.restore()` (`game/strategy/engine/turn_state_snapshot.py:84-99`) is the **turn-rollback** rehydrate path. After deserializing the same galaxy and empires, it registers fleets with the galaxy and resolves order references — but it does **not** call `empire.set_galaxy(...)` and does **not** rebuild pursuer trackers.

The asymmetry is a real bug: a turn that fails partway through and triggers a snapshot restore leaves empires without galaxy back-references and leaves pursuit relationships from `MOVE_TO_FLEET` / `JOIN_FLEET` orders silently broken. Existing snapshot tests at `tests/unit/strategy/turn_engine/test_turn_state_snapshot.py:89-141` cover only coarse restore behavior (empire name round-trip, galaxy system count, empire count) and miss this gap entirely.

This project aligns the two paths. The fix is small (two extra wiring blocks inside `restore()`), but it needs explicit characterization tests first (Phase 0) so the new behavior is locked in by an assertion, not by accident.

## Goals
- Align `TurnStateSnapshot.restore()` with `SessionPersistenceAdapter.rehydrate_state()`'s post-deserialize wiring.
- Eliminate the asymmetry between the two restore paths so a future change to one is caught by tests on the other.
- Pin pursuer-tracker rebuild and galaxy back-reference wiring with focused tests that mirror the existing PROJ-219 / PROJ-222 coverage on the save-load adapter.
- Do **not** regress any existing `TurnStateSnapshot` behavior (capture, crash-dump, isolation).

## Scope
**In:**
- Adding `empire.set_galaxy(galaxy)` wiring inside `TurnStateSnapshot.restore()`.
- Adding pursuer-tracker rebuild for `MOVE_TO_FLEET` / `JOIN_FLEET` orders inside `TurnStateSnapshot.restore()`.
- New focused tests covering both wiring additions; characterization tests for the current restore behavior in Phase 0.
- Docs update: `docs/systems/strategy_layer.md` (and any session-lifecycle doc that references snapshot/rollback) noting that snapshot restore now mirrors the save-load rehydrate.

**Out:**
- Refactoring `TurnStateSnapshot.restore()` to **call into** `SessionPersistenceAdapter.rehydrate_state()` directly. The two paths still differ on input shape (snapshot owns dicts; adapter owns the full save dict + ai_factory + providers) and a unification refactor is a separate, larger scope.
- Save-schema changes; snapshot capture format is unchanged.
- Touching `SessionPersistenceAdapter` itself.

## Dependencies
- **Predecessor:** PROJ-423 (GameSession lifecycle extraction). Complete on `proj/PROJ-423/main`. Hard predecessor only in the sense that this project's diagnosis references the post-PROJ-423 adapter; the code changes here are confined to `turn_state_snapshot.py` and its tests, so no merge conflict surface with other in-flight projects.
- No other hard predecessors. No phase-gate dependencies with peer projects.

## Key Files
| Component | File Path | Action |
|-----------|-----------|--------|
| Snapshot capture + restore (the asymmetric path) | [game/strategy/engine/turn_state_snapshot.py](../../../game/strategy/engine/turn_state_snapshot.py) | Edit (Phase 1: add the two missing wiring blocks inside `restore()`) |
| Canonical save-load rehydrate (the reference path) | [game/strategy/engine/session/persistence_adapter.py](../../../game/strategy/engine/session/persistence_adapter.py) | Read-only reference for wiring shape |
| Snapshot tests | [tests/unit/strategy/turn_engine/test_turn_state_snapshot.py](../../../tests/unit/strategy/turn_engine/test_turn_state_snapshot.py) | Edit (Phase 0: characterization tests; Phase 1: wiring-coverage tests) |
| Persistence-adapter tests (reference pattern) | [tests/unit/strategy/engine/session/test_persistence_adapter.py](../../../tests/unit/strategy/engine/session/test_persistence_adapter.py) | Read-only reference for the back-ref / pursuer-tracker assertion shape |
| Strategy-layer system doc (Phase 2 docs touch) | [docs/systems/strategy_layer.md](../../../docs/systems/strategy_layer.md) | Edit (Phase 2: note the alignment) |

Full enumeration in [manifest.md](manifest.md).

## Phases

### Phase 0: Characterization
Write focused tests that pin the **current** `TurnStateSnapshot.restore()` behavior beyond what `test_restore_resets_empires` / `test_restore_resets_galaxy` / `test_restore_preserves_empire_count` already cover. Include explicit assertions that today fail or pass-by-accident: e.g., `empire._galaxy is session.galaxy` post-restore (currently fails — Phase 1 makes it pass); pursuer-tracker membership for `MOVE_TO_FLEET` / `JOIN_FLEET` orders post-restore (currently fails — Phase 1 makes it pass). Mirror the assertion shape used by `test_rehydrate_wires_galaxy_back_refs` and `test_rehydrate_rebuilds_pursuer_trackers` in the persistence-adapter suite.

### Phase 1: Mirror the rehydrate wiring inside `restore()`
Add the two missing wiring blocks inside `TurnStateSnapshot.restore()`:

- After empire deserialization: `for empire in session.empires: empire.set_galaxy(session.galaxy)`.
- After fleet-order resolution: walk each fleet's orders for `OrderType.MOVE_TO_FLEET` / `OrderType.JOIN_FLEET` and, when `order.target` has a `pursuer_tracker`, register the source fleet via `order.target.pursuer_tracker.add_pursuer(fleet)`.

The Phase 0 tests written for the back-ref wiring and pursuer-tracker rebuild now pass.

### Phase 2: Docs + final verification
Add a paragraph to `docs/systems/strategy_layer.md` (and any session-lifecycle doc referencing rollback) noting that `TurnStateSnapshot.restore()` now mirrors `SessionPersistenceAdapter.rehydrate_state()` for post-deserialize wiring. Run the focused suites plus the sharded run.

## Related Documents
- Predecessor: [PROJ-423 plan](../PROJ-423/plan.md) — GameSession lifecycle extraction; the canonical rehydrate path lives there.
- Codex consult finding: see PROJ-423 [decisions.md](../PROJ-423/decisions.md) §"2026-05-17 — Phase 6 added from Codex consult" entry on TurnStateSnapshot rehydrate-path alignment as a separate project.
- [design.md](design.md) — distilled architecture analysis with the file:line evidence
- [decisions.md](decisions.md) — full decisions log
- [manifest.md](manifest.md) — enumerated file touch list

## Verification
- [ ] `TurnStateSnapshot.restore()` calls `empire.set_galaxy(session.galaxy)` for each restored empire.
- [ ] `TurnStateSnapshot.restore()` rebuilds the pursuer tracker for `MOVE_TO_FLEET` / `JOIN_FLEET` orders, mirroring `SessionPersistenceAdapter.rehydrate_state()`.
- [ ] Focused tests cover both wiring additions and assert post-restore state matches the persistence-adapter assertion shape.
- [ ] `pytest tests/unit/strategy/turn_engine/test_turn_state_snapshot.py` is green.
- [ ] `pytest tests/unit/strategy/engine/session/test_persistence_adapter.py` is green (no regression on the reference path).
- [ ] `python Tools/test_sharded/test_sharded.py` is green.
- [ ] Docs updated under `docs/systems/strategy_layer.md`.
- [ ] User verified.
