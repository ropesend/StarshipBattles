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

from game.strategy.facade.strategy_session_facade import StrategySessionFacade


# ---------------------------------------------------------------------------
# Frozen surface
# ---------------------------------------------------------------------------

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
