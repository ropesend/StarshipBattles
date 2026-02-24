"""
Unit tests for ColonizePlanet and Harvester-related abilities.

Tests ColonizePlanet, ResourceHarvesterAbility, EmpireStorageAbility,
and SpaceShipyardAbility.
"""
import pytest
from unittest.mock import MagicMock

from game.core.exceptions import ValidationException
from game.simulation.components.abilities.colonize import ColonizePlanet
from game.simulation.components.abilities.harvester import (
    ResourceHarvesterAbility,
    EmpireStorageAbility,
    SpaceShipyardAbility,
)
from game.simulation.components.abilities.base import AbilityLayer, AbilityScope
from game.simulation.components.abilities.ui_colors import (
    HINT_COLONIZE,
    HINT_ACCURACY,
    HINT_SHIELD_CAP,
    HINT_DEFAULT,
)


# =============================================================================
# ColonizePlanet Tests
# =============================================================================


class TestColonizePlanet:
    """Tests for ColonizePlanet ability."""

    @pytest.fixture
    def mock_component(self):
        """Create a mock component."""
        return MagicMock()

    def test_init_with_string_shorthand(self, mock_component):
        """String shorthand sets planet_type directly."""
        ability = ColonizePlanet(mock_component, "ICE_DWARF")

        assert ability.planet_type == "ICE_DWARF"

    def test_init_with_dict_format(self, mock_component):
        """Dict format with planet_type key."""
        data = {"planet_type": "CONTINENTAL"}
        ability = ColonizePlanet(mock_component, data)

        assert ability.planet_type == "CONTINENTAL"

    def test_init_with_dict_missing_planet_type(self, mock_component):
        """Dict format without planet_type defaults to empty string."""
        data = {}
        ability = ColonizePlanet(mock_component, data)

        assert ability.planet_type == ""

    def test_init_with_other_type_converts_to_string(self, mock_component):
        """Non-string, non-dict data is converted to string."""
        ability = ColonizePlanet(mock_component, 123)

        assert ability.planet_type == "123"

    def test_layer_is_strategic(self, mock_component):
        """ColonizePlanet is a strategic-layer ability only."""
        ability = ColonizePlanet(mock_component, "BARREN")

        assert ability.layer == AbilityLayer.STRATEGIC
        assert ability.applies_to_layer(AbilityLayer.STRATEGIC)
        assert not ability.applies_to_layer(AbilityLayer.COMBAT)

    def test_allowed_scope_is_self_only(self, mock_component):
        """ColonizePlanet only affects SELF scope."""
        ability = ColonizePlanet(mock_component, "BARREN")

        assert ability.allowed_scopes == [AbilityScope.SELF]
        assert ability.scope == AbilityScope.SELF

    def test_stat_bindings_empty(self, mock_component):
        """ColonizePlanet has no stat bindings (marker ability)."""
        ability = ColonizePlanet(mock_component, "ARID")

        assert ability.STAT_BINDINGS == []

    def test_get_primary_value_returns_zero(self, mock_component):
        """Marker ability returns 0.0 for primary value."""
        ability = ColonizePlanet(mock_component, "PELAGIC")

        assert ability.get_primary_value() == 0.0

    def test_get_ui_rows_formats_planet_type(self, mock_component):
        """UI rows show formatted planet type with proper capitalization."""
        ability = ColonizePlanet(mock_component, "ICE_DWARF")

        rows = ability.get_ui_rows()

        assert len(rows) == 1
        assert rows[0]["label"] == "Colonizes"
        assert rows[0]["value"] == "Ice Dwarf"
        assert rows[0]["color_hint"] == HINT_COLONIZE

    def test_get_ui_rows_simple_planet_type(self, mock_component):
        """UI rows format single-word planet types correctly."""
        ability = ColonizePlanet(mock_component, "CONTINENTAL")

        rows = ability.get_ui_rows()

        assert rows[0]["value"] == "Continental"

    def test_get_ui_rows_multiple_underscores(self, mock_component):
        """UI rows handle planet types with multiple underscores."""
        # Edge case: hypothetical planet type with multiple underscores
        ability = ColonizePlanet(mock_component, "SOME_WEIRD_TYPE")

        rows = ability.get_ui_rows()

        assert rows[0]["value"] == "Some Weird Type"

    def test_all_supported_planet_types(self, mock_component):
        """Verify all documented planet types work correctly."""
        planet_types = [
            "CONTINENTAL", "ARID", "PELAGIC", "MAGMA", "CRYOPLANET",
            "BARREN", "JOVIAN", "ICE_GIANT", "CHTHONIAN", "ICE_DWARF",
            "PLANETOID"
        ]

        for planet_type in planet_types:
            ability = ColonizePlanet(mock_component, planet_type)
            assert ability.planet_type == planet_type
            rows = ability.get_ui_rows()
            assert len(rows) == 1
            assert rows[0]["label"] == "Colonizes"

    def test_scope_validation_rejects_invalid_scope(self, mock_component):
        """ColonizePlanet rejects scopes other than SELF."""
        data = {"planet_type": "CONTINENTAL", "scope": "sector"}

        with pytest.raises(ValidationException) as exc_info:
            ColonizePlanet(mock_component, data)

        # Verify context contains scope info
        assert exc_info.value.context.get("scope") == "sector"


# =============================================================================
# ResourceHarvesterAbility Tests
# =============================================================================


class TestResourceHarvesterAbility:
    """Tests for ResourceHarvesterAbility class."""

    @pytest.fixture
    def mock_component(self):
        """Create a mock component."""
        return MagicMock()

    def test_init_with_dict_data(self, mock_component):
        """Dict data sets resource_type and base_harvest_rate."""
        data = {"resource_type": "Metals", "base_harvest_rate": 10.5}
        ability = ResourceHarvesterAbility(mock_component, data)

        assert ability.resource_type == "Metals"
        assert ability.base_harvest_rate == 10.5

    def test_init_with_empty_dict(self, mock_component):
        """Empty dict uses default values."""
        data = {}
        ability = ResourceHarvesterAbility(mock_component, data)

        assert ability.resource_type == "Unknown"
        assert ability.base_harvest_rate == 0.0

    def test_init_with_non_dict_data(self, mock_component):
        """Non-dict data uses default values."""
        ability = ResourceHarvesterAbility(mock_component, "invalid")

        assert ability.resource_type == "Unknown"
        assert ability.base_harvest_rate == 0.0

    def test_init_partial_dict_uses_defaults(self, mock_component):
        """Partial dict uses defaults for missing keys."""
        data = {"resource_type": "Organics"}
        ability = ResourceHarvesterAbility(mock_component, data)

        assert ability.resource_type == "Organics"
        assert ability.base_harvest_rate == 0.0

    def test_stat_bindings_empty(self, mock_component):
        """ResourceHarvesterAbility has no stat bindings."""
        ability = ResourceHarvesterAbility(mock_component, {})

        assert ability.STAT_BINDINGS == []

    def test_get_primary_value_returns_harvest_rate(self, mock_component):
        """Primary value is the base harvest rate."""
        data = {"resource_type": "Crystals", "base_harvest_rate": 7.5}
        ability = ResourceHarvesterAbility(mock_component, data)

        assert ability.get_primary_value() == 7.5

    def test_get_primary_value_zero_rate(self, mock_component):
        """Primary value is zero when harvest rate is zero."""
        data = {"resource_type": "Crystals", "base_harvest_rate": 0.0}
        ability = ResourceHarvesterAbility(mock_component, data)

        assert ability.get_primary_value() == 0.0

    def test_get_ui_rows_shows_resource_and_rate(self, mock_component):
        """UI rows display resource type and harvest rate."""
        data = {"resource_type": "Metals", "base_harvest_rate": 15.0}
        ability = ResourceHarvesterAbility(mock_component, data)

        rows = ability.get_ui_rows()

        assert len(rows) == 2
        assert rows[0]["label"] == "Resource Type"
        assert rows[0]["value"] == "Metals"
        assert rows[0]["color_hint"] == HINT_COLONIZE
        assert rows[1]["label"] == "Harvest Rate"
        assert rows[1]["value"] == "15.0/turn"
        assert rows[1]["color_hint"] == HINT_ACCURACY

    def test_get_ui_rows_formats_decimal_rate(self, mock_component):
        """UI rows format decimal harvest rates correctly."""
        data = {"resource_type": "Organics", "base_harvest_rate": 3.75}
        ability = ResourceHarvesterAbility(mock_component, data)

        rows = ability.get_ui_rows()

        assert rows[1]["value"] == "3.8/turn"  # Formatted to 1 decimal

    def test_various_resource_types(self, mock_component):
        """Various resource types are stored correctly."""
        resource_types = ["Metals", "Organics", "Crystals", "Fuel", "RareEarths"]

        for resource_type in resource_types:
            data = {"resource_type": resource_type, "base_harvest_rate": 5.0}
            ability = ResourceHarvesterAbility(mock_component, data)
            assert ability.resource_type == resource_type


# =============================================================================
# EmpireStorageAbility Tests
# =============================================================================


class TestEmpireStorageAbility:
    """Tests for EmpireStorageAbility class."""

    @pytest.fixture
    def mock_component(self):
        """Create a mock component with stats."""
        component = MagicMock()
        component.stats = {}
        return component

    def test_init_with_dict_data(self, mock_component):
        """Dict data sets resource_type and capacity."""
        data = {"resource_type": "Metals", "capacity": 5000.0}
        ability = EmpireStorageAbility(mock_component, data)

        assert ability.resource_type == "Metals"
        assert ability.capacity == 5000.0
        assert ability._base_capacity == 5000.0

    def test_init_with_empty_dict(self, mock_component):
        """Empty dict uses default values."""
        data = {}
        ability = EmpireStorageAbility(mock_component, data)

        assert ability.resource_type == ""
        assert ability.capacity == 0.0
        assert ability._base_capacity == 0.0

    def test_init_with_non_dict_data(self, mock_component):
        """Non-dict data uses default values."""
        ability = EmpireStorageAbility(mock_component, 12345)

        assert ability.resource_type == ""
        assert ability.capacity == 0.0

    def test_init_partial_dict_uses_defaults(self, mock_component):
        """Partial dict uses defaults for missing keys."""
        data = {"capacity": 10000.0}
        ability = EmpireStorageAbility(mock_component, data)

        assert ability.resource_type == ""
        assert ability.capacity == 10000.0

    def test_stat_bindings_empty(self, mock_component):
        """EmpireStorageAbility has no stat bindings."""
        ability = EmpireStorageAbility(mock_component, {})

        assert ability.STAT_BINDINGS == []

    def test_get_primary_value_returns_capacity(self, mock_component):
        """Primary value is the storage capacity."""
        data = {"resource_type": "Organics", "capacity": 2500.0}
        ability = EmpireStorageAbility(mock_component, data)

        assert ability.get_primary_value() == 2500.0

    def test_recalculate_applies_storage_modifier(self, mock_component):
        """Recalculate applies storage_mult modifier."""
        data = {"resource_type": "Metals", "capacity": 1000.0}
        ability = EmpireStorageAbility(mock_component, data)
        mock_component.stats = {"storage_mult": 1.5}

        ability.recalculate()

        assert ability.capacity == 1500.0
        assert ability._base_capacity == 1000.0  # Base unchanged

    def test_recalculate_without_modifier(self, mock_component):
        """Recalculate without modifier uses default multiplier of 1.0."""
        data = {"resource_type": "Crystals", "capacity": 3000.0}
        ability = EmpireStorageAbility(mock_component, data)
        mock_component.stats = {}

        ability.recalculate()

        assert ability.capacity == 3000.0

    def test_recalculate_multiple_times(self, mock_component):
        """Multiple recalculations use base capacity."""
        data = {"resource_type": "Fuel", "capacity": 2000.0}
        ability = EmpireStorageAbility(mock_component, data)

        # First recalculation with 1.5x modifier
        mock_component.stats = {"storage_mult": 1.5}
        ability.recalculate()
        assert ability.capacity == 3000.0

        # Second recalculation with different modifier
        mock_component.stats = {"storage_mult": 2.0}
        ability.recalculate()
        assert ability.capacity == 4000.0  # Based on _base_capacity, not previous capacity

    def test_get_ui_rows_shows_resource_and_capacity(self, mock_component):
        """UI rows display resource type and storage capacity."""
        data = {"resource_type": "Metals", "capacity": 10000.0}
        ability = EmpireStorageAbility(mock_component, data)

        rows = ability.get_ui_rows()

        assert len(rows) == 2
        assert rows[0]["label"] == "Resource Type"
        assert rows[0]["value"] == "Metals"
        assert rows[0]["color_hint"] == HINT_COLONIZE
        assert rows[1]["label"] == "Storage Capacity"
        assert rows[1]["value"] == "10,000"
        assert rows[1]["color_hint"] == HINT_ACCURACY

    def test_get_ui_rows_formats_large_capacity(self, mock_component):
        """UI rows format large capacities with thousands separator."""
        data = {"resource_type": "RareEarths", "capacity": 1234567.0}
        ability = EmpireStorageAbility(mock_component, data)

        rows = ability.get_ui_rows()

        assert rows[1]["value"] == "1,234,567"


# =============================================================================
# SpaceShipyardAbility Tests
# =============================================================================


class TestSpaceShipyardAbility:
    """Tests for SpaceShipyardAbility class."""

    @pytest.fixture
    def mock_component(self):
        """Create a mock component."""
        return MagicMock()

    def test_init_with_dict_data(self, mock_component):
        """Dict data sets construction_speed_bonus, max_ship_mass, production_rates."""
        data = {
            "construction_speed_bonus": 1.5,
            "max_ship_mass": 200000,
            "production_rates": {"Metals": 100.0, "Crystals": 50.0}
        }
        ability = SpaceShipyardAbility(mock_component, data)

        assert ability.construction_speed_bonus == 1.5
        assert ability.max_ship_mass == 200000
        assert ability.production_rates == {"Metals": 100.0, "Crystals": 50.0}

    def test_init_with_empty_dict(self, mock_component):
        """Empty dict uses default values."""
        data = {}
        ability = SpaceShipyardAbility(mock_component, data)

        assert ability.construction_speed_bonus == 1.0
        assert ability.max_ship_mass == 100000
        assert ability.production_rates == {}

    def test_init_with_non_dict_data(self, mock_component):
        """Non-dict data uses default values."""
        ability = SpaceShipyardAbility(mock_component, "not a dict")

        assert ability.construction_speed_bonus == 1.0
        assert ability.max_ship_mass == 100000
        assert ability.production_rates == {}

    def test_init_partial_dict_uses_defaults(self, mock_component):
        """Partial dict uses defaults for missing keys."""
        data = {"construction_speed_bonus": 2.0}
        ability = SpaceShipyardAbility(mock_component, data)

        assert ability.construction_speed_bonus == 2.0
        assert ability.max_ship_mass == 100000
        assert ability.production_rates == {}

    def test_stat_bindings_empty(self, mock_component):
        """SpaceShipyardAbility has no stat bindings."""
        ability = SpaceShipyardAbility(mock_component, {})

        assert ability.STAT_BINDINGS == []

    def test_get_primary_value_returns_construction_bonus(self, mock_component):
        """Primary value is the construction speed bonus."""
        data = {"construction_speed_bonus": 2.5}
        ability = SpaceShipyardAbility(mock_component, data)

        assert ability.get_primary_value() == 2.5

    def test_get_ui_rows_without_production_rates(self, mock_component):
        """UI rows without production rates show bonus and max mass."""
        data = {"construction_speed_bonus": 1.5, "max_ship_mass": 150000}
        ability = SpaceShipyardAbility(mock_component, data)

        rows = ability.get_ui_rows()

        assert len(rows) == 2
        assert rows[0]["label"] == "Construction Bonus"
        assert rows[0]["value"] == "1.5x"
        assert rows[0]["color_hint"] == HINT_SHIELD_CAP
        assert rows[1]["label"] == "Max Ship Mass"
        assert rows[1]["value"] == "150,000 kg"
        assert rows[1]["color_hint"] == HINT_DEFAULT

    def test_get_ui_rows_with_uniform_production_rates(self, mock_component):
        """UI rows show single rate when all production rates are equal."""
        data = {
            "construction_speed_bonus": 1.0,
            "max_ship_mass": 100000,
            "production_rates": {"Metals": 200.0, "Crystals": 200.0, "Organics": 200.0}
        }
        ability = SpaceShipyardAbility(mock_component, data)

        rows = ability.get_ui_rows()

        assert len(rows) == 3
        assert rows[2]["label"] == "Production Rate"
        assert rows[2]["value"] == "200/turn"
        assert rows[2]["color_hint"] == HINT_COLONIZE

    def test_get_ui_rows_with_varying_production_rates(self, mock_component):
        """UI rows show range when production rates differ."""
        data = {
            "construction_speed_bonus": 1.0,
            "max_ship_mass": 100000,
            "production_rates": {"Metals": 100.0, "Crystals": 300.0}
        }
        ability = SpaceShipyardAbility(mock_component, data)

        rows = ability.get_ui_rows()

        assert len(rows) == 3
        assert rows[2]["label"] == "Production Rate"
        assert rows[2]["value"] == "100-300/turn"

    def test_get_ui_rows_with_single_production_rate(self, mock_component):
        """UI rows show single rate when only one production rate exists."""
        data = {
            "construction_speed_bonus": 1.2,
            "max_ship_mass": 50000,
            "production_rates": {"Metals": 150.0}
        }
        ability = SpaceShipyardAbility(mock_component, data)

        rows = ability.get_ui_rows()

        assert len(rows) == 3
        assert rows[2]["value"] == "150/turn"

    def test_get_ui_rows_formats_large_mass(self, mock_component):
        """UI rows format large max ship mass with thousands separator."""
        data = {"construction_speed_bonus": 1.0, "max_ship_mass": 5000000}
        ability = SpaceShipyardAbility(mock_component, data)

        rows = ability.get_ui_rows()

        assert rows[1]["value"] == "5,000,000 kg"

    def test_get_ui_rows_empty_production_rates(self, mock_component):
        """UI rows with empty production_rates dict shows only 2 rows."""
        data = {
            "construction_speed_bonus": 1.0,
            "max_ship_mass": 100000,
            "production_rates": {}
        }
        ability = SpaceShipyardAbility(mock_component, data)

        rows = ability.get_ui_rows()

        assert len(rows) == 2


# =============================================================================
# Edge Cases and Integration Tests
# =============================================================================


class TestAbilityEdgeCases:
    """Edge cases and integration tests for colonize/harvester abilities."""

    @pytest.fixture
    def mock_component(self):
        """Create a mock component with ability_stats support."""
        component = MagicMock()
        component.stats = {}
        component.ability_stats = {}
        return component

    def test_colonize_planet_component_reference(self, mock_component):
        """ColonizePlanet stores reference to component."""
        ability = ColonizePlanet(mock_component, "BARREN")

        assert ability.component is mock_component

    def test_harvester_component_reference(self, mock_component):
        """ResourceHarvesterAbility stores reference to component."""
        ability = ResourceHarvesterAbility(mock_component, {"resource_type": "Fuel"})

        assert ability.component is mock_component

    def test_storage_ability_stats_lookup(self, mock_component):
        """EmpireStorageAbility uses get_effective_stat for modifiers."""
        data = {"resource_type": "Metals", "capacity": 1000.0}
        ability = EmpireStorageAbility(mock_component, data)

        # Set up ability-specific stats
        mock_component.ability_stats = {
            "EmpireStorageAbility": {"storage_mult": 2.0}
        }

        ability.recalculate()

        assert ability.capacity == 2000.0

    def test_colonize_sync_data_updates_planet_type(self, mock_component):
        """sync_data updates ability when component data changes."""
        ability = ColonizePlanet(mock_component, "ICE_DWARF")
        assert ability.planet_type == "ICE_DWARF"

        # Note: sync_data updates base class properties but not planet_type
        # since ColonizePlanet doesn't override sync_data
        ability.sync_data({"planet_type": "CONTINENTAL"})

        # The base sync_data updates data and tags, but planet_type
        # is set in __init__ and not updated by sync_data
        assert ability.data == {"planet_type": "CONTINENTAL"}

    def test_harvester_update_returns_true(self, mock_component):
        """Harvester abilities always return True from update (operational)."""
        ability = ResourceHarvesterAbility(mock_component, {"resource_type": "Metals"})

        assert ability.update() is True

    def test_shipyard_update_returns_true(self, mock_component):
        """Shipyard abilities always return True from update (operational)."""
        ability = SpaceShipyardAbility(mock_component, {})

        assert ability.update() is True

    def test_storage_update_returns_true(self, mock_component):
        """Storage abilities always return True from update (operational)."""
        ability = EmpireStorageAbility(mock_component, {"capacity": 1000})

        assert ability.update() is True

    def test_colonize_on_activation_returns_true(self, mock_component):
        """ColonizePlanet always allows activation."""
        ability = ColonizePlanet(mock_component, "MAGMA")

        assert ability.on_activation() is True

    def test_harvester_on_activation_returns_true(self, mock_component):
        """ResourceHarvesterAbility always allows activation."""
        ability = ResourceHarvesterAbility(mock_component, {"resource_type": "Crystals"})

        assert ability.on_activation() is True
