"""
Tests for ComponentInspector utility.

PROJ-108 Phase 3: Tests for consolidated component/ability inspection functions.
"""
import pytest
from unittest.mock import Mock

from game.strategy.services.component_inspector import (
    extract_abilities_from_component,
    get_component_abilities,
    get_ability_list,
    iter_facility_ability_entries,
    iterate_design_components,
    ship_has_ability,
    find_ship_with_ability,
    count_ability,
    list_ship_abilities,
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


class TestExtractAbilitiesFromComponent:
    """Tests for design-entry ability extraction."""

    def test_inline_abilities_take_precedence(self):
        comp_entry = {
            "id": "registry_component",
            "abilities": {"InlineAbility": {"value": 3}},
        }
        registry = {
            "registry_component": {"abilities": {"RegistryAbility": {}}},
        }

        result = extract_abilities_from_component(comp_entry, registry)

        assert result == {"InlineAbility": {"value": 3}}

    def test_dict_entry_uses_registries_components_lookup(self):
        registries = Mock()
        registries.components = {
            "warp_drive": {
                "abilities": {
                    "WarpJump": {"max_tonnage": 1500, "resource": "fuel"}
                }
            }
        }

        result = extract_abilities_from_component({"id": "warp_drive"}, registries)

        assert result == {
            "WarpJump": {"max_tonnage": 1500, "resource": "fuel"}
        }

    def test_string_entry_uses_plain_registry_lookup(self):
        registry = {
            "fuel_tank": {
                "abilities": {
                    "ResourceStorage": [{"resource": "fuel", "capacity": 50}]
                }
            }
        }

        result = extract_abilities_from_component("fuel_tank", registry)

        assert result == {
            "ResourceStorage": [{"resource": "fuel", "capacity": 50}]
        }

    def test_unknown_or_unregistered_component_returns_empty_dict(self):
        assert extract_abilities_from_component({"id": "missing"}, {}) == {}
        assert extract_abilities_from_component("missing", {}) == {}
        assert extract_abilities_from_component({"id": "missing"}, None) == {}


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


class TestListShipAbilities:
    """Tests for unique ability-name extraction."""

    def test_returns_unique_ability_names_across_components(self):
        ship = Mock()
        ship.design_data = {
            "layers": {
                "outer": [
                    {"id": "laser"},
                    {"id": "spare_laser"},
                    {"id": "fuel_tank"},
                ],
            }
        }
        registry = {
            "laser": {"abilities": {"BeamWeaponAbility": {}, "CrewRequired": 2}},
            "spare_laser": {"abilities": {"BeamWeaponAbility": {}}},
            "fuel_tank": {"abilities": {"ResourceStorage": {}}},
        }

        result = list_ship_abilities(ship, registry)

        assert set(result) == {
            "BeamWeaponAbility",
            "CrewRequired",
            "ResourceStorage",
        }


class TestGetAbilityList:
    """Tests for ability payload normalization."""

    def test_missing_ability_returns_empty_list(self):
        assert get_ability_list({}, "ResourceConsumption") == []

    def test_list_payload_passes_through(self):
        payload = [{"resource": "fuel"}, {"resource": "ammo"}]

        result = get_ability_list({"ResourceConsumption": payload}, "ResourceConsumption")

        assert result is payload

    def test_dict_payload_is_wrapped(self):
        payload = {"resource": "fuel", "amount": 1}

        result = get_ability_list({"ResourceConsumption": payload}, "ResourceConsumption")

        assert result == [payload]

    def test_scalar_payload_is_wrapped_as_value_dict(self):
        result = get_ability_list({"CrewRequired": 5}, "CrewRequired")

        assert result == [{"value": 5}]


class TestIterFacilityAbilityEntries:
    """PROJ-375 Task 2.1: tests for iter_facility_ability_entries."""

    def _facility(self, layers):
        facility = Mock()
        facility.design_data = {"layers": layers}
        return facility

    def test_no_components_yields_nothing(self):
        facility = self._facility({})
        assert list(iter_facility_ability_entries(facility, "WaterModifier")) == []

    def test_inline_dict_ability_yielded_once(self):
        comp = {"id": "c1", "abilities": {"WaterModifier": {"modification_rate": 0.5}}}
        facility = self._facility({"hull": [comp]})
        result = list(iter_facility_ability_entries(facility, "WaterModifier"))
        assert len(result) == 1
        out_comp, entry = result[0]
        assert out_comp is comp
        assert entry == {"modification_rate": 0.5}

    def test_inline_list_ability_yielded_per_entry(self):
        comp = {
            "id": "c1",
            "abilities": {
                "ResourceHarvester": [
                    {"resource_type": "metals", "base_harvest_rate": 1.0},
                    {"resource_type": "organics", "base_harvest_rate": 2.0},
                ]
            },
        }
        facility = self._facility({"core": [comp]})
        result = list(iter_facility_ability_entries(facility, "ResourceHarvester"))
        assert len(result) == 2
        assert result[0][1] == {"resource_type": "metals", "base_harvest_rate": 1.0}
        assert result[1][1] == {"resource_type": "organics", "base_harvest_rate": 2.0}
        assert result[0][0] is comp and result[1][0] is comp

    def test_scalar_ability_wrapped_as_value_dict(self):
        comp = {"id": "c1", "abilities": {"CrewRequired": 5}}
        facility = self._facility({"hull": [comp]})
        result = list(iter_facility_ability_entries(facility, "CrewRequired"))
        assert result == [(comp, {"value": 5})]

    def test_missing_ability_skipped(self):
        comp_a = {"id": "a", "abilities": {"WaterModifier": {"modification_rate": 0.1}}}
        comp_b = {"id": "b", "abilities": {"AtmosphereModifier": {"x": 1}}}
        facility = self._facility({"hull": [comp_a, comp_b]})
        result = list(iter_facility_ability_entries(facility, "WaterModifier"))
        assert len(result) == 1
        assert result[0][0] is comp_a

    def test_registry_lookup_by_id(self):
        comp = {"id": "shield_basic"}  # no inline abilities
        registries = {
            "shield_basic": {"abilities": {"PlanetaryShield": {"radius": 100}}}
        }
        facility = self._facility({"hull": [comp]})
        result = list(
            iter_facility_ability_entries(facility, "PlanetaryShield", registries)
        )
        assert len(result) == 1
        out_comp, entry = result[0]
        assert out_comp is comp
        assert entry == {"radius": 100}

    def test_string_component_uses_registry(self):
        registries = {"plain_id": {"abilities": {"LocalStorage": {"capacity": 50}}}}
        facility = self._facility({"hull": ["plain_id"]})
        result = list(
            iter_facility_ability_entries(facility, "LocalStorage", registries)
        )
        assert len(result) == 1
        comp, entry = result[0]
        assert comp == "plain_id"
        assert entry == {"capacity": 50}

    def test_list_with_non_dict_entries_wrapped(self):
        comp = {"id": "c1", "abilities": {"Tags": [42, "alpha"]}}
        facility = self._facility({"hull": [comp]})
        result = list(iter_facility_ability_entries(facility, "Tags"))
        assert result == [(comp, {"value": 42}), (comp, {"value": "alpha"})]

    def test_multiple_components_iterate_all(self):
        comp_a = {"id": "a", "abilities": {"WaterModifier": {"modification_rate": 0.1}}}
        comp_b = {"id": "b", "abilities": {"WaterModifier": {"modification_rate": 0.2}}}
        facility = self._facility({"hull": [comp_a, comp_b]})
        rates = [
            entry["modification_rate"]
            for _, entry in iter_facility_ability_entries(facility, "WaterModifier")
        ]
        assert sorted(rates) == [0.1, 0.2]
