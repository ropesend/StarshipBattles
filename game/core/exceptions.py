"""Custom exception hierarchy for Starship Battles.

PROJ-45: Error Handling and Exception Management Refactor

This module provides a semantic exception hierarchy for better error handling
throughout the codebase. All exceptions inherit from GameException and support
error codes and context dictionaries for detailed error information.

Usage
=====

Basic usage::

    from game.core.exceptions import ValidationException
    from game.core.error_codes import ErrorCode

    raise ValidationException(
        "Invalid component configuration",
        code=ErrorCode.VALIDATION_FAILED.value,
        context={"component_id": "laser_1", "field": "damage"}
    )

Exception chaining (preserve original cause)::

    from game.core.error_codes import ErrorCode

    try:
        load_json(path)
    except json.JSONDecodeError as e:
        raise PersistenceException(
            f"Failed to parse save file: {path}",
            code=ErrorCode.CORRUPT_DATA.value,
            context={"path": path}
        ) from e

Catching and handling::

    from game.core.error_codes import ErrorCode

    try:
        component = load_component(data)
    except ComponentException as e:
        if e.code == ErrorCode.COMPONENT_INVALID.value:
            log_warning(f"Invalid component: {e.context}")
            component = default_component

Hierarchy
=========

GameException (base)
    StateException         - Object state errors
        FrozenStateException   - Modifying frozen objects
    ValidationException    - Input validation failures
    ResourceException      - Resource loading errors
        MissingResourceException - Resource not found
    PersistenceException   - Save/load failures
    StrategyException      - Strategy-layer errors
        EnginePhaseError       - Turn engine phase failures
    SimulationException    - Combat engine errors
        ComponentException     - Component operation errors
        FormulaException       - Formula evaluation errors
    LLMException           - LLM service errors (PROJ-296)
        LLMConfigError         - No key / unknown provider
        LLMNetworkError        - Connection / DNS / SSL / exhausted retries
        LLMResponseError       - Malformed or non-2xx response (other than rate limit)
        LLMRateLimited         - Provider returned 429
        LLMTimeoutError        - Request exceeded timeout
        LLMCancelled           - Cancelled via cancel_token

Error Codes
===========
Use error codes from game.core.error_codes.ErrorCode for programmatic handling::

    from game.core.error_codes import ErrorCode

    raise ValidationException(
        "Value out of range",
        code=ErrorCode.OUT_OF_RANGE.value,  # "V004"
        context={"value": 150, "max": 100}
    )

Design Notes
============
- NO imports from game.* to avoid circular dependencies
- All exceptions support code and context attributes
- Context defaults to empty dict (never None)
- Exception chaining preserves original cause with `raise from`
- See docs/05_ERROR_HANDLING.md for complete usage guide
"""
from typing import Any, Optional


class GameException(Exception):
    """Base class for all Starship Battles exceptions.

    Attributes:
        code: Optional error code for programmatic handling (e.g., "V001")
        context: Dictionary of contextual information about the error
    """

    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        context: Optional[dict[str, Any]] = None
    ):
        """Initialize GameException.

        Args:
            message: Human-readable error message
            code: Optional error code (e.g., "V001", "S001")
            context: Optional dictionary with additional context
        """
        super().__init__(message)
        self.code = code
        self.context = context or {}


# =============================================================================
# State Management Exceptions
# =============================================================================

class StateException(GameException):
    """Exception for state-related errors.

    Raised when operations are attempted on objects in an invalid state,
    or when state transitions are not allowed.
    """
    pass


class FrozenStateException(StateException):
    """Exception for attempting to modify frozen/immutable state.

    Raised when code attempts to modify a ship, component, or other object
    that has been frozen (e.g., during combat resolution).
    """
    pass


# =============================================================================
# Validation Exceptions
# =============================================================================

class ValidationException(GameException):
    """Exception for validation failures.

    Raised when input validation fails, such as invalid component
    configurations, out-of-range values, or schema violations.
    """
    pass


# =============================================================================
# Resource Exceptions
# =============================================================================

class ResourceException(GameException):
    """Exception for resource-related errors.

    Base class for errors involving game resources such as images,
    sounds, data files, and other assets.
    """
    pass


class MissingResourceException(ResourceException):
    """Exception for missing resources.

    Raised when a required resource (image, sound, data file) cannot be found.
    """
    pass


# =============================================================================
# Persistence Exceptions
# =============================================================================

class PersistenceException(GameException):
    """Exception for save/load errors.

    Raised when saving or loading game data fails, including file I/O errors,
    serialization errors, and data corruption.
    """
    pass


# =============================================================================
# Strategy Exceptions
# =============================================================================

class StrategyException(GameException):
    """Exception for strategy-layer errors.

    Base class for errors that occur during turn processing,
    fleet management, and empire operations in the strategy layer.
    """
    pass


class SessionInitializationError(StrategyException):
    """Raised when GameSession initialization fails (PROJ-381 Phase 2 B-11).

    Wraps any error escaping ``GameInitializer.initialize`` so the
    session ends up in a deterministic null-object state (galaxy=None,
    empires=[]) rather than partially constructed. Preserves the
    original exception via ``__cause__``.
    """
    pass


class EnginePhaseError(StrategyException):
    """Exception for sub-engine phase failures during turn processing.

    Raised when a sub-engine phase fails during tick processing.
    Caught by TurnEngine.process_turn() to trigger snapshot rollback.

    Context should include:
        phase_name (str): Which phase failed (e.g., "harvesting", "production")
        tick (int): Which tick (1-100) the failure occurred on
        turn (int): Which turn number
        original_error (str): String representation of the original exception
    """
    pass


class TurnFailedError(StrategyException):
    """Facade-level wrapper around an EnginePhaseError (PROJ-381 Phase 3 B-4).

    The strategy facade re-raises ``EnginePhaseError`` as
    ``TurnFailedError`` so the UI never has to import a domain-engine
    exception type. Preserves the wrapped error via ``__cause__`` and
    exposes UI-formatted convenience properties read from
    ``self.context``.

    Properties (PROJ-395 MAJ-001 / MAJ-004):
        phase_name: Failed phase name, or "unknown" if missing.
        tick: 1-based tick within the failed phase, or "?" if missing.
        turn_number: Game turn number when the failure occurred, or
            "?" if missing.
        save_path: Pre-turn snapshot save path used for rollback, or
            ``None`` if missing.
        original_type: Class name of the wrapped exception, or
            "Exception" if missing.
        recoverable: True — the player can retry the turn (the facade
            already restored pre-turn state via snapshot rollback).

    All properties tolerate missing context keys with documented
    sentinels so dialog rendering never raises.
    """

    @property
    def phase_name(self) -> str:
        """Failed phase name, or 'unknown' if missing from context."""
        result: str = self.context.get("phase_name", "unknown")
        return result

    @property
    def tick(self) -> int | str:
        """1-based tick within the failed phase, or '?' if missing."""
        result: int | str = self.context.get("tick", "?")
        return result

    @property
    def turn_number(self) -> int | str:
        """Game turn number when the failure occurred, or '?' if missing."""
        result: int | str = self.context.get("turn_number", "?")
        return result

    @property
    def save_path(self) -> str | None:
        """Pre-turn snapshot save path used for rollback, or None."""
        result: str | None = self.context.get("save_path")
        return result

    @property
    def original_type(self) -> str:
        """Class name of the wrapped exception, or 'Exception' if missing."""
        result: str = self.context.get("original_type", "Exception")
        return result

    @property
    def recoverable(self) -> bool:
        """Whether the user can retry the turn (always True for now)."""
        return True


class BattleResolutionError(StrategyException):
    """Wrapper around a SimulationException raised during battle resolution
    (PROJ-381 Phase 3 B-6).

    Carries fleet IDs, hex coordinate, and empire IDs in ``context`` so a
    crash dump captures the situation that triggered the failure.
    """
    pass


# =============================================================================
# Simulation Exceptions
# =============================================================================

class SimulationException(GameException):
    """Exception for simulation engine errors.

    Base class for errors that occur during combat simulation,
    including component and formula evaluation errors.
    """
    pass


class ComponentException(SimulationException):
    """Exception for component-related errors.

    Raised when component operations fail, such as invalid component
    configurations, missing abilities, or component state errors.
    """
    pass


class FormulaException(SimulationException):
    """Exception for formula evaluation errors.

    Raised when formula parsing or evaluation fails, including
    syntax errors, undefined variables, and evaluation errors.
    """
    pass


# =============================================================================
# LLM Service Exceptions (PROJ-296)
# =============================================================================

class LLMException(GameException):
    """Base class for LLM service errors.

    Raised by LLM providers, factory, and threading helper. Use the
    `L001`-`L006` codes from `game.core.error_codes.ErrorCode` and
    include relevant context (model, endpoint, status_code, error_code,
    request_duration_ms). NEVER include the API key, request body,
    response body, headers, or message contents in `context`.
    """
    pass


class LLMConfigError(LLMException):
    """LLM provider not configured.

    Raised when no API key is available, an unknown provider is
    requested via `LLM_PROVIDER`, or the concurrent-call limit is
    exceeded.
    """
    pass


class LLMNetworkError(LLMException):
    """LLM network failure.

    Raised on connection errors, DNS failures, SSL errors, or after
    exhausting retries on 5xx responses.
    """
    pass


class LLMResponseError(LLMException):
    """LLM response was malformed or non-2xx (other than rate-limit)."""
    pass


class LLMRateLimited(LLMException):
    """LLM provider returned 429 (rate limit exceeded).

    Never auto-retried — consumer surfaces this immediately.
    """
    pass


class LLMTimeoutError(LLMException):
    """LLM request exceeded its configured timeout."""
    pass


class LLMCancelled(LLMException):
    """LLM call was cancelled via cancel_token.

    The underlying HTTP request may still be in flight in the
    background; its response is discarded.
    """
    pass


class LLMUnexpectedError(LLMException):
    """LLM provider raised a non-LLMException exception (PROJ-321..328 audit S1.1).

    Wraps any unexpected, non-LLM exception that escapes from a
    provider's `complete()` call (`RuntimeError`, `KeyError`,
    third-party HTTP-library exceptions not yet mapped to
    `LLMNetworkError`, etc.). The underlying exception is preserved
    via `__cause__`; the original exception type is also stored in
    `context['original_exception_type']` for safe logging.

    `code` is intentionally `None` — the wrapped exception is, by
    definition, outside the categorized LLM-error taxonomy. Callers
    that need to distinguish "something unexpected happened" from a
    specific known LLM failure should use `isinstance(err,
    LLMUnexpectedError)`.

    Introduced because `LLMBackgroundCall._run()` previously only
    caught `LLMException` and `LLMCancelled`; any other exception
    propagated past the inner try/finally with `_status` still
    `RUNNING`, violating the `wait()` API contract that returns
    True only for terminal state (DONE/ERROR/CANCELLED).
    """
    pass


# =============================================================================
# Image Service Exceptions (PROJ-314)
# =============================================================================

class ImageException(GameException):
    """Base class for image-generation service errors.

    Raised by image providers, factory, and threading helper. Use the
    `I001`-`I006` codes from `game.core.error_codes.ErrorCode` and
    include relevant context (model, endpoint, status_code,
    request_duration_ms). NEVER include the API key, request body,
    response body, or headers in `context`.
    """
    pass


class ImageConfigError(ImageException):
    """Image provider not configured.

    Raised when no API key is available, an unknown provider is
    requested via `IMAGE_PROVIDER`, or the concurrent-call limit is
    exceeded.
    """
    pass


class ImageNetworkError(ImageException):
    """Image-service network failure.

    Raised on connection errors, DNS failures, SSL errors, or after
    exhausting retries on 5xx responses.
    """
    pass


class ImageResponseError(ImageException):
    """Image-service response was malformed or non-2xx (other than rate-limit)."""
    pass


class ImageRateLimited(ImageException):
    """Image provider returned 429 (rate limit exceeded).

    Never auto-retried — consumer surfaces this immediately.
    """
    pass


class ImageTimeoutError(ImageException):
    """Image request exceeded its configured timeout."""
    pass


class ImageCancelled(ImageException):
    """Image call was cancelled via cancel_token.

    The underlying HTTP request may still be in flight in the
    background; its response is discarded.
    """
    pass


class ImageUnexpectedError(ImageException):
    """Image provider raised a non-ImageException exception (PROJ-381 Phase 2 B-10).

    Mirror of :class:`LLMUnexpectedError`. Wraps any unexpected,
    non-Image exception that escapes from a provider's
    ``generate_image()`` call (`RuntimeError`, third-party HTTP-library
    exceptions not yet mapped to ``ImageNetworkError``, etc.). The
    underlying exception is preserved via ``__cause__``; the original
    exception type is also stored in
    ``context['original_exception_type']`` for safe logging.

    ``code`` is intentionally ``None`` — the wrapped exception is, by
    definition, outside the categorized image-error taxonomy. Callers
    that need to distinguish "something unexpected happened" from a
    specific known image failure should use ``isinstance(err,
    ImageUnexpectedError)``.

    Introduced because :class:`ImageBackgroundCall._run()` previously
    only caught :class:`ImageException` and :class:`ImageCancelled`; any
    other exception propagated past the inner try/finally with
    ``_status`` still ``RUNNING``, leaking the worker thread and leaving
    callers polling forever.
    """
    pass


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Base
    'GameException',
    # State
    'StateException',
    'FrozenStateException',
    # Validation
    'ValidationException',
    # Resources
    'ResourceException',
    'MissingResourceException',
    # Persistence
    'PersistenceException',
    # Strategy
    'StrategyException',
    'EnginePhaseError',
    'SessionInitializationError',
    'TurnFailedError',
    'BattleResolutionError',
    # Simulation
    'SimulationException',
    'ComponentException',
    'FormulaException',
    # LLM Service (PROJ-296)
    'LLMException',
    'LLMConfigError',
    'LLMNetworkError',
    'LLMResponseError',
    'LLMRateLimited',
    'LLMTimeoutError',
    'LLMCancelled',
    'LLMUnexpectedError',
    # Image Service (PROJ-314)
    'ImageException',
    'ImageConfigError',
    'ImageNetworkError',
    'ImageResponseError',
    'ImageRateLimited',
    'ImageTimeoutError',
    'ImageCancelled',
    'ImageUnexpectedError',
]
