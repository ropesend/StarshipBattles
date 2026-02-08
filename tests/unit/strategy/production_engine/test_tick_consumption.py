"""Tests for per-tick resource consumption in production.

PROJ-75 Phase 4: Production resource consumption.

Task 4.5: Per-tick consumption tests.
"""
import pytest
from unittest.mock import MagicMock

from game.strategy.data.empire import Empire
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
    cost_per_tick=None,
    resources_consumed=None,
    ticks_in_current_turn=0
) -> dict:
    """Create a queue item with cost tracking fields."""
    total = total_cost or {"Metals": 500}
    total_turns = turns_remaining + (ticks_in_current_turn > 0 and 0 or 0)  # noqa
    # Calculate cost_per_tick from total_cost and turns_remaining if not given
    if cost_per_tick is None:
        # For consistency: use turns_remaining * 100 as total ticks
        # Note: cost_per_tick is set at queue creation based on original turns
        total_ticks = turns_remaining * 100
        cpt = {}
        for res, amount in total.items():
            cpt[res] = amount / total_ticks if total_ticks > 0 else 0
        cost_per_tick = cpt
    return {
        "design_id": design_id,
        "type": vehicle_type,
        "turns_remaining": turns_remaining,
        "total_cost": total,
        "cost_per_tick": cost_per_tick,
        "resources_consumed": resources_consumed or {res: 0.0 for res in total},
        "ticks_in_current_turn": ticks_in_current_turn,
    }


class TestTickConsumption:
    """Tests for process_construction_tick method."""

    def test_successful_tick_deducts_from_empire(self):
        """Each tick deducts cost_per_tick from the empire resource pool."""
        engine = ProductionEngine()
        empire = _make_empire({"Metals": 1000.0})
        item = _make_queue_item(
            turns_remaining=5,
            total_cost={"Metals": 500},
            cost_per_tick={"Metals": 1.0},  # 500 / (5*100)
        )
        colony = _make_colony(construction_queue=[item])
        empire.colonies = [colony]

        engine.process_construction_tick(1, [empire], None)

        assert empire.resource_pool["Metals"] == pytest.approx(999.0)

    def test_resources_consumed_incremented(self):
        """resources_consumed tracks cumulative consumption per tick."""
        engine = ProductionEngine()
        empire = _make_empire({"Metals": 1000.0})
        item = _make_queue_item(
            turns_remaining=5,
            total_cost={"Metals": 500},
            cost_per_tick={"Metals": 1.0},
        )
        colony = _make_colony(construction_queue=[item])
        empire.colonies = [colony]

        engine.process_construction_tick(1, [empire], None)
        engine.process_construction_tick(2, [empire], None)

        assert item["resources_consumed"]["Metals"] == pytest.approx(2.0)

    def test_ticks_in_current_turn_incremented(self):
        """ticks_in_current_turn increments each successful tick."""
        engine = ProductionEngine()
        empire = _make_empire({"Metals": 1000.0})
        item = _make_queue_item(
            turns_remaining=5,
            total_cost={"Metals": 500},
            cost_per_tick={"Metals": 1.0},
        )
        colony = _make_colony(construction_queue=[item])
        empire.colonies = [colony]

        engine.process_construction_tick(1, [empire], None)

        assert item["ticks_in_current_turn"] == 1

    def test_pause_on_insufficient_resources(self):
        """When empire lacks resources, no consumption occurs and no tick increment."""
        engine = ProductionEngine()
        empire = _make_empire({"Metals": 0.0})
        item = _make_queue_item(
            turns_remaining=5,
            total_cost={"Metals": 500},
            cost_per_tick={"Metals": 1.0},
        )
        colony = _make_colony(construction_queue=[item])
        empire.colonies = [colony]

        engine.process_construction_tick(1, [empire], None)

        assert empire.resource_pool["Metals"] == 0.0
        assert item["ticks_in_current_turn"] == 0
        assert item["resources_consumed"]["Metals"] == 0.0

    def test_resume_after_resources_available(self):
        """Production resumes when resources become available again."""
        engine = ProductionEngine()
        empire = _make_empire({"Metals": 0.0})
        item = _make_queue_item(
            turns_remaining=5,
            total_cost={"Metals": 500},
            cost_per_tick={"Metals": 1.0},
        )
        colony = _make_colony(construction_queue=[item])
        empire.colonies = [colony]

        # Tick 1: paused - no resources
        engine.process_construction_tick(1, [empire], None)
        assert item["ticks_in_current_turn"] == 0

        # Add resources
        empire.resource_pool["Metals"] = 100.0

        # Tick 2: resumes
        engine.process_construction_tick(2, [empire], None)
        assert item["ticks_in_current_turn"] == 1
        assert empire.resource_pool["Metals"] == pytest.approx(99.0)

    def test_turn_decremented_after_100_ticks(self):
        """After 100 ticks, turns_remaining decrements and ticks reset."""
        engine = ProductionEngine()
        empire = _make_empire({"Metals": 10000.0})
        item = _make_queue_item(
            turns_remaining=2,
            total_cost={"Metals": 200},
            cost_per_tick={"Metals": 1.0},
            ticks_in_current_turn=99,
        )
        colony = _make_colony(construction_queue=[item])
        empire.colonies = [colony]

        engine.process_construction_tick(1, [empire], None)

        assert item["turns_remaining"] == 1
        assert item["ticks_in_current_turn"] == 0

    def test_item_remains_when_turns_remaining_above_zero(self):
        """Item stays in queue when turns_remaining > 0 after turn boundary."""
        engine = ProductionEngine()
        empire = _make_empire({"Metals": 10000.0})
        item = _make_queue_item(
            turns_remaining=2,
            total_cost={"Metals": 200},
            cost_per_tick={"Metals": 1.0},
            ticks_in_current_turn=99,
        )
        colony = _make_colony(construction_queue=[item])
        empire.colonies = [colony]

        engine.process_construction_tick(1, [empire], None)

        assert len(colony.construction_queue) == 1
        assert colony.construction_queue[0]["turns_remaining"] == 1

    def test_multiple_queue_items_only_first_processes(self):
        """Only the first queue item consumes resources each tick."""
        engine = ProductionEngine()
        empire = _make_empire({"Metals": 1000.0})
        item1 = _make_queue_item(
            design_id="Scout",
            turns_remaining=5,
            total_cost={"Metals": 500},
            cost_per_tick={"Metals": 1.0},
        )
        item2 = _make_queue_item(
            design_id="Cruiser",
            turns_remaining=10,
            total_cost={"Metals": 2000},
            cost_per_tick={"Metals": 2.0},
        )
        colony = _make_colony(construction_queue=[item1, item2])
        empire.colonies = [colony]

        engine.process_construction_tick(1, [empire], None)

        assert item1["ticks_in_current_turn"] == 1
        assert item2["ticks_in_current_turn"] == 0
        assert empire.resource_pool["Metals"] == pytest.approx(999.0)

    def test_empty_queue_no_consumption(self):
        """Empty queue results in no resource consumption."""
        engine = ProductionEngine()
        empire = _make_empire({"Metals": 1000.0})
        colony = _make_colony(construction_queue=[])
        empire.colonies = [colony]

        engine.process_construction_tick(1, [empire], None)

        assert empire.resource_pool["Metals"] == 1000.0

    def test_facility_queue_tick_consumption(self):
        """Facility (shipyard) queues also consume resources per tick."""
        engine = ProductionEngine()
        empire = _make_empire({"Metals": 1000.0})
        item = _make_queue_item(
            turns_remaining=5,
            total_cost={"Metals": 500},
            cost_per_tick={"Metals": 1.0},
        )
        yard = _make_shipyard(construction_queue=[item])
        colony = _make_colony(construction_queue=[], facilities=[yard])
        empire.colonies = [colony]

        engine.process_construction_tick(1, [empire], None)

        assert item["ticks_in_current_turn"] == 1
        assert empire.resource_pool["Metals"] == pytest.approx(999.0)

    def test_multiple_resources_all_consumed(self):
        """All resource types in cost_per_tick are consumed per tick."""
        engine = ProductionEngine()
        empire = _make_empire({"Metals": 1000.0, "Organics": 500.0, "Radioactives": 200.0})
        item = _make_queue_item(
            turns_remaining=5,
            total_cost={"Metals": 500, "Organics": 250, "Radioactives": 100},
            cost_per_tick={"Metals": 1.0, "Organics": 0.5, "Radioactives": 0.2},
        )
        colony = _make_colony(construction_queue=[item])
        empire.colonies = [colony]

        engine.process_construction_tick(1, [empire], None)

        assert empire.resource_pool["Metals"] == pytest.approx(999.0)
        assert empire.resource_pool["Organics"] == pytest.approx(499.5)
        assert empire.resource_pool["Radioactives"] == pytest.approx(199.8)

    def test_partial_resource_pauses_all(self):
        """If any one resource is insufficient, the entire tick is paused."""
        engine = ProductionEngine()
        empire = _make_empire({"Metals": 1000.0, "Organics": 0.0})
        item = _make_queue_item(
            turns_remaining=5,
            total_cost={"Metals": 500, "Organics": 250},
            cost_per_tick={"Metals": 1.0, "Organics": 0.5},
        )
        colony = _make_colony(construction_queue=[item])
        empire.colonies = [colony]

        engine.process_construction_tick(1, [empire], None)

        # Nothing consumed since Organics is insufficient
        assert empire.resource_pool["Metals"] == 1000.0
        assert item["ticks_in_current_turn"] == 0

    def test_zero_cost_item_processes_normally(self):
        """Items with no resource cost still tick (free construction)."""
        engine = ProductionEngine()
        empire = _make_empire({})
        item = _make_queue_item(
            turns_remaining=5,
            total_cost={},
            cost_per_tick={},
        )
        colony = _make_colony(construction_queue=[item])
        empire.colonies = [colony]

        engine.process_construction_tick(1, [empire], None)

        assert item["ticks_in_current_turn"] == 1

    def test_items_without_cost_fields_skip_gracefully(self):
        """Legacy items without cost tracking fields are skipped by tick processing."""
        engine = ProductionEngine()
        empire = _make_empire({"Metals": 1000.0})
        # Legacy queue item without cost fields
        legacy_item = {
            "design_id": "Scout",
            "type": "ship",
            "turns_remaining": 5,
        }
        colony = _make_colony(construction_queue=[legacy_item])
        empire.colonies = [colony]

        # Should not crash - just skip
        engine.process_construction_tick(1, [empire], None)

        # Legacy item should not have ticks_in_current_turn modified
        assert "ticks_in_current_turn" not in legacy_item or legacy_item.get("ticks_in_current_turn", 0) == 0
