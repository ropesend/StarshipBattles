# PROJ-388 File Manifest

## Files

| File | Type | Action | Notes |
|------|------|--------|-------|
| `game/ui/screens/builder/modifier_logic.py` | Production | Edit | LEG-03-009 + LEG-03-015 — delete the entire `ModifierLogic` class starting line 177 |
| `game/ui/panels/modifier_editor_panel.py` | Production | Migrate-callers | Migrate `_build_panels` to `ModifierLogicService` via constructor injection |
| (additional consumers found via Task 1.1 grep) | Production | Migrate-callers | Same |
