"""
Tests for enhanced planet report panel in build queue screen.

This test verifies that the planet report panel displays comprehensive planet
information including portrait, stats, and atmosphere graph.
"""

import pytest
import pygame
import pygame_gui
from unittest.mock import MagicMock, patch
from game.strategy.data.planet import Planet, PlanetType
from game.core.hex_math import HexCoord
from game.strategy.data.empire import Empire


class MockSession:
    def __init__(self):
        self.save_path = "test_savegame"
        self.current_empire = Empire(1, "Test Empire", (255, 0, 0))
        self.turn = 1


@pytest.fixture
def mock_design_library():
    """Mock DesignLibrary for testing.

    PROJ-40: Updated to create mock directly instead of patching.
    Now injected via DI.
    """
    mock_instance = MagicMock()
    mock_instance.scan_designs.return_value = []
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
def test_planet():
    """Create a test planet with full data."""
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
        planet_type=PlanetType.CONTINENTAL
    )
    planet.owner_id = 1
    planet.id = 100

    # Add atmosphere data (format: gas_name -> pressure in Pa)
    planet.atmosphere = {
        'N2': 78000.0,
        'O2': 21000.0,
        'Ar': 1000.0,
        'CO2': 400.0,
        'Ne': 18.0,
        'He': 5.0
    }

    # Add resource data (PROJ-82)
    planet.deposits = {
        "metals": {"quantity": 250000, "quality": 85.0},
        "organics": {"quantity": 120000, "quality": 72.0},
        "vapors": {"quantity": 80000, "quality": 91.0},
        "radioactives": {"quantity": 45000, "quality": 43.0},
        "exotics": {"quantity": 12000, "quality": 67.0},
    }

    return planet


@pytest.fixture
def planet_report_panel(test_planet, mock_design_library):
    """Create PlanetReportPanel for testing."""
    pygame.init()
    screen = pygame.display.set_mode((1024, 768))
    manager = pygame_gui.UIManager((1024, 768))

    # Create container panel
    container = pygame_gui.elements.UIPanel(
        relative_rect=pygame.Rect(0, 0, 500, 350),
        manager=manager
    )

    # Import and create panel
    from game.ui.panels.planet_report_panel import PlanetReportPanel
    panel = PlanetReportPanel(
        manager=manager,
        rect=pygame.Rect(0, 0, 500, 350),
        planet=test_planet,
        container=container
    )

    yield panel

    pygame.quit()


def test_planet_report_panel_initializes(planet_report_panel):
    """Test that PlanetReportPanel creates without crashing."""
    assert planet_report_panel is not None
    assert planet_report_panel.planet is not None
    # PROJ-82: Resource panel should also exist
    assert planet_report_panel.resource_panel is not None


def test_planet_portrait_exists(planet_report_panel):
    """Test that planet portrait image is displayed."""
    assert hasattr(planet_report_panel, 'portrait_image')
    assert planet_report_panel.portrait_image is not None
    assert isinstance(planet_report_panel.portrait_image, pygame_gui.elements.UIImage)


def test_planet_portrait_dimensions(planet_report_panel):
    """Test that planet portrait has correct dimensions (150x150)."""
    portrait = planet_report_panel.portrait_image
    rect = portrait.relative_rect  # Use relative_rect for position within container

    assert rect.width == 150, f"Portrait width should be 150px, got {rect.width}"
    assert rect.height == 150, f"Portrait height should be 150px, got {rect.height}"
    assert rect.x == 10, f"Portrait x should be 10, got {rect.x}"
    assert rect.y == 10, f"Portrait y should be 10, got {rect.y}"


def test_planet_info_textbox_exists(planet_report_panel):
    """Test that planet info uses UITextBox for HTML formatting."""
    assert hasattr(planet_report_panel, 'detail_text')
    assert planet_report_panel.detail_text is not None
    assert isinstance(planet_report_panel.detail_text, pygame_gui.elements.UITextBox)


def test_planet_info_textbox_position(planet_report_panel):
    """Test that planet info textbox is positioned correctly."""
    detail_text = planet_report_panel.detail_text
    rect = detail_text.relative_rect  # Use relative_rect for position within container

    assert rect.x == 170, f"Info text x should be 170 (right of portrait), got {rect.x}"
    assert rect.y == 10, f"Info text y should be 10, got {rect.y}"


def test_planet_info_contains_planet_name(planet_report_panel):
    """Test that planet info displays the planet name."""
    detail_text = planet_report_panel.detail_text
    html_text = detail_text.html_text

    assert 'Test Colony' in html_text, "Planet name should be in info text"


def test_planet_info_contains_basic_stats(planet_report_panel):
    """Test that planet info contains basic planet stats."""
    detail_text = planet_report_panel.detail_text
    html_text = detail_text.html_text

    # Should contain mass info
    assert 'Mass' in html_text or 'mass' in html_text.lower(), "Should display mass"

    # Should contain radius info
    assert 'Radius' in html_text or 'radius' in html_text.lower(), "Should display radius"

    # Should contain gravity info
    assert 'Gravity' in html_text or 'gravity' in html_text.lower(), "Should display gravity"


def test_atmosphere_graph_exists(planet_report_panel):
    """Test that atmosphere graph widget is present."""
    assert hasattr(planet_report_panel, 'graph')
    assert planet_report_panel.graph is not None


def test_atmosphere_graph_position(planet_report_panel):
    """Test that atmosphere graph is positioned correctly."""
    # Check the UIImage that displays the graph
    graph_image = planet_report_panel.graph_image
    rect = graph_image.relative_rect

    # Graph should be below portrait at (10, 170)
    assert rect.x == 10, f"Graph x should be 10, got {rect.x}"
    assert rect.y == 170, f"Graph y should be 170 (below portrait), got {rect.y}"
    assert rect.width == 150, f"Graph width should be 150, got {rect.width}"


def test_update_planet_method_exists(planet_report_panel):
    """Test that panel has update_planet method."""
    assert hasattr(planet_report_panel, 'update_planet')
    assert callable(planet_report_panel.update_planet)


def test_update_planet_changes_display(planet_report_panel, test_planet):
    """Test that update_planet method updates the display."""
    # Create a different planet
    new_planet = Planet(
        name="New World",
        location=HexCoord(10, 10),
        orbit_distance=2,
        mass=4.0e24,
        radius=5000000,
        surface_area=3.1e14,
        density=5000,
        surface_gravity=8.0,
        surface_pressure=90000,
        surface_temperature=280,
        surface_water=0.5,
        tectonic_activity=0.2,
        magnetic_field=0.8,
        planet_type=PlanetType.CONTINENTAL
    )
    new_planet.owner_id = 1
    new_planet.id = 200

    # Update panel
    planet_report_panel.update_planet(new_planet)

    # Verify new planet name appears
    html_text = planet_report_panel.detail_text.html_text
    assert 'New World' in html_text, "Updated planet name should appear"
    assert 'Test Colony' not in html_text, "Old planet name should not appear"


def test_panel_minimum_height(planet_report_panel):
    """Test that panel has sufficient height for portrait + graph."""
    # Panel should be at least 350px high to fit portrait (150) + gap + graph (150+)
    assert hasattr(planet_report_panel, 'rect')
    min_height = 350
    assert planet_report_panel.rect.height >= min_height, \
        f"Panel height should be at least {min_height}px, got {planet_report_panel.rect.height}"


def test_get_height_required_method_exists(planet_report_panel):
    """Test that panel has get_height_required method."""
    assert hasattr(planet_report_panel, 'get_height_required')
    assert callable(planet_report_panel.get_height_required)


def test_get_height_required_returns_valid_height(planet_report_panel):
    """Test that get_height_required returns a sensible value."""
    height = planet_report_panel.get_height_required()

    assert isinstance(height, (int, float)), "Height should be numeric"
    # PROJ-82: Height increased to accommodate resource panel (+100)
    assert height >= 400, f"Required height should be at least 400px (350 + resource panel), got {height}"
    assert height <= 600, f"Required height should not exceed 600px, got {height}"


def test_panel_works_with_no_atmosphere(test_planet, mock_design_library):
    """Test that panel handles planet with no atmosphere gracefully."""
    pygame.init()
    screen = pygame.display.set_mode((1024, 768))  # Need display mode for pygame.Surface.convert_alpha()
    manager = pygame_gui.UIManager((1024, 768))

    # Create planet with no atmosphere
    test_planet.atmosphere = {}

    container = pygame_gui.elements.UIPanel(
        relative_rect=pygame.Rect(0, 0, 500, 350),
        manager=manager
    )

    # Should not crash
    from game.ui.panels.planet_report_panel import PlanetReportPanel
    panel = PlanetReportPanel(
        manager=manager,
        rect=pygame.Rect(0, 0, 500, 350),
        planet=test_planet,
        container=container
    )

    assert panel is not None
    pygame.quit()


def test_panel_integrates_with_container(test_planet, mock_design_library):
    """Test that panel properly integrates with a parent container."""
    pygame.init()
    screen = pygame.display.set_mode((1024, 768))  # Need display mode for pygame.Surface.convert_alpha()
    manager = pygame_gui.UIManager((1024, 768))

    container = pygame_gui.elements.UIPanel(
        relative_rect=pygame.Rect(10, 10, 500, 350),
        manager=manager
    )

    from game.ui.panels.planet_report_panel import PlanetReportPanel
    panel = PlanetReportPanel(
        manager=manager,
        rect=pygame.Rect(0, 0, 500, 350),
        planet=test_planet,
        container=container
    )

    # Verify panel components are created
    assert panel.portrait_image is not None
    assert panel.detail_text is not None
    assert panel.graph is not None

    pygame.quit()


def test_portrait_surface_at_init(test_planet, mock_design_library):
    """Test passing portrait_surface at initialization."""
    pygame.init()
    screen = pygame.display.set_mode((1024, 768))
    manager = pygame_gui.UIManager((1024, 768))

    # Create a test portrait surface
    portrait = pygame.Surface((150, 150))
    portrait.fill((100, 100, 200))

    from game.ui.panels.planet_report_panel import PlanetReportPanel
    panel = PlanetReportPanel(
        manager=manager,
        rect=pygame.Rect(0, 0, 580, 350),
        planet=test_planet,
        portrait_surface=portrait
    )

    # Verify portrait was applied
    assert panel.portrait_image is not None
    # Verify no crash, panel created successfully
    assert panel.planet == test_planet

    pygame.quit()


def test_show_complexes_false(test_planet, mock_design_library):
    """Test panel with complexes list hidden."""
    pygame.init()
    screen = pygame.display.set_mode((1024, 768))
    manager = pygame_gui.UIManager((1024, 768))

    from game.ui.panels.planet_report_panel import PlanetReportPanel
    panel = PlanetReportPanel(
        manager=manager,
        rect=pygame.Rect(0, 0, 580, 350),
        planet=test_planet,
        show_complexes=False
    )

    # Verify complexes container is None
    assert panel.complexes_container is None
    assert panel.complex_items == []

    # Verify panel still functions (info text wider)
    assert panel.detail_text is not None

    pygame.quit()


# ============================================================================
# PROJ-82: Resource Grid Tests
# ============================================================================


def test_resource_grid_exists(planet_report_panel):
    """Test that resource grid panel is created and has items."""
    # Resource panel should exist
    assert planet_report_panel.resource_panel is not None
    # Grid items should exist (icons + labels for 5 resources + 3 row labels)
    assert len(planet_report_panel._resource_grid_items) > 0


def test_resource_grid_shows_all_resources(test_planet, mock_design_library):
    """Test that resource grid shows all 5 resource icons."""
    pygame.init()
    screen = pygame.display.set_mode((1024, 768))
    manager = pygame_gui.UIManager((1024, 768))

    from game.ui.panels.planet_report_panel import PlanetReportPanel
    panel = PlanetReportPanel(
        manager=manager,
        rect=pygame.Rect(0, 0, 500, 450),  # Taller to fit resource panel
        planet=test_planet
    )

    # Should have icons for all 8 resources
    assert len(panel._resource_icons) == 8
    assert "metals" in panel._resource_icons
    assert "organics" in panel._resource_icons
    assert "vapors" in panel._resource_icons
    assert "radioactives" in panel._resource_icons
    assert "exotics" in panel._resource_icons
    assert "fuel" in panel._resource_icons
    assert "energy" in panel._resource_icons
    assert "ammo" in panel._resource_icons

    pygame.quit()


def test_resource_grid_with_production(test_planet, mock_design_library):
    """Test that panel accepts production_rates parameter."""
    pygame.init()
    screen = pygame.display.set_mode((1024, 768))
    manager = pygame_gui.UIManager((1024, 768))

    from game.ui.panels.planet_report_panel import PlanetReportPanel
    production_rates = {"metals": 100.0, "organics": 50.0}

    panel = PlanetReportPanel(
        manager=manager,
        rect=pygame.Rect(0, 0, 500, 450),
        planet=test_planet,
        production_rates=production_rates
    )

    # Should accept and store production rates
    assert panel.production_rates == production_rates
    assert panel.resource_panel is not None

    pygame.quit()


def test_resource_grid_no_production(test_planet, mock_design_library):
    """Test that panel works without production_rates parameter."""
    pygame.init()
    screen = pygame.display.set_mode((1024, 768))
    manager = pygame_gui.UIManager((1024, 768))

    from game.ui.panels.planet_report_panel import PlanetReportPanel
    panel = PlanetReportPanel(
        manager=manager,
        rect=pygame.Rect(0, 0, 500, 450),
        planet=test_planet
        # No production_rates - should default to empty
    )

    # Should have empty production rates
    assert panel.production_rates == {}
    assert panel.resource_panel is not None

    pygame.quit()


def test_resource_grid_updates_on_planet_change(test_planet, mock_design_library):
    """Test that resource grid updates when planet changes."""
    pygame.init()
    screen = pygame.display.set_mode((1024, 768))
    manager = pygame_gui.UIManager((1024, 768))

    from game.ui.panels.planet_report_panel import PlanetReportPanel
    panel = PlanetReportPanel(
        manager=manager,
        rect=pygame.Rect(0, 0, 500, 450),
        planet=test_planet
    )

    # Create a different planet with different resources
    new_planet = Planet(
        name="Barren Rock",
        location=HexCoord(10, 10),
        orbit_distance=2,
        mass=4.0e24,
        radius=5000000,
        surface_area=3.1e14,
        density=5000,
        surface_gravity=8.0,
        surface_pressure=90000,
        surface_temperature=280,
        surface_water=0.5,
        tectonic_activity=0.2,
        magnetic_field=0.8,
        planet_type=PlanetType.CONTINENTAL
    )
    new_planet.owner_id = 1
    new_planet.id = 200
    new_planet.deposits = {
        "metals": {"quantity": 500000, "quality": 95.0},
    }

    # Update panel with new planet and production rates
    new_rates = {"metals": 200.0}
    panel.update_planet(new_planet, production_rates=new_rates)

    # Verify state updated
    assert panel.planet == new_planet
    assert panel.production_rates == new_rates
    # Grid items should still exist
    assert len(panel._resource_grid_items) > 0

    pygame.quit()


def test_resource_panel_no_resources(mock_design_library):
    """Test that panel handles planet with empty resources dict."""
    pygame.init()
    screen = pygame.display.set_mode((1024, 768))
    manager = pygame_gui.UIManager((1024, 768))

    # Create planet with empty resources
    empty_planet = Planet(
        name="Empty World",
        location=HexCoord(3, 3),
        orbit_distance=1,
        mass=2.0e24,
        radius=4000000,
        surface_area=2.0e14,
        density=4000,
        surface_gravity=6.0,
        surface_pressure=50000,
        surface_temperature=200,
        surface_water=0.0,
        tectonic_activity=0.0,
        magnetic_field=0.5,
        planet_type=PlanetType.CONTINENTAL
    )
    empty_planet.owner_id = 1
    empty_planet.id = 300
    empty_planet.deposits = {}
    empty_planet.atmosphere = {}

    from game.ui.panels.planet_report_panel import PlanetReportPanel
    panel = PlanetReportPanel(
        manager=manager,
        rect=pygame.Rect(0, 0, 500, 450),
        planet=empty_planet
    )

    # Should not crash, grid should still exist with zero values
    assert panel.resource_panel is not None
    assert len(panel._resource_grid_items) > 0

    pygame.quit()


def test_resource_icons_loaded(planet_report_panel):
    """Test that resource icons are loaded or fallback created."""
    # All 8 resources should have icons
    assert len(planet_report_panel._resource_icons) == 8

    for resource_name, icon_surface in planet_report_panel._resource_icons.items():
        assert isinstance(icon_surface, pygame.Surface)
        assert icon_surface.get_width() == 20
        assert icon_surface.get_height() == 20
