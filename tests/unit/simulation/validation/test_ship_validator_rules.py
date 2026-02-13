"""
Unit tests for ship validation rules.

Tests for each validation rule in game.simulation.validation.ship_validator.
Covers all rule logic, edge cases, and error handling.
"""
import pytest
from unittest.mock import Mock, MagicMock, PropertyMock, patch

from game.simulation.validation.ship_validator import (
    LayerConstraintRule,
    UniqueComponentRule,
    ExclusiveGroupRule,
    MountDependencyRule,
    LayerRestrictionDefinitionRule,
    MassBudgetRule,
    ClassRequirementsRule,
    ResourceDependencyRule,
    ShipDesignValidator,
    _parse_restriction,
    RestrictionPrefixes
)
from game.simulation.validation.base import ValidationResult
from game.core.constants import LayerType


# =============================================================================
# Helper Function Tests
# =============================================================================

class TestParseRestriction:
    """Tests for _parse_restriction helper function."""

    def test_parse_restriction_returns_value_after_colon(self):
        """Should return value after prefix:."""
        result = _parse_restriction("block_classification:Weapon", "block_classification")
        assert result == "Weapon"

    def test_parse_restriction_returns_none_if_prefix_not_match(self):
        """Should return None if prefix doesn't match."""
        result = _parse_restriction("block_classification:Weapon", "allow_classification")
        assert result is None

    def test_parse_restriction_returns_none_for_empty_value(self):
        """Should handle prefix without value gracefully."""
        result = _parse_restriction("block_classification:", "block_classification")
        assert result == ""

    def test_parse_restriction_handles_value_with_colon(self):
        """Should return full value even if it contains colons."""
        result = _parse_restriction("block_id:some:weird:id", "block_id")
        assert result == "some:weird:id"


class TestRestrictionPrefixes:
    """Tests for RestrictionPrefixes constants."""

    def test_all_prefixes_defined(self):
        """All expected prefixes should be defined."""
        assert RestrictionPrefixes.BLOCK_CLASSIFICATION == "block_classification"
        assert RestrictionPrefixes.BLOCK_ID == "block_id"
        assert RestrictionPrefixes.DENY_ABILITY == "deny_ability"
        assert RestrictionPrefixes.ALLOW_CLASSIFICATION == "allow_classification"
        assert RestrictionPrefixes.ALLOW_ID == "allow_id"
        assert RestrictionPrefixes.ALLOW_ABILITY == "allow_ability"
        assert RestrictionPrefixes.ALLOW == "allow_"
        assert RestrictionPrefixes.HULL_ONLY == "HullOnly"


# =============================================================================
# LayerConstraintRule Tests
# =============================================================================

class TestLayerConstraintRule:
    """Tests for LayerConstraintRule."""

    @pytest.fixture
    def mock_ship(self):
        """Create mock ship."""
        ship = Mock()
        ship.ship_class = "Cruiser"
        ship.vehicle_type = "starship"
        ship.layers = {LayerType.CORE: Mock()}
        return ship

    @pytest.fixture
    def mock_component(self):
        """Create mock component."""
        component = Mock()
        component.name = "TestComponent"
        component.allowed_vehicle_types = ["starship", "station"]
        return component

    def test_valid_layer_and_vehicle_type(self, mock_ship, mock_component):
        """Should pass when layer exists and vehicle type is allowed."""
        rule = LayerConstraintRule()
        result = rule.validate(mock_ship, mock_component, LayerType.CORE)
        assert result.is_valid

    def test_layer_does_not_exist(self, mock_ship, mock_component):
        """Should fail when layer doesn't exist on ship."""
        rule = LayerConstraintRule()
        result = rule.validate(mock_ship, mock_component, LayerType.OUTER)

        assert not result.is_valid
        assert any("Layer OUTER does not exist" in e for e in result.errors)

    def test_vehicle_type_not_allowed(self, mock_ship, mock_component):
        """Should fail when component not allowed on vehicle type."""
        mock_ship.vehicle_type = "fighter"
        mock_component.allowed_vehicle_types = ["starship"]  # No fighter

        rule = LayerConstraintRule()
        result = rule.validate(mock_ship, mock_component, LayerType.CORE)

        assert not result.is_valid
        assert any("not allowed on fighter" in e for e in result.errors)


# =============================================================================
# UniqueComponentRule Tests
# =============================================================================

class TestUniqueComponentRule:
    """Tests for UniqueComponentRule."""

    @pytest.fixture
    def mock_ship(self):
        """Create mock ship."""
        ship = Mock()
        ship.get_all_components.return_value = []
        return ship

    @pytest.fixture
    def unique_component(self):
        """Create unique component."""
        component = Mock()
        component.id = "unique_bridge"
        component.name = "Unique Bridge"
        component.data = {"is_unique": True}
        return component

    def test_unique_component_allowed_when_none_exist(self, mock_ship, unique_component):
        """Should pass when no duplicate unique component exists."""
        rule = UniqueComponentRule()
        result = rule.validate(mock_ship, unique_component, LayerType.CORE)
        assert result.is_valid

    def test_unique_component_blocked_when_exists(self, mock_ship, unique_component):
        """Should fail when same unique component already exists."""
        existing = Mock()
        existing.id = "unique_bridge"
        mock_ship.get_all_components.return_value = [existing]

        rule = UniqueComponentRule()
        result = rule.validate(mock_ship, unique_component, LayerType.CORE)

        assert not result.is_valid
        assert any("Usage limit exceeded" in e for e in result.errors)

    def test_non_unique_component_allowed_duplicates(self, mock_ship):
        """Should pass for non-unique components with duplicates."""
        component = Mock()
        component.id = "basic_armor"
        component.data = {"is_unique": False}

        existing = Mock()
        existing.id = "basic_armor"
        mock_ship.get_all_components.return_value = [existing]

        rule = UniqueComponentRule()
        result = rule.validate(mock_ship, component, LayerType.CORE)
        assert result.is_valid

    def test_skips_validation_without_component(self, mock_ship):
        """Should skip validation when component is None."""
        rule = UniqueComponentRule()
        result = rule.validate(mock_ship, None, LayerType.CORE)
        assert result.is_valid


# =============================================================================
# ExclusiveGroupRule Tests
# =============================================================================

class TestExclusiveGroupRule:
    """Tests for ExclusiveGroupRule."""

    @pytest.fixture
    def mock_ship(self):
        """Create mock ship."""
        ship = Mock()
        ship.get_all_components.return_value = []
        return ship

    def test_exclusive_group_allowed_when_empty(self, mock_ship):
        """Should pass when no other component in exclusive group."""
        component = Mock()
        component.data = {"exclusive_group": "reactor"}

        rule = ExclusiveGroupRule()
        result = rule.validate(mock_ship, component, LayerType.CORE)
        assert result.is_valid

    def test_exclusive_group_blocked_when_exists(self, mock_ship):
        """Should fail when component in same exclusive group exists."""
        component = Mock()
        component.data = {"exclusive_group": "reactor"}

        existing = Mock()
        existing.data = {"exclusive_group": "reactor"}
        mock_ship.get_all_components.return_value = [existing]

        rule = ExclusiveGroupRule()
        result = rule.validate(mock_ship, component, LayerType.CORE)

        assert not result.is_valid
        assert any("Key component conflict: reactor" in e for e in result.errors)

    def test_different_exclusive_groups_allowed(self, mock_ship):
        """Should pass when components in different exclusive groups."""
        component = Mock()
        component.data = {"exclusive_group": "reactor"}

        existing = Mock()
        existing.data = {"exclusive_group": "engine"}
        mock_ship.get_all_components.return_value = [existing]

        rule = ExclusiveGroupRule()
        result = rule.validate(mock_ship, component, LayerType.CORE)
        assert result.is_valid

    def test_no_exclusive_group_always_allowed(self, mock_ship):
        """Should pass for components without exclusive group."""
        component = Mock()
        component.data = {}  # No exclusive_group

        rule = ExclusiveGroupRule()
        result = rule.validate(mock_ship, component, LayerType.CORE)
        assert result.is_valid


# =============================================================================
# MountDependencyRule Tests
# =============================================================================

class TestMountDependencyRule:
    """Tests for MountDependencyRule."""

    @pytest.fixture
    def mock_ship(self):
        """Create mock ship with layer."""
        ship = Mock()
        layer_data = Mock()
        layer_data.components = []
        ship.layers = {LayerType.CORE: layer_data}
        return ship

    def test_no_mount_required_passes(self, mock_ship):
        """Should pass when component has no required mount."""
        component = Mock()
        component.data = {}  # No required_mount

        rule = MountDependencyRule()
        result = rule.validate(mock_ship, component, LayerType.CORE)
        assert result.is_valid

    def test_mount_available_passes(self, mock_ship):
        """Should pass when required mount is available."""
        component = Mock()
        component.data = {"required_mount": "weapon_hardpoint"}

        mount_component = Mock()
        mount_component.data = {"mount_type": "weapon_hardpoint", "required_mount": None}
        mock_ship.layers[LayerType.CORE].components = [mount_component]

        rule = MountDependencyRule()
        result = rule.validate(mock_ship, component, LayerType.CORE)
        assert result.is_valid

    def test_mount_not_available_fails(self, mock_ship):
        """Should fail when required mount is not available."""
        component = Mock()
        component.data = {"required_mount": "weapon_hardpoint"}

        # No mount components in layer
        mock_ship.layers[LayerType.CORE].components = []

        rule = MountDependencyRule()
        result = rule.validate(mock_ship, component, LayerType.CORE)

        assert not result.is_valid
        assert any("Missing required mount: weapon_hardpoint" in e for e in result.errors)

    def test_mount_already_used_fails(self, mock_ship):
        """Should fail when all mounts are already used."""
        component = Mock()
        component.data = {"required_mount": "weapon_hardpoint"}

        mount_component = Mock()
        mount_component.data = {"mount_type": "weapon_hardpoint", "required_mount": None}

        user_component = Mock()
        user_component.data = {"required_mount": "weapon_hardpoint", "mount_type": None}

        mock_ship.layers[LayerType.CORE].components = [mount_component, user_component]

        rule = MountDependencyRule()
        result = rule.validate(mock_ship, component, LayerType.CORE)

        assert not result.is_valid

    def test_skips_validation_if_layer_doesnt_exist(self, mock_ship):
        """Should skip validation when layer doesn't exist."""
        component = Mock()
        component.data = {"required_mount": "weapon_hardpoint"}

        rule = MountDependencyRule()
        result = rule.validate(mock_ship, component, LayerType.OUTER)  # Not in ship.layers
        assert result.is_valid


# =============================================================================
# LayerRestrictionDefinitionRule Tests
# =============================================================================

class TestLayerRestrictionDefinitionRule:
    """Tests for LayerRestrictionDefinitionRule."""

    @pytest.fixture
    def mock_ship(self):
        """Create mock ship with layer."""
        ship = Mock()
        layer_data = Mock()
        layer_data.restrictions = []
        ship.layers = {LayerType.CORE: layer_data}
        return ship

    @pytest.fixture
    def mock_component(self):
        """Create mock component."""
        component = Mock()
        component.id = "test_comp"
        component.data = {"major_classification": "Weapon"}
        component.has_ability.return_value = False
        return component

    def test_no_restrictions_allows_all(self, mock_ship, mock_component):
        """Should pass when no restrictions defined."""
        rule = LayerRestrictionDefinitionRule()
        result = rule.validate(mock_ship, mock_component, LayerType.CORE)
        assert result.is_valid

    def test_block_classification_blocks_matching(self, mock_ship, mock_component):
        """Should block when classification matches block rule."""
        mock_ship.layers[LayerType.CORE].restrictions = ["block_classification:Weapon"]

        rule = LayerRestrictionDefinitionRule()
        result = rule.validate(mock_ship, mock_component, LayerType.CORE)

        assert not result.is_valid
        assert any("Classification 'Weapon' blocked" in e for e in result.errors)

    def test_block_id_blocks_matching(self, mock_ship, mock_component):
        """Should block when component ID matches block rule."""
        mock_ship.layers[LayerType.CORE].restrictions = ["block_id:test_comp"]

        rule = LayerRestrictionDefinitionRule()
        result = rule.validate(mock_ship, mock_component, LayerType.CORE)

        assert not result.is_valid
        assert any("Component 'test_comp' blocked" in e for e in result.errors)

    def test_deny_ability_blocks_matching(self, mock_ship, mock_component):
        """Should block when component has denied ability."""
        mock_ship.layers[LayerType.CORE].restrictions = ["deny_ability:WeaponAbility"]
        mock_component.has_ability.return_value = True

        rule = LayerRestrictionDefinitionRule()
        result = rule.validate(mock_ship, mock_component, LayerType.CORE)

        assert not result.is_valid

    def test_allow_classification_passes_matching(self, mock_ship, mock_component):
        """Should pass when classification matches allow rule."""
        mock_ship.layers[LayerType.CORE].restrictions = ["allow_classification:Weapon"]

        rule = LayerRestrictionDefinitionRule()
        result = rule.validate(mock_ship, mock_component, LayerType.CORE)
        assert result.is_valid

    def test_allow_classification_blocks_non_matching(self, mock_ship, mock_component):
        """Should block when classification doesn't match any allow rule."""
        mock_ship.layers[LayerType.CORE].restrictions = ["allow_classification:Armor"]
        mock_component.data["major_classification"] = "Weapon"

        rule = LayerRestrictionDefinitionRule()
        result = rule.validate(mock_ship, mock_component, LayerType.CORE)

        assert not result.is_valid
        assert any("Layer restricts components" in e for e in result.errors)

    def test_allow_id_passes_matching(self, mock_ship, mock_component):
        """Should pass when ID matches allow rule."""
        mock_ship.layers[LayerType.CORE].restrictions = ["allow_id:test_comp"]

        rule = LayerRestrictionDefinitionRule()
        result = rule.validate(mock_ship, mock_component, LayerType.CORE)
        assert result.is_valid

    def test_allow_ability_passes_matching(self, mock_ship, mock_component):
        """Should pass when ability matches allow rule."""
        mock_ship.layers[LayerType.CORE].restrictions = ["allow_ability:WeaponAbility"]
        mock_component.has_ability.return_value = True

        rule = LayerRestrictionDefinitionRule()
        result = rule.validate(mock_ship, mock_component, LayerType.CORE)
        assert result.is_valid

    def test_hull_only_allows_hull_components(self, mock_ship, mock_component):
        """Should pass hull components when HullOnly restriction."""
        mock_ship.layers[LayerType.CORE].restrictions = ["HullOnly"]
        mock_component.id = "hull_corvette"

        rule = LayerRestrictionDefinitionRule()
        result = rule.validate(mock_ship, mock_component, LayerType.CORE)
        assert result.is_valid

    def test_hull_only_blocks_non_hull_components(self, mock_ship, mock_component):
        """Should block non-hull components when HullOnly restriction."""
        mock_ship.layers[LayerType.CORE].restrictions = ["HullOnly"]
        mock_component.id = "basic_armor"  # Not hull_

        rule = LayerRestrictionDefinitionRule()
        result = rule.validate(mock_ship, mock_component, LayerType.CORE)

        assert not result.is_valid
        assert any("only allows Hull components" in e for e in result.errors)

    def test_skips_if_layer_doesnt_exist(self, mock_ship, mock_component):
        """Should skip validation when layer doesn't exist."""
        rule = LayerRestrictionDefinitionRule()
        result = rule.validate(mock_ship, mock_component, LayerType.OUTER)
        assert result.is_valid


# =============================================================================
# MassBudgetRule Tests
# =============================================================================

class TestMassBudgetRule:
    """Tests for MassBudgetRule."""

    @pytest.fixture
    def mock_ship(self):
        """Create mock ship with mass budget."""
        ship = Mock()
        ship.name = "TestShip"
        ship.current_mass = 5000
        ship.max_mass_budget = 10000

        layer_data = Mock()
        layer_data.components = []
        layer_data.max_mass_pct = 0.5  # 50% = 5000 max
        ship.layers = {LayerType.CORE: layer_data}
        return ship

    def test_under_budget_passes(self, mock_ship):
        """Should pass when under mass budget."""
        component = Mock()
        component.mass = 1000

        rule = MassBudgetRule()
        result = rule.validate(mock_ship, component, LayerType.CORE)
        assert result.is_valid

    def test_over_ship_budget_fails(self, mock_ship):
        """Should fail when component exceeds ship mass budget."""
        component = Mock()
        component.mass = 6000  # 5000 current + 6000 = 11000 > 10000 max

        rule = MassBudgetRule()
        result = rule.validate(mock_ship, component, LayerType.CORE)

        assert not result.is_valid
        assert any("Mass budget exceeded" in e for e in result.errors)

    def test_over_layer_budget_fails(self, mock_ship):
        """Should fail when component exceeds layer mass budget."""
        component = Mock()
        component.mass = 3000

        # Layer has 2500 mass already, max is 5000 (50% of 10000)
        existing = Mock()
        existing.mass = 2500
        mock_ship.layers[LayerType.CORE].components = [existing]

        rule = MassBudgetRule()
        result = rule.validate(mock_ship, component, LayerType.CORE)

        assert not result.is_valid
        assert any("Mass budget exceeded for CORE" in e for e in result.errors)

    def test_design_validation_without_component(self, mock_ship):
        """Should validate ship mass even without component."""
        mock_ship.current_mass = 11000  # Over budget

        rule = MassBudgetRule()
        result = rule.validate(mock_ship, None, None)

        assert not result.is_valid


# =============================================================================
# ClassRequirementsRule Tests
# =============================================================================

class TestClassRequirementsRule:
    """Tests for ClassRequirementsRule."""

    @pytest.fixture
    def mock_registries(self):
        """Create mock registries."""
        registries = Mock()
        registries.vehicle_classes = {
            "Cruiser": {"max_mass": 10000}
        }
        return registries

    @pytest.fixture
    def mock_ship(self):
        """Create mock ship."""
        ship = Mock()
        ship.ship_class = "Cruiser"
        ship.get_all_components.return_value = []
        return ship

    def test_requires_registries(self):
        """Should require registries parameter."""
        with pytest.raises(TypeError, match="registries is required"):
            ClassRequirementsRule(registries=None)

    def test_valid_design_passes(self, mock_registries, mock_ship):
        """Should pass for valid design."""
        rule = ClassRequirementsRule(registries=mock_registries)
        result = rule.validate(mock_ship, None, None)
        assert result.is_valid

    def test_missing_command_fails(self, mock_registries, mock_ship):
        """Should fail when command required but missing."""
        component = Mock()
        component.ability_instances = []

        # Mock ability totals to require command but not have it
        with patch('game.simulation.entities.ship_stats.ShipStatsCalculator') as MockCalc:
            mock_calc = Mock()
            mock_calc.calculate_ability_totals.return_value = {
                'RequiresCommandAndControl': 1,
                'CommandAndControl': 0
            }
            MockCalc.return_value = mock_calc

            rule = ClassRequirementsRule(registries=mock_registries)
            result = rule.validate(mock_ship, None, None)

            assert not result.is_valid
            assert any("Command capability" in e for e in result.errors)

    def test_missing_propulsion_fails(self, mock_registries, mock_ship):
        """Should fail when propulsion required but missing."""
        with patch('game.simulation.entities.ship_stats.ShipStatsCalculator') as MockCalc:
            mock_calc = Mock()
            mock_calc.calculate_ability_totals.return_value = {
                'RequiresCombatMovement': 1,
                'CombatPropulsion': 0
            }
            MockCalc.return_value = mock_calc

            rule = ClassRequirementsRule(registries=mock_registries)
            result = rule.validate(mock_ship, None, None)

            assert not result.is_valid
            assert any("Combat propulsion" in e for e in result.errors)

    def test_insufficient_crew_housing_fails(self, mock_registries, mock_ship):
        """Should fail when crew capacity insufficient."""
        with patch('game.simulation.entities.ship_stats.ShipStatsCalculator') as MockCalc:
            mock_calc = Mock()
            mock_calc.calculate_ability_totals.return_value = {
                'CrewCapacity': 5,
                'CrewRequired': 10,
                'LifeSupportCapacity': 10
            }
            MockCalc.return_value = mock_calc

            rule = ClassRequirementsRule(registries=mock_registries)
            result = rule.validate(mock_ship, None, None)

            assert not result.is_valid
            assert any("crew housing" in e for e in result.errors)

    def test_insufficient_life_support_fails(self, mock_registries, mock_ship):
        """Should fail when life support insufficient."""
        with patch('game.simulation.entities.ship_stats.ShipStatsCalculator') as MockCalc:
            mock_calc = Mock()
            mock_calc.calculate_ability_totals.return_value = {
                'CrewCapacity': 10,
                'CrewRequired': 10,
                'LifeSupportCapacity': 5
            }
            MockCalc.return_value = mock_calc

            rule = ClassRequirementsRule(registries=mock_registries)
            result = rule.validate(mock_ship, None, None)

            assert not result.is_valid
            assert any("life support" in e for e in result.errors)


# =============================================================================
# ResourceDependencyRule Tests
# =============================================================================

class TestResourceDependencyRule:
    """Tests for ResourceDependencyRule."""

    @pytest.fixture
    def mock_ship(self):
        """Create mock ship."""
        ship = Mock()
        ship.get_all_components.return_value = []
        return ship

    def test_no_resources_passes(self, mock_ship):
        """Should pass when no resources required."""
        rule = ResourceDependencyRule()
        result = rule.validate(mock_ship, None, None)
        assert result.is_valid

    def test_matched_resources_passes(self, mock_ship):
        """Should pass when resources have storage."""
        from game.simulation.components.abilities.resources import ResourceConsumption, ResourceStorage

        consumer = Mock(spec=ResourceConsumption)
        consumer.resource_type = "fuel"

        storage = Mock(spec=ResourceStorage)
        storage.resource_type = "fuel"
        storage.max_amount = 100

        comp1 = Mock()
        comp1.ability_instances = [consumer]

        comp2 = Mock()
        comp2.ability_instances = [storage]

        mock_ship.get_all_components.return_value = [comp1, comp2]

        rule = ResourceDependencyRule()
        result = rule.validate(mock_ship, None, None)
        assert result.is_valid

    def test_missing_storage_warns(self, mock_ship):
        """Should warn when resource lacks storage."""
        from game.simulation.components.abilities.resources import ResourceConsumption

        consumer = Mock(spec=ResourceConsumption)
        consumer.resource_type = "fuel"

        comp = Mock()
        comp.ability_instances = [consumer]

        mock_ship.get_all_components.return_value = [comp]

        rule = ResourceDependencyRule()
        result = rule.validate(mock_ship, None, None)

        # Should have warning but still valid
        assert result.is_valid
        assert any("Fuel Storage" in w for w in result.warnings)


# =============================================================================
# ShipDesignValidator Tests
# =============================================================================

class TestShipDesignValidator:
    """Tests for ShipDesignValidator."""

    @pytest.fixture
    def mock_registries(self):
        """Create mock registries."""
        registries = Mock()
        registries.vehicle_classes = {
            "Cruiser": {"max_mass": 10000}
        }
        return registries

    def test_requires_registries(self):
        """Should require registries parameter."""
        with pytest.raises(TypeError, match="registries is required"):
            ShipDesignValidator(registries=None)

    def test_has_addition_rules(self, mock_registries):
        """Should have addition rules."""
        validator = ShipDesignValidator(registries=mock_registries)
        assert len(validator.addition_rules) > 0

    def test_has_design_rules(self, mock_registries):
        """Should have design rules."""
        validator = ShipDesignValidator(registries=mock_registries)
        assert len(validator.design_rules) > 0

    def test_validate_addition_runs_all_addition_rules(self, mock_registries):
        """validate_addition should run all addition rules."""
        validator = ShipDesignValidator(registries=mock_registries)

        layer_data = Mock()
        layer_data.restrictions = []
        layer_data.components = []
        layer_data.max_mass_pct = 0.5

        mock_ship = Mock()
        mock_ship.layers = {LayerType.CORE: layer_data}
        mock_ship.vehicle_type = "starship"
        mock_ship.ship_class = "Cruiser"
        mock_ship.current_mass = 0
        mock_ship.max_mass_budget = 10000
        mock_ship.get_all_components.return_value = []

        mock_component = Mock()
        mock_component.id = "test"
        mock_component.name = "Test"
        mock_component.mass = 100
        mock_component.data = {}
        mock_component.allowed_vehicle_types = ["starship"]

        result = validator.validate_addition(mock_ship, mock_component, LayerType.CORE)
        assert isinstance(result, ValidationResult)

    def test_validate_design_runs_all_design_rules(self, mock_registries):
        """validate_design should run all design rules."""
        validator = ShipDesignValidator(registries=mock_registries)

        mock_ship = Mock()
        mock_ship.ship_class = "Cruiser"
        mock_ship.current_mass = 5000
        mock_ship.max_mass_budget = 10000
        mock_ship.get_all_components.return_value = []
        mock_ship.name = "TestShip"

        result = validator.validate_design(mock_ship)
        assert isinstance(result, ValidationResult)
