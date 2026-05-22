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
        _session=SimpleNamespace(registries=registries),
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
        _session=SimpleNamespace(registries=object()),
    )

    assert EmpireSlice(state).get_empire_build_queues(999) == []
    collector.assert_not_called()


def test_get_hex_build_queues_threads_hex_galaxy_empire_and_registries(
    monkeypatch,
) -> None:
    empire = SimpleNamespace(id=4)
    # PROJ-472 1B: the slice now resolves owner scalars against the galaxy,
    # so the stub galaxy must answer the planet system lookup.
    planet = SimpleNamespace(id=21, owner_id=4, location=HexCoord(1, 1))
    system = SimpleNamespace(name="Vega", global_location=HexCoord(10, 0))
    galaxy = SimpleNamespace(get_system_of_planet=Mock(return_value=system))
    registries = object()
    hex_coord = HexCoord(2, 3)
    source = _source(planet)
    collector = Mock(return_value=[source])
    monkeypatch.setattr(
        build_queue_source,
        "collect_build_queues_at_hex",
        collector,
    )
    state = SimpleNamespace(
        get_empire_by_id=Mock(return_value=empire),
        _session=SimpleNamespace(galaxy=galaxy, registries=registries),
    )

    result = EmpireSlice(state).get_hex_build_queues(4, hex_coord)

    assert result == [
        BuildQueueSourceDTO.from_domain(
            source,
            owner_global_hex=HexCoord(10, 0) + HexCoord(1, 1),
            owner_system_name="Vega",
        )
    ]
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
        _session=SimpleNamespace(galaxy=object(), registries=object()),
    )

    assert EmpireSlice(state).get_hex_build_queues(404, HexCoord(0, 0)) == []
    collector.assert_not_called()


def test_get_hex_build_queues_resolves_fleet_owner_scalars(monkeypatch) -> None:
    """PROJ-472 1B: fleet sources project location + system-at-hex name."""
    empire = SimpleNamespace(id=4)
    fleet = SimpleNamespace(id=88, owner_id=4, location=HexCoord(7, 2))
    system = SimpleNamespace(name="Orion")
    galaxy = SimpleNamespace(
        get_system_at_location=Mock(return_value=system),
    )
    fleet_source = SimpleNamespace(
        queue_id="fleet_88_yard_1",
        display_name="Strike Group",
        owner_entity=fleet,
        construction_queue=[],
        can_build_ships=True,
        can_build_complexes=True,
        context_type="fleet",
        build_rate={"metals": 50.0},
        planet_id=None,
        is_paused=True,
    )
    monkeypatch.setattr(
        build_queue_source,
        "collect_build_queues_at_hex",
        Mock(return_value=[fleet_source]),
    )
    state = SimpleNamespace(
        get_empire_by_id=Mock(return_value=empire),
        _session=SimpleNamespace(galaxy=galaxy, registries=object()),
    )

    [dto] = EmpireSlice(state).get_hex_build_queues(4, HexCoord(7, 2))

    assert dto.owner_global_hex == HexCoord(7, 2)
    assert dto.owner_system_name == "Orion"
    assert dto.is_paused is True
    galaxy.get_system_at_location.assert_called_once_with(HexCoord(7, 2))
