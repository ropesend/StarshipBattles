"""
Tests for HarvestingEngine - planetary resource harvesting to colony stockpile.

PROJ-75 Phase 2: TDD tests for HarvestingEngine.
PROJ-161: Now per-tick only via process_harvesting_tick().
PROJ-191 Phase 3: Updated mocks to use spec= for type safety.
PROJ-XXX: Updated for local stockpile system — harvest deposits into
colony.stockpile instead of empire.resource_pool.

Covers single/multiple harvesters, planet depletion, storage overflow,
non-operational facilities, empty colonies, quality-scaled extraction,
and per-tick (1/100th) harvesting.
"""
import pytest
from unittest.mock import MagicMock

from game.strategy.data.empire import Empire
from game.strategy.data.planet import Planet, PlanetaryFacility


# ===========================================================================
# Fixtures / Helpers
# ===========================================================================

def _make_empire(colonies=None, resource_pool=None, max_storage=None):
    """Create a mock empire with colonies and resource pool."""
    empire = MagicMock(spec=Empire)
    empire.colonies = colonies or []
    empire.resource_pool = resource_pool or {}
    empire.max_storage = max_storage or {}

    # Wire add_resources to behave like the real Empire
    def add_resources(resource_type, amount):
        current = empire.resource_pool.get(resource_type, 0.0)
        max_cap = empire.max_storage.get(resource_type, float('inf'))
        new_total = current + amount
        if new_total > max_cap:
            empire.resource_pool[resource_type] = max_cap
            return new_total - max_cap
        empire.resource_pool[resource_type] = new_total
        return 0.0

    empire.add_resources = add_resources
    return empire


def _make_planet(resources=None, facilities=None, name="Test Planet",
                  stockpile=None, max_stockpile=None):
    """Create a minimal Planet-like object for harvesting tests.

    Includes stockpile and add_to_stockpile() to support local stockpile
    harvesting (resources deposited to colony, not empire).
    """
    planet = MagicMock(spec=Planet)
    planet.name = name
    planet.deposits = resources or {}
    planet.facilities = facilities or []
    planet.stockpile = stockpile or {}
    planet.max_stockpile = max_stockpile or {}

    # Wire add_to_stockpile to mirror real Planet behavior
    def add_to_stockpile(resource_type, amount):
        current = planet.stockpile.get(resource_type, 0.0)
        max_cap = planet.max_stockpile.get(resource_type, float('inf'))
        new_total = current + amount
        if new_total > max_cap:
            planet.stockpile[resource_type] = max_cap
            return new_total - max_cap
        planet.stockpile[resource_type] = new_total
        return 0.0

    planet.add_to_stockpile = add_to_stockpile
    return planet


def _make_harvester_facility(
    resource_type="metals",
    base_harvest_rate=100.0,
    instance_id="harv-001",
    is_operational=True,
):
    """Create a facility with a ResourceHarvester ability in design_data."""
    facility = PlanetaryFacility(
        instance_id=instance_id,
        design_id="metals_harvester_complex",
        name=f"{resource_type} Harvester Complex",
        design_data={
            "layers": {
                "core": [
                    {
                        "id": "metals_harvester",
                        "abilities": {
                            "ResourceHarvester": {
                                "resource_type": resource_type,
                                "base_harvest_rate": base_harvest_rate,
                            }
                        },
                    }
                ]
            }
        },
        is_operational=is_operational,
    )
    return facility


def _make_mock_registries(harvesters=None):
    """Create mock registries with harvester component definitions.

    Args:
        harvesters: Dict mapping component_id -> dict with resource_type and base_harvest_rate.
                   Defaults to a metals_harvester with rate 100.
    """
    if harvesters is None:
        harvesters = {
            "metals_harvester": {"resource_type": "metals", "base_harvest_rate": 100.0},
        }

    registries = MagicMock()

    def get_component(comp_id):
        if comp_id in harvesters:
            comp = MagicMock()
            info = harvesters[comp_id]
            comp.abilities = {
                "ResourceHarvester": {
                    "resource_type": info["resource_type"],
                    "base_harvest_rate": info["base_harvest_rate"],
                }
            }
            return comp
        # Return a generic component with no harvester ability
        generic = MagicMock()
        generic.abilities = {}
        return generic

    registries.components.get = get_component
    return registries


# ===========================================================================
# Tests
# ===========================================================================


def _make_engine(registries=None):
    """Module-level helper. Promoted from per-class duplicates to dedupe."""
    from game.strategy.engine.harvesting_engine import HarvestingEngine
    return HarvestingEngine(registries=registries or _make_mock_registries())


class TestHarvestingEngine:
    """Tests for HarvestingEngine.process_harvesting_tick() - PROJ-161 per-tick only."""

    _make_engine = staticmethod(_make_engine)

    def _process_full_turn(self, engine, empires):
        """Helper to simulate full turn (100 ticks) of harvesting."""
        for tick in range(1, 101):
            engine.process_harvesting_tick(tick, empires)

    # --- Basic harvesting ---

    def test_single_facility_harvests_resources(self):
        """Single harvester extracts resources from planet to colony stockpile (full turn)."""
        facility = _make_harvester_facility("metals", base_harvest_rate=100.0)
        planet = _make_planet(
            resources={"metals": {"quantity": 5000, "quality": 0.8}},
            facilities=[facility],
        )
        empire = _make_empire(
            colonies=[planet],
            resource_pool={"metals": 0.0},
        )

        engine = self._make_engine()
        self._process_full_turn(engine, [empire])

        # harvest = base_rate * quality = 100 * 0.8 = 80
        assert planet.stockpile["metals"] == pytest.approx(80.0)
        assert planet.deposits["metals"]["quantity"] == pytest.approx(5000 - 80.0)

    def test_harvest_amount_scales_with_quality(self):
        """Harvest amount = base_rate * planet quality (full turn)."""
        facility = _make_harvester_facility("metals", base_harvest_rate=200.0)
        planet = _make_planet(
            resources={"metals": {"quantity": 10000, "quality": 0.5}},
            facilities=[facility],
        )
        empire = _make_empire(colonies=[planet], resource_pool={"metals": 0.0})

        engine = self._make_engine()
        self._process_full_turn(engine, [empire])

        # harvest = 200 * 0.5 = 100
        assert planet.stockpile["metals"] == pytest.approx(100.0)

    def test_planet_resource_quantity_reduced(self):
        """Planet's resource quantity decreases by harvest amount (full turn)."""
        facility = _make_harvester_facility("organics", base_harvest_rate=50.0)
        planet = _make_planet(
            resources={"organics": {"quantity": 1000, "quality": 1.0}},
            facilities=[facility],
        )
        empire = _make_empire(colonies=[planet], resource_pool={})

        engine = self._make_engine()
        self._process_full_turn(engine, [empire])

        assert planet.deposits["organics"]["quantity"] == pytest.approx(950.0)

    def test_colony_stockpile_increased_by_harvest(self):
        """Colony stockpile gains the harvested amount (full turn)."""
        facility = _make_harvester_facility("vapors", base_harvest_rate=75.0)
        planet = _make_planet(
            resources={"vapors": {"quantity": 3000, "quality": 0.6}},
            facilities=[facility],
            stockpile={"vapors": 100.0},
        )
        empire = _make_empire(
            colonies=[planet],
            resource_pool={"vapors": 100.0},
        )

        engine = self._make_engine()
        self._process_full_turn(engine, [empire])

        # harvest = 75 * 0.6 = 45. Stockpile: 100 + 45 = 145
        assert planet.stockpile["vapors"] == pytest.approx(145.0)

    # --- Multiple harvesters ---

    def test_multiple_harvesters_same_planet_sum(self):
        """Multiple harvesters on same planet accumulate correctly (full turn)."""
        f1 = _make_harvester_facility("metals", base_harvest_rate=100.0, instance_id="h1")
        f2 = _make_harvester_facility("metals", base_harvest_rate=50.0, instance_id="h2")
        planet = _make_planet(
            resources={"metals": {"quantity": 10000, "quality": 1.0}},
            facilities=[f1, f2],
        )
        empire = _make_empire(colonies=[planet], resource_pool={"metals": 0.0})

        engine = self._make_engine()
        self._process_full_turn(engine, [empire])

        # Total harvest = 100*1.0 + 50*1.0 = 150
        assert planet.stockpile["metals"] == pytest.approx(150.0)
        assert planet.deposits["metals"]["quantity"] == pytest.approx(10000 - 150.0)

    # --- Depletion ---

    def test_planet_depletion_no_negative(self):
        """Planet quantity cannot go negative; harvest capped at available (full turn)."""
        facility = _make_harvester_facility("exotics", base_harvest_rate=200.0)
        planet = _make_planet(
            resources={"exotics": {"quantity": 50, "quality": 1.0}},
            facilities=[facility],
        )
        empire = _make_empire(colonies=[planet], resource_pool={})

        engine = self._make_engine()
        self._process_full_turn(engine, [empire])

        # Wanted 200, only 50 available
        assert planet.deposits["exotics"]["quantity"] == pytest.approx(0.0)
        assert planet.stockpile["exotics"] == pytest.approx(50.0)

    def test_zero_quantity_no_harvest(self):
        """No resources extracted when planet quantity is 0."""
        facility = _make_harvester_facility("metals", base_harvest_rate=100.0)
        planet = _make_planet(
            resources={"metals": {"quantity": 0, "quality": 0.9}},
            facilities=[facility],
        )
        empire = _make_empire(colonies=[planet], resource_pool={"metals": 10.0})

        engine = self._make_engine()
        self._process_full_turn(engine, [empire])

        assert planet.stockpile.get("metals", 0.0) == pytest.approx(0.0)
        assert planet.deposits["metals"]["quantity"] == 0

    # --- Storage overflow ---

    def test_storage_overflow_discarded(self):
        """Excess resources beyond colony max_stockpile are discarded (full turn)."""
        harvester = _make_harvester_facility("metals", base_harvest_rate=100.0, instance_id="h1")
        # Storage facility provides the 1000 cap
        storage = PlanetaryFacility(
            instance_id="s1",
            design_id="metals_vault",
            name="Metals Vault",
            design_data={
                "layers": {
                    "core": [{
                        "id": "vault",
                        "abilities": {
                            "LocalStorage": {
                                "resource_type": "metals",
                                "capacity": 1000.0,
                            }
                        },
                    }]
                }
            },
        )
        planet = _make_planet(
            resources={"metals": {"quantity": 5000, "quality": 1.0}},
            facilities=[storage, harvester],
            stockpile={"metals": 950.0},
        )
        empire = _make_empire(
            colonies=[planet],
            resource_pool={"metals": 950.0},
            max_storage={"metals": 1000.0},
        )

        engine = self._make_engine()
        self._process_full_turn(engine, [empire])

        # Stockpile was 950, harvest 100, cap at 1000. 50 discarded.
        assert planet.stockpile["metals"] == pytest.approx(1000.0)
        # Planet still loses the full harvest amount
        assert planet.deposits["metals"]["quantity"] == pytest.approx(4900.0)

    # --- Non-operational / missing ability ---

    def test_non_operational_facility_skipped(self):
        """Non-operational facility does not harvest."""
        facility = _make_harvester_facility("metals", base_harvest_rate=100.0, is_operational=False)
        planet = _make_planet(
            resources={"metals": {"quantity": 5000, "quality": 1.0}},
            facilities=[facility],
        )
        empire = _make_empire(colonies=[planet], resource_pool={"metals": 0.0})

        engine = self._make_engine()
        self._process_full_turn(engine, [empire])

        assert planet.stockpile.get("metals", 0.0) == pytest.approx(0.0)
        assert planet.deposits["metals"]["quantity"] == pytest.approx(5000.0)

    def test_facility_without_harvester_skipped(self):
        """Facility without ResourceHarvester ability does nothing."""
        facility = PlanetaryFacility(
            instance_id="factory-001",
            design_id="shipyard_complex",
            name="Shipyard",
            design_data={
                "layers": {
                    "core": [
                        {"id": "space_shipyard", "abilities": {"SpaceShipyard": {}}}
                    ]
                }
            },
        )
        planet = _make_planet(
            resources={"metals": {"quantity": 5000, "quality": 1.0}},
            facilities=[facility],
        )
        empire = _make_empire(colonies=[planet], resource_pool={"metals": 0.0})

        engine = self._make_engine()
        self._process_full_turn(engine, [empire])

        assert planet.stockpile.get("metals", 0.0) == pytest.approx(0.0)

    # --- Edge cases ---

    def test_empty_colonies_list(self):
        """Empty colonies list handled gracefully."""
        empire = _make_empire(colonies=[], resource_pool={})

        engine = self._make_engine()
        engine.process_harvesting_tick(1, [empire])  # Should not raise

    def test_empty_empires_list(self):
        """Empty empires list handled gracefully."""
        engine = self._make_engine()
        engine.process_harvesting_tick(1, [])  # Should not raise

    def test_planet_missing_resource_type_for_harvester(self):
        """Harvester for a resource type not on the planet does nothing."""
        facility = _make_harvester_facility("exotics", base_harvest_rate=100.0)
        planet = _make_planet(
            resources={"metals": {"quantity": 5000, "quality": 1.0}},
            facilities=[facility],
        )
        empire = _make_empire(colonies=[planet], resource_pool={})

        engine = self._make_engine()
        self._process_full_turn(engine, [empire])

        assert planet.stockpile.get("exotics", 0.0) == 0.0
        assert planet.deposits["metals"]["quantity"] == pytest.approx(5000.0)

    def test_zero_quality_no_harvest(self):
        """Zero quality planet yields zero harvest."""
        facility = _make_harvester_facility("metals", base_harvest_rate=100.0)
        planet = _make_planet(
            resources={"metals": {"quantity": 5000, "quality": 0.0}},
            facilities=[facility],
        )
        empire = _make_empire(colonies=[planet], resource_pool={"metals": 0.0})

        engine = self._make_engine()
        self._process_full_turn(engine, [empire])

        assert planet.stockpile.get("metals", 0.0) == pytest.approx(0.0)
        assert planet.deposits["metals"]["quantity"] == pytest.approx(5000.0)

    def test_multiple_resource_types(self):
        """Multiple different resource types harvested in same pass (full turn)."""
        metals_fac = _make_harvester_facility("metals", base_harvest_rate=100.0, instance_id="m1")
        organics_fac = _make_harvester_facility("organics", base_harvest_rate=50.0, instance_id="o1")
        planet = _make_planet(
            resources={
                "metals": {"quantity": 5000, "quality": 0.8},
                "organics": {"quantity": 3000, "quality": 1.0},
            },
            facilities=[metals_fac, organics_fac],
        )
        empire = _make_empire(colonies=[planet], resource_pool={})

        engine = self._make_engine()
        self._process_full_turn(engine, [empire])

        assert planet.stockpile["metals"] == pytest.approx(80.0)  # 100*0.8
        assert planet.stockpile["organics"] == pytest.approx(50.0)  # 50*1.0

    def test_multiple_empires_independent(self):
        """Each empire's harvesting is independent (full turn)."""
        f1 = _make_harvester_facility("metals", base_harvest_rate=100.0, instance_id="h1")
        p1 = _make_planet(
            resources={"metals": {"quantity": 5000, "quality": 1.0}},
            facilities=[f1],
            name="Planet A",
        )
        e1 = _make_empire(colonies=[p1], resource_pool={"metals": 0.0})

        f2 = _make_harvester_facility("organics", base_harvest_rate=50.0, instance_id="h2")
        p2 = _make_planet(
            resources={"organics": {"quantity": 3000, "quality": 0.6}},
            facilities=[f2],
            name="Planet B",
        )
        e2 = _make_empire(colonies=[p2], resource_pool={"organics": 0.0})

        engine = self._make_engine()
        self._process_full_turn(engine, [e1, e2])

        assert p1.stockpile["metals"] == pytest.approx(100.0)
        assert p2.stockpile["organics"] == pytest.approx(30.0)  # 50*0.6

    def test_registry_based_harvester_lookup(self):
        """Engine uses registries to resolve component abilities when design_data has plain IDs."""
        # Facility with plain component ID strings (no inline abilities)
        facility = PlanetaryFacility(
            instance_id="reg-001",
            design_id="metals_harvester_complex",
            name="Metals Harvester",
            design_data={
                "layers": {
                    "core": ["metals_harvester"]
                }
            },
        )
        planet = _make_planet(
            resources={"metals": {"quantity": 5000, "quality": 0.5}},
            facilities=[facility],
        )
        empire = _make_empire(colonies=[planet], resource_pool={})

        regs = _make_mock_registries({
            "metals_harvester": {"resource_type": "metals", "base_harvest_rate": 200.0},
        })
        engine = self._make_engine(registries=regs)
        self._process_full_turn(engine, [empire])

        # harvest = 200 * 0.5 = 100
        assert planet.stockpile["metals"] == pytest.approx(100.0)


# ===========================================================================
# Storage Aggregation Tests
# ===========================================================================

def _make_storage_facility(
    resource_type="metals",
    capacity=10000.0,
    instance_id="store-001",
    is_operational=True,
):
    """Create a facility with an LocalStorage ability in design_data."""
    facility = PlanetaryFacility(
        instance_id=instance_id,
        design_id=f"{resource_type.lower()}_vault_complex",
        name=f"{resource_type} Vault",
        design_data={
            "layers": {
                "core": [
                    {
                        "id": f"resource_vault_{resource_type.lower()}",
                        "abilities": {
                            "LocalStorage": {
                                "resource_type": resource_type,
                                "capacity": capacity,
                            }
                        },
                    }
                ]
            }
        },
        is_operational=is_operational,
    )
    return facility


class TestStorageAggregation:
    """Tests for HarvestingEngine.recalculate_storage()."""

    _make_engine = staticmethod(_make_engine)

    def test_single_storage_facility(self):
        """Single storage facility sets colony max_stockpile and empire max_storage."""
        facility = _make_storage_facility("metals", capacity=10000.0)
        planet = _make_planet(facilities=[facility])
        empire = _make_empire(colonies=[planet])

        engine = self._make_engine()
        engine.recalculate_storage([empire])

        assert planet.max_stockpile["metals"] == pytest.approx(10000.0)
        assert empire.max_storage["metals"] == pytest.approx(10000.0)

    def test_multiple_storage_facilities_same_type(self):
        """Multiple facilities for same resource stack additively."""
        f1 = _make_storage_facility("metals", capacity=10000.0, instance_id="s1")
        f2 = _make_storage_facility("metals", capacity=5000.0, instance_id="s2")
        planet = _make_planet(facilities=[f1, f2])
        empire = _make_empire(colonies=[planet])

        engine = self._make_engine()
        engine.recalculate_storage([empire])

        assert planet.max_stockpile["metals"] == pytest.approx(15000.0)
        assert empire.max_storage["metals"] == pytest.approx(15000.0)

    def test_multiple_resource_types(self):
        """Storage for different resource types tracked independently."""
        f1 = _make_storage_facility("metals", capacity=10000.0, instance_id="s1")
        f2 = _make_storage_facility("organics", capacity=8000.0, instance_id="s2")
        f3 = _make_storage_facility("exotics", capacity=2500.0, instance_id="s3")
        planet = _make_planet(facilities=[f1, f2, f3])
        empire = _make_empire(colonies=[planet])

        engine = self._make_engine()
        engine.recalculate_storage([empire])

        assert empire.max_storage["metals"] == pytest.approx(10000.0)
        assert empire.max_storage["organics"] == pytest.approx(8000.0)
        assert empire.max_storage["exotics"] == pytest.approx(2500.0)

    def test_non_operational_facility_not_counted(self):
        """Non-operational storage facility does not contribute capacity."""
        f1 = _make_storage_facility("metals", capacity=10000.0, instance_id="s1")
        f2 = _make_storage_facility("metals", capacity=5000.0, instance_id="s2", is_operational=False)
        planet = _make_planet(facilities=[f1, f2])
        empire = _make_empire(colonies=[planet])

        engine = self._make_engine()
        engine.recalculate_storage([empire])

        assert planet.max_stockpile["metals"] == pytest.approx(10000.0)
        assert empire.max_storage["metals"] == pytest.approx(10000.0)

    def test_resets_max_storage_before_recalculating(self):
        """Recalculate resets max_stockpile/max_storage so removed facilities are not counted."""
        facility = _make_storage_facility("metals", capacity=10000.0)
        planet = _make_planet(
            facilities=[facility],
            max_stockpile={"metals": 99999.0, "organics": 50000.0},
        )
        empire = _make_empire(
            colonies=[planet],
            max_storage={"metals": 99999.0, "organics": 50000.0},
        )

        engine = self._make_engine()
        engine.recalculate_storage([empire])

        assert planet.max_stockpile["metals"] == pytest.approx(10000.0)
        assert planet.max_stockpile.get("organics", 0.0) == pytest.approx(0.0)
        assert empire.max_storage["metals"] == pytest.approx(10000.0)
        # Organics had no facility, so should not be present
        assert empire.max_storage.get("organics", 0.0) == pytest.approx(0.0)

    def test_multiple_colonies_sum(self):
        """Storage from multiple colonies sums up at empire level; each colony tracks its own."""
        f1 = _make_storage_facility("metals", capacity=10000.0, instance_id="s1")
        f2 = _make_storage_facility("metals", capacity=5000.0, instance_id="s2")
        p1 = _make_planet(facilities=[f1], name="Colony A")
        p2 = _make_planet(facilities=[f2], name="Colony B")
        empire = _make_empire(colonies=[p1, p2])

        engine = self._make_engine()
        engine.recalculate_storage([empire])

        # Per-colony max_stockpile
        assert p1.max_stockpile["metals"] == pytest.approx(10000.0)
        assert p2.max_stockpile["metals"] == pytest.approx(5000.0)
        # Empire aggregate
        assert empire.max_storage["metals"] == pytest.approx(15000.0)

    def test_empty_colonies_no_storage(self):
        """Empire with no colonies gets empty max_storage."""
        empire = _make_empire(colonies=[])

        engine = self._make_engine()
        engine.recalculate_storage([empire])

        assert empire.max_storage == {}

    def test_process_harvesting_tick_calls_recalculate_storage(self):
        """process_harvesting_tick recalculates storage before harvesting."""
        storage = _make_storage_facility("metals", capacity=500.0, instance_id="s1")
        harvester = _make_harvester_facility("metals", base_harvest_rate=100.0, instance_id="h1")
        planet = _make_planet(
            resources={"metals": {"quantity": 5000, "quality": 1.0}},
            facilities=[storage, harvester],
            stockpile={"metals": 450.0},
        )
        empire = _make_empire(
            colonies=[planet],
            resource_pool={"metals": 450.0},
            max_storage={},  # Will be calculated
        )

        engine = self._make_engine()
        # Run full turn (100 ticks)
        for tick in range(1, 101):
            engine.process_harvesting_tick(tick, [empire])

        # Storage should be set to 500 from the facility (colony and empire)
        assert planet.max_stockpile["metals"] == pytest.approx(500.0)
        assert empire.max_storage["metals"] == pytest.approx(500.0)
        # Harvest = 100*1.0 = 100, but stockpile was 450, cap at 500, so 500
        assert planet.stockpile["metals"] == pytest.approx(500.0)

    def test_registry_based_storage_lookup(self):
        """Engine uses registries to resolve storage abilities from plain IDs."""
        facility = PlanetaryFacility(
            instance_id="reg-store-001",
            design_id="metals_vault_complex",
            name="Metals Vault",
            design_data={
                "layers": {
                    "core": ["resource_vault_metals"]
                }
            },
        )
        planet = _make_planet(facilities=[facility])
        empire = _make_empire(colonies=[planet])

        regs = _make_mock_registries()
        # Add storage component to registry
        storage_comp = MagicMock()
        storage_comp.abilities = {
            "LocalStorage": {
                "resource_type": "metals",
                "capacity": 10000.0,
            }
        }
        original_get = regs.components.get

        def enhanced_get(comp_id):
            if comp_id == "resource_vault_metals":
                return storage_comp
            return original_get(comp_id)

        regs.components.get = enhanced_get

        engine = self._make_engine(registries=regs)
        engine.recalculate_storage([empire])

        assert planet.max_stockpile["metals"] == pytest.approx(10000.0)
        assert empire.max_storage["metals"] == pytest.approx(10000.0)


# ===========================================================================
# Per-Tick Harvesting Tests (PROJ-161)
# ===========================================================================

class TestPerTickHarvesting:
    """Tests for HarvestingEngine.process_harvesting_tick() - PROJ-161."""

    _make_engine = staticmethod(_make_engine)

    def test_single_tick_harvests_one_hundredth(self):
        """Single tick extracts 1/100th of per-turn harvest rate."""
        facility = _make_harvester_facility("metals", base_harvest_rate=100.0)
        planet = _make_planet(
            resources={"metals": {"quantity": 5000, "quality": 1.0}},
            facilities=[facility],
        )
        empire = _make_empire(
            colonies=[planet],
            resource_pool={"metals": 0.0},
        )

        engine = self._make_engine()
        engine.process_harvesting_tick(1, [empire])

        # Per-turn would be 100 * 1.0 = 100; per-tick is 100/100 = 1.0
        assert planet.stockpile["metals"] == pytest.approx(1.0)
        assert planet.deposits["metals"]["quantity"] == pytest.approx(4999.0)

    def test_100_ticks_total_equals_expected_harvest(self):
        """Calling process_harvesting_tick 100 times produces expected per-turn total."""
        facility = _make_harvester_facility("metals", base_harvest_rate=100.0, instance_id="h1")
        planet = _make_planet(
            resources={"metals": {"quantity": 5000, "quality": 0.8}},
            facilities=[facility],
        )
        empire = _make_empire(
            colonies=[planet],
            resource_pool={"metals": 0.0},
        )

        engine = self._make_engine()

        # Per-tick: call 100 times
        for tick in range(1, 101):
            engine.process_harvesting_tick(tick, [empire])

        # Expected per-turn harvest: base_rate * quality = 100 * 0.8 = 80
        assert planet.stockpile["metals"] == pytest.approx(80.0, rel=1e-9)
        assert planet.deposits["metals"]["quantity"] == pytest.approx(5000 - 80.0, rel=1e-9)

    def test_storage_cap_enforced_per_tick(self):
        """Storage cap correctly limits per-tick accumulation near capacity."""
        storage = _make_storage_facility("metals", capacity=500.0, instance_id="s1")
        harvester = _make_harvester_facility("metals", base_harvest_rate=100.0, instance_id="h1")
        planet = _make_planet(
            resources={"metals": {"quantity": 5000, "quality": 1.0}},
            facilities=[storage, harvester],
            stockpile={"metals": 499.5},  # Near cap
        )
        empire = _make_empire(
            colonies=[planet],
            resource_pool={"metals": 499.5},
            max_storage={"metals": 500.0},
        )

        engine = self._make_engine()
        engine.process_harvesting_tick(1, [empire])

        # Would add 1.0, but cap at 500
        assert planet.stockpile["metals"] == pytest.approx(500.0)

    def test_planet_depletion_across_ticks(self):
        """Planet with small quantity depletes mid-turn, quantity never goes negative."""
        # Planet has only 0.5 units but harvester wants 1.0 per tick
        facility = _make_harvester_facility("exotics", base_harvest_rate=100.0)
        planet = _make_planet(
            resources={"exotics": {"quantity": 0.5, "quality": 1.0}},
            facilities=[facility],
        )
        empire = _make_empire(
            colonies=[planet],
            resource_pool={"exotics": 0.0},
        )

        engine = self._make_engine()

        # First tick: harvester wants 1.0, only 0.5 available
        engine.process_harvesting_tick(1, [empire])
        assert planet.deposits["exotics"]["quantity"] == pytest.approx(0.0)
        assert planet.stockpile["exotics"] == pytest.approx(0.5)

        # Second tick: nothing left to harvest
        engine.process_harvesting_tick(2, [empire])
        assert planet.deposits["exotics"]["quantity"] == pytest.approx(0.0)
        assert planet.stockpile["exotics"] == pytest.approx(0.5)  # Unchanged

    def test_non_operational_facility_skipped_per_tick(self):
        """Non-operational facility produces nothing in per-tick mode."""
        facility = _make_harvester_facility("metals", base_harvest_rate=100.0, is_operational=False)
        planet = _make_planet(
            resources={"metals": {"quantity": 5000, "quality": 1.0}},
            facilities=[facility],
        )
        empire = _make_empire(
            colonies=[planet],
            resource_pool={"metals": 0.0},
        )

        engine = self._make_engine()
        engine.process_harvesting_tick(1, [empire])

        assert planet.stockpile.get("metals", 0.0) == pytest.approx(0.0)
        assert planet.deposits["metals"]["quantity"] == pytest.approx(5000.0)

    def test_recalculate_storage_called_each_tick(self):
        """Storage is recalculated on each tick to handle mid-turn changes."""
        storage = _make_storage_facility("metals", capacity=1000.0, instance_id="s1")
        harvester = _make_harvester_facility("metals", base_harvest_rate=100.0, instance_id="h1")
        planet = _make_planet(
            resources={"metals": {"quantity": 5000, "quality": 1.0}},
            facilities=[storage, harvester],
        )
        empire = _make_empire(
            colonies=[planet],
            resource_pool={"metals": 0.0},
            max_storage={},  # Will be calculated
        )

        engine = self._make_engine()
        engine.process_harvesting_tick(1, [empire])

        # Storage should be set from the facility (colony and empire)
        assert planet.max_stockpile["metals"] == pytest.approx(1000.0)
        assert empire.max_storage["metals"] == pytest.approx(1000.0)
        # And resource harvested into colony stockpile
        assert planet.stockpile["metals"] == pytest.approx(1.0)
