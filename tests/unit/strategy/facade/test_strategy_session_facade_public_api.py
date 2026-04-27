"""Contract test for the StrategySessionFacade public surface (PROJ-309 sub-phase 3.7).

Snapshots the full public method list of `StrategySessionFacade` (plus the
specific underscore-prefixed members that downstream tests reach into) and
asserts every entry remains present after the facade decomposition.

Must PASS pre-split; must continue to PASS post-split.

Frozen contract — if you must change this list, also update:
- `Projects/active_projects/PROJ-309/findings/strategy_session_facade_decomposition.md`
- All callers of the renamed/removed member.
"""

from __future__ import annotations

import inspect

from game.strategy.facade.strategy_session_facade import StrategySessionFacade


# ---------------------------------------------------------------------------
# Frozen surface
# ---------------------------------------------------------------------------

PUBLIC_METHODS: frozenset[str] = frozenset({
    # Lifecycle / write path
    "handle_command",
    "process_turn",
    # Command dispatch helpers (28)
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
    # Fleet queries
    "get_fleet",
    "get_fleets_at_hex",
    "get_fleet_path_preview",
    "get_fleet_path_projection",
    "get_fleet_remaining_pods",
    # System / star / map queries
    "get_all_systems",
    "get_all_stars",
    "get_system_at_hex",
    "get_system_containing_fleet",
    "get_system_near_hex",
    "get_storm_names_at_hex",
    # Planet queries
    "get_planet",
    "get_planets_at_hex",
    # Empire queries
    "get_all_empires",
    "get_empire",
    "get_empire_colonies",
    "get_empire_fleets",
    "get_empire_build_queues",
    "get_hex_build_queues",
    # Game state
    "get_human_player_ids",
    "get_turn_number",
    "get_save_path",
    # Demographics / economy / races
    "get_colony_demographic_view",
    "get_race_registry",
    # Events
    "get_turn_events",
    "get_all_events",
    "get_events_by_category",
    # Validation
    "can_colonize",
    "can_move_to",
})

# Underscore-prefixed members downstream tests reach into. Must remain
# accessible (callable methods or settable attributes) on the composer.
PROTECTED_CALLABLES: frozenset[str] = frozenset({
    "_get_fleet_by_id",
    "_get_planet_by_id",
    "_get_empire_by_id",
    "_build_fleet_hex_index",
    "_build_planet_index",
})

PROTECTED_ATTRS: frozenset[str] = frozenset({
    "_planet_index",
    "_fleets_by_hex_cache",
    "_all_stars_cache",
    "_race_registry",
})


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestPublicMethodSurface:
    def test_every_public_method_present(self) -> None:
        missing = [name for name in PUBLIC_METHODS
                   if not hasattr(StrategySessionFacade, name)]
        assert missing == [], (
            f"StrategySessionFacade is missing public methods: {missing}"
        )

    def test_every_public_method_callable(self) -> None:
        non_callable = [
            name for name in PUBLIC_METHODS
            if not callable(getattr(StrategySessionFacade, name, None))
        ]
        assert non_callable == [], (
            f"Members not callable on the class: {non_callable}"
        )

    def test_no_unexpected_public_methods_added(self) -> None:
        """Catch silent additions to the facade surface — every new public
        method should be a deliberate API decision; add it to PUBLIC_METHODS
        when it is.
        """
        actual_public = {
            name for name, _ in inspect.getmembers(StrategySessionFacade,
                                                   predicate=inspect.isfunction)
            if not name.startswith("_")
        }
        unexpected = actual_public - PUBLIC_METHODS
        assert unexpected == set(), (
            f"Public methods present on the class but not in the frozen "
            f"contract: {sorted(unexpected)}. Add them to PUBLIC_METHODS "
            f"if intentional."
        )


class TestProtectedSurface:
    """Members starting with `_` that downstream tests reach into."""

    def test_protected_callables_present(self) -> None:
        missing = [name for name in PROTECTED_CALLABLES
                   if not hasattr(StrategySessionFacade, name)]
        assert missing == [], (
            f"Protected callables missing: {missing}"
        )

    def test_protected_attrs_settable_on_instance(self) -> None:
        """Tests like `test_colony_demographic_view.py` assign directly to
        `facade._planet_index` and `facade._race_registry`. Verify each
        protected attribute can be both read and written on a fresh instance.
        """
        from unittest.mock import MagicMock

        session = MagicMock()
        session.galaxy.systems = {}
        session.empires = []
        facade = StrategySessionFacade(session)

        for name in PROTECTED_ATTRS:
            # Read should not raise (may be None pre-population).
            assert hasattr(facade, name), (
                f"Protected attribute {name!r} missing from instance"
            )
            # Write should round-trip.
            sentinel = object()
            setattr(facade, name, sentinel)
            assert getattr(facade, name) is sentinel, (
                f"Setting {name!r} on the facade instance did not round-trip"
            )
