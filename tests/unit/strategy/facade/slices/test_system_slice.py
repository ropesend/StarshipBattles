from types import SimpleNamespace

from game.core.hex_math import HexCoord
from game.strategy.data.storm import Storm
from game.strategy.facade.dto import StarInfo, SystemInfo
from game.strategy.facade.slices.system_slice import SystemSlice


def test_get_all_stars_uses_cache_until_turn_changes(monkeypatch) -> None:
    star = SimpleNamespace(name="Sol")
    system = SimpleNamespace(
        name="Solar",
        global_location=HexCoord(1, 1),
        stars=[star],
        planets=[object()],
    )
    session = SimpleNamespace(
        turn_number=1,
        galaxy=SimpleNamespace(systems={"solar": system}),
    )
    state = SimpleNamespace(
        session=session,
        all_stars_cache=None,
        all_stars_cache_turn=-1,
    )
    calls = []
    monkeypatch.setattr(
        StarInfo,
        "from_star",
        staticmethod(lambda star, **kwargs: calls.append(kwargs) or object()),
    )
    system_slice = SystemSlice(state)

    first = system_slice.get_all_stars()
    second = system_slice.get_all_stars()
    session.turn_number = 2
    third = system_slice.get_all_stars()

    assert first is second
    assert third is not first
    assert len(calls) == 2
    assert calls[0]["system_name"] == "Solar"
    assert calls[0]["planet_count"] == 1


def test_get_system_near_hex_returns_closest_system_within_distance(
    monkeypatch,
) -> None:
    near = SimpleNamespace(name="Near", global_location=HexCoord(3, 0))
    far = SimpleNamespace(name="Far", global_location=HexCoord(20, 0))
    galaxy = SimpleNamespace(
        systems={"near": near, "far": far},
        get_system_at_location=lambda hex_coord: None,
    )
    state = SimpleNamespace(session=SimpleNamespace(galaxy=galaxy))
    monkeypatch.setattr(
        SystemInfo,
        "from_star_system",
        staticmethod(lambda system: system.name),
    )

    assert SystemSlice(state).get_system_near_hex(HexCoord(0, 0), max_dist=8) == "Near"


def test_get_system_near_hex_returns_none_when_no_system_is_close() -> None:
    galaxy = SimpleNamespace(
        systems={"far": SimpleNamespace(global_location=HexCoord(20, 0))},
        get_system_at_location=lambda hex_coord: None,
    )
    state = SimpleNamespace(session=SimpleNamespace(galaxy=galaxy))

    assert SystemSlice(state).get_system_near_hex(HexCoord(0, 0), max_dist=8) is None


def test_get_storm_names_at_hex_filters_non_storm_zones() -> None:
    storm = Storm(
        name="Ion Front",
        storm_type="ion",
        location=HexCoord(0, 0),
        hex_offsets=frozenset({HexCoord(0, 0)}),
        abilities={},
    )
    galaxy = SimpleNamespace(
        get_zones_at_global_hex=lambda hex_coord: [object(), storm]
    )
    state = SimpleNamespace(session=SimpleNamespace(galaxy=galaxy))

    assert SystemSlice(state).get_storm_names_at_hex(HexCoord(4, 4)) == ["Ion Front"]


def test_get_storm_names_at_hex_handles_galaxy_without_zone_index() -> None:
    state = SimpleNamespace(session=SimpleNamespace(galaxy=SimpleNamespace()))

    assert SystemSlice(state).get_storm_names_at_hex(HexCoord(4, 4)) == []
