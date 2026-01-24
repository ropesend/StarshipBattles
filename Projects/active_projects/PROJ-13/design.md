# PROJ-13: Design Document

## Phase 1: Dead Code Cleanup

### Files to Delete
| File | Reason | Issue ID |
|------|--------|----------|
| `game/ui/screens/builder_screen.py` | Deprecated wrapper | DC-002 |
| `Debugging/Marked_for_Deletion_2026-01-20/` | Orphaned debug files | DC-007 |

### Code to Remove
| File | Lines | Reason | Issue ID |
|------|-------|--------|----------|
| `game/core/logger.py` | Line 2 | Unused `import sys` | DC-001 |
| `game/core/logger.py` | Line 38 | Commented console handler | DC-003 |
| `game/simulation/entities/ship_physics.py` | Line 4 | Refactoring artifact comment | DC-004 |
| `game/simulation/components/component.py` | 535-538 | Stub `_apply_custom_stats()` | DC-005 |
| `game/ui/screens/planet_list_window.py` | 779-780 | Duplicate line | DC-008 |

### Migrations Required
| Current | Action | Issue ID |
|---------|--------|----------|
| `BuilderSceneGUI` imports | Migrate to `DesignWorkshopGUI` | DC-002 |
| `PresetManager` in planet_list | Clarify status | DC-012 |

## Phase 2: Constants & Magic Numbers

### New Constants File Structure
```python
# game/core/constants.py additions

# Layer defaults
class LayerDefaults:
    INNER_RADIUS_RATIO = 0.2
    MID_RADIUS_RATIO = 0.5
    OUTER_RADIUS_RATIO = 0.8

# Combat constants
class CombatConstants:
    DEFAULT_MAX_TARGETS = 1
    FIGHTER_LAUNCH_SPEED = 100  # TODO: should be configurable

# UI layout constants (new file: game/ui/layout_config.py)
class LayoutConfig:
    PANEL_PADDING = 5
    BANNER_HEIGHT = 30
    DEFAULT_MARGIN = 10
```

### Files to Update
| File | Magic Numbers | Action |
|------|---------------|--------|
| `game/simulation/entities/ship.py` | 0.2, 0.5, 0.8 layer ratios | Use LayerDefaults |
| `game/simulation/systems/battle_engine.py` | 100 fighter speed | Use CombatConstants |
| `game/ui/screens/strategy_renderer.py` | 60 * i hexagon angle | Extract constant |
| `game/ai/controller.py` | max_targets default 1 | Use CombatConstants |

## Phase 3: Documentation

### Architecture Documentation
Create `docs/ARCHITECTURE.md`:
- Layer overview (Simulation, Strategy, UI, Core)
- Dependency rules
- Key abstractions

### System Documentation
| System | File | Content |
|--------|------|---------|
| Battle Engine | `game/simulation/systems/battle_engine.py` | Battle lifecycle, tick processing |
| Turn Engine | `game/strategy/engine/turn_engine.py` | Turn phases, order processing |
| Component System | `game/simulation/components/component.py` | Component lifecycle, abilities |
| Physics Model | `game/engine/physics.py` | Coordinate system, drag, updates |

### API Documentation
Add docstrings to:
- All public service methods
- All public entity methods
- Complex algorithms (collision, targeting)

## Phase 4: UI Improvements

### EventBus Standardization
- Extend EventBus usage beyond builder
- Create consistent event types
- Document event flow

### Layout Configuration
Create `game/ui/layout_config.py`:
```python
class LayoutConfig:
    """Centralized UI layout configuration."""

    # Panel dimensions
    SIDE_PANEL_WIDTH_RATIO = 0.25
    TOP_PANEL_HEIGHT = 60
    BOTTOM_PANEL_HEIGHT = 100

    # Spacing
    ELEMENT_PADDING = 5
    SECTION_MARGIN = 10

    # Colors (defer to theme system later)
    BACKGROUND_COLOR = (30, 30, 40)
    PANEL_COLOR = (40, 40, 50)
```

### ViewModel Pattern
Document and extend ViewModel pattern from builder:
- Create template ViewModel base class
- Document when to use ViewModels
- Apply to strategy screen (if time permits)

## Phase 5: Remaining Code Quality

### DRY Violations
| Location | Issue | Fix |
|----------|-------|-----|
| `game/ai/controller.py:61-138` | Copy-paste targeting | Extract common methods |
| `game/simulation/entities/ability_aggregator.py` | Duplicate aggregation | Extract common logic |

### Getattr Cleanup
- Audit all `getattr()` with defaults
- Ensure attributes are properly declared
- Add type hints where missing

### Formula System Security
- If not addressed in PROJ-10, add here
- Replace eval() with safe evaluator
- Whitelist allowed functions

### Fleet Order Serialization (STRAT-001)
- Implement fleet order restoration on load
- Two-phase deserialization for cross-references
- Test save/load cycle
