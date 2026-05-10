# PROJ-225: Simulation Layer Consolidation (Dedup Campaign 2/5)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/project_status.py PROJ-225` to see what to do next
> - Open the phase checklist file for your current phase

## Overview
Consolidate duplicated logic within the simulation layer: component abilities, ship entities, physics formulas, and firing arc geometry. Second project in the 5-project duplication elimination campaign.

**Source Review:** `Reviews/results/2026-03-24_200858_general_duplication-consolidation-full-codebase/`
**Depends On:** PROJ-224 (complete) -- shared utilities created there

## Goals
1. Extract `StaticValueAbility` base class for defense abilities
2. Extract shared physics formula functions
3. Consolidate Ship component addition and hull auto-equip
4. Consolidate modifier effects and weapon formula parsing
5. Unify firing arc checks across AI and simulation

## Scope
- `game/simulation/components/abilities/defense.py` -- StaticValueAbility extraction
- `game/simulation/components/abilities/weapons.py` -- formula parser extraction
- `game/simulation/components/modifiers.py` -- apply_modifier_effects consolidation
- `game/simulation/components/abilities/stat_keys.py` -- default stats single source of truth
- `game/simulation/entities/ship.py` -- hull auto-equip, component addition, max_mass constant
- `game/simulation/entities/ship_stats.py` -- physics formula extraction
- `game/simulation/entities/ship_physics.py` -- use shared physics formulas
- `game/simulation/entities/ship_stat_querier.py` -- remove redundant cached_summary
- `game/simulation/entities/ship_serialization.py` -- layers_dict dedup
- `game/simulation/physics_constants.py` -- shared formula functions
- `game/ai/combat_utils.py` -- delegate firing arc to WeaponAbility
- `game/simulation/combat/weapon_firing_system.py` -- delegate firing arc to WeaponAbility
- `game/simulation/components/component.py` -- ComponentCacheManager singleton

## Findings (18)

### Phase 1: StaticValueAbility + Physics Formulas
| ID | Severity | Description |
|----|----------|-------------|
| DUP-CMP-001 | MAJOR | ToHitAttackModifier and ToHitDefenseModifier are near-identical |
| DUP-CMP-002 | MAJOR | EmissiveArmor duplicates same pattern |
| DUP-SIM-001 | MAJOR | Physics formulas duplicated between ship_stats.py and ship_physics.py |

### Phase 2: Ship Entity Deduplication
| ID | Severity | Description |
|----|----------|-------------|
| DUP-SIM-002 | MAJOR | Hull auto-equip logic duplicated in __init__ and change_class |
| DUP-SIM-003 | MAJOR | Component addition boilerplate duplicated in add_component/add_components_bulk |
| DUP-SIM-009 | MINOR | ModifierService late import repeated in loop (part of SIM-003) |
| DUP-SIM-005 | MINOR | max_mass_budget lookup uses magic number 1000 in 4 places |

### Phase 3: Component Ability Consolidation
| ID | Severity | Description |
|----|----------|-------------|
| DUP-CMP-005 | MINOR | WeaponAbility __init__ and sync_data both parse formula fields |
| DUP-CMP-008 | MINOR | apply_modifier_effects duplicates _apply_effect_to_dict logic inline |
| DUP-CMP-004 | MINOR | Default stats dict has two independent sources of truth |

### Phase 4: Cross-Cutting + Minor Cleanup
| ID | Severity | Description |
|----|----------|-------------|
| DUP-XL-001 | MAJOR | Firing arc check duplicated across AI and simulation |
| DUP-XL-010 | MINOR | ComponentCacheManager uses manual singleton instead of SingletonMeta |
| DUP-SIM-007 | MINOR | cached_summary property exists on both Ship and ShipStatQuerier |
| DUP-SIM-010 | MINOR | Ship.layers_dict duplicates serialization logic |

## Execution Order
**2nd of 5 projects** -- depends on PROJ-224 utilities (complete).

## Phase Summary
| Phase | Description | Status |
|-------|-------------|--------|
| 1 | StaticValueAbility + Physics Formulas | Complete |
| 2 | Ship Entity Deduplication | Complete |
| 3 | Component Ability Consolidation | Complete |
| 4 | Cross-Cutting + Minor Cleanup | Complete |

## Success Criteria
- [x] All 13434+ tests pass (13471 passed, 2 skipped)
- [x] StaticValueAbility base class exists, ToHit*/EmissiveArmor use it
- [x] Physics formulas extracted to shared functions
- [x] Hull auto-equip extracted to single method
- [x] Component addition uses shared `_attach_component`
- [x] DEFAULT_MAX_MASS named constant exists
- [x] WeaponAbility uses `_parse_formula_field` helper
- [x] `apply_modifier_effects` delegates to `_apply_effect_to_dict`
- [x] Firing arc check has single source of truth
- [x] ComponentCacheManager uses SingletonMeta

## Current State
**Last Updated:** 2026-03-24
**Last Agent Action:** Completed all 4 phases -- project is complete.
**Next Action:** None -- project complete.
**Blockers:** None
**Context for Next Agent:** All phases complete. 13471 tests pass (37 new tests added). Key changes:
- Phase 1: Created `StaticValueAbility` base class in base.py; extracted `compute_acceleration`/`compute_max_speed` to physics_constants.py
- Phase 2: Extracted `_equip_default_hull()` and `_attach_component()` on Ship; added `DEFAULT_MAX_MASS` constant
- Phase 3: Extracted `_parse_formula_field()` for WeaponAbility; consolidated `apply_modifier_effects` onto `_apply_effect_to_dict`; unified default stats to delegate to `StatKey.create_default_stats_dict()`
- Phase 4: Consolidated AI firing arc to delegate to `WeaponAbility.check_firing_solution()`; migrated ComponentCacheManager to SingletonMeta; removed unused `cached_summary` from ShipStatQuerier and dead `layers_dict` from Ship
