"""
Test for build queue screen formatting issues.

This test verifies that HTML formatting is properly rendered instead of being displayed literally.
"""

import pytest
import pygame
import pygame_gui
from unittest.mock import MagicMock, patch
from game.strategy.data.planet import Planet, PlanetType
from game.strategy.data.hex_math import HexCoord
from game.strategy.data.empire import Empire


class MockSession:
    def __init__(self):
        self.save_path = "test_savegame"
        self.current_empire = Empire(1, "Test Empire", (255, 0, 0))
        self.turn = 1

    def handle_command(self, cmd):
        """Mock command handler."""
        from game.core.validation import validation_result
        return validation_result(True, "Command processed")


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
    mock_instance.load_design_data.return_value = None

    return mock_instance


@pytest.fixture
def mock_design_loader():
    """Mock SimulationDesignLoader for testing.

    PROJ-40: New fixture for DI injection.
    """
    return MagicMock()


@pytest.fixture
def build_queue_screen(mock_design_library, mock_design_loader):
    """Create BuildQueueScreen for testing.

    PROJ-40: Updated to use DI injection for dependencies.
    """
    pygame.init()
    screen = pygame.display.set_mode((1024, 768))
    manager = pygame_gui.UIManager((1024, 768))

    # Create test planet
    planet = Planet(
        name="Test Colony",
        location=HexCoord(5, 5),
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
        planet_type=PlanetType.TERRESTRIAL
    )
    planet.owner_id = 1
    planet.id = 100

    # Create mock session
    session = MockSession()

    # Mock callback
    on_close = MagicMock()

    # Import and create screen with injected dependencies
    from game.ui.screens.build_queue_screen import BuildQueueScreen
    bq_screen = BuildQueueScreen(
        manager,
        planet,
        session,
        on_close,
        design_library=mock_design_library,
        design_loader=mock_design_loader
    )

    yield bq_screen

    pygame.quit()


def test_planet_report_panel_exists(build_queue_screen):
    """Test that planet report panel widget is present."""
    # Planet report should now be a PlanetReportPanel widget
    assert hasattr(build_queue_screen, 'planet_report'), \
        "BuildQueueScreen should have planet_report attribute"

    # Should be a PlanetReportPanel instance
    from game.ui.panels.planet_report_panel import PlanetReportPanel
    assert isinstance(build_queue_screen.planet_report, PlanetReportPanel), \
        f"planet_report should be PlanetReportPanel, got {type(build_queue_screen.planet_report)}"


def test_available_designs_header_uses_textbox(build_queue_screen):
    """Test that 'Available Designs' header uses UITextBox for bold formatting."""
    items_list_elements = build_queue_screen.items_list_panel.get_container().elements

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
    queue_panel_elements = build_queue_screen.build_queue_panel.get_container().elements

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
    filter_panel_elements = build_queue_screen.filter_panel.get_container().elements

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
    """Test that 'Actions' header uses UITextBox for bold formatting."""
    filter_panel_elements = build_queue_screen.filter_panel.get_container().elements

    # Find non-button elements
    non_button_elements = [e for e in filter_panel_elements
                          if not isinstance(e, pygame_gui.elements.UIButton)]

    # Should have at least 2 headers
    assert len(non_button_elements) >= 2, "Should have Categories and Actions headers"

    actions_header = non_button_elements[1]

    # Should be UITextBox for HTML formatting
    assert isinstance(actions_header, pygame_gui.elements.UITextBox), \
        f"Actions header should use UITextBox, got {type(actions_header)}"


def test_html_text_contains_bold_tags(build_queue_screen):
    """Test that headers actually contain HTML bold tags in their html_text."""
    # Check Available Designs header
    items_list_elements = build_queue_screen.items_list_panel.get_container().elements
    header_elements = [e for e in items_list_elements
                      if not isinstance(e, pygame_gui.elements.UIScrollingContainer)]

    if header_elements and hasattr(header_elements[0], 'html_text'):
        assert '<b>' in header_elements[0].html_text, "Available Designs header should contain <b> tags"
        assert '</b>' in header_elements[0].html_text, "Available Designs header should contain </b> tags"


def test_design_report_panel_exists(build_queue_screen):
    """Test that design report panel widget is present."""
    # Design report should be a DesignReportPanel widget
    assert hasattr(build_queue_screen, 'design_report'), \
        "BuildQueueScreen should have design_report attribute"

    # Should be a DesignReportPanel instance
    from game.ui.panels.design_report_panel import DesignReportPanel
    assert isinstance(build_queue_screen.design_report, DesignReportPanel), \
        f"design_report should be DesignReportPanel, got {type(build_queue_screen.design_report)}"
