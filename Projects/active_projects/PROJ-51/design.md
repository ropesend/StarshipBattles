# PROJ-51: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source Review
- **Review:** [2026-01-30_consistency_naming_verification](../../../Reviews/results/2026-01-30_consistency_naming_verification/)
- **Type:** consistency-verification
- **Date:** 2026-01-30
- **Report:** [View Full Report](../../../Reviews/results/2026-01-30_consistency_naming_verification/report.md)

## Initial Analysis

### Test Baseline
- **Total tests:** 5734 passed, 3 skipped
- **Pre-existing failures:** 46 failed, 12 errors (in `tests/repro_issues/` and UI builder tests)
- **Core tests:** 1245 passed (simulation, integration)

### UI-007 Event Handling Analysis (CLOSED)

**Finding:** The codebase already follows a correct dual convention:
- `process_event()` - Used by pygame_gui UIWindow subclasses (framework convention)
- `handle_event()` - Used by custom Screen classes (project convention)

**Files using `process_event()` (10 files):**
- All inherit from `pygame_gui.elements.UIWindow`
- Examples: `FleetReportWindow`, `DesignSelectorWindow`, `RaceSetupScreen`

**Files using `handle_event()` (32 files):**
- Custom screens, panels, widgets, input handlers
- Examples: `BattleScreen`, `StrategyScreen`, `WorkshopScreen`

**Decision:** This dual convention is intentional architecture. `process_event()` means "pygame_gui manages me", `handle_event()` means "app.py manages me". No changes needed.

## Swarm Findings Summary

### Architecture

**Scene/Screen Naming (UI-006):**
- **File names:** `*_scene.py` (battle_scene.py, strategy_scene.py, test_lab_scene.py)
- **Class names:** `*Screen` (BattleScreen, StrategyScreen, TestLabScreen)
- **Mismatch:** Files named "scene" contain classes named "Screen"

**Additional complexity:**
- `battle_screen.py` already exists - contains `BattleInterface` class
- `strategy_screen.py` already exists - contains `StrategyInterface` class
- Need to rename Interface files before renaming Scene files

**InputHandler Architecture (NCA-007):**
- `InputHandler` in `game/core/input_handler.py` - static class, battle-specific
- Contains `_handle_battle_keydown()` method
- `StrategyInputHandler` in `game/ui/screens/` - instance-based, strategy-specific
- `FormationInputHandler` in `game/ui/screens/formation/` - instance-based

**Validation Architecture (NCA-008):**
- `game/simulation/validation/` - contains base classes (ValidationRule, etc.)
- `game/simulation/ship_validator.py` - standalone, should be in validation/
- Uses template method pattern with DesignValidationRule, AdditionValidationRule

### Key Patterns to Reuse

- **Input Handler Pattern**: `[Screen]InputHandler` naming convention
  - Example: `StrategyInputHandler` at `game/ui/screens/strategy_input_handler.py`
  - Pattern: Instance-based, takes screen reference in `__init__`

- **Interface/UI Pattern**: `[Screen]Interface` or `[Screen]UI` for UI helpers
  - Example: `BattleInterface` handles UI rendering for `BattleScreen`

- **Validation Pattern**: Template method with base rules
  - Location: `game/simulation/validation/base.py`
  - Classes: `ValidationRule`, `DesignValidationRule`, `AdditionValidationRule`

### Dependencies & Risks

1. **Import Update Volume**
   - `ship_validator.py` imported by 26 files (tests + production)
   - Scene files imported by `game/app.py` + test files
   - Mitigation: Use grep to find all imports, update systematically

2. **File Name Collision (UI-006)**
   - `battle_screen.py` and `strategy_screen.py` already exist
   - Mitigation: First rename `*Interface` classes to `*UI`, then rename files

3. **Circular Import Risk (NCA-007)**
   - Moving InputHandler from `core/` to `ui/screens/` could create issues
   - Mitigation: Test imports after move, check for cycles

### Opportunities Discovered

1. **Consolidate UI helpers**: The `*Interface` -> `*UI` rename creates consistency
2. **Document conventions**: Add comment explaining process_event vs handle_event

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
