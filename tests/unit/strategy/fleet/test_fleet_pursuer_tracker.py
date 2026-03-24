"""Tests for FleetPursuerTracker delegate (PROJ-222)."""

import pytest
from game.core.hex_math import HexCoord
from game.strategy.data.fleet import Fleet
from game.strategy.data.fleet_pursuer_tracker import FleetPursuerTracker
from game.strategy.data.order_types import FleetOrder, OrderType


def make_fleet(fleet_id, location=None):
    """Helper to create a Fleet with a FleetPursuerTracker."""
    loc = location or HexCoord(0, 0)
    return Fleet(fleet_id=fleet_id, owner_id=0, location=loc)


class TestAddRemovePursuer:
    """Tests for basic pursuer registration and unregistration."""

    def test_add_and_remove_pursuer(self):
        target = make_fleet("target")
        pursuer = make_fleet("pursuer")
        tracker = FleetPursuerTracker(target)

        tracker.add_pursuer(pursuer)
        assert pursuer in tracker.pursuers
        assert tracker.pursuer_count == 1

        tracker.remove_pursuer(pursuer)
        assert pursuer not in tracker.pursuers
        assert tracker.pursuer_count == 0

    def test_add_duplicate_pursuer_is_idempotent(self):
        target = make_fleet("target")
        pursuer = make_fleet("pursuer")
        tracker = FleetPursuerTracker(target)

        tracker.add_pursuer(pursuer)
        tracker.add_pursuer(pursuer)
        assert tracker.pursuer_count == 1

    def test_remove_nonexistent_pursuer_is_safe(self):
        target = make_fleet("target")
        pursuer = make_fleet("pursuer")
        tracker = FleetPursuerTracker(target)

        # Should not raise
        tracker.remove_pursuer(pursuer)
        assert tracker.pursuer_count == 0

    def test_pursuers_returns_frozenset(self):
        target = make_fleet("target")
        tracker = FleetPursuerTracker(target)
        assert isinstance(tracker.pursuers, frozenset)


class TestRedirectPursuers:
    """Tests for redirecting pursuers to a new target on merge."""

    def test_redirect_pursuers_rewrites_order_targets(self):
        old_target = make_fleet("old_target")
        new_target = make_fleet("new_target")
        pursuer_a = make_fleet("pursuer_a")
        pursuer_b = make_fleet("pursuer_b")

        # Give pursuers orders targeting old_target
        pursuer_a.add_order(FleetOrder(OrderType.MOVE_TO_FLEET, target=old_target))
        pursuer_a.add_order(FleetOrder(OrderType.JOIN_FLEET, target=old_target))
        pursuer_b.add_order(FleetOrder(OrderType.MOVE_TO_FLEET, target=old_target))

        tracker = FleetPursuerTracker(old_target)
        tracker.add_pursuer(pursuer_a)
        tracker.add_pursuer(pursuer_b)

        tracker.redirect_pursuers(new_target)

        # All order targets should now point to new_target
        assert pursuer_a.orders[0].target is new_target
        assert pursuer_a.orders[1].target is new_target
        assert pursuer_b.orders[0].target is new_target

    def test_redirect_pursuers_transfers_to_new_target(self):
        old_target = make_fleet("old_target")
        new_target = make_fleet("new_target")
        pursuer = make_fleet("pursuer")
        pursuer.add_order(FleetOrder(OrderType.MOVE_TO_FLEET, target=old_target))

        tracker = FleetPursuerTracker(old_target)
        tracker.add_pursuer(pursuer)

        # new_target needs its own tracker
        new_tracker = FleetPursuerTracker(new_target)
        new_target._pursuer_tracker = new_tracker

        tracker.redirect_pursuers(new_target)

        assert new_tracker.pursuer_count == 1
        assert pursuer in new_tracker.pursuers

    def test_redirect_pursuers_clears_source(self):
        old_target = make_fleet("old_target")
        new_target = make_fleet("new_target")
        pursuer = make_fleet("pursuer")
        pursuer.add_order(FleetOrder(OrderType.MOVE_TO_FLEET, target=old_target))

        tracker = FleetPursuerTracker(old_target)
        tracker.add_pursuer(pursuer)

        tracker.redirect_pursuers(new_target)

        assert tracker.pursuer_count == 0

    def test_redirect_pursuers_returns_redirected_list(self):
        old_target = make_fleet("old_target")
        new_target = make_fleet("new_target")
        pursuer = make_fleet("pursuer")
        pursuer.add_order(FleetOrder(OrderType.MOVE_TO_FLEET, target=old_target))

        tracker = FleetPursuerTracker(old_target)
        tracker.add_pursuer(pursuer)

        result = tracker.redirect_pursuers(new_target)
        assert len(result) == 1
        assert result[0][0] is pursuer  # (pursuer, old_target)

    def test_redirect_preserves_non_targeting_orders(self):
        old_target = make_fleet("old_target")
        new_target = make_fleet("new_target")
        other_fleet = make_fleet("other")
        pursuer = make_fleet("pursuer")

        # Mix of orders — some targeting old_target, some targeting other
        pursuer.add_order(FleetOrder(OrderType.MOVE, target=HexCoord(5, 5)))
        pursuer.add_order(FleetOrder(OrderType.MOVE_TO_FLEET, target=old_target))
        pursuer.add_order(FleetOrder(OrderType.MOVE_TO_FLEET, target=other_fleet))

        tracker = FleetPursuerTracker(old_target)
        tracker.add_pursuer(pursuer)

        tracker.redirect_pursuers(new_target)

        # MOVE order unchanged
        assert pursuer.orders[0].target == HexCoord(5, 5)
        # old_target order redirected
        assert pursuer.orders[1].target is new_target
        # other_fleet order unchanged
        assert pursuer.orders[2].target is other_fleet

    def test_redirect_empty_pursuers_does_nothing(self):
        old_target = make_fleet("old_target")
        new_target = make_fleet("new_target")
        tracker = FleetPursuerTracker(old_target)

        result = tracker.redirect_pursuers(new_target)
        assert result == []


class TestUnregisterOnOrderRemoval:
    """Tests for pursuer unregistration when orders are removed from Fleet (PROJ-222 Phase 3)."""

    def test_clear_orders_unregisters_pursuers(self):
        target = make_fleet("target")
        pursuer = make_fleet("pursuer")
        pursuer.add_order(FleetOrder(OrderType.MOVE_TO_FLEET, target=target))
        target.pursuer_tracker.add_pursuer(pursuer)

        pursuer.clear_orders()
        assert target.pursuer_tracker.pursuer_count == 0

    def test_pop_order_unregisters_pursuer(self):
        target = make_fleet("target")
        pursuer = make_fleet("pursuer")
        pursuer.add_order(FleetOrder(OrderType.MOVE_TO_FLEET, target=target))
        target.pursuer_tracker.add_pursuer(pursuer)

        pursuer.pop_order()
        assert target.pursuer_tracker.pursuer_count == 0

    def test_remove_order_at_unregisters_pursuer(self):
        target = make_fleet("target")
        pursuer = make_fleet("pursuer")
        pursuer.add_order(FleetOrder(OrderType.MOVE, target=HexCoord(1, 0)))
        pursuer.add_order(FleetOrder(OrderType.MOVE_TO_FLEET, target=target))
        target.pursuer_tracker.add_pursuer(pursuer)

        pursuer.remove_order_at(1)
        assert target.pursuer_tracker.pursuer_count == 0

    def test_unregister_handles_non_fleet_target_gracefully(self):
        """Order with HexCoord target should not crash on unregister."""
        fleet = make_fleet("f1")
        fleet.add_order(FleetOrder(OrderType.MOVE, target=HexCoord(5, 5)))

        # Should not raise
        fleet.pop_order()
        fleet.clear_orders()

    def test_remove_orders_by_type_unregisters_pursuers(self):
        target = make_fleet("target")
        pursuer = make_fleet("pursuer")
        pursuer.add_order(FleetOrder(OrderType.MOVE_TO_FLEET, target=target))
        pursuer.add_order(FleetOrder(OrderType.JOIN_FLEET, target=target))
        target.pursuer_tracker.add_pursuer(pursuer)

        pursuer.remove_orders_by_type(OrderType.MOVE_TO_FLEET)
        # Still registered because JOIN_FLEET order remains
        # (remove_orders_by_type only removes matching type, pursuer still targets)
        # Actually, removing MOVE_TO_FLEET should call unregister for that order
        # but pursuer is still registered via JOIN_FLEET — that's fine
        assert target.pursuer_tracker.pursuer_count == 1


class TestMergeWithRedirect:
    """Tests for pursuer redirect during Fleet.merge_with() (PROJ-222 Phase 4)."""

    def test_merge_with_redirects_pursuers(self):
        """Fleet A pursues B, B merges into C. A should now pursue C."""
        fleet_a = make_fleet("a")
        fleet_b = make_fleet("b")
        fleet_c = make_fleet("c")

        # A has orders targeting B
        fleet_a.add_order(FleetOrder(OrderType.MOVE_TO_FLEET, target=fleet_b))
        fleet_a.add_order(FleetOrder(OrderType.JOIN_FLEET, target=fleet_b))
        fleet_b.pursuer_tracker.add_pursuer(fleet_a)

        # B merges into C
        fleet_b.merge_with(fleet_c)

        # A's orders should now target C
        assert fleet_a.orders[0].target is fleet_c
        assert fleet_a.orders[1].target is fleet_c
        # A should be registered as pursuer of C
        assert fleet_a in fleet_c.pursuer_tracker.pursuers
        # B's pursuer tracker should be empty
        assert fleet_b.pursuer_tracker.pursuer_count == 0

    def test_merge_with_multihop_chain(self):
        """A→B→C. C merges into D. B redirected to D. Then B merges into D. A redirected to D."""
        fleet_a = make_fleet("a")
        fleet_b = make_fleet("b")
        fleet_c = make_fleet("c")
        fleet_d = make_fleet("d")

        # A pursues B
        fleet_a.add_order(FleetOrder(OrderType.MOVE_TO_FLEET, target=fleet_b))
        fleet_b.pursuer_tracker.add_pursuer(fleet_a)

        # B pursues C
        fleet_b.add_order(FleetOrder(OrderType.MOVE_TO_FLEET, target=fleet_c))
        fleet_b.add_order(FleetOrder(OrderType.JOIN_FLEET, target=fleet_c))
        fleet_c.pursuer_tracker.add_pursuer(fleet_b)

        # C merges into D → B's orders redirect to D
        fleet_c.merge_with(fleet_d)
        assert fleet_b.orders[0].target is fleet_d  # MOVE_TO_FLEET redirected
        assert fleet_b.orders[1].target is fleet_d  # JOIN_FLEET redirected
        assert fleet_b in fleet_d.pursuer_tracker.pursuers

        # B merges into D → A's orders redirect to D
        fleet_b.merge_with(fleet_d)
        assert fleet_a.orders[0].target is fleet_d
        assert fleet_a in fleet_d.pursuer_tracker.pursuers

    def test_merge_with_no_pursuers_does_nothing(self):
        """Merge with no pursuers should not error."""
        fleet_a = make_fleet("a")
        fleet_b = make_fleet("b")
        fleet_a.merge_with(fleet_b)
        # No error, no pursuers to redirect

    def test_merge_with_multiple_pursuers(self):
        """Multiple pursuers all get redirected."""
        target = make_fleet("target")
        new_target = make_fleet("new_target")
        pursuers = [make_fleet(f"p{i}") for i in range(3)]

        for p in pursuers:
            p.add_order(FleetOrder(OrderType.MOVE_TO_FLEET, target=target))
            target.pursuer_tracker.add_pursuer(p)

        target.merge_with(new_target)

        for p in pursuers:
            assert p.orders[0].target is new_target
            assert p in new_target.pursuer_tracker.pursuers


class TestNotifyTargetDestroyed:
    """Tests for cancelling pursuer orders on target destruction."""

    def test_notify_target_destroyed_removes_orders(self):
        target = make_fleet("target")
        pursuer = make_fleet("pursuer")

        pursuer.add_order(FleetOrder(OrderType.MOVE_TO_FLEET, target=target))
        pursuer.add_order(FleetOrder(OrderType.JOIN_FLEET, target=target))

        tracker = FleetPursuerTracker(target)
        tracker.add_pursuer(pursuer)

        tracker.notify_target_destroyed()

        # Both targeting orders should be removed
        assert len(pursuer.orders) == 0

    def test_notify_target_destroyed_returns_affected(self):
        target = make_fleet("target")
        pursuer_a = make_fleet("pursuer_a")
        pursuer_b = make_fleet("pursuer_b")

        pursuer_a.add_order(FleetOrder(OrderType.MOVE_TO_FLEET, target=target))
        pursuer_b.add_order(FleetOrder(OrderType.JOIN_FLEET, target=target))

        tracker = FleetPursuerTracker(target)
        tracker.add_pursuer(pursuer_a)
        tracker.add_pursuer(pursuer_b)

        result = tracker.notify_target_destroyed()
        assert len(result) == 2
        assert pursuer_a in result
        assert pursuer_b in result

    def test_notify_target_destroyed_preserves_other_orders(self):
        target = make_fleet("target")
        other = make_fleet("other")
        pursuer = make_fleet("pursuer")

        pursuer.add_order(FleetOrder(OrderType.MOVE, target=HexCoord(3, 3)))
        pursuer.add_order(FleetOrder(OrderType.MOVE_TO_FLEET, target=target))
        pursuer.add_order(FleetOrder(OrderType.MOVE_TO_FLEET, target=other))

        tracker = FleetPursuerTracker(target)
        tracker.add_pursuer(pursuer)

        tracker.notify_target_destroyed()

        # Only the order targeting 'target' should be removed
        assert len(pursuer.orders) == 2
        assert pursuer.orders[0].target == HexCoord(3, 3)
        assert pursuer.orders[1].target is other

    def test_notify_target_destroyed_clears_pursuers(self):
        target = make_fleet("target")
        pursuer = make_fleet("pursuer")
        pursuer.add_order(FleetOrder(OrderType.MOVE_TO_FLEET, target=target))

        tracker = FleetPursuerTracker(target)
        tracker.add_pursuer(pursuer)

        tracker.notify_target_destroyed()
        assert tracker.pursuer_count == 0

    def test_notify_empty_pursuers_does_nothing(self):
        target = make_fleet("target")
        tracker = FleetPursuerTracker(target)

        result = tracker.notify_target_destroyed()
        assert result == []
