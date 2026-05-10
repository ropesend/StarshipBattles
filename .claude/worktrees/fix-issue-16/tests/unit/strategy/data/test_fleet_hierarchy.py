"""
Unit tests for fleet hierarchy system.

Phase 1: Data model for Fleet -> TaskForce -> Squadron hierarchy
with BattleRole enum, CombatPolicy, and FleetHierarchyNode base class.

TDD: These tests are written BEFORE the implementation exists.
"""

import pytest
from unittest.mock import MagicMock


# =============================================================================
# BattleRole Enum
# =============================================================================

class TestBattleRole:
    """Tests for BattleRole deployment zone enum."""

    def test_all_roles_exist(self):
        """BattleRole has all expected deployment roles."""
        from game.strategy.data.fleet_hierarchy import BattleRole

        assert hasattr(BattleRole, 'VANGUARD')
        assert hasattr(BattleRole, 'SCREEN')
        assert hasattr(BattleRole, 'MAIN_BODY')
        assert hasattr(BattleRole, 'FLANKER_LEFT')
        assert hasattr(BattleRole, 'FLANKER_RIGHT')
        assert hasattr(BattleRole, 'RESERVE')

    def test_roles_are_unique(self):
        """Each role has a distinct value."""
        from game.strategy.data.fleet_hierarchy import BattleRole

        values = [r.value for r in BattleRole]
        assert len(values) == len(set(values))

    def test_serialization_round_trip(self):
        """BattleRole can serialize to string and back."""
        from game.strategy.data.fleet_hierarchy import BattleRole

        for role in BattleRole:
            serialized = role.value
            restored = BattleRole(serialized)
            assert restored == role


# =============================================================================
# CombatPolicy Data Class
# =============================================================================

class TestCombatPolicy:
    """Tests for CombatPolicy — the 3 independent policy axes."""

    def test_default_policy_has_all_none(self):
        """A default CombatPolicy has None for all axes (inherit everything)."""
        from game.strategy.data.fleet_hierarchy import CombatPolicy

        policy = CombatPolicy()
        assert policy.targeting is None
        assert policy.movement is None
        assert policy.retreat is None

    def test_policy_with_values(self):
        """CombatPolicy can be created with specific axis values."""
        from game.strategy.data.fleet_hierarchy import CombatPolicy

        policy = CombatPolicy(
            targeting="focus_strongest",
            movement="advance",
            retreat="group_25",
        )
        assert policy.targeting == "focus_strongest"
        assert policy.movement == "advance"
        assert policy.retreat == "group_25"

    def test_policy_partial_values(self):
        """CombatPolicy can have some axes set and others None."""
        from game.strategy.data.fleet_hierarchy import CombatPolicy

        policy = CombatPolicy(targeting="anti_fighter")
        assert policy.targeting == "anti_fighter"
        assert policy.movement is None
        assert policy.retreat is None

    def test_policy_serialization_round_trip(self):
        """CombatPolicy serializes to dict and back."""
        from game.strategy.data.fleet_hierarchy import CombatPolicy

        original = CombatPolicy(
            targeting="focus_strongest",
            movement="hold_range",
            retreat="group_25",
        )
        data = original.to_dict()
        restored = CombatPolicy.from_dict(data)

        assert restored.targeting == original.targeting
        assert restored.movement == original.movement
        assert restored.retreat == original.retreat

    def test_policy_serialization_with_none_values(self):
        """CombatPolicy with None values omits them from dict."""
        from game.strategy.data.fleet_hierarchy import CombatPolicy

        policy = CombatPolicy(targeting="anti_fighter")
        data = policy.to_dict()

        # None values should not be present in serialized form
        assert "targeting" in data
        assert "movement" not in data
        assert "retreat" not in data

    def test_policy_deserialization_from_empty_dict(self):
        """CombatPolicy from empty dict gives all-None policy."""
        from game.strategy.data.fleet_hierarchy import CombatPolicy

        policy = CombatPolicy.from_dict({})
        assert policy.targeting is None
        assert policy.movement is None
        assert policy.retreat is None

    def test_policy_is_empty(self):
        """is_empty returns True when all axes are None."""
        from game.strategy.data.fleet_hierarchy import CombatPolicy

        assert CombatPolicy().is_empty
        assert not CombatPolicy(targeting="focus_strongest").is_empty

    def test_policy_resolve_with_parent(self):
        """resolve() fills None axes from parent policy."""
        from game.strategy.data.fleet_hierarchy import CombatPolicy

        parent = CombatPolicy(
            targeting="focus_strongest",
            movement="advance",
            retreat="group_25",
        )
        child = CombatPolicy(targeting="anti_fighter")

        resolved = child.resolve(parent)

        assert resolved.targeting == "anti_fighter"  # child override
        assert resolved.movement == "advance"  # inherited from parent
        assert resolved.retreat == "group_25"  # inherited from parent

    def test_policy_resolve_without_parent(self):
        """resolve() with no parent returns the policy unchanged."""
        from game.strategy.data.fleet_hierarchy import CombatPolicy

        policy = CombatPolicy(targeting="anti_fighter")
        resolved = policy.resolve(None)

        assert resolved.targeting == "anti_fighter"
        assert resolved.movement is None
        assert resolved.retreat is None

    def test_policy_resolve_child_fully_set_ignores_parent(self):
        """resolve() when child has all axes set ignores parent."""
        from game.strategy.data.fleet_hierarchy import CombatPolicy

        parent = CombatPolicy(
            targeting="distributed",
            movement="hold_position",
            retreat="never",
        )
        child = CombatPolicy(
            targeting="anti_fighter",
            movement="advance",
            retreat="group_50",
        )

        resolved = child.resolve(parent)

        assert resolved.targeting == "anti_fighter"
        assert resolved.movement == "advance"
        assert resolved.retreat == "group_50"


# =============================================================================
# FleetHierarchyNode Base Class
# =============================================================================

class TestFleetHierarchyNode:
    """Tests for FleetHierarchyNode — shared base for TaskForce and Squadron."""

    def _make_mock_ship(self, name="TestShip"):
        """Create a mock ShipInstance."""
        ship = MagicMock()
        ship.name = name
        ship.instance_id = f"id_{name}"
        ship.is_combat_capable.return_value = True
        ship.to_dict.return_value = {"name": name, "instance_id": f"id_{name}"}
        return ship

    def test_node_has_name_and_id(self):
        """A hierarchy node has a name and unique ID."""
        from game.strategy.data.fleet_hierarchy import FleetHierarchyNode

        node = FleetHierarchyNode(name="Test Group")
        assert node.name == "Test Group"
        assert node.node_id is not None
        assert len(node.node_id) > 0

    def test_node_has_policy(self):
        """A hierarchy node has a CombatPolicy."""
        from game.strategy.data.fleet_hierarchy import FleetHierarchyNode, CombatPolicy

        node = FleetHierarchyNode(name="Test")
        assert isinstance(node.policy, CombatPolicy)
        assert node.policy.is_empty  # default is all-None

    def test_node_has_battle_role(self):
        """A hierarchy node has an optional battle role."""
        from game.strategy.data.fleet_hierarchy import FleetHierarchyNode, BattleRole

        node = FleetHierarchyNode(name="Test")
        assert node.battle_role is None  # default

        node.battle_role = BattleRole.VANGUARD
        assert node.battle_role == BattleRole.VANGUARD

    def test_node_has_lone_ships(self):
        """A hierarchy node can hold lone ships directly."""
        from game.strategy.data.fleet_hierarchy import FleetHierarchyNode

        node = FleetHierarchyNode(name="Test")
        assert node.lone_ships == []

        ship = self._make_mock_ship()
        node.add_lone_ship(ship)
        assert ship in node.lone_ships

    def test_node_remove_lone_ship(self):
        """A hierarchy node can remove a lone ship."""
        from game.strategy.data.fleet_hierarchy import FleetHierarchyNode

        node = FleetHierarchyNode(name="Test")
        ship = self._make_mock_ship()
        node.add_lone_ship(ship)

        result = node.remove_lone_ship(ship)
        assert result is True
        assert ship not in node.lone_ships

    def test_node_remove_nonexistent_lone_ship(self):
        """Removing a ship not in the node returns False."""
        from game.strategy.data.fleet_hierarchy import FleetHierarchyNode

        node = FleetHierarchyNode(name="Test")
        ship = self._make_mock_ship()

        result = node.remove_lone_ship(ship)
        assert result is False

    def test_node_all_ships_returns_lone_ships(self):
        """all_ships includes lone ships."""
        from game.strategy.data.fleet_hierarchy import FleetHierarchyNode

        node = FleetHierarchyNode(name="Test")
        s1 = self._make_mock_ship("Ship1")
        s2 = self._make_mock_ship("Ship2")
        node.add_lone_ship(s1)
        node.add_lone_ship(s2)

        assert s1 in node.all_ships
        assert s2 in node.all_ships
        assert len(node.all_ships) == 2

    def test_node_flagship_id(self):
        """A hierarchy node can have a flagship designation."""
        from game.strategy.data.fleet_hierarchy import FleetHierarchyNode

        node = FleetHierarchyNode(name="Test")
        assert node.flagship_id is None

        node.flagship_id = "id_Flagship"
        assert node.flagship_id == "id_Flagship"

    def test_node_serialization_round_trip(self):
        """FleetHierarchyNode serializes to dict and back."""
        from game.strategy.data.fleet_hierarchy import (
            FleetHierarchyNode, CombatPolicy, BattleRole,
        )

        node = FleetHierarchyNode(
            name="Battle Line",
            node_id="test-id-123",
            policy=CombatPolicy(targeting="focus_strongest", movement="hold_range"),
            battle_role=BattleRole.MAIN_BODY,
            flagship_id="id_Flagship",
        )

        data = node.to_dict()
        restored = FleetHierarchyNode.from_dict(data)

        assert restored.name == "Battle Line"
        assert restored.node_id == "test-id-123"
        assert restored.policy.targeting == "focus_strongest"
        assert restored.policy.movement == "hold_range"
        assert restored.policy.retreat is None
        assert restored.battle_role == BattleRole.MAIN_BODY
        assert restored.flagship_id == "id_Flagship"


# =============================================================================
# Squadron
# =============================================================================

class TestSquadron:
    """Tests for Squadron — leaf organizational node containing ships."""

    def _make_mock_ship(self, name="TestShip"):
        ship = MagicMock()
        ship.name = name
        ship.instance_id = f"id_{name}"
        ship.is_combat_capable.return_value = True
        ship.to_dict.return_value = {"name": name, "instance_id": f"id_{name}"}
        return ship

    def test_squadron_creation(self):
        """Squadron can be created with a name."""
        from game.strategy.data.squadron import Squadron

        sq = Squadron(name="Escort Screen")
        assert sq.name == "Escort Screen"
        assert sq.ships == []

    def test_squadron_add_remove_ships(self):
        """Squadron supports add/remove ship operations."""
        from game.strategy.data.squadron import Squadron

        sq = Squadron(name="Test")
        s1 = self._make_mock_ship("Alpha")
        s2 = self._make_mock_ship("Beta")

        sq.add_ship(s1)
        sq.add_ship(s2)
        assert len(sq.ships) == 2

        sq.remove_ship(s1)
        assert len(sq.ships) == 1
        assert s2 in sq.ships

    def test_squadron_all_ships_includes_squadron_ships_and_lone_ships(self):
        """all_ships includes both squadron ships and lone ships."""
        from game.strategy.data.squadron import Squadron

        sq = Squadron(name="Test")
        s1 = self._make_mock_ship("Member")
        s2 = self._make_mock_ship("Lone")

        sq.add_ship(s1)
        sq.add_lone_ship(s2)

        all_ships = sq.all_ships
        assert s1 in all_ships
        assert s2 in all_ships
        assert len(all_ships) == 2

    def test_squadron_inherits_from_hierarchy_node(self):
        """Squadron inherits FleetHierarchyNode capabilities."""
        from game.strategy.data.squadron import Squadron
        from game.strategy.data.fleet_hierarchy import FleetHierarchyNode

        sq = Squadron(name="Test")
        assert isinstance(sq, FleetHierarchyNode)

    def test_squadron_serialization_round_trip(self):
        """Squadron serializes to dict and back."""
        from game.strategy.data.squadron import Squadron
        from game.strategy.data.fleet_hierarchy import CombatPolicy, BattleRole

        sq = Squadron(
            name="Escort Screen",
            policy=CombatPolicy(targeting="anti_fighter"),
            battle_role=BattleRole.SCREEN,
        )

        data = sq.to_dict()
        restored = Squadron.from_dict(data)

        assert restored.name == "Escort Screen"
        assert restored.policy.targeting == "anti_fighter"
        assert restored.battle_role == BattleRole.SCREEN

    def test_squadron_spatial_behavior(self):
        """Squadron can have a spatial behavior configuration."""
        from game.strategy.data.squadron import Squadron

        sq = Squadron(name="Test")
        assert sq.spatial_behavior is None  # default

        sq.spatial_behavior = "screen"
        assert sq.spatial_behavior == "screen"

    def test_squadron_spatial_behavior_params(self):
        """Squadron spatial behavior can have parameters."""
        from game.strategy.data.squadron import Squadron

        sq = Squadron(name="Test")
        sq.spatial_behavior = "screen"
        sq.spatial_behavior_params = {
            "anchor_type": "group",
            "anchor_id": "battle-line-id",
            "radius": 3000,
            "reactivity": "active",
        }

        assert sq.spatial_behavior_params["reactivity"] == "active"
        assert sq.spatial_behavior_params["radius"] == 3000


# =============================================================================
# TaskForce
# =============================================================================

class TestTaskForce:
    """Tests for TaskForce — mid-level node containing squadrons and lone ships."""

    def _make_mock_ship(self, name="TestShip"):
        ship = MagicMock()
        ship.name = name
        ship.instance_id = f"id_{name}"
        ship.is_combat_capable.return_value = True
        ship.to_dict.return_value = {"name": name, "instance_id": f"id_{name}"}
        return ship

    def test_task_force_creation(self):
        """TaskForce can be created with a name."""
        from game.strategy.data.task_force import TaskForce

        tf = TaskForce(name="Alpha Strike")
        assert tf.name == "Alpha Strike"
        assert tf.squadrons == []

    def test_task_force_add_remove_squadron(self):
        """TaskForce supports add/remove squadron operations."""
        from game.strategy.data.task_force import TaskForce
        from game.strategy.data.squadron import Squadron

        tf = TaskForce(name="Alpha")
        sq1 = Squadron(name="Battle Line")
        sq2 = Squadron(name="Screen")

        tf.add_squadron(sq1)
        tf.add_squadron(sq2)
        assert len(tf.squadrons) == 2

        tf.remove_squadron(sq1)
        assert len(tf.squadrons) == 1
        assert sq2 in tf.squadrons

    def test_task_force_all_ships_includes_squadron_ships(self):
        """all_ships includes ships from all squadrons."""
        from game.strategy.data.task_force import TaskForce
        from game.strategy.data.squadron import Squadron

        tf = TaskForce(name="Alpha")
        sq = Squadron(name="Battle Line")

        s1 = self._make_mock_ship("Ship1")
        s2 = self._make_mock_ship("Ship2")
        sq.add_ship(s1)
        sq.add_ship(s2)

        tf.add_squadron(sq)

        assert s1 in tf.all_ships
        assert s2 in tf.all_ships

    def test_task_force_all_ships_includes_lone_ships(self):
        """all_ships includes lone ships at the task force level."""
        from game.strategy.data.task_force import TaskForce
        from game.strategy.data.squadron import Squadron

        tf = TaskForce(name="Alpha")
        sq = Squadron(name="Battle Line")

        squad_ship = self._make_mock_ship("SquadShip")
        lone_ship = self._make_mock_ship("LoneShip")

        sq.add_ship(squad_ship)
        tf.add_squadron(sq)
        tf.add_lone_ship(lone_ship)

        all_ships = tf.all_ships
        assert squad_ship in all_ships
        assert lone_ship in all_ships
        assert len(all_ships) == 2

    def test_task_force_inherits_from_hierarchy_node(self):
        """TaskForce inherits FleetHierarchyNode capabilities."""
        from game.strategy.data.task_force import TaskForce
        from game.strategy.data.fleet_hierarchy import FleetHierarchyNode

        tf = TaskForce(name="Test")
        assert isinstance(tf, FleetHierarchyNode)

    def test_task_force_serialization_round_trip(self):
        """TaskForce with squadrons serializes and deserializes."""
        from game.strategy.data.task_force import TaskForce
        from game.strategy.data.squadron import Squadron
        from game.strategy.data.fleet_hierarchy import CombatPolicy, BattleRole

        tf = TaskForce(
            name="Alpha Strike",
            policy=CombatPolicy(targeting="focus_strongest", movement="advance"),
            battle_role=BattleRole.MAIN_BODY,
        )
        sq = Squadron(
            name="Escort Screen",
            policy=CombatPolicy(targeting="anti_fighter"),
            battle_role=BattleRole.SCREEN,
        )
        tf.add_squadron(sq)

        data = tf.to_dict()
        restored = TaskForce.from_dict(data)

        assert restored.name == "Alpha Strike"
        assert restored.policy.targeting == "focus_strongest"
        assert len(restored.squadrons) == 1
        assert restored.squadrons[0].name == "Escort Screen"
        assert restored.squadrons[0].policy.targeting == "anti_fighter"


# =============================================================================
# Policy Inheritance Across Hierarchy
# =============================================================================

class TestPolicyInheritance:
    """Tests for policy inheritance through the hierarchy."""

    def test_squadron_inherits_from_task_force(self):
        """Squadron resolves policies from its parent TaskForce."""
        from game.strategy.data.task_force import TaskForce
        from game.strategy.data.squadron import Squadron
        from game.strategy.data.fleet_hierarchy import CombatPolicy

        tf = TaskForce(
            name="Alpha",
            policy=CombatPolicy(
                targeting="focus_strongest",
                movement="advance",
                retreat="group_25",
            ),
        )
        sq = Squadron(
            name="Screen",
            policy=CombatPolicy(targeting="anti_fighter"),  # override targeting only
        )
        tf.add_squadron(sq)

        resolved = sq.resolve_effective_policy(parent_policy=tf.policy)

        assert resolved.targeting == "anti_fighter"  # overridden
        assert resolved.movement == "advance"  # inherited from TF
        assert resolved.retreat == "group_25"  # inherited from TF

    def test_lone_ship_inherits_parent_policy(self):
        """Lone ships at TF level use the TF's policy."""
        from game.strategy.data.task_force import TaskForce
        from game.strategy.data.fleet_hierarchy import CombatPolicy

        tf = TaskForce(
            name="Alpha",
            policy=CombatPolicy(
                targeting="focus_strongest",
                movement="advance",
                retreat="group_25",
            ),
        )

        # A lone ship at TF level resolves the TF's policy directly
        resolved = tf.policy.resolve(None)  # TF has no parent override
        assert resolved.targeting == "focus_strongest"
        assert resolved.movement == "advance"
        assert resolved.retreat == "group_25"

    def test_three_level_inheritance(self):
        """Policy resolves through Fleet -> TaskForce -> Squadron chain."""
        from game.strategy.data.fleet_hierarchy import CombatPolicy

        fleet_policy = CombatPolicy(retreat="group_25")
        tf_policy = CombatPolicy(targeting="focus_strongest", movement="advance")
        sq_policy = CombatPolicy(targeting="anti_fighter")

        # Resolve TF from Fleet
        tf_resolved = tf_policy.resolve(fleet_policy)
        assert tf_resolved.targeting == "focus_strongest"
        assert tf_resolved.movement == "advance"
        assert tf_resolved.retreat == "group_25"  # from fleet

        # Resolve Squadron from resolved TF
        sq_resolved = sq_policy.resolve(tf_resolved)
        assert sq_resolved.targeting == "anti_fighter"  # overridden by squadron
        assert sq_resolved.movement == "advance"  # from TF
        assert sq_resolved.retreat == "group_25"  # from fleet (through TF)

    def test_empty_child_inherits_everything(self):
        """A child with no policy overrides inherits everything."""
        from game.strategy.data.fleet_hierarchy import CombatPolicy

        parent = CombatPolicy(
            targeting="distributed",
            movement="hold_position",
            retreat="never",
        )
        child = CombatPolicy()

        resolved = child.resolve(parent)

        assert resolved.targeting == "distributed"
        assert resolved.movement == "hold_position"
        assert resolved.retreat == "never"


# =============================================================================
# Fleet Hierarchy Integration (Ships Property)
# =============================================================================

class TestFleetHierarchyIntegration:
    """Tests for Fleet.ships computed property with hierarchy backing."""

    def _make_mock_ship(self, name="TestShip"):
        ship = MagicMock()
        ship.name = name
        ship.instance_id = f"id_{name}"
        ship.is_combat_capable.return_value = True
        ship.to_dict.return_value = {"name": name, "instance_id": f"id_{name}"}
        return ship

    def test_fleet_with_no_groups_ships_returns_empty(self):
        """Fleet with no task forces has empty ships list."""
        from game.strategy.data.task_force import TaskForce
        from game.strategy.data.fleet_hierarchy import FleetHierarchyNode

        # Use FleetHierarchyNode as a stand-in for fleet-level testing
        # (actual Fleet integration will be in a separate test file)
        node = FleetHierarchyNode(name="Fleet")
        assert node.all_ships == []

    def test_complex_hierarchy_all_ships(self):
        """all_ships flattens a complex hierarchy correctly."""
        from game.strategy.data.task_force import TaskForce
        from game.strategy.data.squadron import Squadron

        # Build hierarchy:
        # TF "Alpha"
        #   Squadron "Battle Line" -> [s1, s2]
        #   Squadron "Screen" -> [s3]
        #   Lone ship: s4
        tf = TaskForce(name="Alpha")

        sq1 = Squadron(name="Battle Line")
        s1 = self._make_mock_ship("Ship1")
        s2 = self._make_mock_ship("Ship2")
        sq1.add_ship(s1)
        sq1.add_ship(s2)

        sq2 = Squadron(name="Screen")
        s3 = self._make_mock_ship("Ship3")
        sq2.add_ship(s3)

        s4 = self._make_mock_ship("Ship4")

        tf.add_squadron(sq1)
        tf.add_squadron(sq2)
        tf.add_lone_ship(s4)

        all_ships = tf.all_ships
        assert len(all_ships) == 4
        assert s1 in all_ships
        assert s2 in all_ships
        assert s3 in all_ships
        assert s4 in all_ships

    def test_empty_squadrons_dont_add_ships(self):
        """Empty squadrons don't contribute to all_ships."""
        from game.strategy.data.task_force import TaskForce
        from game.strategy.data.squadron import Squadron

        tf = TaskForce(name="Alpha")
        sq = Squadron(name="Empty")
        tf.add_squadron(sq)

        assert tf.all_ships == []

    def test_ships_order_is_deterministic(self):
        """all_ships returns ships in a consistent order."""
        from game.strategy.data.task_force import TaskForce
        from game.strategy.data.squadron import Squadron

        tf = TaskForce(name="Alpha")
        sq1 = Squadron(name="First")
        sq2 = Squadron(name="Second")

        s1 = self._make_mock_ship("Ship1")
        s2 = self._make_mock_ship("Ship2")
        s3 = self._make_mock_ship("Ship3")
        lone = self._make_mock_ship("Lone")

        sq1.add_ship(s1)
        sq2.add_ship(s2)
        sq2.add_ship(s3)

        tf.add_squadron(sq1)
        tf.add_squadron(sq2)
        tf.add_lone_ship(lone)

        # Order: squadron ships in squadron order, then lone ships
        all_ships = tf.all_ships
        assert all_ships == [s1, s2, s3, lone]

        # Calling again gives same order
        assert tf.all_ships == all_ships
