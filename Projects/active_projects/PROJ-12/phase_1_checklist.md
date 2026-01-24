# PROJ-12 Phase 1: Ship Combat Extraction

## Phase Overview
Extract combat logic from Ship class into ShipCombatEngine.

## Prerequisites
- [ ] PROJ-11 Phase 1-2 complete (Vector2 replacement)

## Tasks

### Create ShipCombatEngine Class
- [ ] Create `game/simulation/entities/ship_combat_engine.py`
- [ ] Define ShipCombatEngine class with clear interface
- [ ] Move fire_weapons() logic from ShipCombatMixin
- [ ] Move take_damage() logic
- [ ] Move solve_lead() calculation
- [ ] Move target selection logic
- [ ] Add type hints and docstrings

### Extract fire_weapons() Sub-Methods (CQ-002)
- [ ] Extract `_process_hangar_launch()` for vehicle launch
- [ ] Extract `_fire_weapon_ability()` for weapon processing
- [ ] Extract `_select_target_from_candidates()` for targeting
- [ ] Extract `_create_projectile()` for projectile creation
- [ ] Each method < 30 lines
- [ ] Clear single responsibility per method

### Update Ship Class
- [ ] Keep ShipCombatMixin as thin wrapper
- [ ] Delegate to ShipCombatEngine internally
- [ ] Maintain backward-compatible interface
- [ ] Mark old methods for eventual deprecation

### Handle Dependencies
- [ ] ShipCombatEngine receives ProjectileManager via constructor
- [ ] ShipCombatEngine receives SpatialGrid for queries
- [ ] Ship creates/owns ShipCombatEngine instance
- [ ] Ensure no circular dependencies

### Unit Tests
- [ ] Create `tests/unit/simulation/test_ship_combat_engine.py`
- [ ] Test fire_weapons() with various weapon types
- [ ] Test target selection logic
- [ ] Test damage application
- [ ] Test projectile creation
- [ ] Test with mock Ship and ProjectileManager

### Integration Tests
- [ ] Existing ship combat tests still pass
- [ ] Battle engine tests still pass
- [ ] AI controller tests still pass

## Verification
- [ ] Ship class reduced by ~100 lines
- [ ] ShipCombatEngine < 200 lines
- [ ] All combat-related tests pass
- [ ] No functionality regression
