"""Tests for ShipInstanceFactory (PROJ-425 Phase 3).

The factory body of ``ShipInstance.create(...)`` and the helper
``_build_full_hp_components_from_design`` move into
``game/strategy/services/ship_instance_factory.py``.

``ShipInstance.create(...)`` remains as a thin shim that delegates to
the factory. Caller migration is *not* a Phase 3 goal — the shim stays
as long as grep finds callers.
"""
from unittest.mock import Mock, patch

import pytest

from game.core.registry import GameRegistries
from game.strategy.data.ship_instance import ShipInstance
from game.strategy.services.ship_instance_factory import (
    ShipInstanceFactory,
    build_full_hp_components_from_design,
)


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


class TestShipInstanceFactoryCreate:
    def test_create_returns_ship_instance(self, mock_registries, basic_design_data):
        with patch(
            'game.simulation.entities.ship_design_stats.calculate_design_stats'
        ) as mock_calc:
            mock_calc.return_value = {'resource_storage': {}}

            ship = ShipInstanceFactory.create(
                design_data=basic_design_data,
                owner_id=7,
                registries=mock_registries,
            )

        assert isinstance(ship, ShipInstance)
        assert ship.owner_id == 7
        assert ship.design_id == 'TestShip'
        assert ship.name == 'TestShip'
        assert ship._registries is mock_registries
        # New instance gets a UUID
        assert ship.instance_id
        # Serial defaults to None when empire absent
        assert ship.serial is None

    def test_create_uses_explicit_name_and_design_id(
        self, mock_registries, basic_design_data,
    ):
        with patch(
            'game.simulation.entities.ship_design_stats.calculate_design_stats'
        ) as mock_calc:
            mock_calc.return_value = {'resource_storage': {}}

            ship = ShipInstanceFactory.create(
                design_data=basic_design_data,
                owner_id=0,
                name='Hero',
                design_id='hero_design',
                registries=mock_registries,
            )

        assert ship.name == 'Hero'
        assert ship.design_id == 'hero_design'

    def test_create_initializes_consumables_from_storage(
        self, mock_registries, basic_design_data,
    ):
        with patch(
            'game.simulation.entities.ship_design_stats.calculate_design_stats'
        ) as mock_calc:
            mock_calc.return_value = {'resource_storage': {'fuel': 1000, 'energy': 500}}

            ship = ShipInstanceFactory.create(
                design_data=basic_design_data,
                owner_id=0,
                registries=mock_registries,
            )

        assert ship.consumable_levels == {'fuel': 1000.0, 'energy': 500.0}

    def test_create_mirrors_design_role(self, mock_registries):
        design = {
            'name': 'TestShip',
            'layers': {},
            'design_role': 'fleet_escort',
        }
        with patch(
            'game.simulation.entities.ship_design_stats.calculate_design_stats'
        ) as mock_calc:
            mock_calc.return_value = {'resource_storage': {}}

            ship = ShipInstanceFactory.create(
                design_data=design,
                owner_id=0,
                registries=mock_registries,
            )

        assert ship.design_role == 'fleet_escort'

    def test_create_uses_empire_serial(self, mock_registries, basic_design_data):
        empire = Mock()
        empire.get_next_serial.return_value = 42

        with patch(
            'game.simulation.entities.ship_design_stats.calculate_design_stats'
        ) as mock_calc:
            mock_calc.return_value = {'resource_storage': {}}

            ship = ShipInstanceFactory.create(
                design_data=basic_design_data,
                owner_id=0,
                empire=empire,
                registries=mock_registries,
            )

        empire.get_next_serial.assert_called_once_with('TestShip')
        assert ship.serial == 42


class TestBuildFullHpComponentsFromDesign:
    def test_returns_empty_when_registries_none(self, basic_design_data):
        result = build_full_hp_components_from_design(basic_design_data, None)
        assert result == {}


class TestShipInstanceCreateShim:
    """``ShipInstance.create`` remains as a thin shim — same observable behavior."""

    def test_shim_delegates_to_factory(self, mock_registries, basic_design_data):
        with patch(
            'game.simulation.entities.ship_design_stats.calculate_design_stats'
        ) as mock_calc:
            mock_calc.return_value = {'resource_storage': {'fuel': 100}}

            ship = ShipInstance.create(
                design_data=basic_design_data,
                owner_id=3,
                registries=mock_registries,
            )

        assert isinstance(ship, ShipInstance)
        assert ship.owner_id == 3
        assert ship._registries is mock_registries
        assert ship.consumable_levels == {'fuel': 100.0}
