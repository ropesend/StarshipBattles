# PROJ-11 Phase 2: Simulation Layer Cleanup

## Phase Overview
Remove all pygame imports from the simulation layer.

## Tasks

### game/simulation/entities/
- [ ] **ship.py**: Replace `pygame.math.Vector2` with `game.core.math.Vector2`
  - [ ] Update import statement
  - [ ] Verify all Vector2 usages work correctly
  - [ ] Run related tests
- [ ] **ship_combat.py**: Replace pygame Vector2
  - [ ] Update import
  - [ ] Test weapon firing and targeting
- [ ] **ship_formation.py**: Replace pygame Vector2
  - [ ] Update import
  - [ ] Test formation calculations
- [ ] **ship_physics.py**: Replace pygame Vector2
  - [ ] Update import
  - [ ] Test physics updates
- [ ] **projectile.py**: Replace pygame Vector2
  - [ ] Update import
  - [ ] Test projectile movement

### game/simulation/systems/
- [ ] **battle_engine.py**: Replace pygame Vector2
  - [ ] Update import
  - [ ] Remove any pygame display dependencies
  - [ ] Test battle execution
- [ ] **persistence.py**: Replace pygame Vector2
  - [ ] Update import
  - [ ] Update save/load to use tuple format
  - [ ] Test save/load cycle
  - [ ] Handle migration of existing saves (if needed)

### game/simulation/
- [ ] **battle_state.py**: Replace pygame Vector2
  - [ ] Update import
  - [ ] Test state serialization
- [ ] **projectile_manager.py**: Replace pygame Vector2
  - [ ] Update import
  - [ ] Test projectile management
- [ ] **ship_theme.py**: Remove any pygame dependencies
  - [ ] Check for pygame imports
  - [ ] Replace if found

### game/engine/
- [ ] **physics.py**: Replace pygame Vector2
  - [ ] Update import
  - [ ] Test PhysicsBody updates
- [ ] **collision.py**: Replace pygame Vector2
  - [ ] Update import
  - [ ] Test collision detection
  - [ ] Test beam attack raycasting
- [ ] **spatial.py**: Replace pygame Vector2
  - [ ] Update import
  - [ ] Test spatial grid operations

### Verification
- [ ] Run: `grep -r "import pygame" game/simulation/` returns nothing
- [ ] Run: `grep -r "import pygame" game/engine/` returns nothing
- [ ] All simulation tests pass
- [ ] Test headless simulation execution (no display)
