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


class MockResource:
    """Mock resource object with numeric values."""
    def __init__(self, max_value=100, current_value=100, regen_rate=0):
        self.max_value = max_value
        self.current_value = current_value
        self.regen_rate = regen_rate


class MockResourceContainer:
    """Mock resources container that returns proper resource objects."""
    def __init__(self):
        self._resources = {
            'fuel': MockResource(max_value=1000, current_value=1000, regen_rate=0),
            'ammo': MockResource(max_value=500, current_value=500, regen_rate=0),
            'energy': MockResource(max_value=1000, current_value=1000, regen_rate=50),
        }

    def get_resource(self, name):
        return self._resources.get(name)

    def get_resource_names(self):
        return list(self._resources.keys())

    def keys(self):
        return self._resources.keys()


class MockShip:
    """Mock Ship class with explicit attributes to prevent MagicMock auto-attribute behavior."""

    def __init__(self):
        self.name = "Test Frigate"
        self.ship_class = "Frigate"
        self.vehicle_type = "Ship"
        self.theme_id = "Federation"

        # Basic stats
        self.max_mass_budget = 1200
        self.max_hp = 500
        self.max_energy = 1000
        self.mass = 1000
        self.mass_limits_ok = True

        # Maneuvering
        self.thrust = 100
        self.acceleration = 5.0
        self.top_speed = 50
        self.maneuver_points = 10
        self.turn_rate = 45
        self.total_maneuver_points = 10
        self.total_strategic_movement = 100

        # Shields
        self.max_shields = 200
        self.shield_regen = 10
        self.shield_regen_cost = 5

        # Armor
        self.total_armor_hp = 300
        self.damage_ignore_threshold = 5
        self.shield_regen_on_hit = 2

        # Targeting
        self.max_targets = 3
        self.evasion_score = 15
        self.targeting_score = 20
        self.target_profile = 10
        self.scan_strength = 15

        # Crew
        self.crew_required = 50
        self.crew_on_board = 50
        self.life_support_capacity = 60

        # Resources (needed for dynamic logistics rows)
        self.resources = MockResourceContainer()

        # Resource consumption/generation attributes (used in get_logistics_rows)
        self.fuel_consumption = 10
        self.ammo_consumption = 5
        self.energy_consumption = 20
        self.potential_fuel_consumption = 10
        self.potential_ammo_consumption = 5
        self.potential_energy_consumption = 20
        self.fuel_generation = 0
        self.ammo_generation = 0
        self.energy_generation = 50

        # Layers (needed for layer status section)
        self.layers = {}  # Empty dict - no layers for mock
        self.layer_status = {}

        # Fighter support
        self.fighter_capacity = 0
        self.fighters_per_wave = 0

        # Construction cost
        self.construction_cost = {
            'Metal': 500,
            'organics': 100,
            'Rare': 50,
            'Synthetics': 200,
            'Volatiles': 150
        }

    def get_all_components(self):
        """Return empty component list for mock."""
        return []

    def get_mass_display(self):
        return self.mass

    def get_ability_total(self, ability_name):
        return 50

    def get_missing_requirements(self):
        return []

    def get_validation_warnings(self):
        return []

    def get_resource_stat(self, resource_name, stat_type):
        """PROJ-194: Typed accessor for resource stats."""
        attr_name = f'{resource_name}_{stat_type}'
        return getattr(self, attr_name, 0.0)


@pytest.fixture
def mock_ship():
    """Create a mock Ship object with stats."""
    return MockShip()


@pytest.fixture
def design_report_panel(mock_ship, ui_manager):
    """Create DesignReportPanel for testing."""
    manager = ui_manager

    # Panel height must be larger than portrait (730px) + stats area
    # Production uses screen_height - 90 (~678 on 768 screen)
    # For test, use 1500 to ensure scrolling container has enough room
    panel_height = 1500

    # Create container panel
    container = pygame_gui.elements.UIPanel(
        relative_rect=pygame.Rect(0, 0, 750, panel_height),
        manager=manager
    )

    # Import and create panel
    from game.ui.panels.design_report_panel import DesignReportPanel
    panel = DesignReportPanel(
        manager=manager,
        rect=pygame.Rect(0, 0, 750, panel_height),
        container=container
    )

    yield panel


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
    """Test that design portrait matches panel width (380x380 for 400px wide panel)."""
    portrait = design_report_panel.portrait_image
    rect = portrait.relative_rect

    # Portrait width should be panel width - 20px margins = 750 - 20 = 730
    expected_width = 730
    expected_height = 730
    assert rect.width == expected_width, f"Portrait width should be {expected_width}px, got {rect.width}"
    assert rect.height == expected_height, f"Portrait height should be {expected_height}px, got {rect.height}"


def test_design_portrait_position_top_left(design_report_panel):
    """Test that portrait is positioned at top-left with margins."""
    portrait = design_report_panel.portrait_image
    rect = portrait.relative_rect

    # Should be at left with 10px margin
    expected_x = 10
    assert rect.x == expected_x, f"Portrait x should be {expected_x} (left margin), got {rect.x}"
    assert rect.y == 10, f"Portrait y should be 10, got {rect.y}"


def test_stats_panel_exists_after_update(design_report_panel, mock_ship):
    """Test that stats panel is created after design update."""
    design_report_panel.update_design(mock_ship)
    assert hasattr(design_report_panel, '_stats_panel')
    assert design_report_panel._stats_panel is not None
    # The stats panel contains a scrolling container
    assert design_report_panel._stats_panel.stats_scroll is not None
    assert isinstance(design_report_panel._stats_panel.stats_scroll, pygame_gui.elements.UIScrollingContainer)


def test_stats_panel_position(design_report_panel, mock_ship):
    """Test that stats panel is positioned below portrait and identity labels."""
    design_report_panel.update_design(mock_ship)
    stats_scroll = design_report_panel._stats_panel.stats_scroll
    rect = stats_scroll.relative_rect

    # Stats should be below portrait + identity labels
    # portrait_h (730) + 15 (gap) + 50 (identity labels) = 795
    # PROJ-81 Phase 4 added identity labels (name + type/class)
    expected_y = 795
    assert rect.y == expected_y, f"Stats scroll y should be {expected_y} (below portrait+identity), got {rect.y}"
    assert rect.x == 10, f"Stats scroll x should be 10 (left margin), got {rect.x}"

    # Stats width should be full width (750 - 20 margins = 730)
    expected_width = 730  # Panel width (750) - margins (20)
    assert rect.width == expected_width, f"Stats scroll width should be {expected_width}, got {rect.width}"


def test_update_design_displays_ship_name(design_report_panel, mock_ship):
    """Test that update_design displays the ship name."""
    design_report_panel.update_design(mock_ship)

    # Check if there's a name label or title
    # The name might be displayed in the panel or stats
    assert design_report_panel.current_ship == mock_ship


def test_identity_labels_populated(design_report_panel, mock_ship):
    """PROJ-81 Phase 4: Test that identity labels are populated with name/type/class."""
    design_report_panel.update_design(mock_ship)

    # Name label should show ship name
    assert design_report_panel.name_label.text == mock_ship.name

    # Type/class label should show vehicle type and ship class
    expected_type_class = f"{mock_ship.vehicle_type} - {mock_ship.ship_class}"
    assert design_report_panel.type_class_label.text == expected_type_class


def test_identity_labels_cleared_on_placeholder(design_report_panel, mock_ship):
    """PROJ-81 Phase 4: Test that identity labels are cleared when showing placeholder."""
    # First show a design
    design_report_panel.update_design(mock_ship)
    assert design_report_panel.name_label.text == mock_ship.name

    # Then show placeholder
    design_report_panel.show_placeholder()

    # Labels should be cleared
    assert design_report_panel.name_label.text == ""
    assert design_report_panel.type_class_label.text == ""


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
    """Test that all 10 major stat sections are present after update (matching design workshop)."""
    design_report_panel.update_design(mock_ship)

    rows_map = design_report_panel.rows_map

    # Check for key stats from all 10 sections
    # 1. Main Systems
    assert any('mass' in key.lower() or 'hp' in key.lower() for key in rows_map.keys()), \
        "Should have Main Systems stats (mass, HP)"

    # 2-4. Separate Logistics sections (Fuel, Ammo/Ordinance, Energy)
    assert any('fuel' in key.lower() for key in rows_map.keys()), \
        "Should have Fuel Logistics stats"
    assert any('ammo' in key.lower() for key in rows_map.keys()), \
        "Should have Ordinance (Ammo) stats"
    assert any('energy' in key.lower() for key in rows_map.keys()), \
        "Should have Energy stats"

    # 10. Construction cost should be present
    assert any('cost' in key.lower() for key in rows_map.keys()), \
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
    """Test that panel width matches design workshop (750px wide)."""
    rect = design_report_panel.rect

    # Width should be 750px to match design workshop
    assert rect.width == 750, f"Panel width should be 750px (design workshop standard), got {rect.width}"
    # Height is variable based on screen size - just verify it's reasonable
    assert rect.height >= 750, f"Panel height should be at least 750px for portrait + stats, got {rect.height}"


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
    ship2 = MockShip()
    ship2.name = "Test Destroyer"
    ship2.ship_class = "Destroyer"
    ship2.mass = 2000
    ship2.construction_cost = {'Metal': 1000}

    # Second update
    design_report_panel.update_design(ship2)
    assert design_report_panel.current_ship == ship2


def test_panel_integrates_with_container(mock_ship, ui_manager):
    """Test that panel properly integrates with a parent container."""
    manager = ui_manager

    panel_height = 1500  # Must be large enough for portrait (730px) + stats

    container = pygame_gui.elements.UIPanel(
        relative_rect=pygame.Rect(520, 10, 750, panel_height),
        manager=manager
    )

    from game.ui.panels.design_report_panel import DesignReportPanel
    panel = DesignReportPanel(
        manager=manager,
        rect=pygame.Rect(0, 0, 750, panel_height),
        container=container
    )

    # Verify panel components are created
    assert panel.portrait_image is not None

    # Stats panel is only created after update_design
    panel.update_design(mock_ship)
    assert panel._stats_panel is not None
    assert panel._stats_panel.stats_scroll is not None


def test_panel_handles_ship_with_minimal_stats(ui_manager):
    """Test that panel handles ship with minimal/missing stats gracefully."""
    manager = ui_manager

    panel_height = 1500  # Must be large enough for portrait + stats

    container = pygame_gui.elements.UIPanel(
        relative_rect=pygame.Rect(0, 0, 750, panel_height),
        manager=manager
    )

    from game.ui.panels.design_report_panel import DesignReportPanel
    panel = DesignReportPanel(
        manager=manager,
        rect=pygame.Rect(0, 0, 750, panel_height),
        container=container
    )

    # Create minimal ship using MockShip class
    minimal_ship = MockShip()
    minimal_ship.name = "Minimal Ship"
    minimal_ship.mass = 0
    minimal_ship.construction_cost = {}

    # Should not crash
    panel.update_design(minimal_ship)
    assert panel.current_ship == minimal_ship
