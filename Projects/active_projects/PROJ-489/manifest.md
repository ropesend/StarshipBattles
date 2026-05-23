# PROJ-489 File Manifest

> Generated during /claude-proj-from-legacy-audit. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Action | Notes |
|------|------|--------|-------|
| `game/simulation/services/modifier_service.py` | Production | Edit | Optional additive changes during Task 1.1 if behavioral reconciliation requires a missing case in the canonical |
| `game/simulation/components/modifier_manager.py` | Production | Edit | Replace inline restriction check at lines 108-117 in `add_modifier()` with delegation to `ModifierService.is_modifier_allowed` |
| `game/ui/services/component_service.py` | Production | Edit | Replace `is_modifier_allowed` body (line 88) with delegation to `ModifierService.is_modifier_allowed` |
| `game/ui/screens/builder/modifier_logic.py` | Production | Edit | Replace 6 method bodies with delegation to `ModifierService`; keep `calculate_snap_value` local |
| `game/ui/screens/workshop_screen.py` | Production | Edit | Inject `ModifierService` reference (Task 1.5) |
| `game/ui/screens/builder/detail_panel.py` | Production | Edit | Inject `ModifierService` reference (Task 1.5) |
| `game/ui/screens/builder/modifier_row.py` | Production | Edit | Inject `ModifierService` reference (Task 1.5) |
| `game/ui/panels/builder_widgets.py` | Production | Edit | Inject `ModifierService` reference (Task 1.5) |
| (associated test files) | Test | Edit | Update construction sites if `ModifierLogicService` constructor signature changes |
