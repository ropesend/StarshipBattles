"""Tests for ``Galaxy.add_warp_point`` (issue #31).

Canonical seam for "add a warp point at runtime" — appends to
``system.warp_points`` AND updates the ``global_hex_warp_points`` index
in one call. Mirrors the ``remove_warp_link`` pattern.
"""
from __future__ import annotations

from game.core.hex_math import HexCoord
from game.strategy.data.galaxy import Galaxy, StarSystem, WarpPoint


class TestGalaxyAddWarpPoint:
    def _make_galaxy_with_two_systems(self):
        galaxy = Galaxy(radius=1000)
        system_a = StarSystem(name="Alpha", global_location=HexCoord(0, 0))
        system_b = StarSystem(name="Beta", global_location=HexCoord(100, 0))
        galaxy.add_system(system_a)
        galaxy.add_system(system_b)
        return galaxy, system_a, system_b

    def test_add_warp_point_appends_to_system_warp_points(self):
        galaxy, system_a, system_b = self._make_galaxy_with_two_systems()
        wp = WarpPoint(system_b.name, HexCoord(3, 4))

        galaxy.add_warp_point(system_a, wp)

        assert wp in system_a.warp_points

    def test_add_warp_point_updates_global_hex_index(self):
        galaxy, system_a, system_b = self._make_galaxy_with_two_systems()
        wp = WarpPoint(system_b.name, HexCoord(3, 4))
        wp_global_hex = system_a.global_location + wp.location

        galaxy.add_warp_point(system_a, wp)

        # The new warp point's global hex resolves to ``system_a`` via the
        # index — same contract as ``create_vars_link``.
        assert galaxy.state.global_hex_warp_points.get(wp_global_hex) is system_a

    def test_add_warp_point_supports_consecutive_additions(self):
        """Calling twice for two new endpoints leaves both indexed."""
        galaxy, system_a, system_b = self._make_galaxy_with_two_systems()
        wp_a = WarpPoint(system_b.name, HexCoord(3, 4))
        wp_b = WarpPoint(system_a.name, HexCoord(-3, -4))

        galaxy.add_warp_point(system_a, wp_a)
        galaxy.add_warp_point(system_b, wp_b)

        a_global = system_a.global_location + wp_a.location
        b_global = system_b.global_location + wp_b.location
        assert galaxy.state.global_hex_warp_points.get(a_global) is system_a
        assert galaxy.state.global_hex_warp_points.get(b_global) is system_b
        assert wp_a in system_a.warp_points
        assert wp_b in system_b.warp_points
