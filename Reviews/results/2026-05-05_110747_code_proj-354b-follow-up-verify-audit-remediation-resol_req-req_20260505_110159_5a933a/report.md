# Review Report: PROJ-354B Follow-up — Audit Remediation Verification

## Metadata
- **Date:** 2026-05-05
- **Type:** code (follow-up, delegated by Claude Code)
- **Request ID:** req_20260505_110159_5a933a
- **Parent:** req_20260505_075712_262732
- **Parent Report:** Reviews/results/2026-05-05_075713_code_proj-354b-review-replay-background-verification-ph_req-req_20260505_075712_262732/report.md
- **Parent Findings:** 42 total (5 CRIT, 13 MAJ, 14 MIN, 10 INFO)
- **Remediation Commit:** `27e297815`
- **Scope:** game/simulation/replay/replay_verifier.py, game/strategy/services/replay_ship_builder.py, game/simulation/replay/replay_player.py, game/strategy/services/replay_store.py, game/strategy/services/replay_verification_coordinator.py, tests/unit/simulation/replay/test_replay_verifier.py, tests/unit/strategy/services/test_replay_*
- **Test Results:** 51/51 passed

## Executive Summary
- **Total Findings Verified:** 18 (5 CRIT + 13 MAJ)
- **Resolved:** 18 | **Partially-Resolved:** 0 | **Unresolved:** 0 | **Regressed:** 0
- **Overall Assessment:** All CRIT and MAJ findings resolved. No regressions detected.

---

## Verification Matrix

### Critical

| Parent Finding | Status | Evidence |
|---|---|---|
| AR-001 | RESOLVED | `build_replay_ship_builder` extracted to `game/strategy/services/replay_ship_builder.py` (new file). `replay_player.py` no longer imports `ShipInstanceSerializer` — imports are `BattleOutcome`, `BattleSpec`, `ReplayRecord` only. Grep confirms zero `from game.strategy` imports in `game/simulation/replay/`. Coordinator now imports from `game.strategy.services.replay_ship_builder`. |
| CJ-01 | RESOLVED | List/tuple equivalence documented in `replay_verifier.py:16-19` module docstring. Both `isinstance(exp, (list, tuple)) and isinstance(act, (list, tuple))` at line 137 walk sequences identically. Tests lock contract: `test_tuple_path_walks_like_list`, `test_tuple_index_diff`, `test_tuple_length_mismatch`. |
| TC-C01 | RESOLVED | `test_missing_key_emits_expected_value_actual_none` (line 116) asserts key "b" in expected→None in actual. `test_extra_key_emits_expected_none_actual_value` (line 127) asserts key "c" in actual→None in expected. Both verify concrete expected/actual values. |
| TC-C02 | RESOLVED | `test_type_mismatch_emits_diff` (line 138) tests `{"x": 1}` vs `{"x": [1]}`. `test_int_float_scalar_not_diffed` (line 148) tests `0` vs `0.0` as non-diff. Verifier at lines 162-166 has the int/float interchangeability gate. |
| TC-C03 | RESOLVED | Tuple path covered by 3 tests: `test_tuple_path_walks_like_list` (line 154), `test_tuple_index_diff` (line 161), `test_tuple_length_mismatch` (line 171). All pass and confirm tuple-vs-list structural equivalence at every level. |

### Major

| Parent Finding | Status | Evidence |
|---|---|---|
| AR-002 | RESOLVED | `replay_dir` promoted to public `@property` at `replay_store.py:209-221`. `load_or_error(replay_id)` added at lines 345-368 returning `tuple[record, reason]` for granular failure modes. Private alias `_replay_dir` kept for backward compat. `ReplayResolver` and `ReplayVerificationCoordinator` access `replay_dir` property. |
| CJ-02 | RESOLVED | Float comparison uses `math.isclose(rel_tol=1e-9, abs_tol=1e-9)` at lines 175-178. Constants `_FLOAT_REL_TOL`/`_FLOAT_ABS_TOL` defined at lines 54-55. Bools kept on strict `!=` path (lines 171-174). Tests: `test_float_drift_within_tolerance_passes` (1e-12 drift→pass), `test_float_drift_outside_tolerance_fails` (0.5 drift→fail). |
| CJ-03 | RESOLVED | List-length mismatch emits `{"__len__": N}` at lines 143-147. Full lists no longer materialized. `test_length_mismatch_does_not_carry_full_lists` (line 208) confirms synthetic payload with 1000-vs-500 lists — no 1000-element blobs in diff. |
| CJ-04 | RESOLVED | `_json_safe(value)` helper at lines 104-133 in coordinator: recursively walks dicts/lists/tuples, converts Enum→`.value`, falls back to `repr(value)`. `_difference_to_dict` applies it to all three fields (lines 136-141). |
| ERR-354B-001 | RESOLVED | Worker loop wrapped in outer `try/except Exception` at lines 296-317. `finally` block at lines 318-324 defensively resets `_busy=False` and sets `_idle_event`. A single bad replay cannot kill the worker or deadlock `wait_for_idle()`. |
| ERR-354B-002 | RESOLVED | `_listener_lock = threading.Lock()` at line 163. `add_on_record_persisted_listener` (line 196), `remove_on_record_persisted_listener` (line 205), and listener snapshot in `persist` (lines 298-299) all run inside the lock. Check-then-mutate is now atomic. |
| TC-M01 | RESOLVED | `test_exactly_at_cap_diff_count` (line 199): 25 diffs at cap=25 → `truncated=False`, `total=25`, `len(diff)=25`. |
| TC-M02 | RESOLVED | `test_replay_verification_result_is_frozen` (line 297): asserts `AttributeError` on mutation attempt. |
| TC-M03 | RESOLVED | `test_shutdown_event_set_drops_listener_callback` (line 407): manually sets `_shutdown_event`, persists record → no enqueue, no sidecar. |
| TC-M04 | RESOLVED | `test_replay_dir_cleared_mid_verification_drops_sidecar` (line 439): blocks worker mid-verification with gate, clears save root, releases gate → no sidecar in detached dir. |
| TC-M05 | RESOLVED | `test_failed_diff_carries_path_expected_actual` (line 483): asserts diff[0] has `path==["duration_ticks"]` and expected≠actual. `test_passed_sidecar_records_positive_duration` (line 516): asserts `duration_ms >= 0`. |
| TC-M06 | RESOLVED | `test_save_json_returning_false_yields_no_sidecar` (line 542): monkeypatches `save_json→False`, persists record → no sidecar file created, worker remains alive. |
| TC-M07 | RESOLVED | `test_duration_ms_none_round_trip` (line 142), `test_duration_ms_zero_round_trip` (line 159), `test_to_dict_from_dict_direct_round_trip` (line 176): all confirm `Optional[int]` propagates correctly through serialization. |

---

## Regression Check

| Area | Result |
|---|---|
| Layer isolation (no game.strategy imports in game/simulation/replay/) | PASS — grep confirms zero matches |
| Test suite (51 tests: verifier + coordinator + sidecar) | PASS — 51/51 |
| Decisions.md consistency | PASS — all verdicts match code |

No regressions detected. No new issues introduced.

---

## Findings by Severity

None — all 18 parent findings are resolved. No new issues found.

---

*Report generated: 2026-05-05*
