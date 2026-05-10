# Code Quality Analysis: Fleet Aura Provider Identity (PROJ-357)

## Summary
- Total issues found: 5
- Critical: 0, Major: 1, Minor: 3, Info: 1

## Findings

#### MAJOR: Derelict ship aura contribution inconsistent with UI

**ID:** CQ-001
**Location:** `game/simulation/combat/fleet_aura_manager.py:55, 341-368, 470-486`
**Issue:** The liveness checks in `_recalculate()` and `_scan_ship()` do not filter out derelict ships from aura contribution, but `get_active_bonuses()` does. The recalculate path at line 355 checks only `not ship.is_alive`, not `is_derelict`. The scan path at line 115 (inside `initialize()`) also only checks `is_alive`. Meanwhile, `get_active_bonuses()` at line 478 explicitly skips derelict ships. This means a derelict ship can silently contribute fleet auras in combat math while the UI reports it as inactive. The `_get_provider_fingerprint()` at line 313 *does* include derelict status for cache invalidation, suggesting the code was aware of derelict as a relevant state — but the actual math path ignores it.
**Impact:** Combat math may include bonuses from derelict ships that should be incapacitated. The UI and combat engine disagree on whether a derelict provider is live. This is a pre-existing issue (not introduced by PROJ-357) but is in the same category of incomplete liveness-check patterns.
**Recommendation:** Add a `ship.is_derelict` check alongside `ship.is_alive` in `_recalculate()` (line 355) and in `_scan_ship()` (line 115) to match the `get_active_bonuses()` filter at line 478. Alternatively, document that derelict ships are intended to retain auras and fix `get_active_bonuses()` to match — but the fingerprint inclusion suggests the former is intended.
**Effort:** Simple

#### MINOR: get_active_bonuses reports snapshot value, not live value

**ID:** CQ-002
**Location:** `game/simulation/combat/fleet_aura_manager.py:482`
**Issue:** `get_active_bonuses()` reads `provider.value` (the snapshot captured at registration time in `_scan_ship`, line 248) rather than the live `ability.value` as read by `_recalculate()` at line 364. The docstring at line 32 explicitly states this is intentional for UI display, but it creates a numerical divergence between what the UI shows and what combat math uses whenever an ability's value changes mid-battle (e.g., formula re-resolution).
**Impact:** UI may display incorrect bonus values after ability re-resolution. Confusing for players debugging fleet buffs.
**Recommendation:** Either (a) read live `ability.value` in `get_active_bonuses()` to match `_recalculate`, or (b) add a comment at the display site noting the value is a registration-time snapshot. Option (a) is preferred for correctness.
**Effort:** Simple

#### MINOR: get_active_bonuses does not filter non-operational components

**ID:** CQ-003
**Location:** `game/simulation/combat/fleet_aura_manager.py:475-486`
**Issue:** `get_active_bonuses()` iterates `_providers` and only filters on `is_alive` and `is_derelict` (line 478). It does NOT check whether the provider's `component.is_operational` is True. The `_recalculate()` path at line 357 correctly skips non-operational components for math contribution. This means the UI can display a bonus as "active" for a disabled component that is not actually contributing to combat.
**Impact:** UI shows phantom active bonuses for disabled components. Players may think a bonus is active when it is not.
**Recommendation:** Add a `provider.component.is_operational` check (guarded with `getattr` for safety) in the `get_active_bonuses()` loop, consistent with the `_recalculate()` skip at line 357.
**Effort:** Simple

#### MINOR: No test exercising update() fingerprint caching path for re-enable scenario

**ID:** CQ-004
**Location:** `tests/unit/simulation/combat/test_fleet_aura_provider_identity.py:181-213`
**Issue:** The `test_same_class_multi_provider_same_stack_group_max` test exercises component disable/re-enable by directly calling `_recalculate()` after setting `_providers_dirty = True`. No test exercises the full `update()` path, which includes fingerprint-based cache invalidation (lines 292-300). The fingerprint at `_get_provider_fingerprint()` includes operational component count (line 312), which *should* trigger invalidation on component state changes, but this is not covered. This is the exact "re-enable-after-disable" path the agent flagged as subtle in the request context.
**Impact:** Fingerprint caching bug could mask issues where a re-enabled component's aura fails to apply through the normal `update()` tick path. The test that "caught" the issue (per request context) bypasses the fingerprint entirely.
**Recommendation:** Add a test that calls `manager.update(ships)` (not `_recalculate()` directly) after toggling component `is_operational`, verifying the fingerprint path correctly recalculates.
**Effort:** Simple

#### INFO: No test for ability-instance identity loss (component replacement)

**ID:** CQ-005
**Location:** `tests/unit/simulation/combat/test_fleet_aura_provider_identity.py`
**Issue:** The `_recalculate()` drop-on-identity-loss logic at line 347-351 checks whether the provider's `ability` instance is still in the component's `ability_instances`. No test verifies this path — e.g., a component being replaced or an ability being re-materialized (new instance, same class). The multi-provider disable tests at lines 127-180 only toggle `is_operational`, which is the "skip" path, not the "drop" path.
**Impact:** Low. The identity loss path is straightforward and indirectly covered by `unregister_ship()` and ship-death tests. But direct coverage of component/ability replacement would improve confidence.
**Recommendation:** Add a test where a component's `ability_instances` list is replaced with a different ability instance (same class, different object), confirming the provider is dropped and the bonus recalculates correctly.
**Effort:** Simple

## Top 5 Priority Issues
1. **CQ-001 (MAJOR):** Derelict ship aura inconsistency — incomplete liveness check in `_recalculate()` and `_scan_ship()` vs `get_active_bonuses()`
2. **CQ-004 (MINOR):** No test for `update()` fingerprint caching path with re-enable-after-disable
3. **CQ-003 (MINOR):** `get_active_bonuses()` doesn't filter non-operational components (UI shows phantom bonuses)
4. **CQ-002 (MINOR):** `get_active_bonuses()` reports snapshot value, not live value
5. **CQ-005 (INFO):** No test for ability-instance identity loss (component replacement)
