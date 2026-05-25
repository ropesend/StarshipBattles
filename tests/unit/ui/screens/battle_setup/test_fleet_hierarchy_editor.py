"""PROJ-282 Phase 7: `FleetHierarchyEditor` tests.

The editor is a stateless helper that owns fleet/TaskForce/Squadron CRUD
and ship-cloning. Extracted from `BattleSetupController` to kill the
duplicated clone-and-reparent logic between `duplicate_task_force` and
`duplicate_squadron`.
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest


def _make_real_fleet():
    from game.core.hex_math import HexCoord
    from game.strategy.data.fleet import Fleet
    return Fleet(1, 0, HexCoord(0, 0))


def _make_ship(name="Scout"):
    """Mock a ShipInstance with just enough to survive Fleet.add_ship's
    speed recalculation AND the editor's clone call."""
    ship = MagicMock()
    ship.instance_id = f"ship-{name}"
    ship.name = name
    ship.owner_id = 0
    ship.design_data = {"name": name, "ship_class": "Escort"}
    ship.design_id = "test_design"
    ship.is_combat_capable.return_value = True
    ship.vehicle_type = "Ship"
    ship.get_calculated_stats.return_value = {"mass": 1000, "strategic_movement": 100}
    return ship


class TestCreateTaskForce:
    def test_appends_empty_tf_to_fleet(self):
        from game.ui.screens.battle_setup.fleet_hierarchy_editor import (
            FleetHierarchyEditor,
        )
        fleet = _make_real_fleet()
        tf = FleetHierarchyEditor.create_task_force(fleet, "TF-Alpha")
        assert tf in fleet.task_forces
        assert tf.name == "TF-Alpha"
        assert len(tf.squadrons) == 0
        assert len(tf.lone_ships) == 0

    def test_default_name_based_on_count(self):
        from game.ui.screens.battle_setup.fleet_hierarchy_editor import (
            FleetHierarchyEditor,
        )
        fleet = _make_real_fleet()
        FleetHierarchyEditor.create_task_force(fleet)
        tf2 = FleetHierarchyEditor.create_task_force(fleet)
        assert tf2.name == "Task Force 2"


class TestCreateSquadron:
    def test_appends_sq_to_tf(self):
        from game.ui.screens.battle_setup.fleet_hierarchy_editor import (
            FleetHierarchyEditor,
        )
        fleet = _make_real_fleet()
        tf = FleetHierarchyEditor.create_task_force(fleet, "TF-1")
        sq = FleetHierarchyEditor.create_squadron(tf, "Alpha Squadron")
        assert sq in tf.squadrons
        assert sq.name == "Alpha Squadron"

    def test_default_name_based_on_count(self):
        from game.ui.screens.battle_setup.fleet_hierarchy_editor import (
            FleetHierarchyEditor,
        )
        fleet = _make_real_fleet()
        tf = FleetHierarchyEditor.create_task_force(fleet, "TF-1")
        FleetHierarchyEditor.create_squadron(tf)
        sq2 = FleetHierarchyEditor.create_squadron(tf)
        assert sq2.name == "Squadron 2"


class TestCloneShip:
    def test_clone_ship_returns_clone_with_matching_attributes(self, fresh_registries):
        """The cloned ship's observable attributes should mirror the
        original's design_data, owner_id, and name.

        PROJ-322 Task 3.16 (S01-CAT6-002): rewritten to assert on the
        cloned ship's attributes instead of mocking
        `ShipInstance.create` and asserting on the kwargs.
        """
        from game.ui.screens.battle_setup.fleet_hierarchy_editor import (
            FleetHierarchyEditor,
        )
        original = _make_ship("Original")
        original._registries = fresh_registries

        clone = FleetHierarchyEditor._clone_ship(original, registries=fresh_registries)

        assert clone is not None
        assert clone.design_data is original.design_data
        assert clone.owner_id == original.owner_id
        assert clone.name == original.name


class TestDuplicateSquadron:
    def test_duplicate_squadron_creates_new_sq_with_cloned_ships(self):
        from game.ui.screens.battle_setup.fleet_hierarchy_editor import (
            FleetHierarchyEditor,
        )
        from game.strategy.data.squadron import Squadron

        fleet = _make_real_fleet()
        tf = FleetHierarchyEditor.create_task_force(fleet, "TF")
        original_sq = Squadron(name="Original")
        tf.add_squadron(original_sq)
        ship1 = _make_ship("A")
        ship2 = _make_ship("B")
        original_sq.add_ship(ship1)
        original_sq.add_ship(ship2)
        fleet.add_ship(ship1)
        fleet.add_ship(ship2)

        with pytest.MonkeyPatch.context() as mp:
            from game.strategy.data import ship_instance
            mp.setattr(
                ship_instance.ShipInstance,
                "create",
                lambda **kwargs: _make_ship(f"clone-{kwargs['name']}"),
            )
            new_sq = FleetHierarchyEditor.duplicate_squadron(fleet, tf, original_sq)

        assert new_sq is not original_sq
        assert new_sq.name == "Original (Copy)"
        assert len(new_sq.ships) == 2
        # Both cloned ships also in the fleet master list
        assert len(fleet.ships) == 4  # 2 original + 2 cloned

    def test_duplicate_squadron_copies_policy_and_battle_role(self):
        from game.ui.screens.battle_setup.fleet_hierarchy_editor import (
            FleetHierarchyEditor,
        )
        from game.strategy.data.fleet_hierarchy import BattleRole, CombatPolicy
        from game.strategy.data.squadron import Squadron

        fleet = _make_real_fleet()
        tf = FleetHierarchyEditor.create_task_force(fleet, "TF")
        policy = CombatPolicy(targeting="focus_strongest", movement="advance")
        original_sq = Squadron(
            name="Original", policy=policy, battle_role=BattleRole.VANGUARD
        )
        tf.add_squadron(original_sq)

        new_sq = FleetHierarchyEditor.duplicate_squadron(fleet, tf, original_sq)

        assert new_sq.policy.targeting == "focus_strongest"
        assert new_sq.policy.movement == "advance"
        assert new_sq.battle_role == BattleRole.VANGUARD


class TestDuplicateTaskForce:
    def test_duplicate_task_force_copies_squadrons_and_lone_ships(self):
        from game.ui.screens.battle_setup.fleet_hierarchy_editor import (
            FleetHierarchyEditor,
        )
        from game.strategy.data.squadron import Squadron

        fleet = _make_real_fleet()
        tf = FleetHierarchyEditor.create_task_force(fleet, "TF-Original")
        sq = Squadron(name="SQ-1")
        tf.add_squadron(sq)
        ship_in_sq = _make_ship("SqShip")
        ship_lone = _make_ship("LoneShip")
        sq.add_ship(ship_in_sq)
        tf.add_lone_ship(ship_lone)
        fleet.add_ship(ship_in_sq)
        fleet.add_ship(ship_lone)

        with pytest.MonkeyPatch.context() as mp:
            from game.strategy.data import ship_instance
            mp.setattr(
                ship_instance.ShipInstance,
                "create",
                lambda **kwargs: _make_ship(f"clone-{kwargs['name']}"),
            )
            new_tf = FleetHierarchyEditor.duplicate_task_force(fleet, tf)

        assert new_tf is not tf
        assert new_tf.name == "TF-Original (Copy)"
        assert len(new_tf.squadrons) == 1
        assert len(new_tf.squadrons[0].ships) == 1  # Cloned ship in SQ
        assert len(new_tf.lone_ships) == 1  # Cloned lone ship
        assert len(fleet.ships) == 4  # 2 original + 2 cloned


class TestDeleteOperations:
    def test_delete_task_force_removes_tf_and_all_its_ships_from_fleet(self):
        from game.ui.screens.battle_setup.fleet_hierarchy_editor import (
            FleetHierarchyEditor,
        )
        from game.strategy.data.squadron import Squadron

        fleet = _make_real_fleet()
        tf = FleetHierarchyEditor.create_task_force(fleet, "TF")
        sq = Squadron(name="SQ")
        tf.add_squadron(sq)
        ship = _make_ship("X")
        sq.add_ship(ship)
        fleet.add_ship(ship)

        FleetHierarchyEditor.delete_task_force(fleet, tf)

        assert tf not in fleet.task_forces
        assert ship not in fleet.ships

    def test_delete_squadron_removes_sq_and_its_ships_from_fleet(self):
        from game.ui.screens.battle_setup.fleet_hierarchy_editor import (
            FleetHierarchyEditor,
        )
        from game.strategy.data.squadron import Squadron

        fleet = _make_real_fleet()
        tf = FleetHierarchyEditor.create_task_force(fleet, "TF")
        sq = Squadron(name="SQ")
        tf.add_squadron(sq)
        ship = _make_ship("X")
        sq.add_ship(ship)
        fleet.add_ship(ship)

        FleetHierarchyEditor.delete_squadron(fleet, tf, sq)

        assert sq not in tf.squadrons
        assert ship not in fleet.ships


