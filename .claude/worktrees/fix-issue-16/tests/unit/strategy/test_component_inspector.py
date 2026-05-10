"""
Tests for ComponentInspector utility.

PROJ-108 Phase 3: Tests for consolidated component/ability inspection functions.
"""
import pytest
from unittest.mock import Mock

from game.strategy.services.component_inspector import (
    get_component_abilities,
    iterate_design_components,
    ship_has_ability,
    find_ship_with_ability,
    count_ability,
)


class TestGetComponentAbilities:
    """Tests for get_component_abilities function."""

    def test_none_returns_empty_dict(self):
        """get_component_abilities(None) returns empty dict."""
        result = get_component_abilities(None)
        assert result == {}

    def test_dict_with_abilities(self):
        """get_component_abilities extracts abilities from dict."""
        comp_def = {"abilities": {"ColonyPod": {"planet_type": "standard"}}}
        result = get_component_abilities(comp_def)
        assert result == {"ColonyPod": {"planet_type": "standard"}}

    def test_dict_without_abilities(self):
        """get_component_abilities returns empty dict when no abilities key."""
        comp_def = {"id": "armor", "hp": 100}
        result = get_component_abilities(comp_def)
        assert result == {}

    def test_component_object_with_abilities(self):
        """get_component_abilities uses getattr for Component objects."""
        comp_obj = Mock()
        comp_obj.abilities = {"DestroyPlanet": {"cooldown": 5}}
        result = get_component_abilities(comp_obj)
        assert result == {"DestroyPlanet": {"cooldown": 5}}

    def test_component_object_without_abilities(self):
        """get_component_abilities returns empty dict for object without abilities."""
        comp_obj = Mock(spec=['id', 'hp'])  # No 'abilities' attribute
        result = get_component_abilities(comp_obj)
        assert result == {}


class TestIterateDesignComponents:
    """Tests for iterate_design_components function."""

    def test_yields_correct_tuples_multi_layer(self):
        """iterate_design_components yields correct tuples for multi-layer design."""
        design_data = {
            "layers": {
                "hull": [{"id": "comp_a"}],
                "internal": [{"id": "comp_b"}, {"id": "comp_c"}],
            }
        }
        registry = {
            "comp_a": {"abilities": {"AbilityA": {}}},
            "comp_b": {"abilities": {"AbilityB": {}}},
            "comp_c": {"abilities": {}},
        }

        results = list(iterate_design_components(design_data, registry))

        assert len(results) == 3

        # Find comp_a result
        comp_a_result = next(r for r in results if r[0].get('id') == 'comp_a')
        assert comp_a_result[1] == {"abilities": {"AbilityA": {}}}
        assert comp_a_result[2] == {"AbilityA": {}}

        # Find comp_b result
        comp_b_result = next(r for r in results if r[0].get('id') == 'comp_b')
        assert comp_b_result[2] == {"AbilityB": {}}

    def test_skips_non_list_layers(self):
        """iterate_design_components skips layers that aren't lists."""
        design_data = {
            "layers": {
                "hull": [{"id": "comp_a"}],
                "metadata": {"some": "data"},  # Not a list
                "internal": [{"id": "comp_b"}],
            }
        }
        registry = {
            "comp_a": {"abilities": {}},
            "comp_b": {"abilities": {}},
        }

        results = list(iterate_design_components(design_data, registry))

        # Should only get 2 components, skipping the metadata layer
        assert len(results) == 2
        ids = [r[0].get('id') for r in results]
        assert 'comp_a' in ids
        assert 'comp_b' in ids

    def test_handles_missing_component_in_registry(self):
        """iterate_design_components handles components not in registry."""
        design_data = {
            "layers": {
                "hull": [{"id": "unknown_comp"}],
            }
        }
        registry = {}  # Empty registry

        results = list(iterate_design_components(design_data, registry))

        assert len(results) == 1
        comp_entry, comp_def, abilities = results[0]
        assert comp_entry == {"id": "unknown_comp"}
        assert comp_def is None
        assert abilities == {}

    def test_empty_design_data(self):
        """iterate_design_components handles empty design data."""
        results = list(iterate_design_components({}, {}))
        assert results == []

        results = list(iterate_design_components({"layers": {}}, {}))
        assert results == []


class TestShipHasAbility:
    """Tests for ship_has_ability function."""

    def test_returns_true_when_ability_present(self):
        """ship_has_ability returns True when ability is found."""
        ship = Mock()
        ship.design_data = {
            "layers": {
                "hull": [{"id": "planet_cracker"}]
            }
        }
        registry = {
            "planet_cracker": {"abilities": {"DestroyPlanet": {}}}
        }

        result = ship_has_ability(ship, "DestroyPlanet", registry)
        assert result is True

    def test_returns_false_when_ability_absent(self):
        """ship_has_ability returns False when ability is not found."""
        ship = Mock()
        ship.design_data = {
            "layers": {
                "hull": [{"id": "armor"}]
            }
        }
        registry = {
            "armor": {"abilities": {"Protection": {}}}
        }

        result = ship_has_ability(ship, "DestroyPlanet", registry)
        assert result is False

class TestFindShipWithAbility:
    """Tests for find_ship_with_ability function."""

    def test_returns_correct_ship_from_list(self):
        """find_ship_with_ability returns first ship with ability."""
        ship1 = Mock()
        ship1.name = "Fighter"
        ship1.design_data = {"layers": {"hull": [{"id": "armor"}]}}

        ship2 = Mock()
        ship2.name = "Destroyer"
        ship2.design_data = {"layers": {"hull": [{"id": "colony_pod"}]}}

        ship3 = Mock()
        ship3.name = "Transport"
        ship3.design_data = {"layers": {"hull": [{"id": "colony_pod"}]}}

        registry = {
            "armor": {"abilities": {}},
            "colony_pod": {"abilities": {"ColonyPod": {"planet_type": "standard"}}},
        }

        result = find_ship_with_ability([ship1, ship2, ship3], "ColonyPod", registry)
        assert result is ship2  # First ship with ability

    def test_returns_none_when_no_match(self):
        """find_ship_with_ability returns None when no ship has ability."""
        ship1 = Mock()
        ship1.design_data = {"layers": {"hull": [{"id": "armor"}]}}

        ship2 = Mock()
        ship2.design_data = {"layers": {"hull": [{"id": "engine"}]}}

        registry = {
            "armor": {"abilities": {}},
            "engine": {"abilities": {"Thrust": {}}},
        }

        result = find_ship_with_ability([ship1, ship2], "ColonyPod", registry)
        assert result is None

    def test_handles_empty_list(self):
        """find_ship_with_ability handles empty ship list."""
        result = find_ship_with_ability([], "SomeAbility", {})
        assert result is None


class TestCountAbility:
    """Tests for count_ability function."""

    def test_returns_correct_count_for_multiple_components(self):
        """count_ability returns correct count for multiple components with ability."""
        ship = Mock()
        ship.design_data = {
            "layers": {
                "external": [
                    {"id": "weapon_a"},
                    {"id": "weapon_b"},
                    {"id": "armor"},
                ],
                "internal": [
                    {"id": "weapon_c"},
                ],
            }
        }
        registry = {
            "weapon_a": {"abilities": {"Damage": {}}},
            "weapon_b": {"abilities": {"Damage": {}}},
            "weapon_c": {"abilities": {"Damage": {}}},
            "armor": {"abilities": {"Protection": {}}},
        }

        result = count_ability(ship, "Damage", registry)
        assert result == 3

    def test_returns_zero_when_no_ability(self):
        """count_ability returns 0 when no components have ability."""
        ship = Mock()
        ship.design_data = {
            "layers": {
                "hull": [{"id": "armor"}]
            }
        }
        registry = {
            "armor": {"abilities": {"Protection": {}}}
        }

        result = count_ability(ship, "DestroyPlanet", registry)
        assert result == 0

    def test_handles_empty_design(self):
        """count_ability handles ship with no components."""
        ship = Mock()
        ship.design_data = {"layers": {}}

        result = count_ability(ship, "SomeAbility", {})
        assert result == 0
