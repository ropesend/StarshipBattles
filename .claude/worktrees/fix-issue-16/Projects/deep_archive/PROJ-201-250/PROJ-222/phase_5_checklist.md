# PROJ-222 Phase 5: Serialization Rebuild

**Objective:** Rebuild pursuer tracker state from order targets after save/load.

## Task 5.1: Add Pursuer Rebuild in GameSession.from_dict() [Simple]
**File:** `game/strategy/engine/game_session.py`
**Tests:** `pytest tests/unit/strategy/fleet/test_fleet_pursuer_tracker.py`
- [ ] After line 351 (after `resolve_order_references` loop): add new loop to rebuild pursuers
- [ ] Implementation: iterate all empires → all fleets → all orders. For each order with type MOVE_TO_FLEET or JOIN_FLEET and target is a Fleet object (use `hasattr(order.target, 'pursuer_tracker')`), call `order.target.pursuer_tracker.add_pursuer(fleet)`
- [ ] Add comment: `# PROJ-222: Rebuild pursuer tracker from resolved order references`
- [ ] Add test: `test_pursuer_rebuild_after_load` — create fleets with join/intercept orders, serialize via `to_dict()`, deserialize via `from_dict()`, verify pursuer tracker state matches
- [ ] Run tests: `pytest tests/unit/strategy/fleet/test_fleet_pursuer_tracker.py`
**Notes:** This is straightforward because resolve_order_references() has already converted marker dicts to Fleet objects.

## Task 5.2: Run Full Test Suite [Simple]
**Tests:** `pytest tests/ -n 12`
- [ ] Run full test suite
- [ ] All tests must pass
**Notes:**

## Phase 5 Completion
- [ ] All Task 5.1-5.2 items checked
- [ ] `pytest tests/ -n 12` passes
