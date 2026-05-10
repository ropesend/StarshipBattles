# Test Coverage Report — PROJ-354B Replay Verification System

**Date:** 2026-05-05
**Reviewer:** OpenCode (Test Coverage Analyst)
**Files analyzed:** 3 test files, 3 production source files

---

## Summary

| Category | Count |
|---|---|
| Files audited | 6 (3 test, 3 production) |
| Test functions reviewed | 30 |
| CRITICAL findings | 3 |
| MAJOR findings | 7 |
| MINOR findings | 6 |
| INFO findings | 3 |

**Overall assessment:** The test suites are well-structured with good fixture reusability and coverage of the happy paths and primary error modes. However, several distinct branches in `compute_outcome_diff` are untested, the coordinator's race-condition shutdown path has no coverage, and assertion depth in some coordinator tests is insufficient.

---

## Findings

#### CRITICAL: `compute_outcome_diff` missing-key / extra-key semantic is untested

**ID:** TC-C01

The `_walk` function at `game/simulation/replay/replay_verifier.py:105-108` emits `expected=<value>, actual=None` for keys present in expected but missing from actual, and `expected=None, actual=<value>` for keys present in actual but missing from expected. These are distinct diff shapes from scalar mismatches but no test verifies either path.

`test_dict_key_mismatch_emits_diff` only asserts `total >= 1` — it does not inspect the individual `Difference` objects to confirm the `expected`/`actual` values are correct for the missing-key case. There is zero coverage of the extra-key case (dict B has keys A doesn't).

**Production lines affected:** `replay_verifier.py:103-108`

**Fix:** Split `test_dict_key_mismatch_emits_diff` into two tests: (1) a key present in expected but missing in actual, asserting `diff[0].expected = <val>`, `diff[0].actual = None`; (2) a key present in actual but missing in expected, asserting `diff[0].expected = None`, `diff[0].actual = <val>`.

---

#### CRITICAL: `compute_outcome_diff` type-mismatch branch is untested

**ID:** TC-C02

The `_walk` function at line 126 checks `type(exp) is not type(act)` before scalar comparison. This catches diverging types at the same path (e.g., `exp=42, act="42"` or `exp=42, act=[42]`). No test exercises this branch.

**Production lines affected:** `replay_verifier.py:126`

**Fix:** Add a test case where expected and actual dicts share a key but the values have different types (e.g., `{"x": 1}` vs `{"x": [1]}`) and assert a diff is emitted.

---

#### CRITICAL: `compute_outcome_diff` tuple path is untested

**ID:** TC-C03

The isinstance check at line 113 handles both `list` and `tuple`. All existing tests use only `list` for sequence comparisons. `tuple` values (which can appear in `BattleOutcome` dicts, e.g., `participating_empires` or `sector_coords`) exercise a different path through the length-mismatch and index-walk branches but are never tested.

**Production lines affected:** `replay_verifier.py:113`

**Fix:** Add a test case with tuples in the dict values to verify the walker treats them identically to lists.

---

#### MAJOR: No test for exactly-at-cap diff count (25 diffs, `max_diffs=25`)

**ID:** TC-M01

`test_diff_capped_at_max` uses 30 diffs with cap=25 and asserts overflow. There is no test for the boundary case where total == max_diffs (25 diffs with cap=25). The truncation logic at `replay_verifier.py:130` returns `counter[0] > max_diffs`, which correctly yields `False` for 25 vs 25, but this boundary is unvalidated.

**Production lines affected:** `replay_verifier.py:130`

**Fix:** Add a test with exactly 25 diffs at cap=25, asserting `truncated is False` and `len(diff) == 25`.

---

#### MAJOR: `ReplayVerificationResult` frozen dataclass invariant untested

**ID:** TC-M02

`test_difference_dataclass_is_frozen` tests that `Difference` is frozen. `ReplayVerificationResult` is also `@dataclass(frozen=True)` but has no equivalent test.

**Fix:** Add a test that attempts to mutate a `ReplayVerificationResult` field and asserts `FrozenInstanceError` or `AttributeError`.

---

#### MAJOR: Race-condition shutdown path in `_on_record_persisted` untested

**ID:** TC-M03

The listener callback at `replay_verification_coordinator.py:221-222` checks `self._shutdown_event.is_set()` and silently returns if True. This handles the race where `shutdown_event` is set but the listener has not yet been removed from the store. `test_post_shutdown_persist_does_not_enqueue` only tests the *listener removal* case (after `shutdown()` fully completes). There is no test for the narrow window where the shutdown event is signaled but the listener is still registered.

**Production lines affected:** `replay_verification_coordinator.py:221-222`

**Fix:** Manually set `coord._shutdown_event.set()` without calling `shutdown()`, then persist a record, and assert no sidecar is written and no work is done.

---

#### MAJOR: R6 replay_dir-cleared-mid-verification path untested

**ID:** TC-M04

`_verify_one` at `replay_verification_coordinator.py:276-283` re-checks `self._store._replay_dir()` and drops the record silently if the save root was cleared mid-verification (R6 requirement per the docstring). No test covers this path.

**Production lines affected:** `replay_verification_coordinator.py:276-283`

**Fix:** Clear the store's save root while the worker is mid-verification (using a barrier or event) and assert no sidecar is written and no exception is raised.

---

#### MAJOR: Weak diff assertions in coordinator PASSED/FAILED tests

**ID:** TC-M05

`test_fails_when_outcome_diverges` checks only `len(sidecar.diff) >= 1` without verifying the individual diff structure (`path`, `expected`, `actual` values). `test_passes_when_outcome_matches` checks `sidecar.diff is None` but doesn't check `duration_ms > 0`. These assertions are too loose to catch subtle verification bugs where the diff is populated but with wrong path/value data.

**Fix:** In the FAILED test, assert `sidecar.diff[0]["path"]` equals the expected path tuple, and `sidecar.diff[0]["expected"]`/`sidecar.diff[0]["actual"]` match the mutated value. In the PASSED test, assert `sidecar.duration_ms > 0`.

---

#### MAJOR: `save_json` returning `False` (non-exception failure) in sidecar writer untested

**ID:** TC-M06

`write_verification_sidecar` at `replay_verification_sidecar.py:129-130` checks `if not ok: return None` when `save_json` returns `False` (e.g., `PermissionError` or `OSError`). The `test_atomic_write_leaves_no_temp_file` test passes because `save_json` succeeds. No test injects a failing `save_json` and asserts `None` is returned.

**Fix:** Monkeypatch `save_json` to return `False` and assert `write_verification_sidecar` returns `None`.

---

#### MAJOR: `duration_ms` may be `None` in `VerificationSidecar` — untested

**ID:** TC-M07

The `VerificationSidecar` dataclass declares `duration_ms: Optional[int]`. All tests use `_make_sidecar()` which always sets `duration_ms=42`. The coordinator writes `duration_ms=0` for `SKIPPED_DISABLED`/`SKIPPED_QUEUE_FULL` sidecars (via `_write_sidecar`), but no test directly asserts that `None` or `0` round-trips correctly through `from_dict`/`to_dict`.

**Fix:** Test `VerificationSidecar.from_dict` with `duration_ms: None` and `duration_ms: 0`.

---

#### MINOR: `start()` idempotence untested

**ID:** TC-m01

The docstring at `replay_verification_coordinator.py:167` says `start()` is idempotent. No test calls `start()` twice and asserts only one worker exists.

---

#### MINOR: `shutdown_all_coordinators` with multiple coordinators untested

**ID:** TC-m02

The module-level `shutdown_all_coordinators` function iterates a snapshot of active coordinators. The autouse fixture calls it for cleanup, but no test explicitly registers multiple coordinators and verifies both are joined. The timeout/warning path is also untested.

---

#### MINOR: `_unlink_sidecar` error path (OSError) untested

**ID:** TC-m03

`ReplayStore._unlink_sidecar` at `replay_store.py:406-418` catches `OSError` on `sidecar_path.unlink()`. No test forces this path (e.g., by making the sidecar path a directory or read-only).

---

#### MINOR: `remove_on_record_persisted_listener` for unregistered callable untested

**ID:** TC-m04

The method at `replay_store.py:193-199` is documented as "tolerant to unknown callables" — calling `remove` for a never-registered callback should be a silent no-op. No test verifies this.

---

#### MINOR: `VerificationSidecar.to_dict()` and `from_dict()` not directly tested

**ID:** TC-m05

These methods are only tested implicitly through the write/read round-trip. Direct unit tests would catch schema drift (e.g., a field added to the dataclass but forgotten in `to_dict`).

---

#### MINOR: `_iter_replay_files` sidecar exclusion has no direct unit test

**ID:** TC-m06

The filter at `replay_store.py:390-391` excludes `.verification.json` files from `glob("replay_*.json")`. This is tested implicitly through eviction tests, but no unit test specifically places a sidecar-only file in the directory and confirms `list()` returns empty or ignores it.

---

#### INFO: Deep mixed nesting not stress-tested in diff walker

**ID:** TC-i01

All diff walker tests use relatively shallow nesting (max 3-4 levels with 2-3 branches). A test with deeply nested mixed types (dict → list → dict → list → scalar) with divergences at multiple levels would increase confidence in the recursive correctness.

---

#### INFO: `_fallback_ship_builder` parameter of coordinator is never tested

**ID:** TC-i02

`ReplayVerificationCoordinator.__init__` accepts `fallback_ship_builder` which feeds into `ship_builder_factory`. All tests pass a `ship_builder_factory` that overrides the default; the fallback parameter is never exercised.

---

#### INFO: Save root set to `None` after persist — `_on_record_persisted` behavior

**ID:** TC-i03

When `_on_record_persisted` fires but `store.save_root` is `None` (e.g., `clear_save_root` called between persist and listener invocation), the coordinator's `_write_sidecar` calls `self._store._replay_dir()` which returns `None`, and the sidecar write is silently dropped. This edge case is not tested, though the code handles it gracefully.

---

## Top 5 Priority Issues

1. **TC-C01** — Missing-key/extra-key diff semantics untested. Two distinct branches with zero coverage.
2. **TC-C02** — Type-mismatch branch in `compute_outcome_diff` untested. Easy to trigger, hard to notice if broken.
3. **TC-C03** — Tuple path in diff walker untested. Production data uses tuples; untested sequence type.
4. **TC-M03** — Race-condition shutdown path untested. Listener-registered-but-shutdown-signaled window has no test.
5. **TC-M05** — Weak coordinator diff assertions. The FAILED test doesn't validate the diff structure, only length. A regression in `_difference_to_dict` would pass unnoticed.
