"""
Tests for find_hybrid_path can_warp parameter.

PROJ-239 Task 3.2: CQ-004 - find_hybrid_path should accept can_warp directly
so callers don't need to construct fake fleet objects.
"""
from unittest.mock import MagicMock


class TestFindHybridPathCanWarp:
    """Test that find_hybrid_path accepts can_warp parameter."""

    def test_accepts_can_warp_parameter(self):
        """find_hybrid_path accepts a can_warp keyword argument."""
        from game.strategy.data.pathfinding import find_hybrid_path
        import inspect
        sig = inspect.signature(find_hybrid_path)
        assert 'can_warp' in sig.parameters, (
            "find_hybrid_path should accept a 'can_warp' parameter"
        )

    def test_can_warp_overrides_fleet_check(self):
        """When can_warp is provided, fleet.capabilities is not accessed."""
        from game.strategy.data.pathfinding import find_hybrid_path
        from game.core.hex_math import HexCoord

        galaxy = MagicMock()
        galaxy.systems = {}

        start = HexCoord(0, 0)
        end = HexCoord(1, 0)

        # fleet with capabilities that should NOT be called when can_warp is explicit
        fleet = MagicMock()

        try:
            find_hybrid_path(galaxy, start, end, fleet=fleet, can_warp=True)
        except Exception:
            pass  # We don't care about the result, just that capabilities wasn't called

        fleet.capabilities.can_use_warp.assert_not_called()


class TestFleetNavigationNoMockHack:
    """Verify FleetNavigationService.compute_path doesn't use MockCapabilities."""

    def test_no_mock_capabilities_class_in_compute_path(self):
        """compute_path should not define an inline MockCapabilities class."""
        import inspect
        from game.strategy.services.fleet_navigation_service import FleetNavigationService
        source = inspect.getsource(FleetNavigationService.compute_path)
        assert 'MockCapabilities' not in source, (
            "compute_path should not contain a MockCapabilities hack"
        )
