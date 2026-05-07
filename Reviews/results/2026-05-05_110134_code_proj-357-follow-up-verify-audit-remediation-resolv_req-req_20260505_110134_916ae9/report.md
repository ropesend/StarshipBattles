# PROJ-357 Follow-up: Audit Remediation Verification

## Metadata
- **Date:** 2026-05-05
- **Type:** code (follow-up)
- **Review Mode:** normal
- **Request ID:** req_20260505_110134_916ae9
- **Parent:** req_20260505_055830_bbffca
- **Remediation SHA:** `00944437d`
- **Scope:**
  - `game/simulation/combat/fleet_aura_manager.py`
  - `tests/unit/simulation/combat/test_fleet_aura_provider_identity.py`
  - `Projects/active_projects/PROJ-357/decisions.md`
- **Limitations:** Follow-up scoped to CQ-001 verification + regression check only. MINOR/INFO findings from parent were explicitly deferred per remediation scope.
- **Reviewer:** OpenCode (ocode-review-request skill)
- **Test run:** 10/10 passed (1.19s)

## Executive Summary
- **Overall Assessment:** CQ-001 is **resolved**. The derelict ship filter is now consistently applied across all three paths (math, fingerprint, UI). No regressions.
- **Verification:** 1 finding verified (resolved), 5 deferred (not in scope).

---

## Verification Matrix

| Parent Finding | Severity | Status | Evidence |
|---|---|---|---|
| CQ-001 | MAJOR | **resolved** | `_recalculate()` (line 370), `initialize()` (line 120), and `register_ship()` (line 274) all now gate on `is_derelict`. `_get_provider_fingerprint()` (line 321) already included it. `get_active_bonuses()` (line 494) already had it. All five code paths agree. New tests pass. |
| CQ-002 | MINOR | **deferred** | `get_active_bonuses()` still reads snapshot `provider.value` (line 498). Not addressed by this commit — remediation scope was CQ-001 only. |
| CQ-003 | MINOR | **deferred** | `get_active_bonuses()` still does not check `component.is_operational` (lines 494-495). Not addressed. |
| CQ-004 | MINOR | **deferred** | New tests still call `_recalculate()` directly rather than exercising `update()` fingerprint path. Not addressed. |
| CQ-005 | INFO | **deferred** | No test for ability-instance identity loss. Not addressed. |
| AR-002 | MINOR | **deferred** | Default group-key comment at line 388 still not added. Not addressed. |

---

## CQ-001: Detailed Verification

### Remediation summary

Commit `00944437d` adds `is_derelict` filtering to three code paths that were missing it:

| Code path | Line | Change | Policy |
|---|---|---|---|
| `_recalculate()` | 370-372 | `if getattr(ship, 'is_derelict', False): continue` | Skip, don't drop — recovery restores contribution without re-scan |
| `initialize()` | 120-121 | `if getattr(ship, 'is_derelict', False): continue` | Don't register providers on already-derelict ships at battle start |
| `register_ship()` | 274 | Guard changed from `if ship.is_alive:` to `if ship.is_alive and not getattr(ship, 'is_derelict', False):` | Don't scan derelict ships added mid-battle |

The other two paths already handled derelict correctly (pre-existing):
- `_get_provider_fingerprint()` line 321: includes `s.is_derelict` in cache key
- `get_active_bonuses()` line 494: `if not provider.ship.is_alive or provider.ship.is_derelict: continue`

### Test coverage

Two new tests added:

1. **`test_derelict_provider_ship_does_not_contribute`** (line 236): Full lifecycle test.
   - Initializes manager with a live provider → contribution = 10.0 ✓
   - Toggles provider derelict → contribution = 0.0 ✓
   - Provider entry retained (skip-not-drop policy) ✓
   - UI (`get_active_bonuses`) agrees: derelict ship not in active bonuses ✓
   - Recovery (no longer derelict) → contribution restored to 10.0 ✓

2. **`test_initialize_skips_derelict_provider_ship`** (line 270): Registration scan test.
   - Ship starts derelict → `initialize()` does not register any providers ✓
   - Contribution = 0.0 ✓

### Regression check

- **Fingerprint consistency:** Already included `is_derelict` — math path now catches up. No behavioral change for the cache path.
- **Existing tests:** All 10 tests pass, including all 8 pre-existing characterization/identity tests.
- **Skip-not-drop policy:** Maintained. Derelict ships are skipped (not removed from `_providers`). Provider entries are retained so recovery on `is_derelict = False` restores contribution.
- **No other systems impacted:** The `is_derelict` guard uses `getattr(ship, 'is_derelict', False)` defensively — ships without the attribute are treated as not-derelict (no breakage for test mocks or ship types that don't implement derelict).
- **`decisions.md`** updated with audit remediation entry documenting the fix rationale and test results.

### Verdict: RESOLVED

All five code paths (scan, math, fingerprint, UI, mid-battle registration) now agree on derelict ship treatment. Tests are thorough: they cover the live-toggle-drop-recover cycle, initialize-time skip, and UI agreement. No regressions detected.

---

## Deferred Findings (not addressed by this remediation)

The commit message and `decisions.md` explicitly scope this remediation to CQ-001 only. Four MINOR and two INFO findings from the parent review remain deferred:

| ID | Title | Current state |
|---|---|---|
| CQ-002 | `get_active_bonuses` uses snapshot value | Still reads `provider.value` (line 498) not live `ability.value` |
| CQ-003 | `get_active_bonuses` skips `is_operational` | Still only checks `is_alive`/`is_derelict` (lines 494-495) |
| CQ-004 | No test for `update()` fingerprint path | New tests call `_recalculate()` directly |
| CQ-005 | No test for ability-instance identity loss | Not in scope |
| AR-002 | Default group-key comment missing | No comment at line 388 |
