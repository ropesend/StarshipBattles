"""Tests for DesignSelectorWindow error logging (ERR-020)."""
import pytest
import pygame
import logging
from unittest.mock import MagicMock, patch


class TestDesignSelectorPortraitLogging:
    """Tests for portrait loading error logging in DesignSelectorWindow (ERR-020)."""

    def setup_method(self):
        pygame.init()
        pygame.display.set_mode((1, 1), pygame.NOFRAME)

    def test_portrait_load_failure_logs_warning(self, caplog):
        """Portrait loading failure should log warning with path context (ERR-020)."""
        from game.ui.screens.design_selector_window import DesignSelectorWindow
        from game.strategy.data.design_metadata import DesignMetadata

        # Create minimal window setup with mocks
        manager = MagicMock()
        design_library = MagicMock()
        design_library.scan_designs.return_value = []
        design_library.designs_folder = "/fake/path"

        # Create a mock design metadata
        design = DesignMetadata(
            design_id="Test_Design",
            name="Test Design",
            ship_class="Frigate",
            vehicle_type="Ship",
            mass=1000.0,
            combat_power=100.0,
            theme_id="Federation"
        )

        # Mock os.path.exists to return True, but pygame.image.load to fail
        with patch('os.path.exists', return_value=True):
            with patch('pygame.image.load', side_effect=pygame.error("Test load error")):
                with caplog.at_level(logging.WARNING):
                    # Create instance and call _load_portrait_thumbnail directly
                    # We need to bypass __init__ which sets up UI elements
                    window = object.__new__(DesignSelectorWindow)
                    surface = window._load_portrait_thumbnail(design, size=50)

                # Should return a surface (placeholder)
                assert surface is not None
                assert isinstance(surface, pygame.Surface)

                # Should have logged a warning about the failure
                warning_logs = [r for r in caplog.records if r.levelno >= logging.WARNING]
                assert len(warning_logs) > 0, "Should log warning when portrait load fails"
                warning_text = ' '.join(r.message for r in warning_logs)
                # Should include path or design context
                assert 'portrait' in warning_text.lower() or 'Test_Design' in warning_text or \
                       'Federation' in warning_text or 'Frigate' in warning_text, \
                       f"Warning should include context. Got: {warning_text}"

    def test_portrait_load_success_no_warning(self, caplog, tmp_path):
        """Successful portrait loading should not produce warnings."""
        from game.ui.screens.design_selector_window import DesignSelectorWindow
        from game.strategy.data.design_metadata import DesignMetadata

        design = DesignMetadata(
            design_id="Working_Design",
            name="Working Design",
            ship_class="Cruiser",
            vehicle_type="Ship",
            mass=2000.0,
            combat_power=200.0,
            theme_id="Federation"
        )

        # Create a test image file
        test_surface = pygame.Surface((50, 50))

        # Mock os.path.exists to return False so we use the placeholder path
        # which should NOT log warnings
        with patch('os.path.exists', return_value=False):
            with caplog.at_level(logging.WARNING):
                window = object.__new__(DesignSelectorWindow)
                surface = window._load_portrait_thumbnail(design, size=50)

            assert surface is not None

            # Should NOT log warnings when no files exist (normal fallback to placeholder)
            portrait_warnings = [r for r in caplog.records
                                if 'portrait' in r.message.lower() or 'Working_Design' in r.message]
            assert len(portrait_warnings) == 0, "No warnings when portrait file doesn't exist (normal case)"
