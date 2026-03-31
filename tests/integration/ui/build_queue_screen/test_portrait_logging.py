"""
Tests for portrait loading error logging (ERR-011).
"""

import pytest
import pygame
import pygame_gui
import logging
from unittest.mock import MagicMock, patch
from game.strategy.data.planet import Planet, PlanetType
from game.core.hex_math import HexCoord
from game.strategy.data.empire import Empire
from game.core.validation import ValidationResult


class MockGalaxy:
    """Minimal mock Galaxy for BuildQueueScreen tests."""
    def __init__(self):
        self.systems = {}
        self._global_hex_planets = {}
        self.fleets_by_id = {}

    def get_planets_at_global_hex(self, hex_coord):
        return self._global_hex_planets.get(hex_coord, [])


class MockSession:
    def __init__(self, galaxy=None, empire=None, registries=None):
        self.savegame_path = "test_savegame"
        self.current_empire = empire or Empire(1, "Test Empire", (255, 0, 0))
        self.galaxy = galaxy or MockGalaxy()
        # PROJ-211: Add registries for DI
        self.registries = registries

    def handle_command(self, cmd):
        """Mock command handler."""
        return ValidationResult()


class TestBuildQueuePortraitLogging:
    """Tests for portrait loading error logging (ERR-011).

    PROJ-40: Updated to use DI injection for dependencies.
    """

    def test_portrait_load_failure_logs_warning(self, caplog, mock_design_library, mock_design_loader, mock_registries):
        """Portrait loading failure should log warning with path context."""
        pygame.init()
        screen = pygame.display.set_mode((1024, 768))
        manager = pygame_gui.UIManager((1024, 768))

        hex_coord = HexCoord(5, 5)
        # Create test planet
        planet = Planet(
            name="Test Colony",
            location=hex_coord,
            orbit_distance=3,
            mass=5.97e24,
            radius=6371000,
            surface_area=5.1e14,
            density=5515,
            surface_gravity=9.81,
            surface_pressure=101325,
            surface_temperature=288,
            surface_water=0.7,
            tectonic_activity=0.1,
            magnetic_field=1.0,
            planet_type=PlanetType.CONTINENTAL
        )
        planet.owner_id = 1
        planet.id = 100

        empire = Empire(1, "Test Empire", (255, 0, 0))
        galaxy = MockGalaxy()
        galaxy._global_hex_planets[hex_coord] = [planet]

        # PROJ-211: Pass registries for DI
        session = MockSession(galaxy=galaxy, empire=empire, registries=mock_registries)
        on_close = MagicMock()

        from game.ui.screens.build_queue_screen import BuildQueueScreen
        bq_screen = BuildQueueScreen(
            manager,
            planet,
            session,
            on_close,
            design_library=mock_design_library,
            design_loader=mock_design_loader,
            hex_coord=hex_coord,
            galaxy=galaxy,
            empire=empire
        )

        # Create mock design
        mock_design = MagicMock()
        mock_design.ship_class = "TestClass"
        mock_design.vehicle_type = "Ship"

        # Simulate file exists but loading fails
        # Make os.path.exists return True for the first portrait path
        # PROJ-63: Use portrait_loader (extracted class)
        with patch('os.path.exists', return_value=True):
            # Make pygame.image.load always raise an exception
            with patch('pygame.image.load', side_effect=pygame.error("Cannot identify image file")):
                with caplog.at_level(logging.WARNING):
                    result = bq_screen.portrait_loader.load_design_portrait(mock_design, 64)

        # Should have returned placeholder (since all paths failed)
        assert result is not None  # Placeholder surface

        # Should have logged a warning about the failed load
        warning_logs = [r for r in caplog.records if r.levelno >= logging.WARNING]
        assert len(warning_logs) > 0, "Should log warning when portrait load fails"
        warning_text = ' '.join(r.message for r in warning_logs)
        # Warning should include the path
        assert 'portrait' in warning_text.lower() or 'load' in warning_text.lower(), \
            f"Warning should mention portrait load failure. Got: {warning_text}"

        pygame.quit()

    def test_portrait_placeholder_fallback_no_spam(self, caplog, mock_design_library, mock_design_loader, mock_registries):
        """When no portrait exists, fallback to placeholder without log spam."""
        pygame.init()
        screen = pygame.display.set_mode((1024, 768))
        manager = pygame_gui.UIManager((1024, 768))

        hex_coord = HexCoord(5, 5)
        planet = Planet(
            name="Test Colony",
            location=hex_coord,
            orbit_distance=3,
            mass=5.97e24,
            radius=6371000,
            surface_area=5.1e14,
            density=5515,
            surface_gravity=9.81,
            surface_pressure=101325,
            surface_temperature=288,
            surface_water=0.7,
            tectonic_activity=0.1,
            magnetic_field=1.0,
            planet_type=PlanetType.CONTINENTAL
        )
        planet.owner_id = 1
        planet.id = 100

        empire = Empire(1, "Test Empire", (255, 0, 0))
        galaxy = MockGalaxy()
        galaxy._global_hex_planets[hex_coord] = [planet]

        # PROJ-211: Pass registries for DI
        session = MockSession(galaxy=galaxy, empire=empire, registries=mock_registries)

        from game.ui.screens.build_queue_screen import BuildQueueScreen
        bq_screen = BuildQueueScreen(
            manager,
            planet,
            session,
            lambda: None,
            design_library=mock_design_library,
            design_loader=mock_design_loader,
            hex_coord=hex_coord,
            galaxy=galaxy,
            empire=empire
        )

        mock_design = MagicMock()
        mock_design.ship_class = "NonexistentClass"
        mock_design.vehicle_type = "Ship"

        # No paths exist - should silently fall through to placeholder
        # PROJ-63: Use portrait_loader (extracted class)
        with patch('os.path.exists', return_value=False):
            with caplog.at_level(logging.WARNING):
                result = bq_screen.portrait_loader.load_design_portrait(mock_design, 64)

        # Should return placeholder surface
        assert result is not None
        assert isinstance(result, pygame.Surface)

        # Should NOT log warnings for design portrait loads when files simply don't exist
        # (resource portrait fallback warnings are expected during initialization)
        design_portrait_warnings = [r for r in caplog.records
                                    if 'portrait' in r.message.lower()
                                    and 'resource' not in r.message.lower()]
        assert len(design_portrait_warnings) == 0, \
            "Should not spam warnings when design portraits simply don't exist"

        pygame.quit()
