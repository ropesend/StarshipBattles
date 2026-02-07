# Naming Conventions

This document defines the intentional naming patterns used throughout the Starship Battles codebase to avoid confusion and maintain consistency.

## Battle vs Combat

These terms have distinct semantic meanings based on scope:

| Term | Scope | Usage | Examples |
|------|-------|-------|----------|
| **Battle** | Simulation-level orchestration | Full battle instances, state management, resolution | `BattleEngine`, `BattleScene`, `BattleService`, `BattleState` |
| **Combat** | Component/system behavior | Individual ship capabilities, per-tick mechanics | `CombatPropulsion`, `ShipCombatMixin`, `CombatConstants` |

### Battle (Simulation Layer)
"Battle" refers to the complete engagement between fleets:
- `BattleEngine` - Core simulation tick loop
- `BattleService` - High-level battle orchestration
- `BattleState` - Snapshot of all ships, seekers, effects
- `BattleScene` - UI screen displaying a battle
- `BattleController` - Manages battle lifecycle
- `BattleResult` - Outcome of a resolved battle
- `IBattleResolver` - Interface for resolving fleet engagements

### Combat (System/Component Level)
"Combat" refers to individual ship or component behavior during battle:
- `CombatPropulsion` - Ability for ship movement in battle
- `ShipCombatMixin` - Per-ship combat calculations
- `ShipCombatEngine` - Ship's individual combat state machine
- `CombatConstants` - Configuration values for combat mechanics
- `RequiresCombatMovement` - Marker ability for movement requirements

### When to Use Which
- Creating a new simulation system that manages the overall battle? Use **Battle**
- Adding a ship ability or per-entity behavior? Use **Combat**
- Interfacing with the strategy layer for fleet resolution? Use **Battle**
- Implementing per-tick mechanics for individual entities? Use **Combat**

## Builder vs Workshop

These terms represent different architectural layers in the ship design UI:

| Term | Layer | Purpose | Location |
|------|-------|---------|----------|
| **Builder** | Reusable UI Panels | Individual visual components | `game/ui/screens/builder/`, `ui/builder/` |
| **Workshop** | Screen Assembly | Composes Builder panels into a screen | `game/ui/screens/workshop_*.py` |

### Builder (UI Panel Components)
"Builder" prefixes reusable UI panel components:
- `game/ui/screens/builder/` - Panel implementations
  - `left_panel.py` - Component selection panel
  - `right_panel.py` - Stats and details panel
  - `schematic_view.py` - Visual ship schematic
  - `detail_panel.py` - Component detail view
  - `weapons_panel.py` - Weapon configuration
- `builder_widgets.py` - Shared widget components
- `builder_utils.py` - Utility functions for builders

### Workshop (Screen-Level Assembly)
"Workshop" prefixes screen-level orchestration:
- `workshop_screen.py` - Main screen that assembles Builder panels
- `workshop_context.py` - Shared state context
- `workshop_viewmodel.py` - Data binding layer
- `workshop_event_router.py` - Event dispatch between panels
- `workshop_data_loader.py` - Data loading coordination

### Architecture Rationale
This separation enables:
1. **Reusability** - Builder panels can be used in other contexts
2. **Testability** - Panels can be unit tested in isolation
3. **Maintainability** - Screen logic separate from panel rendering
4. **Flexibility** - Different screens can compose same panels differently

## Handler Naming

Input handlers are prefixed with their context to avoid class name collisions:

| Class | Context | File |
|-------|---------|------|
| `InputHandler` | Game-level (static methods) | `game/core/input_handler.py` |
| `StrategyInputHandler` | Strategy scene (instance-based) | `game/ui/screens/strategy_input_handler.py` |

### When Adding New Handlers
Prefix with the screen or context name:
- `BattleInputHandler` - For battle scene input
- `WorkshopInputHandler` - For workshop screen input
- etc.

## Scene vs Screen

Both terms appear in the codebase with slightly different connotations:

| Term | Connotation | Examples |
|------|-------------|----------|
| **Scene** | Complex, stateful game state with multiple systems | `BattleScene`, `StrategyScene` |
| **Screen** | UI display, may be simpler or modal | `BuildQueueScreen`, `WorkshopScreen` |

In practice, these are used somewhat interchangeably. New code should prefer:
- **Scene** for major game states with tick loops
- **Screen** for modal or overlay UIs

## Ability Module Structure

Abilities use a package structure rather than a monolithic file:

```
game/simulation/components/abilities/
├── __init__.py       # Registry and exports
├── base.py           # Ability base class
├── resources.py      # ResourceStorage, ResourceConsumption, etc.
├── propulsion.py     # CombatPropulsion, StrategicMovement, etc.
├── defense.py        # ShieldProjection, EmissiveArmor, etc.
├── crew.py           # CrewCapacity, LifeSupportCapacity, etc.
├── markers.py        # VehicleLaunchAbility, CommandAndControl, etc.
├── weapons.py        # WeaponAbility, BeamWeaponAbility, etc.
└── harvester.py      # ResourceHarvesterAbility, SpaceShipyardAbility
```

Import abilities from the package, not individual files:
```python
from game.simulation.components.abilities import CombatPropulsion, WeaponAbility
```

## MVVM Pattern - ViewModel Naming

Complex screens use the MVVM (Model-View-ViewModel) pattern for clean separation of concerns:

| Suffix | Purpose | Example |
|--------|---------|---------|
| `*_viewmodel.py` | Holds screen state, emits events, no pygame code | `workshop_viewmodel.py` |
| `*_context.py` | Shared data context between panels | `workshop_context.py` |
| `*_event_router.py` | Routes events between UI components | `workshop_event_router.py` |
| `*_data_loader.py` | Handles data loading and initialization | `workshop_data_loader.py` |

### ViewModel Conventions

- **File naming:** `{screen_name}_viewmodel.py`
- **Class naming:** `{ScreenName}ViewModel`
- **Example:** `workshop_viewmodel.py` contains `WorkshopViewModel`

### ViewModel Responsibilities

1. **State management** - Holds all screen state (selected items, filters, etc.)
2. **Event emission** - Notifies views when state changes
3. **Business logic** - Validation, transformations, calculations
4. **No pygame code** - Pure Python, easily testable

### When to Create a ViewModel

Use the MVVM pattern when:
- Screen has multiple panels sharing state
- Complex user interactions with state dependencies
- Need to unit test screen logic without pygame
- State changes need to propagate to multiple views

### Example Structure

```
game/ui/screens/workshop/
├── workshop_screen.py       # Main screen (View)
├── workshop_viewmodel.py    # State and logic (ViewModel)
├── workshop_context.py      # Shared context
├── workshop_event_router.py # Event routing
└── workshop_data_loader.py  # Data loading
```

## Related Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) - Layer structure and dependencies
- [UI_STYLE_GUIDE.md](UI_STYLE_GUIDE.md) - UI conventions
