"""Race Setup — race configuration wizard UI package.

PROJ-309 Sub-phase 3.1: extracted from `race_setup_screen.py` (1598 LOC)
into the PROJ-282 MVVM shape. Module roles:

  - `screen.py` — `RaceSetupScreen` (thin pygame_gui.UIWindow shell).
  - `controller.py` — `RaceSetupController` (race_config mutation,
    save/load flow, validation, randomization dispatch).
  - `view_model.py` — `RaceSetupViewModel` (tab state, nav rules,
    LLM threshold counters).
  - `renderer.py` — `RaceSetupRenderer` (FEAT-05 + PROJ-299 modal
    construction).
  - `ship_preview.py` — `ShipPreviewBuilder` (Ships-tab 3x3 image grid).
  - `input_handler.py` — `RaceSetupInputHandler` (pygame_gui event
    dispatch).
  - `llm_dialog_service.py` — `LLMDialogService` (PROJ-299 30s/90s
    threshold checks + error mapper).
  - `panel_factory.py` — per-tab content factories (delegate to the
    extracted panel/gallery classes in `game/ui/panels/`).

The legacy import path `game.ui.screens.race_setup_screen` remains valid
via a re-export shim — see `race_setup_screen.py`.
"""
from game.ui.screens.race_setup.screen import RaceSetupScreen

__all__ = ["RaceSetupScreen"]
