"""Tests for construction_forecast.forecast_queue_turn_spend()."""

import pytest

from game.strategy.engine.construction_forecast import forecast_queue_turn_spend


def _make_item(total_cost, resources_consumed=None):
    """Helper to create a queue item dict."""
    return {
        "design_id": "test",
        "type": "ship",
        "total_cost": total_cost,
        "resources_consumed": resources_consumed or {},
    }


class TestForecastQueueTurnSpend:
    """Tests for queue-level per-turn spend distribution."""

    def test_empty_queue(self):
        result = forecast_queue_turn_spend([], {"Metals": 3000})
        assert result == []

    def test_empty_build_rate(self):
        item = _make_item({"Metals": 100})
        result = forecast_queue_turn_spend([item], {})
        assert result[0]["Metals"] == 0.0

    def test_single_item_completes_within_turn(self):
        """Item costs 500 metals, rate is 3000/turn — spends only 500."""
        item = _make_item({"Metals": 500.0})
        result = forecast_queue_turn_spend([item], {"Metals": 3000.0})
        assert len(result) == 1
        assert result[0]["Metals"] == pytest.approx(500.0)

    def test_single_item_takes_multiple_turns(self):
        """Item costs 6000 metals, rate is 3000/turn — spends 3000."""
        item = _make_item({"Metals": 6000.0})
        result = forecast_queue_turn_spend([item], {"Metals": 3000.0})
        assert len(result) == 1
        assert result[0]["Metals"] == pytest.approx(3000.0)

    def test_single_item_partially_consumed(self):
        """Item costs 1000, 300 consumed, rate 3000 — spends remaining 700."""
        item = _make_item({"Metals": 1000.0}, {"Metals": 300.0})
        result = forecast_queue_turn_spend([item], {"Metals": 3000.0})
        assert result[0]["Metals"] == pytest.approx(700.0)

    def test_carry_over_to_second_item(self):
        """First item costs 749, second also 749, rate 3000.
        Item 1 takes 749/3000 = 0.2497 turns, item 2 gets remaining."""
        items = [
            _make_item({"Metals": 749.0}),
            _make_item({"Metals": 749.0}),
        ]
        result = forecast_queue_turn_spend(items, {"Metals": 3000.0})
        assert result[0]["Metals"] == pytest.approx(749.0)
        assert result[1]["Metals"] == pytest.approx(749.0)

    def test_five_items_partial_last(self):
        """5 items at 749 each, rate 3000. Items 1-3 fit fully (2247),
        item 4 fits fully (2996), item 5 gets remaining capacity (4 metals)."""
        items = [_make_item({"Metals": 749.0}) for _ in range(5)]
        result = forecast_queue_turn_spend(items, {"Metals": 3000.0})
        # Items 1-4 fit (4 * 749 = 2996)
        for i in range(4):
            assert result[i]["Metals"] == pytest.approx(749.0), f"Item {i}"
        # Item 5: remaining capacity = 1.0 - 4*(749/3000) = 0.001333...
        # Spend = 3000 * 0.001333... = 4.0
        assert result[4]["Metals"] == pytest.approx(4.0, abs=0.1)

    def test_sixth_item_gets_zero(self):
        """6 items at 749 each, rate 3000. Item 6 should get ~0."""
        items = [_make_item({"Metals": 749.0}) for _ in range(6)]
        result = forecast_queue_turn_spend(items, {"Metals": 3000.0})
        assert result[5]["Metals"] == pytest.approx(0.0, abs=0.5)

    def test_multi_resource_limiting(self):
        """Item costs 100 metals and 300 organics, rate 3000 each.
        Limiting resource is organics (300/3000 = 0.1 turns).
        Both resources should be fully spent since item completes."""
        item = _make_item({"Metals": 100.0, "Organics": 300.0})
        result = forecast_queue_turn_spend(
            [item], {"Metals": 3000.0, "Organics": 3000.0}
        )
        assert result[0]["Metals"] == pytest.approx(100.0)
        assert result[0]["Organics"] == pytest.approx(300.0)

    def test_zero_rate_resource_gives_zero(self):
        """If a required resource has zero rate, item gets zero spend."""
        item = _make_item({"Metals": 100.0, "Organics": 50.0})
        result = forecast_queue_turn_spend(
            [item], {"Metals": 3000.0, "Organics": 0.0}
        )
        assert result[0]["Metals"] == 0.0
        assert result[0]["Organics"] == 0.0

    def test_already_complete_item_skipped(self):
        """Item fully consumed — no spend, no capacity consumed."""
        items = [
            _make_item({"Metals": 100.0}, {"Metals": 100.0}),  # Complete
            _make_item({"Metals": 500.0}),  # Should get full spend
        ]
        result = forecast_queue_turn_spend(items, {"Metals": 3000.0})
        assert result[0]["Metals"] == 0.0
        assert result[1]["Metals"] == pytest.approx(500.0)

    def test_result_includes_all_planet_resources(self):
        """Result dicts should include all PLANET_RESOURCES, even if zero."""
        from game.core.constants import PLANET_RESOURCES
        item = _make_item({"Metals": 100.0})
        result = forecast_queue_turn_spend([item], {"Metals": 3000.0})
        for res in PLANET_RESOURCES:
            assert res in result[0]

    def test_item_without_total_cost_gets_zero(self):
        """Malformed item without total_cost gets zero spend."""
        item = {"design_id": "bad", "type": "ship"}
        result = forecast_queue_turn_spend([item], {"Metals": 3000.0})
        assert result[0]["Metals"] == 0.0
