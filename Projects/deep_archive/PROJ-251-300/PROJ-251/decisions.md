# PROJ-251: Decisions Log

## Decision 1: Build on existing exception hierarchy
**Date:** 2026-04-06
**Decision:** Add `StrategyException` and `EnginePhaseError` to the existing `game/core/exceptions.py` hierarchy. Do not create a parallel exception system.
**Rationale:** The project already has `GameException` → `SimulationException`, `PersistenceException`, `ValidationException` with error codes, context dicts, and comprehensive docs. Creating a separate hierarchy would fragment error handling and confuse developers. `StrategyException` fills the gap for strategy-layer errors that don't fit under `SimulationException` (which is combat-specific).
**Alternatives Rejected:**
- Creating `EnginePhaseFailedError(SimulationException)` — wrong parent; turn processing is strategy, not simulation
- Creating exceptions in `game/strategy/exceptions.py` — fragments the hierarchy; core is the canonical location

## Decision 2: Snapshot via serialization, not deepcopy
**Date:** 2026-04-06
**Decision:** Use `to_dict()`/`from_dict()` round-trip for state snapshots, not `copy.deepcopy()`.
**Rationale:** The serialization infrastructure is mature (tested by 50+ round-trip tests). `deepcopy` on complex object graphs with pygame surfaces, registries, and circular references is fragile and slow. Serialization also stress-tests the save/load path every turn, catching serialization bugs early. Performance is acceptable at ~16ms for a typical game.
**Alternatives Rejected:**
- `copy.deepcopy()` — fragile with complex objects, doesn't exercise serialization
- Custom field-by-field copy — high maintenance cost, easy to miss new fields
- No snapshot (just halt, no rollback) — leaves game in inconsistent state

## Decision 3: Halt entire turn on any phase failure
**Date:** 2026-04-06
**Decision:** When any phase fails, stop the entire turn immediately and roll back. Do not continue processing remaining phases.
**Rationale:** The core bug is cascade corruption — Phase N+1 operating on state that Phase N failed to mutate. The only safe response is to halt and restore known-good state. A partially-processed turn is strictly worse than no turn (the player gets inconsistent state they can't reason about).
**Alternatives Rejected:**
- Continue-and-skip (current behavior) — this IS the bug we're fixing
- Per-phase rollback (undo just the failed phase) — requires per-phase snapshots (expensive) and phases are interdependent (Phase 3 depends on Phase 2's output)
- Retry failed phase — the phase will fail again for the same reason

## Decision 4: Strict deserialization for strategy data
**Date:** 2026-04-06
**Decision:** Remove `except Exception` from Fleet, Empire, and OrderSerializer `from_dict()` methods. Corrupt data fails the entire load with `PersistenceException`.
**Rationale:** Saves are disposable (pre-production). Silent data loss (missing ships, orders, fleets) is worse than a clear error message. The player would rather see "Save corrupted at Fleet 'Alpha', ship index 3" and start a new game than unknowingly play with a depleted fleet.
**Alternatives Rejected:**
- Keep silent skip for ships but not fleets — inconsistent; if one ship is corrupt, the fleet may be unplayable anyway
- Add a "strict mode" toggle — complexity for no benefit; saves are disposable
- Narrow the catch to specific types but still skip — half-measure; doesn't solve the root problem

## Decision 5: DesignLibrary gets result objects, not strict failure
**Date:** 2026-04-06
**Decision:** Replace `load_design_data() -> Optional[dict]` with `DesignLoadResult` that carries failure reason. Do NOT make it raise exceptions.
**Rationale:** Design files are user-created content on the filesystem. They can be corrupt for many reasons (manual editing, disk errors, version upgrades). The Ship Builder UI needs to handle these gracefully — show "Design corrupt" vs "Design not found" vs "Permission denied". Exceptions would force every caller to wrap in try/except, which is boilerplate for a non-critical path.
**Alternatives Rejected:**
- Raise exceptions and let callers catch — too heavy for a UI-facing utility
- Keep returning None — doesn't tell caller WHY the load failed
- Return (data, error) tuple — stringly-typed, no factory methods for consistent error construction

## Decision 6: Per-tick validation is precondition checks, not exhaustive audits
**Date:** 2026-04-06
**Decision:** Each engine validates specific preconditions (null references, wrong types, impossible values) at the start of its tick method. It does NOT validate all business rules or cross-engine consistency.
**Rationale:** Exhaustive validation would be expensive (14 engines × 100 ticks) and duplicative (business rules are already enforced by command handlers when orders are created). Precondition checks catch state corruption from earlier failed operations or serialization bugs — they're cheap guards against the most common failure modes.
**Alternatives Rejected:**
- Full state audit before each turn — too slow, O(n^2) for cross-references
- No per-tick validation (rely on error boundary alone) — error boundary catches the crash but the error message is "AttributeError: 'NoneType' has no attribute 'deposits'" instead of "Empire 1: colony 'Mars' has no planet reference"
- Validation only on first tick — state changes throughout the 100 ticks
