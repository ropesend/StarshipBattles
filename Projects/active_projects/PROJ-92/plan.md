# PROJ-92: Clean Up Residual Circular Dependency Artifacts

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-92` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-92 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Move HexCoord to core | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Delete no-op TYPE_CHECKING blocks | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Update documentation & audit | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-02-10
**Active Phase:** Plan Approved — Ready for Implementation
**Last Action:** Plan created, reviewed, and approved by user
**Next Action:** Begin Phase 1, Task 1.1 — copy hex_math.py to game/core/ and create re-export shim
**Blockers:** None
**Context for Next Agent:** This is a pure mechanical refactor. No behavioral changes. The re-export shim pattern (Task 1.1) ensures tests pass at every step. All import updates are simple find-and-replace of `game.strategy.data.hex_math` → `game.core.hex_math`. Baseline: 7616 tests passing.

## Overview
A code review identified residual circular dependency artifacts left over from PROJ-90. Three issues remain:
1. **6 vestigial `if TYPE_CHECKING: pass` blocks** — dead code from removed imports
2. **`game/core/protocols.py` imports from `game/strategy/data/hex_math`** — core→strategy layer violation
3. **HexCoord is a pure math utility with zero strategy dependencies** — belongs in core

This project moves `hex_math.py` to `game/core/`, updates all 156 import sites (32 production + 124 test files), deletes the 6 dead TYPE_CHECKING blocks, and updates documentation.

## Goals
- Eliminate the core→strategy layer violation in `protocols.py`
- Remove 6 dead `if TYPE_CHECKING: pass` blocks
- Place `hex_math.py` in the architecturally correct layer (core)
- Leave zero references to `game.strategy.data.hex_math`

## Scope
**In:**
- Move `hex_math.py` from `game/strategy/data/` to `game/core/`
- Update all 32 production imports in `game/`
- Update all 124 test file imports in `tests/`
- Update `game/strategy/__init__.py` re-export
- Delete 6 no-op `if TYPE_CHECKING: pass` blocks + unused TYPE_CHECKING imports
- Update `docs/architecture/ARCHITECTURE.md`

**Out:**
- Refactoring other circular dependencies (remaining late imports in ship.py/ship_instance.py are documented and acceptable)
- Changing any runtime behavior
- Adding new tests (pure mechanical refactor)

## Key Files
| Component | File Path |
|-----------|-----------|
| HexCoord source (move FROM) | `game/strategy/data/hex_math.py` |
| HexCoord target (move TO) | `game/core/hex_math.py` |
| Layer violation | `game/core/protocols.py:39-40` |
| Strategy re-export | `game/strategy/__init__.py:35` |
| No-op block 1 | `game/ui/services/component_service.py:18-19` |
| No-op block 2 | `game/ui/services/vehicle_class_service.py:20-21` |
| No-op block 3 | `game/strategy/services/fleet_navigation_service.py:63-64` |
| No-op block 4 | `game/strategy/engine/fleet_order_processor.py:23-24` |
| No-op block 5 | `game/strategy/engine/maintenance_engine.py:23-24` |
| No-op block 6 | `game/strategy/engine/production_engine.py:30-31` |

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-10 | Move entire hex_math.py to core (not just HexCoord class) | Module is self-contained (only depends on stdlib `math`), all functions are pure utilities |
| 2026-02-10 | Use temporary re-export shim during migration | Ensures tests pass at every intermediate step |
| 2026-02-10 | Delete shim after all imports updated | Per CLAUDE.md: "eradicate the old system completely", no backward compat layers |
| 2026-02-10 | Skip Phase B swarm (6-8 agents) | Prior review already thoroughly analyzed architecture, dependencies, and test impact |

## Initial Analysis
### From Review (2026-02-10)
- **131 files** have TYPE_CHECKING blocks — this is healthy and standard Python
- **6 files** have vestigial `if TYPE_CHECKING: pass` — dead code
- **1 layer violation**: `core/protocols.py` → `strategy/data/hex_math` (TYPE_CHECKING-only)
- **hex_math.py** is 250 lines, depends only on `math` stdlib — perfect candidate for core
- **32 production files** + **124 test files** import from `game.strategy.data.hex_math`
- `game/strategy/__init__.py` re-exports `HexCoord` from `hex_math`
- Original PROJ-90 already fixed: ShipCombatEngine late import, no-op TYPE_CHECKING in ship.py, added IPostBattleShip protocol

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

---

## Phases

### Phase 1: Move HexCoord to core and update all imports [Medium]
**Objective:** Move `hex_math.py` to `game/core/`, update all import sites, leave a re-export shim at the old location for safety, then delete the shim.
**Status:** Not Started

#### Task 1.1: Move hex_math.py to game/core/ [Simple]
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

#### Task 1.2: Update production code imports (32 files) [Simple]
**File:** All files under `game/` importing from `game.strategy.data.hex_math`
**Tests:** `pytest tests/ -n 12 -q`
- [ ] Find-and-replace `from game.strategy.data.hex_math import` → `from game.core.hex_math import` in all 32 files:
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

#### Task 1.3: Update test imports (124 files) [Simple]
**File:** All files under `tests/` importing from `game.strategy.data.hex_math`
**Tests:** `pytest tests/ -n 12 -q`
- [ ] Find-and-replace `from game.strategy.data.hex_math import` → `from game.core.hex_math import` in all 124 test files
- [ ] Run `pytest tests/ -n 12 -q` — all 7616 tests pass
**Notes:**

#### Task 1.4: Delete the re-export shim [Simple]
**File:** `game/strategy/data/hex_math.py`
**Tests:** `pytest tests/ -n 12 -q`
- [ ] Delete `game/strategy/data/hex_math.py` entirely
- [ ] Verify: `grep -r "strategy.data.hex_math" game/ tests/` returns 0 results
- [ ] Run `pytest tests/ -n 12 -q` — all 7616 tests pass
**Notes:**

---

### Phase 2: Delete no-op TYPE_CHECKING blocks [Simple]
**Objective:** Remove 6 vestigial `if TYPE_CHECKING: pass` blocks and clean up unused `TYPE_CHECKING` imports.
**Status:** Not Started

#### Task 2.1: Clean up 6 files [Simple]
**Tests:** `pytest tests/ -n 12 -q`

**File 1:** `game/ui/services/component_service.py`
- [ ] Remove lines 18-19: `if TYPE_CHECKING:\n    pass`
- [ ] Remove `TYPE_CHECKING` from line 13: `from typing import Any, Dict, List, Optional, TYPE_CHECKING` → `from typing import Any, Dict, List, Optional`

**File 2:** `game/ui/services/vehicle_class_service.py`
- [ ] Remove lines 20-21: `if TYPE_CHECKING:\n    pass`
- [ ] Remove `TYPE_CHECKING` from line 16: `from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING` → `from typing import Any, Dict, List, Optional, Tuple`

**File 3:** `game/strategy/services/fleet_navigation_service.py`
- [ ] Remove lines 63-64: `if TYPE_CHECKING:\n    pass`
- [ ] Remove `TYPE_CHECKING` from line 56: `from typing import Optional, TYPE_CHECKING` → `from typing import Optional`

**File 4:** `game/strategy/engine/fleet_order_processor.py`
- [ ] Remove lines 23-24: `if TYPE_CHECKING:\n    pass`
- [ ] Remove `TYPE_CHECKING` from line 16: `from typing import Optional, List, Tuple, Dict, Any, TYPE_CHECKING` → `from typing import Optional, List, Tuple, Dict, Any`

**File 5:** `game/strategy/engine/maintenance_engine.py`
- [ ] Remove lines 23-24: `if TYPE_CHECKING:\n    pass`
- [ ] Remove `TYPE_CHECKING` from line 19: `from typing import List, Dict, TYPE_CHECKING` → `from typing import List, Dict`

**File 6:** `game/strategy/engine/production_engine.py`
- [ ] Remove lines 30-31: `if TYPE_CHECKING:\n    pass`
- [ ] Remove `TYPE_CHECKING` from line 20: `from typing import Optional, List, Dict, Any, TYPE_CHECKING` → `from typing import Optional, List, Dict, Any`

- [ ] Run `pytest tests/ -n 12 -q` — all 7616 tests pass
**Notes:**

---

### Phase 3: Update documentation & audit [Simple]
**Objective:** Update architecture docs and run final verification.
**Status:** Not Started

#### Task 3.1: Update ARCHITECTURE.md [Simple]
**File:** `docs/architecture/ARCHITECTURE.md`
- [ ] Update any references to `hex_math` living in strategy to reflect its new core location
- [ ] Note in "Intentional Late Imports" section that the `core/protocols.py → strategy/hex_math` violation is resolved

#### Task 3.2: Final audit [Simple]
- [ ] Run `pytest tests/ -n 12 -q` — full pass
- [ ] Verify `grep -r "strategy.data.hex_math" game/ tests/` returns 0 results
- [ ] Verify no `TYPE_CHECKING` remains in the 6 cleaned files:
  ```
  grep -rn "TYPE_CHECKING" game/ui/services/component_service.py game/ui/services/vehicle_class_service.py game/strategy/services/fleet_navigation_service.py game/strategy/engine/fleet_order_processor.py game/strategy/engine/maintenance_engine.py game/strategy/engine/production_engine.py
  ```
  → 0 results

---

## Verification Checklist

### Project Start (REQUIRED)
- [x] Run full test suite: `pytest tests/ -n 12` — **7616 passed**, 0 failures (baseline)

### After Phase 1
- [ ] All 7616 tests pass
- [ ] `game/strategy/data/hex_math.py` deleted
- [ ] `game/core/hex_math.py` exists with full module
- [ ] `game/core/protocols.py` imports from `game.core.hex_math` (same layer)
- [ ] Zero references to `game.strategy.data.hex_math` remain

### After Phase 2
- [ ] All 7616 tests pass
- [ ] Zero `if TYPE_CHECKING: pass` blocks remain in the 6 listed files

### Final Verification
- [ ] Full test suite: `pytest tests/ -n 12` — all pass
- [ ] No remaining references to old hex_math location
- [ ] Architecture docs updated
- [ ] Audit passed

---

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

## Completion Checklist
- [ ] All Phase 1 tasks checked off
- [ ] All Phase 2 tasks checked off
- [ ] All Phase 3 tasks checked off
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
