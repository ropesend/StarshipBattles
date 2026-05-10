"""Tests for the simple_size_mount step_buttons configuration in MODIFIER_UI_CONFIG.

Verifies issue #14: size mount step buttons use the ±1 / ±10 / ±100 shape with
snap_floor / snap_ceil modes (matching simple_size), and the smart_floor behavior
on the leftmost arrow is preserved.
"""
import pytest

from game.ui.screens.builder.modifier_config import MODIFIER_UI_CONFIG
from game.ui.screens.builder.modifier_logic import ModifierLogicService


def _button(cfg: dict, label: str) -> dict:
    for btn in cfg['step_buttons']:
        if btn['label'] == label:
            return btn
    raise AssertionError(f"No step button with label {label!r} in {cfg['step_buttons']}")


class TestSimpleSizeMountConfigShape:
    """The config must match simple_size: ±1 / ±10 / ±100 with snap modes."""

    @pytest.fixture
    def cfg(self):
        return MODIFIER_UI_CONFIG['simple_size_mount']

    def test_triple_left_is_100_snap_floor(self, cfg):
        btn = _button(cfg, '<<<')
        assert btn['value'] == 100
        assert btn['mode'] == 'snap_floor'

    def test_double_left_is_10_snap_floor(self, cfg):
        btn = _button(cfg, '<<')
        assert btn['value'] == 10
        assert btn['mode'] == 'snap_floor'

    def test_single_left_is_1_delta_sub(self, cfg):
        btn = _button(cfg, '<')
        assert btn['value'] == 1
        assert btn['mode'] == 'delta_sub'

    def test_single_right_is_1_delta_add(self, cfg):
        btn = _button(cfg, '>')
        assert btn['value'] == 1
        assert btn['mode'] == 'delta_add'

    def test_double_right_is_10_snap_ceil(self, cfg):
        btn = _button(cfg, '>>')
        assert btn['value'] == 10
        assert btn['mode'] == 'snap_ceil'

    def test_triple_right_is_100_snap_ceil(self, cfg):
        btn = _button(cfg, '>>>')
        assert btn['value'] == 100
        assert btn['mode'] == 'snap_ceil'

    def test_smart_floor_retained(self, cfg):
        assert cfg.get('smart_floor') is True

    def test_slider_step_retained(self, cfg):
        assert cfg['slider_step'] == 0.1


class TestSimpleSizeMountTripleLeftBehavior:
    """Acceptance criteria: <<< on size_mount snaps to multiples of 100,
    and collapses to min_val when value <= 100 (smart_floor)."""

    def _triple_left_step(self) -> int | float:
        return _button(MODIFIER_UI_CONFIG['simple_size_mount'], '<<<')['value']

    def test_above_100_snaps_down_to_next_multiple_of_100(self):
        """current_value > 100 -> <<< snaps DOWN to next multiple of 100."""
        step = self._triple_left_step()
        # 250 -> 200 (the previous multiple of 100).
        result = ModifierLogicService.calculate_snap_value(
            current=250, step=step, direction=-1,
            min_val=0.1, max_val=1024.0, smart_floor=True,
        )
        assert result == pytest.approx(200, abs=0.01)

    def test_at_or_below_100_collapses_to_min_val(self):
        """current_value <= 100 -> <<< collapses to min_val (smart_floor)."""
        step = self._triple_left_step()
        # current (50) <= step (100), smart_floor active -> min_val
        result = ModifierLogicService.calculate_snap_value(
            current=50, step=step, direction=-1,
            min_val=0.1, max_val=1024.0, smart_floor=True,
        )
        assert result == pytest.approx(0.1, abs=0.01)
