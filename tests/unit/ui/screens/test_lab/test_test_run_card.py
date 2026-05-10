from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from game.ui.screens.test_lab.test_run_card import TestRunCard as RunCard


class _RenderedText:
    def __init__(self, text: str) -> None:
        self.text = text

    def get_width(self) -> int:
        return len(self.text) * 8


class _FakeFont:
    def __init__(self) -> None:
        self.render_calls: list[tuple[str, object]] = []

    def render(self, text: str, antialias: bool, color: object) -> _RenderedText:
        self.render_calls.append((text, color))
        return _RenderedText(text)


class _RunRecord:
    def __init__(
        self,
        *,
        passed: bool = True,
        metrics: dict[str, object] | None = None,
        validation_results: list[dict[str, object]] | None = None,
        validation_summary: dict[str, int] | None = None,
        ticks_run: int = 20,
        p_value: float | None = None,
    ) -> None:
        self.passed = passed
        self.metrics = metrics or {}
        self.validation_results = validation_results or []
        self.validation_summary = validation_summary or {}
        self.ticks_run = ticks_run
        self._p_value = p_value

    def get_formatted_timestamp(self) -> str:
        return "12:34:56"

    def get_p_value(self) -> float | None:
        return self._p_value


@pytest.fixture
def card_factory():
    def make_card(**record_kwargs: object) -> RunCard:
        is_latest = bool(record_kwargs.pop("is_latest", False))

        def fake_get_font(size: int) -> _FakeFont:
            return _FakeFont()

        with patch("game.ui.screens.test_lab.test_run_card.get_font", side_effect=fake_get_font):
            card = RunCard(
                10,
                20,
                240,
                _RunRecord(**record_kwargs),
                run_number=3,
                is_latest=is_latest,
            )
        return card

    return make_card


def _blitted_text(surface: MagicMock) -> list[str]:
    return [call.args[0].text for call in surface.blit.call_args_list]


def test_click_detection_uses_card_rect_bounds(card_factory) -> None:
    card = card_factory()

    assert card.handle_click(10, 20) is True
    assert card.handle_click(249, 99) is True
    assert card.handle_click(250, 100) is False
    assert card.handle_click(9, 20) is False


def test_hover_detection_toggles_state_from_card_rect(card_factory) -> None:
    card = card_factory()

    card.handle_hover(20, 30)
    assert card.is_hovered is True

    card.handle_hover(400, 30)
    assert card.is_hovered is False


def test_draw_delegates_to_header_after_card_frame(card_factory) -> None:
    card = card_factory()
    surface = MagicMock()

    with patch("game.ui.screens.test_lab.test_run_card.pygame.draw.rect") as draw_rect:
        with patch.object(card, "_draw_header") as draw_header:
            card.draw(surface)

    assert draw_rect.call_count == 2
    draw_header.assert_called_once_with(surface)


def test_header_dispatches_propulsion_metrics(card_factory) -> None:
    metrics = {"test_id": "PROP-001", "angle_change": 1.0}
    card = card_factory(metrics=metrics)
    surface = MagicMock()

    with patch.object(card, "_draw_propulsion_metrics") as draw_propulsion:
        with patch.object(card, "_draw_resource_metrics") as draw_resource:
            card._draw_header(surface)

    draw_propulsion.assert_called_once_with(surface, metrics)
    draw_resource.assert_not_called()


def test_header_dispatches_resource_metrics(card_factory) -> None:
    metrics = {"test_id": "RESOURCE-004", "initial_energy": 10, "final_energy": 5}
    card = card_factory(metrics=metrics)
    surface = MagicMock()

    with patch.object(card, "_draw_propulsion_metrics") as draw_propulsion:
        with patch.object(card, "_draw_resource_metrics") as draw_resource:
            card._draw_header(surface)

    draw_propulsion.assert_not_called()
    draw_resource.assert_called_once_with(surface, metrics)


def test_header_default_path_prioritizes_failed_validation(card_factory) -> None:
    card = card_factory(
        validation_results=[
            {"name": "Passing Metric", "expected": 1, "actual": 1, "status": "PASS"},
            {"name": "Failed Metric", "expected": 2, "actual": 3, "status": "FAIL"},
        ],
        validation_summary={"pass": 1, "fail": 1, "warn": 0},
    )
    surface = MagicMock()

    card._draw_header(surface)

    texts = _blitted_text(surface)
    assert "Failed Metric:" in texts
    assert "Passing Metric:" not in texts
    assert "1P 1F 0W" in texts


def test_header_default_path_draws_hit_rate_and_p_value_when_no_validation(card_factory) -> None:
    card = card_factory(
        metrics={"hit_rate": 0.25, "expected_hit_chance": 0.30, "damage_dealt": 5},
        p_value=0.01,
    )
    surface = MagicMock()

    card._draw_header(surface)

    texts = _blitted_text(surface)
    assert "Hit Rate: 25.0% (5/20)" in texts
    assert "Expected: 30.0%" in texts
    assert "p=0.0100" in texts
