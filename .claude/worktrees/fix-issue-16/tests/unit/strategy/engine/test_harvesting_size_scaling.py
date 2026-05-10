"""Tests for HarvestingEngine size_mount scaling.

Phase 2C/2D: Verify that harvest rates and storage capacities
scale with the size_mount modifier on facility components.
"""
import pytest
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

from game.strategy.engine.harvesting_engine import HarvestingEngine


@dataclass
class MockFacility:
    """Minimal facility for harvesting tests."""
    design_data: Dict[str, Any]
    is_operational: bool = True
    instance_id: str = "test-facility"
    design_id: str = "test"
    name: str = "Test Facility"
    construction_queue: list = field(default_factory=list)
    consumable_levels: dict = field(default_factory=dict)


@dataclass
class MockColony:
    """Minimal colony (planet) for harvesting tests."""
    name: str = "Test Colony"
    deposits: Dict[str, dict] = field(default_factory=dict)
    stockpile: Dict[str, float] = field(default_factory=dict)
    max_stockpile: Dict[str, float] = field(default_factory=dict)
    max_staging_mass: float = 0.0
    facilities: list = field(default_factory=list)

    def add_to_stockpile(self, resource: str, amount: float):
        current = self.stockpile.get(resource, 0.0)
        max_val = self.max_stockpile.get(resource, float('inf'))
        self.stockpile[resource] = min(current + amount, max_val)


@dataclass
class MockEmpire:
    """Minimal empire for harvesting tests."""
    id: int = 0
    colonies: list = field(default_factory=list)
    max_storage: dict = field(default_factory=dict)


class TestHarvestingWithSizeMount:
    """Test that harvest rates scale with size_mount modifier."""

    def _make_facility_with_harvester(self, resource_type, size_mount_value=None):
        """Create a facility with a single harvester at the given size."""
        comp = {
            "id": "metal_harvester",
            "abilities": {
                "ResourceHarvester": {
                    "resource_type": resource_type,
                    "base_harvest_rate": 100.0
                }
            }
        }
        if size_mount_value is not None:
            comp["modifiers"] = [{"id": "simple_size_mount", "value": size_mount_value}]
        return MockFacility(
            design_data={"layers": {"CORE": [comp]}}
        )

    def test_harvester_at_full_size(self, fresh_registries):
        """Full-size harvester (no modifier) should harvest at 100% rate."""
        colony = MockColony(
            deposits={"metals": {"quantity": 10000, "quality": 1.0}},
            max_stockpile={"metals": 100000},
        )
        colony.facilities = [self._make_facility_with_harvester("metals")]

        empire = MockEmpire(colonies=[colony])
        engine = HarvestingEngine(registries=fresh_registries)
        engine.process_harvesting_tick(1, [empire])

        # 100.0 * 1.0 quality * 0.01 tick_fraction = 1.0
        assert colony.stockpile.get("metals", 0) == pytest.approx(1.0, abs=0.01)

    def test_harvester_at_size_0_2(self, fresh_registries):
        """Harvester at size 0.2 should harvest at 20% rate."""
        colony = MockColony(
            deposits={"metals": {"quantity": 10000, "quality": 1.0}},
            max_stockpile={"metals": 100000},
        )
        colony.facilities = [self._make_facility_with_harvester("metals", 0.2)]

        empire = MockEmpire(colonies=[colony])
        engine = HarvestingEngine(registries=fresh_registries)
        engine.process_harvesting_tick(1, [empire])

        # 100.0 * 0.2 size * 1.0 quality * 0.01 tick_fraction = 0.2
        assert colony.stockpile.get("metals", 0) == pytest.approx(0.2, abs=0.01)

    def test_harvester_at_size_1_0_explicit(self, fresh_registries):
        """Harvester at explicit size 1.0 should harvest at 100% rate."""
        colony = MockColony(
            deposits={"metals": {"quantity": 10000, "quality": 1.0}},
            max_stockpile={"metals": 100000},
        )
        colony.facilities = [self._make_facility_with_harvester("metals", 1.0)]

        empire = MockEmpire(colonies=[colony])
        engine = HarvestingEngine(registries=fresh_registries)
        engine.process_harvesting_tick(1, [empire])

        assert colony.stockpile.get("metals", 0) == pytest.approx(1.0, abs=0.01)


class TestStorageWithSizeMount:
    """Test that storage capacities scale with size_mount modifier."""

    def _make_facility_with_storage(self, resource_type, capacity, size_mount_value=None):
        """Create a facility with a single storage vault at the given size."""
        comp = {
            "id": "resource_vault_metals",
            "abilities": {
                "LocalStorage": {
                    "resource_type": resource_type,
                    "capacity": capacity
                }
            }
        }
        if size_mount_value is not None:
            comp["modifiers"] = [{"id": "simple_size_mount", "value": size_mount_value}]
        return MockFacility(
            design_data={"layers": {"CORE": [comp]}}
        )

    def test_storage_at_full_size(self, fresh_registries):
        """Full-size storage should have 100% capacity."""
        colony = MockColony()
        colony.facilities = [self._make_facility_with_storage("metals", 10000.0)]

        empire = MockEmpire(colonies=[colony])
        engine = HarvestingEngine(registries=fresh_registries)
        engine.recalculate_storage([empire])

        assert colony.max_stockpile.get("metals", 0) == pytest.approx(10000.0)

    def test_storage_at_size_0_2(self, fresh_registries):
        """Storage at size 0.2 should have 20% capacity."""
        colony = MockColony()
        colony.facilities = [self._make_facility_with_storage("metals", 10000.0, 0.2)]

        empire = MockEmpire(colonies=[colony])
        engine = HarvestingEngine(registries=fresh_registries)
        engine.recalculate_storage([empire])

        assert colony.max_stockpile.get("metals", 0) == pytest.approx(2000.0)

    def test_storage_at_size_1_0_explicit(self, fresh_registries):
        """Storage at explicit size 1.0 should have 100% capacity."""
        colony = MockColony()
        colony.facilities = [self._make_facility_with_storage("metals", 10000.0, 1.0)]

        empire = MockEmpire(colonies=[colony])
        engine = HarvestingEngine(registries=fresh_registries)
        engine.recalculate_storage([empire])

        assert colony.max_stockpile.get("metals", 0) == pytest.approx(10000.0)
