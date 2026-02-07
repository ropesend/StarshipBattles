# test_lab Package

Combat Lab UI components for viewing and running test scenarios.

## Purpose

This package provides the Combat Lab screen where users can:
- Browse and select test scenarios
- View ship configurations and component data
- Run tests (headless or visual mode)
- Inspect detailed test results and battle outcomes

## Package Structure

| Module | Lines | Classes | Description |
|--------|-------|---------|-------------|
| `__init__.py` | ~20 | - | Package exports (TestLabScreen) |
| `screen.py` | ~2460 | TestLabScreen | Main orchestrator, screen lifecycle |
| `dialogs.py` | ~250 | JSONPopup, ConfirmationDialog | Modal dialog components |
| `json_viewer.py` | ~110 | ScrollableJSONViewer | Scrollable JSON display widget |
| `component_dropdown.py` | ~140 | ComponentDropdown | Component selection dropdown |
| `ship_panels.py` | ~240 | ShipPanel, TabbedShipPanel, ComponentPanel | Ship/component display panels |
| `test_run_card.py` | ~370 | TestRunCard | Individual test run history card |
| `test_run_details.py` | ~830 | TestRunDetailsPanel | Detailed results for selected test |
| `results_panel.py` | ~245 | ResultsPanel | Test run history list |

## Internal Dependencies

```
screen.py (orchestrator)
    |
    +-- dialogs.py (JSONPopup, ConfirmationDialog)
    |       |
    |       +-- json_viewer.py (ScrollableJSONViewer)
    |
    +-- component_dropdown.py (ComponentDropdown)
    |
    +-- ship_panels.py (ShipPanel, TabbedShipPanel, ComponentPanel)
    |
    +-- results_panel.py (ResultsPanel)
            |
            +-- test_run_card.py (TestRunCard)
            |
            +-- test_run_details.py (TestRunDetailsPanel)
```

## Usage

```python
# Import from package (recommended)
from game.ui.screens.test_lab import TestLabScreen

# Or import specific components
from game.ui.screens.test_lab.dialogs import JSONPopup
from game.ui.screens.test_lab.ship_panels import ShipPanel
```

## Adding New Components

1. Create a new module in this package (e.g., `new_widget.py`)
2. Import dependencies from other modules in the package
3. Update `screen.py` to use your new component
4. If the component should be publicly exported, add it to `__init__.py`

## Testing

Related test files:
- `tests/unit/test_lab/` - Data path and visual run tests
- `tests/unit/ui/test_lab_scene/` - UI component unit tests

Run tests:
```bash
pytest tests/unit/test_lab/ -v
pytest tests/unit/ui/test_lab_scene/ -v
```

## Notes for AI Agents

- **screen.py** is the orchestrator (~2460 lines) - future refactoring target
- All widget classes are self-contained with clear boundaries
- Follow existing patterns when adding new panels/widgets
- Keep modules focused - extract to new file if >400 lines
- Use type hints for all public methods
