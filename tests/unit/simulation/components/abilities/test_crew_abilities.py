"""
Unit tests for crew abilities.

Tests CrewCapacity, LifeSupportCapacity, and RequiresMaintenance ability classes.

Addresses TCG-SIM-018 / UNK-03: Crew ability classes have minimal test coverage.
"""
import pytest
from unittest.mock import MagicMock
import math

from game.simulation.components.abilities.crew import (
    CrewCapacity,
    LifeSupportCapacity,
    RequiresMaintenance,
)
from game.simulation.components.abilities.stat_keys import StatKey
from game.simulation.components.abilities.ui_colors import (
    HINT_CREW_CAP,
    HINT_LIFE_SUPPORT,
    HINT_CREW_REQ,
)


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_component():
    """Create a mock component with default empty stats."""
    component = MagicMock()
    component.stats = {}
    component.ability_stats = {}
    return component


@pytest.fixture
def mock_component_with_stats():
    """Factory fixture for creating component with specific stats."""
    def _create(stats=None, ability_stats=None):
        component = MagicMock()
        component.stats = stats or {}
        component.ability_stats = ability_stats or {}
        return component
    return _create


# =============================================================================
# CrewCapacity Tests
# =============================================================================

class TestCrewCapacity:
    """Tests for CrewCapacity ability class."""

    def test_init_with_numeric_value(self, mock_component):
        """Initialize with a simple numeric value."""
        ability = CrewCapacity(mock_component, 10)

        assert ability.amount == 10
        assert ability._base_amount == 10
        assert isinstance(ability.amount, int)

    def test_init_with_dict_value(self, mock_component):
        """Initialize with dict containing 'value' key."""
        data = {'value': 25}
        ability = CrewCapacity(mock_component, data)

        assert ability.amount == 25
        assert ability._base_amount == 25

    def test_init_with_dict_missing_value(self, mock_component):
        """Initialize with dict without 'value' key defaults to 0."""
        data = {'other_key': 'ignored'}
        ability = CrewCapacity(mock_component, data)

        assert ability.amount == 0
        assert ability._base_amount == 0

    def test_init_with_float_truncates(self, mock_component):
        """Initialize with float truncates to int."""
        ability = CrewCapacity(mock_component, 15.9)

        assert ability.amount == 15
        assert isinstance(ability.amount, int)

    def test_init_with_zero(self, mock_component):
        """Initialize with zero value."""
        ability = CrewCapacity(mock_component, 0)

        assert ability.amount == 0
        assert ability._base_amount == 0

    def test_recalculate_no_modifier(self, mock_component):
        """recalculate with no modifier keeps base amount."""
        ability = CrewCapacity(mock_component, 10)

        ability.recalculate()

        assert ability.amount == 10

    def test_recalculate_with_crew_capacity_mult(self, mock_component_with_stats):
        """recalculate applies crew_capacity_mult from component stats."""
        component = mock_component_with_stats(stats={'crew_capacity_mult': 1.5})
        ability = CrewCapacity(component, 10)

        ability.recalculate()

        assert ability.amount == 15  # 10 * 1.5 = 15

    def test_recalculate_with_doubled_modifier(self, mock_component_with_stats):
        """recalculate with 2x multiplier doubles capacity."""
        component = mock_component_with_stats(stats={'crew_capacity_mult': 2.0})
        ability = CrewCapacity(component, 8)

        ability.recalculate()

        assert ability.amount == 16

    def test_recalculate_with_reduced_modifier(self, mock_component_with_stats):
        """recalculate with <1 multiplier reduces capacity."""
        component = mock_component_with_stats(stats={'crew_capacity_mult': 0.5})
        ability = CrewCapacity(component, 10)

        ability.recalculate()

        assert ability.amount == 5

    def test_recalculate_truncates_to_int(self, mock_component_with_stats):
        """recalculate result is truncated to int."""
        component = mock_component_with_stats(stats={'crew_capacity_mult': 1.9})
        ability = CrewCapacity(component, 5)

        ability.recalculate()

        # 5 * 1.9 = 9.5 -> int(9.5) = 9
        assert ability.amount == 9
        assert isinstance(ability.amount, int)

    def test_recalculate_preserves_base_amount(self, mock_component_with_stats):
        """recalculate does not modify _base_amount."""
        component = mock_component_with_stats(stats={'crew_capacity_mult': 2.0})
        ability = CrewCapacity(component, 10)

        ability.recalculate()

        assert ability._base_amount == 10
        assert ability.amount == 20

    def test_get_ui_rows_format(self, mock_component):
        """get_ui_rows returns correct format."""
        ability = CrewCapacity(mock_component, 15)

        rows = ability.get_ui_rows()

        assert len(rows) == 1
        assert rows[0]['label'] == 'Crew Cap'
        assert rows[0]['value'] == '15'
        assert rows[0]['color_hint'] == HINT_CREW_CAP

    def test_get_ui_rows_zero(self, mock_component):
        """get_ui_rows displays zero correctly."""
        ability = CrewCapacity(mock_component, 0)

        rows = ability.get_ui_rows()

        assert rows[0]['value'] == '0'

    def test_get_primary_value(self, mock_component):
        """get_primary_value returns amount as float."""
        ability = CrewCapacity(mock_component, 20)

        assert ability.get_primary_value() == 20.0
        assert isinstance(ability.get_primary_value(), float)

    def test_stat_bindings_defined(self):
        """STAT_BINDINGS contains crew_capacity_mult binding."""
        assert len(CrewCapacity.STAT_BINDINGS) == 1
        binding = CrewCapacity.STAT_BINDINGS[0]
        assert binding.stat_key == StatKey.CREW_CAPACITY_MULT
        assert binding.attribute_name == 'amount'
        assert binding.operation == 'multiply'


# =============================================================================
# LifeSupportCapacity Tests
# =============================================================================

class TestLifeSupportCapacity:
    """Tests for LifeSupportCapacity ability class."""

    def test_init_with_numeric_value(self, mock_component):
        """Initialize with a simple numeric value."""
        ability = LifeSupportCapacity(mock_component, 30)

        assert ability.amount == 30
        assert ability._base_amount == 30
        assert isinstance(ability.amount, int)

    def test_init_with_dict_value(self, mock_component):
        """Initialize with dict containing 'value' key."""
        data = {'value': 50}
        ability = LifeSupportCapacity(mock_component, data)

        assert ability.amount == 50

    def test_init_with_dict_missing_value(self, mock_component):
        """Initialize with dict without 'value' key defaults to 0."""
        data = {'other': 'data'}
        ability = LifeSupportCapacity(mock_component, data)

        assert ability.amount == 0

    def test_init_with_float_truncates(self, mock_component):
        """Initialize with float truncates to int."""
        ability = LifeSupportCapacity(mock_component, 25.7)

        assert ability.amount == 25
        assert isinstance(ability.amount, int)

    def test_init_with_zero(self, mock_component):
        """Initialize with zero value."""
        ability = LifeSupportCapacity(mock_component, 0)

        assert ability.amount == 0

    def test_recalculate_no_modifier(self, mock_component):
        """recalculate with no modifier keeps base amount."""
        ability = LifeSupportCapacity(mock_component, 20)

        ability.recalculate()

        assert ability.amount == 20

    def test_recalculate_with_life_support_mult(self, mock_component_with_stats):
        """recalculate applies life_support_capacity_mult from component stats."""
        component = mock_component_with_stats(stats={'life_support_capacity_mult': 1.5})
        ability = LifeSupportCapacity(component, 20)

        ability.recalculate()

        assert ability.amount == 30  # 20 * 1.5 = 30

    def test_recalculate_with_doubled_modifier(self, mock_component_with_stats):
        """recalculate with 2x multiplier doubles capacity."""
        component = mock_component_with_stats(stats={'life_support_capacity_mult': 2.0})
        ability = LifeSupportCapacity(component, 15)

        ability.recalculate()

        assert ability.amount == 30

    def test_recalculate_with_reduced_modifier(self, mock_component_with_stats):
        """recalculate with <1 multiplier reduces capacity."""
        component = mock_component_with_stats(stats={'life_support_capacity_mult': 0.5})
        ability = LifeSupportCapacity(component, 40)

        ability.recalculate()

        assert ability.amount == 20

    def test_recalculate_truncates_to_int(self, mock_component_with_stats):
        """recalculate result is truncated to int."""
        component = mock_component_with_stats(stats={'life_support_capacity_mult': 1.3})
        ability = LifeSupportCapacity(component, 10)

        ability.recalculate()

        # 10 * 1.3 = 13
        assert ability.amount == 13

    def test_recalculate_preserves_base_amount(self, mock_component_with_stats):
        """recalculate does not modify _base_amount."""
        component = mock_component_with_stats(stats={'life_support_capacity_mult': 3.0})
        ability = LifeSupportCapacity(component, 10)

        ability.recalculate()

        assert ability._base_amount == 10
        assert ability.amount == 30

    def test_get_ui_rows_format(self, mock_component):
        """get_ui_rows returns correct format."""
        ability = LifeSupportCapacity(mock_component, 40)

        rows = ability.get_ui_rows()

        assert len(rows) == 1
        assert rows[0]['label'] == 'Life Support'
        assert rows[0]['value'] == '40'
        assert rows[0]['color_hint'] == HINT_LIFE_SUPPORT

    def test_get_primary_value(self, mock_component):
        """get_primary_value returns amount as float."""
        ability = LifeSupportCapacity(mock_component, 25)

        assert ability.get_primary_value() == 25.0
        assert isinstance(ability.get_primary_value(), float)

    def test_stat_bindings_defined(self):
        """STAT_BINDINGS contains life_support_capacity_mult binding."""
        assert len(LifeSupportCapacity.STAT_BINDINGS) == 1
        binding = LifeSupportCapacity.STAT_BINDINGS[0]
        assert binding.stat_key == StatKey.LIFE_SUPPORT_CAPACITY_MULT
        assert binding.attribute_name == 'amount'
        assert binding.operation == 'multiply'


# =============================================================================
# RequiresMaintenance Tests
# =============================================================================

class TestRequiresMaintenance:
    """Tests for RequiresMaintenance ability class."""

    def test_init_with_numeric_value(self, mock_component):
        """Initialize with a simple numeric value."""
        ability = RequiresMaintenance(mock_component, 5)

        assert ability.amount == 5
        assert ability._base_amount == 5
        assert isinstance(ability.amount, int)

    def test_init_with_dict_value_key(self, mock_component):
        """Initialize with dict containing 'value' key."""
        data = {'value': 8}
        ability = RequiresMaintenance(mock_component, data)

        assert ability.amount == 8

    def test_init_with_dict_amount_key(self, mock_component):
        """Initialize with dict containing 'amount' key."""
        data = {'amount': 12}
        ability = RequiresMaintenance(mock_component, data)

        assert ability.amount == 12

    def test_init_with_dict_value_takes_priority(self, mock_component):
        """'value' key takes priority over 'amount' key."""
        data = {'value': 5, 'amount': 10}
        ability = RequiresMaintenance(mock_component, data)

        assert ability.amount == 5

    def test_init_with_float_truncates(self, mock_component):
        """Initialize with float truncates to int."""
        ability = RequiresMaintenance(mock_component, 7.8)

        assert ability.amount == 7
        assert isinstance(ability.amount, int)

    def test_init_with_zero(self, mock_component):
        """Initialize with zero value."""
        ability = RequiresMaintenance(mock_component, 0)

        assert ability.amount == 0

    def test_recalculate_no_modifier(self, mock_component):
        """recalculate with no modifier keeps base amount (using sqrt of 1.0)."""
        ability = RequiresMaintenance(mock_component, 5)

        ability.recalculate()

        # sqrt(1.0) * 1.0 * 5 = 5
        assert ability.amount == 5

    def test_recalculate_with_mass_mult(self, mock_component_with_stats):
        """recalculate applies sqrt(mass_mult) scaling."""
        component = mock_component_with_stats(stats={'mass_mult': 4.0})
        ability = RequiresMaintenance(component, 5)

        ability.recalculate()

        # sqrt(4.0) = 2.0, 5 * 2.0 = 10, ceil(10) = 10
        assert ability.amount == 10

    def test_recalculate_with_crew_req_mult(self, mock_component_with_stats):
        """recalculate applies crew_req_mult."""
        component = mock_component_with_stats(stats={'crew_req_mult': 2.0})
        ability = RequiresMaintenance(component, 5)

        ability.recalculate()

        # sqrt(1.0) * 5 * 2.0 = 10
        assert ability.amount == 10

    def test_recalculate_with_both_multipliers(self, mock_component_with_stats):
        """recalculate applies both mass_mult (sqrt) and crew_req_mult."""
        component = mock_component_with_stats(stats={
            'mass_mult': 4.0,  # sqrt = 2.0
            'crew_req_mult': 1.5
        })
        ability = RequiresMaintenance(component, 10)

        ability.recalculate()

        # 10 * sqrt(4.0) * 1.5 = 10 * 2.0 * 1.5 = 30
        assert ability.amount == 30

    def test_recalculate_uses_ceiling(self, mock_component_with_stats):
        """recalculate uses ceiling for fractional results."""
        component = mock_component_with_stats(stats={'mass_mult': 2.0})
        ability = RequiresMaintenance(component, 3)

        ability.recalculate()

        # sqrt(2.0) = 1.414, 3 * 1.414 = 4.24, ceil(4.24) = 5
        expected = int(math.ceil(3 * math.sqrt(2.0)))
        assert ability.amount == expected

    def test_recalculate_negative_mass_mult_clamped(self, mock_component_with_stats):
        """Negative mass_mult is clamped to 0."""
        component = mock_component_with_stats(stats={'mass_mult': -5.0})
        ability = RequiresMaintenance(component, 10)

        ability.recalculate()

        # mass_mult clamped to 0, sqrt(0) = 0, 10 * 0 * 1 = 0
        assert ability.amount == 0

    def test_recalculate_preserves_base_amount(self, mock_component_with_stats):
        """recalculate does not modify _base_amount."""
        component = mock_component_with_stats(stats={'mass_mult': 4.0})
        ability = RequiresMaintenance(component, 5)

        ability.recalculate()

        assert ability._base_amount == 5
        assert ability.amount == 10

    def test_get_ui_rows_format(self, mock_component):
        """get_ui_rows returns correct format."""
        ability = RequiresMaintenance(mock_component, 8)

        rows = ability.get_ui_rows()

        assert len(rows) == 1
        assert rows[0]['label'] == 'Maint Req'
        assert rows[0]['value'] == '8'
        assert rows[0]['color_hint'] == HINT_CREW_REQ

    def test_get_ui_rows_zero(self, mock_component):
        """get_ui_rows displays zero correctly."""
        ability = RequiresMaintenance(mock_component, 0)

        rows = ability.get_ui_rows()

        assert rows[0]['value'] == '0'

    def test_get_primary_value(self, mock_component):
        """get_primary_value returns amount as float."""
        ability = RequiresMaintenance(mock_component, 7)

        assert ability.get_primary_value() == 7.0
        assert isinstance(ability.get_primary_value(), float)

    def test_stat_bindings_defined(self):
        """STAT_BINDINGS contains crew_req_mult binding."""
        assert len(RequiresMaintenance.STAT_BINDINGS) == 1
        binding = RequiresMaintenance.STAT_BINDINGS[0]
        assert binding.stat_key == StatKey.CREW_REQ_MULT
        assert binding.attribute_name == 'amount'
        assert binding.operation == 'multiply'


# =============================================================================
# Edge Case Tests (Cross-class)
# =============================================================================

class TestCrewAbilitiesEdgeCases:
    """Edge case tests across all crew abilities."""

    def test_crew_capacity_large_value(self, mock_component):
        """CrewCapacity handles very large values."""
        ability = CrewCapacity(mock_component, 10000)

        assert ability.amount == 10000

    def test_life_support_large_value(self, mock_component):
        """LifeSupportCapacity handles very large values."""
        ability = LifeSupportCapacity(mock_component, 50000)

        assert ability.amount == 50000

    def test_crew_required_zero_base(self, mock_component_with_stats):
        """RequiresMaintenance with zero base stays zero regardless of multipliers."""
        component = mock_component_with_stats(stats={'mass_mult': 4.0, 'crew_req_mult': 2.0})
        ability = RequiresMaintenance(component, 0)

        ability.recalculate()

        assert ability.amount == 0

    def test_crew_capacity_zero_multiplier(self, mock_component_with_stats):
        """CrewCapacity handles zero multiplier."""
        component = mock_component_with_stats(stats={'crew_capacity_mult': 0.0})
        ability = CrewCapacity(component, 20)

        ability.recalculate()

        assert ability.amount == 0

    def test_life_support_zero_multiplier(self, mock_component_with_stats):
        """LifeSupportCapacity handles zero multiplier."""
        component = mock_component_with_stats(stats={'life_support_capacity_mult': 0.0})
        ability = LifeSupportCapacity(component, 30)

        ability.recalculate()

        assert ability.amount == 0

    def test_crew_required_very_large_mass_mult(self, mock_component_with_stats):
        """RequiresMaintenance handles very large mass_mult (sqrt scaling prevents explosion)."""
        component = mock_component_with_stats(stats={'mass_mult': 10000.0})
        ability = RequiresMaintenance(component, 5)

        ability.recalculate()

        # sqrt(10000) = 100, 5 * 100 = 500
        assert ability.amount == 500

    def test_ability_component_reference(self, mock_component):
        """All crew abilities store reference to component."""
        crew_cap = CrewCapacity(mock_component, 10)
        life_sup = LifeSupportCapacity(mock_component, 20)
        crew_req = RequiresMaintenance(mock_component, 5)

        assert crew_cap.component is mock_component
        assert life_sup.component is mock_component
        assert crew_req.component is mock_component

    def test_crew_required_fractional_input_ceiling(self, mock_component_with_stats):
        """RequiresMaintenance rounds up any fractional crew requirement."""
        component = mock_component_with_stats(stats={'mass_mult': 1.21})  # sqrt = 1.1
        ability = RequiresMaintenance(component, 1)

        ability.recalculate()

        # 1 * 1.1 = 1.1, ceil(1.1) = 2
        assert ability.amount == 2

    def test_recalculate_multiple_times(self, mock_component_with_stats):
        """Multiple recalculate calls always use _base_amount."""
        component = mock_component_with_stats(stats={'crew_capacity_mult': 1.5})
        ability = CrewCapacity(component, 10)

        ability.recalculate()
        assert ability.amount == 15

        # Change modifier and recalculate again
        component.stats['crew_capacity_mult'] = 2.0
        ability.recalculate()

        # Should be base * new_mult, not 15 * 2
        assert ability.amount == 20
