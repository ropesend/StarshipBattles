"""PROJ-436 Phase 12 (Option C): Fleet fractional resource-cost contract
under the unified ``IProductionResourceSource`` protocol.

Pins the **truth-up via read-back** contract introduced by Phase 12:
``ProductionEngine._apply_resource_consumption`` records what the
source actually charged (computed as the before/after diff of
``production_get_resource``), NOT the requested float ``amount``. This
closes the Phase 11 Codex finding #1 contract-drift bug where fleet
construction could silently build for free or overpay on fractional
per-step costs because ``Fleet.consume_cargo_resource`` rounds the
requested amount to an integer before unloading.

The two failing-pre-Phase-12 shapes are the engine-call-level
reproductions Codex used in the consult response:

1. **free-build:** seed cargo=1, drive ten ``0.1`` consume calls.
   Pre-fix: ``int(round(0.1))`` = 0 each time, cargo stays at 1, but
   ``resources_consumed`` reaches ~0.999 and the build progresses
   without paying. Post-fix: ``resources_consumed`` matches the
   actual diff (0 for all ten calls), and the build correctly
   makes no progress on this resource.
2. **overpay:** seed cargo=2, drive one ``0.6`` consume call.
   Pre-fix: ``int(round(0.6))`` = 1, cargo becomes 1, but
   ``resources_consumed`` records 0.6 → fleet overpays by 0.4.
   Post-fix: ``resources_consumed`` records 1.0 (the actual diff).

Planet (whose stockpile is float-typed) is unaffected because its
``consume_from_stockpile`` consumes the exact float ``amount``; the
before/after diff equals the requested amount.
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from game.strategy.data.empire import Empire
from game.strategy.data.fleet import Fleet
from game.strategy.data.planet import Planet
from game.strategy.engine.production_engine import ProductionEngine
from game.strategy.events.event_types import EventType
from tests.fixtures.strategy_entities import (
    create_test_fleet,
    create_test_planet,
)


@pytest.fixture
def engine(fresh_registries) -> ProductionEngine:
    return ProductionEngine(registries=fresh_registries, event_bus=MagicMock())


def _empire() -> Empire:
    return Empire(empire_id=1, name="Phase12", color=(0, 0, 0))


class TestFleetFractionalCostFreeBuildBugClosed:
    """Repeated tiny-fractional consume calls against integer-typed
    fleet cargo MUST NOT silently advance the resources_consumed
    tracker beyond what the fleet actually paid.
    """

    def test_ten_tenth_consumes_against_one_cargo_records_zero(self, engine):
        fleet: Fleet = create_test_fleet(num_ships=1)
        fleet.ships[0]._cargo_mgr.set_cargo("metals", 1)
        assert fleet.get_cargo_resource("metals") == 1.0

        item: dict = {"resources_consumed": {"metals": 0.0}}

        for _ in range(10):
            engine._apply_resource_consumption(
                _empire(), item, {"metals": 0.1}, fleet,
            )

        # Truth-up contract: resources_consumed reflects what fleet
        # ACTUALLY charged, not what the engine requested.
        # int(round(0.1)) = 0 → fleet charges nothing → tracker stays 0.
        assert fleet.get_cargo_resource("metals") == 1.0
        assert item["resources_consumed"]["metals"] == 0.0


class TestFleetFractionalCostOverpayBugClosed:
    """A single fractional consume call that rounds UP against
    integer-typed fleet cargo MUST record the actual integer charge
    (1.0), not the requested fractional amount (0.6).
    """

    def test_single_point_six_consume_against_two_cargo_records_one(self, engine):
        fleet: Fleet = create_test_fleet(num_ships=1)
        fleet.ships[0]._cargo_mgr.set_cargo("metals", 2)
        assert fleet.get_cargo_resource("metals") == 2.0

        item: dict = {"resources_consumed": {"metals": 0.0}}

        engine._apply_resource_consumption(
            _empire(), item, {"metals": 0.6}, fleet,
        )

        # int(round(0.6)) = 1 → fleet charges 1, cargo goes 2 → 1.
        # Truth-up contract: resources_consumed records the diff = 1.0.
        assert fleet.get_cargo_resource("metals") == 1.0
        assert item["resources_consumed"]["metals"] == 1.0


class TestPlanetFractionalCostStillExact:
    """Planet stockpile is float-typed; its ``consume_from_stockpile``
    consumes the exact float amount. The before/after diff equals
    the requested amount; behavior is unchanged from pre-Phase-12.
    """

    def test_fractional_planet_consume_records_exact_amount(self, engine):
        planet: Planet = create_test_planet(
            has_facilities=False, has_population=False,
            _stockpile={"metals": 1.0},
        )
        item: dict = {"resources_consumed": {"metals": 0.0}}

        engine._apply_resource_consumption(
            _empire(), item, {"metals": 0.6}, planet,
        )

        # Planet stockpile consumes 0.6 exactly.
        assert planet.get_stockpile("metals") == pytest.approx(0.4)
        assert item["resources_consumed"]["metals"] == pytest.approx(0.6)


class TestWholeNumberAccountingUnchanged:
    """The common-case whole-number consume path still works: the
    diff-based accounting agrees with the requested amount when the
    source accepts the full amount as-is. Sanity baseline against
    regression of the Phase 8 integration tests.
    """

    def test_whole_number_fleet_consume_records_requested_amount(self, engine):
        fleet: Fleet = create_test_fleet(num_ships=1)
        fleet.ships[0]._cargo_mgr.set_cargo("metals", 100)

        item: dict = {"resources_consumed": {}}
        engine._apply_resource_consumption(
            _empire(), item, {"metals": 40.0}, fleet,
        )

        assert fleet.get_cargo_resource("metals") == 60.0
        assert item["resources_consumed"]["metals"] == 40.0

    def test_whole_number_planet_consume_records_requested_amount(self, engine):
        planet: Planet = create_test_planet(
            has_facilities=False, has_population=False,
            _stockpile={"metals": 100.0},
        )
        item: dict = {"resources_consumed": {}}
        engine._apply_resource_consumption(
            _empire(), item, {"metals": 25.0}, planet,
        )

        assert planet.get_stockpile("metals") == 75.0
        assert item["resources_consumed"]["metals"] == 25.0


class TestFleetFractionalCostQueueLoopStallContract:
    """PROJ-436 Phase 12 Codex consult Risk #3: pin the full
    `_process_queue_tick_dynamic` UX for fractional fleet costs.

    When the per-step cost rounds to zero on Fleet's integer cargo,
    the queue must **stall** — `resources_consumed` must not advance,
    cargo must not decrement, and the item must remain in the queue —
    rather than silently progressing. The engine-call-level tests
    above prove the truth-up in isolation; this test exercises the
    behavior through the actual queue tick loop.
    """

    def test_fractional_per_step_cost_against_int_cargo_does_not_advance_resources_consumed(
        self, engine,
    ):
        from unittest.mock import MagicMock

        fleet: Fleet = create_test_fleet(num_ships=1)
        fleet.ships[0]._cargo_mgr.set_cargo("metals", 1)
        assert fleet.get_cargo_resource("metals") == 1.0

        # A fractional per-step rate that rounds to 0 every tick:
        # rate_per_turn = 10 → rate_per_tick = 10 / 100 = 0.1, but
        # cargo is integer-typed so int(round(0.1)) = 0 per call.
        item = {
            "design_id": "fractional-ship",
            "type": "ship",
            "total_cost": {"metals": 100.0},
            "resources_consumed": {"metals": 0.0},
        }
        queue = [item]
        rates = {"metals": 10.0}  # 10 / 100 ticks = 0.1 per tick

        engine._process_queue_tick_dynamic(
            queue, _empire(), 1, MagicMock(),
            rates, fleet, is_complex_only=False,
        )

        # PROJ-436 Phase 12 contract: queue stalls, cargo unchanged,
        # resources_consumed does not advance (because the engine
        # records the actual diff, which is 0).
        assert fleet.get_cargo_resource("metals") == 1.0
        assert item["resources_consumed"]["metals"] == 0.0
        assert len(queue) == 1  # item still in queue, not completed


class TestFractionalCostRoundedToZeroEmitsResourceShortage:
    """PROJ-451 Phase 1 RED: DI-2026-05-18-006 engine-side UX gap.

    When Fleet construction has a fractional per-step cost that rounds
    to 0 against the integer cargo store, the affordability check
    passes vacuously (``Fleet.has_cargo_resources`` rounds the request
    to ``int(round(0.1)) == 0`` and ``cargo >= 0``), the engine
    records ``actually_consumed == 0`` per Phase 12 truth-up, and the
    queue stalls. The player should see a clear shortage signal
    (RESOURCE_SHORTAGE event); pre-fix, no event is emitted.

    Pinning the post-fix contract: when ``_apply_resource_consumption``
    sees ``amount > 0`` requested but ``actually_consumed == 0``, the
    engine must route to the shortage-emit path.
    """

    @pytest.mark.xfail(
        reason="PROJ-451 Phase 1 RED — fixed by Phase 2 (RESOURCE_SHORTAGE emit on zero-consume).",
        strict=True,
    )
    def test_engine_level_zero_consume_emits_resource_shortage(self, engine):
        fleet: Fleet = create_test_fleet(num_ships=1)
        fleet.ships[0]._cargo_mgr.set_cargo("metals", 1)

        item: dict = {
            "design_id": "fractional-ship",
            "type": "ship",
            "resources_consumed": {"metals": 0.0},
        }

        engine._apply_resource_consumption(
            _empire(), item, {"metals": 0.1}, fleet,
        )

        # Currently FAILS: no shortage event is logged in
        # ``_apply_resource_consumption`` when actually_consumed == 0
        # despite the requested ``amount > 0``.
        assert any(
            call.args and call.args[0] == EventType.RESOURCE_SHORTAGE
            for call in engine._event_bus.log_event.call_args_list
        ), (
            "engine._event_bus.log_event(RESOURCE_SHORTAGE, ...) was not invoked; "
            "the rounded-to-zero fleet build stall must emit a shortage event."
        )


class TestQueueLoopRoundedToZeroEmitsResourceShortage:
    """PROJ-451 Phase 1 RED: same UX gap, exercised through
    ``_process_queue_tick_dynamic`` rather than the engine-call-level
    primitive. The queue stalls AND a shortage event must surface.
    """

    @pytest.mark.xfail(
        reason="PROJ-451 Phase 1 RED — fixed by Phase 2 (RESOURCE_SHORTAGE emit on zero-consume).",
        strict=True,
    )
    def test_fractional_per_step_cost_against_int_cargo_emits_resource_shortage(
        self, engine,
    ):
        fleet: Fleet = create_test_fleet(num_ships=1)
        fleet.ships[0]._cargo_mgr.set_cargo("metals", 1)

        item = {
            "design_id": "fractional-ship",
            "type": "ship",
            "total_cost": {"metals": 100.0},
            "resources_consumed": {"metals": 0.0},
        }
        queue = [item]
        rates = {"metals": 10.0}  # 10 / 100 ticks = 0.1 per tick

        engine._process_queue_tick_dynamic(
            queue, _empire(), 1, MagicMock(),
            rates, fleet, is_complex_only=False,
        )

        assert any(
            call.args and call.args[0] == EventType.RESOURCE_SHORTAGE
            for call in engine._event_bus.log_event.call_args_list
        ), (
            "RESOURCE_SHORTAGE event missing after rounded-to-zero per-step "
            "cost stall; player has no shortage indicator."
        )
