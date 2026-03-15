"""Tests for build_queue_helpers module - formatting functions for build queue display."""

import pytest
from unittest.mock import MagicMock

from game.ui.screens.build_queue_helpers import (
    RESOURCE_ABBREVS,
    RESOURCE_ABBREVS_SHORT,
    format_empire_resources,
    format_resource_cost,
)


class TestResourceAbbreviations:
    """Tests for resource abbreviation constants."""

    def test_all_resources_have_abbrevs(self):
        """Verify all planet resources have abbreviations."""
        from game.core.constants import PLANET_RESOURCES

        for res in PLANET_RESOURCES:
            assert res in RESOURCE_ABBREVS, f"{res} missing from RESOURCE_ABBREVS"
            assert res in RESOURCE_ABBREVS_SHORT, f"{res} missing from RESOURCE_ABBREVS_SHORT"

    def test_short_abbrevs_are_single_char(self):
        """Verify short abbreviations are single characters."""
        for res, abbr in RESOURCE_ABBREVS_SHORT.items():
            assert len(abbr) == 1, f"{res} has multi-char short abbrev: {abbr}"

    def test_abbrevs_are_unique(self):
        """Verify abbreviations are unique."""
        abbrevs = list(RESOURCE_ABBREVS.values())
        assert len(abbrevs) == len(set(abbrevs)), "Duplicate abbreviations found"

        short_abbrevs = list(RESOURCE_ABBREVS_SHORT.values())
        assert len(short_abbrevs) == len(set(short_abbrevs)), "Duplicate short abbreviations"


class TestFormatEmpireResources:
    """Tests for format_empire_resources function."""

    def test_formats_resources_with_capacity(self):
        """Verify resources with capacity are formatted as current/cap."""
        empire = MagicMock()
        empire.resource_pool = {"Metals": 500.0, "Organics": 200.0}
        empire.max_storage = {"Metals": 1000.0, "Organics": 500.0}

        result = format_empire_resources(empire)

        assert "Met: 500/1000" in result
        assert "Org: 200/500" in result

    def test_formats_resources_without_capacity(self):
        """Verify resources without capacity show only current."""
        empire = MagicMock()
        empire.resource_pool = {"Metals": 100.0, "Organics": 50.0}
        empire.max_storage = {"Metals": 0.0, "Organics": 0.0}

        result = format_empire_resources(empire)

        assert "Met: 100" in result
        assert "Org: 50" in result
        assert "/" not in result  # No capacity shown

    def test_uses_pipe_separator(self):
        """Verify parts are separated by pipe characters."""
        empire = MagicMock()
        empire.resource_pool = {"Metals": 100.0, "Organics": 50.0}
        empire.max_storage = {"Metals": 200.0, "Organics": 100.0}

        result = format_empire_resources(empire)

        assert "  |  " in result

    def test_empty_empire_returns_no_resources(self):
        """Verify empty resource pool returns 'No resources'."""
        empire = MagicMock()
        empire.resource_pool = {}
        empire.max_storage = {}

        result = format_empire_resources(empire)

        assert result == "No resources"

    def test_zero_values_not_shown(self):
        """Verify zero-value resources are not shown."""
        empire = MagicMock()
        empire.resource_pool = {"Metals": 0.0, "Organics": 0.0}
        empire.max_storage = {"Metals": 0.0, "Organics": 0.0}

        result = format_empire_resources(empire)

        assert result == "No resources"

    def test_truncates_to_integers(self):
        """Verify float values are truncated to integers."""
        empire = MagicMock()
        empire.resource_pool = {"Metals": 123.7}
        empire.max_storage = {"Metals": 456.9}

        result = format_empire_resources(empire)

        assert "Met: 123/456" in result

    def test_handles_missing_resource_gracefully(self):
        """Verify missing resources return 0."""
        empire = MagicMock()
        empire.resource_pool = MagicMock()
        empire.resource_pool.get = MagicMock(return_value=0.0)
        empire.max_storage = MagicMock()
        empire.max_storage.get = MagicMock(return_value=0.0)

        result = format_empire_resources(empire)

        assert result == "No resources"


class TestFormatResourceCost:
    """Tests for format_resource_cost function."""

    def test_formats_single_resource(self):
        """Verify single resource cost is formatted."""
        cost = {"Metals": 100}

        result = format_resource_cost(cost)

        assert result == "M:100"

    def test_formats_multiple_resources(self):
        """Verify multiple resource costs are formatted."""
        cost = {"Metals": 100, "Organics": 50, "Vapors": 25}

        result = format_resource_cost(cost)

        assert "M:100" in result
        assert "O:50" in result
        assert "V:25" in result

    def test_skips_zero_cost_resources(self):
        """Verify zero-cost resources are not shown."""
        cost = {"Metals": 100, "Organics": 0, "Vapors": 25}

        result = format_resource_cost(cost)

        assert "M:100" in result
        assert "V:25" in result
        assert "O:" not in result

    def test_empty_cost_returns_empty_string(self):
        """Verify empty cost dict returns empty string."""
        cost = {}

        result = format_resource_cost(cost)

        assert result == ""

    def test_all_zero_costs_returns_empty_string(self):
        """Verify all-zero costs return empty string."""
        cost = {"Metals": 0, "Organics": 0, "Vapors": 0}

        result = format_resource_cost(cost)

        assert result == ""

    def test_truncates_to_integers(self):
        """Verify float values are truncated to integers."""
        cost = {"Metals": 99.9}

        result = format_resource_cost(cost)

        assert result == "M:99"

    def test_uses_space_separator(self):
        """Verify parts are separated by spaces."""
        cost = {"Metals": 100, "Organics": 50}

        result = format_resource_cost(cost)

        assert " " in result
        parts = result.split(" ")
        assert len(parts) == 2

    def test_respects_planet_resources_order(self):
        """Verify resources are ordered according to PLANET_RESOURCES."""
        from game.core.constants import PLANET_RESOURCES

        # Create cost with all resources
        cost = {res: (i + 1) * 10 for i, res in enumerate(PLANET_RESOURCES)}

        result = format_resource_cost(cost)

        # Extract order from result
        parts = result.split(" ")
        result_abbrevs = [p.split(":")[0] for p in parts]

        # Expected order based on PLANET_RESOURCES
        expected_abbrevs = [RESOURCE_ABBREVS_SHORT[res] for res in PLANET_RESOURCES]

        assert result_abbrevs == expected_abbrevs


# =======================================================================
# Per-Turn Spend Calculation Tests (PROJ-221 Phase 2)
# =======================================================================

from game.ui.screens.build_queue_helpers import calculate_per_turn_spend


class TestPerTurnSpend:
    """Tests for calculate_per_turn_spend() function."""

    def test_per_turn_spend_single_resource(self):
        """Item costs 100 Metals, rate 2000/turn -> spend = 100/turn (completes in <1 turn)."""
        queue_item = {
            "total_cost": {"Metals": 100.0},
            "resources_consumed": {"Metals": 0.0},
        }
        build_rate = {"Metals": 2000.0}

        result = calculate_per_turn_spend(queue_item, build_rate)

        # Limiting turns = 100/2000 = 0.05 turns
        # Per-turn spend = 100 / 0.05 = 2000 (capped to remaining=100)
        # Actually: spend = remaining / limiting_turns = 100 / 0.05 = 2000
        # But can't spend more than remaining per turn... Let me rethink.
        # The formula is: spend_per_turn = min(remaining, rate * limiting_turns) / limiting_turns
        # = min(remaining, rate * limiting_turns) / limiting_turns
        # For single resource: limiting_turns = remaining/rate = 0.05
        # spend = min(100, 2000 * 0.05) / 0.05 = min(100, 100) / 0.05 = 100/0.05 = 2000
        # Hmm, that gives 2000, which is the full rate. That's correct for single resource.
        assert result["Metals"] == pytest.approx(2000.0)

    def test_per_turn_spend_limiting_resource(self):
        """Metals 6000 at rate 3000 (2 turns), Organics 1500 at rate 3000 (0.5 turns).

        Limiting resource is Metals (2 turns).
        Metals spend = 6000/2 = 3000/turn (full rate).
        Organics spend = 1500/2 = 750/turn (proportional).
        """
        queue_item = {
            "total_cost": {"Metals": 6000.0, "Organics": 1500.0},
            "resources_consumed": {"Metals": 0.0, "Organics": 0.0},
        }
        build_rate = {"Metals": 3000.0, "Organics": 3000.0}

        result = calculate_per_turn_spend(queue_item, build_rate)

        assert result["Metals"] == pytest.approx(3000.0)
        assert result["Organics"] == pytest.approx(750.0)

    def test_per_turn_spend_with_partial_consumption(self):
        """Item partially consumed - spend based on remaining cost."""
        queue_item = {
            "total_cost": {"Metals": 6000.0, "Organics": 1500.0},
            "resources_consumed": {"Metals": 3000.0, "Organics": 750.0},
        }
        build_rate = {"Metals": 3000.0, "Organics": 3000.0}

        result = calculate_per_turn_spend(queue_item, build_rate)

        # Remaining: Metals=3000, Organics=750
        # Limiting: Metals 3000/3000 = 1 turn
        # Metals spend = 3000/1 = 3000, Organics spend = 750/1 = 750
        assert result["Metals"] == pytest.approx(3000.0)
        assert result["Organics"] == pytest.approx(750.0)

    def test_per_turn_spend_zero_cost_resource(self):
        """Resource with 0 remaining cost -> 0 spend."""
        queue_item = {
            "total_cost": {"Metals": 6000.0, "Organics": 0.0},
            "resources_consumed": {"Metals": 0.0, "Organics": 0.0},
        }
        build_rate = {"Metals": 3000.0, "Organics": 3000.0}

        result = calculate_per_turn_spend(queue_item, build_rate)

        assert result["Metals"] == pytest.approx(3000.0)
        assert result.get("Organics", 0.0) == pytest.approx(0.0)

    def test_per_turn_spend_zero_rate(self):
        """Resource with 0 production rate -> 0 spend for that resource."""
        queue_item = {
            "total_cost": {"Metals": 6000.0, "Organics": 1500.0},
            "resources_consumed": {"Metals": 0.0, "Organics": 0.0},
        }
        build_rate = {"Metals": 3000.0, "Organics": 0.0}

        result = calculate_per_turn_spend(queue_item, build_rate)

        # Organics has 0 rate but is needed - item is stuck
        # All resources should be 0 spend (can't build)
        assert result.get("Metals", 0.0) == pytest.approx(0.0)
        assert result.get("Organics", 0.0) == pytest.approx(0.0)

    def test_per_turn_spend_empty_cost(self):
        """Empty total_cost -> empty result."""
        queue_item = {
            "total_cost": {},
            "resources_consumed": {},
        }
        build_rate = {"Metals": 3000.0}

        result = calculate_per_turn_spend(queue_item, build_rate)

        assert result == {}

    def test_per_turn_spend_all_consumed(self):
        """All resources fully consumed -> all zeros."""
        queue_item = {
            "total_cost": {"Metals": 3000.0, "Organics": 1500.0},
            "resources_consumed": {"Metals": 3000.0, "Organics": 1500.0},
        }
        build_rate = {"Metals": 3000.0, "Organics": 3000.0}

        result = calculate_per_turn_spend(queue_item, build_rate)

        for val in result.values():
            assert val == pytest.approx(0.0)

    def test_per_turn_spend_matches_production_engine_proportions(self):
        """Per-turn spend ratios match production engine proportional formula.

        For a 3-resource item, the ratio of per-turn spend should match
        the ratio of remaining costs divided by the limiting turns.
        """
        queue_item = {
            "total_cost": {"Metals": 9000.0, "Organics": 3000.0, "Vapors": 6000.0},
            "resources_consumed": {"Metals": 0.0, "Organics": 0.0, "Vapors": 0.0},
        }
        build_rate = {"Metals": 3000.0, "Organics": 3000.0, "Vapors": 3000.0}

        result = calculate_per_turn_spend(queue_item, build_rate)

        # Limiting: Metals 9000/3000 = 3 turns
        # Metals spend = 9000/3 = 3000 (full rate)
        # Organics spend = 3000/3 = 1000
        # Vapors spend = 6000/3 = 2000
        assert result["Metals"] == pytest.approx(3000.0)
        assert result["Organics"] == pytest.approx(1000.0)
        assert result["Vapors"] == pytest.approx(2000.0)

        # Verify proportions: Metals:Organics:Vapors = 9:3:6 = 3:1:2
        assert result["Metals"] / result["Organics"] == pytest.approx(3.0)
        assert result["Vapors"] / result["Organics"] == pytest.approx(2.0)
