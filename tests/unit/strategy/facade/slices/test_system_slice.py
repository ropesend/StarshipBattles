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
        _session=session,
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


def test_get_all_systems_returns_dtos_for_each_system(monkeypatch) -> None:
    alpha = SimpleNamespace(name="Alpha")
    beta = SimpleNamespace(name="Beta")
    galaxy = SimpleNamespace(systems={"alpha": alpha, "beta": beta})
    state = SimpleNamespace(_session=SimpleNamespace(galaxy=galaxy))
    monkeypatch.setattr(
        SystemInfo,
        "from_star_system",
        staticmethod(lambda system: system.name),
    )

    assert SystemSlice(state).get_all_systems() == ["Alpha", "Beta"]


def test_get_system_at_hex_converts_found_system_and_returns_none(monkeypatch) -> None:
    system = SimpleNamespace(name="Alpha")
    galaxy = SimpleNamespace(
        get_system_at_location=lambda hex_coord: (
            system if hex_coord == HexCoord(2, 3) else None
        ),
    )
    state = SimpleNamespace(_session=SimpleNamespace(galaxy=galaxy))
    monkeypatch.setattr(
        SystemInfo,
        "from_star_system",
        staticmethod(lambda system: system.name),
    )
    system_slice = SystemSlice(state)

    assert system_slice.get_system_at_hex(HexCoord(2, 3)) == "Alpha"
    assert system_slice.get_system_at_hex(HexCoord(9, 9)) is None


def test_get_system_containing_fleet_resolves_from_fleet_location(
    monkeypatch,
) -> None:
    fleet = SimpleNamespace(location=HexCoord(4, 5))
    system = SimpleNamespace(name="Fleet System", global_location=fleet.location)
    galaxy = SimpleNamespace(
        systems={"fleet-system": system},
        get_system_at_location=lambda hex_coord: (
            system if hex_coord == fleet.location else None
        ),
    )
    state = SimpleNamespace(
        _session=SimpleNamespace(galaxy=galaxy),
        get_fleet_by_id=lambda fleet_id: fleet,
    )
    monkeypatch.setattr(
        SystemInfo,
        "from_star_system",
        staticmethod(lambda system: system.name),
    )

    assert SystemSlice(state).get_system_containing_fleet(7) == "Fleet System"


def test_get_system_containing_fleet_returns_none_for_unknown_fleet() -> None:
    state = SimpleNamespace(get_fleet_by_id=lambda fleet_id: None)

    assert SystemSlice(state).get_system_containing_fleet(404) is None


def test_get_system_near_hex_returns_closest_system_within_distance(
    monkeypatch,
) -> None:
    near = SimpleNamespace(name="Near", global_location=HexCoord(3, 0))
    far = SimpleNamespace(name="Far", global_location=HexCoord(20, 0))
    galaxy = SimpleNamespace(
        systems={"near": near, "far": far},
        get_system_at_location=lambda hex_coord: None,
    )
    state = SimpleNamespace(_session=SimpleNamespace(galaxy=galaxy))
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
    state = SimpleNamespace(_session=SimpleNamespace(galaxy=galaxy))

    assert SystemSlice(state).get_system_near_hex(HexCoord(0, 0), max_dist=8) is None


def test_get_system_by_name_resolves_and_returns_none(monkeypatch) -> None:
    """PROJ-477 Phase 2: ``get_system_by_name`` delegates to the galaxy's O(1)
    name map and projects to ``SystemInfo``; ``None`` for an unknown name."""
    sol = SimpleNamespace(name="Sol")
    galaxy = SimpleNamespace(
        get_system_by_name=lambda name: (sol if name == "Sol" else None),
    )
    state = SimpleNamespace(_session=SimpleNamespace(galaxy=galaxy))
    monkeypatch.setattr(
        SystemInfo, "from_star_system", staticmethod(lambda system: system.name)
    )
    system_slice = SystemSlice(state)

    assert system_slice.get_system_by_name("Sol") == "Sol"
    assert system_slice.get_system_by_name("Nowhere") is None


def test_get_system_of_object_resolves_and_returns_none(monkeypatch) -> None:
    """PROJ-477 Phase 2: ``get_system_of_object`` delegates to
    ``galaxy.get_system_of_object`` and projects to ``SystemInfo``."""
    planet = object()
    home = SimpleNamespace(name="Home")
    galaxy = SimpleNamespace(
        get_system_of_object=lambda obj: (home if obj is planet else None),
    )
    state = SimpleNamespace(_session=SimpleNamespace(galaxy=galaxy))
    monkeypatch.setattr(
        SystemInfo, "from_star_system", staticmethod(lambda system: system.name)
    )
    system_slice = SystemSlice(state)

    assert system_slice.get_system_of_object(planet) == "Home"
    assert system_slice.get_system_of_object(object()) is None


def test_get_system_at_map_hex_uses_pathfinder_radius_50(monkeypatch) -> None:
    """PROJ-477 Phase 2: ``get_system_at_map_hex`` uses the pathfinder's
    system-radius (default 50) ownership semantics — distinct from
    ``near_hex(max_dist=8)``.

    A system 12 hexes away is OWNED at radius=50 (``at_map_hex`` resolves it)
    but is NOT within ``near_hex``'s default max_dist=8 — proving the two
    queries have different semantics and ``at_map_hex`` is not a ``near_hex``
    alias (design.md risk 2 / decisions.md).
    """
    near = SimpleNamespace(name="Near", global_location=HexCoord(12, 0))
    captured: dict = {}

    def fake_get_system_at_hex(hex_c, radius):
        captured["hex"] = hex_c
        captured["radius"] = radius
        from game.core.hex_math import hex_distance
        return near if hex_distance(hex_c, near.global_location) < radius else None

    pathfinder = SimpleNamespace(get_system_at_hex=fake_get_system_at_hex)
    galaxy = SimpleNamespace(
        _pathfinder=pathfinder,
        systems={"near": near},
        get_system_at_location=lambda h: None,
    )
    state = SimpleNamespace(_session=SimpleNamespace(galaxy=galaxy))
    monkeypatch.setattr(
        SystemInfo, "from_star_system", staticmethod(lambda system: system.name)
    )
    system_slice = SystemSlice(state)

    # Default radius 50: the 12-hex-away system IS owned.
    assert system_slice.get_system_at_map_hex(HexCoord(0, 0)) == "Near"
    assert captured["radius"] == 50

    # near_hex(max_dist=8) does NOT resolve the same system → different semantics.
    assert system_slice.get_system_near_hex(HexCoord(0, 0), max_dist=8) is None

    # Explicit radius is honoured; a too-small radius yields None.
    assert system_slice.get_system_at_map_hex(HexCoord(0, 0), radius=5) is None
    assert captured["radius"] == 5


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
    state = SimpleNamespace(_session=SimpleNamespace(galaxy=galaxy))

    assert SystemSlice(state).get_storm_names_at_hex(HexCoord(4, 4)) == ["Ion Front"]


def test_get_storm_names_at_hex_handles_galaxy_without_zone_index() -> None:
    state = SimpleNamespace(_session=SimpleNamespace(galaxy=SimpleNamespace()))

    assert SystemSlice(state).get_storm_names_at_hex(HexCoord(4, 4)) == []


def test_get_storm_names_at_hex_excludes_abilities_carrying_non_storm() -> None:
    """TG-003 characterization (PROJ-470): the zone spatial index registers
    stars and planets alongside storms (galaxy_entity_registry.py:50,52,83).
    A star-like zone carries an ``abilities`` attribute but NOT ``storm_type``.

    The ``is_storm`` TypeGuard requires BOTH ``storm_type`` and ``abilities``,
    so it must exclude such a zone — exactly as ``isinstance(zone, Storm)``
    did. This pins that the duck-typed guard did not widen the filter to
    include ability-carrying stars/planets.
    """
    storm = Storm(
        name="Ion Front",
        storm_type="ion",
        location=HexCoord(0, 0),
        hex_offsets=frozenset({HexCoord(0, 0)}),
        abilities={},
    )
    # Star-like zone: has `abilities` and a `name`, but no `storm_type`.
    star_like_zone = SimpleNamespace(name="Sol", abilities={"radiation": {}})
    galaxy = SimpleNamespace(
        get_zones_at_global_hex=lambda hex_coord: [star_like_zone, storm]
    )
    state = SimpleNamespace(_session=SimpleNamespace(galaxy=galaxy))

    assert SystemSlice(state).get_storm_names_at_hex(HexCoord(4, 4)) == ["Ion Front"]
