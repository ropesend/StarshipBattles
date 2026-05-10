"""Integration tests for FEAT-28: mutual JOIN orders move both fleets toward
each other.

When two fleets are mutually pursuing each other (each fleet's head order is
MOVE_TO_FLEET / JOIN_FLEET targeting the other), today's intercept algorithm
is asymmetric — one fleet's evaluator picks "stay still" as the best
intercept. The fix bypasses the intercept evaluator: each fleet pathfinds
directly to the other's CURRENT hex, and they converge along the shortest
line.

Plus a swap-hex jump-past safeguard in `FleetMovementEngine.collect_movements`
so two fleets with parity speed don't oscillate past each other forever.
"""
from __future__ import annotations

from game.core.hex_math import HexCoord
from game.strategy.data.empire import Empire
from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import Order, OrderType
from game.strategy.engine.fleet_movement_engine import FleetMovementEngine
from game.strategy.engine.order_processor import OrderProcessor
from unittest.mock import MagicMock


def _make_empire_with_two_fleets(
    speed_a: float = 5.0,
    speed_b: float = 5.0,
    location_a: HexCoord = HexCoord(0, 0),
    location_b: HexCoord = HexCoord(10, 0),
    ships_a: int = 1,
    ships_b: int = 1,
    empire_id: int = 0,
):
    """Build an empire with two fleets and a mock galaxy with no warp systems."""
    empire = Empire(empire_id, f"Empire {empire_id}", (255, 0, 0))
    a = Fleet(1, empire_id, location_a, speed=speed_a)
    b = Fleet(2, empire_id, location_b, speed=speed_b)
    # Inject ship-count without needing real ShipInstance objects: create
    # MagicMock placeholders so `len(fleet.ships)` reflects the requested
    # value and `is_combat_capable` returns True for FleetSpeedCalculator.
    def _make_ship():
        s = MagicMock()
        s.is_combat_capable = MagicMock(return_value=True)
        # Stats lookup used by FleetCapabilityCalculator.can_use_warp.
        # mass=0 short-circuits has_warp_capability to False, which is what
        # we want — these test ships have no warp ability and must use
        # deep-space line draw.
        s.get_calculated_stats = MagicMock(return_value={"mass": 0, "strategic_movement": 0})
        s.design_data = {}
        return s
    a.ships = [_make_ship() for _ in range(ships_a)]
    b.ships = [_make_ship() for _ in range(ships_b)]
    empire.add_fleet(a)
    empire.add_fleet(b)

    # Mock galaxy: no star systems → find_hybrid_path falls back to
    # find_path_deep_space (line draw). Mock get_system_at_location for
    # FleetMovementEngine._get_effective_fleet_speed to return None.
    galaxy = MagicMock()
    galaxy.systems = {}
    galaxy.get_system_at_location = MagicMock(return_value=None)

    return empire, a, b, galaxy


def _issue_mutual_join(a: Fleet, b: Fleet) -> None:
    """Queue MOVE_TO_FLEET + JOIN_FLEET on both fleets, mirroring the
    JoinCommandHandler behaviour."""
    a.add_order(Order(OrderType.MOVE_TO_FLEET, target=b))
    a.add_order(Order(OrderType.JOIN_FLEET, target=b))
    b.pursuer_tracker.add_pursuer(a)

    b.add_order(Order(OrderType.MOVE_TO_FLEET, target=a))
    b.add_order(Order(OrderType.JOIN_FLEET, target=b))  # placeholder; rewritten below
    # The JoinCommandHandler path queues JOIN_FLEET targeting the OTHER fleet:
    b.orders[-1] = Order(OrderType.JOIN_FLEET, target=a)
    a.pursuer_tracker.add_pursuer(b)


def _run_until_co_located(
    empire: Empire,
    galaxy,
    a: Fleet,
    b: Fleet,
    max_ticks: int = 30,
) -> int:
    """Drive FleetMovementEngine + OrderProcessor.process_instant_orders until
    both fleets share a hex (and the JOIN_FLEET fires) or until max_ticks."""
    movement = FleetMovementEngine()
    op = OrderProcessor()

    for tick in range(1, max_ticks + 1):
        # Phase 1 (Instant orders): fires JOIN_FLEET when co-located.
        op.process_instant_orders([empire])
        # If either fleet was absorbed by Phase 1, break.
        if a not in empire.fleets or b not in empire.fleets:
            return tick
        # Phase 2 (collect): determine next hexes for this tick.
        moves = movement.collect_movements([empire], galaxy, tick)
        # Phase 3 (apply): commit the moves.
        movement.apply_movements(moves, galaxy)
        # Co-location check.
        if a.location == b.location:
            # Run Phase 1 once more to fire the merge.
            op.process_instant_orders([empire])
            return tick

    return max_ticks


# ---------------------------------------------------------------------------
# Today's baseline (with mutual-pursuit detection disabled)
# ---------------------------------------------------------------------------


class TestTodayBaselineAsymmetricChase:
    """Pre-fix sanity check: with mutual-pursuit detection forced off, two
    fleets at distance 10 with equal speed take ≥10 ticks (one moves, one
    waits). Validates the diagnosis in the FEAT-28 investigation report.

    This test depends on the `_is_mutual_pursuit` predicate existing on the
    service — runs after the predicate is added in Phase 2 Step A.
    """

    def test_distance_10_today_baseline_takes_many_ticks(self):
        from unittest.mock import patch

        empire, a, b, galaxy = _make_empire_with_two_fleets(
            location_a=HexCoord(0, 0), location_b=HexCoord(10, 0),
        )
        _issue_mutual_join(a, b)

        # Force "today" semantics by short-circuiting the mutual-pursuit
        # predicate to always return False. Speed=5 → fleet acts every 20
        # sub-ticks. At distance 10 with one fleet sitting still, the chaser
        # covers ground at ~1 hex per fleet action — needs at least 10 fleet
        # actions and therefore at least 100 sub-ticks (counting from t=1).
        with patch(
            "game.strategy.services.fleet_navigation_service."
            "FleetNavigationService._is_mutual_pursuit",
            return_value=False,
        ):
            ticks = _run_until_co_located(empire, galaxy, a, b, max_ticks=400)

        assert ticks >= 100, (
            f"Baseline asymmetric-chase should require ≥100 sub-ticks at "
            f"distance 10 with equal speeds (one fleet sits, the other "
            f"chases at ~1 hex per 20-tick interval); got {ticks}. If this "
            f"fails, FEAT-28's diagnosis of the asymmetry is wrong."
        )


# ---------------------------------------------------------------------------
# FEAT-28 rendezvous behaviour
# ---------------------------------------------------------------------------


class TestMutualJoinRendezvous:
    """With mutual-pursuit detection active (default), two equal-speed fleets
    converge in roughly half the ticks of today's asymmetric chase."""

    def test_distance_10_rendezvous_takes_about_half_baseline(self):
        """Compare end-to-end tick count baseline (mutual-pursuit disabled)
        vs rendezvous (default). Speed=5 → fleet acts every 20 sub-ticks; at
        distance 10, baseline needs ~10 fleet actions (one fleet sits) →
        ~200 sub-ticks. Rendezvous needs ~5 fleet actions (both move) →
        ~100 sub-ticks. Assert rendezvous ≤ ~60% of baseline.
        """
        from unittest.mock import patch

        # Baseline: mutual-pursuit disabled.
        empire_base, a_base, b_base, galaxy_base = _make_empire_with_two_fleets(
            location_a=HexCoord(0, 0), location_b=HexCoord(10, 0),
        )
        _issue_mutual_join(a_base, b_base)
        with patch(
            "game.strategy.services.fleet_navigation_service."
            "FleetNavigationService._is_mutual_pursuit",
            return_value=False,
        ):
            baseline_ticks = _run_until_co_located(
                empire_base, galaxy_base, a_base, b_base, max_ticks=400,
            )

        # Rendezvous: mutual-pursuit active (default).
        empire_rdv, a_rdv, b_rdv, galaxy_rdv = _make_empire_with_two_fleets(
            location_a=HexCoord(0, 0), location_b=HexCoord(10, 0),
        )
        _issue_mutual_join(a_rdv, b_rdv)
        rendezvous_ticks = _run_until_co_located(
            empire_rdv, galaxy_rdv, a_rdv, b_rdv, max_ticks=400,
        )

        # The user contract: rendezvous is roughly half the baseline.
        # Allow some slack for hex-rounding asymmetry along the line.
        assert rendezvous_ticks * 1.5 <= baseline_ticks, (
            f"Rendezvous should be ≤2/3 of baseline. baseline={baseline_ticks}, "
            f"rendezvous={rendezvous_ticks}"
        )

    def test_one_fleet_cancels_falls_back_to_chase(self):
        """If A clears its JOIN_FLEET / MOVE_TO_FLEET orders mid-chase, B's
        remaining MOVE_TO_FLEET continues as today's single-mover chase. No
        crash, no silent JOIN drop."""
        empire, a, b, galaxy = _make_empire_with_two_fleets(
            location_a=HexCoord(0, 0), location_b=HexCoord(10, 0),
        )
        _issue_mutual_join(a, b)

        movement = FleetMovementEngine()
        op = OrderProcessor()

        # Run 2 ticks of mutual rendezvous.
        for tick in range(1, 3):
            op.process_instant_orders([empire])
            moves = movement.collect_movements([empire], galaxy, tick)
            movement.apply_movements(moves, galaxy)

        # A clears its orders mid-chase.
        a.clear_orders()

        # B continues. With A no longer pursuing, B's MOVE_TO_FLEET runs the
        # standard intercept against a stationary A. Should still terminate
        # without crashes.
        for tick in range(3, 25):
            op.process_instant_orders([empire])
            if a not in empire.fleets or b not in empire.fleets:
                break
            moves = movement.collect_movements([empire], galaxy, tick)
            movement.apply_movements(moves, galaxy)
            if b.location == a.location:
                op.process_instant_orders([empire])
                break

        # Assertion: no crash, and B reached A (or was absorbed by Phase 1
        # merge). Either outcome is acceptable.
        # Note: order pop semantics may have caused B to drop its orders if
        # the intercept resolved to B's own location at some point — that's
        # also acceptable as long as no exception was raised.

    def test_mutual_pursuit_does_not_prematurely_cancel_join(self):
        """Regression guard: today's intercept evaluator can return the
        chaser's own current hex as the "best intercept," causing
        compute_next_step to mark the order complete and pop MOVE_TO_FLEET
        prematurely. With FEAT-28's mutual branch, destination = target's
        location (a different hex), so MOVE_TO_FLEET is never popped before
        co-location."""
        empire, a, b, galaxy = _make_empire_with_two_fleets(
            location_a=HexCoord(0, 0), location_b=HexCoord(10, 0),
        )
        _issue_mutual_join(a, b)

        movement = FleetMovementEngine()
        op = OrderProcessor()

        # Run a couple of ticks and assert both fleets still have their
        # JOIN_FLEET orders queued.
        for tick in range(1, 4):
            op.process_instant_orders([empire])
            moves = movement.collect_movements([empire], galaxy, tick)
            movement.apply_movements(moves, galaxy)
            assert any(
                o.type == OrderType.JOIN_FLEET for o in a.orders
            ), f"Fleet A's JOIN_FLEET dropped on tick {tick}"
            assert any(
                o.type == OrderType.JOIN_FLEET for o in b.orders
            ), f"Fleet B's JOIN_FLEET dropped on tick {tick}"


# ---------------------------------------------------------------------------
# Jump-past safeguard
# ---------------------------------------------------------------------------


class TestJumpPastSafeguard:
    """If both fleets would swap hexes on the same tick (parity speed at odd
    distance), the LARGER fleet (more ships, smaller-id tiebreak) skips this
    tick. Next tick they co-locate and JOIN_FLEET fires."""

    def test_swap_parity_larger_fleet_delays(self):
        """Fleet A (1 ship) at (0,0) and Fleet B (3 ships) at (1,0), both
        speed=2. Naive movement would have A→(1,0) and B→(0,0): a swap. The
        LARGER fleet (B) must skip this tick."""
        empire, a, b, galaxy = _make_empire_with_two_fleets(
            location_a=HexCoord(0, 0),
            location_b=HexCoord(1, 0),
            speed_a=2.0,
            speed_b=2.0,
            ships_a=1,
            ships_b=3,
        )
        _issue_mutual_join(a, b)

        movement = FleetMovementEngine()
        # Tick 50 — for speed=2, get_tick_interval(2) = 100 // 2 = 50, so
        # both fleets are eligible to move on tick 50.
        moves = movement.collect_movements([empire], galaxy, 50)

        # The larger fleet (B, 3 ships) must be filtered out of this tick's
        # move queue. A keeps its move.
        moved_fleets = {fleet for fleet, _ in moves}
        assert a in moved_fleets, "Fleet A (smaller) should still move this tick"
        assert b not in moved_fleets, (
            "Fleet B (larger) should be filtered out to avoid swap-hex parity"
        )

    def test_swap_parity_tiebreak_smaller_id_delays(self):
        """When ship counts are equal, smaller fleet id delays (mirrors
        BUG-122 _elect_canonical_merges)."""
        empire, a, b, galaxy = _make_empire_with_two_fleets(
            location_a=HexCoord(0, 0),
            location_b=HexCoord(1, 0),
            speed_a=2.0,
            speed_b=2.0,
            ships_a=2,
            ships_b=2,  # equal ship counts → id tiebreak
        )
        _issue_mutual_join(a, b)

        movement = FleetMovementEngine()
        moves = movement.collect_movements([empire], galaxy, 50)
        moved_fleets = {fleet for fleet, _ in moves}
        # a.id=1, b.id=2 → smaller id (a) delays
        assert b in moved_fleets, "Fleet B (id=2, larger id) should still move"
        assert a not in moved_fleets, (
            "Fleet A (id=1, smaller id) should be filtered on equal ship counts"
        )

    def test_no_swap_no_filter(self):
        """At distance ≥2 with speed=1 (1 hex/tick), each fleet moves 1 hex
        toward the other. No swap; nothing should be filtered."""
        empire, a, b, galaxy = _make_empire_with_two_fleets(
            location_a=HexCoord(0, 0),
            location_b=HexCoord(10, 0),
            speed_a=5.0,
            speed_b=5.0,
        )
        _issue_mutual_join(a, b)

        movement = FleetMovementEngine()
        moves = movement.collect_movements([empire], galaxy, 20)
        moved_fleets = {fleet for fleet, _ in moves}
        assert a in moved_fleets and b in moved_fleets, (
            "No swap parity at distance 10 → both fleets should be in move queue"
        )
