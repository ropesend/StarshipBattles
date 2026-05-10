"""
Unit tests for group policy registry.

Phase 3: Group-level policy presets for targeting, movement, and retreat.
Each axis is independent and inheritable through the fleet hierarchy.

TDD: Written before implementation.
"""

import pytest


# =============================================================================
# GroupPolicyRegistry Loading
# =============================================================================

class TestGroupPolicyRegistryLoading:
    """Tests for loading group policies from JSON."""

    def test_registry_loads_from_data_file(self):
        """GroupPolicyRegistry loads from data/group_policies.json."""
        from game.strategy.data.group_policy_registry import GroupPolicyRegistry

        registry = GroupPolicyRegistry()
        registry.load()

        assert len(registry.targeting_policies) > 0
        assert len(registry.movement_policies) > 0
        assert len(registry.retreat_policies) > 0

    @pytest.mark.parametrize('axis', ['targeting', 'movement', 'retreat'])
    def test_policy_registry_structural_invariants(self, axis):
        """Each policy axis loads at least one policy and every entry is
        addressable via its public ``get_<axis>(policy_id)`` accessor.

        PROJ-322 Task 1.11 (S06-CAT4-002): the previous three tests
        hardcoded the seven-element list per axis, forcing test edits
        every time a policy was added. This drives the registry's
        public surface and asserts structural invariants instead.
        """
        from game.strategy.data.group_policy_registry import GroupPolicyRegistry

        registry = GroupPolicyRegistry()
        registry.load()

        policies = getattr(registry, f'{axis}_policies')
        getter = getattr(registry, f'get_{axis}')
        validator = getattr(registry, f'is_valid_{axis}')

        assert len(policies) > 0, f"No {axis} policies loaded"
        for policy_id in policies:
            data = getter(policy_id)
            assert data is not None, f"{axis} policy {policy_id} not retrievable"
            assert isinstance(data, dict)
            assert validator(policy_id)


# =============================================================================
# Policy Validation
# =============================================================================

class TestPolicyValidation:
    """Tests for validating policy IDs against the registry."""

    def test_valid_targeting_policy(self):
        """is_valid_targeting returns True for known policies."""
        from game.strategy.data.group_policy_registry import GroupPolicyRegistry

        registry = GroupPolicyRegistry()
        registry.load()

        assert registry.is_valid_targeting("focus_strongest")
        assert registry.is_valid_targeting("anti_fighter")

    def test_invalid_targeting_policy(self):
        """is_valid_targeting returns False for unknown policies."""
        from game.strategy.data.group_policy_registry import GroupPolicyRegistry

        registry = GroupPolicyRegistry()
        registry.load()

        assert not registry.is_valid_targeting("nonexistent")

    def test_valid_movement_policy(self):
        """is_valid_movement returns True for known policies."""
        from game.strategy.data.group_policy_registry import GroupPolicyRegistry

        registry = GroupPolicyRegistry()
        registry.load()

        assert registry.is_valid_movement("advance")
        assert registry.is_valid_movement("hold_range")

    def test_invalid_movement_policy(self):
        """is_valid_movement returns False for unknown policies."""
        from game.strategy.data.group_policy_registry import GroupPolicyRegistry

        registry = GroupPolicyRegistry()
        registry.load()

        assert not registry.is_valid_movement("nonexistent")

    def test_valid_retreat_policy(self):
        """is_valid_retreat returns True for known policies."""
        from game.strategy.data.group_policy_registry import GroupPolicyRegistry

        registry = GroupPolicyRegistry()
        registry.load()

        assert registry.is_valid_retreat("group_25")
        assert registry.is_valid_retreat("never")

    def test_invalid_retreat_policy(self):
        """is_valid_retreat returns False for unknown policies."""
        from game.strategy.data.group_policy_registry import GroupPolicyRegistry

        registry = GroupPolicyRegistry()
        registry.load()

        assert not registry.is_valid_retreat("nonexistent")

    def test_validate_combat_policy_all_valid(self):
        """validate_policy returns empty list for fully valid policy."""
        from game.strategy.data.group_policy_registry import GroupPolicyRegistry
        from game.strategy.data.fleet_hierarchy import CombatPolicy

        registry = GroupPolicyRegistry()
        registry.load()

        policy = CombatPolicy(
            targeting="focus_strongest",
            movement="advance",
            retreat="group_25",
        )
        errors = registry.validate_policy(policy)
        assert errors == []

    def test_validate_combat_policy_with_invalid(self):
        """validate_policy returns error messages for invalid policy IDs."""
        from game.strategy.data.group_policy_registry import GroupPolicyRegistry
        from game.strategy.data.fleet_hierarchy import CombatPolicy

        registry = GroupPolicyRegistry()
        registry.load()

        policy = CombatPolicy(
            targeting="bad_target",
            movement="advance",
            retreat="bad_retreat",
        )
        errors = registry.validate_policy(policy)
        assert len(errors) == 2
        assert any("targeting" in e for e in errors)
        assert any("retreat" in e for e in errors)

    def test_validate_combat_policy_none_values_are_valid(self):
        """validate_policy accepts None values (inherit from parent)."""
        from game.strategy.data.group_policy_registry import GroupPolicyRegistry
        from game.strategy.data.fleet_hierarchy import CombatPolicy

        registry = GroupPolicyRegistry()
        registry.load()

        policy = CombatPolicy()  # all None
        errors = registry.validate_policy(policy)
        assert errors == []


# =============================================================================
# Policy Data Access
# =============================================================================

class TestPolicyDataAccess:
    """Tests for accessing policy definition data."""

    def test_get_targeting_policy_data(self):
        """get_targeting returns the full policy definition."""
        from game.strategy.data.group_policy_registry import GroupPolicyRegistry

        registry = GroupPolicyRegistry()
        registry.load()

        data = registry.get_targeting("focus_strongest")
        assert data is not None
        assert data["name"] == "Focus Strongest"
        assert data["mode"] == "focus"

    def test_get_movement_policy_data(self):
        """get_movement returns the full policy definition."""
        from game.strategy.data.group_policy_registry import GroupPolicyRegistry

        registry = GroupPolicyRegistry()
        registry.load()

        data = registry.get_movement("advance")
        assert data is not None
        assert data["name"] == "Advance"
        assert "per_ship_policy" in data

    def test_get_retreat_policy_data(self):
        """get_retreat returns the full policy definition."""
        from game.strategy.data.group_policy_registry import GroupPolicyRegistry

        registry = GroupPolicyRegistry()
        registry.load()

        data = registry.get_retreat("group_25")
        assert data is not None
        assert data["mode"] == "group"
        assert data["threshold"] == 0.25

    def test_get_nonexistent_returns_none(self):
        """Getting a nonexistent policy returns None."""
        from game.strategy.data.group_policy_registry import GroupPolicyRegistry

        registry = GroupPolicyRegistry()
        registry.load()

        assert registry.get_targeting("nonexistent") is None
        assert registry.get_movement("nonexistent") is None
        assert registry.get_retreat("nonexistent") is None


# =============================================================================
# Full Hierarchy Policy Resolution
# =============================================================================

class TestHierarchyPolicyResolution:
    """Tests for resolving effective policies through the full 3-level hierarchy."""

    def test_full_fleet_to_squadron_resolution(self):
        """Policies resolve correctly through Fleet -> TaskForce -> Squadron."""
        from game.strategy.data.fleet_hierarchy import CombatPolicy
        from game.strategy.data.task_force import TaskForce
        from game.strategy.data.squadron import Squadron

        # Fleet level: only retreat set
        fleet_policy = CombatPolicy(retreat="group_25")

        # Task force: targeting and movement set
        tf = TaskForce(
            name="Alpha",
            policy=CombatPolicy(targeting="focus_strongest", movement="advance"),
        )

        # Squadron: only targeting override
        sq = Squadron(
            name="Screen",
            policy=CombatPolicy(targeting="anti_fighter"),
        )
        tf.add_squadron(sq)

        # Resolve TF policy from fleet
        tf_effective = tf.resolve_effective_policy(fleet_policy)
        assert tf_effective.targeting == "focus_strongest"
        assert tf_effective.movement == "advance"
        assert tf_effective.retreat == "group_25"

        # Resolve squadron from TF effective
        sq_effective = sq.resolve_effective_policy(tf_effective)
        assert sq_effective.targeting == "anti_fighter"  # overridden
        assert sq_effective.movement == "advance"  # from TF
        assert sq_effective.retreat == "group_25"  # from fleet (through TF)

    def test_unset_policies_remain_none_without_parent(self):
        """Unset policies stay None when no parent provides them."""
        from game.strategy.data.fleet_hierarchy import CombatPolicy
        from game.strategy.data.squadron import Squadron

        sq = Squadron(
            name="Lone",
            policy=CombatPolicy(targeting="distributed"),
        )

        effective = sq.resolve_effective_policy(None)
        assert effective.targeting == "distributed"
        assert effective.movement is None
        assert effective.retreat is None
