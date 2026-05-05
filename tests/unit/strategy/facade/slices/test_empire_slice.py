from types import SimpleNamespace
from unittest.mock import Mock

from game.core.hex_math import HexCoord
from game.strategy.data import build_queue_source
from game.strategy.facade.dto import BuildQueueSourceDTO
from game.strategy.facade.slices.empire_slice import EmpireSlice


def _source(owner: object) -> SimpleNamespace:
    return SimpleNamespace(
        queue_id="queue-1",
        display_name="Alpha Yard",
        owner_entity=owner,
        construction_queue=[{"design_id": "scout", "total_cost": {"metals": 5}}],
        can_build_ships=True,
        can_build_complexes=False,
        context_type="planet",
        build_rate={"metals": 100.0},
        planet_id=17,
    )


def test_get_empire_build_queues_threads_registries_and_returns_dtos(
    monkeypatch,
) -> None:
    empire = SimpleNamespace(id=3)
    registries = object()
    source = _source(SimpleNamespace(id=17, owner_id=3))
    collector = Mock(return_value=[source])
    monkeypatch.setattr(
        build_queue_source,
        "collect_all_build_queues_for_empire",
        collector,
    )
    state = SimpleNamespace(
        get_empire_by_id=Mock(return_value=empire),
        session=SimpleNamespace(registries=registries),
    )

    result = EmpireSlice(state).get_empire_build_queues(3)

    assert result == [BuildQueueSourceDTO.from_domain(source)]
    collector.assert_called_once_with(empire, registries=registries)


def test_get_empire_build_queues_returns_empty_for_unknown_empire(
    monkeypatch,
) -> None:
    collector = Mock()
    monkeypatch.setattr(
        build_queue_source,
        "collect_all_build_queues_for_empire",
        collector,
    )
    state = SimpleNamespace(
        get_empire_by_id=Mock(return_value=None),
        session=SimpleNamespace(registries=object()),
    )

    assert EmpireSlice(state).get_empire_build_queues(999) == []
    collector.assert_not_called()


def test_get_hex_build_queues_threads_hex_galaxy_empire_and_registries(
    monkeypatch,
) -> None:
    empire = SimpleNamespace(id=4)
    galaxy = object()
    registries = object()
    hex_coord = HexCoord(2, 3)
    source = _source(SimpleNamespace(id=21, owner_id=4))
    collector = Mock(return_value=[source])
    monkeypatch.setattr(
        build_queue_source,
        "collect_build_queues_at_hex",
        collector,
    )
    state = SimpleNamespace(
        get_empire_by_id=Mock(return_value=empire),
        session=SimpleNamespace(galaxy=galaxy, registries=registries),
    )

    result = EmpireSlice(state).get_hex_build_queues(4, hex_coord)

    assert result == [BuildQueueSourceDTO.from_domain(source)]
    collector.assert_called_once_with(
        hex_coord,
        galaxy,
        empire,
        registries=registries,
    )


def test_get_hex_build_queues_returns_empty_for_unknown_empire(
    monkeypatch,
) -> None:
    collector = Mock()
    monkeypatch.setattr(
        build_queue_source,
        "collect_build_queues_at_hex",
        collector,
    )
    state = SimpleNamespace(
        get_empire_by_id=Mock(return_value=None),
        session=SimpleNamespace(galaxy=object(), registries=object()),
    )

    assert EmpireSlice(state).get_hex_build_queues(404, HexCoord(0, 0)) == []
    collector.assert_not_called()
