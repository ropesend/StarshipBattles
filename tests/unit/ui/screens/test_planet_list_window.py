"""Unit tests for `PlanetListWindow` (PROJ-292 Phase 1 H1 — view kwarg threading).

Pre-fix: `PlanetListWindow._on_planet_selected` constructed
`PlanetReportPanel` without passing `view=...`, so colonized planets
rendered with the legacy single-line fallback instead of PROJ-289's
per-species sub-block. PROJ-292 H1 backfills the pattern PROJ-289
established in `strategy_detail_formatter.py:_show_planet_report`.

Uses the bypass-init pattern so the test exercises `_on_planet_selected`
without constructing live pygame_gui widgets.
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
    the attributes `_on_planet_selected` touches."""
    from game.ui.screens.planet_list_window import PlanetListWindow

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
    # for colonized planets.
    window._facade = MagicMock()
    window._facade.get_colony_demographic_view = MagicMock(return_value=None)
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
    the `ColonyDemographicView` via `facade.get_colony_demographic_view`
    and thread it through. Mirrors `strategy_detail_formatter._show_planet_report`."""

    def test_colonized_planet_threads_view_into_panel(self):
        """When `planet.owner_id is not None`, the window must call
        `facade.get_colony_demographic_view(planet.id)` and pass the
        result as `view=` to `PlanetReportPanel`."""
        window = _make_planet_list_window()
        stub_view = MagicMock(name="ColonyDemographicView")
        window._facade.get_colony_demographic_view.return_value = stub_view

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
        window._facade.get_colony_demographic_view.assert_called_once_with(42)

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
        window._facade.get_colony_demographic_view.assert_not_called()

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
