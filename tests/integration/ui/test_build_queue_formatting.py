"""
Test for build queue screen formatting issues.

This test verifies that HTML formatting is properly rendered instead of being displayed literally.
"""

import pytest
import pygame_gui
from unittest.mock import MagicMock, patch
from game.strategy.data.planet import Planet, PlanetType
from game.core.hex_math import HexCoord
from game.strategy.data.empire import Empire
from game.strategy.systems.design_library import DesignLoadResult


class MockGalaxy:
    """Minimal mock Galaxy for BuildQueueScreen tests."""
    def __init__(self):
        self.systems = {}
        self._global_hex_planets = {}  # HexCoord -> List[Planet]
        self.fleets_by_id = {}

    def get_planets_at_global_hex(self, hex_coord):
        """Return planets at a given global hex coordinate."""
        return self._global_hex_planets.get(hex_coord, [])


class MockSession:
    def __init__(self, galaxy=None, empire=None, registries=None):
        self.save_path = "test_savegame"
        self.current_empire = empire or Empire(1, "Test Empire", (255, 0, 0))
        self.turn = 1
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
        return self.turn

    def get_save_path(self):
        """PROJ-396 MAJ-004: facade-shaped save-path accessor."""
        return self.save_path

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

    def handle_command(self, cmd):
        """Mock command handler."""
        from game.core.validation import ValidationResult
        return ValidationResult()


@pytest.fixture
def mock_design_library():
    """Mock DesignLibrary for testing.

    PROJ-40: Updated to create mock directly instead of patching.
    Now injected via DI in build_queue_screen fixture.
    """
    mock_instance = MagicMock()

    complex_design = MagicMock()
    complex_design.design_id = "mining_complex_mk1"
    complex_design.name = "Mining Complex"
    complex_design.vehicle_type = "Planetary Complex"

    mock_instance.scan_designs.return_value = [complex_design]
    mock_instance.designs_folder = "test_designs"
    mock_instance.load_design_data.return_value = DesignLoadResult.not_found("test")

    return mock_instance


@pytest.fixture
def mock_design_loader():
    """Mock SimulationDesignLoader for testing.

    PROJ-40: New fixture for DI injection.
    """
    return MagicMock()


@pytest.fixture
def build_queue_screen(ui_manager, mock_design_library, mock_design_loader, mock_registries):
    """Create BuildQueueScreen for testing.

    PROJ-40: Updated to use DI injection for dependencies.
    PROJ-109: Updated to provide required hex_coord, galaxy, empire parameters.
    PROJ-211: Updated to pass registries for DI.
    """
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

    # Create mock galaxy with planet
    empire = Empire(1, "Test Empire", (255, 0, 0))
    galaxy = MockGalaxy()
    galaxy._global_hex_planets[hex_coord] = [planet]

    # Create mock session with registries
    session = MockSession(galaxy=galaxy, empire=empire, registries=mock_registries)

    # Mock callback
    on_close = MagicMock()

    # Import and create screen with injected dependencies
    from game.ui.screens.build_queue_screen import BuildQueueScreen
    bq_screen = BuildQueueScreen(
        manager,
        planet,
        on_close,
        design_library=mock_design_library,
        design_loader=mock_design_loader,
        hex_coord=hex_coord,
        galaxy=galaxy,
        empire=empire,
        facade=session,
        theme_id_supplier=lambda: "Federation",
    )

    yield bq_screen


def test_planet_report_panel_exists(build_queue_screen):
    """Test that planet report panel widget is present."""
    # PROJ-180: Access via panels.*
    assert hasattr(build_queue_screen.panels, 'planet_report'), \
        "BuildQueueScreen should have panels.planet_report attribute"

    # Should be a PlanetReportPanel instance
    from game.ui.panels.planet_report_panel import PlanetReportPanel
    assert isinstance(build_queue_screen.panels.planet_report, PlanetReportPanel), \
        f"planet_report should be PlanetReportPanel, got {type(build_queue_screen.panels.planet_report)}"


def test_available_designs_header_uses_textbox(build_queue_screen):
    """Test that 'Available Designs' header uses UITextBox for bold formatting."""
    # PROJ-180: Access via panels.*
    items_list_elements = build_queue_screen.panels.items_list_panel.get_container().elements

    # Find header element (should be first non-scrolling element)
    header_elements = [e for e in items_list_elements
                      if not isinstance(e, pygame_gui.elements.UIScrollingContainer)]

    assert len(header_elements) > 0, "Should have header element"
    header = header_elements[0]

    # Should be UITextBox for HTML formatting
    assert isinstance(header, pygame_gui.elements.UITextBox), \
        f"Available Designs header should use UITextBox, got {type(header)}"


def test_build_queue_header_uses_textbox(build_queue_screen):
    """Test that 'Build Queue' header uses UITextBox for bold formatting."""
    # PROJ-180: Access via panels.*
    queue_panel_elements = build_queue_screen.panels.build_queue_panel.get_container().elements

    # Find header element
    header_elements = [e for e in queue_panel_elements
                      if not isinstance(e, pygame_gui.elements.UIScrollingContainer)]

    assert len(header_elements) > 0, "Should have header element"
    header = header_elements[0]

    # Should be UITextBox for HTML formatting
    assert isinstance(header, pygame_gui.elements.UITextBox), \
        f"Build Queue header should use UITextBox, got {type(header)}"


def test_categories_header_uses_textbox(build_queue_screen):
    """Test that 'Categories' header uses UITextBox for bold formatting."""
    # PROJ-180: Access via panels.*
    filter_panel_elements = build_queue_screen.panels.filter_panel.get_container().elements

    # Find the Categories header (first element before buttons)
    non_button_elements = [e for e in filter_panel_elements
                          if not isinstance(e, pygame_gui.elements.UIButton)]

    # Should have at least 2 headers (Categories and Actions)
    assert len(non_button_elements) >= 2, "Should have Categories and Actions headers"

    categories_header = non_button_elements[0]

    # Should be UITextBox for HTML formatting
    assert isinstance(categories_header, pygame_gui.elements.UITextBox), \
        f"Categories header should use UITextBox, got {type(categories_header)}"


def test_actions_header_uses_textbox(build_queue_screen):
    """Test that 'Roles' header uses UITextBox for bold formatting.

    The filter panel contains: Categories header (UITextBox),
    categories scrollable, Roles header (UITextBox), roles scrollable.
    We filter to UITextBox elements only to find the headers.
    """
    # PROJ-180: Access via panels.*
    filter_panel_elements = build_queue_screen.panels.filter_panel.get_container().elements

    # Find UITextBox header elements specifically
    header_elements = [e for e in filter_panel_elements
                      if isinstance(e, pygame_gui.elements.UITextBox)]

    # Should have at least 2 headers (Categories and Roles)
    assert len(header_elements) >= 2, "Should have Categories and Roles headers"

    roles_header = header_elements[1]

    # Should be UITextBox for HTML formatting
    assert isinstance(roles_header, pygame_gui.elements.UITextBox), \
        f"Roles header should use UITextBox, got {type(roles_header)}"


def test_html_text_contains_bold_tags(build_queue_screen):
    """Test that headers actually contain HTML bold tags in their html_text."""
    # PROJ-180: Access via panels.*
    items_list_elements = build_queue_screen.panels.items_list_panel.get_container().elements
    header_elements = [e for e in items_list_elements
                      if not isinstance(e, pygame_gui.elements.UIScrollingContainer)]

    if header_elements and hasattr(header_elements[0], 'html_text'):
        assert '<b>' in header_elements[0].html_text, "Available Designs header should contain <b> tags"
        assert '</b>' in header_elements[0].html_text, "Available Designs header should contain </b> tags"


def test_design_report_panel_exists(build_queue_screen):
    """Test that design report panel widget is present."""
    # PROJ-180: Access via panels.*
    assert hasattr(build_queue_screen.panels, 'design_report'), \
        "BuildQueueScreen should have panels.design_report attribute"

    # Should be a DesignReportPanel instance
    from game.ui.panels.design_report_panel import DesignReportPanel
    assert isinstance(build_queue_screen.panels.design_report, DesignReportPanel), \
        f"design_report should be DesignReportPanel, got {type(build_queue_screen.panels.design_report)}"
