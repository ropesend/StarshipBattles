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


# ----------------------------------------------------------------------------
# on_asset_selected: full routing (set, preview, highlight, callback)
# ----------------------------------------------------------------------------


class TestOnAssetSelected:
    def test_on_asset_selected_calls_set_and_preview_and_fires_callback(
        self, manager, panel, race_config,
    ):
        assets = [("alpha", _surface()), ("beta", _surface())]
        callback = MagicMock()

        with _patched_widgets():
            gallery = _FakeGallery(
                panel, manager, race_config,
                x=0, y=0, width=300, height=400,
                assets=assets,
                on_select_callback=callback,
            )

        # Reset capture lists so we only see the second selection.
        gallery.set_calls.clear()
        gallery.preview_calls.clear()
        callback.reset_mock()

        gallery.on_asset_selected("alpha")

        assert gallery.set_calls == ["alpha"]
        assert gallery.preview_calls == ["alpha"]
        callback.assert_called_once_with("alpha")

    def test_on_asset_selected_toggles_highlight_select_on_match_unselect_on_others(
        self, manager, panel, race_config,
    ):
        assets = [("alpha", _surface()), ("beta", _surface())]

        with _patched_widgets():
            gallery = _FakeGallery(
                panel, manager, race_config,
                x=0, y=0, width=300, height=400,
                assets=assets,
            )

        # Replace stored buttons with distinct sentinels so we can
        # observe per-button select/unselect routing without relying
        # on the shared MagicMock UIButton return value.
        replaced = []
        for _btn, aid in gallery.asset_buttons:
            replaced.append((MagicMock(), aid))
        gallery.asset_buttons = replaced

        gallery.on_asset_selected("beta")

        by_id = {aid: btn for btn, aid in gallery.asset_buttons}
        by_id["beta"].select.assert_called_once()
        by_id["beta"].unselect.assert_not_called()
        by_id["alpha"].unselect.assert_called_once()
        by_id["alpha"].select.assert_not_called()

    def test_on_asset_selected_does_not_invoke_callback_when_none_provided(
        self, manager, panel, race_config,
    ):
        # Smoke test: with no on_select_callback, call still routes
        # through set/preview/highlight without raising.
        assets = [("alpha", _surface())]

        with _patched_widgets():
            gallery = _FakeGallery(
                panel, manager, race_config,
                x=0, y=0, width=300, height=400,
                assets=assets,
                # on_select_callback omitted -> defaults to None
            )

        # No callback attribute or it is None.
        assert gallery.on_select_callback is None

        gallery.set_calls.clear()
        gallery.preview_calls.clear()

        gallery.on_asset_selected("alpha")

        assert gallery.set_calls == ["alpha"]
        assert gallery.preview_calls == ["alpha"]


# ----------------------------------------------------------------------------
# _populate_gallery: edge cases
# ----------------------------------------------------------------------------


class TestPopulateGallery:
    def test_populate_gallery_with_zero_assets_creates_no_buttons(
        self, manager, panel, race_config,
    ):
        with _patched_widgets():
            gallery = _FakeGallery(
                panel, manager, race_config,
                x=0, y=0, width=300, height=400,
                assets=[],
            )

        assert gallery.asset_buttons == []
        # Scroll container is still constructed even with zero assets.
        assert gallery.scroll_container is not None
        # set_scrollable_area_dimensions is called once during populate.
        gallery.scroll_container.set_scrollable_area_dimensions.assert_called_once()

    def test_populate_gallery_clamps_columns_to_one_when_width_too_small(
        self, manager, panel, race_config,
    ):
        # thumb_size is 50 (subclass), spacing is 10. With width=20:
        # cols = max(1, (20 - 20) // 60) = max(1, 0) = 1
        # All 3 assets should stack in a single column => row 0,1,2.
        assets = [("a", _surface()), ("b", _surface()), ("c", _surface())]

        with _patched_widgets():
            gallery = _FakeGallery(
                panel, manager, race_config,
                x=0, y=0, width=20, height=400,
                assets=assets,
            )

        # All three buttons should be created despite the impossibly small width.
        assert len(gallery.asset_buttons) == 3
        assert [aid for _btn, aid in gallery.asset_buttons] == ["a", "b", "c"]


# ----------------------------------------------------------------------------
# set_from_config
# ----------------------------------------------------------------------------


class TestSetFromConfig:
    def test_set_from_config_routes_through_on_asset_selected_when_selection_exists(
        self, manager, panel, race_config,
    ):
        assets = [("alpha", _surface()), ("beta", _surface())]

        with _patched_widgets():
            gallery = _FakeGallery(
                panel, manager, race_config,
                x=0, y=0, width=300, height=400,
                assets=assets,
            )

        # Now set the selection that _get_current_selection returns and call
        # set_from_config — it should route through on_asset_selected.
        gallery._current_selection = "alpha"
        gallery.set_calls.clear()
        gallery.preview_calls.clear()

        gallery.set_from_config()

        assert gallery.set_calls == ["alpha"]
        assert gallery.preview_calls == ["alpha"]

    def test_set_from_config_is_noop_when_no_current_selection(
        self, manager, panel, race_config,
    ):
        with _patched_widgets():
            gallery = _FakeGallery(
                panel, manager, race_config,
                x=0, y=0, width=300, height=400,
                assets=[("alpha", _surface())],
                current_selection=None,
            )

        gallery.set_calls.clear()
        gallery.preview_calls.clear()

        gallery.set_from_config()

        assert gallery.set_calls == []
        assert gallery.preview_calls == []


# ----------------------------------------------------------------------------
# _sanitize_object_id
# ----------------------------------------------------------------------------


class TestSanitizeObjectId:
    def test_sanitize_object_id_replaces_dots_and_spaces_with_underscores(
        self, manager, panel, race_config,
    ):
        with _patched_widgets():
            gallery = _FakeGallery(
                panel, manager, race_config,
                x=0, y=0, width=300, height=400,
                assets=[],
            )

        # Pin observed: only '.' and ' ' replaced; case + other punctuation preserved.
        assert gallery._sanitize_object_id("foo.bar") == "foo_bar"
        assert gallery._sanitize_object_id("foo bar") == "foo_bar"
        assert gallery._sanitize_object_id("foo bar.baz.png") == "foo_bar_baz_png"
        assert gallery._sanitize_object_id("AlreadyClean") == "AlreadyClean"
        # Other special chars are left alone.
        assert gallery._sanitize_object_id("foo-bar") == "foo-bar"
