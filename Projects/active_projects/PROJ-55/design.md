# PROJ-55: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### The Problem
`game/ui/screens/test_lab_screen.py` is 4,703 lines with 11 classes and 1 module-level utility function. It is the single largest file in the project (201 KB). All classes are crammed into one module making it impossible to edit one widget without loading the entire file.

### Current File Structure
| Class | Lines | Size | Role |
|-------|-------|------|------|
| `JSONPopup` | 36-139 | ~100 | Modal popup for displaying JSON data |
| `ConfirmationDialog` | 141-289 | ~150 | Confirmation dialog with visual diff |
| `ScrollableJSONViewer` | 291-402 | ~110 | Reusable scrollable JSON panel |
| `ComponentDropdown` | 404-547 | ~140 | Custom dropdown menu for components |
| `ShipPanel` | 549-588 | ~40 | Single ship JSON display panel |
| `TabbedShipPanel` | 590-719 | ~130 | Tabbed multi-ship panel |
| `ComponentPanel` | 721-792 | ~70 | Component dropdown + JSON viewer |
| `TestRunCard` | 794-1165 | ~370 | Test run summary card widget |
| `TestRunDetailsPanel` | 1167-1998 | ~830 | Detailed test results view |
| `ResultsPanel` | 2000-2245 | ~245 | Scrollable test run history |
| `TestLabScreen` | 2247-4703 | ~2460 | Main orchestrator screen |

Module-level: `get_test_data_dir()` (lines 19-33), `logger` (line 16)

### Legacy File
`game/ui/screens/test_lab.py` (189 lines) is a dead legacy implementation from before PROJ-46 naming standardization. Zero imports found anywhere. Safe to delete.

## Swarm Findings Summary

### Architecture
- **No inheritance** between classes — pure composition pattern
- **No circular dependencies** — clean unidirectional tree
- **Event-driven** — callbacks passed as function parameters (e.g., `on_confirm`, `on_cancel`, `load_callback`)
- **Lazy imports** in TestLabScreen for heavy deps (BattleStateViewer, Validator, tkinter)
- **Central controller** — TestLabUIController manages UI state (external to this file)

### Internal Dependency Graph
```
screen.py ──> dialogs.py (leaf)
          ──> ship_panels.py ──> json_viewer.py (leaf)
          |                  ──> component_dropdown.py (leaf)
          ──> results_panel.py ──> test_run_card.py (leaf)
          ──> test_run_details.py (leaf)
```
5 of 8 modules are leaf nodes (no intra-package dependencies).

### Key Patterns to Reuse
- **Builder package `__init__.py`**: `game/ui/screens/builder/__init__.py` — re-exports key classes using relative imports
- **Formation package `__init__.py`**: `game/ui/screens/formation/__init__.py` — includes docstring, `__all__`, uses absolute imports

### Dependencies & Risks

1. **`get_test_data_dir()` path depth change** — Uses `os.path.dirname(__file__)` with 3 levels of `dirname()`. Moving from `game/ui/screens/` to `game/ui/screens/test_lab/` requires 4 levels. **Mitigation:** Fix in Task 3.1, test thoroughly.

2. **18 `patch()` calls in test files** — All reference `game.ui.screens.test_lab_screen.XXX`. Must update to `game.ui.screens.test_lab.screen.XXX`. **Mitigation:** Exact line numbers mapped.

3. **Patch targets are module-level names** — Tests patch `load_json`, `TestRunner`, `JSONPopup`, `WIDTH`, `HEIGHT` as they're imported into `test_lab_screen`. After decomposition, these names will be imported into `screen.py`, so patches must target `game.ui.screens.test_lab.screen.*`.

### External Import Surface
| Consumer | Import | Lines |
|----------|--------|-------|
| `game/app.py` | `from game.ui.screens.test_lab_screen import TestLabScreen` | 30 |
| `tests/unit/test_lab/test_data_paths.py` | `from game.ui.screens.test_lab_screen import TestLabScreen` | 47, 134, 180, 219 |
| `tests/unit/test_lab/test_data_paths.py` | `from game.ui.screens.test_lab_screen import get_test_data_dir` | 255, 274 |
| `tests/unit/test_lab/test_visual_run.py` | `from game.ui.screens.test_lab_screen import TestLabScreen` | 78 |

No references in `game/ui/__init__.py`, `game/ui/screens/__init__.py`, conftest files, or config files.

### Opportunities Discovered
- `TestLabScreen` at 2460 lines could itself be decomposed in a future project (extract draw methods, test execution logic, event handling)
- Several classes create fonts independently — could share a font cache (out of scope)

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
