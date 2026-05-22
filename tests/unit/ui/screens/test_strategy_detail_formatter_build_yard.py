"""PROJ-475 Phase 2 Task 2.7 — Build-Yard button gate reads facade.has_build_yard.

``_show_planet_report`` renders a live ``Planet``; the Build-Yard button gate now
reads the facade-projected ``has_build_yard`` off ``facade.planets.get(planet_id)``
instead of importing ``colony_has_planetary_yard``.
"""

from __future__ import annotations

import ast
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pygame
import pytest

from game.ui.screens.strategy_detail_formatter import StrategyDetailFormatter

_REPO_ROOT = Path(__file__).resolve().parents[4]


def _formatter_with_facade(has_build_yard: bool):
    scene = MagicMock()
    scene.current_empire.id = 1
    scene.facade.planets.get.return_value = SimpleNamespace(
        has_build_yard=has_build_yard
    )
    widgets = MagicMock()
    widgets.spectrum_graph.render = MagicMock(return_value=pygame.Surface((10, 10)))
    detail_panel = MagicMock()
    detail_panel.rect.height = 600
    formatter = StrategyDetailFormatter(
        scene, MagicMock(), detail_panel, widgets,
        pygame.Rect(0, 0, 100, 100), (800, 600),
    )
    # panel_max_height = min(detail_panel.height-60, btn_build_yard.y-20) needs ints.
    formatter.btn_build_yard.relative_rect.y = 400
    return formatter, scene


class TestBuildYardGate:
    @pytest.mark.parametrize("has_yard", [True, False])
    def test_gate_reads_facade_has_build_yard(self, has_yard) -> None:
        formatter, scene = _formatter_with_facade(has_yard)
        formatter.compute_planet_production = MagicMock(return_value=None)
        planet = SimpleNamespace(
            id=42, owner_id=1, has_space_shipyard=False, name="P",
        )

        with patch(
            "game.ui.screens.strategy_detail_formatter.PlanetReportPanel"
        ):
            formatter._show_planet_report(
                planet, portrait_surface=None, current_empire_id=1
            )

        scene.facade.planets.get.assert_called_with(42)
        if has_yard:
            formatter.btn_build_yard.show.assert_called()
        else:
            formatter.btn_build_yard.show.assert_not_called()


def test_detail_formatter_does_not_import_colony_has_planetary_yard() -> None:
    src = (
        _REPO_ROOT / "game/ui/screens/strategy_detail_formatter.py"
    ).read_text(encoding="utf-8")
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                assert alias.name != "colony_has_planetary_yard", (
                    "strategy_detail_formatter must not import "
                    "colony_has_planetary_yard (PROJ-475 Task 2.7)"
                )
