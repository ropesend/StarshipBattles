"""
Unit tests for Fleet hierarchy integration.

Tests that Fleet correctly integrates the TaskForce/Squadron hierarchy
as an organizational overlay while keeping fleet.ships as the canonical
flat list.

TDD: Written before modifying Fleet class.
"""

from unittest.mock import MagicMock

from game.core.hex_math import HexCoord


# =============================================================================
# Fixtures
# =============================================================================

def _make_mock_ship(name="TestShip", combat_capable=True):
    """Create a mock ShipInstance with enough stubs for Fleet operations."""
    ship = MagicMock()
    ship.name = name
    ship.instance_id = f"id_{name}"
    ship.is_combat_capable.return_value = combat_capable
    ship.vehicle_type = "Ship"
    ship.get_calculated_stats.return_value = {
        "mass": 1000,
        "strategic_movement": 100,
    }
    ship.to_dict.return_value = {
        "name": name,
        "instance_id": f"id_{name}",
        "design_data": {},
    }
    return ship


# =============================================================================
# Fleet Task Force Management
# =============================================================================

class TestFleetTaskForceManagement:
    """Tests for Fleet's task force container."""

    def test_fleet_has_task_forces_list(self):
        """Fleet has an accessible task_forces list."""
        from game.strategy.data.fleet import Fleet

        fleet = Fleet(1, 0, HexCoord(0, 0))
        assert fleet.task_forces == []

    def test_fleet_add_task_force(self):
        """Fleet can add task forces."""
        from game.strategy.data.fleet import Fleet
        from game.strategy.data.task_force import TaskForce

        fleet = Fleet(1, 0, HexCoord(0, 0))
        tf = TaskForce(name="Alpha")

        fleet.add_task_force(tf)
        assert tf in fleet.task_forces
        assert len(fleet.task_forces) == 1

    def test_fleet_remove_task_force(self):
        """Fleet can remove task forces."""
        from game.strategy.data.fleet import Fleet
        from game.strategy.data.task_force import TaskForce

        fleet = Fleet(1, 0, HexCoord(0, 0))
        tf = TaskForce(name="Alpha")
        fleet.add_task_force(tf)

        result = fleet.remove_task_force(tf)
        assert result is True
        assert tf not in fleet.task_forces

    def test_fleet_remove_nonexistent_task_force(self):
        """Removing a task force not in the fleet returns False."""
        from game.strategy.data.fleet import Fleet
        from game.strategy.data.task_force import TaskForce

        fleet = Fleet(1, 0, HexCoord(0, 0))
        tf = TaskForce(name="Alpha")

        result = fleet.remove_task_force(tf)
        assert result is False

    def test_fleet_has_fleet_level_policy(self):
        """Fleet has a CombatPolicy for fleet-level defaults."""
        from game.strategy.data.fleet import Fleet
        from game.strategy.data.fleet_hierarchy import CombatPolicy

        fleet = Fleet(1, 0, HexCoord(0, 0))
        assert isinstance(fleet.fleet_policy, CombatPolicy)
        assert fleet.fleet_policy.is_empty


# =============================================================================
# Fleet.ships Remains Canonical Flat List
# =============================================================================

class TestFleetShipsList:
    """Tests that fleet.ships remains the canonical flat list."""

    def test_ships_is_plain_list(self):
        """fleet.ships is a regular list, not a computed property."""
        from game.strategy.data.fleet import Fleet

        fleet = Fleet(1, 0, HexCoord(0, 0))
        assert isinstance(fleet.ships, list)

    def test_add_ship_works_as_before(self):
        """add_ship() adds to fleet.ships."""
        from game.strategy.data.fleet import Fleet

        fleet = Fleet(1, 0, HexCoord(0, 0))
        ship = _make_mock_ship("Ship1")

        fleet.add_ship(ship)
        assert ship in fleet.ships
        assert len(fleet.ships) == 1

    def test_remove_ship_works_as_before(self):
        """remove_ship() removes from fleet.ships."""
        from game.strategy.data.fleet import Fleet

        fleet = Fleet(1, 0, HexCoord(0, 0))
        ship = _make_mock_ship("Ship1")

        fleet.add_ship(ship)
        result = fleet.remove_ship(ship)

        assert result is True
        assert ship not in fleet.ships

    def test_ships_append_works(self):
        """Direct fleet.ships.append() still works."""
        from game.strategy.data.fleet import Fleet

        fleet = Fleet(1, 0, HexCoord(0, 0))
        ship = _make_mock_ship("Ship1")

        fleet.ships.append(ship)
        assert ship in fleet.ships


# =============================================================================
# Unassigned Ships
# =============================================================================

class TestUnassignedShips:
    """Tests for get_unassigned_ships() which finds ships not in hierarchy."""

    def test_all_ships_unassigned_when_no_task_forces(self):
        """All ships are unassigned when fleet has no task forces."""
        from game.strategy.data.fleet import Fleet

        fleet = Fleet(1, 0, HexCoord(0, 0))
        s1 = _make_mock_ship("Ship1")
        s2 = _make_mock_ship("Ship2")
        fleet.add_ship(s1)
        fleet.add_ship(s2)

        unassigned = fleet.get_unassigned_ships()
        assert s1 in unassigned
        assert s2 in unassigned
        assert len(unassigned) == 2

    def test_assigned_ships_excluded(self):
        """Ships in a task force are not returned by get_unassigned_ships()."""
        from game.strategy.data.fleet import Fleet
        from game.strategy.data.task_force import TaskForce
        from game.strategy.data.squadron import Squadron

        fleet = Fleet(1, 0, HexCoord(0, 0))
        assigned = _make_mock_ship("Assigned")
        unassigned = _make_mock_ship("Unassigned")

        fleet.add_ship(assigned)
        fleet.add_ship(unassigned)

        tf = TaskForce(name="Alpha")
        sq = Squadron(name="Line")
        sq.add_ship(assigned)  # same mock as in fleet.ships
        tf.add_squadron(sq)
        fleet.add_task_force(tf)

        result = fleet.get_unassigned_ships()
        assert unassigned in result
        assert assigned not in result


# =============================================================================
# Serialization with Hierarchy
# =============================================================================

class TestFleetHierarchySerialization:
    """Tests for Fleet serialization with task forces."""

    def test_fleet_to_dict_includes_task_forces(self):
        """Fleet.to_dict() serializes task forces."""
        from game.strategy.data.fleet import Fleet
        from game.strategy.data.task_force import TaskForce
        from game.strategy.data.fleet_hierarchy import CombatPolicy, BattleRole

        fleet = Fleet(1, 0, HexCoord(0, 0))
        tf = TaskForce(
            name="Alpha",
            policy=CombatPolicy(targeting="focus_strongest"),
            battle_role=BattleRole.MAIN_BODY,
        )
        fleet.add_task_force(tf)

        data = fleet.to_dict()

        assert "task_forces" in data
        assert len(data["task_forces"]) == 1
        assert data["task_forces"][0]["name"] == "Alpha"

    def test_fleet_to_dict_includes_fleet_policy(self):
        """Fleet.to_dict() serializes fleet-level policy."""
        from game.strategy.data.fleet import Fleet
        from game.strategy.data.fleet_hierarchy import CombatPolicy

        fleet = Fleet(1, 0, HexCoord(0, 0))
        fleet.fleet_policy = CombatPolicy(retreat="group_25")

        data = fleet.to_dict()
        assert "fleet_policy" in data
        assert data["fleet_policy"]["retreat"] == "group_25"

    def test_fleet_to_dict_omits_empty_hierarchy(self):
        """Fleet.to_dict() omits task_forces when empty."""
        from game.strategy.data.fleet import Fleet

        fleet = Fleet(1, 0, HexCoord(0, 0))
        data = fleet.to_dict()

        assert "task_forces" not in data

    def test_fleet_from_dict_without_hierarchy_works(self):
        """Fleet.from_dict() without task_forces field works (backward compat)."""
        from game.strategy.data.fleet import Fleet

        data = {
            "id": 1,
            "owner_id": 0,
            "location": {"q": 0, "r": 0},
            "speed": 5.0,
            "ships": [],
            "orders": [],
            "path": [],
            "construction_queue": [],
        }

        fleet = Fleet.from_dict(data)
        assert fleet.task_forces == []
        assert fleet.ships == []

    def test_fleet_from_dict_with_task_forces(self):
        """Fleet.from_dict() restores task forces."""
        from game.strategy.data.fleet import Fleet

        data = {
            "id": 1,
            "owner_id": 0,
            "location": {"q": 0, "r": 0},
            "speed": 5.0,
            "ships": [],
            "orders": [],
            "path": [],
            "construction_queue": [],
            "task_forces": [
                {
                    "name": "Alpha",
                    "node_id": "tf-1",
                    "type": "task_force",
                    "policy": {"targeting": "focus_strongest"},
                    "battle_role": "main_body",
                    "squadrons": [
                        {
                            "name": "Battle Line",
                            "node_id": "sq-1",
                            "type": "squadron",
                            "policy": {"targeting": "anti_fighter"},
                        }
                    ],
                }
            ],
            "fleet_policy": {"retreat": "group_25"},
        }

        fleet = Fleet.from_dict(data)

        assert len(fleet.task_forces) == 1
        assert fleet.task_forces[0].name == "Alpha"
        assert fleet.task_forces[0].policy.targeting == "focus_strongest"
        assert len(fleet.task_forces[0].squadrons) == 1
        assert fleet.task_forces[0].squadrons[0].name == "Battle Line"
        assert fleet.fleet_policy.retreat == "group_25"

    def test_merge_clears_task_forces(self):
        """merge_with() clears task forces on the source fleet."""
        from game.strategy.data.fleet import Fleet
        from game.strategy.data.task_force import TaskForce

        fleet1 = Fleet(1, 0, HexCoord(0, 0))
        fleet2 = Fleet(2, 0, HexCoord(0, 0))

        tf = TaskForce(name="Alpha")
        fleet1.add_task_force(tf)

        ship = _make_mock_ship("Ship1")
        fleet1.add_ship(ship)

        fleet1.merge_with(fleet2)

        assert fleet1.task_forces == []
        assert ship in fleet2.ships
