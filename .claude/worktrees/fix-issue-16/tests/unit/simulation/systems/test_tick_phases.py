"""Tests for ITickPhase protocol and TickPhaseRegistry."""
from unittest.mock import MagicMock, call

import pytest

from game.simulation.systems.tick_phase import ITickPhase, TickPhaseRegistry


class MockPhase:
    """Simple mock implementing ITickPhase protocol."""

    def __init__(self, name: str, priority: int):
        self._name = name
        self._priority = priority
        self.executed = False
        self.engine_received = None

    @property
    def name(self) -> str:
        return self._name

    @property
    def priority(self) -> int:
        return self._priority

    def execute(self, engine) -> None:
        self.executed = True
        self.engine_received = engine


class TestTickPhaseRegistry:
    """Tests for TickPhaseRegistry."""

    def test_starts_empty(self):
        registry = TickPhaseRegistry()
        assert len(registry.phases) == 0

    def test_register_adds_phase(self):
        registry = TickPhaseRegistry()
        phase = MockPhase("test", 100)
        registry.register(phase)
        assert len(registry.phases) == 1

    def test_phases_sorted_by_priority_ascending(self):
        registry = TickPhaseRegistry()
        registry.register(MockPhase("c", 300))
        registry.register(MockPhase("a", 100))
        registry.register(MockPhase("b", 200))
        names = [p.name for p in registry.phases]
        assert names == ["a", "b", "c"]

    def test_execute_all_calls_in_priority_order(self):
        registry = TickPhaseRegistry()
        order = []
        for name, pri in [("third", 300), ("first", 100), ("second", 200)]:
            phase = MockPhase(name, pri)
            phase.execute = lambda engine, n=name: order.append(n)
            registry.register(phase)

        registry.execute_all(MagicMock())
        assert order == ["first", "second", "third"]

    def test_same_priority_maintains_insertion_order(self):
        registry = TickPhaseRegistry()
        registry.register(MockPhase("alpha", 100))
        registry.register(MockPhase("beta", 100))
        registry.register(MockPhase("gamma", 100))
        names = [p.name for p in registry.phases]
        assert names == ["alpha", "beta", "gamma"]

    def test_execute_all_passes_engine(self):
        registry = TickPhaseRegistry()
        phase = MockPhase("test", 100)
        registry.register(phase)
        mock_engine = MagicMock()
        registry.execute_all(mock_engine)
        assert phase.engine_received is mock_engine

    def test_custom_phase_alongside_others(self):
        registry = TickPhaseRegistry()
        registry.register(MockPhase("builtin_1", 100))
        registry.register(MockPhase("builtin_2", 200))
        registry.register(MockPhase("custom", 150))
        names = [p.name for p in registry.phases]
        assert names == ["builtin_1", "custom", "builtin_2"]


class TestITickPhaseProtocol:
    """Test protocol compliance."""

    def test_mock_phase_satisfies_protocol(self):
        phase = MockPhase("test", 100)
        assert isinstance(phase, ITickPhase)

    def test_object_without_methods_fails_protocol(self):
        class NotAPhase:
            pass
        assert not isinstance(NotAPhase(), ITickPhase)
