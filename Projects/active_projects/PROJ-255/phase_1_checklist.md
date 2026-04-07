# Phase 1: Split AIController.update Into Stages

**Objective:** Decompose `AIController.update()` into focused private methods, each handling one responsibility with typed inputs/outputs.

**Key Principle:** This is a pure extract-method refactor. No behavior change. No new classes. The `update()` method becomes a 4-5 line orchestrator.

---

## Background

`AIController.update()` (lines 278-361, CC ~18-22) mixes five responsibilities in one method:
1. Formation upkeep (throttle reset, master logic, integrity check)
2. Primary target acquisition
3. Secondary target acquisition
4. Retreat/behavior selection (HP-based threshold)
5. Behavior execution

Mixing these makes AI tuning risky — changing targeting logic could inadvertently break retreat logic, etc.

## Design

Extract into:
- `_update_formation() -> None` — throttle, master, integrity
- `_acquire_primary_target() -> Optional[Ship]` — target selection logic
- `_acquire_secondary_targets(primary) -> None` — secondary targeting
- `_select_behavior(target) -> Tuple[str, Optional[Behavior]]` — retreat threshold, behavior mapping
- `_execute_behavior(behavior, target, behavior_key) -> None` — instantiation and tick

`update()` becomes:
```python
def update(self) -> None:
    if not self.ship.is_alive():
        return
    self._update_formation()
    target = self._acquire_primary_target()
    self._acquire_secondary_targets(target)
    behavior_key, behavior = self._select_behavior(target)
    self._execute_behavior(behavior, target, behavior_key)
```

---

## Checklist

### Discovery
- [ ] Read `controller.py:278-361` fully — annotate each responsibility boundary
- [ ] Identify shared state between stages (target, behavior_key, behavior, etc.)
- [ ] Read existing tests for AIController.update — ensure coverage of all branches

### Tests First (TDD)
- [ ] Write test: `update()` on dead ship returns immediately (no further calls)
- [ ] Write test: `_update_formation()` called when ship is alive and in formation
- [ ] Write test: `_acquire_primary_target()` returns valid target when enemies exist
- [ ] Write test: `_acquire_primary_target()` returns None when no enemies
- [ ] Write test: `_select_behavior()` returns retreat behavior when HP below threshold
- [ ] Write test: `_select_behavior()` returns normal behavior when HP above threshold
- [ ] Write test: full `update()` cycle produces same AI state as before refactor (integration)
- [ ] Run tests — confirm existing tests pass (these are behavioral assertions, not implementation-dependent)

### Implementation
- [ ] Extract `_update_formation()` from lines ~280-293
- [ ] Extract `_acquire_primary_target()` from lines ~295-312 (plus ~320-332 no-target handling)
- [ ] Extract `_acquire_secondary_targets(target)` from lines ~314-318
- [ ] Extract `_select_behavior(target)` from lines ~334-345
- [ ] Extract `_execute_behavior(behavior, target, behavior_key)` from lines ~348-360
- [ ] Rewrite `update()` as orchestrator calling the 5 stages
- [ ] Verify CC of new `update()` is ~2-3 (just the alive check)
- [ ] Run tests — confirm they pass

### Verification
- [ ] Run full test suite (`python scripts/test_sharded.py`) — no regressions
- [ ] Run simulation tests (`python -m simulation_tests.run_tests`) — all pass
- [ ] Verify AI behavior is identical: run same battle seed before/after, compare outcomes
