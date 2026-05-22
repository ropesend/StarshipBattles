"""Regression tests for the ``viewing_empire_id`` anchor (QA Obs 1, post-PROJ-FMS).

In hot-seat play, the human at the keyboard is identified by
``current_player_index`` on ``StrategyScreen``; the empire whose turn it
*currently is* is ``session.active_empire``. These can diverge — e.g. when
a save is loaded where ``active_empire`` was rotated mid-turn, or when the
user opens the Workshop from a viewing-empire context while
``active_empire`` has been advanced by another flow.

The Workshop and Build Queue display empire-scoped data (designs). They
must anchor to the *viewing* human (``current_empire``), not the
turn-acting empire (``active_empire``). Otherwise the user saves a design
into one empire's folder and the build queue scans the other empire's
folder — symptom: design appears to vanish (no mines/fighters/satellites
in Available Designs).

Per the user's QA decision (2026-05-16), ``current_empire`` is the
canonical anchor for these surfaces. ``active_empire`` is reserved for
turn-gated authorization (move orders, end-turn).
"""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

from game.app import Game
from game.ui.screens import strategy_screen_lifecycle as lifecycle


def _make_screen_with_divergence(viewing_id: int, active_id: int) -> MagicMock:
    """Build a mock screen where the viewing human (``current_empire``)
    and the turn-acting empire (``active_empire``) refer to different
    empires."""
    screen = MagicMock()
    screen.screen_width = 1920
    screen.screen_height = 1080
    screen.scene_callback = MagicMock()

    viewing_empire = MagicMock(id=viewing_id)
    active_empire = MagicMock(id=active_id)

    screen.current_empire = viewing_empire
    screen.session = MagicMock()
    screen.session.active_empire = active_empire
    return screen


class TestOnDesignClickAnchorsToCurrentEmpire:
    """``on_design_click`` populates ``context_data["empire"]`` with the
    viewing human's empire, not the turn-acting empire."""

    def test_uses_current_empire_when_diverged(self) -> None:
        screen = _make_screen_with_divergence(viewing_id=0, active_id=1)

        lifecycle.on_design_click(screen)

        screen.scene_callback.assert_called_once()
        args, kwargs = screen.scene_callback.call_args
        assert args[0] == "open_builder"
        empire_in_context = kwargs["context_data"]["empire"]
        assert empire_in_context is screen.current_empire
        assert empire_in_context is not screen.session.active_empire
        assert empire_in_context.id == 0

    def test_uses_current_empire_when_aligned(self) -> None:
        # In the steady state, current_empire and active_empire point to
        # the same empire — the helper still passes ``current_empire``.
        screen = MagicMock()
        screen.screen_width = 1920
        screen.screen_height = 1080
        screen.scene_callback = MagicMock()
        same_empire = MagicMock(id=0)
        screen.current_empire = same_empire
        screen.session = MagicMock()
        screen.session.active_empire = same_empire

        lifecycle.on_design_click(screen)

        _, kwargs = screen.scene_callback.call_args
        assert kwargs["context_data"]["empire"] is screen.current_empire


class TestWorkshopContextHonoursViewingEmpire:
    """Tracing the open-builder pipeline end-to-end: the
    ``WorkshopContext`` constructed by ``Game._create_workshop_context``
    receives the viewing empire's ``id``, so designs persist under
    ``designs/empire_<viewing_id>/``."""

    def test_workshop_context_empire_id_matches_current_empire(self) -> None:
        from game.ui.screens.workshop_context import WorkshopContext

        # Build the lifecycle-produced context_data directly so the test
        # mirrors the real call path: lifecycle.on_design_click ->
        # scene_callback("open_builder", context_data=...) ->
        # Game._create_workshop_context.
        screen = _make_screen_with_divergence(viewing_id=0, active_id=1)
        captured: dict = {}
        screen.scene_callback = lambda action, **kw: captured.update(kw)

        lifecycle.on_design_click(screen)

        # Replace the MagicMock empire with a SimpleNamespace so
        # WorkshopContext.integrated sees plain attributes (the MagicMock
        # path injects spurious ``built_ship_designs``-shaped mocks).
        captured["context_data"]["empire"] = SimpleNamespace(
            id=0,
            empire_theme_id="default",
            built_ship_designs=set(),
        )
        captured["context_data"]["game_session"] = SimpleNamespace(
            save_path="saves/divergence_test"
        )

        game = Game.__new__(Game)
        game.registries = MagicMock(name="GameRegistries")

        ctx = game._create_workshop_context(captured["context_data"])

        assert isinstance(ctx, WorkshopContext)
        # The viewing-empire id is what flows to DesignLibrary as
        # ``empire_id`` and decides the ``designs/empire_<id>/`` folder.
        assert ctx.empire_id == 0


class TestBuildQueueScansPlanetOwnersDesigns:
    """``on_build_yard_click`` opens the build queue for a planet the
    viewing human owns. The build queue's ``DesignLibrary.empire_id``
    must match the planet's owner_id (which, for a click the user can
    make, equals ``current_empire.id`` — the gate at line 169 enforces
    this). The bug regressed when other code in the pipeline silently
    used ``active_empire.id`` instead."""

    def test_design_library_uses_planet_owner_id(self) -> None:
        """PROJ-434 Phase 2: the build queue resolves the per-empire
        ``DesignCatalog`` via ``planet.owner_id`` (not active_empire.id)."""
        from unittest.mock import patch

        from game.ui.screens.strategy_build_queue_manager import (
            StrategyBuildQueueManager,
        )

        screen = MagicMock()
        screen.galaxy = MagicMock()
        screen.galaxy.get_system_of_planet.return_value = None
        screen.facade = MagicMock()
        screen.facade.session_meta.save_path = MagicMock(return_value="saves/test")
        # PROJ-472 1C: build queue pulls the catalog via
        # facade.facade_state.get_design_catalog_for_empire(empire_id)
        # (was facade_state.session.services.design_catalogs_by_empire).
        viewing_catalog = MagicMock(name="viewing_catalog")
        active_catalog = MagicMock(name="active_catalog")
        catalogs_by_empire = {0: viewing_catalog, 1: active_catalog}
        screen.facade.facade_state.get_design_catalog_for_empire = MagicMock(
            side_effect=lambda empire_id: catalogs_by_empire.get(empire_id)
        )
        screen.ui = MagicMock()
        screen.ui.manager = MagicMock()
        screen.input_mapper = MagicMock()
        screen.build_queue_screen = None

        viewing_empire = MagicMock(id=0, empire_theme_id="Federation")
        screen.current_empire = viewing_empire

        # Divergent session.active_empire — should be ignored by the
        # build queue path.
        screen.session = MagicMock()
        screen.session.active_empire = MagicMock(id=1)

        from game.strategy.data.planet import Planet
        planet = MagicMock(spec=Planet)
        planet.owner_id = 0  # viewing human owns this planet
        planet.name = "Home"
        screen.selected_object = planet
        screen._get_object_asset = MagicMock(return_value=None)

        manager = StrategyBuildQueueManager(screen)

        with patch(
            "game.ui.screens.strategy_build_queue_manager.BuildQueueScreen"
        ) as MockBQS, patch(
            "game.ui.screens.strategy_build_queue_manager.DesignLoaderAdapter"
        ), patch(
            "game.ui.screens.strategy_build_queue_manager.is_planet",
            return_value=True,
        ):
            manager.on_build_yard_click()

        # The BuildQueueScreen receives the viewing-empire's catalog
        # (planet.owner_id == 0), NOT the divergent active_empire's
        # catalog (id=1).
        MockBQS.assert_called_once()
        kwargs = MockBQS.call_args.kwargs
        assert kwargs["design_catalog"] is viewing_catalog
        assert kwargs["design_catalog"] is not active_catalog


class TestViewingEmpireIdProperty:
    """``StrategyScreen.viewing_empire_id`` is the canonical anchor for
    'whose data should this UI show'. It mirrors ``current_empire.id``
    and is the recommended accessor for new UI surfaces (see
    ``feedback_viewing_empire_anchor`` memory)."""

    def test_property_returns_current_empire_id(self) -> None:
        from game.ui.screens.strategy_screen import StrategyScreen

        screen = StrategyScreen.__new__(StrategyScreen)
        screen._session = MagicMock()
        screen._session.empires = [MagicMock(id=0), MagicMock(id=1)]
        screen._session.active_empire = screen._session.empires[1]
        screen._session.human_player_ids = [0, 1]
        screen.current_player_index = 0

        assert screen.viewing_empire_id == 0

    def test_property_diverges_from_active_empire_id(self) -> None:
        from game.ui.screens.strategy_screen import StrategyScreen

        screen = StrategyScreen.__new__(StrategyScreen)
        screen._session = MagicMock()
        screen._session.empires = [MagicMock(id=0), MagicMock(id=1)]
        # active_empire rotated to empire 1...
        screen._session.active_empire = screen._session.empires[1]
        screen._session.human_player_ids = [0, 1]
        # ...but the viewing human is still at rotation index 0.
        screen.current_player_index = 0

        assert screen.viewing_empire_id == 0
        assert screen.viewing_empire_id != screen.session.active_empire.id
