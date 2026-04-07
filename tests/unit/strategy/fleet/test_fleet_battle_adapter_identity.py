"""
Tests for ship identity matching in FleetBattleAdapter (PROJ-254 Phase 2).

Verifies that battle survivor matching uses instance_id, not name.
"""
from unittest.mock import Mock, MagicMock
from game.strategy.data.fleet_battle_adapter import FleetBattleAdapter


def _mock_fleet_with_ships(ship_names, instance_ids=None):
    """Create a mock fleet with ShipInstance objects."""
    fleet = Mock()
    fleet.ships = []
    for i, name in enumerate(ship_names):
        ship = Mock()
        ship.name = name
        ship.instance_id = instance_ids[i] if instance_ids else f"id_{i}"
        ship.update_from_ship = Mock()
        fleet.ships.append(ship)
    fleet.trigger_speed_recalculation = Mock()
    return fleet


def _mock_survivor(name, instance_id):
    """Create a mock IPostBattleShip survivor."""
    survivor = Mock()
    survivor.name = name
    survivor.instance_id = instance_id
    return survivor


class TestFleetBattleAdapterIdentity:
    """FleetBattleAdapter should match survivors by instance_id."""

    def test_matching_by_instance_id_not_name(self):
        """Two ships with same name but different IDs should be matched correctly."""
        fleet = _mock_fleet_with_ships(
            ["Fighter", "Fighter"],
            ["id_a", "id_b"]
        )
        adapter = FleetBattleAdapter(fleet)

        # Only id_b survived
        survivors = [_mock_survivor("Fighter", "id_b")]

        adapter.update_from_battle_results(survivors)

        # id_a should be removed (destroyed), id_b should remain
        assert len(fleet.ships) == 1
        assert fleet.ships[0].instance_id == "id_b"
        fleet.ships[0].update_from_ship.assert_called_once()

    def test_unique_names_still_work(self):
        """Standard case: unique names with IDs should still work."""
        fleet = _mock_fleet_with_ships(
            ["Alpha", "Bravo"],
            ["id_1", "id_2"]
        )
        adapter = FleetBattleAdapter(fleet)

        survivors = [_mock_survivor("Alpha", "id_1")]

        adapter.update_from_battle_results(survivors)

        assert len(fleet.ships) == 1
        assert fleet.ships[0].name == "Alpha"

    def test_no_survivors_empties_fleet(self):
        """No survivors means all ships destroyed."""
        fleet = _mock_fleet_with_ships(["Ship1"], ["id_1"])
        adapter = FleetBattleAdapter(fleet)

        adapter.update_from_battle_results([])

        assert len(fleet.ships) == 0
