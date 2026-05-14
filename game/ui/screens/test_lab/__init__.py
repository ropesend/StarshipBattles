"""
test_lab package - Combat Lab UI components

This package contains the decomposed Combat Lab UI for viewing and running
test scenarios. The original monolithic test_lab_screen.py has been split
into focused modules for better maintainability.

Modules:
    screen.py           - TestLabScreen main orchestrator class
    data_extractor.py   - TestLabDataExtractor for loading ships/components
    dialogs.py          - JSONPopup and ConfirmationDialog
    component_dropdown.py - ComponentDropdown for component selection
    ship_panels.py      - ShipPanel, TabbedShipPanel, ComponentPanel
    test_run_card.py    - TestRunCard for test history display
    details/            - TestRunDetailsPanel for detailed results (subpackage)
    results_panel.py    - ResultsPanel for test run history
"""

from .screen import TestLabScreen
from .data_extractor import TestLabDataExtractor, get_test_data_dir

__all__ = ['TestLabScreen', 'TestLabDataExtractor', 'get_test_data_dir']
