"""PROJ-438 Phase 2: pin the GameSession ownership categories.

Phase 2 collapsed to a documentation + invariant pass (see decisions.md
row dated 2026-05-18 for the scope rationale). Rather than extracting
holders for ``save_path`` / ``human_player_ids`` / ``active_empire`` /
``enemy_empire`` — which would ripple into 60+ caller files for marginal
clarity gain — Phase 2 instead pins the **categorical ownership** of
``GameSession`` attributes in the class docstring and at each assignment
site in ``_apply_bootstrap_state``. This file ratchets that pin so future
drift surfaces immediately.

The named concerns from ``plan.md:84-85`` map to categories:

- ``save_path``                → Owned persistence metadata
- ``human_player_ids``         → Owned UI configuration
- ``active_empire`` / ``enemy_empire`` → Owned UI-rotation state (mutable via
  ``StrategyGameStateManager.advance_turn``, NOT a derivable projection)
- ``race_registry``            → Lazy-init owned service (property)
- Façade cache                  → Intentional performance boundary
  (``FacadeSessionState``), NOT compensation debt
"""
from __future__ import annotations

from game.strategy.engine.game_session import GameSession
from game.strategy.engine.game_config import GameConfig, PlayerConfig


def _minimal_session() -> GameSession:
    return GameSession(
        config=GameConfig(
            players=[
                PlayerConfig(name="A", theme="Federation", color=(255, 0, 0)),
                PlayerConfig(name="B", theme="Atlantians", color=(0, 255, 0)),
            ],
            system_count=2,
        )
    )


class TestGameSessionAttributeCategories:
    """Pin the categorical ownership of GameSession attributes."""

    def test_owned_domain_state_attributes_present(self) -> None:
        session = _minimal_session()
        for attr in ("galaxy", "empires", "systems", "turn_engine", "turn_number"):
            assert hasattr(session, attr), (
                f"Owned domain attribute missing: {attr}"
            )

    def test_owned_ui_rotation_state_attributes_present(self) -> None:
        """`active_empire`/`enemy_empire` are mutable UI-rotation state per
        BUG-125, not derivable projections."""
        session = _minimal_session()
        for attr in ("active_empire", "enemy_empire"):
            assert hasattr(session, attr), (
                f"Owned UI-rotation attribute missing: {attr}"
            )

    def test_owned_ui_configuration_attributes_present(self) -> None:
        session = _minimal_session()
        assert hasattr(session, "human_player_ids")

    def test_owned_persistence_metadata_attributes_present(self) -> None:
        session = _minimal_session()
        assert hasattr(session, "save_path")

    def test_race_registry_is_lazy_property(self) -> None:
        """`race_registry` must remain a class-level @property with a
        ``None``-seeded ``_race_registry`` backing slot. A regression that
        replaces it with a bare attribute on ``__init__`` would break the
        chicken-and-egg bootstrap closure pattern."""
        assert isinstance(GameSession.__dict__.get("race_registry"), property), (
            "race_registry must be a property on the class"
        )
        session = _minimal_session()
        # Backing slot must exist on the instance (seeded in __init__).
        assert hasattr(session, "_race_registry")

    def test_services_is_property_routing_to_bag(self) -> None:
        """``services`` must remain a property that returns the wired
        ``SessionRuntimeServices`` bag from ``_services``. Direct
        assignment to ``session.services`` would bypass the bootstrap
        contract."""
        assert isinstance(GameSession.__dict__.get("services"), property)
        session = _minimal_session()
        assert session.services is session._services


class TestGameSessionDocumentationContract:
    """Pin that GameSession's class docstring categorizes its attributes by
    ownership, so future agents see the boundaries without reading every
    method body. This is the Phase 2 narrowing: documentation in lieu of
    a holder extraction sweep."""

    def test_class_docstring_documents_ownership_categories(self) -> None:
        doc = GameSession.__doc__ or ""
        required_headers = [
            "Owned domain state",
            "Owned UI",  # matches both "UI-rotation state" and "UI configuration"
            "Owned persistence metadata",
            "Lazy-init",
        ]
        missing = [h for h in required_headers if h not in doc]
        assert not missing, (
            f"GameSession class docstring missing ownership categories: "
            f"{missing}. Phase 2 requires explicit attribute categorization "
            "in the class docstring."
        )


class TestFacadeCacheHolderIsDocumentedPerformanceBoundary:
    """Pin that ``FacadeSessionState`` is explicitly documented as an
    intentional performance boundary, not compensation debt. Phase 2
    addresses this named concern without changing the class's semantics."""

    def test_facade_session_state_marks_intentional_performance_boundary(
        self,
    ) -> None:
        from game.strategy.facade.slices._facade_state import (
            FacadeSessionState,
        )

        doc = FacadeSessionState.__doc__ or ""
        # The class docstring must explicitly use the words "intentional"
        # AND ("performance" OR "perf boundary") so future readers see
        # this is a kept-by-design boundary, not a holdover to retire.
        lower = doc.lower()
        assert "intentional" in lower, (
            "FacadeSessionState class docstring must contain "
            "'intentional' to mark its cache as kept-by-design."
        )
        assert "performance" in lower or "perf boundary" in lower, (
            "FacadeSessionState class docstring must contain 'performance' "
            "or 'perf boundary' to mark its cache as a perf boundary."
        )
