"""Characterization tests for ``PlanetSelectionWindow`` (PROJ-329A
Phase 2 Task 2.3).

Pins the minimum-rect enforcement (950x650), label/selection_list/
btn_select widget construction, planet_detail_panel = None
initialization, callback wiring, and "Any Planet" button conditional
behavior.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pygame

from game.ui.screens.planet_selection_window import (
    MIN_WINDOW_HEIGHT,
    MIN_WINDOW_WIDTH,
    PlanetSelectionWindow,
)
from tests.fixtures.planet_selection_window_ui_builder import (
    MockPlanetSelectionWindowUiBuilder,
    NullPlanetSelectionWindowUiBuilder,
)
from tests.fixtures.ui_widget_factory import bypass_init


def _planet(name: str = "Earth"):
    """A planet-shaped MagicMock with the attributes the window reads."""
    p = MagicMock(name=f"Planet({name})")
    p.name = name
    p.image_id = None
    p.image_rotation = 0
    return p


def _make_window(
    planets,
    *,
    rect=None,
    callback=None,
    ui_builder=None,
    window_title="Select Planet to Colonize",
    list_label="Habitable bodies:",
    show_any_button=True,
    facade=None,
):
    """Construct a real ``PlanetSelectionWindow`` under ``bypass_init``."""
    if rect is None:
        rect = pygame.Rect(0, 0, 1000, 700)
    if ui_builder is None:
        ui_builder = MockPlanetSelectionWindowUiBuilder()
    if callback is None:
        callback = MagicMock()
    with bypass_init(PlanetSelectionWindow):
        return PlanetSelectionWindow(
            rect,
            MagicMock(name="ui_manager"),
            planets,
            callback,
            window_manager=None,
            window_title=window_title,
            list_label=list_label,
            show_any_button=show_any_button,
            ui_builder=ui_builder,
            facade=facade,
        )


class TestPlanetSelectionWindowInit:
    """Stage-1 cheap state survives bypass_init."""

    def test_stores_planets_reference(self):
        planets = [_planet("Earth"), _planet("Mars")]
        window = _make_window(planets)
        assert window.planets is planets

    def test_stores_callback(self):
        callback = MagicMock()
        window = _make_window([_planet()], callback=callback)
        assert window.callback is callback

    def test_window_init_bypassed_flag_set(self):
        window = _make_window([_planet()])
        assert window._window_init_bypassed is True

    def test_planet_detail_panel_starts_none(self):
        window = _make_window([_planet()])
        assert window.planet_detail_panel is None

    def test_selected_planet_starts_none(self):
        window = _make_window([_planet()])
        assert window.selected_planet is None

    def test_current_selection_name_starts_none(self):
        window = _make_window([_planet()])
        assert window.current_selection_name is None

    def test_stores_list_label(self):
        window = _make_window([_planet()], list_label="Targets:")
        assert window._list_label == "Targets:"

    def test_stores_show_any_button_true(self):
        window = _make_window([_planet()], show_any_button=True)
        assert window._show_any_button is True

    def test_stores_show_any_button_false(self):
        window = _make_window([_planet()], show_any_button=False)
        assert window._show_any_button is False


class TestMinimumRectEnforcement:
    """``__init__`` clamps the rect to at least 950x650 in Stage 1, before
    the shell is constructed."""

    def test_undersized_width_clamped_to_min(self):
        rect = pygame.Rect(0, 0, 100, 700)
        _make_window([_planet()], rect=rect)
        assert rect.width == MIN_WINDOW_WIDTH

    def test_undersized_height_clamped_to_min(self):
        rect = pygame.Rect(0, 0, 1000, 100)
        _make_window([_planet()], rect=rect)
        assert rect.height == MIN_WINDOW_HEIGHT

    def test_oversized_dimensions_preserved(self):
        rect = pygame.Rect(0, 0, 1500, 1200)
        _make_window([_planet()], rect=rect)
        assert rect.width == 1500
        assert rect.height == 1200


class TestUiBuilderConditionalAnyButton:
    """The Any-Planet button is conditionally constructed by the builder
    based on the Stage-1 ``_show_any_button`` flag."""

    def test_show_any_true_populates_btn_any(self):
        window = _make_window([_planet()], show_any_button=True)
        assert window.btn_any is not None

    def test_show_any_false_leaves_btn_any_none(self):
        window = _make_window([_planet()], show_any_button=False)
        assert window.btn_any is None

    def test_null_builder_leaves_widget_slots_unset(self):
        window = _make_window(
            [_planet()],
            ui_builder=NullPlanetSelectionWindowUiBuilder(),
        )
        # Stage-1 always initializes btn_any to None for safety.
        assert window.btn_any is None
        # Other widget slots are not set at all when null builder runs.
        assert not hasattr(window, "label")
        assert not hasattr(window, "selection_list")
        assert not hasattr(window, "btn_select")


class TestUpdateButtonDispatch:
    """``update()`` polls Confirm + Any-Planet buttons; valid presses
    invoke the callback (with the planet, or None for Any-Planet) and
    kill the window."""

    def test_confirm_with_valid_selection_invokes_callback_with_planet(self):
        earth, mars = _planet("Earth"), _planet("Mars")
        callback = MagicMock()
        window = _make_window([earth, mars], callback=callback)
        window.btn_select.check_pressed.return_value = True
        window.selection_list.get_single_selection.return_value = "Mars"
        # Pre-seed the selection-tracking attrs so update() skips the
        # PlanetReportPanel-creation branch (which needs self.rect, not
        # set under bypass per PROJ-325 PoC finding 1).
        window.current_selection_name = "Mars"
        window.selected_planet = mars

        with patch("pygame_gui.elements.UIWindow.update", return_value=None):
            with patch.object(window, "kill") as mock_kill:
                window.update(0.016)

        callback.assert_called_once_with(mars)
        mock_kill.assert_called_once()

    def test_confirm_without_selection_does_not_invoke_callback(self):
        callback = MagicMock()
        window = _make_window([_planet()], callback=callback)
        window.btn_select.check_pressed.return_value = True
        window.selection_list.get_single_selection.return_value = None
        # Pre-seed to skip the panel-creation branch (PROJ-325 finding 1).
        window.current_selection_name = None
        window.selected_planet = None

        with patch("pygame_gui.elements.UIWindow.update", return_value=None):
            with patch.object(window, "kill") as mock_kill:
                window.update(0.016)

        callback.assert_not_called()
        mock_kill.assert_not_called()

    def test_any_planet_invokes_callback_with_none(self):
        callback = MagicMock()
        window = _make_window([_planet()], callback=callback, show_any_button=True)
        window.btn_any.check_pressed.return_value = True
        # Skip the panel-creation branch (needs self.rect; bypass shell
        # does not assign it per PROJ-325 PoC finding 1).
        window.current_selection_name = None
        window.selected_planet = None

        with patch("pygame_gui.elements.UIWindow.update", return_value=None):
            with patch.object(window, "kill") as mock_kill:
                window.update(0.016)

        callback.assert_called_once_with(None)
        mock_kill.assert_called_once()


class TestFacadeThreading:
    """PROJ-408 C-04 / PROJ-397 Phase 3 Task 3.2:
    ``PlanetSelectionWindow`` MUST thread the optional ``facade`` kwarg
    into ``update()`` and use it to fetch a fresh
    ``ColonyDemographicView`` for colonized planets so the
    ``PlanetReportPanel`` renders the PROJ-289 per-species sub-block
    instead of legacy fallback layout.

    The PROJ-397 review flagged this path as covered only by UI-level
    tests at the boundary, never by a direct unit test on the window
    itself. These tests pin the threading in isolation.
    """

    def _colonized_planet(self, name="Earth", planet_id=7):
        p = _planet(name)
        p.id = planet_id
        p.owner_id = 1   # colonized
        return p

    def _uncolonized_planet(self, name="Mars", planet_id=11):
        p = _planet(name)
        p.id = planet_id
        p.owner_id = None
        return p

    def _arrange_for_panel_creation(self, window, planet):
        """Wire the window so ``update()`` falls into the
        ``PlanetReportPanel`` creation branch for the given planet."""
        # Make selection_list report a fresh selection.
        window.selection_list.get_single_selection.return_value = planet.name
        # Set both pre-seed slots to a different value so the "selection
        # changed" + "planet changed" branches both fire.
        window.current_selection_name = None
        window.selected_planet = None
        # ``bypass_init`` does not run UIWindow.__init__, so ``self.rect``
        # is unset. Production reads ``self.rect.width`` / ``.height``
        # in the panel-creation branch — provide a Stage-1-equivalent
        # rect directly. (The PROJ-325 PoC finding 1 noted by the
        # other tests in this module is the same constraint; those
        # tests skip the branch instead of arranging for it.)
        window._rect = pygame.Rect(0, 0, 1000, 700)

    def test_facade_stored_on_construction(self):
        """The ``facade`` kwarg lives on ``self._facade`` after
        construction (Stage-1 cheap-state assignment)."""
        facade = MagicMock(name="StrategySessionFacade")
        window = _make_window(
            [self._colonized_planet()],
            facade=facade,
        )
        assert window._facade is facade

    def test_facade_default_is_none_when_omitted(self):
        """Omitting ``facade`` leaves ``self._facade`` as None — legacy
        fixtures continue to work but the PROJ-289 layout is skipped."""
        window = _make_window([self._colonized_planet()])
        assert window._facade is None

    def test_update_fetches_demographic_view_for_colonized_planet(self):
        """When the selection changes to a colonized planet, ``update()``
        calls ``facade.economy.colony_demographic_view(planet.id)`` and
        threads the result into ``PlanetReportPanel(..., view=...)``."""
        sentinel_view = MagicMock(name="ColonyDemographicView")
        facade = MagicMock(name="StrategySessionFacade")
        facade.economy.colony_demographic_view = MagicMock(return_value=sentinel_view)

        earth = self._colonized_planet("Earth", planet_id=7)
        window = _make_window([earth], facade=facade)
        self._arrange_for_panel_creation(window, earth)

        # Patch dependencies the panel-creation branch reaches into:
        # PlanetReportPanel constructor, asset manager, and the parent
        # UIWindow.update.
        with patch(
            "game.ui.screens.planet_selection_window.PlanetReportPanel"
        ) as mock_panel_cls, patch(
            "game.ui.screens.planet_selection_window.get_default_asset_manager"
        ), patch("pygame_gui.elements.UIWindow.update", return_value=None):
            window.update(0.016)

        # PROJ-397 contract: facade is consulted with the planet id.
        facade.economy.colony_demographic_view.assert_called_once_with(7)

        # The fetched view is threaded into the report panel — proves
        # the result actually flows through the production path,
        # not just that the facade was called.
        assert mock_panel_cls.call_count == 1
        _, panel_kwargs = mock_panel_cls.call_args
        assert panel_kwargs["view"] is sentinel_view
        assert panel_kwargs["planet"] is earth

    def test_update_skips_facade_for_uncolonized_planet(self):
        """Uncolonized planets short-circuit before the facade is
        consulted (production comment at line 213-214)."""
        facade = MagicMock(name="StrategySessionFacade")
        facade.economy.colony_demographic_view = MagicMock()

        mars = self._uncolonized_planet("Mars", planet_id=11)
        window = _make_window([mars], facade=facade)
        self._arrange_for_panel_creation(window, mars)

        with patch(
            "game.ui.screens.planet_selection_window.PlanetReportPanel"
        ) as mock_panel_cls, patch(
            "game.ui.screens.planet_selection_window.get_default_asset_manager"
        ), patch("pygame_gui.elements.UIWindow.update", return_value=None):
            window.update(0.016)

        facade.economy.colony_demographic_view.assert_not_called()
        # Panel still created, but with view=None.
        assert mock_panel_cls.call_count == 1
        _, panel_kwargs = mock_panel_cls.call_args
        assert panel_kwargs["view"] is None

    def test_update_passes_view_none_when_facade_is_none(self):
        """Legacy callers without a facade still get a panel, with
        ``view=None`` — the data-rich PROJ-289 layout is skipped but no
        legacy fallback rendering remains."""
        earth = self._colonized_planet("Earth", planet_id=7)
        window = _make_window([earth], facade=None)
        self._arrange_for_panel_creation(window, earth)

        with patch(
            "game.ui.screens.planet_selection_window.PlanetReportPanel"
        ) as mock_panel_cls, patch(
            "game.ui.screens.planet_selection_window.get_default_asset_manager"
        ), patch("pygame_gui.elements.UIWindow.update", return_value=None):
            window.update(0.016)

        assert mock_panel_cls.call_count == 1
        _, panel_kwargs = mock_panel_cls.call_args
        assert panel_kwargs["view"] is None


# ---------------------------------------------------------------------------
# Issue #24: button geometry must fit inside the content-area container,
# not the outer (shadow-inclusive) window rect.
# ---------------------------------------------------------------------------

class TestPlanetSelectionWindowButtonGeometry:
    """Issue #24 regression (sibling fix): Confirm and 'Any Planet' buttons
    must render inside the pygame_gui window's content-area container
    (``get_container().rect``), not the outer ``screen.rect`` which is
    inflated by ``shadow_width`` on each side and includes the title bar.
    """

    def test_buttons_fit_within_container_content_area(self):
        """Confirm/Any buttons must render entirely inside the content
        container at the production spawn size (950x650).
        """
        import pygame_gui

        pygame.display.set_mode((1280, 800))
        ui_manager = pygame_gui.UIManager((1280, 800))

        planets = [_planet("Earth"), _planet("Mars")]
        rect = pygame.Rect(50, 50, 950, 650)
        window = PlanetSelectionWindow(
            rect,
            ui_manager,
            planets,
            MagicMock(),
            window_manager=None,
        )

        container_rect = window.get_container().rect
        assert window.btn_select.relative_rect.bottom <= container_rect.height, (
            f"Confirm button bottom ({window.btn_select.relative_rect.bottom}) "
            f"exceeds container content height ({container_rect.height}); "
            f"button is clipped/invisible (issue #24)."
        )
        assert window.btn_select.relative_rect.right <= container_rect.width
        assert window.btn_select.relative_rect.left >= 0

        # "Any Planet" button is optional but defaults to shown.
        if window.btn_any is not None:
            assert window.btn_any.relative_rect.bottom <= container_rect.height, (
                f"Any Planet button bottom ({window.btn_any.relative_rect.bottom}) "
                f"exceeds container content height ({container_rect.height}); "
                f"button is clipped/invisible (issue #24)."
            )
            assert window.btn_any.relative_rect.right <= container_rect.width
            assert window.btn_any.relative_rect.left >= 0
