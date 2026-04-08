# PROJ-222 Phase 4: Merge Redirect & Destruction Cancel

**Objective:** Implement the core redirect-on-merge and cancel-on-destruction behavior. This is the heart of the project.

## Task 4.1: Add Redirect Logic to Fleet.merge_with() [Medium]
**File:** `game/strategy/data/fleet.py`
**Tests:** `pytest tests/unit/strategy/fleet/test_fleet_pursuer_tracker.py`
- [ ] In `merge_with()`, BEFORE `self.clear_orders()` (before line 195): call `redirected = self._pursuer_tracker.redirect_pursuers(other_fleet)`
- [ ] After redirect: log FLEET_JOIN_REDIRECTED event for each redirected pursuer (use `log_event`)
- [ ] Import `log_event` from `game.core.event_logging` and event types from `game.strategy.events.event_types`
- [ ] Event details: `fleet_id=pursuer.id, old_target_id=self.id, new_target_id=other_fleet.id, location=[self.location.q, self.location.r]`
- [ ] Add test: `test_merge_with_redirects_pursuers` — Fleet A pursues B, B merges into C, verify A now pursues C
- [ ] Add test: `test_merge_with_logs_redirect_events` — verify log_event called with correct args (mock log_event)
- [ ] Add test: `test_merge_with_multihop_chain` — A pursues B, B pursues C. C merges into D. B redirected to D. Then B arrives and merges into D. A now pursues D.
- [ ] Add test: `test_merge_with_no_pursuers_does_nothing` — verify no errors when no pursuers exist
- [ ] Run tests: `pytest tests/unit/strategy/fleet/`
**Notes:** The `clear_orders()` call at line 195 will unregister self from any fleet self was pursuing. The `redirect_pursuers()` must happen BEFORE that.

## Task 4.2: Add Cancel Logic to Empire.remove_fleet() [Medium]
**File:** `game/strategy/data/empire.py`
**Tests:** `pytest tests/unit/strategy/data/test_empire_fleet_registration.py`
- [ ] In `remove_fleet()`, BEFORE removing from list (before line 80): call `cancelled = fleet.pursuer_tracker.notify_target_destroyed()`
- [ ] After cancel: log FLEET_JOIN_CANCELLED event for each cancelled pursuer
- [ ] Import `log_event` and event types
- [ ] Event details: `fleet_id=pursuer.id, target_fleet_id=fleet.id, location=[fleet.location.q, fleet.location.r] if hasattr(fleet.location, 'q') else None`
- [ ] Add test: `test_remove_fleet_cancels_pursuer_orders` — Fleet A pursues B, B removed, verify A's orders cleared
- [ ] Add test: `test_remove_fleet_logs_cancel_events` — verify events logged
- [ ] Add test: `test_remove_fleet_no_pursuers` — verify no errors when no pursuers
- [ ] Run tests: `pytest tests/unit/strategy/data/test_empire_fleet_registration.py`
**Notes:** On the merge path, `empire.remove_fleet(merged_fleet)` is called AFTER `merge_with()`. By then, pursuers have already been redirected, so `notify_target_destroyed()` finds an empty set — correct behavior.

## Task 4.3: Add FLEET_JOINED Event to process_join_fleet() [Simple]
**File:** `game/strategy/engine/fleet_order_processor.py`
**Tests:** `pytest tests/unit/strategy/test_fleet_order_processor.py`
- [ ] In `process_join_fleet()`, after successful merge (after line 112): log `FLEET_JOINED` event
- [ ] Event details: `fleet_id=fleet.id, target_fleet_id=target_fleet.id, ship_count=len(target_fleet.ships), location=[fleet.location.q, fleet.location.r]`
- [ ] In `_process_instant_joins()`, after successful merge (after line 671): log same event
- [ ] Add test: `test_process_join_fleet_logs_joined_event`
- [ ] Run tests: `pytest tests/unit/strategy/test_fleet_order_processor.py`
**Notes:**

## Task 4.4: Run Full Test Suite [Simple]
**Tests:** `pytest tests/ -n 12`
- [ ] Run full test suite
- [ ] All tests must pass (minus pre-existing failures)
**Notes:**

## Phase 4 Completion
- [ ] All Task 4.1-4.4 items checked
- [ ] `pytest tests/ -n 12` passes
