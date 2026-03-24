"""Integration tests for fleet join order redirect and pursuer tracking (PROJ-222).

Tests end-to-end flows: multi-hop chains, concurrent merges, destruction
cancel, order lifecycle, and validation.
"""

from game.core.hex_math import HexCoord
from game.strategy.data.fleet import Fleet
from game.strategy.data.empire import Empire
from game.strategy.data.order_types import FleetOrder, OrderType


def make_empire_with_fleets(*fleet_ids, empire_id=0):
    """Create an empire with the given fleet IDs, all at different locations."""
    empire = Empire(empire_id, f"Empire {empire_id}", (255, 0, 0))
    fleets = {}
    for i, fid in enumerate(fleet_ids):
        fleet = Fleet(fid, empire_id, HexCoord(i * 10, 0))
        empire.add_fleet(fleet)
        fleets[fid] = fleet
    return empire, fleets


class TestJoinRedirectOnMerge:
    """Integration: join order redirect when target merges."""

    def test_join_redirect_on_merge(self):
        """Fleet A joins B, B joins C at same location. B merges first. A redirects to C."""
        empire, f = make_empire_with_fleets("a", "b", "c")

        # B and C at same location
        f["b"].location = HexCoord(50, 0)
        f["c"].location = HexCoord(50, 0)

        # A pursues B
        f["a"].add_order(FleetOrder(OrderType.MOVE_TO_FLEET, target=f["b"]))
        f["a"].add_order(FleetOrder(OrderType.JOIN_FLEET, target=f["b"]))
        f["b"].pursuer_tracker.add_pursuer(f["a"])

        # B merges into C
        f["b"].merge_with(f["c"])
        empire.remove_fleet(f["b"])

        # A's orders should now target C
        assert f["a"].orders[0].target is f["c"]
        assert f["a"].orders[1].target is f["c"]
        assert f["a"] in f["c"].pursuer_tracker.pursuers

    def test_intercept_redirect_on_merge(self):
        """Fleet A intercepts B. B joins C. A's MOVE_TO_FLEET redirects to C."""
        empire, f = make_empire_with_fleets("a", "b", "c")
        f["b"].location = HexCoord(50, 0)
        f["c"].location = HexCoord(50, 0)

        # A intercepts B (only MOVE_TO_FLEET, no JOIN_FLEET)
        f["a"].add_order(FleetOrder(OrderType.MOVE_TO_FLEET, target=f["b"]))
        f["b"].pursuer_tracker.add_pursuer(f["a"])

        # B merges into C
        f["b"].merge_with(f["c"])
        empire.remove_fleet(f["b"])

        # A's order redirected
        assert f["a"].orders[0].target is f["c"]
        assert f["a"] in f["c"].pursuer_tracker.pursuers

    def test_multihop_chain_three_levels(self):
        """A→B→C→D. D merges into E. C redirected to E. C merges into E. B redirected to E. B merges. A redirected."""
        empire, f = make_empire_with_fleets("a", "b", "c", "d", "e")
        # Put D and E at same location
        f["d"].location = HexCoord(100, 0)
        f["e"].location = HexCoord(100, 0)

        # Chain: A→B, B→C, C→D
        for src, tgt in [("a", "b"), ("b", "c"), ("c", "d")]:
            f[src].add_order(FleetOrder(OrderType.MOVE_TO_FLEET, target=f[tgt]))
            f[src].add_order(FleetOrder(OrderType.JOIN_FLEET, target=f[tgt]))
            f[tgt].pursuer_tracker.add_pursuer(f[src])

        # D merges into E → C redirected to E
        f["d"].merge_with(f["e"])
        empire.remove_fleet(f["d"])
        assert f["c"].orders[0].target is f["e"]
        assert f["c"] in f["e"].pursuer_tracker.pursuers

        # Move C to E's location and merge → B redirected to E
        f["c"].location = HexCoord(100, 0)
        f["c"].merge_with(f["e"])
        empire.remove_fleet(f["c"])
        assert f["b"].orders[0].target is f["e"]
        assert f["b"] in f["e"].pursuer_tracker.pursuers

        # Move B to E's location and merge → A redirected to E
        f["b"].location = HexCoord(100, 0)
        f["b"].merge_with(f["e"])
        empire.remove_fleet(f["b"])
        assert f["a"].orders[0].target is f["e"]
        assert f["a"] in f["e"].pursuer_tracker.pursuers

    def test_multiple_pursuers_all_redirected(self):
        """A, B, C all pursue D. D merges into E. All three redirect."""
        empire, f = make_empire_with_fleets("a", "b", "c", "d", "e")
        f["d"].location = HexCoord(50, 0)
        f["e"].location = HexCoord(50, 0)

        for src in ["a", "b", "c"]:
            f[src].add_order(FleetOrder(OrderType.MOVE_TO_FLEET, target=f["d"]))
            f["d"].pursuer_tracker.add_pursuer(f[src])

        f["d"].merge_with(f["e"])
        empire.remove_fleet(f["d"])

        for src in ["a", "b", "c"]:
            assert f[src].orders[0].target is f["e"]
            assert f[src] in f["e"].pursuer_tracker.pursuers
        assert f["e"].pursuer_tracker.pursuer_count == 3


class TestJoinCancelOnDestruction:
    """Integration: join order cancel when target is destroyed."""

    def test_join_cancel_on_destruction(self):
        """Fleet A joins B. B destroyed. A's orders cancelled."""
        empire, f = make_empire_with_fleets("a", "b")

        f["a"].add_order(FleetOrder(OrderType.MOVE_TO_FLEET, target=f["b"]))
        f["a"].add_order(FleetOrder(OrderType.JOIN_FLEET, target=f["b"]))
        f["b"].pursuer_tracker.add_pursuer(f["a"])

        # B destroyed
        empire.remove_fleet(f["b"])

        assert len(f["a"].orders) == 0
        assert f["b"].pursuer_tracker.pursuer_count == 0

    def test_destruction_preserves_non_targeting_orders(self):
        """Only orders targeting destroyed fleet are removed."""
        empire, f = make_empire_with_fleets("a", "b", "c")

        f["a"].add_order(FleetOrder(OrderType.MOVE, target=HexCoord(5, 5)))
        f["a"].add_order(FleetOrder(OrderType.MOVE_TO_FLEET, target=f["b"]))
        f["a"].add_order(FleetOrder(OrderType.MOVE_TO_FLEET, target=f["c"]))
        f["b"].pursuer_tracker.add_pursuer(f["a"])

        empire.remove_fleet(f["b"])

        assert len(f["a"].orders) == 2
        assert f["a"].orders[0].target == HexCoord(5, 5)
        assert f["a"].orders[1].target is f["c"]


class TestOrderLifecycleEdgeCases:
    """Integration: order manipulation during active pursuit."""

    def test_clear_orders_during_pursuit_unregisters(self):
        """Fleet A pursues B. User clears A's orders. A removed from B's pursuers."""
        empire, f = make_empire_with_fleets("a", "b")

        f["a"].add_order(FleetOrder(OrderType.MOVE_TO_FLEET, target=f["b"]))
        f["b"].pursuer_tracker.add_pursuer(f["a"])

        f["a"].clear_orders()
        assert f["b"].pursuer_tracker.pursuer_count == 0

    def test_delete_order_during_pursuit_unregisters(self):
        """Fleet A has [MOVE, MOVE_TO_FLEET→B, JOIN_FLEET→B]. Delete MOVE_TO_FLEET. Pursuer still registered (JOIN_FLEET remains)."""
        empire, f = make_empire_with_fleets("a", "b")

        f["a"].add_order(FleetOrder(OrderType.MOVE, target=HexCoord(1, 0)))
        f["a"].add_order(FleetOrder(OrderType.MOVE_TO_FLEET, target=f["b"]))
        f["a"].add_order(FleetOrder(OrderType.JOIN_FLEET, target=f["b"]))
        f["b"].pursuer_tracker.add_pursuer(f["a"])

        # Delete the MOVE_TO_FLEET order (index 1)
        f["a"].remove_order_at(1)

        # Still registered because JOIN_FLEET→B remains
        assert f["b"].pursuer_tracker.pursuer_count == 1

        # Now delete the JOIN_FLEET order (now at index 1)
        f["a"].remove_order_at(1)

        # Now fully unregistered
        assert f["b"].pursuer_tracker.pursuer_count == 0

    def test_self_join_rejected(self):
        """Validation: fleet cannot join itself."""
        from unittest.mock import Mock
        from game.strategy.engine.command_handlers import JoinCommandHandler

        fleet = Fleet("f1", 0, HexCoord(0, 0))
        session = Mock()
        session._get_fleet_by_id.return_value = fleet
        cmd = Mock(fleet_id="f1", target_fleet_id="f1")

        result = JoinCommandHandler().execute(session, cmd)
        assert not result.is_valid

    def test_cross_empire_join_rejected(self):
        """Validation: fleet cannot join fleet of another empire."""
        from unittest.mock import Mock
        from game.strategy.engine.command_handlers import JoinCommandHandler

        fleet = Fleet("f1", 0, HexCoord(0, 0))
        target = Fleet("f2", 1, HexCoord(5, 5))
        session = Mock()
        lookup = {"f1": fleet, "f2": target}
        session._get_fleet_by_id.side_effect = lambda fid: lookup.get(fid)
        cmd = Mock(fleet_id="f1", target_fleet_id="f2")

        result = JoinCommandHandler().execute(session, cmd)
        assert not result.is_valid
