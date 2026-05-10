# PROJ-361 Follow-up: Audit Remediation Verification

**Request ID:** req_20260505_110136_70aa3a
**Parent:** req_20260505_055831_416bac
**Review Type:** code (follow-up, delegated by Claude Code)
**Review Mode:** normal
**Remediation SHA:** `09de39f3b`
**Completed:** 2026-05-05T11:15:00Z

---

## Executive Summary

**All 4 MAJOR findings from the parent review are RESOLVED. No regressions detected.**

The remediation centralizes the `registries=None` fallback into `_resolve_registries()` at the `resolve_battle` entry point, then tightens all downstream signatures to non-Optional `GameRegistries`. The regression test now captures and asserts registries threading through `_instances_to_ships`, and `_MockShipInstance.to_ship` matches the real signature. Two new tests cover the `shortcut_sole_survivor` branch under both injected and default registries.

---

## Verification Matrix

| Parent Finding | Status | Evidence |
|---|---|---|
| CQ-01 | **resolved** | `_resolve_registries()` at `simulation_adapter.py:39-52` centralizes fallback; `effective_registries` (line 146) is guaranteed non-None; `_instances_to_ships` signature tightened to `registries: 'GameRegistries'` (line 470); `shortcut_sole_survivor` branch uses `effective_registries` (line 170); post-battle call at line 297 passes non-None registries. Two new tests (`test_sole_survivor_shortcut_*`) at test lines 170-215 verify both injected and None cases. |
| CQ-02 | **resolved** | `_build_spec` signature at `simulation_adapter.py:343` is now `registries: 'GameRegistries'` (non-Optional); `_run_simulated_battle` signature at line 241 is `registries: 'GameRegistries'`; both match `build_strategy_battle_spec`'s required parameter. All callers pass `effective_registries` (guaranteed non-None). |
| TC-01 | **resolved** | `_MockShipInstance.last_registries` capture field added (test line 36); `to_ship` sets it (line 42). Existing test asserts `ship_instance.last_registries is fresh_registries` for both ships (lines 126-130). Fallback test asserts `last_registries is default_provider` (lines 164-168). Sole-survivor tests also verify registries threading (lines 195, 215). |
| TC-02 | **resolved** | `_MockShipInstance.to_ship` at test line 41: `def to_ship(self, pos, team_id=0, *, registries)` — keyword-only, no default. Matches real `ShipInstance.to_ship` signature. |

---

## Detailed Verification

### CQ-01: `_instances_to_ships` fallback centralized

**Before:** `_instances_to_ships` accepted `registries=None` and passed raw `None` to `ShipInstance.to_ship()` → crash in `ShipSerializer`. The `shortcut_sole_survivor` branch had the same defect.

**After:**
- `_resolve_registries(registries)` (`simulation_adapter.py:39-52`) resolves `None` to `get_default_registry_provider()` once at `resolve_battle` entry (line 146).
- `_instances_to_ships` signature: `registries: 'GameRegistries'` (line 470) — no Optional, no default.
- `shortcut_sole_survivor` branch (lines 169-174): passes `effective_registries`, not raw `registries`.
- Post-battle `_instances_to_ships` call (line 297): receives guaranteed non-None `registries` from `_run_simulated_battle`.
- Test `test_sole_survivor_shortcut_threads_registries_to_instances` (lines 170-195): verifies injected registries reach `to_ship`.
- Test `test_sole_survivor_shortcut_uses_default_when_registries_none` (lines 197-215): verifies fallback works on `None` input without crashing.

**Verdict: RESOLVED.** No remaining `None` paths to `ShipInstance.to_ship`.

### CQ-02: Signatures tightened to non-Optional

**Before:** `_build_spec` declared `registries: Optional['GameRegistries']` and forwarded to `build_strategy_battle_spec` (requires non-Optional). Type mismatch.

**After:**
- `_build_spec` (`simulation_adapter.py:343`): `registries: 'GameRegistries'` — non-Optional.
- `_run_simulated_battle` (`simulation_adapter.py:241`): `registries: 'GameRegistries'` — non-Optional.
- All callers (`resolve_battle` lines 213, 230) pass `effective_registries` (guaranteed non-None).

**Verdict: RESOLVED.** Types are consistent end-to-end.

### TC-01: Test captures registries through `_instances_to_ships`

**Before:** Regression test only asserted `run_battle.registry_provider` identity; `_instances_to_ships` registries threading was unchecked.

**After:**
- `_MockShipInstance.last_registries` (test line 36): captures the registries argument.
- `_MockShipInstance.to_ship` (line 42): writes `self.last_registries = registries`.
- `test_resolve_battle_threads_injected_registries` (lines 126-130): asserts `last_registries is fresh_registries` for both ships.
- `test_resolve_battle_falls_back_to_default_when_no_registries` (lines 164-168): asserts `last_registries is default_provider`.
- Sole-survivor tests also verify (lines 195, 215).

**Verdict: RESOLVED.** All 4 test paths assert registries threading through `_instances_to_ships`.

### TC-02: Mock signature matches real signature

**Before:** `to_ship(self, pos, team_id=0, registries=None)` — optional with `None` default, masking `None`-passing bugs.

**After:** `to_ship(self, pos, team_id=0, *, registries)` (test line 41) — keyword-only, no default. Matches `ShipInstance.to_ship` at `game/strategy/data/ship_instance.py:684`.

**Verdict: RESOLVED.** Mock accurately reflects the real contract.

---

## Regression Audit

No regressions found. Each change is narrowly scoped to the 4 findings:

| Area | Risk | Assessment |
|---|---|---|
| `resolve_battle` entry | Centralizing fallback changes control flow | No change to logic — `_resolve_registries` replaces inline `registries if registries is not None else get_default_registry_provider()` pattern that was already correct for the `run_battle` path. |
| `_instances_to_ships` signature | Tightening from Optional to required | All 3 call sites pass `effective_registries` (guaranteed non-None). No call site was relying on `None` behavior. |
| `_build_spec` signature | Tightening from Optional to required | All 3 call sites pass `effective_registries`. `build_strategy_battle_spec` already required non-None. |
| `_build_capture_context` | Still `Optional['GameRegistries']` (line 371) | Not a regression — caller always passes non-None now but Optional is defensive within the helper. Handles `None` gracefully via `"sha256:unknown"` fallback (lines 419-422). |

**Additional observations:**
- The `_build_capture_context` signature (`registries: Optional['GameRegistries']`, line 371) could be tightened to `'GameRegistries'` since the sole caller now passes a guaranteed non-None value. This is cosmetic — the function correctly handles both cases — and is not a regression from the remediation.
- MINOR/INFO findings from the parent (CQ-03, CQ-04, AR-01, CQ-05, AR-02) were intentionally deferred per `decisions.md:62-63` and remain unchanged.

---

## Test Verification

```bash
pytest tests/unit/strategy/adapters/ -v
```
Parent validation reported 20 passed. The remediation adds 2 new tests (sole-survivor shortcut coverage) and expands 2 existing tests (TC-01/TC-02 assertions), for a total of 4 tests exercising the registry threading paths.
