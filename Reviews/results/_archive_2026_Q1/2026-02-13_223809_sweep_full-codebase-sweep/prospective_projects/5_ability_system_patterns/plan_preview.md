# PROJ-XXX: Ability System Pattern Consolidation

## Project Goal
Extract common patterns in the ability system to base class methods and create a unified component ability extraction service for the strategy layer.

## Current State
- 11+ ability classes repeat identical 5-line `__init__` patterns
- `sync_data` patterns duplicated across 6+ abilities
- `recalculate` single-line pattern repeated 9+ times
- HarvestingEngine and FleetCapabilityCalculator duplicate ability extraction logic
- ProductionEngine has duplicated ship/facility creation logic

## Target State
- Ability base class provides `_init_single_value_stat()`, `_sync_single_value_stat()`, `_ui_row()` helpers
- Single `ComponentAbilityExtractor` service for all ability lookups
- Consolidated creation helpers in ProductionEngine
- DRY principle applied throughout ability system

---

## Phase 1: Ability Base Class Helpers
**Status:** Not Started

### Tasks
- [ ] 1.1 Add `_init_single_value_stat(attr_name, default=0, cast=float)` to Ability base
- [ ] 1.2 Add `_sync_single_value_stat(attr_name, data, cast=float)` helper
- [ ] 1.3 Add `_ui_row(label, value, color)` helper for standard row format
- [ ] 1.4 Add `_parse_formula_or_value(raw_value, default, context={})` helper
- [ ] 1.5 Add tests for new base class helpers
- [ ] 1.6 Run test suite

### Files Affected
- `game/simulation/components/abilities/base.py` (or appropriate base file)
- `tests/unit/simulation/components/abilities/test_ability_base.py` (new)

---

## Phase 2: Ability Class Refactoring
**Status:** Not Started

### Tasks
- [ ] 2.1 Refactor ShieldProjection to use `_init_single_value_stat`
- [ ] 2.2 Refactor ShieldRegeneration to use helpers
- [ ] 2.3 Refactor ToHitAttackModifier to use helpers
- [ ] 2.4 Refactor ToHitDefenseModifier to use helpers
- [ ] 2.5 Refactor EmissiveArmor to use helpers
- [ ] 2.6 Refactor CrewCapacity to use helpers
- [ ] 2.7 Refactor LifeSupportCapacity to use helpers
- [ ] 2.8 Refactor CrewRequired to use helpers
- [ ] 2.9 Refactor CombatPropulsion to use helpers
- [ ] 2.10 Refactor ManeuveringThruster to use helpers
- [ ] 2.11 Refactor StrategicMovement to use helpers
- [ ] 2.12 Refactor ResourceStorage to use helpers
- [ ] 2.13 Refactor ResourceGeneration to use helpers
- [ ] 2.14 Refactor WeaponAbility to use `_parse_formula_or_value`
- [ ] 2.15 Run test suite

### Files Affected
- `game/simulation/components/abilities/defense.py`
- `game/simulation/components/abilities/crew.py`
- `game/simulation/components/abilities/propulsion.py`
- `game/simulation/components/abilities/resources.py`
- `game/simulation/components/abilities/weapons.py`

---

## Phase 3: Component Ability Extraction Service
**Status:** Not Started

### Tasks
- [ ] 3.1 Create `game/strategy/services/component_ability_extractor.py`
- [ ] 3.2 Implement `get_ability(component_entry, ability_name, registries) -> Optional[dict]`
- [ ] 3.3 Handle inline dict abilities
- [ ] 3.4 Handle registry lookup for ability_id references
- [ ] 3.5 Update HarvestingEngine to use new service
- [ ] 3.6 Update FleetCapabilityCalculator to use new service
- [ ] 3.7 Add comprehensive tests for extractor
- [ ] 3.8 Run test suite

### Files Created
- `game/strategy/services/component_ability_extractor.py`
- `tests/unit/strategy/services/test_component_ability_extractor.py`

### Files Modified
- `game/strategy/engine/harvesting_engine.py`
- `game/strategy/data/fleet_capability_calculator.py`

---

## Phase 4: Strategy Consolidation
**Status:** Not Started

### Tasks
- [ ] 4.1 Extract `_create_ship_instance()` helper in ProductionEngine
- [ ] 4.2 Refactor `_spawn_ship()` to use helper
- [ ] 4.3 Refactor `_spawn_fleet_ship()` to use helper
- [ ] 4.4 Extract `_create_facility()` helper
- [ ] 4.5 Refactor `_spawn_complex()` to use helper
- [ ] 4.6 Refactor `_spawn_fleet_complex()` to use helper
- [ ] 4.7 Extract star generation helpers in stars.py
- [ ] 4.8 Extract `iterate_design_components()` utility
- [ ] 4.9 Run full test suite
- [ ] 4.10 Final audit

### Files Affected
- `game/strategy/engine/production_engine.py`
- `game/strategy/data/stars.py`
- `game/core/design_utils.py` (new, or appropriate location)

---

## Success Metrics
- [ ] Ability classes reduced by ~5 lines each
- [ ] Single ability extraction service
- [ ] ProductionEngine ship/facility creation consolidated
- [ ] All tests passing
- [ ] No duplicate ability patterns remaining
