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
from game.strategy.systems.design_repository import DesignLoadResult

# PROJ-494 T2.18: MockGalaxy + MockSession moved to `tests/integration/ui/conftest.py`
# so other UI integration tests can reuse them.
from tests.integration.ui.conftest import MockGalaxy, MockSession


@pytest.fixture
def mock_design_catalog():
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
def build_queue_screen(ui_manager, mock_design_catalog, mock_design_loader, mock_registries):
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
        initial_yard=planet,
        on_close_callback=on_close,
        design_catalog=mock_design_catalog,
        design_loader=mock_design_loader,
        hex_coord=hex_coord,
        world=galaxy,  # PROJ-477 Phase 4
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
