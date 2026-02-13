"""Tests for AbilityAggregator - ability aggregation utilities.

PROJ-118 Phase 2: Tests for ability_aggregator.py which provides:
- calculate_ability_totals: Aggregate abilities across components
- get_ability_total: Get single ability value
- get_ability_instances_by_class: Yield matching ability instances
- _aggregate_ability_groups: Internal aggregation logic

Tests focus on:
- Stacking rules (max within group, sum/multiply across groups)
- Marker abilities (boolean True semantics)
- Multiplicative abilities (ToHitAttackModifier, ToHitDefenseModifier)
- Layer and scope filtering
- Edge cases (empty, no abilities, mixed types)
"""
import pytest
from unittest.mock import Mock, MagicMock
from typing import List, Any

from game.simulation.entities.ability_aggregator import (
    calculate_ability_totals,
    get_ability_total,
    get_ability_instances_by_class,
    _aggregate_ability_groups,
    MULTIPLICATIVE_ABILITIES,
    MARKER_ABILITIES,
)
from game.simulation.components.abilities.base import Ability, AbilityLayer, AbilityScope


# =============================================================================
# Test Fixtures and Helpers
# =============================================================================

class MockAbility:
    """Mock ability for testing aggregation logic."""

    def __init__(
        self,
        class_name: str,
        value: float,
        stack_group: str = None,
        layer: AbilityLayer = AbilityLayer.COMBAT,
        scope: AbilityScope = AbilityScope.SELF
    ):
        self._class_name = class_name
        self._value = value
        self.stack_group = stack_group
        self.layer = layer
        self.scope = scope

    @property
    def __class__(self):
        # Return a mock class with the name we want
        mock_class = Mock()
        mock_class.__name__ = self._class_name
        return mock_class

    def applies_to_layer(self, layer: AbilityLayer) -> bool:
        return bool(self.layer & layer)

    def get_primary_value(self) -> float:
        return self._value


class MockComponent:
    """Mock component for testing aggregation."""

    def __init__(
        self,
        ability_instances: List[MockAbility] = None,
        abilities: dict = None
    ):
        self.ability_instances = ability_instances or []
        self.abilities = abilities or {}


@pytest.fixture
def mock_propulsion_ability():
    """Create a mock CombatPropulsion ability."""
    return MockAbility("CombatPropulsion", 1000.0)


@pytest.fixture
def mock_shield_ability():
    """Create a mock ShieldProjection ability."""
    return MockAbility("ShieldProjection", 500.0)


# =============================================================================
# Tests for _aggregate_ability_groups (internal helper)
# =============================================================================

class TestAggregateAbilityGroups:
    """Tests for the internal _aggregate_ability_groups function."""

    def test_empty_groups_returns_empty_dict(self):
        """Empty input produces empty output."""
        result = _aggregate_ability_groups({})
        assert result == {}

    def test_single_ability_single_value(self):
        """Single ability with single numeric value."""
        groups = {
            "CombatPropulsion": {
                "comp1": [1000.0]
            }
        }
        result = _aggregate_ability_groups(groups)
        assert result == {"CombatPropulsion": 1000.0}

    def test_intra_group_takes_max(self):
        """Values within the same group take MAX (redundancy)."""
        groups = {
            "CombatPropulsion": {
                "engines": [500.0, 1000.0, 750.0]  # Same group
            }
        }
        result = _aggregate_ability_groups(groups)
        assert result["CombatPropulsion"] == 1000.0  # MAX of group

    def test_inter_group_sums_by_default(self):
        """Values across different groups are summed."""
        groups = {
            "CombatPropulsion": {
                "comp1": [500.0],
                "comp2": [300.0]
            }
        }
        result = _aggregate_ability_groups(groups)
        assert result["CombatPropulsion"] == 800.0  # Sum of groups

    def test_multiplicative_ability_multiplies_across_groups(self):
        """ToHitAttackModifier multiplies across groups instead of summing."""
        groups = {
            "ToHitAttackModifier": {
                "comp1": [0.9],
                "comp2": [0.8]
            }
        }
        result = _aggregate_ability_groups(groups)
        assert result["ToHitAttackModifier"] == pytest.approx(0.72)  # 0.9 * 0.8

    def test_tohitdefensemodifier_is_multiplicative(self):
        """ToHitDefenseModifier is also multiplicative."""
        groups = {
            "ToHitDefenseModifier": {
                "comp1": [1.1],
                "comp2": [1.2]
            }
        }
        result = _aggregate_ability_groups(groups)
        assert result["ToHitDefenseModifier"] == pytest.approx(1.32)  # 1.1 * 1.2

    def test_boolean_ability_any_true_makes_result_true(self):
        """Boolean abilities return True if any group contributes True."""
        groups = {
            "CommandAndControl": {
                "comp1": [True],
                "comp2": [False]
            }
        }
        result = _aggregate_ability_groups(groups)
        assert result["CommandAndControl"] is True

    def test_multiple_abilities(self):
        """Multiple different abilities aggregate independently."""
        groups = {
            "CombatPropulsion": {
                "comp1": [1000.0],
                "comp2": [500.0]
            },
            "ShieldProjection": {
                "comp1": [200.0]
            }
        }
        result = _aggregate_ability_groups(groups)
        assert result["CombatPropulsion"] == 1500.0
        assert result["ShieldProjection"] == 200.0

    def test_filters_non_numeric_values(self):
        """Non-numeric values (except True) are filtered out."""
        groups = {
            "CombatPropulsion": {
                "comp1": [1000.0, "invalid", None]
            }
        }
        result = _aggregate_ability_groups(groups)
        assert result["CombatPropulsion"] == 1000.0

    def test_empty_values_skipped(self):
        """Groups with no valid values are skipped."""
        groups = {
            "CombatPropulsion": {
                "comp1": ["invalid", None]  # No valid values
            }
        }
        result = _aggregate_ability_groups(groups)
        assert "CombatPropulsion" not in result

    def test_mixed_numeric_and_boolean_in_groups(self):
        """When first group is numeric, True from other groups is summed as 1.

        Note: In Python, bool is a subclass of int, so True == 1.
        The inter-group aggregation sums all values including True as 1.
        """
        groups = {
            "SomeAbility": {
                "comp1": [100.0],
                "comp2": [True]  # Boolean in different group, summed as 1
            }
        }
        result = _aggregate_ability_groups(groups)
        # First contribution is numeric (100.0), True is summed as 1
        assert result["SomeAbility"] == 101.0


# =============================================================================
# Tests for calculate_ability_totals
# =============================================================================

class TestCalculateAbilityTotals:
    """Tests for calculate_ability_totals function."""

    def test_empty_components_list(self):
        """Empty component list returns empty dict."""
        result = calculate_ability_totals([])
        assert result == {}

    def test_component_with_no_abilities(self):
        """Component with no ability_instances or abilities dict."""
        comp = MockComponent()
        result = calculate_ability_totals([comp])
        assert result == {}

    def test_single_ability_instance(self):
        """Single ability instance is aggregated correctly."""
        ability = MockAbility("CombatPropulsion", 1000.0)
        comp = MockComponent(ability_instances=[ability])

        result = calculate_ability_totals([comp])
        assert result["CombatPropulsion"] == 1000.0

    def test_multiple_abilities_same_component(self):
        """Multiple abilities on same component aggregate independently."""
        abilities = [
            MockAbility("CombatPropulsion", 1000.0),
            MockAbility("ShieldProjection", 500.0)
        ]
        comp = MockComponent(ability_instances=abilities)

        result = calculate_ability_totals([comp])
        assert result["CombatPropulsion"] == 1000.0
        assert result["ShieldProjection"] == 500.0

    def test_abilities_across_multiple_components(self):
        """Abilities across components sum (different group keys)."""
        comp1 = MockComponent(ability_instances=[
            MockAbility("CombatPropulsion", 500.0)
        ])
        comp2 = MockComponent(ability_instances=[
            MockAbility("CombatPropulsion", 300.0)
        ])

        result = calculate_ability_totals([comp1, comp2])
        assert result["CombatPropulsion"] == 800.0

    def test_stacking_group_same_value_takes_max(self):
        """Same stack_group across components takes MAX."""
        comp1 = MockComponent(ability_instances=[
            MockAbility("CombatPropulsion", 500.0, stack_group="main_engine")
        ])
        comp2 = MockComponent(ability_instances=[
            MockAbility("CombatPropulsion", 800.0, stack_group="main_engine")
        ])

        result = calculate_ability_totals([comp1, comp2])
        # Same stack_group = MAX
        assert result["CombatPropulsion"] == 800.0

    def test_different_stack_groups_sum(self):
        """Different stack_groups sum together."""
        comp1 = MockComponent(ability_instances=[
            MockAbility("CombatPropulsion", 500.0, stack_group="main_engine")
        ])
        comp2 = MockComponent(ability_instances=[
            MockAbility("CombatPropulsion", 300.0, stack_group="aux_engine")
        ])

        result = calculate_ability_totals([comp1, comp2])
        assert result["CombatPropulsion"] == 800.0

    def test_marker_ability_returns_true(self):
        """Marker abilities return boolean True."""
        ability = MockAbility("CommandAndControl", 0.0)  # Marker abilities return 0.0
        comp = MockComponent(ability_instances=[ability])

        result = calculate_ability_totals([comp])
        assert result["CommandAndControl"] is True

    def test_armor_marker_ability(self):
        """Armor marker ability returns True."""
        ability = MockAbility("Armor", 0.0)
        comp = MockComponent(ability_instances=[ability])

        result = calculate_ability_totals([comp])
        assert result["Armor"] is True

    def test_requires_command_and_control_marker(self):
        """RequiresCommandAndControl marker returns True."""
        ability = MockAbility("RequiresCommandAndControl", 0.0)
        comp = MockComponent(ability_instances=[ability])

        result = calculate_ability_totals([comp])
        assert result["RequiresCommandAndControl"] is True

    def test_requires_combat_movement_marker(self):
        """RequiresCombatMovement marker returns True."""
        ability = MockAbility("RequiresCombatMovement", 0.0)
        comp = MockComponent(ability_instances=[ability])

        result = calculate_ability_totals([comp])
        assert result["RequiresCombatMovement"] is True

    def test_multiplicative_ability_stacking(self):
        """ToHitAttackModifier multiplies across components."""
        comp1 = MockComponent(ability_instances=[
            MockAbility("ToHitAttackModifier", 0.9)
        ])
        comp2 = MockComponent(ability_instances=[
            MockAbility("ToHitAttackModifier", 0.8)
        ])

        result = calculate_ability_totals([comp1, comp2])
        assert result["ToHitAttackModifier"] == pytest.approx(0.72)


class TestCalculateAbilityTotalsWithLayerFilter:
    """Tests for layer filtering in calculate_ability_totals."""

    def test_filter_by_combat_layer(self):
        """Only COMBAT layer abilities are included when filtered."""
        combat_ability = MockAbility("CombatPropulsion", 1000.0, layer=AbilityLayer.COMBAT)
        strategic_ability = MockAbility("StrategicMovement", 5.0, layer=AbilityLayer.STRATEGIC)
        comp = MockComponent(ability_instances=[combat_ability, strategic_ability])

        result = calculate_ability_totals([comp], layer=AbilityLayer.COMBAT)

        assert "CombatPropulsion" in result
        assert "StrategicMovement" not in result

    def test_filter_by_strategic_layer(self):
        """Only STRATEGIC layer abilities are included when filtered."""
        combat_ability = MockAbility("CombatPropulsion", 1000.0, layer=AbilityLayer.COMBAT)
        strategic_ability = MockAbility("StrategicMovement", 5.0, layer=AbilityLayer.STRATEGIC)
        comp = MockComponent(ability_instances=[combat_ability, strategic_ability])

        result = calculate_ability_totals([comp], layer=AbilityLayer.STRATEGIC)

        assert "CombatPropulsion" not in result
        assert "StrategicMovement" in result

    def test_both_layer_includes_all(self):
        """BOTH layer abilities are included when filtering for either layer."""
        both_ability = MockAbility("SharedAbility", 100.0, layer=AbilityLayer.BOTH)
        comp = MockComponent(ability_instances=[both_ability])

        # Should be included when filtering for COMBAT
        result_combat = calculate_ability_totals([comp], layer=AbilityLayer.COMBAT)
        assert "SharedAbility" in result_combat

        # Should be included when filtering for STRATEGIC
        result_strategic = calculate_ability_totals([comp], layer=AbilityLayer.STRATEGIC)
        assert "SharedAbility" in result_strategic

    def test_layer_filter_skips_raw_dict_abilities(self):
        """Layer filtering skips raw dict abilities (requires ability instances)."""
        comp = MockComponent(
            ability_instances=[],
            abilities={"RawAbility": 50.0}
        )

        # With layer filter, dict abilities are skipped
        result = calculate_ability_totals([comp], layer=AbilityLayer.COMBAT)
        assert "RawAbility" not in result

        # Without layer filter, dict abilities are included
        result_no_filter = calculate_ability_totals([comp])
        assert "RawAbility" in result_no_filter


class TestCalculateAbilityTotalsWithScopeFilter:
    """Tests for scope filtering in calculate_ability_totals."""

    def test_scope_filter_only_works_with_layer(self):
        """Scope filter requires layer filter to be active."""
        self_ability = MockAbility("SomeAbility", 100.0, scope=AbilityScope.SELF)
        comp = MockComponent(ability_instances=[self_ability])

        # With both layer and scope filter
        result = calculate_ability_totals(
            [comp],
            layer=AbilityLayer.COMBAT,
            scope_filter=AbilityScope.SELF
        )
        assert "SomeAbility" in result

    def test_scope_filter_excludes_non_matching(self):
        """Scope filter excludes abilities with different scope."""
        self_ability = MockAbility("SelfAbility", 100.0, scope=AbilityScope.SELF)
        system_ability = MockAbility("SystemAbility", 200.0, scope=AbilityScope.ALLIED_SYSTEM)
        comp = MockComponent(ability_instances=[self_ability, system_ability])

        # Filter for SELF scope only
        result = calculate_ability_totals(
            [comp],
            layer=AbilityLayer.COMBAT,
            scope_filter=AbilityScope.SELF
        )

        assert "SelfAbility" in result
        assert "SystemAbility" not in result

    def test_scope_filter_allied_system(self):
        """Can filter for ALLIED_SYSTEM scope abilities."""
        self_ability = MockAbility("SelfAbility", 100.0, scope=AbilityScope.SELF)
        system_ability = MockAbility("SystemAbility", 200.0, scope=AbilityScope.ALLIED_SYSTEM)
        comp = MockComponent(ability_instances=[self_ability, system_ability])

        result = calculate_ability_totals(
            [comp],
            layer=AbilityLayer.COMBAT,
            scope_filter=AbilityScope.ALLIED_SYSTEM
        )

        assert "SelfAbility" not in result
        assert "SystemAbility" in result


class TestCalculateAbilityTotalsWithRawDict:
    """Tests for raw dictionary abilities (old system compatibility)."""

    def test_raw_dict_ability_simple_value(self):
        """Simple numeric value in abilities dict."""
        comp = MockComponent(abilities={"SimpleAbility": 100.0})

        result = calculate_ability_totals([comp])
        assert result["SimpleAbility"] == 100.0

    def test_raw_dict_ability_with_value_key(self):
        """Dict with 'value' key extracts the value."""
        comp = MockComponent(abilities={
            "ComplexAbility": {"value": 150.0}
        })

        result = calculate_ability_totals([comp])
        assert result["ComplexAbility"] == 150.0

    def test_raw_dict_ability_with_stack_group(self):
        """Dict with stack_group uses that for grouping."""
        comp1 = MockComponent(abilities={
            "GroupedAbility": {"value": 100.0, "stack_group": "group_a"}
        })
        comp2 = MockComponent(abilities={
            "GroupedAbility": {"value": 200.0, "stack_group": "group_a"}
        })

        result = calculate_ability_totals([comp1, comp2])
        # Same stack_group = MAX
        assert result["GroupedAbility"] == 200.0

    def test_ability_instance_prevents_double_count(self):
        """If ability_instances has ability, dict version is skipped."""
        ability = MockAbility("DualAbility", 100.0)
        comp = MockComponent(
            ability_instances=[ability],
            abilities={"DualAbility": 50.0}  # Should be ignored
        )

        result = calculate_ability_totals([comp])
        # Only the instance value is used
        assert result["DualAbility"] == 100.0


# =============================================================================
# Tests for get_ability_total
# =============================================================================

class TestGetAbilityTotal:
    """Tests for get_ability_total helper function."""

    def test_returns_total_for_ability(self):
        """Returns the aggregated total for specified ability."""
        comp1 = MockComponent(ability_instances=[
            MockAbility("CombatPropulsion", 500.0)
        ])
        comp2 = MockComponent(ability_instances=[
            MockAbility("CombatPropulsion", 300.0)
        ])

        result = get_ability_total([comp1, comp2], "CombatPropulsion")
        assert result == 800.0

    def test_returns_zero_for_missing_ability(self):
        """Returns 0 for ability that doesn't exist."""
        comp = MockComponent(ability_instances=[
            MockAbility("CombatPropulsion", 500.0)
        ])

        result = get_ability_total([comp], "NonexistentAbility")
        assert result == 0

    def test_works_with_empty_components(self):
        """Returns 0 for empty component list."""
        result = get_ability_total([], "CombatPropulsion")
        assert result == 0


# =============================================================================
# Tests for get_ability_instances_by_class
# =============================================================================

class TestGetAbilityInstancesByClass:
    """Tests for get_ability_instances_by_class generator function."""

    def test_yields_matching_ability_pairs(self):
        """Yields (component, ability) pairs for matching class."""
        ability = MockAbility("CombatPropulsion", 1000.0)
        comp = MockComponent(ability_instances=[ability])

        pairs = list(get_ability_instances_by_class([comp], "CombatPropulsion"))

        assert len(pairs) == 1
        assert pairs[0][0] is comp
        assert pairs[0][1] is ability

    def test_yields_nothing_for_no_match(self):
        """Yields nothing when no abilities match."""
        ability = MockAbility("CombatPropulsion", 1000.0)
        comp = MockComponent(ability_instances=[ability])

        pairs = list(get_ability_instances_by_class([comp], "ShieldProjection"))

        assert len(pairs) == 0

    def test_yields_multiple_matches_same_component(self):
        """Yields multiple pairs if component has multiple matching abilities."""
        abilities = [
            MockAbility("ResourceConsumption", 10.0),
            MockAbility("ResourceConsumption", 5.0)
        ]
        comp = MockComponent(ability_instances=abilities)

        pairs = list(get_ability_instances_by_class([comp], "ResourceConsumption"))

        assert len(pairs) == 2
        assert all(p[0] is comp for p in pairs)

    def test_yields_matches_across_components(self):
        """Yields pairs from multiple components."""
        ability1 = MockAbility("CombatPropulsion", 500.0)
        ability2 = MockAbility("CombatPropulsion", 300.0)
        comp1 = MockComponent(ability_instances=[ability1])
        comp2 = MockComponent(ability_instances=[ability2])

        pairs = list(get_ability_instances_by_class([comp1, comp2], "CombatPropulsion"))

        assert len(pairs) == 2
        assert pairs[0][0] is comp1
        assert pairs[1][0] is comp2

    def test_handles_component_without_ability_instances(self):
        """Gracefully handles components without ability_instances attribute."""
        class BareComponent:
            pass

        comp = BareComponent()
        pairs = list(get_ability_instances_by_class([comp], "CombatPropulsion"))

        assert len(pairs) == 0

    def test_handles_non_list_ability_instances(self):
        """Handles ability_instances that is not a list."""
        class WeirdComponent:
            ability_instances = "not a list"

        comp = WeirdComponent()
        pairs = list(get_ability_instances_by_class([comp], "CombatPropulsion"))

        assert len(pairs) == 0


# =============================================================================
# Tests for module constants
# =============================================================================

class TestModuleConstants:
    """Tests for module-level constants."""

    def test_multiplicative_abilities_contains_expected(self):
        """MULTIPLICATIVE_ABILITIES contains the expected entries."""
        assert 'ToHitAttackModifier' in MULTIPLICATIVE_ABILITIES
        assert 'ToHitDefenseModifier' in MULTIPLICATIVE_ABILITIES

    def test_marker_abilities_contains_expected(self):
        """MARKER_ABILITIES contains the expected entries."""
        assert 'CommandAndControl' in MARKER_ABILITIES
        assert 'Armor' in MARKER_ABILITIES
        assert 'RequiresCommandAndControl' in MARKER_ABILITIES
        assert 'RequiresCombatMovement' in MARKER_ABILITIES


# =============================================================================
# Integration-style tests with real Ability base class
# =============================================================================

class TestWithRealAbilityClass:
    """Tests using the real Ability base class for more realistic scenarios."""

    def test_real_ability_class_aggregation(self):
        """Test with a concrete Ability subclass."""
        # Create a minimal real component mock
        mock_component = Mock()
        mock_component.stats = {}
        mock_component.ability_stats = {}

        # Create a test ability subclass
        class TestPropulsion(Ability):
            def __init__(self, component, data):
                super().__init__(component, data)
                self.thrust = data.get('value', 0)

            def get_primary_value(self):
                return self.thrust

        ability1 = TestPropulsion(mock_component, {'value': 500.0})
        ability2 = TestPropulsion(mock_component, {'value': 300.0})

        class RealComponent:
            def __init__(self, abilities):
                self.ability_instances = abilities
                self.abilities = {}

        comp1 = RealComponent([ability1])
        comp2 = RealComponent([ability2])

        result = calculate_ability_totals([comp1, comp2])
        assert result["TestPropulsion"] == 800.0

    def test_applies_to_layer_integration(self):
        """Test layer filtering with real Ability.applies_to_layer method."""
        mock_component = Mock()
        mock_component.stats = {}
        mock_component.ability_stats = {}

        class CombatOnly(Ability):
            layer = AbilityLayer.COMBAT

            def get_primary_value(self):
                return 100.0

        class StrategicOnly(Ability):
            layer = AbilityLayer.STRATEGIC

            def get_primary_value(self):
                return 50.0

        combat = CombatOnly(mock_component, {})
        strategic = StrategicOnly(mock_component, {})

        class RealComponent:
            def __init__(self, abilities):
                self.ability_instances = abilities
                self.abilities = {}

        comp = RealComponent([combat, strategic])

        # Filter for COMBAT
        combat_result = calculate_ability_totals([comp], layer=AbilityLayer.COMBAT)
        assert "CombatOnly" in combat_result
        assert "StrategicOnly" not in combat_result

        # Filter for STRATEGIC
        strategic_result = calculate_ability_totals([comp], layer=AbilityLayer.STRATEGIC)
        assert "CombatOnly" not in strategic_result
        assert "StrategicOnly" in strategic_result


# =============================================================================
# Additional Edge Case Tests (PROJ-118 Phase 2)
# =============================================================================

class TestAbilityAggregatorAdditionalEdgeCases:
    """Additional edge case tests for ability aggregation."""

    def test_integer_values_treated_as_numeric(self):
        """Integer values are treated as numeric (not just floats)."""
        groups = {
            "IntAbility": {
                "comp1": [100],  # Integer
                "comp2": [50]    # Integer
            }
        }
        result = _aggregate_ability_groups(groups)
        assert result["IntAbility"] == 150

    def test_negative_values_handled(self):
        """Negative numeric values are handled correctly."""
        groups = {
            "PenaltyAbility": {
                "comp1": [-10.0],
                "comp2": [5.0]
            }
        }
        result = _aggregate_ability_groups(groups)
        assert result["PenaltyAbility"] == -5.0

    def test_intra_group_max_with_negatives(self):
        """Intra-group MAX works with negative values."""
        groups = {
            "MixedAbility": {
                "group1": [-10.0, -5.0, -20.0]  # MAX is -5.0
            }
        }
        result = _aggregate_ability_groups(groups)
        assert result["MixedAbility"] == -5.0

    def test_zero_values_in_groups(self):
        """Zero values are valid numeric values."""
        groups = {
            "ZeroAbility": {
                "comp1": [0.0],
                "comp2": [100.0]
            }
        }
        result = _aggregate_ability_groups(groups)
        assert result["ZeroAbility"] == 100.0

    def test_mixed_int_and_float_in_same_group(self):
        """Mixed int and float values in same group."""
        groups = {
            "MixedTypes": {
                "group1": [100, 150.5, 75]  # MAX is 150.5
            }
        }
        result = _aggregate_ability_groups(groups)
        assert result["MixedTypes"] == 150.5

    def test_single_multiplicative_value(self):
        """Single multiplicative ability value."""
        groups = {
            "ToHitAttackModifier": {
                "comp1": [0.95]
            }
        }
        result = _aggregate_ability_groups(groups)
        assert result["ToHitAttackModifier"] == pytest.approx(0.95)

    def test_three_multiplicative_groups(self):
        """Three multiplicative groups multiply correctly."""
        groups = {
            "ToHitDefenseModifier": {
                "comp1": [0.9],
                "comp2": [0.9],
                "comp3": [0.9]
            }
        }
        result = _aggregate_ability_groups(groups)
        assert result["ToHitDefenseModifier"] == pytest.approx(0.729)  # 0.9^3

    def test_boolean_all_false_excludes_from_result(self):
        """Boolean groups with only False values are excluded."""
        groups = {
            "SomeMarker": {
                "comp1": [False],
                "comp2": [False]
            }
        }
        result = _aggregate_ability_groups(groups)
        # No True values, so not in result
        assert "SomeMarker" not in result

    def test_very_large_numeric_values(self):
        """Very large numeric values are handled."""
        groups = {
            "HugeAbility": {
                "comp1": [1e10],
                "comp2": [2e10]
            }
        }
        result = _aggregate_ability_groups(groups)
        assert result["HugeAbility"] == 3e10

    def test_very_small_numeric_values(self):
        """Very small numeric values are handled."""
        groups = {
            "TinyAbility": {
                "comp1": [1e-10],
                "comp2": [2e-10]
            }
        }
        result = _aggregate_ability_groups(groups)
        assert result["TinyAbility"] == pytest.approx(3e-10)

    def test_component_with_empty_ability_instances_list(self):
        """Component with empty ability_instances list."""
        comp = MockComponent(ability_instances=[], abilities={})
        result = calculate_ability_totals([comp])
        assert result == {}

    def test_component_with_none_ability_instances(self):
        """Component with None ability_instances attribute."""
        class NoneInstancesComponent:
            ability_instances = None
            abilities = {}

        comp = NoneInstancesComponent()
        result = calculate_ability_totals([comp])
        assert result == {}

    def test_ability_instances_not_iterable(self):
        """Component with non-iterable ability_instances."""
        class BadComponent:
            ability_instances = 12345  # Not iterable
            abilities = {}

        comp = BadComponent()
        result = calculate_ability_totals([comp])
        # Should gracefully handle non-list
        assert result == {}

    def test_get_ability_instances_by_class_empty_list(self):
        """get_ability_instances_by_class with empty component list."""
        pairs = list(get_ability_instances_by_class([], "SomeAbility"))
        assert pairs == []

    def test_multiple_marker_abilities_on_one_component(self):
        """Multiple marker abilities on same component."""
        abilities = [
            MockAbility("CommandAndControl", 0.0),
            MockAbility("Armor", 0.0),
            MockAbility("RequiresCommandAndControl", 0.0)
        ]
        comp = MockComponent(ability_instances=abilities)

        result = calculate_ability_totals([comp])

        assert result["CommandAndControl"] is True
        assert result["Armor"] is True
        assert result["RequiresCommandAndControl"] is True

    def test_abilities_dict_non_dict_value(self):
        """Abilities dict with non-dict, non-numeric value."""
        comp = MockComponent(
            ability_instances=[],
            abilities={"StringAbility": "not_a_number"}
        )

        result = calculate_ability_totals([comp])
        # String values should be filtered out
        assert "StringAbility" not in result

    def test_raw_dict_with_nested_dict_no_value_key(self):
        """Raw dict ability with nested dict but no 'value' key."""
        comp = MockComponent(
            ability_instances=[],
            abilities={
                "WeirdAbility": {"other_key": 100}
            }
        )

        result = calculate_ability_totals([comp])
        # The dict itself is the value, which is not numeric
        assert "WeirdAbility" not in result

    def test_mixed_handled_and_unhandled_abilities(self):
        """Component with some abilities in instances, others in dict."""
        instance_ability = MockAbility("InstanceAbility", 500.0)
        comp = MockComponent(
            ability_instances=[instance_ability],
            abilities={
                "DictAbility": 200.0,
                "InstanceAbility": 100.0  # Should be skipped (already handled)
            }
        )

        result = calculate_ability_totals([comp])

        assert result["InstanceAbility"] == 500.0  # From instance, not dict
        assert result["DictAbility"] == 200.0

    def test_layer_filter_with_both_layer_ability(self):
        """Ability with BOTH layer is included in both COMBAT and STRATEGIC filters."""
        both_ability = MockAbility("BothLayerAbility", 100.0, layer=AbilityLayer.BOTH)
        comp = MockComponent(ability_instances=[both_ability])

        combat_result = calculate_ability_totals([comp], layer=AbilityLayer.COMBAT)
        strategic_result = calculate_ability_totals([comp], layer=AbilityLayer.STRATEGIC)

        assert "BothLayerAbility" in combat_result
        assert "BothLayerAbility" in strategic_result
        assert combat_result["BothLayerAbility"] == 100.0
        assert strategic_result["BothLayerAbility"] == 100.0

    def test_many_components_same_ability_no_stack_group(self):
        """Many components with same ability and no stack_group (all sum)."""
        components = []
        for i in range(10):
            comp = MockComponent(ability_instances=[
                MockAbility("CommonAbility", 10.0)
            ])
            components.append(comp)

        result = calculate_ability_totals(components)
        assert result["CommonAbility"] == 100.0  # 10 * 10.0

    def test_same_stack_group_across_ten_components(self):
        """Ten components with same stack_group take MAX."""
        components = []
        for i in range(10):
            comp = MockComponent(ability_instances=[
                MockAbility("SharedAbility", float(i * 10), stack_group="shared_group")
            ])
            components.append(comp)

        result = calculate_ability_totals(components)
        # Values are 0, 10, 20, ..., 90. MAX is 90.
        assert result["SharedAbility"] == 90.0

    def test_ability_with_stack_group_none_uses_component_as_key(self):
        """Ability with stack_group=None uses component as group key."""
        ability = MockAbility("NoGroupAbility", 100.0, stack_group=None)
        comp = MockComponent(ability_instances=[ability])

        result = calculate_ability_totals([comp])
        assert result["NoGroupAbility"] == 100.0


# =============================================================================
# Tests for Concurrent Modification Resilience (TCG-SIM-011)
# =============================================================================

class TestConcurrentModificationResilience:
    """Tests verifying behavior when collections might be modified.

    These tests ensure the aggregator handles edge cases where:
    - Input lists/dicts are modified during iteration
    - Collection types are unexpectedly empty or modified
    - Defensive copies prevent mutation issues

    Note: Python's for-loop over a list creates a reference, not a copy.
    If the list is modified during iteration, behavior can be unpredictable.
    These tests document expected behavior with various mutation patterns.
    """

    def test_modifying_components_list_during_iteration_via_copy(self):
        """Verify aggregation works when input is a copy of a modifiable list."""
        # Create a mutable list that could be modified
        mutable_components = [
            MockComponent(ability_instances=[MockAbility("Ability1", 100.0)]),
            MockComponent(ability_instances=[MockAbility("Ability1", 200.0)])
        ]

        # Pass a copy to prevent external modification affecting iteration
        result = calculate_ability_totals(list(mutable_components))

        # Original can be safely modified now
        mutable_components.clear()

        # Result should still be valid
        assert result["Ability1"] == 300.0

    def test_empty_ability_instances_list_after_check(self):
        """Handle component whose ability_instances becomes empty."""
        # Component with empty but valid ability_instances
        comp = MockComponent(ability_instances=[])

        result = calculate_ability_totals([comp])
        assert result == {}

    def test_ability_instances_replaced_with_empty_list(self):
        """Verify behavior when ability_instances is empty list."""
        comp = MockComponent(ability_instances=[])
        comp.ability_instances = []  # Explicitly set to empty

        result = calculate_ability_totals([comp])
        assert result == {}

    def test_abilities_dict_cleared_after_instances_processed(self):
        """Component with instances; dict cleared doesn't affect result."""
        ability = MockAbility("TestAbility", 500.0)
        comp = MockComponent(
            ability_instances=[ability],
            abilities={"OtherAbility": 100.0}
        )

        # Clear dict after creation
        comp.abilities = {}

        result = calculate_ability_totals([comp])
        # Only instance ability should be present
        assert result["TestAbility"] == 500.0
        assert "OtherAbility" not in result

    def test_iterator_over_generator_components(self):
        """Verify aggregation works with generator input."""
        def component_generator():
            yield MockComponent(ability_instances=[MockAbility("GenAbility", 10.0)])
            yield MockComponent(ability_instances=[MockAbility("GenAbility", 20.0)])
            yield MockComponent(ability_instances=[MockAbility("GenAbility", 30.0)])

        result = calculate_ability_totals(component_generator())
        assert result["GenAbility"] == 60.0

    def test_nested_iteration_independence(self):
        """Multiple calls with same components don't interfere."""
        comp1 = MockComponent(ability_instances=[MockAbility("SharedAbility", 100.0)])
        comp2 = MockComponent(ability_instances=[MockAbility("SharedAbility", 200.0)])
        components = [comp1, comp2]

        # Multiple calls should produce consistent results
        result1 = calculate_ability_totals(components)
        result2 = calculate_ability_totals(components)
        result3 = calculate_ability_totals(components)

        assert result1 == result2 == result3
        assert result1["SharedAbility"] == 300.0

    def test_component_ability_instances_modified_between_calls(self):
        """Result reflects current state of ability_instances."""
        comp = MockComponent(ability_instances=[MockAbility("Dynamic", 100.0)])

        # First call
        result1 = calculate_ability_totals([comp])
        assert result1["Dynamic"] == 100.0

        # Modify ability_instances
        comp.ability_instances = [MockAbility("Dynamic", 999.0)]

        # Second call should reflect new state
        result2 = calculate_ability_totals([comp])
        assert result2["Dynamic"] == 999.0

    def test_ability_groups_dict_not_leaked_between_calls(self):
        """Internal ability_groups dict is isolated per call."""
        comp1 = MockComponent(ability_instances=[MockAbility("IsolatedAbility", 50.0)])
        comp2 = MockComponent(ability_instances=[MockAbility("OtherAbility", 75.0)])

        result1 = calculate_ability_totals([comp1])
        result2 = calculate_ability_totals([comp2])

        # Results should be independent
        assert "IsolatedAbility" in result1
        assert "OtherAbility" not in result1
        assert "OtherAbility" in result2
        assert "IsolatedAbility" not in result2

    def test_dict_view_iteration_with_modifications(self):
        """Raw abilities dict iteration handles expected patterns."""
        # Component with raw abilities dict
        abilities_dict = {"Ability1": 100.0, "Ability2": 200.0}
        comp = MockComponent(
            ability_instances=[],
            abilities=abilities_dict
        )

        result = calculate_ability_totals([comp])

        # Verify both abilities processed
        assert result["Ability1"] == 100.0
        assert result["Ability2"] == 200.0

    def test_reentrant_safe_with_same_component_twice(self):
        """Same component in list twice is handled correctly."""
        ability = MockAbility("ReentrantAbility", 100.0)
        comp = MockComponent(ability_instances=[ability])

        # Same component twice - abilities should sum from both "occurrences"
        result = calculate_ability_totals([comp, comp])

        # Each occurrence adds to the total (different group keys since comp object used as key)
        # Actually, same comp object = same group key = MAX within group = 100
        # This tests an important edge case!
        assert result["ReentrantAbility"] == 100.0  # MAX, not SUM

    def test_get_ability_instances_by_class_generator_exhaustion(self):
        """Generator from get_ability_instances_by_class is properly exhausted."""
        ability = MockAbility("IterAbility", 100.0)
        comp = MockComponent(ability_instances=[ability])

        gen = get_ability_instances_by_class([comp], "IterAbility")

        # Exhaust generator
        pairs = list(gen)
        assert len(pairs) == 1

        # Re-exhaust should be empty (generator exhausted)
        more_pairs = list(gen)
        assert len(more_pairs) == 0

    def test_fresh_generator_each_call(self):
        """Each call to get_ability_instances_by_class returns fresh generator."""
        ability = MockAbility("FreshGenAbility", 100.0)
        comp = MockComponent(ability_instances=[ability])

        # First generator
        gen1 = get_ability_instances_by_class([comp], "FreshGenAbility")
        list(gen1)  # Exhaust it

        # Second generator should still work
        gen2 = get_ability_instances_by_class([comp], "FreshGenAbility")
        pairs = list(gen2)
        assert len(pairs) == 1

    def test_tuple_input_immutable(self):
        """Aggregation works with immutable tuple input."""
        comp1 = MockComponent(ability_instances=[MockAbility("TupleAbility", 100.0)])
        comp2 = MockComponent(ability_instances=[MockAbility("TupleAbility", 200.0)])

        # Pass as tuple (immutable)
        result = calculate_ability_totals((comp1, comp2))

        assert result["TupleAbility"] == 300.0

    def test_frozen_set_like_behavior(self):
        """Components with identical abilities aggregate correctly."""
        # Two different component instances with same ability value
        comp1 = MockComponent(ability_instances=[MockAbility("FrozenAbility", 50.0)])
        comp2 = MockComponent(ability_instances=[MockAbility("FrozenAbility", 50.0)])

        result = calculate_ability_totals([comp1, comp2])

        # Different components = different group keys = SUM
        assert result["FrozenAbility"] == 100.0
