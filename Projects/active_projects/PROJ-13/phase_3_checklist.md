# PROJ-13 Phase 3: Documentation

## Phase Overview
Add critical documentation to core systems.

## Tasks

### Create Architecture Documentation
- [ ] Create `docs/ARCHITECTURE.md`
- [ ] Document layer structure (Simulation, Strategy, UI, Core)
- [ ] Document dependency rules between layers
- [ ] Add simple ASCII diagram
- [ ] Document key design patterns in use

### Document Battle System (DOC-001, DOC-002)
- [ ] Add module docstring to `game/simulation/systems/battle_engine.py`
- [ ] Document battle lifecycle (init → start → tick → end)
- [ ] Document BattleLogger purpose and format
- [ ] Add docstrings to BattleEngine public methods
- [ ] Document collision/hit calculation in `game/engine/collision.py`
- [ ] Explain sigmoid hit chance formula
- [ ] Document sphere-ray intersection math

### Document Strategy Layer (DOC-003)
- [ ] Add module docstring to `game/strategy/engine/turn_engine.py`
- [ ] Document turn phases and order
- [ ] Document order processing lifecycle
- [ ] Add module docstring to `game/strategy/engine/game_session.py`
- [ ] Document command dispatch

### Document Component System (DOC-005)
- [ ] Add module docstring to `game/simulation/components/component.py`
- [ ] Document component lifecycle
- [ ] Document ability system
- [ ] Add module docstring to `game/simulation/entities/ship_stats.py`
- [ ] Document stat calculation phases
- [ ] Add section comments for each phase

### Document AI System (DOC-004)
- [ ] Add module docstring to `game/ai/controller.py`
- [ ] Document behavior selection flowchart
- [ ] Add module docstring to `game/ai/behaviors.py`
- [ ] Document when each behavior is used
- [ ] Document strategy parameter effects

### Document Physics Model (DOC-007)
- [ ] Add module docstring to `game/engine/physics.py`
- [ ] Document coordinate system (origin, axes, angle convention)
- [ ] Document drag model
- [ ] Document update sequence

### Document Resource System (DOC-008)
- [ ] Add module docstring to `game/simulation/systems/resource_manager.py`
- [ ] Document resource lifecycle
- [ ] Document regeneration mechanics
- [ ] Add example usage

### Document Hex Math (DOC-012)
- [ ] Add module docstring to `game/strategy/data/hex_math.py`
- [ ] Document coordinate system (axial, cube, offset?)
- [ ] Document distance calculation
- [ ] Add conversion examples

## Verification
- [ ] All critical systems have module docstrings
- [ ] Architecture document exists
- [ ] Complex algorithms explained
- [ ] New developers can understand system structure
