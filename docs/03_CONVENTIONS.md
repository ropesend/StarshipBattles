# Conventions

This document defines the naming, coding, file organization, and testing conventions for Starship Battles. Follow these rules when adding or modifying code.

---

## 1. Naming Conventions

### 1.1 Battle vs Combat

These terms are **not interchangeable**. They indicate scope.

| Term | Scope | Examples |
|------|-------|----------|
| **Battle** | Simulation orchestration: full engagements, state, resolution | `BattleEngine`, `BattleService`, `BattleController`, `BattleState`, `BattleResult` |
| **Combat** | Entity-level behavior: per-ship, per-tick mechanics | `ShipCombatEngine`, `CombatPropulsion`, `CombatConstants` |

**Rule:** Creating a system that manages the overall engagement? Use **Battle**. Adding per-ship or per-component behavior? Use **Combat**.

### 1.2 Screen vs Scene

Major game states use **Screen**. Minor/modal states use **Scene**.

| Suffix | Usage | Actual classes |
|--------|-------|----------------|
| **Screen** | Major game states: battle, strategy, workshop, setup | `BattleScreen`, `StrategyScreen`, `DesignWorkshopScreen`, `BuildQueueScreen`, `BattleSetupScreen`, `TestLabScreen`, `FormationEditorScreen`, `NewGameSetupScreen`, `RaceSetupScreen`, `GalaxyTestScreen` |
| **Scene** | Minor overlays: menus, settings | `MenuScene`, `KeybindingsScene` |

- **DO:** Name new major game states with `Screen`.
- **DON'T:** Use `Scene` for anything that occupies the full display as a primary game state.
- **DON'T:** Use `BattleScene` or `StrategyScene` -- these do not exist.

### 1.3 Builder vs Workshop

| Term | Layer | Location |
|------|-------|----------|
| **Builder** | Internal panels (reusable UI components) | `game/ui/screens/builder/` |
| **Workshop** | Top-level screen that composes Builder panels | `game/ui/screens/workshop_*.py` |

Builder panels live in `game/ui/screens/builder/` (e.g., `left_panel.py`, `right_panel.py`, `schematic_view.py`, `detail_panel.py`, `weapons_panel.py`).

Workshop files live directly in `game/ui/screens/` (**not** a `workshop/` subdirectory): `workshop_screen.py` (class: `DesignWorkshopScreen`), `workshop_viewmodel.py`, `workshop_context.py`, `workshop_event_router.py`, `workshop_data_loader.py`, `workshop_data_reloader.py`, `workshop_ship_io.py`.

### 1.4 Star System vs Sector

These terms describe **different spatial granularities** on the galaxy hex map. They are not interchangeable.

| Term | Scope | Data Type | Examples |
|------|-------|-----------|----------|
| **Star system** | A circular region of the galaxy map (radius 50 hexes / 101 hexes across) centered on a star, containing all planets, warp points, and storms within its boundary | `StarSystem` | `galaxy.get_system_at_location()`, `system.name`, `system.global_location` |
| **Sector** | A single hex coordinate on the galaxy map — the smallest addressable location | `HexCoord` | `fleet.location`, `warp_point.location`, `planet.location` |

**Star system spatial properties:**
- **Center:** `system.global_location` — the origin hex in global galaxy coordinates.
- **Boundary:** Circular, radius 50 hexes from center. Defined by `get_system_at_hex()` in `game/strategy/data/pathfinding.py` (`radius=50`). Any sector within 50 hexes of a system center belongs to that system.
- **Separation:** Systems are placed at least 400 hexes apart (center to center), ensuring no overlap.
- **Contents:** Stars (with their own `radius_hexes` for multi-hex visual footprint), planets (at orbital distances up to ~20 hexes), warp points, and storms — each at a specific sector within the system.
- **Coordinate duality:** Entities within a system store **local** coordinates (offset from system center). Convert to global: `global_hex = system.global_location + entity.location`.

**Key distinctions:**
- A system contains **many sectors**. A star system's hexes include the central star, orbiting planets, and warp points — each at a different sector (hex).
- A system can have **multiple warp points in different sectors**. Validating "fleet is in the right system" is not sufficient when targeting a specific warp point — you must validate the fleet is in the correct **sector**.
- `fleet.location` is always a **sector** (specific hex). `system.global_location` is the system's **origin sector** (center hex).
- When an order targets a specific location (warp point, planet), store the **sector** (`HexCoord`) for execution-time validation, not just the system name.

**Rule:** Use **star system** (or just **system**) when referring to the entire region (e.g., "fleet is in the Alpha system"). Use **sector** when referring to a specific hex coordinate (e.g., "fleet is at the warp point's sector"). When validating fleet position for an order, always validate at **sector** precision.

### 1.5 Handler Naming

Input handlers are prefixed with their screen/context name:

| Class | File |
|-------|------|
| `StrategyInputHandler` | `game/ui/screens/strategy_input_handler.py` |
| `FormationInputHandler` | `game/ui/screens/formation_input_handler.py` |
| `TestLabInputHandler` | `game/ui/screens/test_lab/test_lab_input_handler.py` |
| `WeaponsInputHandler` | `game/ui/screens/builder/weapons_input_handler.py` |

- **DON'T:** Reference `InputHandler` at `game/core/input_handler.py` -- it does not exist.
- **DO:** The core layer has `input_actions.py` (`game/core/input_actions.py`), not an input handler.

### 1.6 MVVM Pattern Files

Complex screens use Model-View-ViewModel:

| Suffix | Purpose | Example |
|--------|---------|---------|
| `*_viewmodel.py` | Screen state, events, business logic (no Pygame) | `workshop_viewmodel.py`, `build_queue_viewmodel.py` |
| `*_context.py` | Shared data context between panels | `workshop_context.py` |
| `*_event_router.py` | Event dispatch between UI components | `workshop_event_router.py`, `strategy_event_router.py` |
| `*_data_loader.py` | Data loading coordination | `workshop_data_loader.py` |

### 1.7 Ability Module Names

All ability modules live in `game/simulation/components/abilities/`:

```
__init__.py       # Registry and public exports
base.py           # Ability base class
cargo.py          # CargoStorage
colonize.py       # ColonizePlanet
crew.py           # CrewCapacity, LifeSupportCapacity, CrewRequired
defense.py        # ShieldProjection, ShieldRegeneration, EmissiveArmor, ToHit*Modifier
harvester.py      # ResourceHarvesterAbility, SpaceShipyardAbility, LocalStorageAbility
markers.py        # VehicleLaunchAbility, CommandAndControl, StructuralIntegrity
propulsion.py     # CombatPropulsion, ManeuveringThruster, StrategicMovement, WarpJump
resources.py      # ResourceConsumption, ResourceStorage, ResourceGeneration (component abilities; see also game/core/resources.py for ResourceCatalog)
stat_keys.py      # StatKey, AbilityStatBinding
planetary.py      # PlanetaryShieldAbility, StrategicResourceGenerationAbility (PROJ-237/238)
superweapons.py   # DestroyPlanet, DestroyStar, OpenWarpPoint, CloseWarpPoint, etc.
ui_colors.py      # HINT_SHIELD_CAP, HINT_DAMAGE, etc. (UI hint color constants)
weapons.py        # WeaponAbility, BeamWeaponAbility, etc.
```

- **DO:** Import abilities from the package, not individual files:
  ```python
  from game.simulation.components.abilities import CombatPropulsion, WeaponAbility
  ```

### 1.8 Order System Names (PROJ-238)

`FleetOrder` was renamed to `Order` to support both fleet and planet orders.
`PlanetOrderType` was merged into the unified `OrderType` enum.

| Old Name | New Name | Notes |
|----------|----------|-------|
| `FleetOrder` | `Order` | `from game.strategy.data.order_types import Order` |
| `PlanetOrderType` | merged into `OrderType` | `ACTIVATE_ABILITY`, `DEACTIVATE_ABILITY` added (generic ability toggles) |
| `FleetOrderProcessor` | `OrderProcessor` | Old module deleted; import from `order_processor.py` |
| `FleetOrderSerializer` | `OrderSerializer` | Old module deleted; import from `order_serializer.py` |
| `FleetOrdersWindow` | `OrdersWindow` | Old module deleted; import from `orders_window.py` |

Old backward compatibility alias modules have been deleted. All code must use
the new names and import paths directly.

---

## 2. File Organization

### 2.1 Layer Structure

| Layer | Path | Dependencies |
|-------|------|-------------|
| **Core** | `game/core/` | None (foundation layer) |
| **Simulation** | `game/simulation/` | Core only (no UI, no Pygame) |
| **Strategy** | `game/strategy/` | Core, Simulation |
| **UI** | `game/ui/` | All layers (top-level) |
| **AI** | `game/ai/` | Simulation, Strategy |
| **Engine** | `game/engine/` | Core (spatial, collision utilities) |

- **DO:** Respect dependency direction. Simulation must never import from UI.
- **DON'T:** Import Pygame in simulation or strategy code.

### 2.2 Where New Files Go

| You are adding... | Put it in... |
|-------------------|-------------|
| A new ship ability | `game/simulation/components/abilities/` (new file or extend existing) |
| A new component modifier | `game/simulation/components/` |
| A new battle system | `game/simulation/systems/` |
| A new strategy system | `game/strategy/systems/` |
| A new UI screen | `game/ui/screens/` |
| A new builder panel | `game/ui/screens/builder/` |
| JSON game data | `data/` (root level, not `game/data/`) |
| Static game data (presets, names) | `game/data/` |

### 2.3 File Size

- **Target:** ~500 lines maximum per file.
- **When to extract:** If a file exceeds 500 lines or has clearly separable responsibilities, extract into a subpackage or sibling module.
- **Subpackage vs flat:** Use a subpackage (directory with `__init__.py`) when there are 3+ closely related files that form a logical unit (e.g., `builder/`, `battle_controller/`). Keep it flat when files are loosely related.

---

## 3. Import Conventions

Imports follow a three-group ordering, separated by blank lines:

```python
# 1. Standard library
import logging
import os
from typing import List, Optional, TYPE_CHECKING

# 2. Third-party
import pygame

# 3. Game modules
from game.core.math import Vector2
from game.core.config import PhysicsConfig, BattleTuning
from game.simulation.entities.ship import Ship
```

Additional rules:
- **DO:** Use `from __future__ import annotations` when needed for forward references.
- **DO:** Use `TYPE_CHECKING` blocks for imports only needed by type checkers:
  ```python
  from typing import TYPE_CHECKING
  if TYPE_CHECKING:
      from game.core.registry import GameRegistries
  ```
- **DON'T:** Use wildcard imports (`from module import *`).
- **DO:** Import abilities from the abilities package, not from individual submodules.

---

## 4. Test Conventions

### 4.1 Directory Mirroring

Test files mirror the source structure:

| Source | Test |
|--------|------|
| `game/simulation/systems/battle_engine.py` | `tests/unit/simulation/systems/` |
| `game/ui/screens/strategy_screen.py` | `tests/unit/ui/screens/test_strategy_screen.py` |
| `game/simulation/components/abilities/defense.py` | `tests/unit/simulation/components/abilities/` |

Test file names: `test_<source_file_name>.py`

### 4.2 conftest.py Hierarchy

The project uses a layered conftest structure:

| File | Scope | Provides |
|------|-------|----------|
| `tests/conftest.py` | Root | `session_registries`, `fresh_registries`, `minimal_registries`, `mock_registries`, `ship_factory`, global ship data loading |
| `tests/unit/conftest.py` | Unit tests | Unit-specific fixtures |
| `tests/unit/<layer>/conftest.py` | Per-layer | Layer-specific fixtures (e.g., `tests/unit/combat/conftest.py`) |
| `tests/integration/<domain>/conftest.py` | Per-domain | Integration scenario fixtures |

- **DO:** Put shared fixtures in the nearest common ancestor conftest.
- **DON'T:** Duplicate fixtures across conftest files.

### 4.3 Fixture Naming

Standard fixture names from root conftest:

| Fixture | Scope | Purpose |
|---------|-------|---------|
| `session_registries` | session | Loaded once, shared across all tests (read-only) |
| `fresh_registries` | function | Deep copy per test for isolation |
| `minimal_registries` | function | Empty registries for pure unit tests |
| `mock_registries` | function | Minimal registries with mock data |
| `ship_factory` | function | Helper to create ships from fresh registries |

### 4.4 Test Commands

```bash
pytest tests/ --testmon              # Incremental (fast, runs only affected tests)
pytest tests/path/to/test.py         # Targeted single file
python scripts/test_sharded.py        # Full suite with sharded parallel runner
pytest tests/ --cov=game -n 12       # Full suite with coverage
```

---

## 5. JSON Data Conventions

### 5.1 Component Data (`data/components.json`)

Components are defined in a top-level `"components"` array. Each entry has:

```json
{
    "id": "bridge",
    "name": "Bridge",
    "type": "Bridge",
    "mass": "=50 * sqrt(ship_class_mass / 1000)",
    "hp": "=200 * sqrt(ship_class_mass / 1000)",
    "allowed_vehicle_types": ["Ship"],
    "sprite_index": 3,
    "abilities": {
        "CommandAndControl": true,
        "CrewRequired": "=ceil(5 * sqrt(ship_class_mass / 1000))"
    },
    "major_classification": "Crewsupport",
    "construction_cost": {
        "metals": 80,
        "organics": 20
    }
}
```

Key rules:
- `id` is the unique component identifier (snake_case).
- `mass` and `hp` can be formulas (prefixed with `=`) or plain numbers.
- `abilities` maps ability class names to `true`, a number, or `{"value": N}` format.
- `allowed_vehicle_types` restricts which vehicle types can equip the component.

### 5.2 Static Game Data

| File | Contents |
|------|----------|
| `game/data/homeworld_presets.json` | Homeworld planet configuration presets |
| `game/data/race_names.json` | Generated race name pools |
| `data/components.json` | All component definitions |

### 5.3 Simulation Test Data

Test-specific data lives in `simulation_tests/data/`:
- `components.json` -- Test-only components (e.g., `TestS_2L` class ships)
- `ships/` -- Test ship JSON definitions
- `schemas/` -- JSON schemas (may be outdated; verify against actual data before use)

---

## 6. Code Quality Rules

### 6.1 Type Hints and Docstrings

- **DO:** Add type hints to all function signatures.
- **DO:** Add docstrings to public APIs.
- **DON'T:** Add docstrings to trivial getters/setters or test functions.
- **PRIORITY (PROJ-255):** Constructors and hot-path methods in engine/controller code must have full annotations. Use `TYPE_CHECKING` imports to avoid circular dependencies.

### 6.2 Function Size and Nesting

- **Target:** Functions under 50 lines.
- **Maximum nesting:** 3 levels. Extract helper functions or use early returns to flatten.

### 6.3 Preferred Patterns

| Prefer | Over |
|--------|------|
| Proper refactor | Quick fix |
| Root cause fix | Workaround |
| Named constants | Magic numbers |
| Specific exceptions | Broad `except` catches |
| Dependency injection | Singletons |
| Extract abstraction | Copy-paste |
| Clean-sheet design | Design compromise |
| Data-driven lookups | Hardcoded type/class name lists |

### 6.4 Error Handling Conventions (PROJ-251)

- **Sub-engines must validate preconditions** before mutating state via `_validate_tick_inputs()`
- **Serialization `from_dict()` methods propagate errors**, not swallow them — corrupt data raises `PersistenceException`
- **`except Exception` in strategy layer** must wrap and re-raise via `EnginePhaseError`, not return `None`
- **Design library** uses `DesignLoadResult` result objects for non-critical file loading (not exceptions)

See `docs/05_ERROR_HANDLING.md` for the full error handling reference.

### 6.5 No Hardcoded Type Lists

**Never hardcode lists of ability names, component types, or class names** to control behavior. Instead, search data structures generically or use registry lookups.

```python
# WRONG — breaks when a new weapon type is added:
_WEAPON_NAMES = ['BeamWeaponAbility', 'ProjectileWeaponAbility', 'SeekerWeaponAbility']
for name in _WEAPON_NAMES:
    if name in abilities: ...

# RIGHT — searches all abilities for the relevant property:
for ab_data in abilities.values():
    if isinstance(ab_data, dict) and 'firing_arc' in ab_data: ...
```

If code needs to distinguish types, use a shared property or protocol — not a list of class name strings.

### 6.5 System Migration

When a new system replaces an old one, **eradicate the old system completely**. Delete old code, update all call sites, remove old data files. No fallback paths, no backward compatibility layers. Save files are disposable -- never write migration code for save data.

---

## 7. Python Style

- **Logging:** `logger = logging.getLogger(__name__)` at module level.
- **Constants:** `ALL_CAPS` for module-level constants.
- **Classes:** `PascalCase`. One primary class per file when the class is substantial.
- **Functions/methods:** `snake_case`.
- **Private members:** Single underscore prefix (`_private_method`).
- **File names:** `snake_case`, matching the primary class (`battle_engine.py` contains `BattleEngine`).
