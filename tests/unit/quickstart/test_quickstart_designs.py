"""
Tests for quickstart ship design fixtures.

These tests validate that the design fixtures used by quickstart buttons
are valid, can be loaded correctly, and have correct stats. They also
detect when code changes break the fixture format.
"""
import pytest
from pathlib import Path

from game.simulation.entities.ship import Ship
from game.simulation.entities.ship_loader import initialize_ship_data, load_vehicle_classes
from game.simulation.components.component import load_components, load_modifiers
from game.core.registry import RegistryManager
from game.core.json_utils import load_json
from tests.fixtures.paths import get_data_dir, get_project_root
from tests.unit.quickstart.conftest import (
    get_quickstart_designs_dir,
    load_all_quickstart_designs,
)


# Load all quickstart design fixtures for parametrized tests
QUICKSTART_DESIGNS = load_all_quickstart_designs()


@pytest.fixture
def quickstart_ship_data():
    """
    Fixture that ensures ship data is loaded for quickstart design tests.

    The actual data loading is handled by the root conftest's reset_game_state
    fixture which uses the session cache. This fixture just provides a dependency
    marker to ensure tests that need ship data declare it explicitly.
    """
    # Data is loaded by reset_game_state in root conftest.py
    # This fixture is just a marker for tests that need ship data
    yield


class TestQuickstartDesignFixturesExist:
    """Test that fixture files exist and are valid JSON."""

    def test_quickstart_designs_directory_exists(self, quickstart_designs_dir):
        """The quickstart designs directory should exist."""
        assert quickstart_designs_dir.exists(), "Quickstart designs directory should exist"
        assert quickstart_designs_dir.is_dir()

    def test_quickstart_designs_not_empty(self):
        """Should have at least one quickstart design fixture."""
        assert len(QUICKSTART_DESIGNS) > 0, "Should have at least one quickstart design fixture"

    def test_has_escort_design(self, quickstart_designs_dir):
        """Should have qs_escort.json fixture."""
        assert (quickstart_designs_dir / "qs_escort.json").exists()

    def test_has_complex_design(self, quickstart_designs_dir):
        """Should have qs_complex.json fixture."""
        assert (quickstart_designs_dir / "qs_complex.json").exists()


@pytest.mark.parametrize("design_name,design_data", QUICKSTART_DESIGNS, ids=lambda x: x if isinstance(x, str) else x[0] if isinstance(x, tuple) else "unknown")
class TestQuickstartDesignsValid:
    """Data-driven tests for quickstart design fixture validity."""

    def test_design_has_required_fields(self, design_name, design_data):
        """Each quickstart design should have all required fields."""
        required_fields = ["name", "ship_class", "vehicle_type", "layers"]
        for field in required_fields:
            assert field in design_data, f"{design_name} missing required field: {field}"

    def test_design_loads_as_valid_ship(self, design_name, design_data, quickstart_ship_data):
        """Each quickstart design should load as a valid Ship."""
        ship = Ship.from_dict(design_data)
        assert ship is not None
        assert ship.name, f"{design_name} must have a name"

    def test_design_recalculates_stats(self, design_name, design_data, quickstart_ship_data):
        """Each quickstart design should recalculate stats without error."""
        ship = Ship.from_dict(design_data)
        ship.recalculate_stats()
        assert ship.mass > 0, f"{design_name} should have positive mass"
        assert ship.max_hp > 0, f"{design_name} should have positive HP"

    def test_design_has_expected_stats(self, design_name, design_data):
        """Each quickstart design should have expected_stats for validation."""
        assert "expected_stats" in design_data, f"{design_name} should have expected_stats"
        expected = design_data["expected_stats"]
        assert "max_hp" in expected, f"{design_name} expected_stats should have max_hp"
        assert "mass" in expected, f"{design_name} expected_stats should have mass"

    def test_design_has_metadata(self, design_name, design_data):
        """Each quickstart design should have _metadata section."""
        assert "_metadata" in design_data, f"{design_name} should have _metadata"
        metadata = design_data["_metadata"]
        assert "is_obsolete" in metadata
        assert "times_built" in metadata

    def test_design_stats_match_expected(self, design_name, design_data, quickstart_ship_data):
        """Design stats should match expected_stats within tolerance."""
        expected = design_data.get("expected_stats", {})
        if not expected:
            pytest.skip(f"{design_name} has no expected_stats")

        ship = Ship.from_dict(design_data)
        ship.recalculate_stats()

        # Check mass matches (within 5% tolerance due to formula variations)
        if "mass" in expected:
            tolerance = max(expected["mass"] * 0.05, 25)  # At least 25 or 5%
            assert abs(ship.mass - expected["mass"]) <= tolerance, \
                f"{design_name} mass mismatch: expected {expected['mass']}, got {ship.mass}"

        # Check HP matches (within tolerance due to formula variations)
        if "max_hp" in expected:
            tolerance = expected["max_hp"] * 0.1  # 10% tolerance
            assert abs(ship.max_hp - expected["max_hp"]) <= tolerance, \
                f"{design_name} HP mismatch: expected {expected['max_hp']}, got {ship.max_hp}"


class TestQuickstartDesignSpecificContent:
    """Tests for specific expected content in quickstart designs."""

    def test_escort_has_bridge(self, quickstart_designs_dir, quickstart_ship_data):
        """Escort design should have a bridge component."""
        data = load_json(str(quickstart_designs_dir / "qs_escort.json"))
        ship = Ship.from_dict(data)

        all_comps = ship.get_all_components()
        has_bridge = any(c.type_str == "Bridge" for c in all_comps)
        assert has_bridge, "Escort should have a bridge component"

    def test_escort_has_engine(self, quickstart_designs_dir, quickstart_ship_data):
        """Escort design should have an engine component."""
        data = load_json(str(quickstart_designs_dir / "qs_escort.json"))
        ship = Ship.from_dict(data)

        all_comps = ship.get_all_components()
        has_engine = any(c.has_ability("CombatPropulsion") for c in all_comps)
        assert has_engine, "Escort should have an engine component"

    def test_escort_has_warp_drive(self, quickstart_designs_dir, quickstart_ship_data):
        """Escort design should have a warp drive component."""
        data = load_json(str(quickstart_designs_dir / "qs_escort.json"))
        ship = Ship.from_dict(data)

        all_comps = ship.get_all_components()
        has_warp = any(c.has_ability("WarpJump") for c in all_comps)
        assert has_warp, "Escort should have a warp drive component"

    def test_escort_has_fuel_storage(self, quickstart_designs_dir, quickstart_ship_data):
        """Escort design should have fuel storage."""
        data = load_json(str(quickstart_designs_dir / "qs_escort.json"))
        ship = Ship.from_dict(data)
        ship.recalculate_stats()

        max_fuel = ship.resources.get_max_value('fuel')
        assert max_fuel > 0, "Escort should have fuel storage"

    def test_complex_has_command(self, quickstart_designs_dir, quickstart_ship_data):
        """Complex design should have a command component."""
        data = load_json(str(quickstart_designs_dir / "qs_complex.json"))
        ship = Ship.from_dict(data)

        all_comps = ship.get_all_components()
        has_command = any(c.has_ability("CommandAndControl") for c in all_comps)
        assert has_command, "Complex should have a command component"

    def test_complex_has_shipyard(self, quickstart_designs_dir, quickstart_ship_data):
        """Complex design should have a space shipyard component."""
        data = load_json(str(quickstart_designs_dir / "qs_complex.json"))
        ship = Ship.from_dict(data)

        all_comps = ship.get_all_components()
        has_shipyard = any(c.has_ability("SpaceShipyard") for c in all_comps)
        assert has_shipyard, "Complex should have a space shipyard component"

    def test_complex_is_planetary_complex_type(self, quickstart_designs_dir):
        """Complex design should be of Planetary Complex type."""
        data = load_json(str(quickstart_designs_dir / "qs_complex.json"))
        assert data["vehicle_type"] == "Planetary Complex"

    def test_escort_is_ship_type(self, quickstart_designs_dir):
        """Escort design should be of Ship type."""
        data = load_json(str(quickstart_designs_dir / "qs_escort.json"))
        assert data["vehicle_type"] == "Ship"
