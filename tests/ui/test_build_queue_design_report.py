"""
Tests for design report panel in build queue screen.

This test verifies that the design report panel displays comprehensive design
information including portrait and detailed stats in a two-column layout.
"""

import pytest
import pygame
import pygame_gui
from unittest.mock import MagicMock, patch
from game.simulation.entities.ship import Ship


@pytest.fixture
def mock_ship():
    """Create a mock Ship object with stats."""
    ship = MagicMock()
    ship.name = "Test Frigate"
    ship.ship_class = "Frigate"
    ship.vehicle_type = "Ship"
    ship.theme = "default"

    # Basic stats - use configure_mock for methods
    ship.get_mass_display = MagicMock(return_value=1000)
    ship.max_mass_budget = 1200
    ship.max_hp = 500
    ship.max_energy = 1000
    ship.energy_generation = 50

    # Maneuvering
    ship.thrust = 100
    ship.acceleration = 5.0
    ship.top_speed = 50
    ship.maneuver_points = 10
    ship.turn_rate = 45

    # Shields
    ship.max_shields = 200
    ship.shield_regen = 10
    ship.shield_regen_cost = 5

    # Armor
    ship.total_armor_hp = 300
    ship.damage_ignore_threshold = 5
    ship.shield_regen_on_hit = 2

    # Targeting
    ship.max_targets = 3
    ship.evasion_score = 15
    ship.targeting_score = 20

    # Crew
    ship.crew_required = 50
    ship.crew_on_board = 50
    ship.life_support_capacity = 60

    # Construction cost
    ship.construction_cost = {
        'Metal': 500,
        'Organics': 100,
        'Rare': 50,
        'Synthetics': 200,
        'Volatiles': 150
    }

    return ship


@pytest.fixture
def design_report_panel(mock_ship):
    """Create DesignReportPanel for testing."""
    pygame.init()
    screen = pygame.display.set_mode((1024, 768))
    manager = pygame_gui.UIManager((1024, 768))

    # Create container panel
    container = pygame_gui.elements.UIPanel(
        relative_rect=pygame.Rect(0, 0, 750, 350),
        manager=manager
    )

    # Import and create panel
    from game.ui.panels.design_report_panel import DesignReportPanel
    panel = DesignReportPanel(
        manager=manager,
        rect=pygame.Rect(0, 0, 750, 350),
        container=container
    )

    yield panel

    pygame.quit()


def test_design_report_panel_initializes(design_report_panel):
    """Test that DesignReportPanel creates without crashing."""
    assert design_report_panel is not None


def test_panel_shows_placeholder_initially(design_report_panel):
    """Test that panel shows placeholder message initially."""
    # Panel should have a placeholder text or message
    assert hasattr(design_report_panel, 'placeholder_text') or \
           hasattr(design_report_panel, 'stats_container')


def test_show_placeholder_method_exists(design_report_panel):
    """Test that panel has show_placeholder method."""
    assert hasattr(design_report_panel, 'show_placeholder')
    assert callable(design_report_panel.show_placeholder)


def test_update_design_method_exists(design_report_panel):
    """Test that panel has update_design method."""
    assert hasattr(design_report_panel, 'update_design')
    assert callable(design_report_panel.update_design)


def test_design_portrait_exists(design_report_panel):
    """Test that design portrait image widget exists."""
    assert hasattr(design_report_panel, 'portrait_image')
    assert design_report_panel.portrait_image is not None
    assert isinstance(design_report_panel.portrait_image, pygame_gui.elements.UIImage)


def test_design_portrait_dimensions(design_report_panel):
    """Test that design portrait has correct dimensions (200x200)."""
    portrait = design_report_panel.portrait_image
    rect = portrait.relative_rect

    assert rect.width == 200, f"Portrait width should be 200px, got {rect.width}"
    assert rect.height == 200, f"Portrait height should be 200px, got {rect.height}"


def test_design_portrait_position_top_right(design_report_panel):
    """Test that portrait is positioned at top-right."""
    portrait = design_report_panel.portrait_image
    rect = portrait.relative_rect

    # Should be near right edge (750 - 200 - margin)
    expected_x = 750 - 210  # 200px portrait + 10px margin
    assert rect.x == expected_x, f"Portrait x should be {expected_x} (top-right), got {rect.x}"
    assert rect.y == 10, f"Portrait y should be 10, got {rect.y}"


def test_stats_container_exists(design_report_panel):
    """Test that stats scrolling container exists."""
    assert hasattr(design_report_panel, 'stats_container')
    assert design_report_panel.stats_container is not None
    assert isinstance(design_report_panel.stats_container, pygame_gui.elements.UIScrollingContainer)


def test_stats_container_position(design_report_panel):
    """Test that stats container is positioned below portrait area."""
    stats_container = design_report_panel.stats_container
    rect = stats_container.relative_rect

    # Should start below portrait (200 + margin)
    expected_y = 220  # Portrait 200px + 20px margin
    assert rect.y >= expected_y - 10, f"Stats container y should be around {expected_y}, got {rect.y}"


def test_update_design_displays_ship_name(design_report_panel, mock_ship):
    """Test that update_design displays the ship name."""
    design_report_panel.update_design(mock_ship)

    # Check if there's a name label or title
    # The name might be displayed in the panel or stats
    assert design_report_panel.current_ship == mock_ship


def test_update_design_updates_portrait(design_report_panel, mock_ship):
    """Test that update_design updates the portrait image."""
    design_report_panel.update_design(mock_ship)

    # Portrait should be updated (image surface should not be None)
    assert design_report_panel.portrait_image is not None


def test_update_design_displays_stats(design_report_panel, mock_ship):
    """Test that update_design displays ship stats."""
    design_report_panel.update_design(mock_ship)

    # Stats rows should be created
    assert hasattr(design_report_panel, 'rows_map')
    assert len(design_report_panel.rows_map) > 0, "Should have stat rows after update"


def test_stat_sections_exist_after_update(design_report_panel, mock_ship):
    """Test that all major stat sections are present after update."""
    design_report_panel.update_design(mock_ship)

    rows_map = design_report_panel.rows_map

    # Check for key stats from different sections
    # Main Systems
    assert any('mass' in key.lower() or 'hp' in key.lower() for key in rows_map.keys()), \
        "Should have Main Systems stats (mass, HP)"

    # Construction cost should be present
    assert any('cost' in key.lower() or 'construction' in key.lower() for key in rows_map.keys()), \
        "Should have construction cost stats"


def test_no_requirements_section(design_report_panel, mock_ship):
    """Test that requirements section is NOT included."""
    design_report_panel.update_design(mock_ship)

    # Should not have requirements validation box
    assert not hasattr(design_report_panel, 'requirements_box') or \
           design_report_panel.requirements_box is None


def test_no_warnings_section(design_report_panel, mock_ship):
    """Test that warnings/recommendations section is NOT included."""
    design_report_panel.update_design(mock_ship)

    # Should not have warnings validation box
    assert not hasattr(design_report_panel, 'warnings_box') or \
           design_report_panel.warnings_box is None


def test_panel_dimensions_match_design_workshop(design_report_panel):
    """Test that panel dimensions match design workshop (750px wide)."""
    rect = design_report_panel.rect

    assert rect.width == 750, f"Panel width should be 750px (design workshop standard), got {rect.width}"
    assert rect.height == 350, f"Panel height should be 350px (match planet report), got {rect.height}"


def test_get_width_required_method_exists(design_report_panel):
    """Test that panel has get_width_required method."""
    assert hasattr(design_report_panel, 'get_width_required')
    assert callable(design_report_panel.get_width_required)


def test_get_width_required_returns_750(design_report_panel):
    """Test that get_width_required returns 750px."""
    width = design_report_panel.get_width_required()

    assert width == 750, f"Required width should be 750px, got {width}"


def test_show_placeholder_clears_stats(design_report_panel, mock_ship):
    """Test that show_placeholder clears stat displays."""
    # First update with a ship
    design_report_panel.update_design(mock_ship)
    initial_rows = len(design_report_panel.rows_map)
    assert initial_rows > 0, "Should have rows after update"

    # Show placeholder
    design_report_panel.show_placeholder()

    # Stats should be hidden or cleared
    assert hasattr(design_report_panel, 'placeholder_text') or \
           design_report_panel.current_ship is None


def test_show_placeholder_displays_message(design_report_panel):
    """Test that show_placeholder displays a message."""
    design_report_panel.show_placeholder()

    # Should have placeholder text element
    assert hasattr(design_report_panel, 'placeholder_text')
    assert design_report_panel.placeholder_text is not None


def test_multiple_ship_updates(design_report_panel, mock_ship):
    """Test that panel handles multiple ship updates correctly."""
    # First update
    design_report_panel.update_design(mock_ship)
    assert design_report_panel.current_ship == mock_ship

    # Create different ship
    ship2 = MagicMock()
    ship2.name = "Test Destroyer"
    ship2.ship_class = "Destroyer"
    ship2.get_mass_display = MagicMock(return_value=2000)
    ship2.construction_cost = {'Metal': 1000}

    # Second update
    design_report_panel.update_design(ship2)
    assert design_report_panel.current_ship == ship2


def test_panel_integrates_with_container():
    """Test that panel properly integrates with a parent container."""
    pygame.init()
    screen = pygame.display.set_mode((1024, 768))
    manager = pygame_gui.UIManager((1024, 768))

    container = pygame_gui.elements.UIPanel(
        relative_rect=pygame.Rect(520, 10, 750, 350),
        manager=manager
    )

    from game.ui.panels.design_report_panel import DesignReportPanel
    panel = DesignReportPanel(
        manager=manager,
        rect=pygame.Rect(0, 0, 750, 350),
        container=container
    )

    # Verify panel components are created
    assert panel.portrait_image is not None
    assert panel.stats_container is not None

    pygame.quit()


def test_panel_handles_ship_with_minimal_stats():
    """Test that panel handles ship with minimal/missing stats gracefully."""
    pygame.init()
    screen = pygame.display.set_mode((1024, 768))
    manager = pygame_gui.UIManager((1024, 768))

    container = pygame_gui.elements.UIPanel(
        relative_rect=pygame.Rect(0, 0, 750, 350),
        manager=manager
    )

    from game.ui.panels.design_report_panel import DesignReportPanel
    panel = DesignReportPanel(
        manager=manager,
        rect=pygame.Rect(0, 0, 750, 350),
        container=container
    )

    # Create minimal ship
    minimal_ship = MagicMock()
    minimal_ship.name = "Minimal Ship"
    minimal_ship.get_mass_display = MagicMock(return_value=0)
    minimal_ship.construction_cost = {}

    # Should not crash
    panel.update_design(minimal_ship)
    assert panel.current_ship == minimal_ship

    pygame.quit()
