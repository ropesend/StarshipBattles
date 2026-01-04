import pytest
from unittest.mock import MagicMock, patch
import pygame
import pygame_gui

# Mock the entire pygame_gui system before importing the panel
# We rely on sys.modules patching or just mocking the classes used in the file
# Ideally, we import the file after patching.

from game.simulation.entities.ship import Ship
from ui.builder.right_panel import BuilderRightPanel

class TestBug04Display:
    @pytest.fixture
    def mock_builder(self):
        builder = MagicMock()
        builder.ship = MagicMock(spec=Ship)
        builder.ship.name = "Test Ship"
        builder.ship.ship_class = "Frigate"
        builder.ship.layers = {}
        builder.ship.mass_limits_ok = True
        builder.ship.get_missing_requirements.return_value = []
        builder.ship.get_validation_warnings.return_value = []
        builder.ship.ai_strategy = "standard_ranged"
        builder.ship.mass = 1000
        
        # Mock theme manager
        builder.theme_manager = MagicMock()
        builder.theme_manager.get_available_themes.return_value = ["Federation"]
        
        return builder

    @patch('ui.builder.right_panel.UIPanel')
    @patch('ui.builder.right_panel.UILabel')
    @patch('ui.builder.right_panel.UITextEntryLine')
    @patch('ui.builder.right_panel.UIDropDownMenu')
    @patch('ui.builder.right_panel.UITextBox')
    @patch('ui.builder.right_panel.UIImage')
    @patch('ui.builder.right_panel.pygame_gui.elements.UIScrollingContainer')
    @patch('ui.builder.stats_config.get_logistics_rows')
    @patch('ui.builder.stats_config.STATS_CONFIG', new={})
    @patch('ui.builder.right_panel.BuilderRightPanel.update_portrait_image')
    def test_stats_rebuild_leaves_hashes(self, mock_portrait, mock_get_inv, mock_scroll, mock_img, mock_tb, mock_dd, mock_entry, mock_lbl, mock_panel, mock_builder):
        """
        Reproduce BUG-04: When `rebuild_stats` is called (due to new resource keys), 
        the stats display remains at "--" because update is not called.
        """
        # Setup
        manager = MagicMock()
        rect = pygame.Rect(0, 0, 100, 100)
        
        # Mock get_logistics_rows to simulate changing keys
        # Initial state: No resources
        row_mock = MagicMock()
        row_mock.key = "power"  # Pretend we always have power
        mock_get_inv.return_value = [row_mock]
        
        # We also need to patch the STATS_CONFIG import inside setup_stats if it causes issues,
        # but mocking the module function might be enough if setup_stats just calls it.
        # right_panel imports: from ui.builder.stats_config import STATS_CONFIG, get_logistics_rows
        
        # To make sure STATS_CONFIG import works (it might be a dict), we might need to patch it too 
        # or ensure simple import works.
        
        panel = BuilderRightPanel(mock_builder, manager, rect)
            
        # Verify setup called setup_stats -> build_section -> StatRow created
        # We can't easily check StatRow internal state 'value' text without deeper mocking
        # because StatRow creates UILabels.
        
        # However, we can inspect if update_stats_display was called.
        # We can mock update_stats_display on the instance to track calls.
        
        # But we want to test that the *logic* calls it.
        
        # Let's spy on update_stats_display
        with patch.object(panel, 'update_stats_display', wraps=panel.update_stats_display) as spy_update:
            with patch.object(panel, 'rebuild_stats', wraps=panel.rebuild_stats) as spy_rebuild:
                
                # 1. Trigger update with SAME keys (should call update_stats_display directly)
                # mock_get_inv still returns ["power"]
                panel.current_logistics_keys = {"power"}
                # Identity 1: StatRow
                row_mock.definition.get_status.return_value = (True, "")
                row_mock.definition.get_value.return_value = 100
                # Identity 2: Definition
                row_mock.get_status.return_value = (True, "")
                row_mock.get_value.return_value = 100
                row_mock.key = "power"  # Needed for key access
                
                panel.rows_map = {"power": row_mock} # Fake row map
                
                panel.on_ship_updated(mock_builder.ship)
                
                spy_update.assert_called()
                spy_rebuild.assert_not_called()
                
                spy_update.reset_mock()
                spy_rebuild.reset_mock()
                
                # 2. Trigger update with NEW keys (should call rebuild_stats)
                # Change return value
                new_row = MagicMock()
                new_row.key = "fuel"
                # Identity: Definition (only)
                new_row.get_status.return_value = (True, "")
                new_row.get_value.return_value = 50
                
                mock_get_inv.return_value = [row_mock, new_row] # Power + Fuel
                
                # This should trigger rebuild because {"power", "fuel"} != {"power"}
                panel.on_ship_updated(mock_builder.ship)
                
                spy_rebuild.assert_called()
                
                # THE BUG: update_stats_display should be called AFTER rebuild (or inside it)
                # Currently it returns early.
                # Note: setup_stats (called by rebuild) does NOT call update_stats_display.
                # So spy_update should NOT be called if the bug exists.
                
                try:
                    spy_update.assert_called()
                except AssertionError:
                    # This confirms the bug!
                    print("\nCONFIRMED: update_stats_display was NOT called after rebuild_stats.")
                    raise 
                    
        pass
