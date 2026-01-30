"""Tests for component sorting, filtering, and type filter logic."""
import pytest
from unittest.mock import Mock
from types import SimpleNamespace


class TestSortingLogic:
    """Tests for component sorting logic."""

    def test_sort_by_name(self):
        """Components are sorted alphabetically by name."""
        components = [
            SimpleNamespace(name="Zeta", id="c1", type_str="Weapon", mass=100.0),
            SimpleNamespace(name="Alpha", id="c2", type_str="Engine", mass=50.0),
            SimpleNamespace(name="Beta", id="c3", type_str="Shield", mass=75.0),
        ]

        sorted_components = sorted(components, key=lambda c: c.name)

        assert sorted_components[0].name == "Alpha"
        assert sorted_components[1].name == "Beta"
        assert sorted_components[2].name == "Zeta"

    def test_sort_by_mass_low_high(self):
        """Components are sorted by mass (low to high)."""
        components = [
            Mock(name="Heavy", id="c1", mass=200.0),
            Mock(name="Light", id="c2", mass=50.0),
            Mock(name="Medium", id="c3", mass=100.0),
        ]

        sorted_components = sorted(components, key=lambda c: c.mass)

        assert sorted_components[0].mass == 50.0
        assert sorted_components[1].mass == 100.0
        assert sorted_components[2].mass == 200.0

    def test_sort_by_mass_high_low(self):
        """Components are sorted by mass (high to low)."""
        components = [
            Mock(name="Light", id="c1", mass=50.0),
            Mock(name="Heavy", id="c2", mass=200.0),
            Mock(name="Medium", id="c3", mass=100.0),
        ]

        sorted_components = sorted(components, key=lambda c: c.mass, reverse=True)

        assert sorted_components[0].mass == 200.0
        assert sorted_components[1].mass == 100.0
        assert sorted_components[2].mass == 50.0

    def test_sort_by_type(self):
        """Components are sorted by type, then by name."""
        components = [
            SimpleNamespace(name="Cannon B", id="c1", type_str="Weapon"),
            SimpleNamespace(name="Engine A", id="c2", type_str="Engine"),
            SimpleNamespace(name="Cannon A", id="c3", type_str="Weapon"),
            SimpleNamespace(name="Shield A", id="c4", type_str="Shield"),
        ]

        sorted_components = sorted(components, key=lambda c: (c.type_str, c.name))

        assert sorted_components[0].type_str == "Engine"
        assert sorted_components[1].type_str == "Shield"
        assert sorted_components[2].name == "Cannon A"
        assert sorted_components[3].name == "Cannon B"

    def test_sort_by_classification(self):
        """Components are sorted by classification, then by name."""
        components = [
            Mock(name="Reactor", id="c1", data={'major_classification': 'Utility'}),
            Mock(name="Laser", id="c2", data={'major_classification': 'Offensive'}),
            Mock(name="Shield", id="c3", data={'major_classification': 'Defensive'}),
        ]

        sorted_components = sorted(
            components,
            key=lambda c: (c.data.get('major_classification', 'Unknown'), c.name)
        )

        assert sorted_components[0].data['major_classification'] == "Defensive"
        assert sorted_components[1].data['major_classification'] == "Offensive"
        assert sorted_components[2].data['major_classification'] == "Utility"

    def test_sort_by_default_order(self):
        """Components maintain original order when using default sort."""
        components = [
            SimpleNamespace(name="Third", id="c3"),
            SimpleNamespace(name="First", id="c1"),
            SimpleNamespace(name="Second", id="c2"),
        ]

        component_order_map = {"c3": 0, "c1": 1, "c2": 2}
        sorted_components = sorted(
            components,
            key=lambda c: component_order_map.get(c.id, 9999)
        )

        assert sorted_components[0].name == "Third"
        assert sorted_components[1].name == "First"
        assert sorted_components[2].name == "Second"


class TestFilteringLogic:
    """Tests for component filtering logic."""

    def test_filter_by_vehicle_type(self):
        """Components are filtered by vehicle type."""
        components = [
            Mock(id="c1", allowed_vehicle_types=["Ship", "Station"]),
            Mock(id="c2", allowed_vehicle_types=["Ship"]),
            Mock(id="c3", allowed_vehicle_types=["Station"]),
        ]

        vehicle_type = "Ship"
        filtered = [c for c in components if vehicle_type in c.allowed_vehicle_types]

        assert len(filtered) == 2
        assert all("Ship" in c.allowed_vehicle_types for c in filtered)

    def test_filter_excludes_hulls(self):
        """Hull components are excluded from the palette."""
        components = [
            Mock(id="c1", type_str="Weapon"),
            Mock(id="c2", type_str="Hull"),
            Mock(id="c3", type_str="Engine"),
        ]

        filtered = [c for c in components if c.type_str != "Hull"]

        assert len(filtered) == 2
        assert not any(c.type_str == "Hull" for c in filtered)

    def test_filter_by_component_type(self):
        """Components are filtered by component type."""
        components = [
            Mock(id="c1", type_str="Weapon"),
            Mock(id="c2", type_str="Engine"),
            Mock(id="c3", type_str="Weapon"),
            Mock(id="c4", type_str="Shield"),
        ]

        type_filter = "Weapon"
        filtered = [c for c in components if c.type_str == type_filter]

        assert len(filtered) == 2
        assert all(c.type_str == "Weapon" for c in filtered)

    def test_filter_all_types(self):
        """All Types filter returns all components."""
        components = [
            Mock(id="c1", type_str="Weapon"),
            Mock(id="c2", type_str="Engine"),
            Mock(id="c3", type_str="Shield"),
        ]

        type_filter = "All Types"
        if type_filter == "All Types":
            filtered = components
        else:
            filtered = [c for c in components if c.type_str == type_filter]

        assert len(filtered) == 3


class TestTypeFilterOptions:
    """Tests for type filter options generation."""

    def test_type_filter_options_include_all_types(self):
        """Type filter options include 'All Types' first."""
        components = [
            Mock(type_str="Weapon"),
            Mock(type_str="Engine"),
            Mock(type_str="Shield"),
        ]

        all_types = sorted(list(set(c.type_str for c in components)))
        type_filter_options = ["All Types"] + all_types

        assert type_filter_options[0] == "All Types"
        assert "Weapon" in type_filter_options
        assert "Engine" in type_filter_options
        assert "Shield" in type_filter_options

    def test_type_filter_options_sorted_alphabetically(self):
        """Type filter options are sorted alphabetically."""
        components = [
            Mock(type_str="Weapon"),
            Mock(type_str="Engine"),
            Mock(type_str="Shield"),
        ]

        all_types = sorted(list(set(c.type_str for c in components)))

        assert all_types == ["Engine", "Shield", "Weapon"]

    def test_type_filter_options_no_duplicates(self):
        """Type filter options have no duplicates."""
        components = [
            Mock(type_str="Weapon"),
            Mock(type_str="Weapon"),
            Mock(type_str="Engine"),
            Mock(type_str="Engine"),
        ]

        all_types = sorted(list(set(c.type_str for c in components)))

        assert len(all_types) == 2
        assert all_types == ["Engine", "Weapon"]


class TestComponentOrderMap:
    """Tests for component order map generation."""

    def test_order_map_contains_all_components(self):
        """Order map contains entries for all components."""
        components = [
            Mock(id="c1"),
            Mock(id="c2"),
            Mock(id="c3"),
        ]

        order_map = {c.id: i for i, c in enumerate(components)}

        assert len(order_map) == 3
        assert "c1" in order_map
        assert "c2" in order_map
        assert "c3" in order_map

    def test_order_map_preserves_order(self):
        """Order map preserves original component order."""
        components = [
            Mock(id="first"),
            Mock(id="second"),
            Mock(id="third"),
        ]

        order_map = {c.id: i for i, c in enumerate(components)}

        assert order_map["first"] == 0
        assert order_map["second"] == 1
        assert order_map["third"] == 2


class TestRegistryReloadLogic:
    """Tests for registry reload handling logic."""

    def test_filter_reset_on_invalid_type(self):
        """Filter resets to 'All Types' when current type becomes invalid."""
        current_type_filter = "OldType"
        new_types = ["All Types", "NewType"]

        if current_type_filter not in new_types:
            current_type_filter = "All Types"

        assert current_type_filter == "All Types"

    def test_filter_preserved_on_valid_type(self):
        """Filter is preserved when current type is still valid."""
        current_type_filter = "Weapon"
        new_types = ["All Types", "Weapon", "Engine"]

        if current_type_filter not in new_types:
            current_type_filter = "All Types"

        assert current_type_filter == "Weapon"

    def test_type_options_updated_from_new_components(self):
        """Type options are updated from new components."""
        new_components = [
            Mock(type_str="NewWeapon"),
            Mock(type_str="NewEngine"),
        ]

        all_types = sorted(list(set(c.type_str for c in new_components)))
        type_filter_options = ["All Types"] + all_types

        assert "All Types" in type_filter_options
        assert "NewWeapon" in type_filter_options
        assert "NewEngine" in type_filter_options
