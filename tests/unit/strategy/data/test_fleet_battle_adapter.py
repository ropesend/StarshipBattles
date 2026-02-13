"""
Unit tests for FleetBattleAdapter.

PROJ-119 Task 1.4: TCG-STR-004 - FleetBattleAdapter has minimal test coverage.
Tests focus on battle ship conversion and result updates.
"""

import pytest
from unittest.mock import MagicMock, PropertyMock, patch

from game.core.hex_math import HexCoord


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_fleet():
    """Create a mock Fleet."""
    fleet = MagicMock()
    fleet.ships = []
    fleet.can_use_warp.return_value = True
    fleet.speed = 10
    fleet.trigger_speed_recalculation = MagicMock()
    return fleet


@pytest.fixture
def mock_ship_instance():
    """Create a mock ShipInstance."""
    ship = MagicMock()
    ship.name = "USS Enterprise"
    ship.is_combat_capable.return_value = True
    ship.to_ship.return_value = MagicMock()
    ship.update_from_ship = MagicMock()
    return ship


@pytest.fixture
def mock_non_combat_ship():
    """Create a mock non-combat ship (e.g., colony ship)."""
    ship = MagicMock()
    ship.name = "Colonizer"
    ship.is_combat_capable.return_value = False
    return ship


@pytest.fixture
def fleet_battle_adapter(mock_fleet):
    """Create a FleetBattleAdapter with mock fleet."""
    from game.strategy.data.fleet_battle_adapter import FleetBattleAdapter
    return FleetBattleAdapter(mock_fleet)


# =============================================================================
# Test: FleetBattleAdapter Initialization
# =============================================================================

class TestFleetBattleAdapterInit:
    """Tests for FleetBattleAdapter initialization."""

    def test_adapter_can_be_created(self, mock_fleet):
        """FleetBattleAdapter can be instantiated."""
        from game.strategy.data.fleet_battle_adapter import FleetBattleAdapter

        adapter = FleetBattleAdapter(mock_fleet)

        assert adapter is not None
        assert adapter._fleet is mock_fleet


# =============================================================================
# Test: to_battle_ships()
# =============================================================================

class TestToBattleShips:
    """Tests for to_battle_ships() conversion."""

    def test_empty_fleet_returns_empty_list(self, fleet_battle_adapter, mock_fleet):
        """Empty fleet returns no battle ships."""
        mock_fleet.ships = []

        result = fleet_battle_adapter.to_battle_ships(team_id=0)

        assert result == []

    def test_converts_combat_capable_ships(self, fleet_battle_adapter, mock_fleet, mock_ship_instance):
        """Combat-capable ships are converted to battle ships."""
        mock_fleet.ships = [mock_ship_instance]
        mock_battle_ship = MagicMock()
        mock_ship_instance.to_ship.return_value = mock_battle_ship

        result = fleet_battle_adapter.to_battle_ships(team_id=0)

        assert len(result) == 1
        assert result[0] is mock_battle_ship
        mock_ship_instance.to_ship.assert_called_once()

    def test_skips_non_combat_ships(self, fleet_battle_adapter, mock_fleet, mock_ship_instance, mock_non_combat_ship):
        """Non-combat ships are not included in battle."""
        mock_fleet.ships = [mock_ship_instance, mock_non_combat_ship]

        result = fleet_battle_adapter.to_battle_ships(team_id=0)

        assert len(result) == 1
        mock_non_combat_ship.to_ship.assert_not_called()

    def test_passes_team_id_to_ships(self, fleet_battle_adapter, mock_fleet, mock_ship_instance):
        """Team ID is passed to each ship conversion."""
        mock_fleet.ships = [mock_ship_instance]

        fleet_battle_adapter.to_battle_ships(team_id=1)

        call_args = mock_ship_instance.to_ship.call_args
        assert call_args[0][1] == 1  # Second positional arg is team_id

    def test_uses_provided_formation_positions(self, fleet_battle_adapter, mock_fleet, mock_ship_instance):
        """Provided formation positions are used."""
        mock_fleet.ships = [mock_ship_instance]
        positions = [(100, 200)]

        fleet_battle_adapter.to_battle_ships(team_id=0, formation_positions=positions)

        call_args = mock_ship_instance.to_ship.call_args
        assert call_args[0][0] == (100, 200)  # First positional arg is position

    def test_generates_default_positions_when_not_provided(self, fleet_battle_adapter, mock_fleet, mock_ship_instance):
        """Default positions are generated if not provided."""
        mock_fleet.ships = [mock_ship_instance]

        fleet_battle_adapter.to_battle_ships(team_id=0)

        # Should have called with some position
        call_args = mock_ship_instance.to_ship.call_args
        assert call_args[0][0] is not None
        assert isinstance(call_args[0][0], tuple)
        assert len(call_args[0][0]) == 2

    def test_passes_registries_to_ships(self, fleet_battle_adapter, mock_fleet, mock_ship_instance):
        """Registries are passed to ship conversion."""
        mock_fleet.ships = [mock_ship_instance]
        mock_registries = MagicMock()

        fleet_battle_adapter.to_battle_ships(team_id=0, registries=mock_registries)

        call_kwargs = mock_ship_instance.to_ship.call_args[1]
        assert call_kwargs.get('registries') is mock_registries


# =============================================================================
# Test: _default_formation_positions()
# =============================================================================

class TestDefaultFormationPositions:
    """Tests for default formation position generation."""

    def test_generates_correct_count(self, fleet_battle_adapter):
        """Generates correct number of positions."""
        positions = fleet_battle_adapter._default_formation_positions(5, team_id=0)

        assert len(positions) == 5

    def test_team_0_starts_on_left(self, fleet_battle_adapter):
        """Team 0 positions start on the left side."""
        positions = fleet_battle_adapter._default_formation_positions(1, team_id=0)

        # Team 0 base_x is 20000
        assert positions[0][0] == 20000

    def test_team_1_starts_on_right(self, fleet_battle_adapter):
        """Team 1 positions start on the right side."""
        positions = fleet_battle_adapter._default_formation_positions(1, team_id=1)

        # Team 1 base_x is 80000
        assert positions[0][0] == 80000

    def test_positions_are_evenly_spaced(self, fleet_battle_adapter):
        """Positions are evenly spaced in y direction."""
        positions = fleet_battle_adapter._default_formation_positions(3, team_id=0)

        # Check y positions are spaced by 2000
        y_positions = sorted([p[1] for p in positions])
        spacing = y_positions[1] - y_positions[0]

        assert spacing == 2000


# =============================================================================
# Test: update_from_battle_results()
# =============================================================================

class TestUpdateFromBattleResults:
    """Tests for update_from_battle_results()."""

    def test_removes_destroyed_ships(self, fleet_battle_adapter, mock_fleet, mock_ship_instance):
        """Ships not in survivors list are removed."""
        mock_fleet.ships = [mock_ship_instance]

        # Empty survivors - ship was destroyed
        fleet_battle_adapter.update_from_battle_results([])

        # Fleet ships should be empty after update
        assert mock_fleet.ships == []

    def test_keeps_surviving_ships(self, fleet_battle_adapter, mock_fleet, mock_ship_instance):
        """Surviving ships are kept in fleet."""
        mock_fleet.ships = [mock_ship_instance]

        # Ship survives
        survivor = MagicMock()
        survivor.name = "USS Enterprise"

        fleet_battle_adapter.update_from_battle_results([survivor])

        # Ship should still be in fleet
        assert len(mock_fleet.ships) == 1

    def test_updates_ship_state_from_survivor(self, fleet_battle_adapter, mock_fleet, mock_ship_instance):
        """Ship state is updated from battle results."""
        mock_fleet.ships = [mock_ship_instance]

        survivor = MagicMock()
        survivor.name = "USS Enterprise"

        fleet_battle_adapter.update_from_battle_results([survivor])

        mock_ship_instance.update_from_ship.assert_called_once_with(survivor)

    def test_triggers_speed_recalculation(self, fleet_battle_adapter, mock_fleet, mock_ship_instance):
        """Speed is recalculated after battle."""
        mock_fleet.ships = [mock_ship_instance]

        fleet_battle_adapter.update_from_battle_results([])

        mock_fleet.trigger_speed_recalculation.assert_called_once()

    def test_handles_partial_losses(self, fleet_battle_adapter, mock_fleet):
        """Handles case where some ships survive, some don't."""
        ship1 = MagicMock()
        ship1.name = "Ship A"
        ship1.update_from_ship = MagicMock()

        ship2 = MagicMock()
        ship2.name = "Ship B"

        mock_fleet.ships = [ship1, ship2]

        # Only ship A survives
        survivor = MagicMock()
        survivor.name = "Ship A"

        fleet_battle_adapter.update_from_battle_results([survivor])

        # Only ship A should remain
        assert len(mock_fleet.ships) == 1
        assert mock_fleet.ships[0].name == "Ship A"


# =============================================================================
# Test: Edge Cases
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases."""

    def test_multiple_ships_different_names(self, fleet_battle_adapter, mock_fleet):
        """Multiple ships with different names handled correctly."""
        ships = []
        for i in range(5):
            ship = MagicMock()
            ship.name = f"Ship {i}"
            ship.is_combat_capable.return_value = True
            ship.to_ship.return_value = MagicMock()
            ships.append(ship)

        mock_fleet.ships = ships

        result = fleet_battle_adapter.to_battle_ships(team_id=0)

        assert len(result) == 5

    def test_mixed_combat_and_non_combat(self, fleet_battle_adapter, mock_fleet):
        """Mixed fleet with combat and non-combat ships."""
        combat_ship = MagicMock()
        combat_ship.name = "Warship"
        combat_ship.is_combat_capable.return_value = True
        combat_ship.to_ship.return_value = MagicMock()

        support_ship = MagicMock()
        support_ship.name = "Support"
        support_ship.is_combat_capable.return_value = False

        colony_ship = MagicMock()
        colony_ship.name = "Colony"
        colony_ship.is_combat_capable.return_value = False

        mock_fleet.ships = [combat_ship, support_ship, colony_ship]

        result = fleet_battle_adapter.to_battle_ships(team_id=0)

        # Only combat ship should be included
        assert len(result) == 1
