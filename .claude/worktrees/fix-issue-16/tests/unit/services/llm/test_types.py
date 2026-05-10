"""Tests for LLM DTOs in game.services.llm.types (PROJ-296)."""
from dataclasses import asdict, FrozenInstanceError

import pytest


# ============================================================================
# Role enum
# ============================================================================

class TestRoleEnum:
    def test_has_expected_members(self):
        from game.services.llm.types import Role

        assert {r.name for r in Role} == {"SYSTEM", "USER", "ASSISTANT", "TOOL"}

    def test_values_are_lowercase_strings(self):
        from game.services.llm.types import Role

        assert Role.SYSTEM.value == "system"
        assert Role.USER.value == "user"
        assert Role.ASSISTANT.value == "assistant"
        assert Role.TOOL.value == "tool"

    def test_is_str_enum(self):
        """Role inherits str so JSON serialization is trivial."""
        from game.services.llm.types import Role

        assert isinstance(Role.USER.value, str)
        assert Role.USER == "user"  # str-enum equality with the literal


# ============================================================================
# FinishReason enum
# ============================================================================

class TestFinishReasonEnum:
    def test_has_expected_members(self):
        from game.services.llm.types import FinishReason

        assert {r.name for r in FinishReason} == {"STOP", "LENGTH", "CANCELLED", "ERROR"}

    def test_values_are_lowercase_strings(self):
        from game.services.llm.types import FinishReason

        assert FinishReason.STOP.value == "stop"
        assert FinishReason.LENGTH.value == "length"
        assert FinishReason.CANCELLED.value == "cancelled"
        assert FinishReason.ERROR.value == "error"


# ============================================================================
# Message dataclass
# ============================================================================

class TestMessage:
    def test_construction(self):
        from game.services.llm.types import Message, Role

        msg = Message(role=Role.USER, content="hello")
        assert msg.role == Role.USER
        assert msg.content == "hello"

    def test_is_frozen(self):
        from game.services.llm.types import Message, Role

        msg = Message(role=Role.USER, content="hi")
        with pytest.raises(FrozenInstanceError):
            msg.content = "changed"  # type: ignore[misc]

    def test_asdict_round_trip(self):
        """Sanity check that the DTO is asdict()-friendly."""
        from game.services.llm.types import Message, Role

        msg = Message(role=Role.SYSTEM, content="be helpful")
        d = asdict(msg)
        assert d == {"role": Role.SYSTEM, "content": "be helpful"}


# ============================================================================
# TokenUsage dataclass
# ============================================================================

class TestTokenUsage:
    def test_construction_required_fields(self):
        from game.services.llm.types import TokenUsage

        usage = TokenUsage(prompt_tokens=10, completion_tokens=20, total_tokens=30)
        assert usage.prompt_tokens == 10
        assert usage.completion_tokens == 20
        assert usage.total_tokens == 30
        assert usage.cached_prompt_tokens == 0  # default

    def test_construction_with_cached(self):
        from game.services.llm.types import TokenUsage

        usage = TokenUsage(
            prompt_tokens=10, completion_tokens=20, total_tokens=30,
            cached_prompt_tokens=5,
        )
        assert usage.cached_prompt_tokens == 5

    def test_is_frozen(self):
        from game.services.llm.types import TokenUsage

        usage = TokenUsage(prompt_tokens=1, completion_tokens=2, total_tokens=3)
        with pytest.raises(FrozenInstanceError):
            usage.prompt_tokens = 999  # type: ignore[misc]


# ============================================================================
# CompletionResult dataclass
# ============================================================================

class TestCompletionResult:
    def _make_result(self, **overrides):
        from game.services.llm.types import (
            CompletionResult,
            FinishReason,
            TokenUsage,
        )
        defaults = dict(
            text="hi",
            usage=TokenUsage(prompt_tokens=1, completion_tokens=1, total_tokens=2),
            model="deepseek-chat",
            finish_reason=FinishReason.STOP,
            latency_seconds=0.5,
            provider="deepseek",
            request_id="req_abc",
        )
        defaults.update(overrides)
        return CompletionResult(**defaults)

    def test_has_all_seven_fields(self):
        from game.services.llm.types import CompletionResult, FinishReason

        result = self._make_result()
        assert result.text == "hi"
        assert result.usage.total_tokens == 2
        assert result.model == "deepseek-chat"
        assert result.finish_reason == FinishReason.STOP
        assert result.latency_seconds == 0.5
        assert result.provider == "deepseek"
        assert result.request_id == "req_abc"

    def test_is_frozen(self):
        result = self._make_result()
        with pytest.raises(FrozenInstanceError):
            result.text = "changed"  # type: ignore[misc]

    def test_request_id_can_be_none(self):
        """Some providers don't return a request id."""
        result = self._make_result(request_id=None)
        assert result.request_id is None
