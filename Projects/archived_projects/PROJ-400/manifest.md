# PROJ-400 File Manifest

## Files

| File | Type | Notes |
|------|------|-------|
| game/ui/screens/new_game_setup_screen.py | Production | Replace `self.generate_default_save_name()` at line 348 with the canonical `NewGameSetupController.generate_default_save_name(...)` call. |
| game/ui/screens/new_game_setup_controller.py | Production (read-only) | Source of the canonical static method; not modified, just referenced. |
| tests/unit/ui/screens/test_new_game_setup_screen.py | Test | Add regression that exercises `_create_ui()` widget construction path. (Path may differ — confirm existing module before creating.) |
