"""Tests for ShipStatsCache helper (PROJ-425 Phase 1).

The stats-calculation + cache-invalidation logic is moving out of
``ShipInstance`` into ``ship_stats_cache.py``. ``_cached_stats`` storage
stays on the entity for this phase per TD-06 Weak-LLM Guardrail #2.
"""

from unittest.mock import Mock, patch

import pytest

from game.core.registry import GameRegistries
from game.strategy.data.ship_instance import ShipInstance
from game.strategy.data.ship_stats_cache import ShipStatsCache


@pytest.fixture
def mock_registries():
    registries = Mock(spec=GameRegistries)
    registries.components = {}
    registries.modifiers = {}
    registries.vehicle_classes = {}
    registries.resources = {}
    return registries


@pytest.fixture
def basic_design_data():
    return {
        'name': 'TestShip',
        'ship_class': 'Frigate',
        'layers': {},
    }


def _make_ship(design_data, registries):
    ship = ShipInstance(
        instance_id='test-1',
        design_id='TestDesign',
        name='Test Ship',
        owner_id=0,
        design_data=design_data,
    )
    ship._registries = registries
    return ship


class TestShipStatsCacheCalculate:
    """The helper performs the calculation and writes ``_cached_stats``."""

    def test_calculate_calls_calculate_design_stats_with_registries(
        self, mock_registries, basic_design_data,
    ):
        ship = _make_ship(basic_design_data, mock_registries)
        with patch(
            'game.simulation.entities.ship_design_stats.calculate_design_stats'
        ) as mock_calc:
            mock_calc.return_value = {'max_hp': 250}

            stats = ShipStatsCache.calculate(ship)

            mock_calc.assert_called_once()
            args = mock_calc.call_args[0]
            assert args[0] is ship.design_data
            assert args[1] is mock_registries
            kwargs = mock_calc.call_args[1]
            assert kwargs.get('components') is ship.components
            assert kwargs.get('component_toggles') is ship.component_toggles
            assert stats == {'max_hp': 250}

    def test_calculate_raises_when_registries_none(self, basic_design_data):
        ship = _make_ship(basic_design_data, registries=None)
        with pytest.raises(ValueError, match='ShipInstance requires registries'):
            ShipStatsCache.calculate(ship)


class TestShipStatsCacheGetOrCompute:
    """``get_or_compute`` honours cache hit / miss / force_refresh."""

    def test_cache_hit_returns_cached_without_recompute(
        self, mock_registries, basic_design_data,
    ):
        ship = _make_ship(basic_design_data, mock_registries)
        ship._cached_stats = {'max_hp': 999}

        with patch(
            'game.simulation.entities.ship_design_stats.calculate_design_stats'
        ) as mock_calc:
            stats = ShipStatsCache.get_or_compute(ship)

            mock_calc.assert_not_called()
            assert stats == {'max_hp': 999}

    def test_cache_miss_populates_and_returns(
        self, mock_registries, basic_design_data,
    ):
        ship = _make_ship(basic_design_data, mock_registries)
        assert ship._cached_stats is None
        with patch(
            'game.simulation.entities.ship_design_stats.calculate_design_stats'
        ) as mock_calc:
            mock_calc.return_value = {'max_hp': 100}

            stats = ShipStatsCache.get_or_compute(ship)

            mock_calc.assert_called_once()
            assert stats == {'max_hp': 100}
            assert ship._cached_stats == {'max_hp': 100}

    def test_force_refresh_bypasses_cache(
        self, mock_registries, basic_design_data,
    ):
        ship = _make_ship(basic_design_data, mock_registries)
        ship._cached_stats = {'max_hp': 1}
        with patch(
            'game.simulation.entities.ship_design_stats.calculate_design_stats'
        ) as mock_calc:
            mock_calc.return_value = {'max_hp': 2}

            stats = ShipStatsCache.get_or_compute(ship, force_refresh=True)

            mock_calc.assert_called_once()
            assert stats == {'max_hp': 2}
            assert ship._cached_stats == {'max_hp': 2}


class TestShipStatsCacheInvalidate:
    """``invalidate`` clears ``_cached_stats`` on the entity."""

    def test_invalidate_resets_cache_to_none(
        self, mock_registries, basic_design_data,
    ):
        ship = _make_ship(basic_design_data, mock_registries)
        ship._cached_stats = {'max_hp': 42}

        ShipStatsCache.invalidate(ship)

        assert ship._cached_stats is None
