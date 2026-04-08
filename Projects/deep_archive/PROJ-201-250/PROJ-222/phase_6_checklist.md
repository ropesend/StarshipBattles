# PROJ-222 Phase 6: Integration Tests & Final Validation

**Objective:** End-to-end integration tests covering multi-hop chains, concurrent merges, and the full order lifecycle.

## Task 6.1: Integration Test — Full Join-Redirect Flow [Medium]
**File:** `tests/integration/strategy/test_fleet_join_redirect.py` (NEW)
**Tests:** `pytest tests/integration/strategy/test_fleet_join_redirect.py`
- [ ] Create integration test file
- [ ] Test: `test_join_redirect_on_merge` — Fleet A joins B, B joins C (B arrives first). A's orders redirect to C. A arrives and merges into C.
- [ ] Test: `test_join_cancel_on_destruction` — Fleet A joins B, B is destroyed via `empire.remove_fleet()`. A's orders cancelled, event logged.
- [ ] Test: `test_intercept_redirect_on_merge` — Fleet A intercepts B, B joins C. A's MOVE_TO_FLEET redirected to C.
- [ ] Test: `test_multihop_chain_three_levels` — A→B→C→D. D merges into E. Verify A, B, C all redirect correctly.
- [ ] Test: `test_multiple_pursuers_all_redirected` — A, B, C all pursue D. D merges into E. All three redirect.
- [ ] Test: `test_save_load_preserves_pursuit` — create pursuit scenario, serialize, deserialize, verify pursuer state intact
- [ ] Run tests: `pytest tests/integration/strategy/test_fleet_join_redirect.py`
**Notes:**

## Task 6.2: Integration Test — Edge Cases [Medium]
**File:** `tests/integration/strategy/test_fleet_join_redirect.py`
**Tests:** `pytest tests/integration/strategy/test_fleet_join_redirect.py`
- [ ] Test: `test_clear_orders_during_pursuit_unregisters` — Fleet A pursues B, user clears A's orders. A removed from B's pursuers.
- [ ] Test: `test_delete_order_during_pursuit_unregisters` — Fleet A has [MOVE, MOVE_TO_FLEET→B, JOIN_FLEET→B]. Delete the MOVE_TO_FLEET order. Verify pursuer count adjusts correctly.
- [ ] Test: `test_self_join_rejected` — Verify validation prevents fleet from joining itself
- [ ] Test: `test_cross_empire_join_rejected` — Verify validation prevents cross-empire join
- [ ] Run tests: `pytest tests/integration/strategy/test_fleet_join_redirect.py`
**Notes:**

## Task 6.3: Run Full Test Suite — Final Verification [Simple]
**Tests:** `pytest tests/ -n 12`
- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] Verify 13358+ tests pass (accounting for new tests added)
- [ ] No new failures introduced
**Notes:**

## Phase 6 Completion
- [ ] All Task 6.1-6.3 items checked
- [ ] `pytest tests/ -n 12` passes
- [ ] All verification checklist items in plan.md checked
