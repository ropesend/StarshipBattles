# Validation Report: Validator 4
## Summary
- **Findings Reviewed:** 11
- **Confirmed:** 10 | **Downgraded:** 1 | **Rejected:** 0

## Verdicts

### Finding: TC-M06
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified — `write_verification_sidecar` at `replay_verification_sidecar.py:129-130` checks `if not ok: return None` for a `save_json` that returns `False` on filesystem/serialization failures. `save_json` (in `json_utils.py:193-204`) catches `PermissionError`, `OSError`, `TypeError`, and `ValueError` internally and returns `False` — it never raises. The `except Exception` block above it is unreachable for `save_json` calls. No test in `test_replay_verification_sidecar.py` exercises this `False`-return path (e.g., via a read-only directory). The function has no injection point for `save_json`, making direct testing difficult, but the coverage gap is real.

### Finding: TC-M07
**Original Severity:** Major
**Verdict:** DOWNGRADED to Minor
**Reason:** Partially correct. The original claim states "all tests use `42`. No test for `None` or `0`." However, `duration_ms=0` IS implicitly tested via coordinator tests (`test_disabled_setting_writes_skipped_sidecar` and `test_queue_full_writes_skipped_queue_full_sidecar`), which pass `duration_ms=0` to `_write_sidecar` and then read back the sidecar asserting its presence. The `None` path is indeed untested — no test creates a `VerificationSidecar` with `duration_ms=None` and verifies round-trip behavior. The `from_dict` logic at `replay_verification_sidecar.py:100-101` handles `None` via `is not None` guard but this is never validated. Severity downgraded because (a) `0` is covered, (b) the `None` path only risks a serialization glitch in `to_dict()` which would produce `null` — unlikely to break anything.

### Finding: TC-m01
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified — `start()` at `replay_verification_coordinator.py:166-170` checks `if self._worker is not None: return` and is documented as "Idempotent." The test file has `test_shutdown_idempotent` (line 328) that verifies shutdown idempotence, but no test calls `coord.start()` twice and asserts (a) no crash, (b) the listener is only registered once, (c) only one worker thread exists. The idempotence guard is in a `with self._state_lock` block so it's thread-safe, but untested.

### Finding: TC-m02
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified — `shutdown_all_coordinators` at `replay_verification_coordinator.py:76-92` iterates `_active_coordinators` under lock and calls `coord.shutdown()` for each. The autouse fixture `_shutdown_all_coordinators_after_test` (line 93) calls it as cleanup but all tests create at most one coordinator. No test registers two coordinators simultaneously, adds both to `_active_coordinators`, calls `shutdown_all_coordinators()`, and asserts both worker threads are joined.

### Finding: TC-m03
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified — `_unlink_sidecar` at `replay_store.py:406-418` catches `OSError` from `sidecar_path.unlink()` and logs it. No test forces this error path (e.g., creating a sidecar file in a read-only directory, mocking `Path.unlink()` to raise `OSError`, or using a patched filesystem). The existing `test_delete_removes_sidecar` (line 192) only exercises the happy path; `test_evicts_sidecars_alongside_records` (line 239) also uses normal filesystem conditions.

### Finding: TC-m04
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified — `remove_on_record_persisted_listener` at `replay_store.py:193-199` checks `if callback in self._on_record_persisted_listeners` before removing, making it tolerant to unknown callables. The existing test `test_listener_unsubscribe` (line 327) subscribes then unsubscribes the same callable, but no test calls `remove_on_record_persisted_listener` with a callable that was never added and asserts it is a silent no-op (no exception, no state change).

### Finding: TC-m05
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified — `VerificationSidecar.to_dict()` (line 80) and `from_dict()` (line 92) are only exercised implicitly through the `write_verification_sidecar` → `read_verification_sidecar` round-trip in `test_round_trip_write_read` and similar tests. No test directly constructs a dict, calls `from_dict()`, and asserts each field individually; no test calls `to_dict()` and asserts the exact dict shape including `None` for optional fields. Isolation testing would catch field naming/typo bugs before integration tests need to run.

### Finding: TC-m06
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified — `_iter_replay_files` at `replay_store.py:389-392` filters out sidecar files (`if p.name.endswith(SIDECAR_FILE_SUFFIX): continue`). This is tested only implicitly: `test_evicts_sidecars_alongside_records` (line 239) relies on correct filtering for its count assertions, and `test_verification_does_not_create_new_replay_records` (line 366) manually re-implements the filter. No isolated unit test creates replay JSON files and sidecar JSON files in a temp directory, calls `_iter_replay_files()`, and asserts only replay files are yielded.

### Finding: TC-i01
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** Verified — The diff walker tests use shallow to moderately nested test data. The deepest test is `test_single_leaf_mismatch` with `{"teams": [{"ships": [{"current_hp": ...}]}]}` (5 levels: dict→list→dict→list→dict→key). Deep mixed-type nesting (e.g., alternating lists/dicts 10+ levels deep, lists containing heterogeneous types, dicts with both scalar and nested values at the same level) are not stress-tested. The walker uses recursive traversal so coverage from shallow tests is reasonable, but edge cases like deeply nested empty containers or mixed-type containers at extreme depth are unexplored.

### Finding: TC-i02
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** Verified — `_fallback_ship_builder` parameter at `replay_verification_coordinator.py:136-138` defaults to `None` and is forwarded to `self._ship_builder_factory(fallback_builder=self._fallback_ship_builder)` at line 287-290. All 11 test cases in `test_replay_verification_coordinator.py` pass `ship_builder_factory=lambda *a, **k: None`, which discards all keyword arguments including `fallback_builder`. The production path where `fallback_ship_builder` is non-None and used by `build_replay_ship_builder` is never tested in the coordinator tests. (The factory itself may be tested elsewhere, but the coordinator's wiring of this parameter is not.)

### Finding: TC-i03
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** Verified — When `_on_record_persisted` fires, it calls `_write_sidecar` which checks `rd = self._store._replay_dir()` and returns silently if `None` (line 339-341 and 276-283). The test `test_post_shutdown_persist_does_not_enqueue` (line 342) verifies the shutdown event blocks enqueue, and `test_persist_returns_none_when_no_save_root` (line 167 in integration tests) covers no save root at persist time, but no test simulates the mid-verification race where `save_root` is cleared between persist notification and sidecar write (`clear_save_root()` called while `_verify_one` is mid-flight). The silent drop is intentional and correct design (per the `R6` comment), but untested.
