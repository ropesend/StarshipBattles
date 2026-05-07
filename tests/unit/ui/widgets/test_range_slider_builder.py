"""Tests for the shared range-slider row builder."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pygame


def test_build_range_slider_row_constructs_min_max_controls() -> None:
    """The builder wires labels, sliders, text entries, and return shape."""
    from game.ui.widgets.range_slider_builder import build_range_slider_row

    manager = MagicMock()
    container = MagicMock()
    min_entry = MagicMock()
    max_entry = MagicMock()

    with (
        patch("game.ui.widgets.range_slider_builder.UILabel") as mock_label,
        patch("game.ui.widgets.range_slider_builder.UIHorizontalSlider") as mock_slider,
        patch("game.ui.widgets.range_slider_builder.UITextEntryLine") as mock_entry,
    ):
        min_slider = MagicMock()
        max_slider = MagicMock()
        mock_slider.side_effect = [min_slider, max_slider]
        mock_entry.side_effect = [min_entry, max_entry]

        new_y, entry = build_range_slider_row(
            "Gravity",
            "gravity",
            0.5,
            2.5,
            12,
            220,
            manager,
            container,
        )

    assert new_y == 96
    assert entry == {
        "min": min_slider,
        "max": max_slider,
        "min_txt": min_entry,
        "max_txt": max_entry,
        "limits": (0.5, 2.5),
    }

    assert [call.args[1] for call in mock_label.call_args_list] == [
        "Gravity",
        "Min",
        "Max",
    ]
    assert mock_slider.call_args_list[0].kwargs == {
        "relative_rect": pygame.Rect(45, 32, 115, 24),
        "start_value": 0.5,
        "value_range": (0.5, 2.5),
        "manager": manager,
        "container": container,
    }
    assert mock_slider.call_args_list[1].kwargs == {
        "relative_rect": pygame.Rect(45, 61, 115, 24),
        "start_value": 2.5,
        "value_range": (0.5, 2.5),
        "manager": manager,
        "container": container,
    }
    min_entry.set_text.assert_called_once_with("0.5")
    max_entry.set_text.assert_called_once_with("2.5")

