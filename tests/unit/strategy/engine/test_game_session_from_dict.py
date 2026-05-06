"""Focused GameSession.from_dict edge tests."""

import pytest

from game.core.exceptions import PersistenceException
from game.core.hex_math import HexCoord
from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import Order, OrderType
from game.strategy.engine.game_config import GameConfig, PlayerConfig
from game.strategy.engine.game_session import GameSession


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
