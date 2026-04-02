"""
Tests for the complexes list in planet report panel.

This test verifies that the planet report panel displays a scrollable list
of built complexes on the right side, with identical complexes grouped and
shown with quantity counts (e.g. "Mining Complex x3").
"""

import pytest
import pygame
import pygame_gui
from dataclasses import dataclass
from typing import Dict, Any, List
from game.strategy.data.planet import Planet, PlanetType
from game.core.hex_math import HexCoord


@dataclass
class MockFacility:
    """Mock PlanetaryFacility for testing."""
    instance_id: str
    design_id: str
    name: str
    design_data: Dict[str, Any]
    is_operational: bool = True


@pytest.fixture
def mock_planet_with_complexes():
    """Create a planet with multiple facilities."""
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
    planet.atmosphere = {
        'N2': 78000.0,
        'O2': 21000.0,
        'Ar': 1000.0
    }

    # Add facilities (complexes)
    planet.facilities = [
        MockFacility(
            instance_id="fac_1",
            design_id="mining_complex_mk1",
            name="Mining Complex Mk1",
            design_data={}
        ),
        MockFacility(
            instance_id="fac_2",
            design_id="mining_complex_mk1",
            name="Mining Complex Mk1",
            design_data={}
        ),
        MockFacility(
            instance_id="fac_3",
            design_id="mining_complex_mk1",
            name="Mining Complex Mk1",
            design_data={}
        ),
        MockFacility(
            instance_id="fac_4",
            design_id="research_lab_mk1",
            name="Research Lab Mk1",
            design_data={}
        ),
        MockFacility(
            instance_id="fac_5",
            design_id="power_plant_mk2",
            name="Power Plant Mk2",
            design_data={}
        ),
    ]

    return planet


@pytest.fixture
def planet_report_with_complexes(mock_planet_with_complexes, ui_manager):
    """Create PlanetReportPanel with complexes."""
    from game.ui.panels.planet_report_panel import PlanetReportPanel
    panel = PlanetReportPanel(
        manager=ui_manager,
        rect=pygame.Rect(0, 0, 580, 350),
        planet=mock_planet_with_complexes,
        container=None
    )

    yield panel


def test_complexes_container_exists(planet_report_with_complexes):
    """Test that complexes scrolling container exists."""
    assert hasattr(planet_report_with_complexes, 'complexes_container')
    assert planet_report_with_complexes.complexes_container is not None
    assert isinstance(planet_report_with_complexes.complexes_container, pygame_gui.elements.UIScrollingContainer)


def test_complexes_container_position(planet_report_with_complexes):
    """Test that complexes container is positioned on the right side."""
    container = planet_report_with_complexes.complexes_container
    rect = container.relative_rect

    # Should be on the right side (580px panel - 200px width - 10px margin = 370)
    expected_x = 370
    assert rect.x == expected_x, f"Complexes container x should be {expected_x} (right side), got {rect.x}"
    assert rect.y == 10, f"Complexes container y should be 10, got {rect.y}"
    assert rect.width == 200, f"Complexes container width should be 200px, got {rect.width}"


def test_complexes_list_displays_items(planet_report_with_complexes):
    """Test that complexes list displays facility items."""
    panel = planet_report_with_complexes

    # Should have complex items
    assert hasattr(panel, 'complex_items')
    assert len(panel.complex_items) > 0, "Should have complex items"


def test_identical_complexes_grouped_with_count(planet_report_with_complexes):
    """Test that identical complexes are grouped with 'x3' notation."""
    panel = planet_report_with_complexes

    # Find the labels in complex_items
    labels = [item for item in panel.complex_items if isinstance(item, pygame_gui.elements.UILabel)]

    # Should have 3 unique complexes: Mining Complex x3, Research Lab, Power Plant
    assert len(labels) >= 3, f"Should have at least 3 complex types, got {len(labels)}"

    # Check for grouped count notation
    label_texts = [label.text for label in labels]

    # Mining Complex should show "x3"
    mining_labels = [text for text in label_texts if "Mining Complex" in text]
    assert len(mining_labels) == 1, "Should have exactly one Mining Complex entry"
    assert "x3" in mining_labels[0], f"Mining Complex should show 'x3', got: {mining_labels[0]}"


def test_single_complex_no_count(planet_report_with_complexes):
    """Test that single complexes don't show count."""
    panel = planet_report_with_complexes

    # Find the labels
    labels = [item for item in panel.complex_items if isinstance(item, pygame_gui.elements.UILabel)]
    label_texts = [label.text for label in labels]

    # Research Lab and Power Plant should not have "x" notation
    research_labels = [text for text in label_texts if "Research Lab" in text]
    power_labels = [text for text in label_texts if "Power Plant" in text]

    assert len(research_labels) == 1, "Should have exactly one Research Lab entry"
    assert "x" not in research_labels[0], f"Single Research Lab should not show count, got: {research_labels[0]}"

    assert len(power_labels) == 1, "Should have exactly one Power Plant entry"
    assert "x" not in power_labels[0], f"Single Power Plant should not show count, got: {power_labels[0]}"


def test_empty_planet_shows_none(ui_manager):
    """Test that planet with no complexes shows 'None' message."""
    # Create planet with no facilities
    planet = Planet(
        name="Empty Planet",
        location=HexCoord(5, 5),
        orbit_distance=3,
        mass=5.97e24,
        radius=6371000,
        surface_area=5.1e14,
        density=5515,
        surface_gravity=9.81,
        surface_pressure=101325,
        surface_temperature=288,
        surface_water=0.0,
        tectonic_activity=0.0,
        magnetic_field=0.0,
        planet_type=PlanetType.BARREN
    )
    planet.owner_id = 1
    planet.id = 101
    planet.atmosphere = {}
    planet.facilities = []  # No facilities

    from game.ui.panels.planet_report_panel import PlanetReportPanel
    panel = PlanetReportPanel(
        manager=ui_manager,
        rect=pygame.Rect(0, 0, 580, 350),
        planet=planet,
        container=None
    )

    # Should have one item showing "None"
    labels = [item for item in panel.complex_items if isinstance(item, pygame_gui.elements.UILabel)]
    assert len(labels) == 1, "Should have one label"
    assert labels[0].text == "None", f"Should show 'None', got: {labels[0].text}"


def test_update_planet_refreshes_complexes_list(ui_manager):
    """Test that update_planet refreshes the complexes list."""
    # Start with empty planet
    planet1 = Planet(
        name="Planet 1",
        location=HexCoord(5, 5),
        orbit_distance=3,
        mass=5.97e24,
        radius=6371000,
        surface_area=5.1e14,
        density=5515,
        surface_gravity=9.81,
        surface_pressure=101325,
        surface_temperature=288,
        surface_water=0.0,
        tectonic_activity=0.0,
        magnetic_field=0.0,
        planet_type=PlanetType.CONTINENTAL
    )
    planet1.owner_id = 1
    planet1.id = 102
    planet1.atmosphere = {}
    planet1.facilities = []

    from game.ui.panels.planet_report_panel import PlanetReportPanel
    panel = PlanetReportPanel(
        manager=ui_manager,
        rect=pygame.Rect(0, 0, 580, 350),
        planet=planet1,
        container=None
    )

    # Should show "None"
    initial_labels = [item for item in panel.complex_items if isinstance(item, pygame_gui.elements.UILabel)]
    assert len(initial_labels) == 1
    assert initial_labels[0].text == "None"

    # Update to planet with facilities
    planet2 = Planet(
        name="Planet 2",
        location=HexCoord(6, 6),
        orbit_distance=4,
        mass=5.97e24,
        radius=6371000,
        surface_area=5.1e14,
        density=5515,
        surface_gravity=9.81,
        surface_pressure=101325,
        surface_temperature=288,
        surface_water=0.5,
        tectonic_activity=0.1,
        magnetic_field=1.0,
        planet_type=PlanetType.CONTINENTAL
    )
    planet2.owner_id = 1
    planet2.id = 103
    planet2.atmosphere = {}
    planet2.facilities = [
        MockFacility(
            instance_id="fac_1",
            design_id="factory_mk1",
            name="Factory Mk1",
            design_data={}
        )
    ]

    panel.update_planet(planet2)

    # Should now show the factory
    updated_labels = [item for item in panel.complex_items if isinstance(item, pygame_gui.elements.UILabel)]
    assert len(updated_labels) == 1
    assert "Factory" in updated_labels[0].text


def test_complexes_list_is_scrollable(ui_manager):
    """Test that complexes list can handle many items with scrolling."""
    # Create planet with many different complexes
    planet = Planet(
        name="Industrial Hub",
        location=HexCoord(7, 7),
        orbit_distance=5,
        mass=5.97e24,
        radius=6371000,
        surface_area=5.1e14,
        density=5515,
        surface_gravity=9.81,
        surface_pressure=101325,
        surface_temperature=288,
        surface_water=0.3,
        tectonic_activity=0.2,
        magnetic_field=1.0,
        planet_type=PlanetType.CONTINENTAL
    )
    planet.owner_id = 1
    planet.id = 104
    planet.atmosphere = {}

    # Create 15 different complex types
    planet.facilities = [
        MockFacility(
            instance_id=f"fac_{i}",
            design_id=f"complex_type_{i}",
            name=f"Complex Type {i}",
            design_data={}
        )
        for i in range(15)
    ]

    from game.ui.panels.planet_report_panel import PlanetReportPanel
    panel = PlanetReportPanel(
        manager=ui_manager,
        rect=pygame.Rect(0, 0, 580, 350),
        planet=planet,
        container=None
    )

    # Should have 15 complex items
    labels = [item for item in panel.complex_items if isinstance(item, pygame_gui.elements.UILabel)]
    assert len(labels) == 15, f"Should have 15 complex types, got {len(labels)}"

    # Container should be scrollable
    assert isinstance(panel.complexes_container, pygame_gui.elements.UIScrollingContainer)
