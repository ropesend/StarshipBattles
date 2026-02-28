import pytest
from unittest.mock import MagicMock, patch
from game.strategy.validation.transfer_validator import TransferValidator
from game.core.hex_math import HexCoord
from game.core.validation import ValidationResult

class TestTransferValidatorRobustness:
    @pytest.fixture
    def mock_galaxy(self):
        galaxy = MagicMock()
        return galaxy

    @pytest.fixture
    def mock_fleet(self):
        fleet = MagicMock()
        fleet.location = HexCoord(10, 10) # Global system location
        fleet.resources.get_fleet_cargo_capacity.return_value = 1000
        fleet.resources.get_fleet_cargo_current.return_value = 0
        return fleet

    @pytest.fixture
    def mock_planet(self):
        planet = MagicMock()
        planet.name = "Test Planet"
        planet.owner_id = 0
        planet.location = HexCoord(2, 2) # Local hex in system
        planet.total_population = 100
        return planet
    
    @pytest.fixture
    def mock_system(self, mock_planet):
        system = MagicMock()
        system.planets = [mock_planet]
        return system

    def test_validate_accepts_fleet_at_system_center(self, mock_galaxy, mock_fleet, mock_planet, mock_system):
        """Verify that TransferValidator accepts a transfer if the fleet is in the correctly resolved system."""
        # Setup: Galaxy resolves system at fleet location
        mock_galaxy.get_system_at_location.return_value = mock_system
        
        # Galaxy systems dict contains the system
        mock_galaxy.systems = {(10,10): mock_system}
        
        # Act
        with patch('game.core.protocols.is_planet', return_value=True):
            with patch('game.core.protocols.is_fleet', return_value=False):
                result = TransferValidator.validate(
                    mock_galaxy, mock_fleet, mock_planet, "passengers", "load", 50
                )
        
        # Assert
        assert result.is_valid, f"Validation failed: {result.message}"

    def test_validate_rejects_fleet_in_wrong_system(self, mock_galaxy, mock_fleet, mock_planet):
        """Verify that TransferValidator rejects if the fleet is in a different system."""
        # Setup: Galaxy resolves a DIFFERENT system (or None)
        mock_galaxy.get_system_at_location.return_value = MagicMock() # Some other system
        mock_galaxy.systems = {(100,100): MagicMock()}
        
        # Act
        with patch('game.core.protocols.is_planet', return_value=True):
            with patch('game.core.protocols.is_fleet', return_value=False):
                result = TransferValidator.validate(
                    mock_galaxy, mock_fleet, mock_planet, "passengers", "load", 50
                )
        
        # Assert
        assert not result.is_valid
        assert "not at Test Planet's system" in result.message
