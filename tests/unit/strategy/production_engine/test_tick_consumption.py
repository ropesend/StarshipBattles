"""Tests for per-tick resource consumption in production.

PROJ-75 Phase 4: Production resource consumption.
PROJ-79 Phase 2: Tick-based completion (mid-turn spawning).

Task 4.5: Per-tick consumption tests.
"""
import pytest
from unittest.mock import MagicMock, patch

from game.strategy.data.empire import Empire
from game.strategy.data.fleet import Fleet
from game.strategy.data.planet import PlanetaryFacility
from game.strategy.engine.production_engine import ProductionEngine


def _make_empire(resources: dict = None) -> Empire:
    """Create a real Empire with optional starting resources."""
    empire = Empire(empire_id=0, name="Test Empire", color=(255, 0, 0))
    if resources:
        for res, amount in resources.items():
            empire.resource_pool[res] = amount
    return empire


def _make_colony(construction_queue=None, facilities=None):
    """Create a mock colony."""
    colony = MagicMock()
    colony.name = "Test Colony"
    colony.construction_queue = construction_queue or []
    colony.facilities = facilities or []
    return colony


def _make_shipyard(construction_queue=None) -> PlanetaryFacility:
    """Create a shipyard facility with optional queue."""
    yard = PlanetaryFacility(
        instance_id="yard_1",
        design_id="shipyard_complex",
        name="Space Shipyard",
        design_data={
            "layers": {
                "CORE": [{"id": "space_shipyard", "abilities": {"SpaceShipyard": {"value": 1}}}]
            }
        },
        is_operational=True,
    )
    yard.construction_queue = construction_queue or []
    return yard


def _make_queue_item(
    design_id="Scout",
    vehicle_type="ship",
    turns_remaining=5,
    total_cost=None,
    resources_consumed=None,
) -> dict:
    """Create a queue item with cost tracking fields.

    NOTE: The dynamic production system (PROJ-79) uses production_rates.json to
    determine consumption rates, NOT item-level cost_per_tick. Queue items track:
    - total_cost: Full cost to complete
    - resources_consumed: Progress so far

    Dead fields (no longer used by dynamic system):
    - cost_per_tick: Dynamic system calculates from production_rates.json
    - ticks_in_current_turn: Dynamic system tracks via resources_consumed
    """
    # Use explicit None check so empty dict {} is preserved
    total = total_cost if total_cost is not None else {"Metals": 500}
    return {
        "design_id": design_id,
        "type": vehicle_type,
        "turns_remaining": turns_remaining,
        "total_cost": total,
        "resources_consumed": resources_consumed if resources_consumed is not None else {res: 0.0 for res in total},
    }


class TestTickConsumption:
    """Tests for process_construction_tick method.

    NOTE: PROJ-79 changed base queue to only process complexes. Tests using
    base queue now use vehicle_type="complex". Ship tests use facility queues.
    """

    def test_successful_tick_deducts_from_empire(self):
        """Each tick deducts resources based on production_rates.json rates.

        Planetary yard rate = 2000/turn = 20/tick per resource.
        Item with total_cost=500 Metals, remaining=500, rate=20/tick:
        -> 1 tick consumes 20 Metals.
        """
        engine = ProductionEngine()
        empire = _make_empire({"Metals": 1000.0})
        item = _make_queue_item(
            vehicle_type="complex",  # Base queue only processes complexes
            turns_remaining=5,
            total_cost={"Metals": 500},
        )
        colony = _make_colony(construction_queue=[item])
        colony.facilities = []
        colony.resource_qualities = {}
        colony.id = 1
        empire.id = 0
        empire.colonies = [colony]

        engine.process_construction_tick(1, [empire], None)

        # Planetary yard rate = 2000/turn = 20/tick
        assert empire.resource_pool["Metals"] == pytest.approx(980.0)

    def test_resources_consumed_incremented(self):
        """resources_consumed tracks cumulative consumption per tick.

        Planetary yard rate = 2000/turn = 20/tick per resource.
        After 2 ticks: 2 * 20 = 40 Metals consumed.
        """
        engine = ProductionEngine()
        empire = _make_empire({"Metals": 1000.0})
        item = _make_queue_item(
            vehicle_type="complex",
            turns_remaining=5,
            total_cost={"Metals": 500},
        )
        colony = _make_colony(construction_queue=[item])
        colony.facilities = []
        colony.resource_qualities = {}
        colony.id = 1
        empire.id = 0
        empire.colonies = [colony]

        engine.process_construction_tick(1, [empire], None)
        engine.process_construction_tick(2, [empire], None)

        # 2 ticks * 20/tick = 40 Metals consumed
        assert item["resources_consumed"]["Metals"] == pytest.approx(40.0)

    def test_pause_on_insufficient_resources(self):
        """When empire lacks resources, no consumption occurs."""
        engine = ProductionEngine()
        empire = _make_empire({"Metals": 0.0})
        item = _make_queue_item(
            vehicle_type="complex",
            turns_remaining=5,
            total_cost={"Metals": 500},
        )
        colony = _make_colony(construction_queue=[item])
        colony.facilities = []
        colony.resource_qualities = {}
        colony.id = 1
        empire.id = 0
        empire.colonies = [colony]

        engine.process_construction_tick(1, [empire], None)

        assert empire.resource_pool["Metals"] == 0.0
        assert item["resources_consumed"]["Metals"] == 0.0

    def test_resume_after_resources_available(self):
        """Production resumes when resources become available again.

        Planetary yard rate = 2000/turn = 20/tick.
        After adding 100 Metals and processing 1 tick: 100 - 20 = 80 remaining.
        """
        engine = ProductionEngine()
        empire = _make_empire({"Metals": 0.0})
        item = _make_queue_item(
            vehicle_type="complex",
            turns_remaining=5,
            total_cost={"Metals": 500},
        )
        colony = _make_colony(construction_queue=[item])
        colony.facilities = []
        colony.resource_qualities = {}
        colony.id = 1
        empire.id = 0
        empire.colonies = [colony]

        # Tick 1: paused - no resources
        engine.process_construction_tick(1, [empire], None)
        assert item["resources_consumed"]["Metals"] == 0.0

        # Add resources
        empire.resource_pool["Metals"] = 100.0

        # Tick 2: resumes - consumes 20 Metals at planetary_yard rate
        engine.process_construction_tick(2, [empire], None)
        assert item["resources_consumed"]["Metals"] == pytest.approx(20.0)
        assert empire.resource_pool["Metals"] == pytest.approx(80.0)

    def test_item_remains_when_resources_consumed_below_total(self):
        """Item stays in queue when resources_consumed < total_cost.

        Planetary yard rate = 2000/turn = 20/tick.
        Item with total_cost=1000 Metals, rate=20/tick needs 50 ticks.
        After 1 tick: 20 consumed, 980 remaining -> item stays in queue.
        """
        engine = ProductionEngine()
        empire = _make_empire({"Metals": 10000.0})
        item = _make_queue_item(
            vehicle_type="complex",
            turns_remaining=5,
            total_cost={"Metals": 1000},  # Needs 50 ticks at 20/tick
        )
        colony = _make_colony(construction_queue=[item])
        colony.facilities = []
        colony.resource_qualities = {}
        colony.id = 1
        empire.id = 0
        empire.colonies = [colony]

        engine.process_construction_tick(1, [empire], None)

        # Item still in queue with partial progress
        assert len(colony.construction_queue) == 1
        assert item["resources_consumed"]["Metals"] == pytest.approx(20.0)

    def test_multiple_queue_items_only_first_processes(self):
        """Only the first queue item consumes resources each tick.

        Planetary yard rate = 2000/turn = 20/tick.
        After 1 tick: item1 consumes 20, item2 consumes 0.
        """
        engine = ProductionEngine()
        empire = _make_empire({"Metals": 1000.0})
        item1 = _make_queue_item(
            design_id="Factory1",
            vehicle_type="complex",
            turns_remaining=5,
            total_cost={"Metals": 500},
        )
        item2 = _make_queue_item(
            design_id="Factory2",
            vehicle_type="complex",
            turns_remaining=10,
            total_cost={"Metals": 2000},
        )
        colony = _make_colony(construction_queue=[item1, item2])
        colony.facilities = []
        colony.resource_qualities = {}
        colony.id = 1
        empire.id = 0
        empire.colonies = [colony]

        engine.process_construction_tick(1, [empire], None)

        # Item1 consumed 20 Metals, item2 consumed nothing
        assert item1["resources_consumed"]["Metals"] == pytest.approx(20.0)
        assert item2["resources_consumed"]["Metals"] == 0.0
        assert empire.resource_pool["Metals"] == pytest.approx(980.0)

    def test_empty_queue_no_consumption(self):
        """Empty queue results in no resource consumption."""
        engine = ProductionEngine()
        empire = _make_empire({"Metals": 1000.0})
        colony = _make_colony(construction_queue=[])
        colony.facilities = []
        empire.colonies = [colony]

        engine.process_construction_tick(1, [empire], None)

        assert empire.resource_pool["Metals"] == 1000.0

    def test_facility_queue_tick_consumption(self):
        """Facility (shipyard) queues consume resources at shipyard rate.

        Space shipyard rate = 3000/turn = 30/tick per resource.
        After 1 tick: 30 Metals consumed.
        """
        engine = ProductionEngine()
        empire = _make_empire({"Metals": 1000.0})
        item = _make_queue_item(
            vehicle_type="ship",  # Facility queues can build ships
            turns_remaining=5,
            total_cost={"Metals": 500},
        )
        yard = _make_shipyard(construction_queue=[item])
        colony = _make_colony(construction_queue=[], facilities=[yard])
        colony.resource_qualities = {}
        colony.id = 1
        empire.id = 0
        empire.colonies = [colony]

        engine.process_construction_tick(1, [empire], None)

        # Shipyard rate = 3000/turn = 30/tick
        assert item["resources_consumed"]["Metals"] == pytest.approx(30.0)
        assert empire.resource_pool["Metals"] == pytest.approx(970.0)

    def test_multiple_resources_all_consumed(self):
        """All resources consumed at production rate per tick.

        Planetary yard rate = 2000/turn = 20/tick per resource.
        Each resource is consumed at its own rate, clamped to remaining cost.

        Item total_cost: Metals=500, Organics=250, Radioactives=100
        Rate = 20/tick for each resource type.

        Per tick consumption (capped by remaining cost):
        - Metals: min(20, 500) = 20/tick
        - Organics: min(20, 250) = 20/tick
        - Radioactives: min(20, 100) = 20/tick
        """
        engine = ProductionEngine()
        empire = _make_empire({"Metals": 1000.0, "Organics": 500.0, "Radioactives": 200.0})
        item = _make_queue_item(
            vehicle_type="complex",
            turns_remaining=5,
            total_cost={"Metals": 500, "Organics": 250, "Radioactives": 100},
        )
        colony = _make_colony(construction_queue=[item])
        colony.facilities = []
        colony.resource_qualities = {}
        colony.id = 1
        empire.id = 0
        empire.colonies = [colony]

        engine.process_construction_tick(1, [empire], None)

        # Each resource consumed at 20/tick rate
        assert empire.resource_pool["Metals"] == pytest.approx(980.0)  # 1000 - 20
        assert empire.resource_pool["Organics"] == pytest.approx(480.0)  # 500 - 20
        assert empire.resource_pool["Radioactives"] == pytest.approx(180.0)  # 200 - 20

    def test_partial_resource_pauses_all(self):
        """If any one resource is insufficient, the entire tick is paused."""
        engine = ProductionEngine()
        empire = _make_empire({"Metals": 1000.0, "Organics": 0.0})
        item = _make_queue_item(
            vehicle_type="complex",
            turns_remaining=5,
            total_cost={"Metals": 500, "Organics": 250},
        )
        colony = _make_colony(construction_queue=[item])
        colony.facilities = []
        colony.resource_qualities = {}
        colony.id = 1
        empire.id = 0
        empire.colonies = [colony]

        engine.process_construction_tick(1, [empire], None)

        # Nothing consumed since Organics is insufficient
        assert empire.resource_pool["Metals"] == 1000.0
        assert item["resources_consumed"]["Metals"] == 0.0

    def test_zero_cost_item_completes_immediately(self):
        """Items with no resource cost complete immediately (free construction)."""
        engine = ProductionEngine()
        empire = _make_empire({})
        item = _make_queue_item(
            design_id="FreeComplex",
            vehicle_type="complex",
            turns_remaining=5,
            total_cost={},
        )
        colony = _make_colony(construction_queue=[item])
        colony.facilities = []
        colony.resource_qualities = {}
        colony.id = 1
        empire.id = 0
        empire.colonies = [colony]

        with patch.object(engine, '_spawn_complex'):
            engine.process_construction_tick(1, [empire], None)

        # Zero cost = instant completion, item removed from queue
        assert len(colony.construction_queue) == 0

    def test_items_without_total_cost_skip_gracefully(self):
        """Items without total_cost field are handled gracefully.

        Note: Per CLAUDE.md, we do NOT support legacy items. However, the
        production engine should not crash on malformed items.
        """
        engine = ProductionEngine()
        empire = _make_empire({"Metals": 1000.0})
        # Malformed queue item without total_cost
        malformed_item = {
            "design_id": "Factory",
            "type": "complex",
            "turns_remaining": 5,
        }
        colony = _make_colony(construction_queue=[malformed_item])
        colony.facilities = []
        colony.resource_qualities = {}
        colony.id = 1
        empire.id = 0
        empire.colonies = [colony]

        # Should not crash
        engine.process_construction_tick(1, [empire], None)

        # No resources consumed since item lacks proper cost tracking
        assert empire.resource_pool["Metals"] == 1000.0


class TestMidTurnCompletion:
    """PROJ-79 Phase 2: Tests for mid-turn item completion."""

    def test_item_completes_when_all_resources_consumed(self):
        """Item pops from queue when resources_consumed >= total_cost.

        Planetary yard rate = 20/tick. Item needs 1 more Metals to complete.
        Any tick will consume >= 1 Metals (actually 20), completing the item.
        """
        engine = ProductionEngine()
        empire = _make_empire({"Metals": 1000.0})

        # Item almost complete - just needs 1 more Metal to finish
        item = _make_queue_item(
            design_id="Factory",
            vehicle_type="complex",
            turns_remaining=1,
            total_cost={"Metals": 100},
            resources_consumed={"Metals": 99.0},  # Need 1 more
        )
        colony = _make_colony(construction_queue=[item])
        colony.facilities = []
        colony.resource_qualities = {}
        colony.id = 1
        empire.id = 0
        empire.colonies = [colony]

        with patch.object(engine, '_spawn_complex') as mock_spawn:
            engine.process_construction_tick(100, [empire], None)

            # Item should be removed from queue
            assert len(colony.construction_queue) == 0
            # Spawn should be called
            mock_spawn.assert_called_once()

    def test_next_item_starts_after_completion(self):
        """After item completes mid-turn, next item gets queue position 0."""
        engine = ProductionEngine()
        empire = _make_empire({"Metals": 1000.0})

        item1 = _make_queue_item(
            design_id="Factory1",
            vehicle_type="complex",
            turns_remaining=1,
            total_cost={"Metals": 100},
            resources_consumed={"Metals": 99.0},  # Completes this tick
        )
        item2 = _make_queue_item(
            design_id="Factory2",
            vehicle_type="complex",
            turns_remaining=5,
            total_cost={"Metals": 500},
        )
        colony = _make_colony(construction_queue=[item1, item2])
        colony.facilities = []
        colony.resource_qualities = {}
        colony.id = 1
        empire.id = 0
        empire.colonies = [colony]

        with patch.object(engine, '_spawn_complex'):
            engine.process_construction_tick(100, [empire], None)

            # Item1 removed, Item2 now at position 0
            assert len(colony.construction_queue) == 1
            assert colony.construction_queue[0]["design_id"] == "Factory2"

    def test_fleet_tick_processing_added(self):
        """Fleet queues are processed in tick-based completion."""
        engine = ProductionEngine()
        empire = _make_empire({"Metals": 1000.0})
        empire.id = 0
        empire.colonies = []

        item = _make_queue_item(
            design_id="Scout",
            vehicle_type="ship",
            turns_remaining=1,
            total_cost={"Metals": 100},
            resources_consumed={"Metals": 99.0},  # Near-complete
        )

        fleet = MagicMock(spec=Fleet)
        fleet.is_building = True
        fleet.has_space_shipyard = True
        fleet.space_shipyard_count = 1  # Required for rate calculation
        fleet.construction_queue = [item]
        fleet.id = 1
        fleet.location = (10, 10)

        empire.fleets = [fleet]

        with patch.object(engine, '_spawn_fleet_ship') as mock_spawn:
            engine.process_construction_tick(100, [empire], None)

            # Should spawn ship
            mock_spawn.assert_called_once()
            # Queue should be empty
            assert len(fleet.construction_queue) == 0

    def test_fleet_complex_paused_when_not_at_planet(self):
        """Fleet building complex pauses tick processing when not at planet."""
        engine = ProductionEngine()
        empire = _make_empire({"Metals": 1000.0})
        empire.id = 0
        empire.colonies = []

        item = _make_queue_item(
            design_id="Factory",
            vehicle_type="complex",
            turns_remaining=1,
            total_cost={"Metals": 100},
        )

        fleet = MagicMock(spec=Fleet)
        fleet.is_building = True
        fleet.has_space_shipyard = True
        fleet.space_shipyard_count = 1
        fleet.construction_queue = [item]
        fleet.id = 1
        fleet.location = (10, 10)

        empire.fleets = [fleet]

        galaxy = MagicMock()
        galaxy.get_planets_at_global_hex.return_value = []  # No planets

        engine.process_construction_tick(1, [empire], galaxy)

        # No resources consumed - paused due to no planet
        assert empire.resource_pool["Metals"] == 1000.0
        assert item["resources_consumed"]["Metals"] == 0.0

    # PROJ-161: Removed test_mid_turn_complex_triggers_partial_harvest and
    # test_storage_recalculated_on_mid_turn_complex as _apply_partial_harvest
    # was deleted. Mid-turn facilities now participate in per-tick harvesting
    # automatically on subsequent ticks.

    def test_partial_resources_consumed_not_complete(self):
        """Item doesn't complete until ALL resources are consumed."""
        engine = ProductionEngine()
        empire = _make_empire({"Metals": 1000.0, "Organics": 1000.0})
        empire.id = 0

        # Metals complete but Organics not
        item = _make_queue_item(
            design_id="Factory",
            vehicle_type="complex",
            turns_remaining=1,
            total_cost={"Metals": 100, "Organics": 100},
            resources_consumed={"Metals": 100.0, "Organics": 50.0},  # Organics not done
        )

        colony = _make_colony(construction_queue=[item])
        colony.facilities = []
        colony.id = 1
        empire.colonies = [colony]

        with patch.object(engine, '_spawn_complex') as mock_spawn:
            engine.process_construction_tick(1, [empire], None)

            # Should NOT spawn - Organics not complete
            mock_spawn.assert_not_called()
            assert len(colony.construction_queue) == 1
