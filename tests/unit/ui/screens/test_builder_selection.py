"""Tests for builder_selection module - component selection management."""

import pytest
from unittest.mock import MagicMock

from game.ui.screens.builder_selection import (
    normalize_selection,
    process_selection_change,
    get_primary_selection,
)


class MockComponent:
    """Mock component for testing."""

    def __init__(self, comp_id: str):
        self.id = comp_id


class MockShip:
    """Mock ship for testing."""

    def __init__(self):
        self.layers = {}

    def add_layer(self, layer_type, components):
        """Add a layer with components."""
        layer = MagicMock()
        layer.components = components
        self.layers[layer_type] = layer


class TestNormalizeSelection:
    """Tests for normalize_selection function."""

    def test_already_normalized_tuple_passes_through(self):
        """Verify 3-tuple selection items pass through unchanged."""
        ship = MockShip()
        comp = MockComponent("laser")
        selection = [("weapons", 0, comp)]

        result = normalize_selection(selection, ship)

        assert result == [("weapons", 0, comp)]

    def test_finds_component_in_ship_layers(self):
        """Verify component is found in ship layers."""
        comp = MockComponent("laser")
        ship = MockShip()
        ship.add_layer("weapons", [comp])

        result = normalize_selection([comp], ship)

        assert len(result) == 1
        assert result[0] == ("weapons", 0, comp)

    def test_finds_component_in_second_layer(self):
        """Verify component is found even if not in first layer."""
        comp = MockComponent("shield")
        ship = MockShip()
        ship.add_layer("weapons", [])
        ship.add_layer("defense", [comp])

        result = normalize_selection([comp], ship)

        assert len(result) == 1
        assert result[0] == ("defense", 0, comp)

    def test_handles_component_not_in_ship(self):
        """Verify unfound components get (None, -1, comp) tuple."""
        comp = MockComponent("template")
        ship = MockShip()
        ship.add_layer("weapons", [])

        result = normalize_selection([comp], ship)

        assert len(result) == 1
        assert result[0] == (None, -1, comp)

    def test_normalizes_multiple_components(self):
        """Verify multiple components are normalized."""
        comp1 = MockComponent("laser")
        comp2 = MockComponent("missile")
        ship = MockShip()
        ship.add_layer("weapons", [comp1, comp2])

        result = normalize_selection([comp1, comp2], ship)

        assert len(result) == 2
        assert result[0] == ("weapons", 0, comp1)
        assert result[1] == ("weapons", 1, comp2)

    def test_mixed_tuples_and_components(self):
        """Verify mix of tuples and components works."""
        comp1 = MockComponent("laser")
        comp2 = MockComponent("shield")
        ship = MockShip()
        ship.add_layer("defense", [comp2])

        selection = [("weapons", 0, comp1), comp2]
        result = normalize_selection(selection, ship)

        assert len(result) == 2
        assert result[0] == ("weapons", 0, comp1)
        assert result[1] == ("defense", 0, comp2)


class TestProcessSelectionChange:
    """Tests for process_selection_change function."""

    def test_none_clears_selection(self):
        """Verify None new_selection clears selection."""
        ship = MockShip()
        current = [("weapons", 0, MockComponent("laser"))]

        result, was_replaced = process_selection_change(current, None, ship)

        assert result == []
        assert was_replaced is False

    def test_none_with_append_keeps_selection(self):
        """Verify None with append=True keeps current selection."""
        ship = MockShip()
        comp = MockComponent("laser")
        current = [("weapons", 0, comp)]

        result, was_replaced = process_selection_change(current, None, ship, append=True)

        assert result == current
        assert was_replaced is False

    def test_single_item_wrapped_in_list(self):
        """Verify single non-list item is wrapped."""
        comp = MockComponent("laser")
        ship = MockShip()
        ship.add_layer("weapons", [comp])

        result, was_replaced = process_selection_change([], comp, ship)

        assert len(result) == 1
        assert result[0][2] is comp

    def test_replace_selection_without_append(self):
        """Verify selection is replaced without append flag."""
        comp1 = MockComponent("laser")
        comp2 = MockComponent("missile")
        ship = MockShip()
        ship.add_layer("weapons", [comp1, comp2])
        current = [("weapons", 0, comp1)]

        result, was_replaced = process_selection_change(current, [comp2], ship)

        assert len(result) == 1
        assert result[0][2] is comp2
        assert was_replaced is False

    def test_append_same_type_adds_item(self):
        """Verify append with same type adds item."""
        comp1 = MockComponent("laser")  # Same id
        comp2 = MockComponent("laser")  # Same id
        ship = MockShip()
        ship.add_layer("weapons", [comp1, comp2])
        current = [("weapons", 0, comp1)]

        result, was_replaced = process_selection_change(current, [comp2], ship, append=True)

        assert len(result) == 2
        assert comp1 in [r[2] for r in result]
        assert comp2 in [r[2] for r in result]
        assert was_replaced is False

    def test_append_different_type_replaces(self):
        """Verify append with different type replaces selection."""
        comp1 = MockComponent("laser")
        comp2 = MockComponent("shield")  # Different id
        ship = MockShip()
        ship.add_layer("weapons", [comp1])
        ship.add_layer("defense", [comp2])
        current = [("weapons", 0, comp1)]

        result, was_replaced = process_selection_change(current, [comp2], ship, append=True)

        assert len(result) == 1
        assert result[0][2] is comp2
        assert was_replaced is True

    def test_toggle_removes_existing_item(self):
        """Verify toggle removes already-selected item."""
        comp1 = MockComponent("laser")
        comp2 = MockComponent("laser")
        ship = MockShip()
        ship.add_layer("weapons", [comp1, comp2])
        current = [("weapons", 0, comp1), ("weapons", 1, comp2)]

        result, was_replaced = process_selection_change(current, [comp1], ship, append=True, toggle=True)

        assert len(result) == 1
        assert result[0][2] is comp2

    def test_toggle_without_append_has_no_effect(self):
        """Verify toggle without append just replaces."""
        comp1 = MockComponent("laser")
        comp2 = MockComponent("laser")
        ship = MockShip()
        ship.add_layer("weapons", [comp1, comp2])
        current = [("weapons", 0, comp1), ("weapons", 1, comp2)]

        # toggle=True but append=False
        result, was_replaced = process_selection_change(current, [comp1], ship, toggle=True)

        assert len(result) == 1
        assert result[0][2] is comp1

    def test_append_to_empty_selection(self):
        """Verify append to empty selection works."""
        comp = MockComponent("laser")
        ship = MockShip()
        ship.add_layer("weapons", [comp])

        result, was_replaced = process_selection_change([], [comp], ship, append=True)

        assert len(result) == 1
        assert result[0][2] is comp
        assert was_replaced is False

    def test_no_duplicate_items_on_append(self):
        """Verify same object not added twice on append."""
        comp = MockComponent("laser")
        ship = MockShip()
        ship.add_layer("weapons", [comp])
        current = [("weapons", 0, comp)]

        result, was_replaced = process_selection_change(current, [comp], ship, append=True)

        assert len(result) == 1

    def test_homogeneity_check_uses_definition_id(self):
        """Verify homogeneity uses component.id not object identity."""
        comp1 = MockComponent("laser")
        comp2 = MockComponent("laser")  # Same definition ID
        comp3 = MockComponent("missile")  # Different definition ID
        ship = MockShip()
        ship.add_layer("weapons", [comp1, comp2, comp3])
        current = [("weapons", 0, comp1)]

        # Same type should append
        result1, replaced1 = process_selection_change(current, [comp2], ship, append=True)
        assert len(result1) == 2
        assert replaced1 is False

        # Different type should replace
        result2, replaced2 = process_selection_change(current, [comp3], ship, append=True)
        assert len(result2) == 1
        assert replaced2 is True


class TestGetPrimarySelection:
    """Tests for get_primary_selection function."""

    def test_returns_last_item(self):
        """Verify last item in selection is returned."""
        comp1 = MockComponent("laser")
        comp2 = MockComponent("missile")
        selection = [("weapons", 0, comp1), ("weapons", 1, comp2)]

        result = get_primary_selection(selection)

        assert result == ("weapons", 1, comp2)

    def test_returns_none_for_empty_selection(self):
        """Verify None returned for empty selection."""
        result = get_primary_selection([])

        assert result is None

    def test_returns_single_item(self):
        """Verify single item selection works."""
        comp = MockComponent("laser")
        selection = [("weapons", 0, comp)]

        result = get_primary_selection(selection)

        assert result == ("weapons", 0, comp)
