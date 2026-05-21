"""PROJ-466 Phase 3: minor hardening regression tests.

Covers the observable Phase 3 changes: safe DTO __repr__ overrides, the
RoleRegistryReadOnlyError base-class change, construction-queue swallow
logging, and the minefield_balance json_utils routing.
"""
from __future__ import annotations

import logging

import pytest


# ---------------------------------------------------------------------------
# Task 3.3: safe __repr__ for LLM DTOs
# ---------------------------------------------------------------------------


class TestLLMDtoRepr:
    def test_completion_result_repr_hides_text(self):
        from game.services.llm.types import (
            CompletionResult,
            FinishReason,
            TokenUsage,
        )

        secret = "TOP SECRET LLM RESPONSE that must not leak in logs"
        result = CompletionResult(
            text=secret,
            usage=TokenUsage(prompt_tokens=1, completion_tokens=2, total_tokens=3),
            model="deepseek-chat",
            finish_reason=FinishReason.STOP,
            latency_seconds=1.5,
            provider="deepseek",
        )
        r = repr(result)
        assert secret not in r
        assert "text_len=" in r
        assert "deepseek-chat" in r

    def test_message_repr_hides_content(self):
        from game.services.llm.types import Message, Role

        secret = "private prompt content"
        msg = Message(role=Role.USER, content=secret)
        r = repr(msg)
        assert secret not in r
        assert "content_len=" in r
        assert "user" in r


# ---------------------------------------------------------------------------
# Task 3.4: safe __repr__ for Image DTO
# ---------------------------------------------------------------------------


def test_image_result_repr_hides_bytes_and_prompt():
    from game.ui.services.image.types import ImageResult

    secret_prompt = "a revised prompt that should not leak"
    result = ImageResult(
        image_bytes=b"\x89PNG\r\n\x1a\n" + b"\x00" * 100,
        size=(512, 512),
        model="gpt-image-2",
        latency_ms=42.0,
        provider="openai",
        revised_prompt=secret_prompt,
    )
    r = repr(result)
    assert secret_prompt not in r
    assert "PNG" not in r
    assert "bytes_len=" in r
    assert "gpt-image-2" in r


# ---------------------------------------------------------------------------
# Task 3.8: RoleRegistryReadOnlyError inherits from GameException
# ---------------------------------------------------------------------------


def test_role_registry_readonly_error_is_game_exception():
    from game.core.exceptions import GameException, StateException
    from game.core.roles import RoleRegistryReadOnlyError

    assert issubclass(RoleRegistryReadOnlyError, StateException)
    assert issubclass(RoleRegistryReadOnlyError, GameException)
    # Participates in the code/context contract.
    err = RoleRegistryReadOnlyError("read only", code="S003", context={"k": "v"})
    assert err.code == "S003"
    assert err.context == {"k": "v"}


# ---------------------------------------------------------------------------
# Task 3.10: minefield_balance routes through json_utils
# ---------------------------------------------------------------------------


def test_minefield_balance_falls_back_to_defaults_on_missing(monkeypatch, caplog):
    import game.strategy.engine.minefield_balance as mb

    mb.reset_minefield_balance_cache()
    # PROJ-466 Phase 4 Task 4.4: a missing canonical balance file warns
    # explicitly (not just DEBUG) and falls back to defaults.
    monkeypatch.setattr(mb.os.path, "exists", lambda _p: False)
    with caplog.at_level(
        logging.WARNING, logger="game.strategy.engine.minefield_balance"
    ):
        result = mb.load_minefield_balance(force_reload=True)
    assert isinstance(result, mb.MinefieldBalance)
    assert "not found" in caplog.text
    mb.reset_minefield_balance_cache()


def test_minefield_balance_corrupt_data_falls_back(monkeypatch):
    import game.strategy.engine.minefield_balance as mb

    mb.reset_minefield_balance_cache()
    monkeypatch.setattr(mb.os.path, "exists", lambda _p: True)
    monkeypatch.setattr(mb, "load_json", lambda path, default=None: default)
    result = mb.load_minefield_balance(force_reload=True)
    assert isinstance(result, mb.MinefieldBalance)
    mb.reset_minefield_balance_cache()


# ---------------------------------------------------------------------------
# Task 3.9: construction_queue logs the swallowed validation failure
# ---------------------------------------------------------------------------


def test_check_design_valid_logs_on_swallowed_error(caplog):
    from game.strategy.engine.handlers.construction_queue import (
        AddToConstructionQueueCommandHandler,
    )

    handler = AddToConstructionQueueCommandHandler.__new__(
        AddToConstructionQueueCommandHandler
    )

    def boom(session, entity, design_id):
        raise KeyError("missing component")

    handler._resolve_design_data = boom  # type: ignore[attr-defined]

    logger_name = "game.strategy.engine.handlers.construction_queue"
    with caplog.at_level(logging.WARNING, logger=logger_name):
        result = handler._check_design_valid(object(), object(), "broken_design")

    # Behavior preserved: corrupt/unvalidatable design is allowed by default.
    assert result is True
    # But it is no longer silent.
    assert "broken_design" in caplog.text
    assert "could not be validated" in caplog.text


def test_minefield_balance_no_direct_json_load():
    import inspect

    import game.strategy.engine.minefield_balance as mb

    src = inspect.getsource(mb)
    assert "json.load(" not in src
    assert "json.dump(" not in src
