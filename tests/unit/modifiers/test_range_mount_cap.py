"""Tests for the range_mount modifier cap (raised from 3 to 10).

Issue #15: design space for long-range weapons extends beyond the previous
cap of 3 levels. Per-level multipliers are intentionally steep (3.5x mass/
HP/cost per level, 2x range per level) and act as a natural disincentive.
"""
import pytest

from game.simulation.components.component import load_modifiers_data


class TestRangeMountCap:
    def test_range_mount_max_is_ten(self) -> None:
        modifiers = load_modifiers_data('data/modifiers.json')
        range_mount = modifiers['range_mount']
        assert range_mount.max_val == 10

    def test_range_mount_min_is_zero(self) -> None:
        modifiers = load_modifiers_data('data/modifiers.json')
        range_mount = modifiers['range_mount']
        assert range_mount.min_val == 0

    def test_range_mount_evaluates_at_new_cap(self) -> None:
        modifiers = load_modifiers_data('data/modifiers.json')
        range_mount = modifiers['range_mount']

        effects = range_mount.evaluate_effects(10.0)
        by_stat = {e.stat_key: e.value for e in effects}

        expected_curve = 3.5 ** 10  # ~275,854.74 — steep on purpose
        assert by_stat['range_mult'] == pytest.approx(1024.0)  # 2^10
        assert by_stat['mass_mult'] == pytest.approx(expected_curve, rel=1e-3)
        assert by_stat['hp_mult'] == pytest.approx(expected_curve, rel=1e-3)
        assert by_stat['cost_mult'] == pytest.approx(expected_curve, rel=1e-3)
