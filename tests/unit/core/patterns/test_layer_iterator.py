"""
Tests for LayerIterator utility.

PROJ-204 Phase 1: Tests for layer iteration patterns extracted from strategy layer.
"""

import pytest
from game.core.patterns.layer_iterator import (
    iter_components,
    iter_layers_and_components,
    get_component_id,
    iter_components_with_ids,
    generate_component_key,
    iter_keyed_components,
)


class TestGetComponentId:
    """Tests for get_component_id helper."""

    def test_string_component(self):
        """String component returns itself as ID."""
        assert get_component_id("bridge") == "bridge"

    def test_dict_component_with_id(self):
        """Dict component returns 'id' field."""
        comp = {"id": "reactor_core", "modifiers": []}
        assert get_component_id(comp) == "reactor_core"

    def test_dict_component_without_id(self):
        """Dict component without 'id' returns empty string."""
        comp = {"modifiers": [], "abilities": {}}
        assert get_component_id(comp) == ""

    def test_none_component(self):
        """None component returns empty string."""
        assert get_component_id(None) == ""

    def test_invalid_type(self):
        """Invalid type returns empty string."""
        assert get_component_id(123) == ""
        assert get_component_id([]) == ""


class TestIterComponents:
    """Tests for iter_components function."""

    def test_empty_layers(self):
        """Empty layers dict yields nothing."""
        design_data = {"layers": {}}
        result = list(iter_components(design_data))
        assert result == []

    def test_no_layers_key(self):
        """Missing layers key yields nothing."""
        design_data = {}
        result = list(iter_components(design_data))
        assert result == []

    def test_list_format_layers(self):
        """List format layers yield components directly."""
        design_data = {
            "layers": {
                "CORE": [{"id": "bridge"}, {"id": "reactor"}],
                "INNER": [{"id": "armor_plate"}],
            }
        }
        result = list(iter_components(design_data))
        assert len(result) == 3
        assert result[0] == {"id": "bridge"}
        assert result[1] == {"id": "reactor"}
        assert result[2] == {"id": "armor_plate"}

    def test_dict_format_layers_with_components_key(self):
        """Dict format with 'components' key yields components."""
        design_data = {
            "layers": {
                "CORE": {"components": [{"id": "bridge"}, {"id": "reactor"}]},
                "INNER": {"components": [{"id": "armor_plate"}]},
            }
        }
        result = list(iter_components(design_data))
        assert len(result) == 3
        assert result[0] == {"id": "bridge"}
        assert result[1] == {"id": "reactor"}
        assert result[2] == {"id": "armor_plate"}

    def test_string_components(self):
        """String components are yielded as-is."""
        design_data = {
            "layers": {
                "CORE": ["bridge", "reactor"],
            }
        }
        result = list(iter_components(design_data))
        assert len(result) == 2
        assert result[0] == "bridge"
        assert result[1] == "reactor"

    def test_mixed_formats_across_layers(self):
        """Different layers may have different formats."""
        design_data = {
            "layers": {
                "CORE": [{"id": "bridge"}],  # list format
                "INNER": {"components": [{"id": "armor"}]},  # dict format
            }
        }
        result = list(iter_components(design_data))
        assert len(result) == 2
        assert result[0] == {"id": "bridge"}
        assert result[1] == {"id": "armor"}

    def test_invalid_layer_format_skipped(self):
        """Invalid layer formats are skipped silently."""
        design_data = {
            "layers": {
                "CORE": [{"id": "bridge"}],
                "INVALID": "not_a_valid_format",
                "OUTER": None,
            }
        }
        result = list(iter_components(design_data))
        assert len(result) == 1
        assert result[0] == {"id": "bridge"}

    def test_empty_components_list(self):
        """Empty components list yields nothing for that layer."""
        design_data = {
            "layers": {
                "CORE": [],
                "INNER": [{"id": "armor"}],
            }
        }
        result = list(iter_components(design_data))
        assert len(result) == 1

    def test_dict_format_missing_components_key(self):
        """Dict format without 'components' key yields nothing."""
        design_data = {
            "layers": {
                "CORE": {"other_key": "value"},
            }
        }
        result = list(iter_components(design_data))
        assert result == []


class TestIterLayersAndComponents:
    """Tests for iter_layers_and_components function."""

    def test_yields_layer_name_tuples(self):
        """Yields (layer_name, component) tuples."""
        design_data = {
            "layers": {
                "CORE": [{"id": "bridge"}],
                "INNER": [{"id": "armor"}],
            }
        }
        result = list(iter_layers_and_components(design_data))
        assert len(result) == 2
        assert result[0] == ("CORE", {"id": "bridge"})
        assert result[1] == ("INNER", {"id": "armor"})

    def test_multiple_components_per_layer(self):
        """Multiple components in same layer share layer name."""
        design_data = {
            "layers": {
                "CORE": [{"id": "bridge"}, {"id": "reactor"}, {"id": "computer"}],
            }
        }
        result = list(iter_layers_and_components(design_data))
        assert len(result) == 3
        assert all(layer == "CORE" for layer, comp in result)

    def test_empty_layers(self):
        """Empty layers dict yields nothing."""
        design_data = {"layers": {}}
        result = list(iter_layers_and_components(design_data))
        assert result == []


class TestIterComponentsWithIds:
    """Tests for iter_components_with_ids function."""

    def test_yields_component_with_id(self):
        """Yields (component_entry, component_id) tuples."""
        design_data = {
            "layers": {
                "CORE": [{"id": "bridge"}, {"id": "reactor"}],
            }
        }
        result = list(iter_components_with_ids(design_data))
        assert len(result) == 2
        assert result[0] == ({"id": "bridge"}, "bridge")
        assert result[1] == ({"id": "reactor"}, "reactor")

    def test_string_components(self):
        """String components have themselves as ID."""
        design_data = {
            "layers": {
                "CORE": ["bridge", "reactor"],
            }
        }
        result = list(iter_components_with_ids(design_data))
        assert len(result) == 2
        assert result[0] == ("bridge", "bridge")
        assert result[1] == ("reactor", "reactor")

    def test_mixed_components(self):
        """Mixed dict and string components work."""
        design_data = {
            "layers": {
                "CORE": [{"id": "bridge"}, "reactor_simple"],
            }
        }
        result = list(iter_components_with_ids(design_data))
        assert len(result) == 2
        assert result[0] == ({"id": "bridge"}, "bridge")
        assert result[1] == ("reactor_simple", "reactor_simple")

    def test_component_without_id_has_empty_string(self):
        """Dict component without 'id' has empty string ID."""
        design_data = {
            "layers": {
                "CORE": [{"abilities": {}}],
            }
        }
        result = list(iter_components_with_ids(design_data))
        assert len(result) == 1
        assert result[0] == ({"abilities": {}}, "")


class TestGenerateComponentKey:
    """Tests for generate_component_key."""

    def test_basic_key(self):
        assert generate_component_key("OUTER", 0, "reactor") == "OUTER:0:reactor"

    def test_duplicate_components_get_different_keys(self):
        key1 = generate_component_key("OUTER", 0, "stabilizer")
        key2 = generate_component_key("OUTER", 1, "stabilizer")
        assert key1 != key2
        assert key1 == "OUTER:0:stabilizer"
        assert key2 == "OUTER:1:stabilizer"

    def test_different_layers_different_keys(self):
        key1 = generate_component_key("CORE", 0, "reactor")
        key2 = generate_component_key("OUTER", 0, "reactor")
        assert key1 != key2


class TestIterKeyedComponents:
    """Tests for iter_keyed_components."""

    def test_single_component(self):
        design_data = {
            "layers": {"CORE": [{"id": "bridge"}]}
        }
        result = list(iter_keyed_components(design_data))
        assert len(result) == 1
        key, layer, comp = result[0]
        assert key == "CORE:0:bridge"
        assert layer == "CORE"
        assert comp == {"id": "bridge"}

    def test_duplicate_components_get_unique_keys(self):
        design_data = {
            "layers": {
                "OUTER": [
                    {"id": "geologic_stabilizer_system"},
                    {"id": "geologic_stabilizer_system"},
                ]
            }
        }
        result = list(iter_keyed_components(design_data))
        assert len(result) == 2
        assert result[0][0] == "OUTER:0:geologic_stabilizer_system"
        assert result[1][0] == "OUTER:1:geologic_stabilizer_system"

    def test_multiple_layers(self):
        design_data = {
            "layers": {
                "CORE": [{"id": "bridge"}],
                "OUTER": [{"id": "shield"}],
            }
        }
        result = list(iter_keyed_components(design_data))
        assert len(result) == 2
        assert result[0][0] == "CORE:0:bridge"
        assert result[1][0] == "OUTER:0:shield"

    def test_empty_layers(self):
        design_data = {"layers": {}}
        result = list(iter_keyed_components(design_data))
        assert result == []

    def test_string_components(self):
        design_data = {"layers": {"CORE": ["bridge", "reactor"]}}
        result = list(iter_keyed_components(design_data))
        assert result[0][0] == "CORE:0:bridge"
        assert result[1][0] == "CORE:1:reactor"
