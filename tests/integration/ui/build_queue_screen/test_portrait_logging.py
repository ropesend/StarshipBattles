"""
Tests for portrait loading error logging (ERR-011).
"""

import pytest
import pygame
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

    def get_registries(self):
        """PROJ-382 Phase 1: facade-shaped registries accessor."""
        return self.registries

    def get_colony_demographic_view(self, planet_id):
        """PROJ-382 Phase 1: facade-shaped demographic view stub for tests."""
        return None

    def get_turn_number(self) -> int:
        """PROJ-396 MAJ-003: facade-shaped turn-number accessor."""
        return 0

    def get_save_path(self):
        """PROJ-396 MAJ-004: facade-shaped save-path accessor."""
        return self.savegame_path

    # PROJ-430 / TD-08: expose grouped namespace accessors so production
    # code that calls ``facade.session_meta.registries()`` etc. resolves on the
    # mock without rewriting every helper method.
    @property
    def economy(self):
        class _EconomyNS:
            def __init__(self, parent):
                self._parent = parent
            def colony_demographic_view(self, planet_id):
                return self._parent.get_colony_demographic_view(planet_id) if hasattr(self._parent, "get_colony_demographic_view") else None
            def race_registry(self):
                return getattr(self._parent, "race_registry", None)
            def resolve_config(self):
                return getattr(self._parent, "economy_config", None)
        return _EconomyNS(self)

    @property
    def session_meta(self):
        class _SessionMetaNS:
            def __init__(self, parent):
                self._parent = parent
            def turn_number(self):
                if hasattr(self._parent, "get_turn_number"):
                    return self._parent.get_turn_number()
                return getattr(self._parent, "turn_number", 0)
            def save_path(self):
                if hasattr(self._parent, "get_save_path"):
                    return self._parent.get_save_path()
                return getattr(self._parent, "savegame_path", None) or getattr(self._parent, "save_path", None)
            def human_player_ids(self):
                if hasattr(self._parent, "get_human_player_ids"):
                    return self._parent.get_human_player_ids()
                return getattr(self._parent, "human_player_ids", [])
            def registries(self):
                return self._parent.get_registries() if hasattr(self._parent, "get_registries") else self._parent.registries
        return _SessionMetaNS(self)

    # PROJ-472 Phase 1B: expose ``empires.hex_build_queues`` so BuildQueueScreen
    # resolves build-queue *DTOs* off the mock, mirroring
    # ``FacadeEmpireQueries.hex_build_queues`` (projects domain sources through
    # ``BuildQueueSourceDTO.from_domain``).
    @property
    def empires(self):
        from game.strategy.data.build_queue_source import collect_build_queues_at_hex
        from game.strategy.facade.dto import BuildQueueSourceDTO

        class _EmpiresNS:
            def __init__(self, parent):
                self._parent = parent
            def hex_build_queues(self, empire_id, hex_coord):
                sources = collect_build_queues_at_hex(
                    hex_coord,
                    self._parent.galaxy,
                    self._parent.current_empire,
                    registries=self._parent.get_registries(),
                )
                return [BuildQueueSourceDTO.from_domain(s) for s in sources]
        return _EmpiresNS(self)

    def handle_command(self, cmd):
        """Mock command handler."""
        return ValidationResult()


class TestBuildQueuePortraitLogging:
    """Tests for portrait loading error logging (ERR-011).

    PROJ-40: Updated to use DI injection for dependencies.
    """

    def test_portrait_load_failure_logs_warning(self, caplog, mock_design_catalog, mock_design_loader, mock_registries, ui_manager):
        """Portrait loading failure should log warning with path context."""
        manager = ui_manager

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
            initial_yard=planet,
            on_close_callback=on_close,
            design_catalog=mock_design_catalog,
            design_loader=mock_design_loader,
            hex_coord=hex_coord,
            galaxy=galaxy,
            empire=empire,
            facade=session,
            theme_id_supplier=lambda: "Federation",
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

    def test_portrait_placeholder_fallback_no_spam(self, caplog, mock_design_catalog, mock_design_loader, mock_registries, ui_manager):
        """When no portrait exists, fallback to placeholder without log spam."""
        manager = ui_manager

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
            initial_yard=planet,
            on_close_callback=lambda: None,
            design_catalog=mock_design_catalog,
            design_loader=mock_design_loader,
            hex_coord=hex_coord,
            galaxy=galaxy,
            empire=empire,
            facade=session,
            theme_id_supplier=lambda: "Federation",
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
        # (resource portrait fallback warnings are expected during initialization;
        # PROJ-314 image_sizes-mismatch warnings are also informational and expected
        # when art assets are at non-canonical resolutions)
        design_portrait_warnings = [
            r for r in caplog.records
            if 'portrait' in r.message.lower()
            and 'resource' not in r.message.lower()
            and 'image_sizes' not in r.message.lower()
        ]
        assert len(design_portrait_warnings) == 0, \
            "Should not spam warnings when design portraits simply don't exist"
