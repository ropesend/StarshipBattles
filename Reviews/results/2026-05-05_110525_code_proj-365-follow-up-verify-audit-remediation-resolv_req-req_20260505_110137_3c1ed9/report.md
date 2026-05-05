# Follow-Up Review: PROJ-365 Audit Remediation Verification

**Request ID:** req_20260505_110137_3c1ed9
**Parent:** req_20260505_055831_a52654
**Review type:** code (follow-up)
**Review mode:** normal (full-depth, inline analysis)
**Scope:** 3 files (turn_engine.py, test_turn_engine_phase_timing.py, decisions.md)
**Checkout SHA:** N/A (working tree review)
**Remediation commit:** `4e25c7d83`

---

## Verification Matrix

| Parent Finding | Status | Evidence |
|---|---|---|
| MAJ-001 (`planet_modifier_effects` missing from TURN PERF log) | **RESOLVED** | `turn_engine.py:653` — format string now includes `planet_modifier_effects=%.3fs`. `turn_engine.py:662` — positional arg `self._phase_times['planet_modifier_effects']` provided. |
| MAJ-002 (5 end-of-turn engines missing from TURN PERF log) | **RESOLVED** | `turn_engine.py:653-654` — format string now includes `organics_consumption`, `happiness`, `quality_improvement`, `atmosphere`, `water_modification` tokens. `turn_engine.py:665-667` — all five positional args provided. |
| Regression-guard test robustness | **ADEQUATE+** | Test introspects `process_turn` source, enumerates all `_phase_times` keys, and asserts each has a labeled token. See analysis below. |

---

## Per-Finding Verification

### MAJ-001: `planet_modifier_effects` — RESOLVED

**Context:** PROJ-365 routed `planet_modifier_effects` through `_time_phase` uniformly. The timing accumulated in `_phase_times` but was omitted from the TURN PERF format string.

**Verification:**

| Check | File:Line | Result |
|---|---|---|
| Key in `_phase_times` dict | `turn_engine.py:253` | `'planet_modifier_effects': 0.0` — present since original PROJ-365 commit |
| Format token in TURN PERF | `turn_engine.py:653` | `planet_modifier_effects=%.3fs` — added between `activation_timers` and `move_calc` |
| Positional arg supplied | `turn_engine.py:662` | `self._phase_times['planet_modifier_effects'],` — present, correct dict key |
| Phase routed through `_time_phase` | `turn_engine.py:752` | Dispatch loop calls `self._time_phase(bucket, target, ...)` for all phases including this one — unchanged from PROJ-365 initial commit |

**Verdict:** The format string token and positional argument are both present and correct. The existing timing infrastructure (dict key, `_time_phase` routing) was already in place pre-remediation. The remediation completes the observability picture. **RESOLVED.**

---

### MAJ-002: 5 end-of-turn engines — RESOLVED

**Context:** PROJ-343 T1.2-engines routes end-of-turn engines through `_time_phase` for rollback safety. Their timings accumulated but were never logged.

**Verification:**

| Engine (`_time_phase` key) | Format token | Token position | Arg position |
|---|---|---|---|
| `organics_consumption` | `organics_consumption=%.3fs` | `turn_engine.py:653` | `turn_engine.py:665` |
| `happiness` | `happiness=%.3fs` | `turn_engine.py:653` | `turn_engine.py:665` |
| `quality_improvement` | `quality_improvement=%.3fs` | `turn_engine.py:653` | `turn_engine.py:666` |
| `atmosphere` | `atmosphere=%.3fs` | `turn_engine.py:654` | `turn_engine.py:666` |
| `water_modification` | `water_modification=%.3fs` | `turn_engine.py:654` | `turn_engine.py:667` |

All five tokens are present in the format string in logical order (after `combat`, before `population=`). All five positional arguments reference the correct `_phase_times` keys.

The sixth end-of-turn key (`population_growth`) was already logged pre-remediation under the legacy alias `population=%.3fs` (`turn_engine.py:654`, arg at `turn_engine.py:668`). This alias is preserved for log-grep compatibility.

**Verdict:** **RESOLVED.**

---

### Regression-Guard Test Robustness

**Test:** `test_turn_perf_log_format_string_includes_all_phase_keys` (`test_turn_engine_phase_timing.py:130-173`)

**Mechanism:**
1. Uses `inspect.getsource(TurnEngine.process_turn)` to read the method source.
2. Instantiates `TurnEngine(registries=fresh_registries)` to get the live `_phase_times` dict.
3. Iterates all keys, applying `legacy_label_aliases` for known label mismatches (`population_growth→population`, `movement_calc→move_calc`, `movement_apply→move_apply`).
4. Asserts `{label}=%.3fs` appears in the source for every key.

**Strengths:**
- **Exhaustive:** Enumerates ALL keys from a live engine instance — no hardcoded expectation list. Future additions to `_phase_times` will fail this test automatically.
- **Precise token format:** `{label}=%.3fs` is the exact token that appears in the format string. No false-positive risk from substring matches (the source is scoped to `process_turn` only).
- **Legacy alias awareness:** The alias map correctly accounts for all three known label divergences. Adding a new alias without updating the map would trigger a test failure (fail-safe behavior).

**Limitations (acknowledged, not blocking):**
- **No positional-arg ordering verification.** The test checks the token exists in the source, not that the corresponding `%` format specifier receives the correct `_phase_times[key]` value. A bug where someone swaps two positionals or uses the wrong dict key for a format specifier would not be caught. However, this failure mode requires the programmer to actively edit the arg list (not just forget to add one), and the `_reset_phase_times` characterization test (`test_reset_phase_times_returns_dict_with_canonical_keys`) independently pins the dict shape.
- **Inspect dependency.** If `process_turn` were moved to a C extension or obfuscated, `inspect.getsource` would fail. Unlikely in this codebase.
- **Alias map maintenance.** A new legacy alias would need manual addition. The test's failure message explicitly guides the maintainer: `"TURN PERF format string missing '{label}=%.3fs'"`.

**Verdict:** The test is **adequate for its intended purpose** (preventing recurrence of MAJ-001/MAJ-002). It will catch any future addition to `_phase_times` that lacks a corresponding log label. The positional-ordering gap is a reasonable tradeoff against test complexity and is mitigated by the existing `_reset_phase_times` characterization test. **No MIN/CRIT issues with the guard.**

---

## Regression Check

The remediation changed only the TURN PERF format string and its positional arguments in `turn_engine.py:647-669`. No changes were made to:
- `_process_tick` dispatch loop
- `DEFAULT_TICK_PHASE_LIST` / `turn_phase_registry.py`
- Any engine properties, methods, or initialization logic
- Any phase-ordering or cross-phase state (PROJ-320 `moved_fleet_ids`, `TickContext`)
- Any production-side logic beyond the log line

**No regressions detected.** The existing `test_reset_phase_times_returns_dict_with_canonical_keys` test was updated to expect 21 keys (from the original 14) — this is a correct synchronization, not a regression.

---

## Findings Summary

| Severity | Count |
|---|---|
| CRITICAL | 0 |
| MAJOR | 0 |
| MINOR | 0 |
| INFO | 0 |

**Both MAJ findings from the parent review are verified RESOLVED. No regressions detected. The regression-guard test is robust for its intended purpose.**
