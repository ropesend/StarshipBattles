"""PROJ-477 Phase 5 Task 5.1 — StrategyWorldAccess live-traversal seam.

The scene-owned ``StrategyWorldAccess`` is the SINGLE raw-domain seam for the
render-hot stack and the raw-window handoffs. It hands back LIVE collections /
O(1) map lookups — NO per-frame DTO allocation. POST-FLESH B1: the identity
invariant is per-ELEMENT (same live ``StarSystem`` objects), not container
identity (``galaxy.systems.values()`` returns a fresh view per call).
"""
from __future__ import annotations

from types import SimpleNamespace

from game.core.hex_math import HexCoord
from game.ui.screens.strategy_world_access import StrategyWorldAccess


def _make_galaxy(systems_by_hex=None, *, state=None, **methods):
    galaxy = SimpleNamespace(
        systems=systems_by_hex or {},
        state=state or SimpleNamespace(
            global_hex_planets={},
            global_hex_zones={},
            global_hex_warp_points={},
        ),
    )
    for name, fn in methods.items():
        setattr(galaxy, name, fn)
    return galaxy


def _world(galaxy, empires=None):
    session = SimpleNamespace(galaxy=galaxy, empires=empires or [])
    return StrategyWorldAccess(lambda: session)


def test_iter_systems_yields_same_live_objects() -> None:
    """Element identity: the systems yielded ARE the live StarSystem objects in
    ``galaxy.systems.values()`` — no DTO projection (POST-FLESH B1)."""
    sys_a = SimpleNamespace(name="A")
    sys_b = SimpleNamespace(name="B")
    galaxy = _make_galaxy({HexCoord(0, 0): sys_a, HexCoord(1, 1): sys_b})
    world = _world(galaxy)

    yielded = list(world.iter_systems())
    assert sys_a in yielded and sys_b in yielded
    # Element identity (not container identity).
    assert all(any(y is s for s in (sys_a, sys_b)) for y in yielded)


def test_iter_empires_yields_live_empires() -> None:
    e1 = SimpleNamespace(id=1)
    e2 = SimpleNamespace(id=2)
    world = _world(_make_galaxy(), empires=[e1, e2])
    assert list(world.iter_empires()) == [e1, e2]


def test_system_by_name_returns_live_system() -> None:
    sol = SimpleNamespace(name="Sol")
    galaxy = _make_galaxy(get_system_by_name=lambda n: sol if n == "Sol" else None)
    world = _world(galaxy)
    assert world.system_by_name("Sol") is sol
    assert world.system_by_name("X") is None


def test_system_for_object_returns_live_system() -> None:
    planet = object()
    home = SimpleNamespace(name="Home")
    galaxy = _make_galaxy(
        get_system_of_object=lambda o: home if o is planet else None
    )
    world = _world(galaxy)
    assert world.system_for_object(planet) is home
    assert world.system_for_object(object()) is None


def test_system_at_map_hex_uses_pathfinder_radius_50() -> None:
    near = SimpleNamespace(name="Near", global_location=HexCoord(12, 0))
    captured = {}

    def at_hex(hex_c, radius):
        captured["radius"] = radius
        return near

    galaxy = _make_galaxy()
    galaxy._pathfinder = SimpleNamespace(get_system_at_hex=at_hex)
    world = _world(galaxy)

    assert world.system_at_map_hex(HexCoord(0, 0)) is near
    assert captured["radius"] == 50
    world.system_at_map_hex(HexCoord(0, 0), radius=7)
    assert captured["radius"] == 7


def test_planets_at_exact_hex_returns_live_planets() -> None:
    target = HexCoord(3, 3)
    planet = SimpleNamespace(name="Terra")
    galaxy = _make_galaxy(
        get_planets_at_global_hex=lambda h: [planet] if h == target else []
    )
    world = _world(galaxy)
    assert world.planets_at_exact_hex(target) == [planet]
    assert world.planets_at_exact_hex(HexCoord(9, 9)) == []


def test_zones_at_hex_returns_live_zones() -> None:
    target = HexCoord(4, 4)
    zone = SimpleNamespace(name="Dyson")
    galaxy = _make_galaxy(
        get_zones_at_global_hex=lambda h: [zone] if h == target else []
    )
    world = _world(galaxy)
    assert world.zones_at_hex(target) == [zone]


def test_warp_points_at_hex_returns_owner_system() -> None:
    target = HexCoord(6, 6)
    owner = SimpleNamespace(name="Owner")
    state = SimpleNamespace(
        global_hex_planets={},
        global_hex_zones={},
        global_hex_warp_points={target: owner},
    )
    galaxy = _make_galaxy(state=state)
    world = _world(galaxy)
    assert world.warp_points_at_hex(target) is owner
    assert world.warp_points_at_hex(HexCoord(0, 0)) is None


def test_planet_by_id_routes_to_galaxy() -> None:
    planet = SimpleNamespace(id=42)
    galaxy = _make_galaxy(
        get_planet_by_id=lambda pid: planet if pid == 42 else None
    )
    world = _world(galaxy)
    assert world.planet_by_id(42) is planet
    assert world.planet_by_id(1) is None


def test_global_hex_map_accessors_return_live_maps() -> None:
    state = SimpleNamespace(
        global_hex_planets={HexCoord(0, 0): ["p"]},
        global_hex_zones={HexCoord(1, 1): ["z"]},
        global_hex_warp_points={HexCoord(2, 2): "s"},
    )
    galaxy = _make_galaxy(state=state)
    world = _world(galaxy)
    assert world.global_hex_planets is state.global_hex_planets
    assert world.global_hex_zones is state.global_hex_zones
    assert world.global_hex_warp_points is state.global_hex_warp_points


def test_world_resolves_session_lazily() -> None:
    """The world reads the CURRENT session via the provider (honours swaps)."""
    g1 = _make_galaxy({HexCoord(0, 0): SimpleNamespace(name="One")})
    g2 = _make_galaxy({HexCoord(1, 1): SimpleNamespace(name="Two")})
    box = {"s": SimpleNamespace(galaxy=g1, empires=[])}
    world = StrategyWorldAccess(lambda: box["s"])

    assert [s.name for s in world.iter_systems()] == ["One"]
    box["s"] = SimpleNamespace(galaxy=g2, empires=[])
    assert [s.name for s in world.iter_systems()] == ["Two"]
