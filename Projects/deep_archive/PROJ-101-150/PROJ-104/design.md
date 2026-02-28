# PROJ-104: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Problem Statement
Radon cyclomatic complexity analysis identified 6 functions with CC ≥ 40 (the "spaghetti" threshold is typically 15). The codebase average is a healthy A (3.69), but these outliers represent concentrated complexity that hinders maintainability.

### Target Functions
| Function | CC | Lines | Root Cause |
|----------|-----|-------|-----------|
| `BuilderScreen.handle_event` | 111 | 319 | Giant if/elif chain dispatching panel actions, buttons, dropdowns |
| `ShipStatsCalculator.calculate` | 62 | 420 | 5-phase sequential computation with per-ability-type branching |
| `StrategyInputHandler._handle_keydown_mapped` | 50 | 135 | 30+ InputAction elif branches |
| `TargetEvaluator.evaluate` | 49 | 169 | 16 targeting rule types in if/elif chain |
| `TestRunDetailsPanel.draw` | 47 | 283 | 12 drawing sections with nested conditionals |
| `FormationEditorScreen.handle_event` | 45 | 108 | 8 pygame event types with nested button dispatch |

### Refactoring Approach
**Sub-method extraction within the same class.** Each monolithic method is decomposed into focused private helpers (`_handle_*`, `_phase_*`, `_draw_*`, `_eval_*`). The original method becomes a short dispatcher/orchestrator.

This is **not** an architectural change — it's a mechanical decomposition. No new classes, no new files, no API changes.

## Swarm Findings Summary

### Architecture
- All 6 classes are **leaf nodes** — no subclasses override these methods
- No circular import risks — all extraction stays within existing class boundaries
- No `getattr`/`hasattr` targeting internal methods of these classes
- Zero new imports needed

### Key Patterns to Reuse
- **WorkshopEventRouter** (`game/ui/screens/workshop_event_router.py:43-282`): Uses `_handle_panel_action()`, `_handle_button_pressed()`, `_handle_dropdown_changed()`, `_handle_select_component_type()` etc. — the exact pattern we'll follow for BuilderScreen and FormationEditor
- **StrategyInputHandler existing extractions** (`game/ui/screens/strategy_input_handler.py:208-210`): `_take_screenshot_full()` and `_take_screenshot_viewport()` already extracted and successfully mocked by tests
- **FormationEditor existing extractions** (`game/ui/screens/formation_editor.py:631+`): `_handle_left_down()`, `_handle_left_up()`, `_handle_mouse_motion()` already extracted

### Dependencies & Risks
1. **ShipStatsCalculator phase ordering** — Phases 1-5 must execute sequentially (Phase 2 depends on Phase 1 outputs, Phase 3 depends on Phase 2 deactivation, etc.). Mitigation: keep the orchestrating loop in `calculate()`, extract only the body of each phase as a separate method.
2. **TargetEvaluator early termination** — `required` rules return `-float('inf')` mid-loop. Mitigation: extracted rule handlers return `(val, match)` tuples; the main loop handles the early exit logic.
3. **Test patches** — Tests mock `_take_screenshot_full` and `_take_screenshot_viewport` on StrategyInputHandler. Mitigation: these methods stay as-is, no renaming.

### Opportunities Discovered
- The codebase already has a proven extraction pattern (WorkshopEventRouter) that was applied successfully. Following it ensures consistency.
- `ShipStatsCalculator.calculate` already has docstrings documenting the 5 phases — the phase boundaries are well-defined and map cleanly to extracted methods.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
