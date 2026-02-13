"""
Unit tests for FleetOrderProcessor TRANSFER operations.

PROJ-119 Task 1.2: TCG-STR-002 - FleetOrderProcessor Transfer logic has minimal tests.
Tests focus on cargo transfer between fleets and colonies.
"""

import pytest
from unittest.mock import MagicMock, patch

from game.strategy.data.fleet import Fleet, FleetOrder, OrderType
from game.core.hex_math import HexCoord


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_fleet():
    """Create a mock fleet for transfer tests."""
    fleet = MagicMock(spec=Fleet)
    fleet.id = 1
    fleet.owner_id = 0
    fleet.location = HexCoord(5, 5)
    fleet.orders = []
    fleet.get_current_order = MagicMock(return_value=None)
    fleet.pop_order = MagicMock()
    fleet.get_fleet_cargo_capacity = MagicMock(return_value=100)
    fleet.get_fleet_cargo_current = MagicMock(return_value=50)
    fleet.load_cargo_to_fleet = MagicMock()
    fleet.unload_cargo_from_fleet = MagicMock(return_value=50)
    return fleet


@pytest.fixture
def mock_empire():
    """Create a mock empire."""
    empire = MagicMock()
    empire.id = 0
    empire.name = "Test Empire"
    empire.race_config = MagicMock()
    empire.race_config.race_id = "humans"
    return empire


@pytest.fixture
def mock_galaxy():
    """Create a mock galaxy."""
    galaxy = MagicMock()
    galaxy.get_planet_by_id = MagicMock(return_value=None)
    return galaxy


@pytest.fixture
def mock_planet():
    """Create a mock planet for transfer tests."""
    planet = MagicMock()
    planet.id = 100
    planet.name = "Colony Alpha"
    planet.location = HexCoord(5, 5)
    planet.owner_id = 0
    planet.populations = []
    return planet


@pytest.fixture
def processor():
    """Create a FleetOrderProcessor."""
    from game.strategy.engine.fleet_order_processor import FleetOrderProcessor
    return FleetOrderProcessor()


# =============================================================================
# Test: TRANSFER Order Processing
# =============================================================================

class TestProcessTransfer:
    """Tests for process_transfer() method."""

    def test_transfer_no_order_returns_failure(self, processor, mock_fleet, mock_empire, mock_galaxy):
        """Returns failure when no TRANSFER order exists."""
        mock_fleet.get_current_order.return_value = None

        result = processor.process_transfer(mock_fleet, mock_empire, mock_galaxy)

        assert result.success is False

    def test_transfer_wrong_order_type_returns_failure(self, processor, mock_fleet, mock_empire, mock_galaxy):
        """Returns failure when current order is not TRANSFER."""
        order = FleetOrder(OrderType.MOVE, HexCoord(10, 10))
        mock_fleet.get_current_order.return_value = order

        result = processor.process_transfer(mock_fleet, mock_empire, mock_galaxy)

        assert result.success is False

    def test_transfer_invalid_params_returns_failure(self, processor, mock_fleet, mock_empire, mock_galaxy):
        """Returns failure when transfer params are invalid."""
        order = FleetOrder(OrderType.TRANSFER, "not_a_dict")
        mock_fleet.get_current_order.return_value = order

        result = processor.process_transfer(mock_fleet, mock_empire, mock_galaxy)

        assert result.success is False
        mock_fleet.pop_order.assert_called()


class TestTransferValidation:
    """Tests for transfer validation via TransferValidator."""

    def test_transfer_validates_direction(self, processor, mock_fleet, mock_empire, mock_galaxy, mock_planet):
        """Invalid direction causes validation failure."""
        params = {
            'direction': 'invalid_direction',
            'cargo_type': 'passengers',
            'amount': 50,
            'planet_id': 100
        }
        order = FleetOrder(OrderType.TRANSFER, params)
        mock_fleet.get_current_order.return_value = order
        mock_galaxy.get_planet_by_id.return_value = mock_planet

        result = processor.process_transfer(mock_fleet, mock_empire, mock_galaxy)

        assert result.success is False

    def test_transfer_load_passengers(self, processor, mock_fleet, mock_empire, mock_galaxy, mock_planet):
        """Loading passengers from colony to fleet."""
        from game.strategy.data.planet import SpeciesPopulation

        # Setup colony with population
        pop = SpeciesPopulation(race_id="humans", count=200, happiness=0.5)
        mock_planet.populations = [pop]
        mock_planet.location = mock_fleet.location  # Same location
        mock_planet.total_population = 200  # Total pop for validation

        # Mock galaxy to return planet at fleet's location
        mock_galaxy.get_planets_at_global_hex = MagicMock(return_value=[mock_planet])

        params = {
            'direction': 'load',
            'cargo_type': 'passengers',
            'amount': 50,
            'planet_id': 100
        }
        order = FleetOrder(OrderType.TRANSFER, params)
        mock_fleet.get_current_order.return_value = order
        mock_galaxy.get_planet_by_id.return_value = mock_planet

        result = processor.process_transfer(mock_fleet, mock_empire, mock_galaxy)

        assert result.success is True
        mock_fleet.pop_order.assert_called()

    def test_transfer_unload_passengers(self, processor, mock_fleet, mock_empire, mock_galaxy, mock_planet):
        """Unloading passengers from fleet to colony."""
        mock_planet.location = mock_fleet.location
        mock_planet.populations = []

        # Mock galaxy to return planet at fleet's location
        mock_galaxy.get_planets_at_global_hex = MagicMock(return_value=[mock_planet])

        params = {
            'direction': 'unload',
            'cargo_type': 'passengers',
            'amount': 30,
            'planet_id': 100
        }
        order = FleetOrder(OrderType.TRANSFER, params)
        mock_fleet.get_current_order.return_value = order
        mock_galaxy.get_planet_by_id.return_value = mock_planet

        result = processor.process_transfer(mock_fleet, mock_empire, mock_galaxy)

        assert result.success is True


# =============================================================================
# Test: Load Operation (_execute_load)
# =============================================================================

class TestExecuteLoad:
    """Tests for _execute_load() method."""

    def test_load_passengers_from_colony(self, processor, mock_fleet, mock_planet, mock_empire):
        """Load passengers from colony population."""
        from game.strategy.data.planet import SpeciesPopulation

        pop = SpeciesPopulation(race_id="humans", count=200, happiness=0.5)
        mock_planet.populations = [pop]

        # Fleet has capacity
        mock_fleet.get_fleet_cargo_capacity.return_value = 100
        mock_fleet.get_fleet_cargo_current.return_value = 20  # 80 available

        result = processor._execute_load(mock_fleet, mock_planet, "passengers", 50, mock_empire)

        assert result == 50
        assert pop.count == 150  # 200 - 50
        mock_fleet.load_cargo_to_fleet.assert_called_with("passengers", 50)

    def test_load_capped_by_capacity(self, processor, mock_fleet, mock_planet, mock_empire):
        """Load amount capped by available cargo capacity."""
        from game.strategy.data.planet import SpeciesPopulation

        pop = SpeciesPopulation(race_id="humans", count=200, happiness=0.5)
        mock_planet.populations = [pop]

        # Fleet nearly full
        mock_fleet.get_fleet_cargo_capacity.return_value = 100
        mock_fleet.get_fleet_cargo_current.return_value = 90  # Only 10 space

        result = processor._execute_load(mock_fleet, mock_planet, "passengers", 50, mock_empire)

        assert result == 10  # Capped by available space
        mock_fleet.load_cargo_to_fleet.assert_called_with("passengers", 10)

    def test_load_capped_by_colony_population(self, processor, mock_fleet, mock_planet, mock_empire):
        """Load amount capped by colony population."""
        from game.strategy.data.planet import SpeciesPopulation

        pop = SpeciesPopulation(race_id="humans", count=30, happiness=0.5)
        mock_planet.populations = [pop]

        # Fleet has plenty of capacity
        mock_fleet.get_fleet_cargo_capacity.return_value = 100
        mock_fleet.get_fleet_cargo_current.return_value = 0

        result = processor._execute_load(mock_fleet, mock_planet, "passengers", 50, mock_empire)

        assert result == 30  # Capped by population
        assert pop.count == 0

    def test_load_with_species_id(self, processor, mock_fleet, mock_planet, mock_empire):
        """Load passengers of specific species."""
        from game.strategy.data.planet import SpeciesPopulation

        pop1 = SpeciesPopulation(race_id="humans", count=100, happiness=0.5)
        pop2 = SpeciesPopulation(race_id="klingons", count=50, happiness=0.5)
        mock_planet.populations = [pop1, pop2]

        mock_fleet.get_fleet_cargo_capacity.return_value = 100
        mock_fleet.get_fleet_cargo_current.return_value = 0

        result = processor._execute_load(
            mock_fleet, mock_planet, "passengers", 30, mock_empire, species_id="klingons"
        )

        assert result == 30
        assert pop2.count == 20  # Klingons reduced
        assert pop1.count == 100  # Humans unchanged

    def test_load_zero_amount_loads_all_capacity(self, processor, mock_fleet, mock_planet, mock_empire):
        """Amount of 0 means load as much as possible."""
        from game.strategy.data.planet import SpeciesPopulation

        pop = SpeciesPopulation(race_id="humans", count=200, happiness=0.5)
        mock_planet.populations = [pop]

        mock_fleet.get_fleet_cargo_capacity.return_value = 100
        mock_fleet.get_fleet_cargo_current.return_value = 20  # 80 available

        result = processor._execute_load(mock_fleet, mock_planet, "passengers", 0, mock_empire)

        assert result == 80  # Loads all available space


# =============================================================================
# Test: Unload Operation (_execute_unload)
# =============================================================================

class TestExecuteUnload:
    """Tests for _execute_unload() method."""

    def test_unload_passengers_to_colony(self, processor, mock_fleet, mock_planet, mock_empire):
        """Unload passengers to colony population."""
        mock_planet.populations = []

        mock_fleet.get_fleet_cargo_current.return_value = 100
        mock_fleet.unload_cargo_from_fleet.return_value = 50

        result = processor._execute_unload(mock_fleet, mock_planet, "passengers", 50, mock_empire)

        assert result == 50
        # Should create new species population
        assert len(mock_planet.populations) == 1
        assert mock_planet.populations[0].count == 50

    def test_unload_capped_by_cargo(self, processor, mock_fleet, mock_planet, mock_empire):
        """Unload capped by available cargo."""
        mock_planet.populations = []

        mock_fleet.get_fleet_cargo_current.return_value = 30
        mock_fleet.unload_cargo_from_fleet.return_value = 30

        result = processor._execute_unload(mock_fleet, mock_planet, "passengers", 50, mock_empire)

        assert result == 30

    def test_unload_zero_amount_unloads_all(self, processor, mock_fleet, mock_planet, mock_empire):
        """Amount of 0 means unload all cargo."""
        mock_planet.populations = []

        mock_fleet.get_fleet_cargo_current.return_value = 75
        mock_fleet.unload_cargo_from_fleet.return_value = 75

        result = processor._execute_unload(mock_fleet, mock_planet, "passengers", 0, mock_empire)

        assert result == 75

    def test_unload_adds_to_existing_species(self, processor, mock_fleet, mock_planet, mock_empire):
        """Unloading adds to existing species population."""
        from game.strategy.data.planet import SpeciesPopulation

        existing_pop = SpeciesPopulation(race_id="humans", count=100, happiness=0.5)
        mock_planet.populations = [existing_pop]

        mock_fleet.get_fleet_cargo_current.return_value = 50
        mock_fleet.unload_cargo_from_fleet.return_value = 50

        result = processor._execute_unload(mock_fleet, mock_planet, "passengers", 50, mock_empire)

        assert result == 50
        assert existing_pop.count == 150  # 100 + 50

    def test_unload_with_species_id(self, processor, mock_fleet, mock_planet, mock_empire):
        """Unload to specific species population."""
        from game.strategy.data.planet import SpeciesPopulation

        mock_planet.populations = []

        mock_fleet.get_fleet_cargo_current.return_value = 50
        mock_fleet.unload_cargo_from_fleet.return_value = 50

        result = processor._execute_unload(
            mock_fleet, mock_planet, "passengers", 50, mock_empire, species_id="vulcans"
        )

        assert result == 50
        # Should create population with specified race_id
        assert len(mock_planet.populations) == 1
        assert mock_planet.populations[0].race_id == "vulcans"


# =============================================================================
# Test: TransferResult Dataclass
# =============================================================================

class TestTransferResult:
    """Tests for TransferResult dataclass."""

    def test_transfer_result_has_required_fields(self):
        """TransferResult has expected fields."""
        from game.strategy.engine.fleet_order_processor import TransferResult

        result = TransferResult(success=True, amount_transferred=100, message="OK")

        assert result.success is True
        assert result.amount_transferred == 100
        assert result.message == "OK"

    def test_transfer_result_defaults(self):
        """TransferResult has sensible defaults."""
        from game.strategy.engine.fleet_order_processor import TransferResult

        result = TransferResult(success=False)

        assert result.success is False
        assert result.amount_transferred == 0
        assert result.message == ""
