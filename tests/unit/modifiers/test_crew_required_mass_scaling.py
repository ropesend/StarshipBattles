"""
Tests for CrewRequired ability's non-standard mass_mult handling.

Task 9.4: Verify the documented behavior where CrewRequired uses
sqrt(mass_mult) instead of direct multiplication.
"""
import pytest
import math
from unittest.mock import MagicMock

from game.simulation.components.abilities.crew import CrewRequired
from game.simulation.components.abilities.stat_keys import StatKey


class TestCrewRequiredMassScaling:
    """Tests for CrewRequired's sqrt-based mass scaling."""

    def test_crew_required_scales_with_sqrt_of_mass_mult(self):
        """Crew requirement should scale with sqrt(mass_mult), not mass_mult directly."""
        mock_component = MagicMock()
        mock_component.stats = {'mass_mult': 4.0, 'crew_req_mult': 1.0}
        mock_component.ability_stats = {}

        ability = CrewRequired(mock_component, {'value': 10})
        ability.recalculate()

        # sqrt(4.0) = 2.0, so crew should be 10 * 2.0 = 20
        assert ability.amount == 20, \
            f"Expected crew=20 (10 * sqrt(4)), got {ability.amount}"

    def test_crew_required_combines_mass_and_crew_multipliers(self):
        """Crew requirement should combine sqrt(mass_mult) AND crew_req_mult."""
        mock_component = MagicMock()
        mock_component.stats = {'mass_mult': 4.0, 'crew_req_mult': 0.5}
        mock_component.ability_stats = {}

        ability = CrewRequired(mock_component, {'value': 10})
        ability.recalculate()

        # sqrt(4.0) * 0.5 = 2.0 * 0.5 = 1.0, so crew should be 10 * 1.0 = 10
        assert ability.amount == 10, \
            f"Expected crew=10 (10 * sqrt(4) * 0.5), got {ability.amount}"

    def test_crew_required_no_mass_modifier(self):
        """Without mass modifier, crew should just use crew_req_mult."""
        mock_component = MagicMock()
        mock_component.stats = {'crew_req_mult': 2.0}  # No mass_mult
        mock_component.ability_stats = {}

        ability = CrewRequired(mock_component, {'value': 10})
        ability.recalculate()

        # mass_mult defaults to 1.0, sqrt(1.0) = 1.0
        # crew should be 10 * 1.0 * 2.0 = 20
        assert ability.amount == 20, \
            f"Expected crew=20 (10 * 1 * 2), got {ability.amount}"

    def test_crew_required_mass_mult_nine(self):
        """Test with mass_mult=9 to verify sqrt(9)=3."""
        mock_component = MagicMock()
        mock_component.stats = {'mass_mult': 9.0, 'crew_req_mult': 1.0}
        mock_component.ability_stats = {}

        ability = CrewRequired(mock_component, {'value': 10})
        ability.recalculate()

        # sqrt(9.0) = 3.0, so crew should be 10 * 3.0 = 30
        assert ability.amount == 30, \
            f"Expected crew=30 (10 * sqrt(9)), got {ability.amount}"

    def test_crew_required_handles_negative_mass_mult(self):
        """Negative mass_mult should be clamped to 0 (sqrt of 0 = 0)."""
        mock_component = MagicMock()
        mock_component.stats = {'mass_mult': -4.0, 'crew_req_mult': 1.0}
        mock_component.ability_stats = {}

        ability = CrewRequired(mock_component, {'value': 10})
        ability.recalculate()

        # Negative mass_mult is clamped to 0, sqrt(0) = 0
        # crew should be ceil(10 * 0 * 1) = 0
        assert ability.amount == 0, \
            f"Expected crew=0 (negative mass clamped), got {ability.amount}"

    def test_crew_required_rounds_up(self):
        """Crew requirement should round up (ceil) to whole number."""
        mock_component = MagicMock()
        mock_component.stats = {'mass_mult': 2.0, 'crew_req_mult': 1.0}
        mock_component.ability_stats = {}

        ability = CrewRequired(mock_component, {'value': 10})
        ability.recalculate()

        # sqrt(2.0) ≈ 1.414, so crew should be ceil(10 * 1.414) = ceil(14.14) = 15
        expected = int(math.ceil(10 * math.sqrt(2.0)))
        assert ability.amount == expected, \
            f"Expected crew={expected} (ceil of 10 * sqrt(2)), got {ability.amount}"


class TestCrewRequiredStatBindings:
    """Tests verifying STAT_BINDINGS is correctly configured."""

    def test_crew_req_mult_in_stat_bindings(self):
        """STAT_BINDINGS should include crew_req_mult."""
        stat_keys = [b.stat_key for b in CrewRequired.STAT_BINDINGS]
        assert StatKey.CREW_REQ_MULT in stat_keys, \
            "CrewRequired.STAT_BINDINGS should include CREW_REQ_MULT"

    def test_mass_mult_not_in_stat_bindings(self):
        """STAT_BINDINGS should NOT include mass_mult (uses custom sqrt handling)."""
        stat_keys = [b.stat_key for b in CrewRequired.STAT_BINDINGS]
        assert StatKey.MASS_MULT not in stat_keys, \
            "CrewRequired.STAT_BINDINGS should NOT include MASS_MULT (uses custom sqrt handling)"

    def test_class_docstring_documents_mass_mult_handling(self):
        """Class docstring should document the non-standard mass_mult handling."""
        docstring = CrewRequired.__doc__
        assert docstring is not None, "CrewRequired should have a docstring"
        assert 'mass_mult' in docstring.lower(), \
            "Docstring should mention mass_mult"
        assert 'sqrt' in docstring.lower(), \
            "Docstring should mention sqrt scaling"
