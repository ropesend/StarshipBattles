# PROJ-12 Phase 1: Ship Combat Extraction

## Phase Overview
Extract combat logic from Ship class into ShipCombatEngine.

**Status:** Complete

## Prerequisites
- [x] PROJ-11 Phase 1-2 complete (Vector2 replacement) - Archived, Vector2 in game/core/math.py

## Tasks

### Create ShipCombatEngine Class
- [x] Create `game/simulation/entities/ship_combat_engine.py`
- [x] Define ShipCombatEngine class with clear interface
- [x] Move fire_weapons() logic from ShipCombatMixin
- [x] Move take_damage() logic
- [x] Move solve_lead() calculation
- [x] Move target selection logic (select_target method added)
- [x] Add type hints and docstrings

### Extract fire_weapons() Sub-Methods (CQ-002)
- [x] Extract `_process_hangar_launch()` for vehicle launch
- [x] Extract `_process_weapon_fire()` for weapon processing (renamed from _fire_weapon_ability)
- [x] Extract `_find_valid_target()` for targeting (renamed from _select_target_from_candidates)
- [x] Extract `_create_attack()` for attack creation
- [x] Extract `_create_seeker_projectile()` for missile projectiles
- [x] Extract `_create_standard_projectile()` for standard projectiles
- [x] Each method < 30 lines
- [x] Clear single responsibility per method

### Update Ship Class
- [x] Keep ShipCombatMixin as thin wrapper
- [x] Delegate to ShipCombatEngine internally via combat_engine property
- [x] Maintain backward-compatible interface
- [x] Lazy initialization of combat engine

### Handle Dependencies
- [x] ShipCombatEngine receives Ship via constructor
- [x] Ship creates/owns ShipCombatEngine instance (lazy via property)
- [x] Ensure no circular dependencies (TYPE_CHECKING imports)
**Notes:** Decided against passing ProjectileManager/SpatialGrid to constructor. Instead, engine accesses Ship's data directly which is simpler and matches existing patterns.

### Unit Tests
- [x] Create `tests/unit/simulation/test_ship_combat_engine.py`
- [x] Test fire_weapons() with various weapon types
- [x] Test target selection logic
- [x] Test damage application
- [x] Test projectile creation
- [x] Test with mock Ship and ProjectileManager

### Integration Tests
- [x] Existing ship combat tests still pass (74/74)
- [x] Battle engine tests still pass (26/26)
- [x] AI controller tests still pass (part of integration tests)

## Verification
- [x] ShipCombatMixin reduced from ~420 lines to ~185 lines (thin facade)
- [x] ShipCombatEngine ~380 lines (contains all combat logic with sub-methods)
- [x] All combat-related tests pass
- [x] No functionality regression

## Implementation Notes
- Used facade pattern: ShipCombatMixin now delegates all methods to ShipCombatEngine
- Lazy initialization via `combat_engine` property prevents import cycles
- Fixed import issue: test_projectiles.py was importing AttackType from wrong module
- All 21 new unit tests pass + all existing tests maintain compatibility
