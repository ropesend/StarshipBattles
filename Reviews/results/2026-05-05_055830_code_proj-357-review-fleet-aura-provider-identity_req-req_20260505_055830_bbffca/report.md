# PROJ-357 Review: Fleet Aura Provider Identity

## Metadata
- **Date:** 2026-05-05
- **Type:** code
- **Review Mode:** normal
- **Request ID:** req_20260505_055830_bbffca
- **Scope:**
  - `game/simulation/combat/fleet_aura_manager.py` (full file)
  - `tests/unit/simulation/combat/test_fleet_aura_provider_identity.py` (new)
  - `Projects/active_projects/PROJ-357/decisions.md`
- **Parent:** None
- **Checkout SHA:** N/A (daemon-managed)
- **Limitations:** Manual single-reviewer analysis (3 files, ~770 lines). No sub-agents launched.
- **Reviewer:** OpenCode (ocode-review-request skill)

## Executive Summary
- **Total Findings:** 7
- **Critical:** 0 | **Major:** 1 | **Minor:** 4 | **Info:** 2
- **Overall Assessment:** The PROJ-357 fix is correct and self-contained. The provider identity now correctly binds to `(ship, component, ability_instance)`, the skip-non-operational/drop-on-real-loss policy is sound with no registration leak, stacking semantics match `calculate_ability_totals()`, and no other systems were found with the same `(ship, ability_class_name)` identity bug. Five actionable items remain, all Minor or lower, focused on UI consistency and test gap fill.

## Verification of Requested Items

### Provider Identity (end-to-end)
**Status: CORRECT.** The `AuraProvider` dataclass holds `ship`, `component`, `ability` references (line 44-51). `_scan_ship()` registers one provider per `(component, ability)` pair (line 232-252). `_recalculate()` at line 347-351 verifies the specific `ability` instance is still in `component.ability_instances` — if not, the provider is dropped (identity loss). This is the correct pattern.

### Stacking Semantics
**Status: CORRECT, bit-identical.** The two-phase aggregation via `_aggregate_ability_groups()` is shared between component abilities and fleet auras. MAX within same `stack_group`, SUM across different groups. Default group keys differ intentionally (see AR-002) but produce identical semantics: unique providers without explicit stack_group each contribute independently via SUM.

### Skip Non-Operational / Drop on Real Loss Policy
**Status: CORRECT, no leak.** `_recalculate()` at line 357-358 skips non-operational components (they can resume when repaired — no drop). Line 349-351 drops only when the ability instance is no longer in `component.ability_instances` (real identity loss). Dead ships are skipped at line 355. Destroyed/replaced components lose their ability instances, which triggers the identity check → correct drop. The `_providers` list is compacted at line 383-384 only when entries are actually removed.

### Other Systems Audited
**Status: CLEAR.** Per decisions.md #17 and independent audit (AR-001), no other systems key on `(ship, ability_class_name)` for liveness. The `ability_aggregator.py` groups by component object, `ability_manager.py` indexes by name per component instance, and collision.py is a plain consumer. The bug class was isolated to `FleetAuraManager`.

### Tests That Should Have Caught This Earlier
**Status: NEW TESTS ARE ADEQUATE, but one gap remains.** The new test file covers single-provider characterization, multi-provider disable/symmetry, MAX semantics with re-enable, and unregister removal. However, all tests bypass the `update()` fingerprint caching path by calling `_recalculate()` directly. See CQ-004.

---

## Priority Findings

### 1. MAJOR: Derelict ship aura contribution inconsistent with UI
**ID:** CQ-001
**Agent:** Code Quality Analyst
**Location:** `game/simulation/combat/fleet_aura_manager.py:55, 341-368, 470-486`
**Issue:** The liveness checks in `_recalculate()` and `_scan_ship()` do not filter out derelict ships from aura contribution, but `get_active_bonuses()` does. The recalculate path checks only `not ship.is_alive` (line 355), not `is_derelict`. The scan path at line 115 (inside `initialize()`) also only checks `is_alive`. `get_active_bonuses()` at line 478 explicitly skips derelict ships. The `_get_provider_fingerprint()` at line 313 includes derelict status for cache invalidation — evidence this was known to be relevant — but the math path ignores it.
**Impact:** Combat math may include bonuses from derelict ships that should be incapacitated. UI and combat engine disagree.
**Recommendation:** Add `ship.is_derelict` check alongside `ship.is_alive` in `_recalculate()` (line 355) and `_scan_ship()` (line 115).
**Effort:** Simple

### 2. MINOR: get_active_bonuses reports snapshot value, not live value
**ID:** CQ-002
**Location:** `game/simulation/combat/fleet_aura_manager.py:482`
**Issue:** Uses `provider.value` (registration snapshot) rather than live `ability.value` (used by `_recalculate()` at line 364). Numerical divergence when ability values change mid-battle.
**Recommendation:** Read live `ability.value` in `get_active_bonuses()`.
**Effort:** Simple

### 3. MINOR: get_active_bonuses does not filter non-operational components
**ID:** CQ-003
**Location:** `game/simulation/combat/fleet_aura_manager.py:475-486`
**Issue:** Only filters on `is_alive`/`is_derelict`, not `component.is_operational`. `_recalculate()` at line 357 correctly skips non-operational components. UI can show phantom active bonuses.
**Recommendation:** Add `provider.component.is_operational` check to the `get_active_bonuses()` loop.
**Effort:** Simple

### 4. MINOR: No test exercising update() fingerprint caching path for re-enable
**ID:** CQ-004
**Location:** `tests/unit/simulation/combat/test_fleet_aura_provider_identity.py:181-213`
**Issue:** Tests call `_recalculate()` directly, bypassing `update()` (which uses fingerprint-based cache invalidation). The re-enable-after-disable scenario flagged by the agent in the request context is untested through the normal tick path.
**Recommendation:** Add a test calling `manager.update(ships)` after toggling `is_operational`.
**Effort:** Simple

### 5. MINOR: Default group-key logic differs between _recalculate and calculate_ability_totals
**ID:** AR-002
**Location:** `game/simulation/combat/fleet_aura_manager.py:372` vs `game/simulation/entities/ability_aggregator.py:118`
**Issue:** `_recalculate()` uses `f"_default_{id(provider)}"` (unique per provider), while `calculate_ability_totals()` uses `comp` (shared by component). Both produce correct semantics but the difference is undocumented.
**Recommendation:** Add a comment at line 372 explaining the rationale.
**Effort:** Simple

---

## Findings by Category

### Code Quality
| ID | Severity | Title | Location | Effort |
|----|----------|-------|----------|--------|
| CQ-001 | MAJOR | Derelict ship aura inconsistency | `fleet_aura_manager.py:355,115,478` | Simple |
| CQ-002 | MINOR | Snapshot vs live value in get_active_bonuses | `fleet_aura_manager.py:482` | Simple |
| CQ-003 | MINOR | get_active_bonuses skips is_operational check | `fleet_aura_manager.py:475-486` | Simple |
| CQ-004 | MINOR | No test for update() fingerprint path | `test_fleet_aura_provider_identity.py:181-213` | Simple |
| CQ-005 | INFO | No test for ability-instance identity loss | `test_fleet_aura_provider_identity.py` | Simple |

### Architecture
| ID | Severity | Title | Location | Effort |
|----|----------|-------|----------|--------|
| AR-001 | INFO | No other systems affected by same bug class | Audit of `game/simulation/` | N/A |
| AR-002 | MINOR | Default group-key logic differs across callers | `fleet_aura_manager.py:372` / `ability_aggregator.py:118` | Simple |

---

## Agent Reports
- [Code Quality](findings/code_quality_report.md)
- [Architecture](findings/architecture_report.md)

## Scope Details
See `scope.md`.
