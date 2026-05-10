"""PROJ-372 Phase 4: GalaxyPathfindingService acceptance tests.

Closes goal G5: pathfinding callable on a 3-system stub graph (no
``Galaxy()`` construction, no naming-registry disk load).
"""
from __future__ import annotations

from typing import Dict
from unittest.mock import MagicMock

from game.core.hex_math import HexCoord
from game.strategy.data.galaxy_protocols import IGalaxySystemGraph
from game.strategy.services.galaxy_pathfinding_service import (
    GalaxyPathfindingService,
)


def _system(name: str, loc: HexCoord, warp_destinations=None):
    """Tiny duck-typed StarSystem stub."""
    sys = MagicMock()
    sys.name = name
    sys.global_location = loc
    sys.warp_points = []
    if warp_destinations:
        for dest_name in warp_destinations:
            wp = MagicMock()
            wp.destination_id = dest_name
            wp.location = HexCoord(0, 0)
            sys.warp_points.append(wp)
    sys.__eq__ = lambda self, other: getattr(other, "name", None) == self.name
    sys.__hash__ = lambda self: hash(self.name)
    return sys


class _StubGalaxyGraph:
    """Minimal IGalaxySystemGraph implementation."""

    def __init__(self, systems_dict: Dict[HexCoord, object]):
        self._systems = systems_dict

    @property
    def systems(self):
        return self._systems

    def get_system_by_name(self, name: str):
        for s in self._systems.values():
            if s.name == name:
                return s
        return None


def _build_three_system_chain():
    """Build A <-> B <-> C linear chain. Returns (graph, A, B, C)."""
    a = _system("A", HexCoord(0, 0), warp_destinations=["B"])
    b = _system("B", HexCoord(5, 0), warp_destinations=["A", "C"])
    c = _system("C", HexCoord(10, 0), warp_destinations=["B"])
    graph = _StubGalaxyGraph({
        HexCoord(0, 0): a,
        HexCoord(5, 0): b,
        HexCoord(10, 0): c,
    })
    return graph, a, b, c


def test_stub_graph_satisfies_protocol() -> None:
    graph, _, _, _ = _build_three_system_chain()
    assert isinstance(graph, IGalaxySystemGraph)


def test_find_path_interstellar_returns_three_system_path() -> None:
    graph, a, b, c = _build_three_system_chain()
    svc = GalaxyPathfindingService(graph)
    path = svc.find_path_interstellar(a, c)
    assert path is not None
    assert [s.name for s in path] == ["A", "B", "C"]


def test_find_path_interstellar_same_system_returns_singleton() -> None:
    graph, a, _, _ = _build_three_system_chain()
    svc = GalaxyPathfindingService(graph)
    path = svc.find_path_interstellar(a, a)
    assert path == [a]


def test_find_path_interstellar_disconnected_returns_none() -> None:
    a = _system("A", HexCoord(0, 0), warp_destinations=[])
    b = _system("B", HexCoord(50, 0), warp_destinations=[])
    graph = _StubGalaxyGraph({HexCoord(0, 0): a, HexCoord(50, 0): b})
    svc = GalaxyPathfindingService(graph)
    assert svc.find_path_interstellar(a, b) is None


def test_get_system_at_hex_exact_match() -> None:
    graph, a, b, _ = _build_three_system_chain()
    svc = GalaxyPathfindingService(graph)
    assert svc.get_system_at_hex(HexCoord(0, 0)) is a
    assert svc.get_system_at_hex(HexCoord(5, 0)) is b


def test_get_system_at_hex_radius_search() -> None:
    graph, a, _, _ = _build_three_system_chain()
    svc = GalaxyPathfindingService(graph)
    assert svc.get_system_at_hex(HexCoord(1, 0), radius=10) is a


def test_find_nearest_system() -> None:
    graph, _, _, c = _build_three_system_chain()
    svc = GalaxyPathfindingService(graph)
    assert svc.find_nearest_system(HexCoord(11, 0)) is c


def test_find_path_deep_space_via_hex_linedraw() -> None:
    """Deep-space pathfinding now uses ``hex_linedraw`` directly (PROJ-392)."""
    from game.core.hex_math import hex_linedraw

    path = hex_linedraw(HexCoord(0, 0), HexCoord(3, 0))
    assert path[0] == HexCoord(0, 0)
    assert path[-1] == HexCoord(3, 0)


def test_strip_start_hex_static() -> None:
    """strip_start_hex is a static helper (no graph needed)."""
    path = [HexCoord(0, 0), HexCoord(1, 0), HexCoord(2, 0)]
    stripped = GalaxyPathfindingService.strip_start_hex(HexCoord(0, 0), path)
    assert stripped == [HexCoord(1, 0), HexCoord(2, 0)]


def test_pathfinding_shim_forwards_to_hex_linedraw() -> None:
    """Phase 4 shim must produce identical results to direct ``hex_linedraw`` (PROJ-392)."""
    from game.core.hex_math import hex_linedraw
    from game.strategy.data.pathfinding import find_path_deep_space

    shim_path = find_path_deep_space(HexCoord(0, 0), HexCoord(2, 0))
    direct_path = hex_linedraw(HexCoord(0, 0), HexCoord(2, 0))
    assert shim_path == direct_path
