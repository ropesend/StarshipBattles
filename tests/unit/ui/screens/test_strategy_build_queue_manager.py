"""Tests for StrategyBuildQueueManager (PROJ-173 Phase 4).

Tests the extracted build queue management functionality.
"""

import pytest
from unittest.mock import MagicMock, patch


def _make_build_queue_manager():
    """Create a StrategyBuildQueueManager with mocked screen dependency.

    PROJ-396 MAJ-004: ``StrategyBuildQueueManager`` no longer reads
    ``screen.session.{save_path,galaxy}`` — those reads are routed
    through ``screen.facade.session_meta.save_path()`` and ``screen.galaxy``
    respectively.  The mock screen exposes both surfaces.
    """
    from game.ui.screens.strategy_build_queue_manager import StrategyBuildQueueManager

    # Create mock screen
    mock_screen = MagicMock()
    mock_screen.galaxy = MagicMock()  # PROJ-396 MAJ-004
    mock_screen.facade = MagicMock()  # PROJ-212: facade for command dispatch
    mock_screen.facade.session_meta.save_path = MagicMock(return_value="test_savegame")
    # PROJ-472 1C: manager pulls the per-empire catalog through
    # facade.facade_state.get_design_catalog_for_empire(empire_id) (was the
    # facade_state.session.services.design_catalogs_by_empire bypass).
    mock_catalog = MagicMock()
    mock_screen.facade.facade_state.get_design_catalog_for_empire = MagicMock(
        return_value=mock_catalog
    )
    mock_screen.ui = MagicMock()
    mock_screen.ui.manager = MagicMock()
    mock_screen.selected_object = None
    mock_screen.build_queue_screen = None
    mock_screen.input_mapper = MagicMock()

    # Setup empire mocking
    empire = MagicMock()
    empire.id = 0
    empire.empire_theme_id = "Federation"
    mock_screen.current_player_index = 0

    # Property mock for current_empire
    type(mock_screen).current_empire = property(lambda s: empire)

    manager = StrategyBuildQueueManager(mock_screen)

    return manager, mock_screen


class TestBuildQueueManagerInit:
    """Test StrategyBuildQueueManager initialization."""

    def test_init_stores_screen_reference(self):
        """Manager should store reference to parent screen."""
        manager, screen = _make_build_queue_manager()
        assert manager._screen is screen


class TestProj472SessionConsumerCleanup:
    """PROJ-472 1C: catalog + live-yard resolution route through the facade
    state accessors, not the facade_state.session bypass."""

    def test_design_catalog_routes_through_facade_state_accessor(self):
        manager, screen = _make_build_queue_manager()
        catalog = manager._design_catalog_for_empire(0)
        screen.facade.facade_state.get_design_catalog_for_empire.assert_called_once_with(0)
        assert catalog is screen.facade.facade_state.get_design_catalog_for_empire.return_value

    def test_design_catalog_missing_raises_keyerror(self):
        manager, screen = _make_build_queue_manager()
        screen.facade.facade_state.get_design_catalog_for_empire = MagicMock(
            return_value=None
        )
        with pytest.raises(KeyError):
            manager._design_catalog_for_empire(5)

    def test_resolve_live_fleet_uses_facade_state_id_lookup(self):
        manager, screen = _make_build_queue_manager()
        fleet = MagicMock()
        screen.facade.facade_state.get_fleet_by_id = MagicMock(return_value=fleet)
        source = MagicMock()
        source.context_type = "fleet"
        source.entity_id = 99

        result = manager._resolve_live_yard(source)

        screen.facade.facade_state.get_fleet_by_id.assert_called_once_with(99)
        assert result is fleet


class TestOnBuildYardClick:
    """Test on_build_yard_click() method."""

    def test_reopens_when_build_queue_already_constructed(self):
        """PROJ-376 Phase 2: reopens reuse the cached instance via open_for_yard.

        Pre-Phase-2 the manager had an entry guard that ignored clicks
        when the screen slot was non-None. Post-Phase-2 the slot is
        cached and reuses are routed through ``open_for_yard()``.
        """
        manager, screen = _make_build_queue_manager()

        from game.strategy.data.planet import Planet
        mock_planet = MagicMock(spec=Planet)
        mock_planet.owner_id = 0
        mock_planet.name = "Test Planet"
        screen.selected_object = mock_planet
        screen._get_object_asset = MagicMock(return_value=None)
        screen.world.system_for_object.return_value = None

        # Pre-populate the cached screen — simulate a prior open.
        cached_screen = MagicMock()
        screen.build_queue_screen = cached_screen

        with patch('game.ui.screens.strategy_build_queue_manager.BuildQueueScreen') as MockBQS, \
             patch('game.ui.screens.strategy_build_queue_manager.DesignLoaderAdapter'), \
             patch('game.ui.screens.strategy_build_queue_manager.is_planet', return_value=True):
            manager.on_build_yard_click()

        # No fresh construction — the cached instance is reused.
        MockBQS.assert_not_called()
        cached_screen.open_for_yard.assert_called_once()
        screen.ui.hide_ui.assert_called_once()

    def test_ignores_when_no_selected_object(self):
        """Should do nothing when no object is selected."""
        manager, screen = _make_build_queue_manager()
        screen.selected_object = None

        manager.on_build_yard_click()

        screen.ui.hide_ui.assert_not_called()

    def test_ignores_non_planet_selection(self):
        """Should do nothing when selected object is not a Planet."""
        manager, screen = _make_build_queue_manager()
        screen.selected_object = MagicMock()  # Generic mock, not a Planet

        manager.on_build_yard_click()

        screen.ui.hide_ui.assert_not_called()

    def test_opens_build_queue_for_owned_planet(self):
        """Should open build queue for player-owned planet."""
        manager, screen = _make_build_queue_manager()

        # Create a properly mocked Planet
        from game.strategy.data.planet import Planet
        mock_planet = MagicMock(spec=Planet)
        mock_planet.owner_id = 0  # Same as player empire
        mock_planet.name = "Test Planet"
        screen.selected_object = mock_planet
        screen._get_object_asset = MagicMock(return_value=None)
        screen.world.system_for_object.return_value = None

        # PROJ-208: is_planet uses Protocol isinstance, need to patch it for mocks
        with patch('game.ui.screens.strategy_build_queue_manager.BuildQueueScreen') as MockBQS, \
             patch('game.ui.screens.strategy_build_queue_manager.DesignLoaderAdapter'), \
             patch('game.ui.screens.strategy_build_queue_manager.is_planet', return_value=True):
            manager.on_build_yard_click()

        MockBQS.assert_called_once()
        # PROJ-376 Phase 2: open_for_yard runs on every open (including the first).
        MockBQS.return_value.open_for_yard.assert_called_once()
        screen.ui.hide_ui.assert_called_once()

    def test_second_click_calls_open_for_yard_not_construct(self):
        """PROJ-376 Phase 2: manager constructs once, reuses across opens."""
        manager, screen = _make_build_queue_manager()

        from game.strategy.data.planet import Planet
        mock_planet = MagicMock(spec=Planet)
        mock_planet.owner_id = 0
        mock_planet.name = "Test Planet"
        screen.selected_object = mock_planet
        screen._get_object_asset = MagicMock(return_value=None)
        screen.world.system_for_object.return_value = None

        with patch('game.ui.screens.strategy_build_queue_manager.BuildQueueScreen') as MockBQS, \
             patch('game.ui.screens.strategy_build_queue_manager.DesignLoaderAdapter'), \
             patch('game.ui.screens.strategy_build_queue_manager.BuildQueuePortraitLoader'), \
             patch('game.ui.screens.strategy_build_queue_manager.is_planet', return_value=True):
            # First click — constructs.
            manager.on_build_yard_click()

            # MagicMock side effect: assigning return_value to the slot
            # only happens if the manager actually constructs. Mirror the
            # production behavior: the first open returned MockBQS instance,
            # so it should now be the cached slot.
            assert screen.build_queue_screen is MockBQS.return_value

            # Second click — same yard, no fresh construction.
            manager.on_build_yard_click()

            assert MockBQS.call_count == 1
            assert MockBQS.return_value.open_for_yard.call_count == 2

    def test_close_callback_does_not_null_screen_slot(self):
        """PROJ-376 Phase 2: close callback must NOT null the cached instance."""
        manager, screen = _make_build_queue_manager()

        cached = MagicMock()
        cached.queue_sources = []
        screen.build_queue_screen = cached
        screen.selected_object = None

        manager._on_build_queue_close()

        # The cached instance survives across opens.
        assert screen.build_queue_screen is cached

    def test_close_callback_does_not_call_hide(self):
        """PROJ-376 Phase 2: close-button handler is the only hide() caller.

        ``_on_build_queue_close`` runs AFTER ``_request_close`` already
        invoked ``hide()``; calling ``hide()`` again from the callback
        would split the source of truth.
        """
        manager, screen = _make_build_queue_manager()

        cached = MagicMock()
        cached.queue_sources = []
        screen.build_queue_screen = cached
        screen.selected_object = None

        manager._on_build_queue_close()

        cached.hide.assert_not_called()


class TestOnBuildQueueClose:
    """Test _on_build_queue_close() method."""

    def test_does_not_null_build_queue_screen(self):
        """PROJ-376 Phase 2: cached instance survives across closes."""
        manager, screen = _make_build_queue_manager()
        cached = MagicMock()
        cached.queue_sources = []
        screen.build_queue_screen = cached
        screen.selected_object = None

        manager._on_build_queue_close()

        assert screen.build_queue_screen is cached

    def test_shows_ui(self):
        """Should call ui.show_ui()."""
        manager, screen = _make_build_queue_manager()
        screen.build_queue_screen = MagicMock()
        screen.build_queue_screen.queue_sources = []
        screen.selected_object = None

        manager._on_build_queue_close()

        screen.ui.show_ui.assert_called_once()

    def test_refreshes_selected_object(self):
        """Should refresh display for selected object."""
        manager, screen = _make_build_queue_manager()
        screen.build_queue_screen = MagicMock()
        screen.build_queue_screen.queue_sources = []
        screen.selected_object = MagicMock()
        screen._get_object_asset = MagicMock(return_value=None)

        manager._on_build_queue_close()

        screen.ui.show_detailed_report.assert_called_once()


class TestHandleFleetBuildQueueClose:
    """Test _handle_fleet_build_queue_close() method.

    PROJ-207 Phase 4: Tests now verify command dispatch instead of direct fleet manipulation.
    """

    @staticmethod
    def _fleet_info(fleet_id, *, queue_size, orders):
        """Build a FleetInfo-shaped stub for the facade fleet query.

        PROJ-472 1B: the manager reads BUILD-order state via
        ``facade.fleets.get(fleet_id)`` → ``FleetInfo`` (orders is a tuple of
        ``FleetOrderInfo`` with a string ``order_type``), not a live fleet.
        """
        info = MagicMock()
        info.construction_queue_size = queue_size
        info.orders = tuple(orders)
        return info

    def test_dispatches_build_command_when_queue_has_items(self):
        """Should dispatch IssueBuildOrderCommand when construction queue is not empty."""
        from game.strategy.engine.commands import IssueBuildOrderCommand
        manager, screen = _make_build_queue_manager()

        info = self._fleet_info(42, queue_size=1, orders=[])
        screen.facade.fleets.get = MagicMock(return_value=info)

        manager._handle_fleet_build_queue_close(42)

        # Should have dispatched IssueBuildOrderCommand
        screen.facade.handle_command.assert_called_once()
        cmd = screen.facade.handle_command.call_args[0][0]
        assert isinstance(cmd, IssueBuildOrderCommand)
        assert cmd.fleet_id == 42

    def test_does_not_dispatch_build_command_if_fleet_already_has_build_order(self):
        """Should not dispatch command if fleet already has BUILD order."""
        from game.strategy.data.order_types import OrderType
        manager, screen = _make_build_queue_manager()

        build_order = MagicMock()
        build_order.order_type = OrderType.BUILD.name
        info = self._fleet_info(42, queue_size=1, orders=[build_order])
        screen.facade.fleets.get = MagicMock(return_value=info)

        manager._handle_fleet_build_queue_close(42)

        # Should NOT dispatch command
        screen.facade.handle_command.assert_not_called()

    def test_dispatches_remove_command_when_queue_empty(self):
        """Should dispatch RemoveBuildOrderCommand when construction queue is empty."""
        from game.strategy.engine.commands import RemoveBuildOrderCommand
        manager, screen = _make_build_queue_manager()

        info = self._fleet_info(99, queue_size=0, orders=[])
        screen.facade.fleets.get = MagicMock(return_value=info)

        manager._handle_fleet_build_queue_close(99)

        # Should have dispatched RemoveBuildOrderCommand
        screen.facade.handle_command.assert_called_once()
        cmd = screen.facade.handle_command.call_args[0][0]
        assert isinstance(cmd, RemoveBuildOrderCommand)
        assert cmd.fleet_id == 99


class TestOnFleetBuildClick:
    """Test on_fleet_build_click() method."""

    def test_reopens_when_build_queue_already_constructed(self):
        """PROJ-376 Phase 2: reopens reuse the cached instance via open_for_yard."""
        manager, screen = _make_build_queue_manager()

        from game.strategy.data.fleet import Fleet
        mock_fleet = MagicMock(spec=Fleet)
        mock_fleet.owner_id = 0
        mock_fleet.has_space_shipyard = True
        mock_fleet.location = MagicMock()
        mock_fleet.id = 1
        screen.selected_object = mock_fleet
        screen._get_object_asset = MagicMock(return_value=None)

        cached_screen = MagicMock()
        screen.build_queue_screen = cached_screen

        with patch('game.ui.screens.strategy_build_queue_manager.BuildQueueScreen') as MockBQS, \
             patch('game.ui.screens.strategy_build_queue_manager.DesignLoaderAdapter'), \
             patch('game.ui.screens.strategy_build_queue_manager.BuildQueuePortraitLoader'), \
             patch('game.ui.screens.strategy_build_queue_manager.is_fleet', return_value=True):
            manager.on_fleet_build_click()

        MockBQS.assert_not_called()
        cached_screen.open_for_yard.assert_called_once()
        screen.ui.hide_ui.assert_called_once()

    def test_ignores_non_fleet_selection(self):
        """Should do nothing when selected object is not a Fleet."""
        manager, screen = _make_build_queue_manager()
        screen.selected_object = MagicMock()  # Generic mock

        manager.on_fleet_build_click()

        screen.ui.hide_ui.assert_not_called()

    def test_opens_build_queue_for_fleet_with_shipyard(self):
        """Should open build queue for fleet with space shipyard."""
        manager, screen = _make_build_queue_manager()

        from game.strategy.data.fleet import Fleet
        mock_fleet = MagicMock(spec=Fleet)
        mock_fleet.owner_id = 0
        mock_fleet.has_space_shipyard = True
        mock_fleet.location = MagicMock()
        mock_fleet.id = 1
        screen.selected_object = mock_fleet
        screen._get_object_asset = MagicMock(return_value=None)

        # PROJ-208: is_fleet uses Protocol isinstance, need to patch it for mocks
        with patch('game.ui.screens.strategy_build_queue_manager.BuildQueueScreen') as MockBQS, \
             patch('game.ui.screens.strategy_build_queue_manager.DesignLoaderAdapter'), \
             patch('game.ui.screens.strategy_build_queue_manager.is_fleet', return_value=True):
            manager.on_fleet_build_click()

        MockBQS.assert_called_once()
        screen.ui.hide_ui.assert_called_once()


class TestOnNavigateToHexBuild:
    """Test on_navigate_to_hex_build() method."""

    @staticmethod
    def _planet_source(planet_id=7, display_name="Test Planet"):
        """A BuildQueueSourceDTO-shaped planet source (PROJ-472 1B)."""
        src = MagicMock()
        src.context_type = "planet"
        src.entity_id = planet_id
        src.planet_id = planet_id
        src.display_name = display_name
        return src

    def test_reopens_when_build_queue_already_constructed(self):
        """PROJ-376 Phase 2: navigate reuses the cached instance via open_for_yard."""
        manager, screen = _make_build_queue_manager()
        screen._get_object_asset = MagicMock(return_value=None)
        # PROJ-472 1B: the live yard is resolved by id from the galaxy.
        screen.world.planet_by_id = MagicMock(return_value=MagicMock())

        cached_screen = MagicMock()
        screen.build_queue_screen = cached_screen

        mock_hex = MagicMock()
        mock_source = self._planet_source(display_name="Test")

        with patch('game.ui.screens.strategy_build_queue_manager.BuildQueueScreen') as MockBQS, \
             patch('game.ui.screens.strategy_build_queue_manager.DesignLoaderAdapter'), \
             patch('game.ui.screens.strategy_build_queue_manager.BuildQueuePortraitLoader'):
            manager.on_navigate_to_hex_build(mock_hex, mock_source)

        MockBQS.assert_not_called()
        cached_screen.open_for_yard.assert_called_once()
        screen.ui.hide_ui.assert_called_once()

    def test_ignores_source_when_live_yard_unresolved(self):
        """PROJ-472 1B: do nothing if the live yard cannot be resolved by id."""
        manager, screen = _make_build_queue_manager()
        screen.world.planet_by_id = MagicMock(return_value=None)

        mock_hex = MagicMock()
        mock_source = self._planet_source()

        manager.on_navigate_to_hex_build(mock_hex, mock_source)

        screen.ui.hide_ui.assert_not_called()

    def test_opens_build_queue_for_valid_source(self):
        """Should open build queue for valid hex and source."""
        manager, screen = _make_build_queue_manager()
        screen._get_object_asset = MagicMock(return_value=None)
        screen.world.planet_by_id = MagicMock(return_value=MagicMock())

        mock_hex = MagicMock()
        mock_source = self._planet_source(display_name="Test Planet")

        with patch('game.ui.screens.strategy_build_queue_manager.BuildQueueScreen') as MockBQS, \
             patch('game.ui.screens.strategy_build_queue_manager.DesignLoaderAdapter'):
            manager.on_navigate_to_hex_build(mock_hex, mock_source)

        MockBQS.assert_called_once()
        screen.ui.close_empire_build_queue_window.assert_called_once()
        screen.ui.hide_ui.assert_called_once()


# =========================================================================
# PROJ-410 Task 1.4: turn-boundary detection + cached-screen rebind
# =========================================================================
#
# Per Codex review (arc01-002 + arc01-006), the manager must:
#   1. Poll self._screen.current_empire.id on each _open_build_queue() to
#      detect player change (no facade callback API exists today).
#   2. On change, call cached_screen.on_active_player_changed() to flush
#      widget/queue state.
#   3. ALWAYS before open_for_yard(): rebind cached_screen.empire,
#      .galaxy, and .facade to current values, so the cached screen
#      queries as the current empire (collect_build_queues_at_hex filters
#      by empire.id).
#
# Without these, the cached screen retains the prior player's empire
# reference (BuildQueueScreen.__init__ stores empire/galaxy/facade once
# at construction; only design_library/loader/portrait are rebound in
# the existing reuse path at strategy_build_queue_manager.py:126-142).
# =========================================================================


class TestProj410TurnBoundaryRebind:
    """PROJ-410 Task 1.4 + Phase 4 Task 4.2 contract."""

    def _two_empire_screen(self):
        """Build a manager + screen where current_empire can be flipped
        between empire_1 and empire_2 by mutating an outer reference."""
        from game.ui.screens.strategy_build_queue_manager import StrategyBuildQueueManager

        empire_1 = MagicMock()
        empire_1.id = 1
        empire_1.empire_theme_id = "Federation"
        empire_2 = MagicMock()
        empire_2.id = 2
        empire_2.empire_theme_id = "Klingon"

        active = {"empire": empire_1}

        mock_screen = MagicMock()
        mock_screen.galaxy = MagicMock()
        mock_screen.facade = MagicMock()
        mock_screen.facade.session_meta.save_path = MagicMock(return_value="test_savegame")
        mock_screen.ui = MagicMock()
        mock_screen.ui.manager = MagicMock()
        mock_screen.selected_object = None
        mock_screen.build_queue_screen = None
        mock_screen.input_mapper = MagicMock()
        type(mock_screen).current_empire = property(lambda s: active["empire"])

        manager = StrategyBuildQueueManager(mock_screen)
        return manager, mock_screen, empire_1, empire_2, active

    # PROJ-479 Task 1.13: `test_open_after_active_player_change_calls_on_active_player_changed`
    # was merged into `test_issue17_player_turn_change_flush_invokes_invalidate_widget_caches`
    # below — both did the same flip-empire-then-call-twice + assert
    # on_active_player_changed.assert_called_once() pattern. The kept test
    # carries the additional Issue #17 invalidate-widget-cache documentation.

    def test_open_rebinds_cached_screen_empire_galaxy_facade_each_open(self):
        """Every _open_build_queue() must rebind cached_screen.empire,
        .galaxy, and .facade to the current screen's values BEFORE
        open_for_yard() runs.

        FAILS today: the existing rebind path at
        strategy_build_queue_manager.py:126-142 only sets design_library,
        design_loader, and portrait_loader. Phase 4 Task 4.2.
        """
        manager, screen, empire_1, empire_2, active = self._two_empire_screen()

        cached_screen = MagicMock()
        screen.build_queue_screen = cached_screen

        # Active empire is empire_1 initially. Switch to empire_2.
        active["empire"] = empire_2

        from game.strategy.data.planet import Planet
        planet_e2 = MagicMock(spec=Planet)
        planet_e2.owner_id = 2
        planet_e2.name = "Empire 2 Planet"
        screen.selected_object = planet_e2
        screen._get_object_asset = MagicMock(return_value=None)
        screen.world.system_for_object.return_value = None

        with patch("game.ui.screens.strategy_build_queue_manager.BuildQueueScreen"), \
             patch("game.ui.screens.strategy_build_queue_manager.BuildQueuePortraitLoader"), \
             patch("game.ui.screens.strategy_build_queue_manager.DesignLoaderAdapter"), \
             patch("game.ui.screens.strategy_build_queue_manager.BuildQueuePortraitLoader"), \
             patch("game.ui.screens.strategy_build_queue_manager.is_planet", return_value=True):
            manager.on_build_yard_click()

        # Rebind contract: empire, galaxy, facade reflect current values.
        assert cached_screen.empire is empire_2, (
            f"PROJ-410 Phase 4 Task 4.2: cached_screen.empire must be rebound "
            f"to current empire (empire_2). Got {cached_screen.empire!r}."
        )
        assert cached_screen.world is screen.world, (
            "PROJ-410 Phase 4 Task 4.2: cached_screen.world must be rebound "
            "to current screen.world."
        )
        assert cached_screen.facade is screen.facade, (
            "PROJ-410 Phase 4 Task 4.2: cached_screen.facade must be rebound "
            "to current screen.facade."
        )

    def test_open_with_unchanged_empire_does_not_call_on_active_player_changed(self):
        """When the active empire is unchanged across two opens, the manager
        must NOT call on_active_player_changed() on the cached screen.

        Locks the polled-comparison semantics: the hook only fires on
        actual player change, not on every open. Phase 4 Task 4.2.
        """
        manager, screen, empire_1, empire_2, active = self._two_empire_screen()

        cached_screen = MagicMock()
        cached_screen.on_active_player_changed = MagicMock()
        screen.build_queue_screen = cached_screen

        from game.strategy.data.planet import Planet
        planet_e1 = MagicMock(spec=Planet)
        planet_e1.owner_id = 1
        planet_e1.name = "Empire 1 Planet"
        screen.selected_object = planet_e1
        screen._get_object_asset = MagicMock(return_value=None)
        screen.world.system_for_object.return_value = None

        with patch("game.ui.screens.strategy_build_queue_manager.BuildQueueScreen"), \
             patch("game.ui.screens.strategy_build_queue_manager.BuildQueuePortraitLoader"), \
             patch("game.ui.screens.strategy_build_queue_manager.DesignLoaderAdapter"), \
             patch("game.ui.screens.strategy_build_queue_manager.BuildQueuePortraitLoader"), \
             patch("game.ui.screens.strategy_build_queue_manager.is_planet", return_value=True):
            # Two opens with the same active empire.
            manager.on_build_yard_click()
            manager.on_build_yard_click()

        cached_screen.on_active_player_changed.assert_not_called()

    def test_issue17_player_turn_change_flush_invokes_invalidate_widget_caches(self):
        """Issue #17: the A-hook player flush path goes through
        ``BuildQueueScreen.on_active_player_changed()`` which calls
        ``panels.virtual_table.invalidate_widget_caches()``. Issue #17's
        fix extends ``invalidate_widget_caches`` to clear pygame_gui
        widget content (set_text(""), set_image(blank)) in addition to
        cache attrs — so this manager-level test pins that on
        empire-change, the cached screen's flush path is invoked, which
        in turn triggers the (now content-clearing) invalidation.

        Combined with the VirtualTable-level test
        (``TestIssue17InvalidateClearsWidgetContent``) this guarantees
        end-to-end coverage of the turn-change scenario without needing
        a full integration test.
        """
        manager, screen, empire_1, empire_2, active = self._two_empire_screen()

        cached_screen = MagicMock()
        cached_screen.on_active_player_changed = MagicMock()
        screen.build_queue_screen = cached_screen

        from game.strategy.data.planet import Planet
        planet_e1 = MagicMock(spec=Planet)
        planet_e1.owner_id = 1
        planet_e1.name = "Empire 1 Planet"
        screen.selected_object = planet_e1
        screen._get_object_asset = MagicMock(return_value=None)
        screen.world.system_for_object.return_value = None

        with patch("game.ui.screens.strategy_build_queue_manager.BuildQueueScreen"), \
             patch("game.ui.screens.strategy_build_queue_manager.BuildQueuePortraitLoader"), \
             patch("game.ui.screens.strategy_build_queue_manager.DesignLoaderAdapter"), \
             patch("game.ui.screens.strategy_build_queue_manager.BuildQueuePortraitLoader"), \
             patch("game.ui.screens.strategy_build_queue_manager.is_planet", return_value=True):
            # First open under empire_1 — seeds _last_active_empire_id.
            manager.on_build_yard_click()
            cached_screen.on_active_player_changed.reset_mock()

            # Active empire flips to empire_2.
            active["empire"] = empire_2
            planet_e2 = MagicMock(spec=Planet)
            planet_e2.owner_id = 2
            planet_e2.name = "Empire 2 Planet"
            screen.selected_object = planet_e2

            # Second open under empire_2 — A-hook must fire.
            manager.on_build_yard_click()

        cached_screen.on_active_player_changed.assert_called_once(), (
            "Issue #17: on player turn-change the A-hook "
            "(on_active_player_changed) must fire. The screen-level "
            "implementation calls panels.virtual_table.invalidate_widget_caches() "
            "which (post issue #17 fix) clears widget content too — "
            "preventing previous-player rows from re-appearing under "
            "pygame_gui's UIPanel.show(show_contents=True) recursive un-hide."
        )
