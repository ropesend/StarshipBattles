"""
Tests for configuration module.

These configuration classes centralize magic numbers and constants
used throughout the codebase.
"""
import pytest


class TestDisplayConfig:
    """Tests for DisplayConfig."""

    def test_default_resolution_tuple(self):
        """default_resolution() returns tuple (4K)."""
        from game.core.config import DisplayConfig

        resolution = DisplayConfig.default_resolution()
        assert resolution == (3840, 2160)
        assert isinstance(resolution, tuple)

    def test_test_resolution_tuple(self):
        """test_resolution() returns tuple."""
        from game.core.config import DisplayConfig

        resolution = DisplayConfig.test_resolution()
        assert resolution == (1440, 900)


class TestLLMConfig:
    """Tests for LLMConfig (PROJ-296).

    Plain class with class-level constants; mirrors PhysicsConfig style
    (NOT a dataclass).
    """

    def test_llm_config_has_expected_constants(self):
        from game.core.config import LLMConfig

        assert LLMConfig.DEFAULT_TIMEOUT_SECONDS == 60.0
        assert LLMConfig.CONNECT_TIMEOUT_SECONDS == 5.0
        assert LLMConfig.DEFAULT_MAX_TOKENS == 4096
        assert LLMConfig.DEFAULT_TEMPERATURE == 0.7
        assert LLMConfig.DEFAULT_MODEL == "deepseek-chat"
        assert LLMConfig.MAX_RETRIES_5XX == 2
        assert LLMConfig.RETRY_BACKOFF_BASE_SECONDS == 1.0
        assert LLMConfig.MAX_CONCURRENT_CALLS == 3
        assert LLMConfig.USER_AGENT == "starship-battles-llm/1.0"

    def test_llm_config_constants_have_correct_types(self):
        """Type-annotated constants must hold the annotated type at class level."""
        from game.core.config import LLMConfig

        assert isinstance(LLMConfig.DEFAULT_TIMEOUT_SECONDS, float)
        assert isinstance(LLMConfig.CONNECT_TIMEOUT_SECONDS, float)
        assert isinstance(LLMConfig.DEFAULT_MAX_TOKENS, int)
        assert isinstance(LLMConfig.DEFAULT_TEMPERATURE, float)
        assert isinstance(LLMConfig.DEFAULT_MODEL, str)
        assert isinstance(LLMConfig.MAX_RETRIES_5XX, int)
        assert isinstance(LLMConfig.RETRY_BACKOFF_BASE_SECONDS, float)
        assert isinstance(LLMConfig.MAX_CONCURRENT_CALLS, int)
        assert isinstance(LLMConfig.USER_AGENT, str)

    def test_llm_config_is_plain_class_not_dataclass(self):
        """LLMConfig must be a plain class to match the codebase convention.

        See docs/02_PATTERNS.md Pattern 12: config classes are plain
        classes with class-level attributes, NOT @dataclass.
        """
        from dataclasses import is_dataclass
        from game.core.config import LLMConfig

        assert not is_dataclass(LLMConfig)
