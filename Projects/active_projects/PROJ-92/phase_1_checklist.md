# Phase 1: Move HexCoord to core and update all imports

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-92 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Move `hex_math.py` to `game/core/`, update all import sites, delete the old file.

---

## Tasks

### Task 1.1: Move hex_math.py to game/core/ [Simple]
**File:** `game/strategy/data/hex_math.py` → `game/core/hex_math.py`
**Tests:** `pytest tests/unit/strategy/test_hex_math.py`

- [ ] Copy `game/strategy/data/hex_math.py` to `game/core/hex_math.py`
- [ ] Update module docstring: change "strategy layer" references to "core layer"
- [ ] Replace `game/strategy/data/hex_math.py` contents with re-export shim:
  ```python
  """Re-export shim — HexCoord moved to game.core.hex_math (PROJ-92)."""
  from game.core.hex_math import *  # noqa: F401,F403
  from game.core.hex_math import HexCoord, hex_distance, hex_to_pixel, pixel_to_hex, hex_ring, hex_lerp, hex_linedraw, hex_to_dict, hex_from_dict
  ```
- [ ] Run `pytest tests/unit/strategy/test_hex_math.py` — pass via shim

**Notes:**

### Task 1.2: Update production code imports (32 files) [Simple]
**File:** All files under `game/` importing from `game.strategy.data.hex_math`
**Tests:** `pytest tests/ -n 12 -q`

- [ ] Find-and-replace `from game.strategy.data.hex_math import` → `from game.core.hex_math import` in all production files:
  - `game/core/protocols.py` (line 40) — **layer violation fix**
  - `game/strategy/data/fleet.py`
  - `game/strategy/data/galaxy.py`
  - `game/strategy/data/planet.py`
  - `game/strategy/data/stars.py`
  - `game/strategy/data/pathfinding.py`
  - `game/strategy/data/spatial_index.py`
  - `game/strategy/data/physics.py`
  - `game/strategy/data/planet_gen.py`
  - `game/strategy/engine/fleet_order_processor.py`
  - `game/strategy/engine/fleet_movement_engine.py`
  - `game/strategy/engine/command_handlers.py`
  - `game/strategy/services/fleet_navigation_service.py`
  - `game/strategy/services/fleet_speed_calculator.py`
  - `game/strategy/interfaces/engines.py`
  - `game/strategy/facade/strategy_session_facade.py`
  - `game/strategy/facade/dto/fleet_dto.py`
  - `game/strategy/facade/dto/planet_dto.py`
  - `game/strategy/facade/dto/system_dto.py`
  - `game/strategy/generation/placement_strategies.py`
  - `game/strategy/generation/region_classifier.py`
  - `game/strategy/generation/density/density_map.py`
  - `game/strategy/__init__.py` (line 35 — update re-export)
  - `game/ui/screens/strategy_input_handler.py`
  - `game/ui/screens/strategy_event_router.py`
  - `game/ui/screens/strategy_screen.py`
  - `game/ui/screens/strategy_renderer.py`
  - `game/ui/screens/strategy_fleet_ops.py`
  - `game/ui/screens/strategy_colonization.py`
  - `game/ui/screens/strategy_camera_nav.py`
  - `game/ui/screens/build_queue_screen.py`
  - `game/ui/panels/build_queue_controller.py`
  - `game/ui/screens/galaxy_test/system_mode.py`
  - `game/ui/screens/galaxy_test/galaxy_mode.py`
- [ ] Run `pytest tests/ -n 12 -q` — all 7616 tests pass

**Notes:**

### Task 1.3: Update test imports (124 files) [Simple]
**File:** All files under `tests/` importing from `game.strategy.data.hex_math`
**Tests:** `pytest tests/ -n 12 -q`

- [ ] Find-and-replace `from game.strategy.data.hex_math import` → `from game.core.hex_math import` in all 124 test files
- [ ] Run `pytest tests/ -n 12 -q` — all 7616 tests pass

**Notes:**

### Task 1.4: Delete the re-export shim [Simple]
**File:** `game/strategy/data/hex_math.py`
**Tests:** `pytest tests/ -n 12 -q`

- [ ] Delete `game/strategy/data/hex_math.py` entirely
- [ ] Verify: `grep -r "strategy.data.hex_math" game/ tests/` returns 0 results
- [ ] Run `pytest tests/ -n 12 -q` — all 7616 tests pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
