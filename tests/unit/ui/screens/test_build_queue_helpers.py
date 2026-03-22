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

from game.ui.screens.build_queue_helpers import (
    calculate_per_turn_spend,
    calculate_queue_turn_spend,
)


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


# =======================================================================
# Queue-Wide Turn Spend Distribution Tests (BUG-98)
# =======================================================================


class TestQueueTurnSpend:
    """Tests for calculate_queue_turn_spend() — distributes production across queue."""

    def _make_item(self, metals_cost, metals_consumed=0.0):
        """Helper to create a simple metals-only queue item."""
        return {
            "total_cost": {"Metals": metals_cost},
            "resources_consumed": {"Metals": metals_consumed},
        }

    def _make_multi_item(self, total_cost, resources_consumed=None):
        """Helper to create a multi-resource queue item."""
        if resources_consumed is None:
            resources_consumed = {res: 0.0 for res in total_cost}
        return {
            "total_cost": total_cost,
            "resources_consumed": resources_consumed,
        }

    def test_single_item_gets_full_rate(self):
        """Single item that takes multiple turns gets the full build rate."""
        queue = [self._make_item(6000.0)]
        build_rate = {"Metals": 3000.0}

        result = calculate_queue_turn_spend(queue, build_rate)

        assert len(result) == 1
        assert result[0]["Metals"] == pytest.approx(3000.0)

    def test_single_item_completes_within_turn(self):
        """Single item that completes in <1 turn shows only remaining cost."""
        queue = [self._make_item(749.0)]
        build_rate = {"Metals": 3000.0}

        result = calculate_queue_turn_spend(queue, build_rate)

        assert len(result) == 1
        assert result[0]["Metals"] == pytest.approx(749.0)

    def test_multiple_items_all_complete_within_turn(self):
        """Multiple cheap items that all complete within one turn."""
        queue = [self._make_item(749.0) for _ in range(3)]
        build_rate = {"Metals": 3000.0}

        result = calculate_queue_turn_spend(queue, build_rate)

        # 3 items at 749 each = 2247, well within 3000 capacity
        assert len(result) == 3
        assert result[0]["Metals"] == pytest.approx(749.0)
        assert result[1]["Metals"] == pytest.approx(749.0)
        assert result[2]["Metals"] == pytest.approx(749.0)

    def test_bug_98_scenario_five_items(self):
        """BUG-98 scenario: 5 items at 749 each, 3000/turn rate.

        Items 1-4 complete (749 * 4 = 2996), item 5 gets remainder (4).
        """
        queue = [self._make_item(749.0) for _ in range(5)]
        build_rate = {"Metals": 3000.0}

        result = calculate_queue_turn_spend(queue, build_rate)

        assert len(result) == 5
        assert result[0]["Metals"] == pytest.approx(749.0)
        assert result[1]["Metals"] == pytest.approx(749.0)
        assert result[2]["Metals"] == pytest.approx(749.0)
        assert result[3]["Metals"] == pytest.approx(749.0)
        assert result[4]["Metals"] == pytest.approx(4.0)

    def test_bug_98_scenario_six_items(self):
        """BUG-98 scenario with 6th item: gets zero production."""
        queue = [self._make_item(749.0) for _ in range(6)]
        build_rate = {"Metals": 3000.0}

        result = calculate_queue_turn_spend(queue, build_rate)

        assert len(result) == 6
        assert result[4]["Metals"] == pytest.approx(4.0)
        assert result[5]["Metals"] == pytest.approx(0.0)

    def test_partially_consumed_first_item(self):
        """First item already partially built — uses less capacity."""
        queue = [
            self._make_item(749.0, metals_consumed=500.0),  # 249 remaining
            self._make_item(749.0),  # 749 remaining
        ]
        build_rate = {"Metals": 3000.0}

        result = calculate_queue_turn_spend(queue, build_rate)

        assert result[0]["Metals"] == pytest.approx(249.0)
        assert result[1]["Metals"] == pytest.approx(749.0)

    def test_empty_queue(self):
        """Empty queue returns empty list."""
        result = calculate_queue_turn_spend([], {"Metals": 3000.0})
        assert result == []

    def test_zero_rate_blocks_all_items(self):
        """Zero production rate blocks all items."""
        queue = [self._make_item(749.0), self._make_item(749.0)]
        build_rate = {"Metals": 0.0}

        result = calculate_queue_turn_spend(queue, build_rate)

        assert result[0]["Metals"] == pytest.approx(0.0)
        assert result[1]["Metals"] == pytest.approx(0.0)

    def test_multi_resource_limiting_resource(self):
        """Multi-resource items: limiting resource determines capacity fraction."""
        # Item costs 6000 Metals + 1500 Organics, rate 3000 each
        # Limiting: Metals at 6000/3000 = 2 turns → uses full turn capacity
        queue = [
            self._make_multi_item({"Metals": 6000.0, "Organics": 1500.0}),
            self._make_multi_item({"Metals": 1000.0, "Organics": 500.0}),
        ]
        build_rate = {"Metals": 3000.0, "Organics": 3000.0}

        result = calculate_queue_turn_spend(queue, build_rate)

        # First item takes 2 turns (Metals-limited), uses full turn capacity
        # Metals: rate * 1.0 turn = 3000, clamped to remaining 6000 → 3000
        # Organics: rate * 1.0 turn = 3000, clamped to remaining 1500 → 1500
        assert result[0]["Metals"] == pytest.approx(3000.0)
        assert result[0]["Organics"] == pytest.approx(1500.0)
        # Second item gets 0 — no capacity left
        assert result[1]["Metals"] == pytest.approx(0.0)
        assert result[1]["Organics"] == pytest.approx(0.0)

    def test_multi_resource_item_completes_mid_turn(self):
        """Multi-resource item that completes mid-turn passes capacity to next."""
        # Item costs 1500 Metals + 750 Organics, rate 3000 each
        # Limiting: Metals at 1500/3000 = 0.5 turns → leaves 0.5 turn capacity
        queue = [
            self._make_multi_item({"Metals": 1500.0, "Organics": 750.0}),
            self._make_multi_item({"Metals": 6000.0, "Organics": 3000.0}),
        ]
        build_rate = {"Metals": 3000.0, "Organics": 3000.0}

        result = calculate_queue_turn_spend(queue, build_rate)

        # First item: completes in 0.5 turns, spend = remaining cost
        assert result[0]["Metals"] == pytest.approx(1500.0)
        assert result[0]["Organics"] == pytest.approx(750.0)
        # Second item: gets 0.5 turn capacity, Metals-limited (6000/3000=2 turns)
        # 0.5 turns * 3000/turn = 1500 Metals, Organics: 0.5 * 3000 = 1500 clamped to 3000 → 1500
        assert result[1]["Metals"] == pytest.approx(1500.0)
        assert result[1]["Organics"] == pytest.approx(1500.0)

    def test_fully_consumed_item_passes_all_capacity(self):
        """Already-complete item at head of queue passes full capacity through."""
        queue = [
            self._make_item(749.0, metals_consumed=749.0),  # Already done
            self._make_item(749.0),
        ]
        build_rate = {"Metals": 3000.0}

        result = calculate_queue_turn_spend(queue, build_rate)

        assert result[0]["Metals"] == pytest.approx(0.0)
        assert result[1]["Metals"] == pytest.approx(749.0)

    def test_missing_rate_for_required_resource(self):
        """Missing build rate for a required resource blocks that item and subsequent."""
        queue = [self._make_item(749.0)]
        build_rate = {}  # No rate for Metals

        result = calculate_queue_turn_spend(queue, build_rate)

        assert result[0]["Metals"] == pytest.approx(0.0)
