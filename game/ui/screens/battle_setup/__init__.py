"""Battle Setup — fleet-based battle setup UI package.

Structure (PROJ-282):
  - `screen.py` — `FleetBattleSetupScreen` (thin IScene shell)
  - `view_model.py` — `BattleSetupViewModel` (selection + derived view state)
  - `renderer.py` — `BattleSetupRenderer` (orchestrator for panels + bottom bar)
  - `panels/{left,center,right}_panel.py` — per-panel pygame_gui builders
  - `input_handler.py` — `BattleSetupInputHandler` (pygame_gui event dispatch)
  - `controller.py` — `BattleSetupController` (all state mutations, save/load, battle launch)
  - `fleet_hierarchy_editor.py` — `FleetHierarchyEditor` (stateless TF/SQ CRUD + ship cloning)
  - `constants.py` — shared option tables (scope complexes, policies, battle roles)
  - `spec_compiler.py` — `build_manual_battle_spec` (state → BattleSpec; PROJ-269)
"""
from game.ui.screens.battle_setup.screen import FleetBattleSetupScreen

__all__ = ["FleetBattleSetupScreen"]
