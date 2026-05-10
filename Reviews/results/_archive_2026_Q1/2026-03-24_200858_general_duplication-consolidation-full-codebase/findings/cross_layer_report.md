# Cross-Layer Duplication Report

**Date:** 2026-03-24
**Scope:** Full codebase (`game/`) - all packages
**Focus:** Logic duplicated across 2+ architectural layers

---

## Summary

Found **10 cross-layer duplication instances** across the codebase. The most impactful patterns involve:

1. **Firing arc geometry** reimplemented in 3 locations across AI and Simulation layers
2. **Compact number formatting** (K/M suffixes) duplicated in 4+ UI files
3. **Entity lookup delegation chains** creating 4-layer deep pass-throughs for fleet/planet lookups
4. **HP-to-color mapping** implemented separately for combat UI vs strategy UI
5. **ShipFactory lazy initialization** copy-pasted between two UI screen modules

Overall the codebase shows good discipline: core math utilities (`clamp`, `lerp`, `angle_diff`, `Vector2`) are properly centralized in `game/core/math.py`, and the singleton pattern uses the canonical `SingletonMeta` metaclass consistently. Most duplication is in UI formatting helpers and cross-layer geometric calculations.

---

## Findings

#### MAJOR: Firing Arc Check Logic Duplicated Across AI and Simulation

**ID:** DUP-XL-001
**Location:**
- `game/ai/combat_utils.py:219-229` (`is_in_pdc_arc` function)
- `game/simulation/components/abilities/weapons.py:218-245` (`WeaponAbility.check_firing_solution`)
- `game/simulation/combat/weapon_firing_system.py:251-256` (inline in seeker launch logic)

**Issue:** The same geometric pattern -- compute `comp_facing = (ship_angle + facing_angle) % 360`, compute `diff = (target_angle - comp_facing + 180) % 360 - 180`, check `abs(diff) <= firing_arc / 2` -- is implemented independently in three places. The AI layer's `is_in_pdc_arc` reimplements what `WeaponAbility.check_firing_solution` already does, and `weapon_firing_system.py` also inlines the same check. Notably, `check_firing_solution` includes an epsilon tolerance (`+ 0.01`) that the other two do not, creating a subtle behavioral inconsistency.

**Impact:** Three separate implementations means three places where arc check bugs must be fixed. The epsilon discrepancy could cause AI and simulation to disagree on whether a target is in arc at boundary angles.

**Recommendation:** The simulation layer's `WeaponAbility.check_firing_solution` should be the single source of truth. The AI layer should call `weapon_ab.check_firing_solution(ship_pos, ship_angle, target_pos)` instead of reimplementing the geometry. The inline check in `weapon_firing_system.py` should also delegate to the ability's method.

**Effort:** Simple

---

#### MAJOR: Compact Number Formatting (K/M Suffixes) Reimplemented in 4+ UI Files

**ID:** DUP-XL-002
**Location:**
- `game/ui/panels/planet_report_panel.py:311-318` (`_format_compact_number`)
- `game/ui/screens/empire_build_queue_formatter.py:185-192` (inline in function)
- `game/ui/screens/planet_list_filters.py:301-306` (inline)
- `game/ui/screens/strategy_detail_fmt.py:109-121` (inline, twice)

**Issue:** The same pattern -- check `>= 1_000_000` format as `M`, check `>= 1_000` format as `k`/`K`, else integer -- is copy-pasted across at least 4 UI files. There are minor inconsistencies: some use `K` (uppercase) vs `k` (lowercase), some use `//` integer division vs `:.0f` float formatting, and some use `_` separators in literals while others don't.

**Impact:** Inconsistent display to the user (mixed K/k), multiple places to update if formatting rules change. Each reimplementation has slight behavioral differences.

**Recommendation:** Create a single `format_compact_number(value: float) -> str` utility in `game/ui/formatting.py` (or similar shared UI utility module). All UI files should import and use this single function.

**Effort:** Simple

---

#### MAJOR: ShipFactory Lazy Initialization Copy-Pasted Between UI Modules

**ID:** DUP-XL-003
**Location:**
- `game/ui/screens/setup_data_io.py:24-40` (`_get_ship_factory`)
- `game/ui/screens/setup_screen.py:36-52` (`_get_ship_factory`)

**Issue:** Both files contain an identical `_get_ship_factory()` function with the same module-level `_ship_factory = None` singleton pattern, the same imports, the same `GameRegistries` construction from `get_default_registry_provider()`, and the same `ShipFactory(registry_provider=registries)` call. This is a textbook copy-paste.

**Impact:** If ShipFactory initialization changes (e.g., new registry parameters), both files must be updated in lockstep. The duplication also creates two independent singleton instances, which may cause subtle caching issues.

**Recommendation:** Consolidate into a single factory accessor, either in a shared UI service module or by having `setup_screen.py` import from `setup_data_io.py`.

**Effort:** Simple

---

#### MAJOR: Entity Lookup 4-Layer Delegation Chain (Fleet/Planet by ID)

**ID:** DUP-XL-004
**Location:**
- `game/strategy/facade/strategy_session_facade.py:82-93` (`_get_fleet_by_id` -> delegates to session)
- `game/strategy/engine/game_session.py:208-219` (`_get_fleet_by_id` -> delegates to galaxy)
- `game/strategy/data/galaxy.py:385-396` (`get_fleet_by_id` -> delegates to registry)
- `game/strategy/data/galaxy_entity_registry.py:145-154` (`get_fleet_by_id` -> actual lookup)

Same chain exists for `get_planet_by_id` (facade -> session -> galaxy -> registry) and `_get_empire_by_id`.

**Issue:** Each layer adds a thin wrapper that does nothing but delegate. The facade's `_get_fleet_by_id` calls session's `_get_fleet_by_id`, which calls galaxy's `get_fleet_by_id`, which calls registry's `get_fleet_by_id`. This is 4 method calls deep for a single dict lookup. While individual delegation is fine in the facade pattern, the GameSession and Galaxy wrappers add no value beyond renaming.

**Impact:** Cognitive overhead for developers tracing lookups. Each layer's docstrings re-explain the same O(1) lookup. Not a correctness issue, but a maintenance burden.

**Recommendation:** Consider having the facade access `self._session.galaxy.get_fleet_by_id()` directly (or `self._session.galaxy._registry.get_fleet_by_id()`). The GameSession wrappers add no logic beyond delegation.

**Effort:** Medium (requires updating all call sites within strategy layer)

---

#### MINOR: HP-to-Color Mapping Duplicated in Two UI Panels

**ID:** DUP-XL-005
**Location:**
- `game/ui/panels/ship_detail_panel.py:29-50` (`get_damage_color`)
- `game/ui/panels/ship_stats_renderer.py:90-106` (`get_hp_bar_color`)

**Issue:** Both functions map HP percentage to a color tuple using similar threshold logic, but with different thresholds and return values:
- `get_damage_color`: 0% -> DESTROYED, <50% -> CRITICAL, <75% -> DAMAGED, else HEALTHY
- `get_hp_bar_color`: <20% -> CRITICAL, <50% -> DAMAGED, >50% -> HEALTHY

The different thresholds (50%/75% vs 20%/50%) may be intentional for different contexts, but there's no documentation explaining the design difference.

**Impact:** Two independently-maintained color scales for the same concept. If color constants change, both must be updated. The difference in thresholds could confuse developers.

**Recommendation:** If the thresholds are intentionally different (ship-level vs component-level), document why. If not, consolidate into a single parameterizable function in a shared UI colors/formatting module.

**Effort:** Simple

---

#### MINOR: Radiation Formatting Duplicated with Fallback Copy

**ID:** DUP-XL-006
**Location:**
- `game/ui/panels/race_environment_panel.py:407-416` (`_format_radiation`)
- `game/ui/screens/race_setup_screen.py:548-563` (`_format_radiation`)

**Issue:** `race_setup_screen.py:_format_radiation` delegates to `race_environment_panel._format_radiation` but also contains a complete fallback copy of the same logic "if panel not initialized." This fallback is a backward-compatibility shim that duplicates the canonical implementation.

**Impact:** Per the project's System Migration Policy, backward-compatibility layers should be eradicated. This fallback code is dead weight if the panel is always initialized.

**Recommendation:** Remove the fallback code in `race_setup_screen.py`. If the panel can be None, fix the initialization order instead of maintaining duplicate logic.

**Effort:** Simple

---

#### MINOR: `angle_to_target` via `math.atan2` Inlined Instead of Using `Vector2.angle_to`

**ID:** DUP-XL-007
**Location:**
- `game/ai/combat_utils.py:223` (`math.degrees(math.atan2(vec.y, vec.x)) % 360`)
- `game/ai/controller.py:445` (`math.degrees(math.atan2(dy, dx)) % 360`)
- `game/simulation/components/abilities/weapons.py:232` (same pattern)
- `game/simulation/combat/weapon_firing_system.py:254` (same pattern)

**Issue:** The pattern `math.degrees(math.atan2(vec.y, vec.x)) % 360` appears in 4 locations across AI and Simulation layers. `Vector2.angle_to()` exists in `game/core/math.py:166` and could replace some of these, though it returns a signed angle rather than 0-360. A dedicated `angle_to_degrees_360(vec)` utility would eliminate this repeated idiom.

**Impact:** Minor -- the pattern is well-understood. But it's a repeated computation that could be centralized for consistency.

**Recommendation:** Add a `angle_degrees_360(vec: Vector2) -> float` utility to `game/core/math.py` that wraps `math.degrees(math.atan2(vec.y, vec.x)) % 360`. Replace inlined instances.

**Effort:** Simple

---

#### MINOR: `_format_value` Implemented Independently in Multiple UI Panels

**ID:** DUP-XL-008
**Location:**
- `game/ui/panels/empire_treasury_panel.py:233-247` (formats with comma separators)
- `game/ui/panels/modifier_impact_grid.py:247-269` (formats with x/+/= prefixes and sig digits)
- `game/ui/widgets/scrollable_json_panel.py:242-256` (formats JSON primitive values)
- `game/ui/screens/test_lab/formatting_utils.py:8-33` (formats with precision modes)
- `game/ui/screens/builder/stats_config.py:46` (formats stat values)

**Issue:** Five different `_format_value` implementations exist across UI panels, each with slightly different formatting logic. While some serve genuinely different purposes (JSON rendering vs stat display), the treasury panel and build queue both format integers with comma separators using nearly identical logic.

**Impact:** The name collision makes code navigation confusing. Some implementations could share a common base formatter.

**Recommendation:** Identify which formatters are truly distinct (JSON vs stat vs resource). For the numeric-with-commas pattern, extract to a shared utility. Consider a `UIFormatters` class or module in `game/ui/` with named methods for each formatting style.

**Effort:** Medium

---

#### MINOR: `replace('_', ' ').title()` Pattern Repeated for Display Name Generation

**ID:** DUP-XL-009
**Location:**
- `game/ui/panels/modifier_impact_grid.py:239`
- `game/ui/screens/builder/right_panel.py:113, 123, 205, 215`
- `game/simulation/components/abilities/colonize.py:66`
- `game/simulation/components/modifier_introspection.py:300`
- `game/ui/panels/ship_detail_panel.py:397`
- `game/ui/screens/planet_list_filters.py:34`
- `game/ui/screens/strategy_detail_fmt.py:272`
- `game/ui/screens/test_lab/screen.py:485`
- `game/ui/screens/test_lab/test_run_details.py:313`

**Issue:** The pattern `name.replace('_', ' ').title()` to convert snake_case identifiers to display names appears in 9+ locations across UI and Simulation layers. This is a utility operation that should be a single function.

**Impact:** If display name rules change (e.g., special handling for acronyms like "HP", "ECM", "PDC"), every location must be updated independently. The modifier_impact_grid already handles "HP" as a special case that other locations don't.

**Recommendation:** Create a `display_name(snake_case: str) -> str` utility in `game/core/` or `game/ui/` that handles the conversion with a lookup table for special cases (HP, ECM, PDC, etc.). All locations should use this single function.

**Effort:** Simple

---

#### MINOR: ComponentCacheManager Uses Manual Singleton Instead of SingletonMeta

**ID:** DUP-XL-010
**Location:**
- `game/simulation/components/component.py:444-463` (manual `_instance`/`_lock` pattern)
- All other singletons use `game/core/singleton.py:SingletonMeta`

**Issue:** `ComponentCacheManager` implements its own singleton pattern with `_instance = None`, `_lock = threading.Lock()`, and double-checked locking in a class method -- exactly what `SingletonMeta` already provides. Every other singleton in the codebase uses `SingletonMeta`.

**Impact:** Inconsistent pattern. If `SingletonMeta` behavior changes (e.g., test reset support), `ComponentCacheManager` won't benefit. The manual implementation is also more error-prone.

**Recommendation:** Migrate `ComponentCacheManager` to use `metaclass=SingletonMeta`. Ensure its `reset()` method maps to `SingletonMeta.reset()`.

**Effort:** Simple

---

## Top 5 Priority List

| Priority | ID | Title | Severity | Effort |
|----------|------|-------|----------|--------|
| 1 | DUP-XL-001 | Firing arc check logic duplicated across AI/Simulation | MAJOR | Simple |
| 2 | DUP-XL-002 | Compact number formatting reimplemented 4+ times | MAJOR | Simple |
| 3 | DUP-XL-003 | ShipFactory lazy init copy-pasted between UI modules | MAJOR | Simple |
| 4 | DUP-XL-009 | `replace('_',' ').title()` pattern in 9+ locations | MINOR | Simple |
| 5 | DUP-XL-007 | atan2-to-degrees-360 pattern inlined in 4 locations | MINOR | Simple |

**Rationale:** Priorities 1-3 are MAJOR severity with Simple effort -- maximum impact for minimal cost. Priority 4 has the highest instance count (9+) making it a high-value consolidation target. Priority 5 is closely related to Priority 1 (same geometric domain) and would naturally be addressed together.

---

## Patterns That Are NOT Duplicated (Positive Findings)

The following areas show good centralization:
- **Core math utilities** (`clamp`, `lerp`, `angle_diff`, `Vector2`) are properly in `game/core/math.py`
- **Hex math** is centralized in `game/core/hex_math.py`
- **Singleton pattern** consistently uses `SingletonMeta` (except DUP-XL-010)
- **Layer iterator** (`iter_layers_and_components`) is in `game/core/patterns/layer_iterator.py`
- **Component inspector** (`iterate_design_components`, `find_ship_with_ability`) is properly centralized in `game/strategy/services/component_inspector.py`
- **Serialization** (`to_dict`/`from_dict`) is per-class as expected -- no cross-layer duplication
- **Validation utilities** are centralized in `game/core/validation_helpers.py`
