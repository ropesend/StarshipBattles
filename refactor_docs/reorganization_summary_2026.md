# System Reorganization Summary (2026)

## Executive Summary
This document outlines the package-based architecture implemented in the 2026 Refactor (Phases 1-6). The codebase has moved from a flat script structure to a hierarchical `game` package to improve modularity, separation of concerns (Simulation vs View), and testing isolation.

**New Entry Point:** execute `python launcher.py` in the root directory.

---

## Directory Structure

### Root
| Path | Description |
|---|---|
| `launcher.py` | **Entry Point**. Bootstraps the application. |
| `game/` | Primary source code package. |
| `assets/` | (Formerly `Resources/`) Images, themes, audio, fonts. |
| `data/` | JSON definitions (ships, components, strategies). |
| `tests/` | Unified test suite (Unit & Integration). |
| `tools/` | (Formerly `scripts/`) Dev tools and utilities. |

### Game Package (`game/`)
The `game` package is divided into 5 sub-packages:

#### 1. `game.core` (Shared Utilities)
Low-level utilities used across the entire system.
*   `constants.py`: Global constants (screens, colors, physics defaults).
*   `logger.py`: Centralized logging configuration.
*   `profiling.py`: Decorators and utils for performance timing.

#### 2. `game.engine` (Physics & Math)
Game-agnostic engine logic.
*   `physics.py`: Velocity, acceleration, drag calculations.
*   `spatial.py`: Spatial hashing/grid for entity lookups.
*   `collision.py`: Collision detection algorithms (AABB, circle).

#### 3. `game.simulation` (Game Rules & State)
The "Business Logic" of the game. Pure simulation, no UI dependencies.
*   **`components/`**: ECS definitions.
    *   `component.py`: Base `Component` class and Component Registry.
    *   `abilities.py`: Ability System implementations.
    *   `modifiers.py`: Stat modifier logic.
*   **`entities/`**: Game objects.
    *   `ship.py`: The `Ship` class (composition root for components).
    *   `projectile.py`: Projectile logic.
*   **`systems/`**: Managers and Loop Logic.
    *   `battle_engine.py`: The core combat loop/rules referee.
    *   `resource_manager.py`: Global resource handling.
    *   `persistence.py`: (Was `ship_io.py`) Save/Load logic.

#### 4. `game.ai` (Intelligence)
*   `controller.py`: `AIController` state machine.
*   `behaviors.py`: Individual steering behaviors (Seek, Flee, Kite).

#### 5. `game.ui` (Presentation Layer)
Visuals and User Interaction.
*   **`renderer/`**: wrappers for Pygame/Drawing.
    *   `game_renderer.py`: Main render loops.
    *   `camera.py`: Viewport management.
    *   `sprites.py`: Sprite loading and caching.
*   **`screens/`**: High-level game states.
    *   `battle_scene.py`: The RTS combat mode.
    *   `builder_screen.py`: The Ship Editor.
    *   `setup_screen.py`: Match setup/Team selection.
*   **`panels/`**: Specific UI widgets (sidebars, info panels).

---

## Key File Migrations (Cheatsheet)

| Old Location | New Location |
|---|---|
| `main.py` | `game/app.py` |
| `game_constants.py` | `game/core/constants.py` |
| `logger.py` | `game/core/logger.py` |
| `physics.py` | `game/engine/physics.py` |
| `collision_system.py` | `game/engine/collision.py` |
| `components.py` | `game/simulation/components/component.py` |
| `ship.py` | `game/simulation/entities/ship.py` |
| `battle.py` | `game/ui/screens/battle_scene.py` |
| `builder_gui.py` | `game/ui/screens/builder_screen.py` |
| `battle_setup.py` | `game/ui/screens/setup_screen.py` |
| `ship_io.py` | `game/simulation/systems/persistence.py` |
| `ai.py` | `game/ai/controller.py` |

---

## Testing Strategy
Tests are located in `tests/unit/`. The folder structure mirrors `game/` where possible.
*   Legacy `unit_tests/` have been migrated to `tests/unit/`.
*   Tests import via pure python paths (e.g. `from game.simulation.entities.ship import Ship`).
*   **Run command:** `pytest tests/unit/`

## Known "Gotchas" for Future Development
1.  **Imports**: Always use absolute imports from the `game` root (e.g. `import game.core.constants`). usage of `sys.path` modification in app code is discouraged.
2.  **Asset Loading**: `os.chdir()` is NOT guaranteed. Use `game.core.constants.ASSET_DIR` or relative paths from `launcher.py` root.
3.  **UI vs Sim**: Simulation code (layers 1-4) should **NEVER** import from `game.ui`. UI code imports simulation code, not vice-versa.
