"""Public-API contract test for ``StrategySessionFacade`` (PROJ-430 / TD-08).

Pins the *post-TD-08* shape of the facade: a minimal top-level surface of two
callable methods (``handle_command``, ``process_turn``) plus 10 grouped
namespace attributes (``facade_state`` and 9 ``Facade*`` domain accessors).
Every other public name on the pre-TD-08 facade — the 36 ``dispatch_*``
helpers and the 32 flat read methods — must be reachable through the new
grouped surface, never at the top level.

The legacy underscore-prefixed cache attributes (`_planet_index`,
`_all_stars_cache`, `_all_stars_cache_turn`, `_fleets_by_hex_cache`,
`_fleets_by_hex_turn`, `_race_registry`) must not be settable on a fresh
facade instance — tests seed cache state through
``facade.facade_state.seed_*`` helpers instead.

Phase 1 (PROJ-430) authors this as the failing TDD anchor. Phase 2 adds the
grouped accessors (parity tests in ``test_facade_grouped_namespaces.py`` go
green). Phase 5 root-cause-deletes the legacy flat surface and the cache
forwarders — at that point every assertion below goes green.
"""

from __future__ import annotations

import inspect

import pytest

from game.strategy.facade.strategy_session_facade import StrategySessionFacade


# ---------------------------------------------------------------------------
# Target shape (the post-TD-08 contract)
# ---------------------------------------------------------------------------

# Only two callables survive at the top level.
PUBLIC_TOP_LEVEL: frozenset[str] = frozenset({
    "handle_command",
    "process_turn",
})

# Grouped namespace accessors (``facade_state`` is already public; the other
# nine are new in Phase 2).
PUBLIC_GROUP_ACCESSORS: frozenset[str] = frozenset({
    "facade_state",
    "commands",
    "fleets",
    "systems",
    "planets",
    "empires",
    "events",
    "session_meta",
    "economy",
    "validation",
})

# Per-group expected method/attribute names. Driven by behavior coverage in
# ``test_facade_grouped_namespaces.py``; this dict is the canonical source of
# truth for which renamed verbs each namespace must expose.
GROUP_CONTRACT: dict[str, frozenset[str]] = {
    "fleets": frozenset({
        "get",
        "at_hex",
        "path_preview",
        "path_projection",
        "remaining_pods",
    }),
    "planets": frozenset({
        "get",
        "at_hex",
    }),
    "systems": frozenset({
        "all",
        "all_stars",
        "at_hex",
        "containing_fleet",
        "near_hex",
        "storm_names_at_hex",
    }),
    "empires": frozenset({
        "all",
        "get",
        "colonies",
        "fleets",
        "build_queues",
        "hex_build_queues",
    }),
    "events": frozenset({
        "turn_events",
        "all",
        "by_category",
    }),
    "session_meta": frozenset({
        "turn_number",
        "save_path",
        "human_player_ids",
    }),
    "economy": frozenset({
        "race_registry",
        "colony_demographic_view",
        "resolve_config",
        "registries",
    }),
    "validation": frozenset({
        "can_colonize",
        "can_move_to",
    }),
}

# Legacy flat methods that must NOT exist as top-level facade attributes after
# Phase 5. Pinned from the pre-TD-08 PUBLIC_METHODS roster so the assertion is
# exhaustive (36 dispatch_* + 32 flat reads = 68; minus the two survivors
# handle_command/process_turn).
LEGACY_FLAT_METHODS: frozenset[str] = frozenset({
    # 36 dispatch_* helpers
    "dispatch_issue_colonize",
    "dispatch_issue_move",
    "dispatch_issue_intercept",
    "dispatch_issue_join_fleet",
    "dispatch_queue_colonize_mission",
    "dispatch_clear_orders",
    "dispatch_issue_transfer",
    "dispatch_issue_implode_planet",
    "dispatch_issue_stellerate_star",
    "dispatch_issue_open_warp_point",
    "dispatch_issue_close_warp_point",
    "dispatch_issue_create_dyson_sphere",
    "dispatch_issue_self_destruct",
    "dispatch_queue_implode_planet_mission",
    "dispatch_queue_stellerate_star_mission",
    "dispatch_queue_open_warp_point_mission",
    "dispatch_queue_close_warp_point_mission",
    "dispatch_queue_create_dyson_sphere_mission",
    "dispatch_issue_warp",
    "dispatch_issue_lay_mines",
    "dispatch_issue_launch_fighters",
    "dispatch_issue_recover_fighters",
    "dispatch_issue_launch_satellites",
    "dispatch_issue_recover_satellites",
    "dispatch_issue_build_order",
    "dispatch_remove_build_order",
    "dispatch_split_fleet",
    "dispatch_delete_order",
    "dispatch_reorder_order",
    "dispatch_add_to_construction_queue",
    "dispatch_remove_from_construction_queue",
    "dispatch_reorder_construction_queue",
    "dispatch_issue_planet_order",
    "dispatch_clear_planet_orders",
    "dispatch_delete_planet_order",
    "dispatch_set_atmosphere_target",
    # Flat read methods
    "get_fleet",
    "get_fleets_at_hex",
    "get_fleet_path_preview",
    "get_fleet_path_projection",
    "get_fleet_remaining_pods",
    "get_all_systems",
    "get_all_stars",
    "get_system_at_hex",
    "get_system_containing_fleet",
    "get_system_near_hex",
    "get_storm_names_at_hex",
    "get_planet",
    "get_planets_at_hex",
    "get_all_empires",
    "get_empire",
    "get_empire_colonies",
    "get_empire_fleets",
    "get_empire_build_queues",
    "get_hex_build_queues",
    "get_human_player_ids",
    "get_turn_number",
    "get_save_path",
    "get_colony_demographic_view",
    "get_race_registry",
    "get_registries",
    "get_turn_events",
    "get_all_events",
    "get_events_by_category",
    "can_colonize",
    "can_move_to",
})

# Underscore-prefixed cache fields that must NOT be settable on a fresh
# instance after Phase 5 (the @property forwarders are gone; tests use
# ``facade.facade_state.seed_*`` helpers instead).
LEGACY_CACHE_ATTRS: frozenset[str] = frozenset({
    "_planet_index",
    "_all_stars_cache",
    "_all_stars_cache_turn",
    "_fleets_by_hex_cache",
    "_fleets_by_hex_turn",
    "_race_registry",
})


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def fresh_facade() -> StrategySessionFacade:
    """Return a fresh facade instance over a minimal mocked session."""
    from unittest.mock import MagicMock

    session = MagicMock()
    session.galaxy.systems = {}
    session.empires = []
    return StrategySessionFacade(session)


# ---------------------------------------------------------------------------
# Top-level surface tests
# ---------------------------------------------------------------------------

class TestTopLevelSurface:
    """The post-TD-08 facade exposes exactly two callables and 10 grouped
    attribute accessors at the top level. Everything else moves under a
    namespace.
    """

    def test_only_target_top_level_callables_exist(self) -> None:
        actual_public_callables = {
            name for name, _ in inspect.getmembers(
                StrategySessionFacade, predicate=inspect.isfunction
            )
            if not name.startswith("_")
        }
        assert actual_public_callables == PUBLIC_TOP_LEVEL, (
            f"Top-level callables drifted from the target contract. "
            f"Expected exactly {sorted(PUBLIC_TOP_LEVEL)}; "
            f"got {sorted(actual_public_callables)}."
        )

    def test_only_target_top_level_attrs_exist(
        self, fresh_facade: StrategySessionFacade
    ) -> None:
        actual_public_attrs = {
            name for name in dir(fresh_facade)
            if not name.startswith("_")
            and not callable(getattr(fresh_facade, name, None))
        }
        # Group accessors return objects (the namespace dataclasses), not
        # functions, so they appear here. The two PUBLIC_TOP_LEVEL callables
        # do not.
        assert actual_public_attrs == PUBLIC_GROUP_ACCESSORS, (
            f"Top-level non-callable attributes drifted. "
            f"Expected exactly {sorted(PUBLIC_GROUP_ACCESSORS)}; "
            f"got {sorted(actual_public_attrs)}."
        )

    def test_no_legacy_flat_methods(self) -> None:
        """None of the 68 pre-TD-08 dispatch_* / get_* / can_* helpers may
        survive at the top level after Phase 5.
        """
        survivors = sorted(
            name for name in LEGACY_FLAT_METHODS
            if hasattr(StrategySessionFacade, name)
        )
        assert survivors == [], (
            f"Legacy flat methods still exist on StrategySessionFacade: "
            f"{survivors}. Move them onto the appropriate grouped namespace."
        )


class TestGroupedNamespaces:
    """Each grouped accessor exposes its expected verb set (renamed forms
    with redundant prefixes stripped).
    """

    @pytest.mark.parametrize("group_name", sorted(GROUP_CONTRACT.keys()))
    def test_grouped_namespaces_expose_expected_methods(
        self, fresh_facade: StrategySessionFacade, group_name: str
    ) -> None:
        ns = getattr(fresh_facade, group_name)
        expected = GROUP_CONTRACT[group_name]
        actual = {
            name for name in dir(ns)
            if not name.startswith("_")
        }
        missing = expected - actual
        assert not missing, (
            f"Group {group_name!r} is missing expected verbs: "
            f"{sorted(missing)}. (Has: {sorted(actual)}.)"
        )

    def test_commands_namespace_strips_dispatch_prefix(
        self, fresh_facade: StrategySessionFacade
    ) -> None:
        """All 36 ``dispatch_*`` helpers reachable through ``commands.<verb>``
        with the prefix stripped — driven from the registry, not hand-listed.
        """
        from game.strategy.engine.commands.registry import (
            command_registry,
            seed_default_commands,
        )

        if len(command_registry) == 0:
            seed_default_commands(command_registry)

        commands_ns = fresh_facade.commands
        missing = []
        for helper_name in command_registry.specs_by_facade_helper():
            assert helper_name.startswith("dispatch_"), helper_name
            verb = helper_name[len("dispatch_"):]
            if not hasattr(commands_ns, verb):
                missing.append(verb)
        assert missing == [], (
            f"facade.commands is missing renamed dispatch verbs: {missing}"
        )


# ---------------------------------------------------------------------------
# Legacy cache attribute removal
# ---------------------------------------------------------------------------

class TestLegacyCacheAttrsRemoved:
    """The 6 underscore-prefixed cache fields (12 get+set property halves)
    must NOT be settable on a fresh facade instance after Phase 5. Tests use
    the public ``facade_state.seed_*`` seam instead.
    """

    @pytest.mark.parametrize("attr_name", sorted(LEGACY_CACHE_ATTRS))
    def test_legacy_cache_attr_not_settable(
        self, fresh_facade: StrategySessionFacade, attr_name: str
    ) -> None:
        sentinel = object()
        try:
            setattr(fresh_facade, attr_name, sentinel)
        except AttributeError:
            # Acceptable: writing is blocked outright (e.g. read-only
            # property or no descriptor at all on a non-slotted class).
            return
        # If the setattr succeeded, the value must NOT round-trip through a
        # forwarder onto the underlying FacadeSessionState — otherwise the
        # cache forwarders are still effectively in place.
        underlying = getattr(fresh_facade.facade_state,
                             attr_name.lstrip("_"), None)
        assert underlying is not sentinel, (
            f"Setting {attr_name!r} on the facade still round-trips onto "
            f"facade.facade_state.{attr_name.lstrip('_')} — the legacy "
            f"cache forwarder property is still installed."
        )
