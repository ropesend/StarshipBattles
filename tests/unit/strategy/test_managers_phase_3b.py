"""PROJ-436 Phase 3b: manager setter API tests.

Phase 3b adds explicit `set_level(...)` to ``ShipConsumableManager`` and
`set_cargo(...)` to ``ShipCargoManager`` so external callers
(``ShipInstanceWriteService``, ``ShipInstanceFactory``,
``ShipInstanceBridge``) can write through a stable API instead of
poking ``ship.consumable_levels[...]`` /
``ship.cargo_contents[...]`` directly.

Phase 3f flips the durable substrate to ``Container``; routing every
write through the manager methods now means that cutover does not need
to touch any external caller — only the two manager bodies.
"""
from __future__ import annotations

from unittest.mock import Mock


class TestShipConsumableManagerSetLevel:
    """``ShipConsumableManager.set_level`` writes the per-resource level."""

    def _make_ship(self) -> Mock:
        ship = Mock()
        ship.consumable_levels = {}
        ship.get_calculated_stats = Mock(return_value={
            'resource_storage': {'fuel': 1000.0, 'energy': 500.0},
        })
        return ship

    def test_set_level_writes_through_to_consumable_levels(self) -> None:
        from game.strategy.data.ship_consumable_manager import (
            ShipConsumableManager,
        )
        ship = self._make_ship()
        manager = ShipConsumableManager(ship)
        manager.set_level('fuel', 750.0)
        assert ship.consumable_levels['fuel'] == 750.0

    def test_set_level_overwrites_existing(self) -> None:
        from game.strategy.data.ship_consumable_manager import (
            ShipConsumableManager,
        )
        ship = self._make_ship()
        ship.consumable_levels = {'fuel': 100.0}
        manager = ShipConsumableManager(ship)
        manager.set_level('fuel', 500.0)
        assert ship.consumable_levels['fuel'] == 500.0

    def test_set_level_supports_new_resource_id(self) -> None:
        from game.strategy.data.ship_consumable_manager import (
            ShipConsumableManager,
        )
        ship = self._make_ship()
        manager = ShipConsumableManager(ship)
        manager.set_level('ammo', 50.0)
        assert ship.consumable_levels['ammo'] == 50.0

    def test_replace_levels_replaces_full_dict(self) -> None:
        from game.strategy.data.ship_consumable_manager import (
            ShipConsumableManager,
        )
        ship = self._make_ship()
        ship.consumable_levels = {'fuel': 100.0, 'energy': 200.0}
        manager = ShipConsumableManager(ship)
        manager.replace_levels({'fuel': 500.0, 'ammo': 25.0})
        assert ship.consumable_levels == {'fuel': 500.0, 'ammo': 25.0}

    def test_get_all_levels_returns_copy(self) -> None:
        from game.strategy.data.ship_consumable_manager import (
            ShipConsumableManager,
        )
        ship = self._make_ship()
        ship.consumable_levels = {'fuel': 100.0}
        manager = ShipConsumableManager(ship)
        snap = manager.get_all_levels()
        snap['fuel'] = 999.0
        # original untouched
        assert ship.consumable_levels['fuel'] == 100.0


class TestShipCargoManagerSetCargo:
    """``ShipCargoManager.set_cargo`` writes the per-type cargo amount."""

    def _make_ship(self) -> Mock:
        ship = Mock()
        ship.cargo_contents = {}
        ship.get_calculated_stats = Mock(return_value={
            'cargo_storage': {'passengers': 100, 'generic': 500},
        })
        return ship

    def test_set_cargo_writes_through_to_cargo_contents(self) -> None:
        from game.strategy.data.ship_cargo_manager import ShipCargoManager
        ship = self._make_ship()
        manager = ShipCargoManager(ship)
        manager.set_cargo('passengers', 25)
        assert ship.cargo_contents['passengers'] == 25

    def test_set_cargo_overwrites_existing(self) -> None:
        from game.strategy.data.ship_cargo_manager import ShipCargoManager
        ship = self._make_ship()
        ship.cargo_contents = {'passengers': 10}
        manager = ShipCargoManager(ship)
        manager.set_cargo('passengers', 50)
        assert ship.cargo_contents['passengers'] == 50

    def test_set_cargo_zero_removes_key(self) -> None:
        from game.strategy.data.ship_cargo_manager import ShipCargoManager
        ship = self._make_ship()
        ship.cargo_contents = {'passengers': 10}
        manager = ShipCargoManager(ship)
        manager.set_cargo('passengers', 0)
        assert 'passengers' not in ship.cargo_contents

    def test_set_cargo_supports_new_type(self) -> None:
        from game.strategy.data.ship_cargo_manager import ShipCargoManager
        ship = self._make_ship()
        manager = ShipCargoManager(ship)
        manager.set_cargo('generic', 120)
        assert ship.cargo_contents['generic'] == 120

    def test_has_cargo_returns_false_when_empty(self) -> None:
        from game.strategy.data.ship_cargo_manager import ShipCargoManager
        ship = self._make_ship()
        manager = ShipCargoManager(ship)
        assert manager.has_cargo() is False

    def test_has_cargo_returns_true_when_any_positive(self) -> None:
        from game.strategy.data.ship_cargo_manager import ShipCargoManager
        ship = self._make_ship()
        ship.cargo_contents = {'passengers': 10}
        manager = ShipCargoManager(ship)
        assert manager.has_cargo() is True

    def test_total_cargo_units_sums_all_types(self) -> None:
        from game.strategy.data.ship_cargo_manager import ShipCargoManager
        ship = self._make_ship()
        ship.cargo_contents = {'passengers': 10, 'generic': 25}
        manager = ShipCargoManager(ship)
        assert manager.total_cargo_units() == 35

    def test_get_all_cargo_returns_copy(self) -> None:
        from game.strategy.data.ship_cargo_manager import ShipCargoManager
        ship = self._make_ship()
        ship.cargo_contents = {'passengers': 10}
        manager = ShipCargoManager(ship)
        snap = manager.get_all_cargo()
        snap['passengers'] = 999
        assert ship.cargo_contents['passengers'] == 10
