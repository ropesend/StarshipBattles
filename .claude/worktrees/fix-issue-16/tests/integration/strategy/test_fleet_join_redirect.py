"""Integration tests for fleet join order redirect and pursuer tracking (PROJ-222).

Tests end-to-end flows: multi-hop chains, concurrent merges, destruction
cancel, order lifecycle, and validation.
"""

from game.core.hex_math import HexCoord
from game.strategy.data.fleet import Fleet
from game.strategy.data.empire import Empire
from game.strategy.data.order_types import Order, OrderType


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
        f["a"].add_order(Order(OrderType.MOVE_TO_FLEET, target=f["b"]))
        f["a"].add_order(Order(OrderType.JOIN_FLEET, target=f["b"]))
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
        f["a"].add_order(Order(OrderType.MOVE_TO_FLEET, target=f["b"]))
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
            f[src].add_order(Order(OrderType.MOVE_TO_FLEET, target=f[tgt]))
            f[src].add_order(Order(OrderType.JOIN_FLEET, target=f[tgt]))
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
            f[src].add_order(Order(OrderType.MOVE_TO_FLEET, target=f["d"]))
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

        f["a"].add_order(Order(OrderType.MOVE_TO_FLEET, target=f["b"]))
        f["a"].add_order(Order(OrderType.JOIN_FLEET, target=f["b"]))
        f["b"].pursuer_tracker.add_pursuer(f["a"])

        # B destroyed
        empire.remove_fleet(f["b"])

        assert len(f["a"].orders) == 0
        assert f["b"].pursuer_tracker.pursuer_count == 0

    def test_destruction_preserves_non_targeting_orders(self):
        """Only orders targeting destroyed fleet are removed."""
        empire, f = make_empire_with_fleets("a", "b", "c")

        f["a"].add_order(Order(OrderType.MOVE, target=HexCoord(5, 5)))
        f["a"].add_order(Order(OrderType.MOVE_TO_FLEET, target=f["b"]))
        f["a"].add_order(Order(OrderType.MOVE_TO_FLEET, target=f["c"]))
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

        f["a"].add_order(Order(OrderType.MOVE_TO_FLEET, target=f["b"]))
        f["b"].pursuer_tracker.add_pursuer(f["a"])

        f["a"].clear_orders()
        assert f["b"].pursuer_tracker.pursuer_count == 0

    def test_delete_order_during_pursuit_unregisters(self):
        """Fleet A has [MOVE, MOVE_TO_FLEET→B, JOIN_FLEET→B]. Delete MOVE_TO_FLEET. Pursuer still registered (JOIN_FLEET remains)."""
        empire, f = make_empire_with_fleets("a", "b")

        f["a"].add_order(Order(OrderType.MOVE, target=HexCoord(1, 0)))
        f["a"].add_order(Order(OrderType.MOVE_TO_FLEET, target=f["b"]))
        f["a"].add_order(Order(OrderType.JOIN_FLEET, target=f["b"]))
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


class TestMutualAndCyclicJoin:
    """BUG-122: mutual / cyclic / convergent JOIN_FLEET semantics.

    Three structural failures interacted to silently destroy fleets:
    1. process_instant_orders snapshotted candidates without re-validating
       aliveness during execution.
    2. _execute_fleet_merge unconditionally removed the source even when
       the target was already absorbed.
    3. redirect_pursuers rewrote the absorbing fleet's own pursuit order
       onto itself, creating a self-join cycle.
    """

    def _add_dummy_ships(self, fleet, count):
        """Append `count` placeholder ship stand-ins for ship-count assertions.

        Returns is_combat_capable=False so FleetSpeedCalculator skips them
        during merge-triggered speed recalc — the bug under test is about
        fleet/order plumbing, not speed."""
        class _DummyShip:
            def is_combat_capable(self):
                return False
        for _ in range(count):
            fleet.ships.append(_DummyShip())

    def test_mutual_join_equal_ships_smaller_id_wins(self):
        """F2 ↔ F3 mutual JOIN_FLEET, equal ships → smaller id wins, all ships in survivor."""
        from game.strategy.engine.order_processor import OrderProcessor

        empire = Empire(0, "E", (255, 0, 0))
        f2 = Fleet("f2", 0, HexCoord(50, 0))
        f3 = Fleet("f3", 0, HexCoord(50, 0))
        empire.add_fleet(f2)
        empire.add_fleet(f3)
        self._add_dummy_ships(f2, 1)
        self._add_dummy_ships(f3, 1)

        f2.add_order(Order(OrderType.JOIN_FLEET, target=f3))
        f3.add_order(Order(OrderType.JOIN_FLEET, target=f2))
        f3.pursuer_tracker.add_pursuer(f2)
        f2.pursuer_tracker.add_pursuer(f3)

        OrderProcessor().process_instant_orders([empire])

        assert len(empire.fleets) == 1, (
            f"Expected exactly one survivor, got {[f.id for f in empire.fleets]}"
        )
        survivor = empire.fleets[0]
        assert survivor.id == "f2", "Smaller id should win on tie"
        assert len(survivor.ships) == 2, "All ships should be in the survivor"

    def test_mutual_join_unequal_ships_more_ships_wins(self):
        """F2 (3 ships) ↔ F3 (1 ship) → F2 wins regardless of id ordering."""
        from game.strategy.engine.order_processor import OrderProcessor

        empire = Empire(0, "E", (255, 0, 0))
        # Use ids where smaller-id tiebreaker would pick the LOSER, to prove
        # that ship-count is the primary criterion.
        big = Fleet("z_big", 0, HexCoord(50, 0))
        small = Fleet("a_small", 0, HexCoord(50, 0))
        empire.add_fleet(big)
        empire.add_fleet(small)
        self._add_dummy_ships(big, 3)
        self._add_dummy_ships(small, 1)

        big.add_order(Order(OrderType.JOIN_FLEET, target=small))
        small.add_order(Order(OrderType.JOIN_FLEET, target=big))
        small.pursuer_tracker.add_pursuer(big)
        big.pursuer_tracker.add_pursuer(small)

        OrderProcessor().process_instant_orders([empire])

        assert len(empire.fleets) == 1
        survivor = empire.fleets[0]
        assert survivor.id == "z_big", "More ships should win, ignoring id ordering"
        assert len(survivor.ships) == 4

    def test_redirect_does_not_create_self_join_order(self):
        """BUG-122 Failure 3: F3 pursues F2; F2 merges into F3 → F3's order
        targeting F2 must be dropped, not rewritten to target F3 itself."""
        empire = Empire(0, "E", (255, 0, 0))
        f2 = Fleet("f2", 0, HexCoord(50, 0))
        f3 = Fleet("f3", 0, HexCoord(50, 0))
        empire.add_fleet(f2)
        empire.add_fleet(f3)

        # F3 has a JOIN_FLEET order targeting F2 → F3 is a pursuer of F2
        f3.add_order(Order(OrderType.JOIN_FLEET, target=f2))
        f2.pursuer_tracker.add_pursuer(f3)

        # F2 merges into F3 directly (isolating Failure 3)
        f2.merge_with(f3)
        empire.remove_fleet(f2)

        # F3 must not have any self-targeting orders
        for order in f3.orders:
            assert order.target is not f3, (
                f"BUG-122 Failure 3: F3 has self-targeting order: {order.type}"
            )
        # F3 must not be its own pursuer
        assert f3 not in f3.pursuer_tracker.pursuers

    def test_three_fleet_cycle_one_survives_no_ships_lost(self):
        """F1 → F2 → F3 → F1 at same hex. Whichever direction iterates first
        wins; the rest must skip with target_absorbed_mid_iteration. Total
        ship count is preserved and exactly one fleet survives."""
        from game.strategy.engine.order_processor import OrderProcessor

        empire = Empire(0, "E", (255, 0, 0))
        f1 = Fleet("f1", 0, HexCoord(50, 0))
        f2 = Fleet("f2", 0, HexCoord(50, 0))
        f3 = Fleet("f3", 0, HexCoord(50, 0))
        empire.add_fleet(f1)
        empire.add_fleet(f2)
        empire.add_fleet(f3)
        self._add_dummy_ships(f1, 1)
        self._add_dummy_ships(f2, 1)
        self._add_dummy_ships(f3, 1)

        f1.add_order(Order(OrderType.JOIN_FLEET, target=f2))
        f2.add_order(Order(OrderType.JOIN_FLEET, target=f3))
        f3.add_order(Order(OrderType.JOIN_FLEET, target=f1))
        f2.pursuer_tracker.add_pursuer(f1)
        f3.pursuer_tracker.add_pursuer(f2)
        f1.pursuer_tracker.add_pursuer(f3)

        OrderProcessor().process_instant_orders([empire])

        assert len(empire.fleets) == 1, (
            f"Expected one survivor in 3-cycle, got {[f.id for f in empire.fleets]}"
        )
        survivor = empire.fleets[0]
        assert len(survivor.ships) == 3, (
            f"All 3 ships should be in survivor, got {len(survivor.ships)}"
        )

    def test_convergent_join_target_absorbed_mid_iteration(self):
        """F4 → F5 → F2 ↔ F3 at same hex. F2/F3 mutual-merge first, then
        F5 finds its target (F2) gone. F5 must NOT silently drop ships;
        ship count across the empire must be preserved."""
        from game.strategy.engine.order_processor import OrderProcessor

        empire = Empire(0, "E", (255, 0, 0))
        f2 = Fleet("f2", 0, HexCoord(50, 0))
        f3 = Fleet("f3", 0, HexCoord(50, 0))
        f4 = Fleet("f4", 0, HexCoord(50, 0))
        f5 = Fleet("f5", 0, HexCoord(50, 0))
        for fl in (f2, f3, f4, f5):
            empire.add_fleet(fl)
            self._add_dummy_ships(fl, 1)

        # F4 → F5
        f4.add_order(Order(OrderType.JOIN_FLEET, target=f5))
        f5.pursuer_tracker.add_pursuer(f4)
        # F5 → F2
        f5.add_order(Order(OrderType.JOIN_FLEET, target=f2))
        f2.pursuer_tracker.add_pursuer(f5)
        # F2 ↔ F3
        f2.add_order(Order(OrderType.JOIN_FLEET, target=f3))
        f3.add_order(Order(OrderType.JOIN_FLEET, target=f2))
        f3.pursuer_tracker.add_pursuer(f2)
        f2.pursuer_tracker.add_pursuer(f3)

        initial_total = sum(len(fl.ships) for fl in (f2, f3, f4, f5))

        OrderProcessor().process_instant_orders([empire])

        final_total = sum(len(fl.ships) for fl in empire.fleets)
        assert final_total == initial_total, (
            f"BUG-122: ships were lost. Started with {initial_total}, ended with {final_total}"
        )
