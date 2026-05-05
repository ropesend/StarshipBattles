# Architecture Review: Fleet Aura Provider Identity (PROJ-357)

## Summary
- Total issues found: 2
- Critical: 0, Major: 0, Minor: 1, Info: 1

## Findings

#### INFO: Provider identity fix correctly scoped — no other systems affected

**ID:** AR-001
**Location:** Audit of `game/simulation/` for (ship, ability_class_name) keying patterns
**Issue:** The instruction asked to audit other systems that key on `(ship, ability_class_name)` for similar bugs. Per the decisions.md (#17), this was already confirmed: "No other systems key on (ship, ability_class_name) for liveness — confirmed via grep on AuraProvider constructor sites (only 2 callers, both updated)." My independent audit confirms this:
- `ability_aggregator.py:calculate_ability_totals()` groups by component object (line 118: `group_key = stack_group if stack_group else comp`), not by ability class name. This is the correct pattern — same-class abilities on the same component MAX, different components SUM.
- `ability_aggregator.py:get_ability_instances_by_class()` yields `(component, ability)` pairs by class name (line 202-203), but this is a read-only query utility, not a liveness/stacking mechanism.
- `ability_manager.py` indexes by `ability_name` → `set[Ability]` (line 106), but this is per-component instance indexing for lookup, not a stacking or identity decision.
- `component.py:get_abilities(ability_name)` delegates to `ability_manager.get_abilities()` which returns correct per-instance references.
- `ship.py:get_total_ability_value(ability_name)` delegates to `stat_querier.get_total_ability_value()` which uses `calculate_ability_totals()` with component-object grouping. Correct.
- `collision.py:115,120` reads `fleet_attack_bonus` / `fleet_defense_bonus` as plain numeric attributes — just consumers, not identity managers.
**Impact:** None. The bug class was isolated to `FleetAuraManager._recalculate()` alone, and the fix is correctly self-contained.
**Recommendation:** None needed. This confirms the decisions.md audit result.
**Effort:** N/A

#### MINOR: _aggregate_ability_groups default group-key logic differs between callers

**ID:** AR-002
**Location:** `game/simulation/combat/fleet_aura_manager.py:372` vs `game/simulation/entities/ability_aggregator.py:118`
**Issue:** Both `FleetAuraManager._recalculate()` and `calculate_ability_totals()` use `_aggregate_ability_groups()` for two-phase aggregation, but they construct group keys differently for providers without explicit `stack_group`:
- `_recalculate()`: `f"_default_{id(provider)}"` — unique per AuraProvider instance
- `calculate_ability_totals()`: `comp` (the component object) — shared by abilities on the same component

These are not semantically identical. In `_recalculate()`, every provider without a stack_group gets a unique key, meaning they all SUM. In `calculate_ability_totals()`, two same-class abilities on the *same component* without a stack_group share a group, meaning they MAX. The difference is intentional: fleet auras are per-provider (ship+component+ability triple), while component abilities are per-component. However, this subtle difference is not documented and could surprise someone refactoring to share more logic between the two paths.
**Impact:** Low. Current behavior is correct and intentional. The risk is future refactoring accidentally collapsing the two patterns.
**Recommendation:** Add a comment in `_recalculate()` at the group-key construction (line 372) explaining why `id(provider)` is the correct default (not `comp`): each provider is a unique (ship, component, ability) triple, and providers without explicit stack_groups should SUM because they represent independent sources (different components on the same ship, or different ships).
**Effort:** Simple
