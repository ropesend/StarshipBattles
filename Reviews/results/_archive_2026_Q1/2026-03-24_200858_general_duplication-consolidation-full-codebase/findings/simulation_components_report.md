# Simulation Components Duplication Report

**Scope:** `game/simulation/components/` and `game/simulation/components/abilities/`
**Date:** 2026-03-24
**Files Reviewed:** 20 Python files (all files in scope)

## Executive Summary

The codebase has already undergone significant consolidation work (PROJ-176 introduced `SimpleMultiplierAbility`, PROJ-176 introduced `SuperweaponMarker`). These abstractions eliminated what would have been the most severe duplication. The remaining duplication is moderate -- primarily in defense ability classes that share identical structure, resource ability classes with repeated sync_data/recalculate patterns, and duplicated default stats dictionaries.

**Findings:** 8 total (3 MAJOR, 5 MINOR)

---

## Findings

#### MAJOR: ToHitAttackModifier and ToHitDefenseModifier are near-identical classes
**ID:** DUP-CMP-001
**Location:** `abilities/defense.py:53-97` (ToHitAttackModifier lines 53-76, ToHitDefenseModifier lines 78-97)
**Issue:** These two classes share identical structure: same `__init__` (parse value, store base), same no-op `recalculate`, same `get_primary_value`, and nearly identical `get_ui_rows` (differ only in label string and color hint). Both are simple value-holding abilities with no stat bindings and no modifier support.
**Impact:** 45 lines where ~25 are duplicated. Any behavioral change (e.g., adding modifier support) must be applied to both. They are strong candidates for `SimpleMultiplierAbility` or a shared base class.
**Recommendation:** Create a `SimpleValueAbility` base class (or use `SimpleMultiplierAbility` with a stat_key of '' and override recalculate to no-op), parameterized by `ui_label`, `ui_color`, and `ui_format`. Both classes become 3-line subclasses setting class attributes. EmissiveArmor (lines 100-117) shares the same pattern and could also use it.
**Effort:** Simple

---

#### MAJOR: EmissiveArmor duplicates ToHitAttackModifier/ToHitDefenseModifier pattern
**ID:** DUP-CMP-002
**Location:** `abilities/defense.py:100-117` (EmissiveArmor)
**Issue:** EmissiveArmor follows the exact same pattern as ToHitAttackModifier and ToHitDefenseModifier: parse a single value in `__init__`, store `_base_amount`, no-op `recalculate`, single-row `get_ui_rows`, trivial `get_primary_value`. The only differences are: attribute name (`amount` vs `value`), int cast, and UI label/color.
**Impact:** Combined with DUP-CMP-001, this is 3 classes with ~65 total lines sharing an identical pattern. This is the most impactful consolidation opportunity in the abilities subsystem.
**Recommendation:** Consolidate all three into subclasses of a `StaticValueAbility` base class that handles: parse value, store base, return primary value, and format a single UI row. Parameters: `value_attr`, `base_attr`, `ui_label`, `ui_color`, `cast_fn` (int vs float).
**Effort:** Simple

---

#### MAJOR: ResourceConsumption, ResourceStorage, ResourceGeneration share sync_data/recalculate boilerplate
**ID:** DUP-CMP-003
**Location:** `abilities/resources.py:10-230`
**Issue:** All three resource abilities follow the same structural pattern:
1. `__init__`: Parse `resource_type` and a numeric value from dict, store `_base_*`
2. `sync_data`: Re-parse from dict or scalar, reset `_base_*`
3. `recalculate`: `current = _base * get_effective_stat(key, 1.0)`
4. `get_ui_rows`: Format with resource-type-specific color
5. `get_primary_value`: Return current value

The sync_data methods in particular are nearly identical across all three (and also CargoStorage in `cargo.py:49-58`). Each has the same `if isinstance(data, dict) ... elif isinstance(data, (int, float))` branching.
**Impact:** ~220 lines across 3 classes (plus CargoStorage) with significant structural duplication. Sync_data alone accounts for ~40 duplicated lines across the four classes.
**Recommendation:** Extract a `ResourceAbility` base class that handles the common `resource_type` + numeric value pattern with generic sync_data. Subclasses only specify: which attribute name to use, which stat key for recalculation, and UI formatting. Alternatively, these could potentially use `SimpleMultiplierAbility` if it were extended to support `resource_type` parsing.
**Effort:** Medium

---

#### MINOR: Duplicate default stats dictionaries in modifiers.py and stat_keys.py
**ID:** DUP-CMP-004
**Location:** `modifiers.py:120-157` (`get_default_stat_multipliers()`) and `abilities/stat_keys.py:63-101` (`StatKey.get_default()` + `create_default_stats_dict()`)
**Issue:** Two independent sources of truth for default stat values. `get_default_stat_multipliers()` returns a hardcoded dict. `StatKey.create_default_stats_dict()` builds the same dict from enum values using `get_default()`. Both must be kept in sync manually. If a new stat key is added to `StatKey` enum but not to `get_default_stat_multipliers()`, or vice versa, they will silently diverge.
**Impact:** Maintenance burden -- adding a new stat key requires updating two places. Risk of silent divergence.
**Recommendation:** Have `get_default_stat_multipliers()` delegate to `StatKey.create_default_stats_dict()`, making `StatKey` the single source of truth. Or vice versa -- pick one canonical location and have the other call it.
**Effort:** Simple

---

#### MINOR: WeaponAbility __init__ and sync_data both parse damage/range/reload with formula handling
**ID:** DUP-CMP-005
**Location:** `abilities/weapons.py:51-148`
**Issue:** The `__init__` method (lines 51-110) and `sync_data` method (lines 112-148) both contain formula-parsing logic for damage, range, and reload. Each field follows the same pattern: check if string starts with '=', evaluate formula, store float. This pattern is repeated 3 times in `__init__` and 3 times in `sync_data`, for 6 total occurrences.
**Impact:** ~60 lines of duplicated formula-parsing boilerplate within a single class. Adding a new formula-capable field requires adding the pattern in two places.
**Recommendation:** Extract a `_parse_formula_field(data, key, default)` helper method that handles the `isinstance(raw, str) and raw.startswith('=')` check. Use it in both `__init__` and `sync_data` to reduce each field parse to a single line.
**Effort:** Simple

---

#### MINOR: CargoStorage duplicates ResourceStorage pattern
**ID:** DUP-CMP-006
**Location:** `abilities/cargo.py:14-79` and `abilities/resources.py:153-190`
**Issue:** `CargoStorage` and `ResourceStorage` are structurally identical: both store a typed capacity value, parse from dict/scalar, sync_data with the same branching, recalculate with `capacity_mult`, and provide single-row UI output. The only real differences are: CargoStorage uses `cargo_type` instead of `resource_type`, and different UI color logic.
**Impact:** ~65 lines of duplicated structure across two files. They even share the same `STAT_BINDINGS` (`CAPACITY_MULT`).
**Recommendation:** Merge `CargoStorage` into `ResourceStorage` with a generalized "storage type" concept, or extract a shared `TypedCapacityAbility` base. Given they serve different game layers (cargo is STRATEGIC), a shared base that both inherit from is cleaner.
**Effort:** Medium (requires updating all references and tests)

---

#### MINOR: EmpireStorageAbility duplicates ResourceStorage/CargoStorage capacity pattern
**ID:** DUP-CMP-007
**Location:** `abilities/harvester.py:46-93`
**Issue:** `EmpireStorageAbility` follows the same capacity-with-type pattern as `ResourceStorage` and `CargoStorage`: stores `resource_type` + `capacity`, has `_base_capacity`, `recalculate` with a multiplier stat, and returns capacity as primary value. It uses `storage_mult` instead of `capacity_mult` for its recalculate, but the structural pattern is identical.
**Impact:** Third instance of the same storage pattern. Combined with DUP-CMP-006, there are now 3 classes (~150 lines) with the same structure.
**Recommendation:** Include in the `TypedCapacityAbility` extraction from DUP-CMP-006. Each subclass specifies its stat_key and UI formatting.
**Effort:** Medium (same effort as DUP-CMP-006, consolidate together)

---

#### MINOR: apply_modifier_effects duplicates _apply_effect_to_dict logic inline
**ID:** DUP-CMP-008
**Location:** `modifiers.py:15-49` (`_apply_effect_to_dict`) and `modifiers.py:51-117` (`apply_modifier_effects`)
**Issue:** `_apply_effect_to_dict` is a clean helper for applying an effect to a dict by operation type. However, `apply_modifier_effects` largely reimplements the same switch logic inline (lines 85-117) rather than consistently using `_apply_effect_to_dict`. The inline version adds special-case handling for specific stat keys (`mass_add`, `arc_add`, `accuracy_add`, `facing_angle`), but the core multiply/add/set logic is duplicated.
**Impact:** ~30 lines of duplicated switch logic. The inline version has subtle differences (e.g., the `add` branch has hardcoded fallback keys) that could diverge from `_apply_effect_to_dict`.
**Recommendation:** Refactor `apply_modifier_effects` to use `_apply_effect_to_dict` for the standard cases, with pre-processing for the special cases (facing_angle -> properties, etc.). The special key handling can be done before the generic application.
**Effort:** Simple

---

## Top 5 Priority Consolidation List

| Priority | ID | Severity | Title | Est. Lines Saved | Effort |
|----------|------------|----------|-------|-----------------|--------|
| 1 | DUP-CMP-001 + DUP-CMP-002 | MAJOR | Extract `StaticValueAbility` for ToHitAttack, ToHitDefense, EmissiveArmor | ~35 | Simple |
| 2 | DUP-CMP-003 + DUP-CMP-006 + DUP-CMP-007 | MAJOR | Extract `ResourceAbility` / `TypedCapacityAbility` for all resource/storage classes | ~80 | Medium |
| 3 | DUP-CMP-004 | MINOR | Unify default stats dict (single source of truth) | ~25 | Simple |
| 4 | DUP-CMP-005 | MINOR | Extract formula-field parser in WeaponAbility | ~30 | Simple |
| 5 | DUP-CMP-008 | MINOR | Consolidate apply_modifier_effects onto _apply_effect_to_dict | ~20 | Simple |

**Total estimated lines saved:** ~190 lines
**Total estimated effort:** 2 Medium + 3 Simple tasks

---

## Notes

- The existing `SimpleMultiplierAbility` base class (PROJ-176) is well-designed and has already eliminated what would have been the largest source of duplication (7 ability classes). The remaining duplication is in classes that don't quite fit its pattern (static values with no modifier support, resource-typed capacities).
- The `SuperweaponMarker` base class is similarly well-designed and has eliminated duplication across 6 superweapon classes.
- The weapon type hierarchy (WeaponAbility -> Projectile/Beam/Seeker) is clean and uses proper inheritance. No significant duplication there beyond the formula parsing noted in DUP-CMP-005.
- The modifier system files (modifiers.py, modifier_effects.py, modifier_schema.py, modifier_introspection.py) are well-separated with clear responsibilities. DUP-CMP-008 is the only real issue there.
