# Presentation Layer Reorganization Proposal

## 1. Executive Summary
The current codebase mixes "Game Rendering" (drawing logic) and "User Interface" (interaction logic) at the root level. This proposal outlines a plan to unify these into a structured `ui` package, clearly distinguishing between the *Simulation Visualization* (Renderer) and the *Interactive Layer* (GUI).

## 2. Core Concepts
To resolve the ecosystem split, we define two distinct concerns:

### A. Game Rendering (`ui.renderer`)
*   **Responsibility:** Visualizing the simulation state.
*   **Key Traits:** Pure function of game state. Driven by `dt` and `GameState`.
*   **Tech:** Raw `pygame` drawing, sprite blitting, camera transforms, layer sorting.
*   **Examples:** Drawing ships, projectiles, stars, particle effects.

### B. User Interface (`ui.screens`, `ui.panels`)
*   **Responsibility:** Facilitating user interaction and control.
*   **Key Traits:** Event-driven. Manages state transitions (e.g., clicking a button).
*   **Tech:** `pygame_gui`, widget hierarchies, input event handling.
*   **Examples:** Buttons, Sidebars, HUD overlays, Editors.

## 3. Proposed Directory Structure

We propose moving all presentation logic into the `ui/` directory with the following structure:

```text
starship_battles/
├── ui/
│   ├── __init__.py
│   │
│   ├── renderer/               # [NEW] Game Rendering Engine
│   │   ├── __init__.py
│   │   ├── game_renderer.py    # (Refactored rendering.py)
│   │   ├── camera.py           # (Moved from root)
│   │   ├── sprites.py          # (Moved from root)
│   │   └── utils.py            # (Drawing helpers)
│   │
│   ├── screens/                # [NEW] Top-level Game Scenes
│   │   ├── __init__.py
│   │   ├── battle_screen.py    # (Moved battle_ui.py)
│   │   ├── builder_screen.py   # (Moved builder_gui.py)
│   │   └── formation_screen.py # (Moved formation_editor.py)
│   │
│   ├── panels/                 # [NEW] Functional UI Modules
│   │   ├── battle/             # Battle-specific panels
│   │   │   ├── __init__.py
│   │   │   ├── controls.py     # (Extract from battle_panels.py)
│   │   │   └── stats.py        # (Extract from battle_panels.py)
│   │   └── builder/            # (Existing ui/builder/ content)
│   │       ├── detail_panel.py
│   │       ├── layer_panel.py
│   │       └── ...
│   │
│   └── widgets/                # [NEW] Reusable UI Components
│       ├── __init__.py
│       ├── standard.py         # (Moved builder_components.py)
│       └── styles.py           # (Moved ui/colors.py)
```

## 4. Migration Plan

### Phase 1: Relocation
Move root files to their new homes without massive code changes.
1.  `rendering.py` -> `ui/renderer/game_renderer.py`
2.  `camera.py` -> `ui/renderer/camera.py`
3.  `sprites.py` -> `ui/renderer/sprites.py`
4.  `battle_ui.py` -> `ui/screens/battle_screen.py`
5.  `builder_gui.py` -> `ui/screens/builder_screen.py`

### Phase 2: Refactoring `rendering.py`
The current `rendering.py` contains mixed concerns.
*   **Action:** Extract `draw_hud()` and related UI-drawing code.
*   **Destination:** Move HUD logic to a new `ui/panels/battle/hud.py` class using `pygame_gui` or dedicated UI drawing routines, keeping `game_renderer.py` pure.

### Phase 3: Unifying Panels
*   **Action:** Decompose `battle_panels.py` into distinct files within `ui/panels/battle/`.
*   **Action:** Rename `builder_components.py` to `ui/widgets/standard.py` if they are generic, or keep in `ui/panels/builder/` if specific.

### Phase 4: Formation Editor
`formation_editor.py` currently mixes the Data Model (`FormationCore`) with the UI (`FormationEditorScene`).
*   **Action:** Extract `FormationCore` to `ai/formations/formation_core_model.py` (or similar).
*   **Action:** Move `FormationEditorScene` to `ui/screens/formation_screen.py`.

## 5. Implementation Notes

### Imports Update
Moving these files will break imports in `main.py` and across the codebase.
*   *Old:* `from rendering import draw_ship`
*   *New:* `from ui.renderer.game_renderer import draw_ship`

### Graphics Home
We have placed graphics logic in `ui.renderer`.
*   *Alternative:* `engine.visuals` - Rejected to keep "engine" focused on simulation/physics.
*   *Decision:* `ui.renderer` aligns with the "Presentation Layer" concept where the UI package owns all output to the screen.

## 6. Next Steps
1.  Approve this structure.
2.  Create the directory tree.
3.  Execute **Phase 1 (Relocation)** and fix imports.
4.  Verify the game runs.
