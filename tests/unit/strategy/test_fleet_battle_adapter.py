"""Tests for FleetBattleAdapter.

PROJ-87 Phase 4: Extracted battle conversion logic from Fleet class.
"""

import pytest
from unittest.mock import MagicMock, patch


def make_ship_instance(name: str, design_data: dict = None, registries=None):
    """Helper to create ShipInstance with required fields.

    PROJ-211: Added registries parameter for DI compliance.
    Required when ship is added to fleet (triggers speed calc).
    """
    from game.strategy.data.ship_instance import ShipInstance
    ship = ShipInstance(
        instance_id=f"test-{name}",
        design_id=f"design-{name}",
        name=name,
        owner_id=0,
        design_data=design_data or {}
    )
    if registries is not None:
        ship._registries = registries
    return ship


class TestFleetBattleAdapter:
    """Tests for FleetBattleAdapter."""

    def test_default_formation_positions_team_0(self):
        """Team 0 formations start on left side."""
        from game.strategy.data.fleet_battle_adapter import FleetBattleAdapter
        from game.strategy.data.fleet import Fleet
        from game.core.hex_math import HexCoord

        fleet = Fleet(1, 0, HexCoord(0, 0))
        adapter = FleetBattleAdapter(fleet)

        positions = adapter._default_formation_positions(3, team_id=0)

        assert len(positions) == 3
        # Team 0 base_x = 20000
        for pos in positions:
            assert pos[0] == 20000

    def test_default_formation_positions_team_1(self):
        """Team 1 formations start on right side."""
        from game.strategy.data.fleet_battle_adapter import FleetBattleAdapter
        from game.strategy.data.fleet import Fleet
        from game.core.hex_math import HexCoord

        fleet = Fleet(1, 0, HexCoord(0, 0))
        adapter = FleetBattleAdapter(fleet)

        positions = adapter._default_formation_positions(3, team_id=1)

        assert len(positions) == 3
        # Team 1 base_x = 80000
        for pos in positions:
            assert pos[0] == 80000

    def test_default_formation_positions_spacing(self):
        """Ships are spaced vertically."""
        from game.strategy.data.fleet_battle_adapter import FleetBattleAdapter
        from game.strategy.data.fleet import Fleet
        from game.core.hex_math import HexCoord

        fleet = Fleet(1, 0, HexCoord(0, 0))
        adapter = FleetBattleAdapter(fleet)

        positions = adapter._default_formation_positions(3, team_id=0)

        # Verify spacing between ships
        y_values = [p[1] for p in positions]
        assert len(set(y_values)) == 3  # All different y values

    def test_to_battle_ships_empty_fleet(self):
        """Empty fleet returns empty list."""
        from game.strategy.data.fleet_battle_adapter import FleetBattleAdapter
        from game.strategy.data.fleet import Fleet
        from game.core.hex_math import HexCoord

        fleet = Fleet(1, 0, HexCoord(0, 0))
        adapter = FleetBattleAdapter(fleet)

        ships = adapter.to_battle_ships(team_id=0)
        assert ships == []

    def test_to_battle_ships_converts_instances(self, fresh_registries):
        """Combat-capable ships are converted."""
        from game.strategy.data.fleet_battle_adapter import FleetBattleAdapter
        from game.strategy.data.fleet import Fleet
        from game.core.hex_math import HexCoord

        fleet = Fleet(1, 0, HexCoord(0, 0))
        # PROJ-211: Pass registries for DI compliance (add_ship triggers speed calc)
        ship = make_ship_instance(name="Cruiser", design_data={}, registries=fresh_registries)
        fleet.add_ship(ship)
        adapter = FleetBattleAdapter(fleet)

        with patch.object(ship, 'to_ship') as mock_to_ship:
            mock_battle_ship = MagicMock()
            mock_to_ship.return_value = mock_battle_ship

            result = adapter.to_battle_ships(team_id=0)

            assert len(result) == 1
            assert result[0] == mock_battle_ship
            mock_to_ship.assert_called_once()

    def test_to_battle_ships_skips_non_combat(self, fresh_registries):
        """Non-combat ships are skipped."""
        from game.strategy.data.fleet_battle_adapter import FleetBattleAdapter
        from game.strategy.data.fleet import Fleet
        from game.core.hex_math import HexCoord

        fleet = Fleet(1, 0, HexCoord(0, 0))
        # PROJ-211: Pass registries for DI compliance (add_ship triggers speed calc)
        ship = make_ship_instance(name="Cruiser", design_data={}, registries=fresh_registries)
        fleet.add_ship(ship)
        adapter = FleetBattleAdapter(fleet)

        with patch.object(ship, 'is_combat_capable', return_value=False):
            result = adapter.to_battle_ships(team_id=0)
            assert result == []

    def test_to_battle_ships_custom_positions(self, fresh_registries):
        """Custom formation positions are used when provided."""
        from game.strategy.data.fleet_battle_adapter import FleetBattleAdapter
        from game.strategy.data.fleet import Fleet
        from game.core.hex_math import HexCoord

        fleet = Fleet(1, 0, HexCoord(0, 0))
        # PROJ-211: Pass registries for DI compliance (add_ship triggers speed calc)
        ship = make_ship_instance(name="Cruiser", design_data={}, registries=fresh_registries)
        fleet.add_ship(ship)
        adapter = FleetBattleAdapter(fleet)

        custom_positions = [(100, 200)]

        with patch.object(ship, 'to_ship') as mock_to_ship:
            mock_battle_ship = MagicMock()
            mock_to_ship.return_value = mock_battle_ship

            adapter.to_battle_ships(team_id=0, formation_positions=custom_positions)

            # Check position was passed
            call_args = mock_to_ship.call_args
            assert call_args[0][0] == (100, 200)

    def test_to_battle_ships_passes_registries(self, fresh_registries):
        """Registries are passed to ship conversion."""
        from game.strategy.data.fleet_battle_adapter import FleetBattleAdapter
        from game.strategy.data.fleet import Fleet
        from game.core.hex_math import HexCoord

        fleet = Fleet(1, 0, HexCoord(0, 0))
        # PROJ-211: Pass registries for DI compliance (add_ship triggers speed calc)
        ship = make_ship_instance(name="Cruiser", design_data={}, registries=fresh_registries)
        fleet.add_ship(ship)
        adapter = FleetBattleAdapter(fleet)

        mock_registries = MagicMock()

        with patch.object(ship, 'to_ship') as mock_to_ship:
            mock_battle_ship = MagicMock()
            mock_to_ship.return_value = mock_battle_ship

            adapter.to_battle_ships(team_id=0, registries=mock_registries)

            # Check registries was passed as keyword arg
            call_kwargs = mock_to_ship.call_args[1]
            assert call_kwargs.get('registries') is mock_registries

    def test_update_from_battle_results_survivors(self, fresh_registries):
        """Survivors are kept and updated."""
        from game.strategy.data.fleet_battle_adapter import FleetBattleAdapter
        from game.strategy.data.fleet import Fleet
        from game.core.hex_math import HexCoord

        fleet = Fleet(1, 0, HexCoord(0, 0))
        # PROJ-211: Pass registries for DI compliance (add_ship triggers speed calc)
        ship1 = make_ship_instance(name="Survivor", design_data={}, registries=fresh_registries)
        ship2 = make_ship_instance(name="Destroyed", design_data={}, registries=fresh_registries)
        fleet.add_ship(ship1)
        fleet.add_ship(ship2)
        adapter = FleetBattleAdapter(fleet)

        # Only ship1 survives — PROJ-254: match by instance_id
        survivor_sim = MagicMock()
        survivor_sim.name = "Survivor"
        survivor_sim.instance_id = ship1.instance_id

        with patch.object(ship1, 'update_from_ship') as mock_update:
            adapter.update_from_battle_results([survivor_sim])

            # Ship1 should be updated
            mock_update.assert_called_once_with(survivor_sim)

            # Only survivor remains
            assert len(fleet.ships) == 1
            assert fleet.ships[0].name == "Survivor"

    def test_update_from_battle_results_all_destroyed(self, fresh_registries):
        """All ships destroyed leaves empty fleet."""
        from game.strategy.data.fleet_battle_adapter import FleetBattleAdapter
        from game.strategy.data.fleet import Fleet
        from game.core.hex_math import HexCoord

        fleet = Fleet(1, 0, HexCoord(0, 0))
        # PROJ-211: Pass registries for DI compliance (add_ship triggers speed calc)
        ship = make_ship_instance(name="Victim", design_data={}, registries=fresh_registries)
        fleet.add_ship(ship)
        adapter = FleetBattleAdapter(fleet)

        adapter.update_from_battle_results([])

        assert len(fleet.ships) == 0

    def test_update_from_battle_results_triggers_speed_recalc(self, fresh_registries):
        """Speed is recalculated after battle."""
        from game.strategy.data.fleet_battle_adapter import FleetBattleAdapter
        from game.strategy.data.fleet import Fleet
        from game.core.hex_math import HexCoord

        fleet = Fleet(1, 0, HexCoord(0, 0))
        # PROJ-211: Pass registries for DI compliance (add_ship triggers speed calc)
        ship = make_ship_instance(name="Ship", design_data={}, registries=fresh_registries)
        fleet.add_ship(ship)
        adapter = FleetBattleAdapter(fleet)

        with patch.object(fleet, 'trigger_speed_recalculation') as mock_recalc:
            adapter.update_from_battle_results([])
            mock_recalc.assert_called_once()


class TestFleetBattleAdapterDelegation:
    """Test that Fleet properly delegates to FleetBattleAdapter."""

    def test_fleet_to_battle_ships_delegates(self):
        """Fleet.battle.to_battle_ships delegates to adapter."""
        from game.strategy.data.fleet import Fleet
        from game.core.hex_math import HexCoord

        fleet = Fleet(1, 0, HexCoord(0, 0))
        # Empty fleet should work - use fleet.battle.to_battle_ships (PROJ-210)
        result = fleet.battle.to_battle_ships(team_id=0)
        assert result == []

    def test_fleet_update_from_battle_results_delegates(self, fresh_registries):
        """Fleet.battle.update_from_battle_results delegates to adapter."""
        from game.strategy.data.fleet import Fleet
        from game.core.hex_math import HexCoord

        fleet = Fleet(1, 0, HexCoord(0, 0))
        # PROJ-211: Pass registries for DI compliance (add_ship triggers speed calc)
        ship = make_ship_instance(name="Ship", design_data={}, registries=fresh_registries)
        fleet.add_ship(ship)

        # Simulate battle with no survivors - use fleet.battle.* (PROJ-210)
        fleet.battle.update_from_battle_results([])
        assert len(fleet.ships) == 0
