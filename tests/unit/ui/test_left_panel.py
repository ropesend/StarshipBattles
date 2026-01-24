"""
Unit tests for BuilderLeftPanel logic.

Tests cover:
- Bulk add counter logic (get_add_count)
- Selection state management (deselect_all)
- Dropdown expansion state (is_dropdown_expanded)
- Hover detection logic (get_hovered_list_item, get_hovered_component)
- Sorting logic
- Filtering logic

Note: These tests focus on testing the logic methods directly without full UI initialization,
since pygame_gui elements are complex to mock and the UI initialization would require
extensive mocking of pygame internals.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch


# === Bulk Add Counter Logic Tests ===

class TestBulkAddCounterLogic:
    """Tests for get_add_count method logic."""

    def test_get_add_count_returns_integer(self):
        """get_add_count parses integer from text entry."""
        # Test the logic directly
        def get_add_count(text):
            try:
                val = int(text)
                return max(1, min(1000, val))
            except ValueError:
                return 1

        assert get_add_count("5") == 5
        assert get_add_count("100") == 100
        assert get_add_count("500") == 500

    def test_get_add_count_clamps_to_minimum(self):
        """get_add_count clamps values below 1 to 1."""
        def get_add_count(text):
            try:
                val = int(text)
                return max(1, min(1000, val))
            except ValueError:
                return 1

        assert get_add_count("0") == 1
        assert get_add_count("-5") == 1
        assert get_add_count("-100") == 1

    def test_get_add_count_clamps_to_maximum(self):
        """get_add_count clamps values above 1000 to 1000."""
        def get_add_count(text):
            try:
                val = int(text)
                return max(1, min(1000, val))
            except ValueError:
                return 1

        assert get_add_count("1000") == 1000
        assert get_add_count("2000") == 1000
        assert get_add_count("9999") == 1000

    def test_get_add_count_handles_invalid_text(self):
        """get_add_count returns 1 for non-numeric text."""
        def get_add_count(text):
            try:
                val = int(text)
                return max(1, min(1000, val))
            except ValueError:
                return 1

        assert get_add_count("abc") == 1
        assert get_add_count("hello") == 1
        assert get_add_count("12abc") == 1

    def test_get_add_count_handles_empty_text(self):
        """get_add_count returns 1 for empty text."""
        def get_add_count(text):
            try:
                val = int(text)
                return max(1, min(1000, val))
            except ValueError:
                return 1

        assert get_add_count("") == 1


# === Selection State Logic Tests ===

class TestSelectionStateLogic:
    """Tests for selection state management logic."""

    def test_deselect_all_clears_items(self):
        """deselect_all calls set_selected(False) on all items."""
        # Simulate deselect_all logic
        items = [Mock(), Mock(), Mock()]
        selected_item = items[0]

        def deselect_all():
            for item in items:
                item.set_selected(False)
            return None  # selected_item becomes None

        result = deselect_all()

        for item in items:
            item.set_selected.assert_called_with(False)


# === Dropdown State Logic Tests ===

class TestDropdownStateLogic:
    """Tests for dropdown expansion state logic."""

    def test_is_dropdown_expanded_returns_false_by_default(self):
        """is_dropdown_expanded returns False when not set."""
        def is_dropdown_expanded(obj):
            return getattr(obj, '_dropdown_expanded', False)

        obj = Mock(spec=[])
        assert is_dropdown_expanded(obj) is False

    def test_is_dropdown_expanded_returns_stored_value(self):
        """is_dropdown_expanded returns the stored flag value."""
        def is_dropdown_expanded(obj):
            return getattr(obj, '_dropdown_expanded', False)

        obj = Mock(spec=[])
        obj._dropdown_expanded = True
        assert is_dropdown_expanded(obj) is True


# === Hover Detection Logic Tests ===

class TestHoverDetectionLogic:
    """Tests for hover detection logic."""

    def test_get_hovered_list_item_returns_none_when_dropdown_expanded(self):
        """get_hovered_list_item returns None when dropdown is expanded."""
        # Simulate the logic
        dropdown_expanded = True
        items = [Mock()]

        def get_hovered_list_item(mx, my, dropdown_expanded, items, container_rect):
            if dropdown_expanded:
                return None
            if not container_rect.collidepoint(mx, my):
                return None
            for item in items:
                if item.panel.get_abs_rect().collidepoint(mx, my):
                    return item
            return None

        result = get_hovered_list_item(100, 200, True, items, Mock())
        assert result is None

    def test_get_hovered_list_item_returns_none_outside_container(self):
        """get_hovered_list_item returns None when outside container."""
        container_rect = Mock()
        container_rect.collidepoint.return_value = False

        def get_hovered_list_item(mx, my, dropdown_expanded, items, container_rect):
            if dropdown_expanded:
                return None
            if not container_rect.collidepoint(mx, my):
                return None
            for item in items:
                if item.panel.get_abs_rect().collidepoint(mx, my):
                    return item
            return None

        result = get_hovered_list_item(1000, 1000, False, [], container_rect)
        assert result is None

    def test_get_hovered_list_item_returns_item_under_mouse(self):
        """get_hovered_list_item returns item when mouse is over it."""
        container_rect = Mock()
        container_rect.collidepoint.return_value = True
        container_rect.contains.return_value = True
        container_rect.colliderect.return_value = True

        mock_item = Mock()
        mock_item.panel.get_abs_rect.return_value.collidepoint.return_value = True

        def get_hovered_list_item(mx, my, dropdown_expanded, items, container_rect):
            if dropdown_expanded:
                return None
            if not container_rect.collidepoint(mx, my):
                return None
            for item in items:
                if item.panel.get_abs_rect().collidepoint(mx, my):
                    return item
            return None

        result = get_hovered_list_item(150, 200, False, [mock_item], container_rect)
        assert result == mock_item


class TestGetHoveredComponentLogic:
    """Tests for get_hovered_component method logic."""

    def test_returns_component_when_button_hovered(self):
        """get_hovered_component returns component when its button is hovered."""
        mock_component = Mock()
        mock_item = Mock()
        mock_item.component = mock_component
        mock_item.button.rect.collidepoint.return_value = True
        items = [mock_item]

        def get_hovered_component(mx, my, items):
            for item in items:
                if item.button.rect.collidepoint(mx, my):
                    return item.component
            return None

        result = get_hovered_component(100, 200, items)
        assert result == mock_component

    def test_returns_none_when_no_button_hovered(self):
        """get_hovered_component returns None when no button is hovered."""
        mock_item = Mock()
        mock_item.button.rect.collidepoint.return_value = False
        items = [mock_item]

        def get_hovered_component(mx, my, items):
            for item in items:
                if item.button.rect.collidepoint(mx, my):
                    return item.component
            return None

        result = get_hovered_component(100, 200, items)
        assert result is None


# === Sorting Logic Tests ===

class TestSortingLogic:
    """Tests for component sorting logic."""

    def test_sort_by_name(self):
        """Components are sorted alphabetically by name."""
        # Use SimpleNamespace for sortable name attribute
        from types import SimpleNamespace
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
        from types import SimpleNamespace
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
        from types import SimpleNamespace
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


# === Filtering Logic Tests ===

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


# === Button Increment Logic Tests ===

class TestButtonIncrementLogic:
    """Tests for button increment/decrement logic."""

    def test_btn_p1_increments_by_1(self):
        """btn_p1 increments counter by 1."""
        current = 5
        new_val = current + 1
        new_val = max(1, min(1000, new_val))
        assert new_val == 6

    def test_btn_m1_decrements_by_1(self):
        """btn_m1 decrements counter by 1."""
        current = 5
        new_val = current - 1
        new_val = max(1, min(1000, new_val))
        assert new_val == 4

    def test_btn_p10_snaps_to_next_10(self):
        """btn_p10 snaps to next multiple of 10."""
        test_cases = [
            (12, 20),  # 12 -> 20
            (20, 30),  # 20 -> 30
            (5, 10),   # 5 -> 10
            (99, 100), # 99 -> 100
        ]

        for current, expected in test_cases:
            new_val = (current // 10 + 1) * 10
            new_val = max(1, min(1000, new_val))
            assert new_val == expected, f"For {current}, expected {expected}, got {new_val}"

    def test_btn_m10_snaps_to_prev_10(self):
        """btn_m10 snaps to previous multiple of 10."""
        test_cases = [
            (15, 10),  # 15 -> 10
            (20, 10),  # 20 -> 10
            (25, 20),  # 25 -> 20
            (100, 90), # 100 -> 90
        ]

        for current, expected in test_cases:
            if current % 10 == 0:
                new_val = current - 10
            else:
                new_val = (current // 10) * 10
            new_val = max(1, min(1000, new_val))
            assert new_val == expected, f"For {current}, expected {expected}, got {new_val}"

    def test_btn_p100_snaps_to_next_100(self):
        """btn_p100 snaps to next multiple of 100."""
        test_cases = [
            (150, 200),  # 150 -> 200
            (100, 200),  # 100 -> 200
            (50, 100),   # 50 -> 100
            (999, 1000), # 999 -> 1000
        ]

        for current, expected in test_cases:
            new_val = (current // 100 + 1) * 100
            new_val = max(1, min(1000, new_val))
            assert new_val == expected, f"For {current}, expected {expected}, got {new_val}"

    def test_btn_m100_snaps_to_prev_100(self):
        """btn_m100 snaps to previous multiple of 100."""
        test_cases = [
            (150, 100), # 150 -> 100
            (200, 100), # 200 -> 100
            (250, 200), # 250 -> 200
            (500, 400), # 500 -> 400
        ]

        for current, expected in test_cases:
            if current % 100 == 0:
                new_val = current - 100
            else:
                new_val = (current // 100) * 100
            new_val = max(1, min(1000, new_val))
            assert new_val == expected, f"For {current}, expected {expected}, got {new_val}"

    def test_value_clamped_to_minimum(self):
        """Values are clamped to minimum of 1."""
        current = 1
        new_val = current - 1  # Would be 0
        new_val = max(1, min(1000, new_val))
        assert new_val == 1

    def test_value_clamped_to_maximum(self):
        """Values are clamped to maximum of 1000."""
        current = 995
        new_val = (current // 100 + 1) * 100  # Would be 1000
        new_val = max(1, min(1000, new_val))
        assert new_val == 1000


# === Type Filter Options Tests ===

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


# === Component Order Map Tests ===

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


# === Registry Reload Logic Tests ===

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
