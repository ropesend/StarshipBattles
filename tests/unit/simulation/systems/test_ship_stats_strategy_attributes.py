"""
Tests for strategy-relevant attributes on Ship after recalculate_stats().

These attributes are needed by the strategy layer and must be populated
by the simulation ShipStatsCalculator so that Ship is the single source
of truth for all stat calculations.

Attributes under test:
- cargo_storage: Dict[str, float] — cargo capacity by type
- pod_storage_mass: float — drop pod mass capacity
- warp_resource_costs: Dict[str, float] — full warp cost breakdown
"""
import pytest
from game.simulation.entities.ship import Ship
from game.core.json_utils import load_json
from game.core.paths import Paths


FIXTURES_DIR = Paths.get_starter_designs_dir()


class TestCargoStorageAttribute:
    """Ship.cargo_storage should be populated by recalculate_stats()."""

    def test_cargo_storage_exists_after_recalculate(self, fresh_registries):
        """Ship should have a cargo_storage attribute after recalculate_stats()."""
        data = load_json(str(FIXTURES_DIR / "qs_escort.json"))
        ship = Ship.from_dict(data, registries=fresh_registries)
        ship.recalculate_stats()
        assert hasattr(ship, 'cargo_storage')

    def test_cargo_storage_is_dict(self, fresh_registries):
        """cargo_storage should be a dict."""
        data = load_json(str(FIXTURES_DIR / "qs_escort.json"))
        ship = Ship.from_dict(data, registries=fresh_registries)
        ship.recalculate_stats()
        assert isinstance(ship.cargo_storage, dict)

    def test_cargo_storage_empty_when_no_cargo_components(self, fresh_registries):
        """Ship without CargoStorage components should have empty cargo_storage."""
        data = load_json(str(FIXTURES_DIR / "qs_escort.json"))
        ship = Ship.from_dict(data, registries=fresh_registries)
        ship.recalculate_stats()
        assert ship.cargo_storage == {}

    def test_cargo_storage_populated_for_cargo_ship(self, fresh_registries):
        """Cargo freighter should have non-empty cargo_storage."""
        data = load_json(str(FIXTURES_DIR / "qs_cargo_freighter.json"))
        ship = Ship.from_dict(data, registries=fresh_registries)
        ship.recalculate_stats()
        assert len(ship.cargo_storage) > 0
        # All values should be positive
        for cargo_type, capacity in ship.cargo_storage.items():
            assert isinstance(cargo_type, str)
            assert capacity > 0


class TestPodStorageMassAttribute:
    """Ship.pod_storage_mass should be populated by recalculate_stats()."""

    def test_pod_storage_mass_exists_after_recalculate(self, fresh_registries):
        """Ship should have a pod_storage_mass attribute after recalculate_stats()."""
        data = load_json(str(FIXTURES_DIR / "qs_escort.json"))
        ship = Ship.from_dict(data, registries=fresh_registries)
        ship.recalculate_stats()
        assert hasattr(ship, 'pod_storage_mass')

    def test_pod_storage_mass_is_float(self, fresh_registries):
        """pod_storage_mass should be a float."""
        data = load_json(str(FIXTURES_DIR / "qs_escort.json"))
        ship = Ship.from_dict(data, registries=fresh_registries)
        ship.recalculate_stats()
        assert isinstance(ship.pod_storage_mass, float)

    def test_pod_storage_mass_zero_when_no_pod_components(self, fresh_registries):
        """Ship without PodStorage components should have 0 pod_storage_mass."""
        data = load_json(str(FIXTURES_DIR / "qs_escort.json"))
        ship = Ship.from_dict(data, registries=fresh_registries)
        ship.recalculate_stats()
        assert ship.pod_storage_mass == 0.0

    def test_pod_storage_mass_positive_for_colony_ship(self, fresh_registries):
        """Colony ship should have positive pod_storage_mass."""
        data = load_json(str(FIXTURES_DIR / "qs_colony_ship.json"))
        ship = Ship.from_dict(data, registries=fresh_registries)
        ship.recalculate_stats()
        assert ship.pod_storage_mass > 0


class TestWarpResourceCostsAttribute:
    """Ship.warp_resource_costs should be populated by recalculate_stats()."""

    def test_warp_resource_costs_exists_after_recalculate(self, fresh_registries):
        """Ship should have a warp_resource_costs attribute after recalculate_stats()."""
        data = load_json(str(FIXTURES_DIR / "qs_escort.json"))
        ship = Ship.from_dict(data, registries=fresh_registries)
        ship.recalculate_stats()
        assert hasattr(ship, 'warp_resource_costs')

    def test_warp_resource_costs_is_dict(self, fresh_registries):
        """warp_resource_costs should be a dict."""
        data = load_json(str(FIXTURES_DIR / "qs_escort.json"))
        ship = Ship.from_dict(data, registries=fresh_registries)
        ship.recalculate_stats()
        assert isinstance(ship.warp_resource_costs, dict)

    def test_warp_resource_costs_populated_for_warp_ship(self, fresh_registries):
        """Ship with warp drive should have non-empty warp_resource_costs."""
        data = load_json(str(FIXTURES_DIR / "qs_escort.json"))
        ship = Ship.from_dict(data, registries=fresh_registries)
        ship.recalculate_stats()
        # Escort has a warp drive — should have energy cost
        if ship.warp_max_tonnage > 0:
            assert len(ship.warp_resource_costs) > 0

    def test_warp_resource_costs_empty_for_non_warp_ship(self, fresh_registries):
        """Ship without warp drive should have empty warp_resource_costs."""
        data = load_json(str(FIXTURES_DIR / "qs_geologic_stabilizer_complex.json"))
        ship = Ship.from_dict(data, registries=fresh_registries)
        ship.recalculate_stats()
        assert ship.warp_resource_costs == {}

    def test_warp_resource_costs_matches_scalar_energy_cost(self, fresh_registries):
        """warp_resource_costs['energy'] should equal warp_energy_cost."""
        data = load_json(str(FIXTURES_DIR / "qs_escort.json"))
        ship = Ship.from_dict(data, registries=fresh_registries)
        ship.recalculate_stats()
        if ship.warp_energy_cost > 0:
            assert ship.warp_resource_costs.get('energy', 0) == ship.warp_energy_cost
