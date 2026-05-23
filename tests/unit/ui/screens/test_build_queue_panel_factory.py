"""Unit tests for `BuildQueuePanelFactory` (PROJ-292 Phase 1 H1 — view kwarg threading).

Pre-fix: `BuildQueuePanelFactory._create_context_report_panel` constructed
`PlanetReportPanel` without passing `view=...`, so the BuildQueueScreen
context-report always rendered with the legacy single-line fallback —
PROJ-289's per-species sub-block was invisible in this context despite
BuildQueueScreen ONLY ever showing colonized planets. PROJ-292 H1
mirrors the pattern PROJ-289 established in
`strategy_detail_formatter._show_planet_report`.
"""
from __future__ import annotations

import pytest

from unittest.mock import MagicMock, patch


@pytest.fixture
def factory_for_create_all_panels():
    """PROJ-494 T2.1: shared factory configured for create_all_panels exercises.

    Stands up a bypass-init `BuildQueuePanelFactory` with all UI primitives
    available for patching. Set up for a fleet-context build (avoids the
    PlanetReportPanel branch) — tests that need a planet context can mutate
    `factory.build_context.context_type` directly.
    """
    from game.ui.screens.build_queue_panel_factory import BuildQueuePanelFactory

    factory = BuildQueuePanelFactory.__new__(BuildQueuePanelFactory)
    factory.manager = MagicMock()
    # PROJ-396 MAJ-003: factory has no .session field; facade is the
    # canonical surface for registries / turn.
    factory._facade = MagicMock()
    factory._facade.economy.registries = MagicMock(return_value=MagicMock())
    factory._facade.session_meta.turn_number = MagicMock(return_value=0)
    factory._empire = None

    build_context = MagicMock()
    build_context.context_type = "fleet"  # avoid PlanetReportPanel branch
    build_context.id = 1
    build_context.owner_id = 1
    build_context.name = "Test Fleet"
    build_context.has_space_shipyard = True
    build_context.construction_queue = []
    build_context.ships = []
    factory.build_context = build_context

    factory.queue_sources = []
    factory.portrait_loader = MagicMock()
    factory.portrait_loader.load_resource_icons.return_value = {}
    factory.portrait_surface = None
    factory.on_queue_selection_changed = MagicMock()

    factory.screen_width = 1600
    factory.screen_height = 900

    factory.resource_icons = {}
    return factory


def _make_factory():
    """Bypass-init a `BuildQueuePanelFactory`. Callers set attributes
    individually so we can exercise `_create_context_report_panel`
    without constructing queue sources, portrait loaders, etc."""
    from game.ui.screens.build_queue_panel_factory import BuildQueuePanelFactory

    factory = BuildQueuePanelFactory.__new__(BuildQueuePanelFactory)
    factory.manager = MagicMock()

    build_context = MagicMock()
    build_context.context_type = "planet"
    build_context.id = 123
    build_context.owner_id = 1
    build_context.name = "Earth"
    factory.build_context = build_context

    # PROJ-396 MAJ-003: factory.session removed; registries / turn route
    # through facade. ``_empire`` replaces the previous session reach-through.
    factory._empire = MagicMock()
    factory._empire.resource_pool = MagicMock()

    factory.portrait_surface = None
    factory.screen_height = 900
    factory.screen_width = 1600

    # PROJ-292 H1: facade provides `get_colony_demographic_view(planet.id)`.
    # PROJ-396 MAJ-003: facade also provides get_registries / get_turn_number.
    factory._facade = MagicMock()
    factory._facade.economy.colony_demographic_view = MagicMock(return_value=None)
    factory._facade.economy.registries = MagicMock(return_value=MagicMock())
    factory._facade.session_meta.turn_number = MagicMock(return_value=0)
    return factory


class TestViewThreading:
    """`_create_context_report_panel` must resolve a
    `ColonyDemographicView` via the facade for colonized planets and
    thread it into `PlanetReportPanel`. BuildQueueScreen only ever opens
    on colonized planets, so the view should essentially always be
    populated in practice."""

    def test_colonized_planet_threads_view_into_panel(self):
        factory = _make_factory()
        stub_view = MagicMock(name="ColonyDemographicView")
        factory._facade.economy.colony_demographic_view.return_value = stub_view

        with patch(
            "game.ui.screens.build_queue_panel_factory.PlanetReportPanel"
        ) as mock_panel_cls, patch(
            "game.ui.screens.build_queue_panel_factory.compute_planet_production",
            return_value={},
        ):
            factory._create_context_report_panel(container=MagicMock())

        mock_panel_cls.assert_called_once()
        kwargs = mock_panel_cls.call_args.kwargs
        assert kwargs.get("view") is stub_view, (
            f"Expected view=stub_view; got view={kwargs.get('view')!r}"
        )
        factory._facade.economy.colony_demographic_view.assert_called_once_with(123)

    def test_uncolonized_planet_passes_view_none(self):
        """Uncolonized planets (``owner_id is None``) skip the facade
        lookup and render with ``view=None`` — the per-species sub-block
        only applies to colonized planets.

        PROJ-396 MAJ-003: replaces the now-impossible
        ``test_no_facade_falls_back_to_view_none`` (facade is a required
        ctor kwarg post-MAJ-003)."""
        factory = _make_factory()
        factory.build_context.owner_id = None

        with patch(
            "game.ui.screens.build_queue_panel_factory.PlanetReportPanel"
        ) as mock_panel_cls, patch(
            "game.ui.screens.build_queue_panel_factory.compute_planet_production",
            return_value={},
        ):
            factory._create_context_report_panel(container=MagicMock())

        mock_panel_cls.assert_called_once()
        kwargs = mock_panel_cls.call_args.kwargs
        assert kwargs.get("view") is None
        factory._facade.economy.colony_demographic_view.assert_not_called()

    def test_fleet_context_does_not_invoke_facade_or_panel(self):
        """When the build context is a fleet (no planet rendering),
        `PlanetReportPanel` is not constructed and the facade is not
        consulted — the existing fleet-info panel path is preserved."""
        factory = _make_factory()
        factory.build_context.context_type = "fleet"
        factory._create_fleet_info_panel = MagicMock(return_value=MagicMock())

        with patch(
            "game.ui.screens.build_queue_panel_factory.PlanetReportPanel"
        ) as mock_panel_cls:
            factory._create_context_report_panel(container=MagicMock())

        mock_panel_cls.assert_not_called()
        factory._facade.economy.colony_demographic_view.assert_not_called()


# ===========================================================================
# PROJ-373 Phase 4 — Scoped fast-panel object_id
#
# Every UIPanel created by BuildQueuePanelFactory should opt into
# `@fast_panel` so the global `panel` rounded-corner shape is replaced by
# the scoped `panel.@fast_panel` rectangle shape — eliminates ~3s of
# pygame_gui anti-alias rasterization on first build-queue open without
# touching any other screen's visuals.
# ===========================================================================


class TestScopedFastPanelObjectId:
    """PROJ-373 Phase 4: every UIPanel in the factory opts into @fast_panel.

    PROJ-494 T2.1: factory construction moved to the module-level
    `factory_for_create_all_panels` fixture.
    """

    def test_every_uipanel_in_factory_uses_fast_panel_class_id(self, factory_for_create_all_panels):
        """Every `ui.UIPanel(...)` call inside the factory passes
        `object_id="@fast_panel"` so the scoped rectangle shape applies."""
        factory = factory_for_create_all_panels
        with patch(
            "game.ui.screens.build_queue_panel_factory.ui.UIPanel"
        ) as mock_panel, patch(
            "game.ui.screens.build_queue_panel_factory.ui.UIScrollingContainer"
        ), patch(
            "game.ui.screens.build_queue_panel_factory.ui.UITextBox"
        ), patch(
            "game.ui.screens.build_queue_panel_factory.ui.UIButton"
        ), patch(
            "game.ui.screens.build_queue_panel_factory.ui.UILabel"
        ), patch(
            "game.ui.screens.build_queue_panel_factory.BuildQueueSelector"
        ), patch(
            "game.ui.screens.build_queue_panel_factory.DesignReportPanel"
        ), patch(
            "game.ui.screens.build_queue_panel_factory.VirtualTable"
        ), patch(
            "game.ui.screens.build_queue_panel_factory.TableColumnManager"
        ), patch(
            "game.ui.screens.build_queue_panel_factory.BuildQueueQueueDataSource"
        ), patch(
            "game.ui.screens.build_queue_panel_factory.SingleSelect"
        ):
            factory.create_all_panels(format_empire_resources=lambda _e: "")

        assert mock_panel.call_count >= 5, (
            f"Expected ≥5 UIPanel constructions; got {mock_panel.call_count}"
        )
        for call in mock_panel.call_args_list:
            assert call.kwargs.get("object_id") == "@fast_panel", (
                f"UIPanel called without object_id='@fast_panel': "
                f"args={call.args}, kwargs={call.kwargs}"
            )

    def test_theme_json_has_fast_panel_block_with_rectangle_shape(self):
        """Sanity-check that the data file actually defines the scoped
        block referenced by the factory.

        PROJ-494 T4.6: was a 5-level `os.path.dirname` chain to reach
        `data/builder_theme.json`. Replaced with the canonical `Paths.data_dir()`
        accessor — a single source of truth for repo-relative file locations.
        """
        import json
        from game.core.paths import Paths

        theme_path = Paths.get_data_dir() / "builder_theme.json"
        with open(theme_path) as f:
            theme = json.load(f)

        assert "panel.@fast_panel" in theme, (
            "panel.@fast_panel block missing from data/builder_theme.json"
        )
        block = theme["panel.@fast_panel"]
        assert block.get("misc", {}).get("shape") == "rectangle", (
            f"@fast_panel must use shape='rectangle'; got "
            f"{block.get('misc', {}).get('shape')!r}"
        )
