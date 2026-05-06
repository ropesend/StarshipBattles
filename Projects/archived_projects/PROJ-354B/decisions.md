# PROJ-354B: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-04 | Project initialized | Phase B of replay verification — coordinator + verifier + sidecar. Implements C4–C9 of consensus plan r003 from Claude+Codex inter-agent discussion. |
| 2026-05-04 | Verification triggers post-persist of LIVE battles, NOT user-clicks-Replay | Codex correction (r002). Matches user requirement: "background process that occurs when the simulator ends combat". The user-replay verification path is reserved as a future opt-in (sidecar `source: VISUAL_REPLAY` field reserved). |
| 2026-05-04 | Single FIFO worker, queue cap 16 | r003 §C6. Bounded mitigation against hostile/runaway mods. Single worker = deterministic + bounded CPU + no race-condition complexity. |
| 2026-05-04 | NO thread-level hard timeout in first pass | Codex pushback (r004). A thread cannot terminate CPU-burning code; only a process boundary can. Process-boundary worker is out of scope for first pass. Cap + drop-on-full + user-toggle-off provides bounded escape hatch. Deferred follow-up. |
| 2026-05-04 | Sidecar file `replay_<id>.verification.json` with separate `REPLAY_VERIFICATION_SCHEMA_VERSION` | r003 §C7. Sidecar avoids mutating immutable replay JSON (which would break atomic-write semantics). Separate version constant because verification schema lifecycle is independent of replay schema. |
| 2026-05-04 | Always write a sidecar for every captured replay (including SKIPPED_QUEUE_FULL, SKIPPED_DISABLED, PENDING) | r003 §C7. Replay Browser / event log can read one consistent source for status. No "missing sidecar" implies "?". |
| 2026-05-04 | List-based listener API on `ReplayStore` | Swarm finding: future-proofs for additional subscribers (telemetry, debug). Minimal API overhead vs. single-callback. Each listener exception caught individually so one bad subscriber doesn't break others. |
| 2026-05-04 | Verifier in `game/simulation/replay/`; coordinator in `game/strategy/services/` | r003 §C5. Verifier is layer-agnostic and depends only on simulation DTOs (works for Combat Lab too). Coordinator depends on Strategy + ApplicationContext-injected services. AST lint test (Phase 6 Task 6.2) prevents future imports from crossing the boundary. |
| 2026-05-04 | Strict dict-equality oracle (no tolerance) | r003 §C5. Existing test `tests/integration/replay/test_replay_playback.py:120-136` does strict `==` and passes — determinism holds. Ship strict; if flake appears, add comparator policy in a separate change. Don't pre-weaken. |
| 2026-05-04 | Diff capped at first 25 entries with truncation flag + total count | r003 open-question response. 100-ship battle could produce massive diff; cap keeps sidecar JSON manageable. Trunc flag + total_count preserve the "and N more" footer signal. |
| 2026-05-04 | Test boundary at `BattleController.start_from_spec`, NOT `BattleScreen` | Codex correction (r004). Both paths route through `start_engine_from_spec` → `run_battle`; equivalence at this boundary proves equivalence at every downstream point WITHOUT coupling tests to Pygame UI. |
| 2026-05-04 | Combat Lab uses EXPLICIT synthetic-builder fallback | r003 Combat Lab Position. Composition root passes `combat_lab.design_loader.load_combat_lab_design` as `fallback_builder=` argument to `build_replay_ship_builder`. NEVER silent fall-back to global registry lookup — silent fallback would hide configuration bugs. |
| 2026-05-04 | Coordinator uses DI for `ai_factory`, `registry_provider`, `replay_store`, `settings`, `fallback_ship_builder`, `clock`, `logger` | Pattern #1 ApplicationContext. No module-level globals. Construction is explicit at the composition root. |
| 2026-05-04 | Module-level `_active_coordinators` + `shutdown_all_coordinators(timeout)` mirror `_in_flight_calls` + `shutdown_all_calls` | Pattern #28. Allows shutdown sequence to drain background work without each consumer registering individually. Mirrors existing pattern at `game/services/llm/background.py:56-62, 345-368`. |
| 2026-05-04 | `run_replay_headless` is the verification engine entry point (NOT `BattleController.start_from_spec`) | r003 §C6. Headless run passes `capture_context=None`, which avoids the recursion path (`battle_runner.py:180` checks `if capture_context is not None`). Phase 4 Task 4.5 has explicit no-recursion regression test. |
| 2026-05-04 | Save deletion mid-verification: drop sidecar silently (logged at debug) | R6 mitigation. Coordinator checks `replay_store._replay_dir()` before writing sidecar; if save was deleted, `replay_dir` is None → drop. User has explicitly invalidated the data; no action needed. |
| 2026-05-04 | Listener fires AFTER successful write but BEFORE `_evict_excess` | Subscribers see the path before any eviction churn. Important for the coordinator: ensures the record is on disk when we enqueue it (so worker can re-read if needed). |
| 2026-05-04 | Phases 1-4 are independent of sink wiring; Phase 5 blocks on it | Allows substantial implementation progress + test coverage in isolation while user finalizes the prereq with codex. |

## Audit Remediation (OpenCode review 2026-05-05)

OpenCode swarm review of PROJ-354B (`Reviews/results/2026-05-05_075713_code_proj-354b-review-replay-background-verification-ph_req-req_20260505_075712_262732/`) flagged 5 CRITICAL and 13 MAJOR findings. All CRITs and MAJs fixed in a single remediation commit; MIN/INFO were skipped per scope. Per-finding verdicts:

### CRITICAL

| ID | Verdict | Rationale |
|----|---------|-----------|
| AR-001 | FIXED | `build_replay_ship_builder` extracted to new file `game/strategy/services/replay_ship_builder.py`; `game/simulation/replay/replay_player.py` no longer imports `ShipInstanceSerializer`. Coordinator imports the factory from its new home. Layer rule (Simulation must not depend on Strategy) restored. The closure still runs inside Simulation via DI from Strategy — that direction is allowed. |
| CJ-01 | FIXED | The diff walker's list/tuple branch is now explicitly documented as JSON-equivalent (CJ-01 design note in module docstring). The behavior is the same in practice — the JSON contract guarantees both sides arrive as lists at the verifier — but tests now lock the contract: `test_tuple_path_walks_like_list`, `test_tuple_index_diff`, `test_tuple_length_mismatch`. The user task brief asked for "normalize list/tuple"; what was already correct is now also explicit + tested. |
| TC-C01 | FIXED | Added `test_missing_key_emits_expected_value_actual_none` and `test_extra_key_emits_expected_none_actual_value` — both branches now lock concrete `expected`/`actual` values. |
| TC-C02 | FIXED | Added `test_type_mismatch_emits_diff` for the `{"x": 1}` vs `{"x": [1]}` case, plus `test_int_float_scalar_not_diffed` to lock int/float interchangeability (so `0` vs `0.0` doesn't diverge). |
| TC-C03 | FIXED | Tuple path covered by 3 new tests (above). Verified tuples and lists walk identically and produce identical diffs at every level. |

### MAJOR

| ID | Verdict | Rationale |
|----|---------|-----------|
| AR-002 | FIXED | Promoted `ReplayStore._replay_dir` to public `replay_dir` property; added `load_or_error(replay_id) -> tuple[record, reason]` for granular failure modes. `ReplayResolver` and `ReplayVerificationCoordinator` updated to use the public surface; the `_replay_dir`/`_safe_load` private accesses outside the class are gone. The `_replay_dir` private alias is kept inside `ReplayStore` itself to avoid a churning intra-class rename. |
| CJ-02 | FIXED | Float comparison now uses `math.isclose` with `rel_tol=1e-9`, `abs_tol=1e-9` (top-of-module constants `_FLOAT_REL_TOL` / `_FLOAT_ABS_TOL`). bools stay on the strict path (bool subclasses int and we must not silently equate `True` with `1.0`). Tests: `test_float_drift_within_tolerance_passes`, `test_float_drift_outside_tolerance_fails`. |
| CJ-03 | FIXED | List-length mismatch now emits a synthetic `{"__len__": N}` payload instead of the full lists. Cap-25 budget no longer consumed by tens of KB of low-signal data. Test: `test_length_mismatch_does_not_carry_full_lists`. |
| CJ-04 | FIXED | `_difference_to_dict` now passes every value through a new `_json_safe(value)` helper that recursively coerces Enum/tuple/unknown types so a leaked non-JSON value (`Vector2`, `Enum`, `datetime`) cannot silently fail at `save_json`. Unknown types fall back to `repr(value)` so the diff still records something visible. |
| ERR-354B-001 | FIXED | Worker loop body wrapped in outer `try/except Exception` (annotated broad-catch) with a `finally` that defensively resets `_busy` and sets `_idle_event`. A single bad replay can no longer kill the worker; even an unexpected raise leaves `wait_for_idle()` resolvable so callers don't deadlock. |
| ERR-354B-002 | FIXED | `ReplayStore` now owns `_listener_lock = threading.Lock()`. `add_on_record_persisted_listener`, `remove_on_record_persisted_listener`, and the `persist()` snapshot all run inside the lock. Check-then-mutate sequences are now atomic. |
| TC-M01 | FIXED | Added `test_exactly_at_cap_diff_count` — 25 diffs at cap=25, asserts `truncated is False` and `len(diff) == 25`. |
| TC-M02 | FIXED | Added `test_replay_verification_result_is_frozen`. |
| TC-M03 | FIXED | Added `test_shutdown_event_set_drops_listener_callback` — sets `_shutdown_event` directly without calling `shutdown`, persists a record, asserts no enqueue and no sidecar. |
| TC-M04 | FIXED | Added `test_replay_dir_cleared_mid_verification_drops_sidecar` — uses a gate to block the runner mid-verification, clears the save root, releases the gate, asserts no sidecar in the now-detached dir. |
| TC-M05 | FIXED | Added `test_failed_diff_carries_path_expected_actual` (locks `path == ["duration_ticks"]` plus concrete value mismatch) and `test_passed_sidecar_records_positive_duration` (asserts `duration_ms is not None and >= 0`). |
| TC-M06 | FIXED | Added `test_save_json_returning_false_yields_no_sidecar` — monkeypatches the sidecar module's `save_json` to return `False`, asserts no sidecar file is created and the worker stays alive (next persists still succeed). |
| TC-M07 | FIXED | Added `test_duration_ms_none_round_trip`, `test_duration_ms_zero_round_trip`, and `test_to_dict_from_dict_direct_round_trip` to lock the `Optional[int]` round trip. |

### Also fixed opportunistically (not in scope but trivial)

| ID | Verdict | Rationale |
|----|---------|-----------|
| AR-003 | FIXED | `start()` now registers the listener BEFORE spawning the worker. Race window where a record is persisted between worker-spawn and listener-register is closed. |
| AR-004 | FIXED | `shutdown()` docstring corrected to describe the actual drain-then-terminate semantics. Implementation already did this; the doc was wrong. |

### Skipped (out of scope)

All 14 MIN and 10 INFO findings (CJ-05 through CJ-10, ERR-354B-003 through ERR-354B-009, TC-i01-i03, TC-m01-m06, AR-005, AR-006). The MIN findings are real but lower priority; reopening the project for them now would inflate this remediation commit beyond its stated 5-CRIT-13-MAJ scope. They can be picked up in a follow-up if the project is reopened.
