"""End-to-end smoke test for the design_role_registry invalidation contract
(PROJ-278 Phase 5).

PROJ-278 Phase 5 audit found that NO subsystem in the codebase currently
caches role-derived data — formation defaults use a hardcoded dict, AI
doesn't consume design_role, design_library filters in-line. Phase 5 ships
this smoke test to:

  1. Prove the `RoleRegistry.register_invalidation_callback` API works
     end-to-end with `add_user_role` (regression guard for Phase 1
     infrastructure that has no production users yet).
  2. Serve as a worked example for future implementers — any new code that
     caches role-derived data should follow this pattern.

The fake cacher below models the future authoring pattern documented in
`docs/systems/strategy_layer.md` § "Design Roles" → "Authoring rule for
new role-derived caches".
"""
from __future__ import annotations

from typing import Optional

import pytest

from game.core.roles import Role, RoleRegistry
from game.strategy.data.design_role_registry import (
    get_default_design_role_registry,
    reset_default_design_role_registry,
)


class _FakeRoleArchetypeCache:
    """Worked example: a subsystem that caches role-derived data and
    correctly invalidates on runtime mutation.

    Mirrors what `resolve_default_for_task_force` would look like if the
    `_DESIGN_ROLE_TO_ARCHETYPE` mapping moved into the registry — see the
    "Future opportunities" note in PROJ-278 phase_5_checklist.md.
    """

    def __init__(self, registry: RoleRegistry):
        self._registry = registry
        self._cache: Optional[dict] = None
        self._populate_count = 0
        self._invalidate_count = 0
        registry.register_invalidation_callback(self._invalidate)

    def get_archetype_for(self, role_id: str) -> str:
        if self._cache is None:
            self._populate()
        return self._cache.get(role_id, "unknown")

    def _populate(self) -> None:
        # In a real cacher this would derive archetypes from role data,
        # external lookups, etc. For the smoke test we just snapshot the
        # set of currently-registered role ids.
        self._cache = {r.id: "default" for r in self._registry.all()}
        self._populate_count += 1

    def _invalidate(self) -> None:
        self._cache = None
        self._invalidate_count += 1


@pytest.fixture(autouse=True)
def _reset_registry():
    """Each test starts with a fresh module-level registry."""
    reset_default_design_role_registry()
    yield
    reset_default_design_role_registry()


class TestInvalidationContract:
    """The registered callback fires when add_user_role succeeds, and
    cachers that follow the worked-example pattern see fresh data."""

    def test_cacher_receives_callback_on_add_user_role(self):
        registry = get_default_design_role_registry()
        cacher = _FakeRoleArchetypeCache(registry)

        # Trigger initial population
        cacher.get_archetype_for("general_purpose")
        assert cacher._populate_count == 1
        assert cacher._invalidate_count == 0

        # Player adds a custom role at runtime
        new_role = Role(
            id="custom_player_role",
            display_name="Custom Player Role",
            description="Added at runtime by the player.",
        )
        registry.add_user_role(new_role)

        assert cacher._invalidate_count == 1, (
            "Cacher's invalidation callback did not fire on add_user_role"
        )

    def test_cacher_picks_up_new_role_after_invalidation(self):
        registry = get_default_design_role_registry()
        cacher = _FakeRoleArchetypeCache(registry)

        # First lookup — new role not yet added
        assert cacher.get_archetype_for("custom_player_role") == "unknown"

        registry.add_user_role(Role(
            id="custom_player_role",
            display_name="Custom",
            description="...",
        ))

        # Next lookup — cache was invalidated → repopulated → includes new role
        assert cacher.get_archetype_for("custom_player_role") == "default"

    def test_multiple_reads_share_one_population(self):
        """Cache survives reads — only writes invalidate."""
        registry = get_default_design_role_registry()
        cacher = _FakeRoleArchetypeCache(registry)

        for role_id in ("general_purpose", "carrier", "interceptor", "scout"):
            cacher.get_archetype_for(role_id)

        # Despite 4 reads, only 1 populate
        assert cacher._populate_count == 1
        assert cacher._invalidate_count == 0

    def test_each_add_fires_one_invalidation(self):
        """One add → one invalidation → one repopulation on next read."""
        registry = get_default_design_role_registry()
        cacher = _FakeRoleArchetypeCache(registry)

        cacher.get_archetype_for("general_purpose")  # populate #1
        registry.add_user_role(Role(id="r1", display_name="R1", description="r"))
        cacher.get_archetype_for("r1")               # populate #2 (after invalidate)
        registry.add_user_role(Role(id="r2", display_name="R2", description="r"))
        cacher.get_archetype_for("r2")               # populate #3 (after invalidate)

        assert cacher._populate_count == 3
        assert cacher._invalidate_count == 2


class TestMultipleCachersIndependent:
    """Two cachers registered against the same registry both receive
    callbacks — proves the callback list is not exclusive."""

    def test_both_cachers_invalidated(self):
        registry = get_default_design_role_registry()
        cacher_a = _FakeRoleArchetypeCache(registry)
        cacher_b = _FakeRoleArchetypeCache(registry)

        cacher_a.get_archetype_for("general_purpose")
        cacher_b.get_archetype_for("carrier")

        registry.add_user_role(Role(
            id="custom", display_name="Custom", description="...",
        ))

        assert cacher_a._invalidate_count == 1
        assert cacher_b._invalidate_count == 1
