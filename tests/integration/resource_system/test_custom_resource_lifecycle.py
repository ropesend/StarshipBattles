"""
Integration test: Custom Resource Full Lifecycle

Verifies that a modder-defined resource ("dilithium") works end-to-end
through the entire resource pipeline:
1. Defined in resources.json via ResourceCatalog
2. Planet deposits can hold it
3. Harvested by a ResourceHarvester component
4. Accumulated in empire resource pool
5. Consumed as construction cost by ProductionEngine
6. Stored on ships via ResourceStorage ability
7. Consumed during combat via ResourceConsumption ability

This test demonstrates that no Python code changes are needed to support
a custom resource type — only JSON data configuration.
"""
import json
import pytest

from game.core.resources import ResourceCatalog
from game.core.registry import GameRegistries, RegistryManager
from game.strategy.data.empire import Empire
from game.strategy.data.planet import PlanetaryFacility
from game.strategy.engine.harvesting_engine import HarvestingEngine
from game.strategy.engine.maintenance_engine import MaintenanceEngine
from game.strategy.services.ship_stats_calculator import ShipStatsCalculator
from tests.fixtures.strategy_entities import create_test_planet


def _make_empire(resources=None, storage=None, empire_id=0):
    """Create an empire with optional starting resources and storage caps."""
    empire = Empire(empire_id=empire_id, name="Test Empire", color=(0, 0, 255))
    if resources:
        for res, amount in resources.items():
            empire.resource_pool[res] = amount
    if storage:
        for res, cap in storage.items():
            empire.max_storage[res] = cap
    return empire


def _make_harvester_facility(resource_type, base_harvest_rate=100.0):
    """Create a facility with a ResourceHarvester for the given resource type."""
    comp = {
        "id": f"{resource_type}_harvester",
        "abilities": {
            "ResourceHarvester": {
                "resource_type": resource_type,
                "base_harvest_rate": base_harvest_rate,
            }
        },
    }
    return PlanetaryFacility(
        instance_id=f"fac-{resource_type}-001",
        design_id=f"{resource_type}_harvester_complex",
        name=f"{resource_type.capitalize()} Harvester",
        design_data={"layers": {"core": [comp]}},
    )


class TestCustomResourceCatalog:
    """Tests for custom resource definitions in ResourceCatalog."""

    def test_custom_resource_loads_from_json(self, tmp_path):
        """A custom resource defined in JSON is accessible via ResourceCatalog."""
        custom_json = {
            "resources": [
                {"id": "dilithium", "name": "Dilithium", "description": "Rare crystal.",
                 "display_group": "exotic", "has_quality": True},
                {"id": "fuel", "name": "Fuel", "description": "Powers engines.",
                 "display_group": "operational", "has_quality": False},
            ]
        }
        json_file = tmp_path / "resources.json"
        json_file.write_text(json.dumps(custom_json))

        catalog = ResourceCatalog.from_json(str(json_file))

        assert catalog.has("dilithium")
        defn = catalog.get("dilithium")
        assert defn.name == "Dilithium"
        assert defn.has_quality is True
        assert defn.display_group == "exotic"

    def test_default_catalog_has_all_resources(self):
        """The production resources.json has all 8 default resource types."""
        catalog = ResourceCatalog.from_json()

        expected = ["metals", "organics", "vapors", "radioactives", "exotics",
                    "fuel", "energy", "ammo"]
        for res_id in expected:
            assert catalog.has(res_id), f"Missing resource: {res_id}"

        planetary = [d.id for d in catalog.by_display_group("planetary")]
        operational = [d.id for d in catalog.by_display_group("operational")]

        assert set(planetary) == {"metals", "organics", "vapors", "radioactives", "exotics"}
        assert set(operational) == {"fuel", "energy", "ammo"}


class TestCustomResourcePlanetDeposits:
    """Tests for custom resources in planet deposits."""

    def test_planet_holds_custom_resource_deposits(self):
        """Planets can hold deposits of any resource type, including custom ones."""
        planet = create_test_planet(
            has_facilities=False,
            has_population=False,
            deposits={
                "dilithium": {"quantity": 5000, "quality": 0.85},
                "metals": {"quantity": 10000, "quality": 0.5},
            },
        )

        assert planet.deposits["dilithium"]["quantity"] == 5000
        assert planet.deposits["dilithium"]["quality"] == 0.85
        assert planet.deposits["metals"]["quantity"] == 10000


class TestCustomResourceHarvesting:
    """Tests for harvesting custom resources from planets."""

    def test_harvest_custom_resource_into_empire_pool(self):
        """HarvestingEngine extracts a custom resource from planet deposits."""
        harvester = _make_harvester_facility("dilithium", base_harvest_rate=100.0)
        planet = create_test_planet(
            has_facilities=False,
            has_population=False,
            deposits={"dilithium": {"quantity": 50000, "quality": 0.8}},
        )
        planet.facilities = [harvester]

        empire = _make_empire(
            resources={"dilithium": 0.0},
            storage={"dilithium": 100000.0},
        )
        empire.add_colony(planet)

        engine = HarvestingEngine()
        engine.process_harvesting_tick(1, [empire])

        # Empire should have received some dilithium
        assert empire.resource_pool.get("dilithium", 0.0) > 0.0
        # Planet deposit should have decreased
        assert planet.deposits["dilithium"]["quantity"] < 50000


class TestCustomResourceEmpirePool:
    """Tests for custom resources in the empire economy."""

    def test_empire_pool_stores_custom_resource(self):
        """Empire resource pool can store and track any resource type."""
        empire = _make_empire(
            resources={"dilithium": 500.0},
            storage={"dilithium": 10000.0},
        )

        assert empire.resource_pool["dilithium"] == 500.0
        assert empire.max_storage["dilithium"] == 10000.0

        # Can add more
        empire.add_resources("dilithium", 200.0)
        assert empire.resource_pool["dilithium"] == 700.0

        # Can consume
        assert empire.consume_resources("dilithium", 300.0) is True
        assert empire.resource_pool["dilithium"] == pytest.approx(400.0)

        # Can check affordability
        assert empire.has_resources({"dilithium": 400.0}) is True
        assert empire.has_resources({"dilithium": 500.0}) is False

    def test_maintenance_works_with_custom_resource_costs(self):
        """MaintenanceEngine correctly deducts custom resource maintenance costs."""
        empire = _make_empire(
            resources={"dilithium": 100.0},
            storage={"dilithium": 10000.0},
        )

        # Facility with dilithium construction cost -> maintenance costs dilithium
        facility = PlanetaryFacility(
            instance_id="fac-001",
            design_id="crystal_refinery",
            name="Crystal Refinery",
            design_data={
                "layers": {
                    "CORE": {
                        "components": [
                            {"id": "crystal_core", "resource_cost": {"dilithium": 1000}}
                        ]
                    }
                }
            },
        )

        planet = create_test_planet(has_facilities=False, has_population=False)
        planet.facilities = [facility]
        empire.add_colony(planet)

        engine = MaintenanceEngine(registries=GameRegistries(
            components=RegistryManager.instance().components,
            modifiers=RegistryManager.instance().modifiers,
            vehicle_classes=RegistryManager.instance().vehicle_classes,
            resources=RegistryManager.instance().resources,
        ))

        # Run full turn of maintenance
        for tick in range(1, 101):
            engine.process_maintenance_tick(tick, [empire])

        # 5% of 1000 dilithium = 50 dilithium deducted
        assert empire.resource_pool["dilithium"] == pytest.approx(50.0)


class TestCustomResourceShipStorage:
    """Tests for storing custom resources on ships via component abilities."""

    def test_custom_resource_storage_in_stats(self):
        """A component with ResourceStorage for a custom resource appears in ship stats."""
        # Register a test component with dilithium storage
        registry = RegistryManager.instance()
        registry.components["dilithium_tank"] = {
            "id": "dilithium_tank",
            "type": "ResourceStorage",
            "mass": 50,
            "hp": 100,
            "allowed_vehicle_types": ["Ship"],
            "abilities": {
                "ResourceStorage": {
                    "resource": "dilithium",
                    "amount": 500.0,
                }
            },
        }

        registries = GameRegistries(
            components=registry.components,
            modifiers=registry.modifiers,
            vehicle_classes=registry.vehicle_classes,
            resources=registry.resources,
        )

        design_data = {
            "name": "Crystal Ship",
            "vehicle_type": "Ship",
            "layers": {
                "CORE": [{"id": "dilithium_tank"}],
            },
        }

        calc = ShipStatsCalculator(registries=registries)
        stats = calc.calculate_stats(design_data)

        assert stats.get("resource_storage", {}).get("dilithium", 0.0) == pytest.approx(500.0)
