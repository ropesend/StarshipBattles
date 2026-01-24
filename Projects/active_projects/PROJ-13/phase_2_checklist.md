# PROJ-13 Phase 2: Constants & Magic Numbers

## Phase Overview
Extract magic numbers to configuration constants.

## Tasks

### Create/Update Constants Infrastructure
- [ ] Review existing `game/core/constants.py`
- [ ] Add LayerDefaults class for layer radius ratios
- [ ] Add CombatConstants class for combat values
- [ ] Add PhysicsConstants class for physics values
- [ ] Document each constant with units and acceptable ranges

### Extract Layer Defaults (CQ-009)
- [ ] Find all layer radius magic numbers (0.2, 0.5, 0.8)
- [ ] Replace with LayerDefaults.INNER_RADIUS_RATIO etc.
- [ ] Update `game/simulation/entities/ship.py`
- [ ] Run tests

### Extract Combat Constants
- [ ] Find fighter launch speed (100)
- [ ] Replace with CombatConstants.FIGHTER_LAUNCH_SPEED
- [ ] Update `game/simulation/systems/battle_engine.py`
- [ ] Find max_targets default (1)
- [ ] Replace with CombatConstants.DEFAULT_MAX_TARGETS
- [ ] Update all locations using default

### Extract Physics Constants
- [ ] Review `game/engine/physics.py` for magic numbers
- [ ] Review `game/simulation/physics_constants.py` (may already exist)
- [ ] Consolidate if needed
- [ ] Document all physics constants

### Create UI Layout Config
- [ ] Create `game/ui/layout_config.py`
- [ ] Define LayoutConfig class
- [ ] Extract panel padding values
- [ ] Extract margin values
- [ ] Document all layout constants

### Update UI Files
- [ ] Find magic pixel values in strategy_screen.py
- [ ] Find magic pixel values in battle_panels.py
- [ ] Replace with LayoutConfig constants where practical
- [ ] Note: Full extraction may be deferred to future

### Address CQ-022: Duplicated Default Values
- [ ] Find all duplicated default values
- [ ] Create single source of truth
- [ ] Update all references
- [ ] Run tests

## Verification
- [ ] Magic numbers in core files replaced
- [ ] Constants documented with units
- [ ] All tests pass
- [ ] Code more readable and maintainable
