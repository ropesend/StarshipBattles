# Core Engineer Report: Ship.py Core Logic Refactor (Phase 2)

## Executive Summary
Analysis of the `Ship` core logic, component systems, and resource management has identified several critical optimizations and consistency issues. While the transition to the v2.0 Ability System is well underway, several legacy shims and redundant logic paths remain, posing risks to simulation performance and state stability. A critical bug in resource clamping was also discovered.

## Critical Issues & Optimization Hazards

### 1. Resource Management Bug (CRITICAL)
In `game/simulation/systems/resource_manager.py`, the `modify_value` method contains a catastrophic clamping error:
```python
if res.current_value > res.max_value:
    res.current_value = res.max_value
    res.current_value = 0.0  # <--- CRITICAL BUG
```
Any resource overflow (e.g., fuel intake, energy surge) will immediately reset the resource level to zero. This must be addressed immediately.

### 2. Performance Bottlenecks: Iterative Properties
The `Ship` class implements several properties that perform full O(N) traversals of all components on every access:
- `Ship.hp` / `Ship.max_hp`: Recursively sums HP across all layers.
- `Ship.max_weapon_range`: Performs complex string-based MRO checks across all components to find the maximum range.
**Impact:** High. These are frequently accessed by the UI and AI systems. Recommend caching these values in `recalculate_stats` rather than calculating on-demand.

### 3. Logic Inconsistencies & State Pollution
- **Derelict Status Conflict:** `ShipStatsCalculator.calculate` explicitly disables derelict logic (`ship.is_derelict = False`), yet `Ship.update_derelict_status` and the `is_derelict` property remain active and functional in `ship.py`. This indicates an incomplete architectural shift.
- **Double Definition of To-Hit Stats:** `baseline_to_hit_offense` and `to_hit_profile` are defined twice in `Ship.__init__` with conflicting default values (0.0 and 1.0).
- **Stat Reset Duplication:** `ShipStatsCalculator.calculate` manually resets dozens of fields, some of which are redundant or already handled by `ResourceRegistry.reset_stats()`.

## Architectural Debt & Refactor Gaps

### 1. Brittle Ability Mapping
`Component._instantiate_abilities` relies on hardcoded string-to-class mappings for resource storage and generation. This bypasses the flexibility of the `ABILITY_REGISTRY` and makes the system harder to extend without modifying core component logic.

### 2. Maintenance Hazard: MRO-based Identity Checks
The use of `ab.__class__.mro()` name checks in `Ship` and `Component` to identify weapon types is a brittle workaround for "Module Identity Drift." While effective for stability during reloads, it obscures class hierarchies and should be replaced with a robust registration or tagging system.

### 3. Redundant Mass Tracking
`Ship` tracks `current_mass` manually during component addition/removal, yet `ShipStatsCalculator` performs a full re-summation in `recalculate_stats`. This creates two sources of truth for mass that can easily drift if `recalculate_stats` is not called consistently.

### 4. Hardcoded Data Fallbacks
`load_vehicle_classes` and `Ship._initialize_layers` contain substantial hardcoded dictionaries for default behavior. These "emergency defaults" should be moved to JSON configuration to maintain strict data/logic separation.

## Recommended Actions (Phase 3)
1. **Fix the Resource Registry** clamping logic in `modify_value`.
2. **Implement Stat Caching** for `hp`, `max_hp`, and `max_weapon_range` within `ShipStatsCalculator`.
3. **Unify Derelict Logic**: Either fully remove the derelict system or reintegrate it into the `RegistryManager` validator.
4. **Clean up duplicate initializations** in `Ship.__init__`.
5. **Standardize mass tracking** to a single source of truth (the calculator).

---
**Report compiled by:** Core Engineer (Swarm Node)
**Status:** Analysis Complete / Phase 2 Oversight
