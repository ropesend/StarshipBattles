"""Characterization tests for BaseGallery (PROJ-340).

Pins observed widget-construction and click-routing behavior of the
abstract gallery base at ``game/ui/panels/base_gallery.py``.

``pygame_gui`` widget classes are patched so construction is inert;
assertions inspect call shapes rather than rendered pixels (PROJ-340
D-005).
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pygame
import pytest

# Module-import: we rely on the production module being importable
# under test so the patch targets resolve.
from game.ui.panels import base_gallery as bg_module
from game.ui.panels.base_gallery import BaseGallery


class _FakeGallery(BaseGallery):
    """Minimal concrete subclass with all 9 abstracts implemented."""

    def __init__(self, *args, assets=None, current_selection=None, **kwargs):
        # Deferred so the abstract resolution happens at construction time.
        self._assets = assets if assets is not None else []
        self._current_selection = current_selection
        self.set_calls: list[str] = []
        self.preview_calls: list[str] = []
        super().__init__(*args, **kwargs)

    def _get_label_text(self) -> str:
        return "Pick:"

    def _get_thumb_size(self) -> int:
        return 50

    def _get_preview_size(self) -> int:
        return 200

    def _get_object_id_prefix(self) -> str:
        return "thumb"

    def _get_preview_panel_object_id(self) -> str:
        return "#preview_panel"

    def _discover_assets(self):
        return list(self._assets)

    def _get_current_selection(self):
        return self._current_selection

    def _set_selection(self, asset_id: str) -> None:
        self.set_calls.append(asset_id)

    def _update_preview(self, asset_id: str) -> None:
        self.preview_calls.append(asset_id)


def _patched_widgets():
    """Patch all pygame_gui widget classes used by BaseGallery construction.

    Returns a context manager that, while active, replaces
    ``pygame_gui.elements.{UILabel,UIPanel,UIScrollingContainer,
    UIButton,UIImage}`` with MagicMocks. The MagicMock classes return
    MagicMock instances on call; for UIButton instances we ensure
    ``select`` / ``unselect`` / ``asset_id`` attributes exist (set by
    BaseGallery on the instance, not by pygame_gui).
    """
    return patch.multiple(
        bg_module.pygame_gui.elements,
        UILabel=MagicMock(),
        UIPanel=MagicMock(),
        UIScrollingContainer=MagicMock(),
        UIButton=MagicMock(),
        UIImage=MagicMock(),
    )


@pytest.fixture
def manager():
    return MagicMock()


@pytest.fixture
def panel():
    return MagicMock()


@pytest.fixture
def race_config():
    return MagicMock()


def _surface() -> pygame.Surface:
    return pygame.Surface((20, 20), pygame.SRCALPHA)


class TestBaseGalleryInit:
    def test_init_constructs_expected_widget_tree_for_populated_asset_list(
        self, manager, panel, race_config,
    ):
        assets = [("alpha", _surface()), ("beta", _surface())]

        with _patched_widgets():
            gallery = _FakeGallery(
                panel, manager, race_config,
                x=0, y=0, width=300, height=400,
                assets=assets,
            )

        # 9 abstracts: 2 entries -> 2 buttons + 2 image overlays cached.
        # asset_buttons should hold one (button, asset_id) pair per asset.
        assert len(gallery.asset_buttons) == 2
        assert [aid for _btn, aid in gallery.asset_buttons] == ["alpha", "beta"]
        # The scroll container reference is set during _create_content.
        assert gallery.scroll_container is not None
        # Preview panel is also constructed.
        assert gallery.preview_panel is not None

    def test_existing_selection_in_config_fires_on_asset_selected_during_init(
        self, manager, panel, race_config,
    ):
        assets = [("alpha", _surface()), ("beta", _surface())]

        with _patched_widgets():
            gallery = _FakeGallery(
                panel, manager, race_config,
                x=0, y=0, width=300, height=400,
                assets=assets,
                current_selection="beta",
            )

        # _set_selection + _update_preview should have been invoked once
        # during __init__ -> _create_content -> on_asset_selected("beta").
        assert gallery.set_calls == ["beta"]
        assert gallery.preview_calls == ["beta"]


class TestHandleButtonClick:
    def test_handle_button_click_returns_false_for_untracked_button(
        self, manager, panel, race_config,
    ):
        assets = [("alpha", _surface())]

        with _patched_widgets():
            gallery = _FakeGallery(
                panel, manager, race_config,
                x=0, y=0, width=300, height=400,
                assets=assets,
            )

        unrelated_button = MagicMock()
        result = gallery.handle_button_click(unrelated_button)

        assert result is False
