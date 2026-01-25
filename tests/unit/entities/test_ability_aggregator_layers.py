"""
Tests for layer-aware ability aggregation.

TDD Phase 1, Step 1.2: Tests for calculate_ability_totals_for_layer().
"""

import pytest
from unittest.mock import MagicMock

from game.simulation.components.abilities.base import Ability, AbilityLayer, AbilityScope


class MockCombatAbility(Ability):
    """Test ability that only applies to COMBAT layer."""
    layer = AbilityLayer.COMBAT
    allowed_scopes = [AbilityScope.SELF]
    default_scope = AbilityScope.SELF

    def __init__(self, component, data):
        super().__init__(component, data)
        self.value = data if isinstance(data, (int, float)) else data.get('value', 0)

    def get_primary_value(self) -> float:
        return float(self.value)


class MockStrategicAbility(Ability):
    """Test ability that only applies to STRATEGIC layer."""
    layer = AbilityLayer.STRATEGIC
    allowed_scopes = [AbilityScope.SELF, AbilityScope.ALLIED_SYSTEM]
    default_scope = AbilityScope.SELF

    def __init__(self, component, data):
        super().__init__(component, data)
        self.value = data if isinstance(data, (int, float)) else data.get('value', 0)

    def get_primary_value(self) -> float:
        return float(self.value)


class MockDualLayerAbility(Ability):
    """Test ability that applies to BOTH layers."""
    layer = AbilityLayer.BOTH
    allowed_scopes = [AbilityScope.SELF]
    default_scope = AbilityScope.SELF

    def __init__(self, component, data):
        super().__init__(component, data)
        self.value = data if isinstance(data, (int, float)) else data.get('value', 0)

    def get_primary_value(self) -> float:
        return float(self.value)


class MockComponent:
    """Mock component with ability_instances list."""

    def __init__(self, abilities=None):
        self.ability_instances = abilities or []
        self.abilities = {}  # Raw dict (not used in these tests)


class TestCalculateAbilityTotalsForLayer:
    """Tests for the calculate_ability_totals_for_layer() function."""

    def test_calculate_totals_for_combat_layer(self):
        """Should only include COMBAT layer abilities when filtering for COMBAT."""
        from game.simulation.entities.ability_aggregator import calculate_ability_totals_for_layer

        mock_component = MagicMock()

        # Create components with mixed abilities
        combat_ability = MockCombatAbility(mock_component, 100)
        strategic_ability = MockStrategicAbility(mock_component, 200)
        dual_ability = MockDualLayerAbility(mock_component, 50)

        comp = MockComponent([combat_ability, strategic_ability, dual_ability])

        # Get totals for COMBAT layer
        totals = calculate_ability_totals_for_layer([comp], AbilityLayer.COMBAT)

        # Should include combat and dual, exclude strategic
        assert 'MockCombatAbility' in totals
        assert totals['MockCombatAbility'] == 100

        assert 'MockDualLayerAbility' in totals
        assert totals['MockDualLayerAbility'] == 50

        assert 'MockStrategicAbility' not in totals

    def test_calculate_totals_for_strategic_layer(self):
        """Should only include STRATEGIC layer abilities when filtering for STRATEGIC."""
        from game.simulation.entities.ability_aggregator import calculate_ability_totals_for_layer

        mock_component = MagicMock()

        combat_ability = MockCombatAbility(mock_component, 100)
        strategic_ability = MockStrategicAbility(mock_component, 200)
        dual_ability = MockDualLayerAbility(mock_component, 50)

        comp = MockComponent([combat_ability, strategic_ability, dual_ability])

        # Get totals for STRATEGIC layer
        totals = calculate_ability_totals_for_layer([comp], AbilityLayer.STRATEGIC)

        # Should include strategic and dual, exclude combat
        assert 'MockStrategicAbility' in totals
        assert totals['MockStrategicAbility'] == 200

        assert 'MockDualLayerAbility' in totals
        assert totals['MockDualLayerAbility'] == 50

        assert 'MockCombatAbility' not in totals

    def test_calculate_totals_excludes_wrong_layer(self):
        """Should completely exclude abilities from the wrong layer."""
        from game.simulation.entities.ability_aggregator import calculate_ability_totals_for_layer

        mock_component = MagicMock()

        # Only combat abilities
        combat_ability1 = MockCombatAbility(mock_component, 100)
        combat_ability2 = MockCombatAbility(mock_component, 150)

        comp = MockComponent([combat_ability1, combat_ability2])

        # Get totals for STRATEGIC layer
        totals = calculate_ability_totals_for_layer([comp], AbilityLayer.STRATEGIC)

        # Should be empty - no strategic abilities
        assert 'MockCombatAbility' not in totals
        assert len(totals) == 0

    def test_calculate_totals_with_scope_filter(self):
        """Should filter by scope when scope_filter is provided."""
        from game.simulation.entities.ability_aggregator import calculate_ability_totals_for_layer

        mock_component = MagicMock()

        # Create abilities with different scopes
        self_scoped = MockStrategicAbility(mock_component, {'value': 100, 'scope': 'self'})
        system_scoped = MockStrategicAbility(mock_component, {'value': 200, 'scope': 'allied_system'})

        comp = MockComponent([self_scoped, system_scoped])

        # Filter for only ALLIED_SYSTEM scope
        totals = calculate_ability_totals_for_layer(
            [comp],
            AbilityLayer.STRATEGIC,
            scope_filter=AbilityScope.ALLIED_SYSTEM
        )

        # Should only include the system-scoped ability
        assert 'MockStrategicAbility' in totals
        assert totals['MockStrategicAbility'] == 200

    def test_calculate_totals_aggregates_multiple_components(self):
        """Should aggregate abilities across multiple components."""
        from game.simulation.entities.ability_aggregator import calculate_ability_totals_for_layer

        mock_component = MagicMock()

        combat1 = MockCombatAbility(mock_component, 100)
        combat2 = MockCombatAbility(mock_component, 150)

        comp1 = MockComponent([combat1])
        comp2 = MockComponent([combat2])

        totals = calculate_ability_totals_for_layer([comp1, comp2], AbilityLayer.COMBAT)

        # Should sum both combat abilities
        assert 'MockCombatAbility' in totals
        assert totals['MockCombatAbility'] == 250

    def test_calculate_totals_empty_components_list(self):
        """Should return empty dict for empty components list."""
        from game.simulation.entities.ability_aggregator import calculate_ability_totals_for_layer

        totals = calculate_ability_totals_for_layer([], AbilityLayer.COMBAT)

        assert totals == {}

    def test_calculate_totals_respects_stack_groups(self):
        """Should respect stack_group aggregation rules (MAX within group)."""
        from game.simulation.entities.ability_aggregator import calculate_ability_totals_for_layer

        mock_component = MagicMock()

        # Create abilities with same stack group
        combat1 = MockCombatAbility(mock_component, {'value': 100, 'stack_group': 'engines'})
        combat2 = MockCombatAbility(mock_component, {'value': 150, 'stack_group': 'engines'})

        comp = MockComponent([combat1, combat2])

        totals = calculate_ability_totals_for_layer([comp], AbilityLayer.COMBAT)

        # With same stack_group, should take MAX (150), not sum
        assert 'MockCombatAbility' in totals
        assert totals['MockCombatAbility'] == 150


class TestBackwardCompatibility:
    """Tests to ensure the original calculate_ability_totals still works."""

    def test_original_function_unchanged(self):
        """Original calculate_ability_totals should still exist and work."""
        from game.simulation.entities.ability_aggregator import calculate_ability_totals

        mock_component = MagicMock()
        combat_ability = MockCombatAbility(mock_component, 100)

        comp = MockComponent([combat_ability])

        # Original function should work without layer filter
        totals = calculate_ability_totals([comp])

        assert 'MockCombatAbility' in totals
        assert totals['MockCombatAbility'] == 100


class TestAggregateAbilityGroups:
    """Tests for the _aggregate_ability_groups helper function (SIM-08 refactoring)."""

    def test_aggregate_groups_sums_by_default(self):
        """Should sum values from different groups by default."""
        from game.simulation.entities.ability_aggregator import _aggregate_ability_groups

        ability_groups = {
            'Thrust': {
                'engine1': [100],
                'engine2': [150]
            }
        }

        totals = _aggregate_ability_groups(ability_groups)
        assert totals['Thrust'] == 250

    def test_aggregate_groups_takes_max_within_group(self):
        """Should take MAX value within same group (redundancy)."""
        from game.simulation.entities.ability_aggregator import _aggregate_ability_groups

        ability_groups = {
            'Thrust': {
                'main_engines': [100, 150, 120]  # Multiple values in same group
            }
        }

        totals = _aggregate_ability_groups(ability_groups)
        assert totals['Thrust'] == 150  # MAX of the group

    def test_aggregate_groups_multiplies_for_special_abilities(self):
        """Should multiply values for ToHitAttackModifier and ToHitDefenseModifier."""
        from game.simulation.entities.ability_aggregator import _aggregate_ability_groups

        ability_groups = {
            'ToHitDefenseModifier': {
                'ecm': [2.0],
                'scattering': [1.5]
            }
        }

        totals = _aggregate_ability_groups(ability_groups)
        assert totals['ToHitDefenseModifier'] == pytest.approx(3.0)  # 2.0 * 1.5

    def test_aggregate_groups_handles_boolean_marker_abilities(self):
        """Should return True if any group contributes True."""
        from game.simulation.entities.ability_aggregator import _aggregate_ability_groups

        ability_groups = {
            'Armor': {
                'armor1': [True],
                'armor2': [True]
            }
        }

        totals = _aggregate_ability_groups(ability_groups)
        assert totals['Armor'] is True

    def test_aggregate_groups_empty_returns_empty(self):
        """Should return empty dict for empty input."""
        from game.simulation.entities.ability_aggregator import _aggregate_ability_groups

        totals = _aggregate_ability_groups({})
        assert totals == {}
