"""Tests for combat_lab.scenario_role_registry — module-level accessor +
read-only RoleRegistry instance for Combat Lab scenario wiring labels (PROJ-278).

Combat Lab scenario_role and gameplay design_role share the same RoleRegistry
machinery (`game.core.roles`) but live in separate registry instances loaded
from separate files. The Combat Lab instance is read-only at runtime
(`allow_runtime_add=False`) — players don't write Combat Lab scenarios.
"""
from __future__ import annotations

import pytest

from game.core.roles import Role, RoleRegistry, RoleRegistryReadOnlyError
from combat_lab.scenario_role_registry import (
    get_default_combat_lab_role_registry,
    reset_default_combat_lab_role_registry,
    set_default_combat_lab_role_registry,
)


@pytest.fixture(autouse=True)
def _reset_registry():
    """Each test starts with a fresh module state."""
    reset_default_combat_lab_role_registry()
    yield
    reset_default_combat_lab_role_registry()


class TestDefaultRegistryAccessor:
    """Lazy-constructed singleton accessor."""

    def test_returns_role_registry_instance(self):
        reg = get_default_combat_lab_role_registry()
        assert isinstance(reg, RoleRegistry)

    def test_subsequent_calls_return_same_instance(self):
        reg1 = get_default_combat_lab_role_registry()
        reg2 = get_default_combat_lab_role_registry()
        assert reg1 is reg2


class TestRegistryIsReadOnly:
    """`combat_lab_role_registry` MUST disallow runtime add — players don't
    write Combat Lab scenarios so the use case doesn't exist."""

    def test_add_user_role_raises_read_only_error(self):
        reg = get_default_combat_lab_role_registry()
        custom = Role(id="x", display_name="X", description="x")
        with pytest.raises(RoleRegistryReadOnlyError):
            reg.add_user_role(custom)


class TestDefaultRegistryOverride:
    """Test injection via `set_default_*` / `reset_default_*`."""

    def test_set_default_overrides_accessor(self):
        custom = RoleRegistry(allow_runtime_add=False)
        # Custom registry — empty, but valid
        set_default_combat_lab_role_registry(custom)
        assert get_default_combat_lab_role_registry() is custom

    def test_reset_clears_override(self):
        custom = RoleRegistry(allow_runtime_add=False)
        set_default_combat_lab_role_registry(custom)
        reset_default_combat_lab_role_registry()

        fresh = get_default_combat_lab_role_registry()
        assert fresh is not custom


class TestExpectedRolesPresent:
    """The 10 audited roles from `combat_lab/data/scenario_roles.json`
    are all loaded by the default accessor."""

    EXPECTED_IDS = {
        "attacker", "target",
        "ship1", "ship2",
        "ship",
        "low", "med", "high",
        "provider_a", "provider_b",
    }

    def test_all_expected_roles_present(self):
        reg = get_default_combat_lab_role_registry()
        actual_ids = {r.id for r in reg.all()}
        missing = self.EXPECTED_IDS - actual_ids
        assert not missing, f"Missing roles in registry: {missing}"

    def test_every_role_has_non_empty_display_name_and_description(self):
        reg = get_default_combat_lab_role_registry()
        for role in reg.all():
            assert role.display_name, f"Role {role.id} missing display_name"
            assert role.description, f"Role {role.id} missing description"

    def test_combat_lab_roles_have_no_vehicle_type_filter(self):
        """Combat Lab roles are scenario-positional, not gameplay-typed.
        They should accept any vehicle (empty filter)."""
        reg = get_default_combat_lab_role_registry()
        for role in reg.all():
            assert role.vehicle_type_filter == (), \
                f"Role {role.id} has vehicle_type_filter — should be empty"
