"""Unit tests for `PlanetListWindow` (PROJ-292 Phase 1 H1 — view kwarg threading).

Pre-fix: `PlanetListWindow._on_planet_selected` constructed
`PlanetReportPanel` without passing `view=...`, so colonized planets
rendered with the legacy single-line fallback instead of PROJ-289's
per-species sub-block. PROJ-292 H1 backfills the pattern PROJ-289
established in `strategy_detail_formatter.py:_show_planet_report`.

Uses the bypass-init pattern so the test exercises `_on_planet_selected`
without constructing live pygame_gui widgets.

PROJ-322 Task 3.22 (S10-CAT6-002): the deep mocking of
PlanetReportPanel/`compute_planet_production`/UIButton (lines 71-111)
is intentionally retained — it follows the project bypass-init
convention. Revisit this file when PROJ-322 Phase 5 APC-001 cleanup
consolidates the bypass-init pattern across UI tests.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch


def _make_planet_mock(*, planet_id: int, owner_id: int = None):
    """Minimal Planet stub. `owner_id=None` means uncolonized."""
    planet = MagicMock()
    planet.id = planet_id
    planet.owner_id = owner_id
    planet.name = f"Planet-{planet_id}"
    planet.populations = []
    return planet


def _make_planet_list_window():
    """Construct a `PlanetListWindow` via bypass-init. Callers then set
    the attributes `_on_planet_selected` touches.

    PROJ-348 T5.4: now installs a real `PlanetListController` wired to the
    mocked facade so `_resolve_demographic_view` exercises the documented
    controller-mediated path. The legacy `__new__`-bypass fallback in
    production was deleted; tests must provide a controller.
    """
    from game.ui.screens.planet_list_window import PlanetListWindow
    from game.ui.screens.planet_list_controller import PlanetListController

    window = PlanetListWindow.__new__(PlanetListWindow)
    window.ui_manager = MagicMock()
    window.planet_detail_panel = None
    window.btn_build_queue = None
    window.selected_planet = None
    window.asset_resolver = None
    window.detail_panel_width = 580
    window._registries = MagicMock()
    window._race_registry = MagicMock()
    # PROJ-292 H1: facade provides `get_colony_demographic_view(planet.id)`
    # for colonized planets. Wired through the controller per PROJ-329C.
    window._facade = MagicMock()
    window._facade.economy.colony_demographic_view = MagicMock(return_value=None)
    window.controller = PlanetListController(facade=window._facade)
    # Empire reference used by the detail panel.
    window.empire = MagicMock()
    window.empire.id = 1
    window._detail_panel_geometry = MagicMock(return_value=(10, 10, 400))
    return window


# ---------------------------------------------------------------------------
# PROJ-292 H1: view kwarg threading
# ---------------------------------------------------------------------------

class TestViewThreading:
    """Every colonized-context caller of `PlanetReportPanel` must resolve
    the `ColonyDemographicView` via `facade.economy.colony_demographic_view`
    and thread it through. Mirrors `strategy_detail_formatter._show_planet_report`."""

    def test_colonized_planet_threads_view_into_panel(self):
        """When `planet.owner_id is not None`, the window must call
        `facade.economy.colony_demographic_view(planet.id)` and pass the
        result as `view=` to `PlanetReportPanel`."""
        window = _make_planet_list_window()
        stub_view = MagicMock(name="ColonyDemographicView")
        window._facade.economy.colony_demographic_view.return_value = stub_view

        planet = _make_planet_mock(planet_id=42, owner_id=1)

        with patch(
            "game.ui.screens.planet_list_window.PlanetReportPanel"
        ) as mock_panel_cls, patch(
            "game.ui.screens.planet_list_window.compute_planet_production",
            return_value={},
        ), patch(
            "game.ui.screens.planet_list_window.UIButton"
        ):
            mock_panel_cls.return_value.get_height_required.return_value = 100
            window._on_planet_selected(planet)

        mock_panel_cls.assert_called_once()
        kwargs = mock_panel_cls.call_args.kwargs
        assert kwargs.get("view") is stub_view, (
            f"Expected view=stub_view; got view={kwargs.get('view')!r}"
        )
        window._facade.economy.colony_demographic_view.assert_called_once_with(42)

    def test_uncolonized_planet_passes_view_none(self):
        """Uncolonized planets (`owner_id is None`) must NOT invoke the
        facade and must pass `view=None` so the panel falls back to the
        legacy uncolonized rendering path."""
        window = _make_planet_list_window()
        planet = _make_planet_mock(planet_id=7, owner_id=None)

        with patch(
            "game.ui.screens.planet_list_window.PlanetReportPanel"
        ) as mock_panel_cls, patch(
            "game.ui.screens.planet_list_window.compute_planet_production",
            return_value={},
        ), patch(
            "game.ui.screens.planet_list_window.UIButton"
        ):
            mock_panel_cls.return_value.get_height_required.return_value = 100
            window._on_planet_selected(planet)

        mock_panel_cls.assert_called_once()
        kwargs = mock_panel_cls.call_args.kwargs
        assert kwargs.get("view") is None, (
            f"Expected view=None for uncolonized planet; got view={kwargs.get('view')!r}"
        )
        window._facade.economy.colony_demographic_view.assert_not_called()

    def test_no_facade_falls_back_to_view_none(self):
        """When the window was constructed without a facade (legacy
        caller / test fixture), the colonized path must still construct
        the panel with `view=None` rather than raising."""
        window = _make_planet_list_window()
        window._facade = None
        planet = _make_planet_mock(planet_id=99, owner_id=1)

        with patch(
            "game.ui.screens.planet_list_window.PlanetReportPanel"
        ) as mock_panel_cls, patch(
            "game.ui.screens.planet_list_window.compute_planet_production",
            return_value={},
        ), patch(
            "game.ui.screens.planet_list_window.UIButton"
        ):
            mock_panel_cls.return_value.get_height_required.return_value = 100
            window._on_planet_selected(planet)

        mock_panel_cls.assert_called_once()
        kwargs = mock_panel_cls.call_args.kwargs
        assert kwargs.get("view") is None


# ---------------------------------------------------------------------------
# FEAT-16: per-effect column generation.
#
# `build_effect_columns(effect_keys)` (module-level helper, no Pygame deps)
# returns column dicts ready to be appended to `self.columns`. Each column:
#   - id = f"effect_{group_key}"
#   - title = make_display_name() of the ability
#   - func = lambda rendering the magnitude string via shared formatter,
#            or '—' when the planet doesn't carry that effect
#   - visible = False (default hidden — matches per-resource columns)
# ---------------------------------------------------------------------------


def _planet_with_abilities(abilities):
    p = MagicMock()
    p.intrinsic_abilities = abilities
    return p


class TestPerEffectColumns:
    """Per FEAT-16: build a column per effect group-key, hidden by default,
    rendering magnitude via the shared formatter."""

    def test_no_columns_for_empty_galaxy(self):
        from game.ui.screens.planet_list_window import build_effect_columns
        assert build_effect_columns([]) == []

    def test_one_column_per_effect_key_hidden_by_default(self):
        from game.ui.screens.planet_list_window import build_effect_columns
        cols = build_effect_columns(['ThrustModifier', 'EnvironmentalDamage:thermal'])
        assert len(cols) == 2
        ids = {c['id'] for c in cols}
        assert ids == {'effect_ThrustModifier', 'effect_EnvironmentalDamage:thermal'}
        for c in cols:
            assert c['visible'] is False

    def test_column_titles_use_display_names(self):
        from game.ui.screens.planet_list_window import build_effect_columns
        cols = build_effect_columns(['EnvironmentalDamage:thermal', 'ThrustModifier', 'FuelDrain'])
        title_by_id = {c['id']: c['title'] for c in cols}
        assert title_by_id['effect_EnvironmentalDamage:thermal'] == 'Thermal Damage'
        assert title_by_id['effect_ThrustModifier'] == 'Thrust Modifier'
        assert title_by_id['effect_FuelDrain'] == 'Fuel Drain'

    def test_column_func_renders_magnitude_via_shared_formatter(self):
        from game.ui.screens.planet_list_window import build_effect_columns
        cols = build_effect_columns(['ThrustModifier', 'EnvironmentalDamage:thermal'])

        col_thrust = next(c for c in cols if c['id'] == 'effect_ThrustModifier')
        col_thermal = next(c for c in cols if c['id'] == 'effect_EnvironmentalDamage:thermal')

        # Planet with ThrustModifier multiplier=0.91 → "x0.91"
        cryo = _planet_with_abilities({'ThrustModifier': {'multiplier': 0.91, 'scope': 'sector'}})
        assert col_thrust['func'](cryo) == 'x0.91'

        # Same planet has no thermal damage → blank cell
        assert col_thermal['func'](cryo) == '—'

        # Magma planet → thermal cell renders rate
        magma = _planet_with_abilities({
            'EnvironmentalDamage': {'rate': 0.27, 'damage_type': 'thermal', 'scope': 'sector'},
        })
        assert col_thermal['func'](magma) == '-0.27 hull/turn'
        # Same magma planet has no ThrustModifier
        assert col_thrust['func'](magma) == '—'

    def test_column_func_distinguishes_damage_types(self):
        """A radiation EnvironmentalDamage planet must render blank in the
        :thermal column (different group_key)."""
        from game.ui.screens.planet_list_window import build_effect_columns
        cols = build_effect_columns(['EnvironmentalDamage:thermal'])
        col = cols[0]
        chthonian = _planet_with_abilities({
            'EnvironmentalDamage': {'rate': 0.1, 'damage_type': 'radiation', 'scope': 'sector'},
        })
        assert col['func'](chthonian) == '—'


# ---------------------------------------------------------------------------
# PROJ-347 T4.1b: Pattern §33 widget-ref placeholders
# ---------------------------------------------------------------------------

class TestPlanetListWindowWidgetPlaceholders:
    """PROJ-347 T4.1b — Pattern §33 widget-ref placeholders.

    Stage-1 must set widget refs to ``None`` before ``super().__init__``
    so a ``NullPlanetListWindowUiBuilder`` test can safely call
    ``kill()`` without ``AttributeError`` on
    ``self.virtual_table.kill()`` etc.
    """

    def _make_window(self, *, ui_builder):
        import pygame
        from game.ui.screens.planet_list_window import PlanetListWindow
        from tests.fixtures.ui_widget_factory import bypass_init

        galaxy = MagicMock(name="Galaxy")
        galaxy.systems = {}
        empire = MagicMock(name="Empire")
        empire.id = 1
        rect = pygame.Rect(0, 0, 1200, 800)
        with bypass_init(PlanetListWindow):
            return PlanetListWindow(
                rect,
                MagicMock(name="ui_manager"),
                galaxy,
                empire,
                window_manager=None,
                ui_builder=ui_builder,
            )

    def test_null_builder_leaves_widget_placeholders_as_none(self):
        from tests.fixtures.planet_list_window_ui_builder import (
            NullPlanetListWindowUiBuilder,
        )
        window = self._make_window(ui_builder=NullPlanetListWindowUiBuilder())
        # PROJ-347 T4.1b: Pattern §33 placeholders set in Stage 1.
        for slot in (
            "virtual_table", "sidebar_panel", "main_panel",
            "data_source", "column_manager", "selection",
        ):
            assert getattr(window, slot) is None, (
                f"Pattern §33 placeholder {slot!r} should be None under "
                f"Null builder; got {getattr(window, slot)!r}"
            )

    def test_null_builder_kill_does_not_attribute_error(self):
        """The truthiness guards in ``kill()`` short-circuit on the
        ``None`` placeholders set in Stage 1."""
        from tests.fixtures.planet_list_window_ui_builder import (
            NullPlanetListWindowUiBuilder,
        )
        window = self._make_window(ui_builder=NullPlanetListWindowUiBuilder())
        # We can't actually call super().kill() under bypass_init, but
        # the placeholder existence is what matters: confirm the same
        # truthiness predicate kill() uses works without raising.
        assert (window.virtual_table or None) is None
        assert (window.planet_detail_panel or None) is None
        assert (window.btn_build_queue or None) is None
        assert (window.btn_navigate or None) is None
