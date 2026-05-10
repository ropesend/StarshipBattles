# PROJ-348 File Manifest

## Files

| File | Type | Notes |
|------|------|-------|
| `game/ui/screens/cargo_quick_dialog.py` | Production (refactor) | T5.1 — slider reads move into dialog `_issue_orders`; resolved values dict passed to controller |
| `game/ui/screens/cargo_quick_dialog_controller.py` | Production (refactor) | T5.1 — `issue_orders` accepts resolved values dict, never touches pygame_gui widgets |
| `game/ui/screens/cargo_quick_dialog.py` (Stage 1) | Production (refactor) | T5.2 — gate `scene.facade` access behind bypass |
| `game/ui/screens/planet_list_controller.py` | Production (delete or rewire) | T5.3 — `navigate_to()` decision |
| `game/ui/screens/planet_list_window.py` | Production (refactor) | T5.3 (rewire) and T5.4 — remove `_resolve_demographic_view` `__new__` fallback at lines 687-701 |
| `tests/unit/ui/screens/test_planet_list_window.py` | Tests (rewrite) | T5.4 — replace `__new__` construction with bypass-path construction |
| `tests/unit/ui/screens/test_cargo_quick_dialog*.py` | Tests (add) | T5.1 — assert controller never accesses widgets; characterize new dialog `_issue_orders` contract |
| `Projects/active_projects/PROJ-348/plan.md` | Project artifact | Updates per phase |
| `Projects/projects_index.md` | Project index | Status update at end of Phase 1 |

## Verification commands

| Phase | Command |
|-------|---------|
| 1 | `pytest tests/unit/ui/screens/test_cargo_quick_dialog* tests/unit/ui/screens/test_planet_list_window* -x` then `python Tools/lint_test_files.py` |
