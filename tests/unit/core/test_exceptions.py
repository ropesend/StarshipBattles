"""Tests for custom exception hierarchy in game.core.exceptions.

PROJ-45 Phase 1: Foundation - Exception Hierarchy Tests

These tests verify:
- Base GameException with code and context attributes
- Inheritance chain for all exception types
- Exception chaining with `raise from`
"""
import pytest

from game.core.exceptions import (
    GameException,
    StateException,
    FrozenStateException,
    ValidationException,
    ResourceException,
    MissingResourceException,
    PersistenceException,
    SimulationException,
    ComponentException,
    FormulaException,
    StrategyException,
    EnginePhaseError,
    LLMException,
    LLMConfigError,
    LLMNetworkError,
    LLMResponseError,
    LLMRateLimited,
    LLMTimeoutError,
    LLMCancelled,
)


class TestGameExceptionBase:
    """Tests for base GameException class."""

    def test_basic_instantiation(self):
        """GameException can be created with just a message."""
        exc = GameException("Test error")
        assert str(exc) == "Test error"
        assert exc.code is None
        assert exc.context == {}

    def test_with_code(self):
        """GameException can store an error code."""
        exc = GameException("Test error", code="E001")
        assert exc.code == "E001"

    def test_with_context(self):
        """GameException can store context dictionary."""
        context = {"file": "test.json", "line": 42}
        exc = GameException("Test error", context=context)
        assert exc.context == context
        assert exc.context["file"] == "test.json"
        assert exc.context["line"] == 42

    def test_with_code_and_context(self):
        """GameException can have both code and context."""
        exc = GameException("Test error", code="E001", context={"key": "value"})
        assert exc.code == "E001"
        assert exc.context["key"] == "value"

    def test_context_defaults_to_empty_dict(self):
        """Context defaults to empty dict, not None."""
        exc = GameException("Test error")
        assert exc.context == {}
        assert isinstance(exc.context, dict)

    def test_is_exception_subclass(self):
        """GameException inherits from Exception."""
        assert issubclass(GameException, Exception)

    def test_can_be_raised_and_caught(self):
        """GameException can be raised and caught."""
        with pytest.raises(GameException) as exc_info:
            raise GameException("Raised error", code="E001")
        assert str(exc_info.value) == "Raised error"
        assert exc_info.value.code == "E001"


class TestStateExceptions:
    """Tests for state-related exceptions."""

    def test_state_exception_inherits_from_game_exception(self):
        """StateException is a GameException."""
        assert issubclass(StateException, GameException)

    def test_state_exception_instantiation(self):
        """StateException can be created with code and context."""
        exc = StateException("Invalid state", code="S001", context={"state": "frozen"})
        assert str(exc) == "Invalid state"
        assert exc.code == "S001"
        assert exc.context["state"] == "frozen"

    def test_frozen_state_exception_inherits_from_state_exception(self):
        """FrozenStateException is a StateException."""
        assert issubclass(FrozenStateException, StateException)
        assert issubclass(FrozenStateException, GameException)

    def test_frozen_state_exception_instantiation(self):
        """FrozenStateException can be created normally."""
        exc = FrozenStateException("Cannot modify frozen state", code="S001")
        assert str(exc) == "Cannot modify frozen state"
        assert exc.code == "S001"

    def test_catching_state_exception_catches_frozen(self):
        """Catching StateException catches FrozenStateException."""
        with pytest.raises(StateException):
            raise FrozenStateException("Frozen!")


class TestValidationException:
    """Tests for ValidationException."""

    def test_inherits_from_game_exception(self):
        """ValidationException is a GameException."""
        assert issubclass(ValidationException, GameException)

    def test_instantiation(self):
        """ValidationException can be created with context."""
        exc = ValidationException(
            "Invalid component",
            code="V002",
            context={"component_id": "laser_1", "field": "damage"}
        )
        assert str(exc) == "Invalid component"
        assert exc.code == "V002"
        assert exc.context["component_id"] == "laser_1"


class TestResourceExceptions:
    """Tests for resource-related exceptions."""

    def test_resource_exception_inherits_from_game_exception(self):
        """ResourceException is a GameException."""
        assert issubclass(ResourceException, GameException)

    def test_missing_resource_inherits_from_resource_exception(self):
        """MissingResourceException is a ResourceException."""
        assert issubclass(MissingResourceException, ResourceException)
        assert issubclass(MissingResourceException, GameException)

    def test_missing_resource_instantiation(self):
        """MissingResourceException can store resource details."""
        exc = MissingResourceException(
            "Asset not found",
            code="R001",
            context={"path": "images/ship.png", "type": "image"}
        )
        assert exc.code == "R001"
        assert exc.context["path"] == "images/ship.png"

    def test_catching_resource_catches_missing(self):
        """Catching ResourceException catches MissingResourceException."""
        with pytest.raises(ResourceException):
            raise MissingResourceException("Not found")


class TestPersistenceException:
    """Tests for PersistenceException."""

    def test_inherits_from_game_exception(self):
        """PersistenceException is a GameException."""
        assert issubclass(PersistenceException, GameException)

    def test_instantiation(self):
        """PersistenceException can store save/load details."""
        exc = PersistenceException(
            "Failed to save game",
            code="P001",
            context={"filename": "save1.json", "reason": "disk full"}
        )
        assert str(exc) == "Failed to save game"
        assert exc.code == "P001"
        assert exc.context["filename"] == "save1.json"


class TestSimulationExceptions:
    """Tests for simulation-related exceptions."""

    def test_simulation_exception_inherits_from_game_exception(self):
        """SimulationException is a GameException."""
        assert issubclass(SimulationException, GameException)

    def test_component_exception_inherits_from_simulation(self):
        """ComponentException is a SimulationException."""
        assert issubclass(ComponentException, SimulationException)
        assert issubclass(ComponentException, GameException)

    def test_formula_exception_inherits_from_simulation(self):
        """FormulaException is a SimulationException."""
        assert issubclass(FormulaException, SimulationException)
        assert issubclass(FormulaException, GameException)

    def test_component_exception_instantiation(self):
        """ComponentException can store component details."""
        exc = ComponentException(
            "Invalid component configuration",
            code="C001",
            context={"component_type": "weapon", "component_id": "laser_1"}
        )
        assert exc.code == "C001"
        assert exc.context["component_type"] == "weapon"

    def test_formula_exception_instantiation(self):
        """FormulaException can store formula details."""
        exc = FormulaException(
            "Syntax error in formula",
            code="F001",
            context={"formula": "base_damage * ", "position": 12}
        )
        assert exc.code == "F001"
        assert exc.context["formula"] == "base_damage * "

    def test_catching_simulation_catches_children(self):
        """Catching SimulationException catches Component and Formula exceptions."""
        with pytest.raises(SimulationException):
            raise ComponentException("Component error")

        with pytest.raises(SimulationException):
            raise FormulaException("Formula error")


class TestStrategyExceptions:
    """Tests for strategy-layer exceptions (PROJ-251)."""

    def test_strategy_exception_inherits_from_game_exception(self):
        """StrategyException is a GameException."""
        assert issubclass(StrategyException, GameException)

    def test_strategy_exception_instantiation(self):
        """StrategyException can be created with code and context."""
        exc = StrategyException(
            "Turn processing failed",
            code="T001",
            context={"turn": 5}
        )
        assert str(exc) == "Turn processing failed"
        assert exc.code == "T001"
        assert exc.context["turn"] == 5

    def test_strategy_exception_not_simulation_exception(self):
        """StrategyException is NOT a SimulationException (separate domains)."""
        assert not issubclass(StrategyException, SimulationException)

    def test_engine_phase_error_inherits_from_strategy_exception(self):
        """EnginePhaseError is a StrategyException."""
        assert issubclass(EnginePhaseError, StrategyException)
        assert issubclass(EnginePhaseError, GameException)

    def test_engine_phase_error_instantiation(self):
        """EnginePhaseError can store phase failure details."""
        exc = EnginePhaseError(
            "Phase 'harvesting' failed",
            code="T001",
            context={
                "phase_name": "harvesting",
                "tick": 37,
                "turn": 5,
                "original_error": "KeyError: 'deposits'",
            }
        )
        assert str(exc) == "Phase 'harvesting' failed"
        assert exc.code == "T001"
        assert exc.context["phase_name"] == "harvesting"
        assert exc.context["tick"] == 37
        assert exc.context["turn"] == 5

    def test_engine_phase_error_not_caught_by_simulation_exception(self):
        """EnginePhaseError is NOT caught by except SimulationException."""
        with pytest.raises(EnginePhaseError):
            raise EnginePhaseError("Phase failed")
        # Verify it does NOT match SimulationException
        caught = False
        try:
            raise EnginePhaseError("Phase failed")
        except SimulationException:
            caught = True
        except EnginePhaseError:
            pass
        assert not caught, "EnginePhaseError should not be caught by SimulationException"

    def test_catching_strategy_exception_catches_engine_phase_error(self):
        """Catching StrategyException catches EnginePhaseError."""
        with pytest.raises(StrategyException):
            raise EnginePhaseError("Phase failed")

    def test_catching_game_exception_catches_engine_phase_error(self):
        """Catching GameException catches EnginePhaseError."""
        with pytest.raises(GameException):
            raise EnginePhaseError("Phase failed")


class TestExceptionChaining:
    """Tests for exception chaining with raise from."""

    def test_chaining_preserves_cause(self):
        """Exception chaining preserves the original cause."""
        original = ValueError("Original error")
        try:
            try:
                raise original
            except ValueError as e:
                raise GameException("Wrapped error", code="E001") from e
        except GameException as exc:
            assert exc.__cause__ is original
            assert str(exc.__cause__) == "Original error"

    def test_nested_chaining(self):
        """Multiple levels of chaining are preserved."""
        try:
            try:
                try:
                    raise KeyError("missing_key")
                except KeyError as e:
                    raise ResourceException("Resource lookup failed") from e
            except ResourceException as e:
                raise PersistenceException("Save failed") from e
        except PersistenceException as exc:
            assert isinstance(exc.__cause__, ResourceException)
            assert isinstance(exc.__cause__.__cause__, KeyError)


class TestExceptionAll:
    """Tests to verify all exceptions are properly exported."""

    def test_all_exceptions_importable(self):
        """All expected exceptions can be imported."""
        # This test passes if the imports at the top of the file succeed
        exceptions = [
            GameException,
            StateException,
            FrozenStateException,
            ValidationException,
            ResourceException,
            MissingResourceException,
            PersistenceException,
            SimulationException,
            ComponentException,
            FormulaException,
            StrategyException,
            EnginePhaseError,
            LLMException,
            LLMConfigError,
            LLMNetworkError,
            LLMResponseError,
            LLMRateLimited,
            LLMTimeoutError,
            LLMCancelled,
        ]
        for exc_class in exceptions:
            assert issubclass(exc_class, Exception)
            assert issubclass(exc_class, GameException)


class TestLLMExceptions:
    """Tests for LLM service exception branch (PROJ-296)."""

    def test_llm_exception_inherits_from_game_exception(self):
        """LLMException is a GameException."""
        assert issubclass(LLMException, GameException)

    def test_llm_subclasses_inherit_from_llm_exception(self):
        """All LLM sub-classes inherit from LLMException."""
        for cls in (LLMConfigError, LLMNetworkError, LLMResponseError,
                    LLMRateLimited, LLMTimeoutError, LLMCancelled):
            assert issubclass(cls, LLMException), f"{cls.__name__} should subclass LLMException"

    def test_llm_exceptions_accept_code_and_context(self):
        """Each LLM exception accepts message + code + context kwargs."""
        from game.core.error_codes import ErrorCode
        exc = LLMConfigError(
            "no key",
            code=ErrorCode.LLM_CONFIG_MISSING.value,
            context={"provider": "deepseek"},
        )
        assert str(exc) == "no key"
        assert exc.code == "L001"
        assert exc.context == {"provider": "deepseek"}

    def test_llm_chaining_preserves_cause(self):
        """LLM exceptions support `raise from` chaining."""
        try:
            try:
                raise ConnectionError("DNS failure")
            except ConnectionError as e:
                raise LLMNetworkError("network down", code="L002") from e
        except LLMNetworkError as exc:
            assert isinstance(exc.__cause__, ConnectionError)
            assert str(exc.__cause__) == "DNS failure"

    def test_llm_exceptions_are_catchable_as_llm_exception(self):
        """Catching LLMException catches all sub-classes."""
        for cls in (LLMConfigError, LLMNetworkError, LLMResponseError,
                    LLMRateLimited, LLMTimeoutError, LLMCancelled):
            with pytest.raises(LLMException):
                raise cls("test")

    def test_llm_exceptions_are_catchable_as_game_exception(self):
        """LLM exceptions propagate through the GameException umbrella."""
        with pytest.raises(GameException):
            raise LLMRateLimited("429")
