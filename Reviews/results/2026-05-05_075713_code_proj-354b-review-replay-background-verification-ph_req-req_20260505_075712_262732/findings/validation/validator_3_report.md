# Validation Report: Validator 3

## Summary
- **Findings Reviewed:** 11
- **Confirmed:** 11 | **Downgraded:** 0 | **Rejected:** 0

## Verdicts

#### Finding: ERR-354B-007
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** Verified — the 8 broad `except Exception` clauses in the PROJ-354B replay scope (`replay_verification_coordinator.py:315`, `replay_store.py:86,267,275,339,346`, `replay_verification_sidecar.py:126,149`) all carry the required `# Intentional broad catch:` annotation with a rationale. Note: the count of 8 is correct for the new/changed files in the PROJ-354B review scope; other non-replay files in the codebase have unannotated broad excepts, but those are outside this review's scope.

#### Finding: ERR-354B-008
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** Verified — `save_json()` at `game/core/json_utils.py:184-189` writes serialized data to `<path>.tmp` via `json.dump()`, then calls `tmp_path.replace(file_path)`. `Path.replace()` is atomic on all supported platforms (Windows, Linux, macOS). If the original file doesn't exist, the temp file is atomically moved into place; if it does exist, the old file is atomically replaced. Serialization failures (TypeError, ValueError) are caught separately at lines 199-204 with temp-file cleanup.

#### Finding: ERR-354B-009
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** Verified — `shutdown_all_coordinators()` (`replay_verification_coordinator.py:76-92`) correctly mirrors `shutdown_all_calls()` (`game/services/llm/background.py:345-368`). Both: (1) snapshot the active set under lock, (2) return early if empty, (3) use `time.monotonic()` for a shared deadline, (4) iterate workers with `max(0.0, deadline - time.monotonic())` for per-worker remaining timeout, (5) log a warning if the worker doesn't finish in time. The coordinator variant delegates to `coord.shutdown(timeout=remaining)` which internally joins the thread; the LLM variant calls `worker.join(timeout=remaining)` directly. No deadlock risks — both use a lock-protected snapshot pattern with no nested lock acquisitions.

#### Finding: TC-C01
**Original Severity:** Critical
**Verdict:** CONFIRMED
**Reason:** Verified — `test_dict_key_mismatch_emits_diff` at `tests/unit/simulation/replay/test_replay_verifier.py:108-112` only asserts `total >= 1`. It does not verify the diff structure: the missing-key entry path `("b",)` with value `(2, None)`, nor the extra-key entry path `("c",)` with value `(None, 2)`. The production code at `replay_verifier.py:103-108` records these as distinct `_record()` calls with specific path/expected/actual triples, but the test never inspects them. Severity is appropriate — the semantic meaning of missing vs. extra keys is the most subtle part of the diff walker and could regress without detection.

#### Finding: TC-C02
**Original Severity:** Critical
**Verdict:** CONFIRMED
**Reason:** Verified — the `type(exp) is not type(act)` branch at `replay_verifier.py:126` has zero test coverage. All existing tests (`test_identical_dicts_yield_no_diff`, `test_single_leaf_mismatch`, `test_multi_leaf_mismatch`, `test_diff_capped_at_max`, `test_list_length_mismatch_emits_diff`, `test_dict_key_mismatch_emits_diff`) use dict-vs-dict and list-vs-list comparisons where types always match at the leaf level. No test passes, e.g., `{"x": 1}` vs `{"x": "1"}` or `{"x": [1]}` vs `{"x": {"a": 1}}` to exercise type mismatch. Severity is appropriate — type-mismatch detection is a fundamental correctness path.

#### Finding: TC-C03
**Original Severity:** Critical
**Verdict:** CONFIRMED
**Reason:** Verified — the `isinstance(exp, (list, tuple))` check at `replay_verifier.py:113` handles both lists and tuples, but all tests use only lists. `test_list_length_mismatch_emits_diff` and `test_single_leaf_mismatch` use dicts containing lists. No test passes a tuple as a value, e.g., `{"x": (1, 2)}` vs `{"x": (1, 3)}`. If the tuple-handling path in the walker regresses (e.g., a refactor drops `tuple` from the isinstance check), no test would catch it.

#### Finding: TC-M01
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified — `test_diff_capped_at_max` tests the overflow case (30 diffs, cap=25 → truncated=True, len(diffs)=25). No test covers the exact boundary: exactly 25 diffs with cap=25 should yield truncated=False, len(diffs)=25, total=25. The off-by-one condition at line 130 (`counter[0] > max_diffs`) is correct (25 > 25 is False), but a future refactor to `>=` would not be caught.

#### Finding: TC-M02
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified — `test_difference_dataclass_is_frozen` at line 185-188 tests immutability of the `Difference` dataclass only. `ReplayVerificationResult` is also `@dataclass(frozen=True)` (line 49-62) but has no immutability test. If `frozen=True` is accidentally removed from `ReplayVerificationResult`, no test would fail. The `test_round_trip_identity_passes` test instantiates a result but only inspects fields — it never attempts mutation.

#### Finding: TC-M03
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified — the `self._shutdown_event.is_set()` check at `replay_verification_coordinator.py:221-222` in `_on_record_persisted` has no test. While `shutdown()` removes the listener BEFORE setting the event (lines 190-197), the shutdown-event check serves as defense-in-depth against a race between another shutdown path signaling the event and a persist callback arriving concurrently. No test simulates this scenario (e.g., manually setting `_shutdown_event` without removing the listener, then persisting a record to confirm the callback returns early).

#### Finding: TC-M04
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified — the `_replay_dir()` re-check at `replay_verification_coordinator.py:276-283` in `_verify_one` guards against the save root being set to None mid-verification (which makes `_replay_dir()` return None per `replay_store.py:201-204`). No test covers this path. All coordinator tests use a fixed `tmp_path` with a valid `SaveRoot` that persists for the test duration. To test this, a test would need to set `store._save_root = None` after persisting a record but before the worker processes it.

#### Finding: TC-M05
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified — `test_fails_when_outcome_diverges` at `test_replay_verification_coordinator.py:131-153` only asserts `len(sidecar.diff) >= 1` (line 153). It does not verify the diff's structure: the `_divergent_replay_runner` mutates `duration_ticks` by +1 (line 86), so the diff should contain exactly one entry with path `("duration_ticks",)`, expected = `record.outcome.data["duration_ticks"]`, and actual = `expected + 1`. The test could trivially assert these specific values. The PASSED test at line 128 correctly asserts `sidecar.diff is None`, which is fine for a passing case.
