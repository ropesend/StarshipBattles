# Code Reviewer Report: Phase 3 Infrastructure & Logic Analysis

**Date:** 2026-01-04
**Reviewer:** Code_Reviewer Agent
**Focus:** Phase 3 Infrastructure (SessionCache, RegistryManager) & Logic Flaws

## Executive Summary

Phase 3 Infrastructure (`RegistryManager`, `SessionRegistryCache`, `conftest.py`) is **ARCHITECTURALLY SOUND** and correctly implements the "Fast Hydration" pattern to solve IO contention. Test isolation is preserved via deep-copying and module patching.

However, a **CRITICAL LOGIC FLAW** was detected in `Component.recalculate_stats()`, which causes complete loss of runtime state (cooldowns, stored energy) whenever modifiers are applied. This also explains the failure in `test_bug_05_logistics.py`.

## Key Findings

### 1. Infrastructure (PASSED)
The new Registry Infrastructure is robust:
- **RegistryManager**: Correctly uses in-place dictionary updates (`clear()` + `update()`) in `hydrate()`. This preserves referential identity for modules aliasing `COMPONENT_REGISTRY = RegistryManager.instance().components`, preventing stale reference bugs.
- **SessionRegistryCache**: Correctly utilizes `copy.deepcopy()` to serve fresh objects to `RegistryManager`, ensuring one test cannot pollute the next.
- **Conftest**: The fixture `reset_game_state` correctly patches `load_vehicle_classes` and `_COMPONENT_CACHE` to prevent disk I/O, ensuring strict isolation.

### 2. Critical Logic Flaw: State wiping in `recalculate_stats`
**Severity:** Critical
**Location:** `game/simulation/components/component.py`
**Method:** `recalculate_stats` -> `_reset_and_evaluate_base_formulas` -> `_instantiate_abilities`

**The Defect:**
When `recalculate_stats()` is called (e.g., when adding a modifier), it calls `_instantiate_abilities()`. This method destroys the existing `self.ability_instances` list and recreates them from raw data.
**Consequences:**
1.  **Runtime State Loss:** If a Battery has 50/100 energy, and a modifier is applied, the Battery ability is re-instantiated, resetting energy to default (100/100). Cooldowns and ammo are similarly reset.
2.  **Test Fragility:** `test_bug_05_logistics.py` manually injects `ability_instances` into the component. When `ShipStatsCalculator` runs, it triggers `recalculate_stats`, which **wipes out the manually injected abilities** and replaces them with defaults from `self.data` (which are empty or basic). This causes the assertion failure (missing "energy_gen" rows).

### 3. Logic Flaw: `take_damage` Status Inconsistency
**Severity:** Minor
**Location:** `game/simulation/components/component.py`
**Method:** `take_damage`

**The Defect:**
`take_damage` updates `current_hp` and `is_active` (on destruction), but fails to update `self.status`. It does not transition to `ComponentStatus.DAMAGED` or other states defined in the Enum.

## Recommendations

### Immediate Actions (Phase 4 Logic Repair)

1.  **Refactor `recalculate_stats` Ability Handling:**
    *   **Do NOT** blindly destroy ability instances.
    *   Implement a `sync_abilities` method that:
        *   Check if ability exists.
        *   If it exists, `recalculate()` its stats (capacity, rate) based on new multipliers.
        *   **Preserve** current state (current energy, cooldown timer).
        *   Only instantiate NEW abilities if they were added by the modifier (unlikely but possible).

2.  **Fix `test_bug_05_logistics.py`:**
    *   Update the test to set up components correctly via `data` dict or `abilities` dict, NOT by overwriting `ability_instances` directly, OR patch `request_recalc` to be no-op if focusing on UI only.
    *   *Best Practice:* Define component data properly so proper hydration works.

### Validated Code Patterns
The following patterns are verified safe and should be retained:
*   `RegistryManager.instance().hydrate(...)`
*   `SessionRegistryCache.instance().get_components()` (Deep Copy)

## Conclusion
Proceed to **Phase 4**, prioritized on fixing `Component.recalculate_stats`. The infrastructure is ready.
