# Phase 9 Audit: LayerType Import Locations

**Date:** 2026-01-28

## Summary

LayerType is canonically defined in `game/core/constants.py` (lines 82-93).
The `game/simulation/components/component_constants.py` file re-exports it for backward compatibility (lines 17-19).

## Canonical Definition

**File:** `game/core/constants.py:82-93`
```python
class LayerType(Enum):
    """Ship layer zones for component placement and damage distribution."""
    HULL = 0
    CORE = 1
    INNER = 2
    OUTER = 3
    ARMOR = 4

    @staticmethod
    def from_string(s):
        return getattr(LayerType, s.upper())
```

## Re-export (Backward Compatibility)

**File:** `game/simulation/components/component_constants.py:17-19`
```python
# Re-export LayerType from core for backward compatibility
# PROJ-17: LayerType moved to game/core/constants.py for proper layer architecture
from game.core.constants import LayerType
```

## Files Using Canonical Location (CORRECT - No changes needed)

| File | Line | Import Statement |
|------|------|-----------------|
| game/ui/renderer/renderer.py | 8 | `from game.core.constants import LayerType` |
| game/ui/renderer/game_renderer.py | 9 | `from game.core.constants import LayerType, LayerDefaults` |
| game/ui/panels/design_report_panel.py | 18 | `from game.core.constants import LayerType` |
| game/ui/hud/panels.py | 16 | `from game.core.constants import LayerType` |
| game/ui/services/validation_service.py | 17 | `from game.core.constants import LayerType` |
| game/ui/screens/builder/component_ref.py | 31 | `from game.core.constants import LayerType` |
| game/ui/screens/builder/detail_panel.py | 13 | `from game.core.constants import LayerType` |
| game/ui/panels/ship_detail_panel.py | 18 | `from game.core.constants import LayerType` |
| game/ui/screens/builder/layer_panel.py | 11 | `from game.core.constants import LayerType` |
| game/ui/panels/ship_stats_renderer.py | 14 | `from game.core.constants import CombatConstants, LayerType` |
| game/ui/screens/builder/main.py | 27 | `from game.core.constants import LayerType` |
| game/ui/screens/builder/right_panel.py | 510 | `from game.core.constants import LayerType` |
| game/ui/screens/builder/schematic_view.py | 9 | `from game.core.constants import LayerType` |
| game/ui/screens/builder/stats_config.py | 9 | `from game.core.constants import LayerType` |
| game/ui/screens/workshop_event_router.py | 19 | `from game.core.constants import LayerType` |
| game/ui/screens/workshop_screen.py | 16 | `from game.core.constants import LayerType` |

## Files Using Deprecated Location (NEEDS UPDATE)

### AI Layer (AR-013 - Cross-layer violation)

| File | Line | Current Import |
|------|------|----------------|
| game/ai/target_evaluator.py | 7 | `from game.simulation.components.component_constants import LayerType` |

### Simulation Layer (Internal - OK to use re-export, but better to use canonical)

| File | Line | Current Import |
|------|------|----------------|
| game/simulation/designs.py | 3 | `from game.simulation.components.component_constants import LayerType` |
| game/simulation/validation/base.py | 18 | `from game.simulation.components.component_constants import LayerType` |
| game/simulation/entities/ship_stats.py | 52 | `from game.simulation.components.component_constants import ComponentStatus, LayerType` |
| game/simulation/entities/ship_serialization.py | 10 | `from game.simulation.components.component_constants import LayerType` |
| game/simulation/entities/ship_combat_engine.py | 19 | `from game.simulation.components.component_constants import LayerType, ComponentStatus` |
| game/simulation/entities/ship.py | 8 | `from game.simulation.components.component_constants import LayerType` |
| game/simulation/entities/ship_component_manager.py | 17 | `from game.simulation.components.component_constants import LayerType` |
| game/simulation/battle_state.py | 18 | `from game.simulation.components.component_constants import LayerType` |
| game/simulation/ship_validator.py | 11 | `from game.simulation.components.component_constants import LayerType` |
| game/simulation/systems/stats.py | 3 | `from game.simulation.components.component_constants import LayerType` |
| game/simulation/services/vehicle_design_service.py | 13 | `from game.simulation.components.component_constants import LayerType` |
| game/simulation/systems/validator.py | 11 | `from game.simulation.components.component_constants import LayerType` |

### UI Files with Incorrect Imports (imports from ship.py)

| File | Line | Current Import | Issue |
|------|------|----------------|-------|
| game/ui/screens/builder/left_panel.py | 259 | `from game.simulation.entities.ship import LayerType` | ship.py imports from component_constants |
| game/ui/screens/builder/stats_config.py | 126 | `from game.simulation.entities.ship import LayerType` | Local re-import, already has module-level import |
| game/ui/screens/workshop_viewmodel.py | 22 | `from game.simulation.entities.ship import Ship, LayerType` | Should import LayerType from core |

## Action Plan

1. **Task 9.2:** LayerType is already in canonical location - VERIFIED
2. **Task 9.3:** Update 12 simulation files to use `game.core.constants`
3. **Task 9.4:** Update 1 AI file (`target_evaluator.py`) to use `game.core.constants` - AR-013 fix
4. **Task 9.5:** Fix 3 UI files with incorrect local imports
5. **Task 9.6:** No strategy files found importing LayerType
6. **Task 9.7:** component_constants.py already has deprecation re-export
7. **Task 9.8:** Verify both imports resolve to same enum

## Notes

- The re-export in `component_constants.py` is already properly documented
- Most UI files already use canonical location (done in previous projects)
- Simulation layer files consistently use the deprecated path
- The `ship.py` file doesn't define LayerType, it imports from component_constants
