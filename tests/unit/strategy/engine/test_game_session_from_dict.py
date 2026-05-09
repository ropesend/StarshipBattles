"""Focused GameSession.from_dict edge tests."""

import pytest

from game.core.exceptions import PersistenceException
from game.core.hex_math import HexCoord
from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import Order, OrderType
from game.strategy.engine.game_config import GameConfig, PlayerConfig
from game.strategy.engine.game_session import GameSession
from game.strategy.services.empire_write_service import EmpireWriteService
from game.strategy.services.fleet_write_service import FleetWriteService
from game.strategy.services.planet_write_service import PlanetWriteService
from game.strategy.services.ship_instance_write_service import (
    ShipInstanceWriteService,
)


def _small_config() -> GameConfig:
    return GameConfig(
        players=[
            PlayerConfig(
                name="Player A",
                theme="Federation",
                color=(255, 0, 0),
            ),
            PlayerConfig(
                name="Player B",
                theme="Atlantians",
                color=(0, 255, 0),
            ),
        ],
        system_count=2,
    )


def test_from_dict_missing_config_raises_persistence_exception() -> None:
    with pytest.raises(PersistenceException) as exc_info:
        GameSession.from_dict({"galaxy": {}, "empires": []})

    assert "Missing required config field" in str(exc_info.value)
    assert exc_info.value.context["section"] == "config"
    assert exc_info.value.context["missing_field"] == "'config'"


def test_from_dict_missing_galaxy_raises_persistence_exception() -> None:
    data = {
        "config": _small_config().to_dict(),
        "empires": [],
    }

    with pytest.raises(PersistenceException) as exc_info:
        GameSession.from_dict(data)

    assert "Missing required galaxy field" in str(exc_info.value)
    assert exc_info.value.context["section"] == "galaxy"
    assert exc_info.value.context["missing_field"] == "'galaxy'"


@pytest.mark.parametrize(
    "order_type",
    [OrderType.MOVE_TO_FLEET, OrderType.JOIN_FLEET],
)
def test_from_dict_rebuilds_pursuer_tracker_for_fleet_orders(order_type) -> None:
    session = GameSession(config=_small_config())
    empire = session.empires[0]
    source = Fleet(
        fleet_id=9101,
        owner_id=empire.id,
        location=HexCoord(1, 1),
        speed=5.0,
    )
    target = Fleet(
        fleet_id=9102,
        owner_id=empire.id,
        location=HexCoord(2, 2),
        speed=5.0,
    )
    source.add_order(Order(order_type, target))
    empire.add_fleet(target)
    empire.add_fleet(source)

    data = session.to_dict()

    restored = GameSession.from_dict(data)
    restored_source = restored.galaxy.get_fleet_by_id(source.id)
    restored_target = restored.galaxy.get_fleet_by_id(target.id)

    assert restored_source is not None
    assert restored_target is not None
    assert restored_source.orders[0].target is restored_target
    assert restored_source in restored_target.pursuer_tracker.pursuers


# ----------------------------------------------------------------------
# PROJ-396 CRIT-002: GameSession.from_dict() must restore mutator services.
# ----------------------------------------------------------------------


def test_from_dict_restores_all_mutator_services() -> None:
    """Deserialized session exposes all four mutator services.

    Pattern #2 invariant: a session must function identically whether
    constructed via ``__init__`` or ``from_dict``. Before PROJ-396, the
    private mutator fields were never assigned in ``from_dict``, so any
    command handler call (e.g. ``add_move_order_if_needed``) raised
    ``AttributeError`` against ``session.fleet_mutator``.
    """
    session = GameSession(config=_small_config())
    restored = GameSession.from_dict(session.to_dict())

    # Property accessors must not raise AttributeError.
    assert isinstance(restored.fleet_mutator, FleetWriteService)
    assert isinstance(restored.planet_mutator, PlanetWriteService)
    assert isinstance(restored.empire_mutator, EmpireWriteService)
    assert isinstance(restored.ship_mutator, ShipInstanceWriteService)


def test_from_dict_fleet_mutator_set_path_does_not_raise() -> None:
    """Regression: command-handler-equivalent ``set_path`` call works after load.

    PROJ-396 CRIT-002: ``add_move_order_if_needed`` calls
    ``session.fleet_mutator.set_path(...)``. Before the fix, this raised
    ``AttributeError`` because ``from_dict`` never constructed the mutator.
    """
    session = GameSession(config=_small_config())
    empire = session.empires[0]
    fleet = Fleet(
        fleet_id=9201,
        owner_id=empire.id,
        location=HexCoord(0, 0),
        speed=5.0,
    )
    empire.add_fleet(fleet)

    restored = GameSession.from_dict(session.to_dict())
    restored_fleet = restored.galaxy.get_fleet_by_id(fleet.id)
    assert restored_fleet is not None

    # Exercises the navigation slice — the FleetWriteService delegates
    # to its internal FleetNavigationService, which from_dict must also
    # have constructed.
    new_path = [HexCoord(1, 0), HexCoord(2, 0)]
    restored.fleet_mutator.set_path(restored_fleet, new_path)
    assert restored_fleet.path == new_path
