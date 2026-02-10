"""
TestLabPanelManager - Widget factory for TestLabScreen panels.

Extracted from TestLabScreen to reduce god class complexity.
Creates ship panels, component panels, results panels, and UI buttons.
"""
import pygame
import pygame_gui
from pygame_gui.elements import UIButton

from game.core.config import DisplayConfig

from .ship_panels import ShipPanel, TabbedShipPanel, ComponentPanel
from .test_run_details import TestRunDetailsPanel
from .results_panel import ResultsPanel

# Module-level height constant (used for panel positioning)
HEIGHT = DisplayConfig.DEFAULT_HEIGHT


class TestLabPanelManager:
    """
    Factory class for creating TestLabScreen panels.

    Extracts panel creation logic from TestLabScreen to improve
    testability and reduce class complexity.
    """

    def __init__(self, data_extractor, test_history, layout: dict):
        """
        Initialize the panel manager.

        Args:
            data_extractor: TestLabDataExtractor for loading component data
            test_history: TestHistory for results panel
            layout: dict with keys: header_height, category_width, test_list_width, metadata_width
        """
        self._data_extractor = data_extractor
        self._test_history = test_history
        self._layout = layout

    def create_ship_panels(self, test_id: str, screen) -> tuple:
        """
        Create ship panels and component panels for the selected test.

        Uses TabbedShipPanel when there are 3+ ships, individual ShipPanels otherwise.

        Args:
            test_id: Test ID (e.g., "BEAM360-001")
            screen: TestLabScreen instance (for _extract_ships_from_scenario callback)

        Returns:
            Tuple of (ship_panels, component_panels, tabbed_ship_panel)
        """
        ship_panels = []
        component_panels = []
        tabbed_ship_panel = None

        # Extract ships from scenario
        ships = screen._extract_ships_from_scenario(test_id)

        if not ships:
            return (ship_panels, component_panels, tabbed_ship_panel)

        # Panel dimensions from layout
        header_height = self._layout['header_height']
        category_width = self._layout['category_width']
        test_list_width = self._layout['test_list_width']
        metadata_width = self._layout['metadata_width']

        base_x = 20 + category_width + 20 + test_list_width + 20 + metadata_width + 20
        panel_width = 540

        # Ship panel (top half) - ~960px tall (100-1060)
        ship_panel_y_start = header_height + 20  # 100px
        ship_panel_height = HEIGHT // 2 - ship_panel_y_start - 20  # Ends at ~1060px with 20px gap

        # Component panel (bottom half) - ~980px tall (1080-2060)
        component_panel_y_start = HEIGHT // 2 + 20  # 1080px (middle + 20px gap)
        component_panel_height = HEIGHT - component_panel_y_start - 100  # ~980px tall

        # Use TabbedShipPanel for 3+ ships
        if len(ships) >= 3:
            # Create single tabbed panel for all ships
            tabbed_width = panel_width * 2 + 20  # Use width of 2 normal panels
            tabbed_ship_panel = TabbedShipPanel(
                x=base_x,
                y=ship_panel_y_start,
                width=tabbed_width,
                height=ship_panel_height,
                ships_info=ships
            )

            # Create single component panel that updates based on selected tab
            # Collect all component IDs from all ships for combined panel
            all_component_ids = []
            for ship_info in ships:
                all_component_ids.extend(ship_info.get('component_ids', []))
            # Remove duplicates while preserving order
            seen = set()
            unique_component_ids = []
            for cid in all_component_ids:
                if cid not in seen:
                    seen.add(cid)
                    unique_component_ids.append(cid)

            component_panel = ComponentPanel(
                x=base_x,
                y=component_panel_y_start,
                width=tabbed_width,
                height=component_panel_height,
                component_ids=unique_component_ids,
                load_component_callback=self._data_extractor.load_component_data
            )
            component_panels.append(component_panel)
        else:
            # Use individual panels for 1-2 ships
            for i, ship_info in enumerate(ships):
                panel_x = base_x + (i * (panel_width + 20))

                # Create ship panel (top)
                ship_panel = ShipPanel(
                    x=panel_x,
                    y=ship_panel_y_start,
                    width=panel_width,
                    height=ship_panel_height,
                    ship_info=ship_info
                )
                ship_panels.append(ship_panel)

                # Create component panel (bottom)
                component_panel = ComponentPanel(
                    x=panel_x,
                    y=component_panel_y_start,
                    width=panel_width,
                    height=component_panel_height,
                    component_ids=ship_info['component_ids'],
                    load_component_callback=self._data_extractor.load_component_data
                )
                component_panels.append(component_panel)

        return (ship_panels, component_panels, tabbed_ship_panel)

    def create_results_panel(
        self,
        test_id: str,
        ship_panels: list,
        tabbed_ship_panel,
        callbacks: dict
    ) -> tuple:
        """
        Create results panel for selected test.

        Positions panel to the right of ship panels, using remaining 4K display space.

        Args:
            test_id: Test ID (e.g., "BEAM360-001")
            ship_panels: List of ShipPanel instances
            tabbed_ship_panel: TabbedShipPanel instance or None
            callbacks: dict with keys: on_view_battle_states, on_use_seed, on_copy_results

        Returns:
            Tuple of (results_panel, test_details_panel)
        """
        header_height = self._layout['header_height']
        category_width = self._layout['category_width']
        test_list_width = self._layout['test_list_width']
        metadata_width = self._layout['metadata_width']

        # Calculate position: after tabbed ship panel, last ship panel, or after Test Details
        if tabbed_ship_panel:
            # Place after tabbed ship panel
            base_x = tabbed_ship_panel.x + tabbed_ship_panel.width + 20
        elif len(ship_panels) > 0:
            # Place after last ship panel
            last_ship_panel = ship_panels[-1]
            base_x = last_ship_panel.x + last_ship_panel.width + 20
        else:
            # No ships, place after Test Details panel
            base_x = 20 + category_width + 20 + test_list_width + 20 + metadata_width + 20

        # Create results panel (600px width)
        results_panel = ResultsPanel(
            x=base_x,
            y=header_height + 20,
            width=600,
            height=HEIGHT - header_height - 120,
            test_history=self._test_history
        )

        # Create test run details panel (to the right of results panel)
        details_x = base_x + 600 + 20
        test_details_panel = TestRunDetailsPanel(
            x=details_x,
            y=header_height + 20,
            width=600,
            height=HEIGHT - header_height - 120
        )

        # Link panels
        results_panel.set_details_panel(test_details_panel)

        # Set up callbacks
        test_details_panel.on_view_states = callbacks.get('on_view_battle_states')
        test_details_panel.on_use_seed = callbacks.get('on_use_seed')
        test_details_panel.on_copy_results = callbacks.get('on_copy_results')

        results_panel.set_test(test_id)

        return (results_panel, test_details_panel)

    def create_ui_buttons(self, ui_manager, on_back_callback) -> tuple:
        """
        Create UI buttons for TestLabScreen.

        Args:
            ui_manager: pygame_gui UIManager
            on_back_callback: Callback for Back button

        Returns:
            Tuple of (btn_back, button_callbacks_dict)
        """
        button_callbacks = {}

        # Back Button (pygame_gui UIButton)
        btn_back = UIButton(
            relative_rect=pygame.Rect(20, 20, 100, 40),
            text="Back",
            manager=ui_manager
        )
        button_callbacks[btn_back] = on_back_callback

        return (btn_back, button_callbacks)
