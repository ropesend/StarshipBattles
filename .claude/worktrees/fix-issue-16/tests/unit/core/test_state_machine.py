"""Tests for ScreenStateMachine — generic state machine with transition table, guards, and stack."""
import pytest
from enum import IntEnum

from game.core.exceptions import StateException
from game.core.state_machine import ScreenStateMachine


class MockState(IntEnum):
    """Test states mimicking GameState."""
    MENU = 0
    BUILDER = 1
    BATTLE = 2
    SETTINGS = 3


# Valid transitions for tests
TRANSITIONS = frozenset({
    (MockState.MENU, MockState.BUILDER),
    (MockState.MENU, MockState.BATTLE),
    (MockState.MENU, MockState.SETTINGS),
    (MockState.BUILDER, MockState.MENU),
    (MockState.BUILDER, MockState.BATTLE),
    (MockState.BATTLE, MockState.MENU),
    (MockState.BATTLE, MockState.BUILDER),
    (MockState.SETTINGS, MockState.MENU),
})


class TestStateMachineInit:
    """Test initial state setup."""

    def test_initial_state_set(self):
        sm = ScreenStateMachine(initial_state=MockState.MENU, transitions=TRANSITIONS)
        assert sm.state == MockState.MENU

    def test_works_with_int_enum(self):
        sm = ScreenStateMachine(initial_state=MockState.MENU, transitions=TRANSITIONS)
        assert isinstance(sm.state, IntEnum)


class TestTransition:
    """Test state transitions."""

    def test_transition_to_allowed_state(self):
        sm = ScreenStateMachine(initial_state=MockState.MENU, transitions=TRANSITIONS)
        sm.transition(MockState.BUILDER)
        assert sm.state == MockState.BUILDER

    def test_transition_to_disallowed_state_raises(self):
        sm = ScreenStateMachine(initial_state=MockState.MENU, transitions=TRANSITIONS)
        with pytest.raises(StateException):
            sm.transition(MockState.MENU)  # MENU -> MENU not in transitions

    def test_can_transition_true(self):
        sm = ScreenStateMachine(initial_state=MockState.MENU, transitions=TRANSITIONS)
        assert sm.can_transition(MockState.BUILDER) is True

    def test_can_transition_false(self):
        sm = ScreenStateMachine(initial_state=MockState.BATTLE, transitions=TRANSITIONS)
        assert sm.can_transition(MockState.SETTINGS) is False

    def test_sequential_transitions(self):
        sm = ScreenStateMachine(initial_state=MockState.MENU, transitions=TRANSITIONS)
        sm.transition(MockState.BUILDER)
        sm.transition(MockState.BATTLE)
        sm.transition(MockState.MENU)
        assert sm.state == MockState.MENU


class TestGuards:
    """Test transition guards."""

    def test_passing_guard_allows_transition(self):
        guards = {(MockState.MENU, MockState.BUILDER): lambda: True}
        sm = ScreenStateMachine(initial_state=MockState.MENU, transitions=TRANSITIONS, guards=guards)
        sm.transition(MockState.BUILDER)
        assert sm.state == MockState.BUILDER

    def test_failing_guard_blocks_transition(self):
        guards = {(MockState.MENU, MockState.BUILDER): lambda: False}
        sm = ScreenStateMachine(initial_state=MockState.MENU, transitions=TRANSITIONS, guards=guards)
        with pytest.raises(StateException):
            sm.transition(MockState.BUILDER)

    def test_no_guard_means_always_allowed(self):
        """Transitions without guards are always allowed if in transition table."""
        sm = ScreenStateMachine(initial_state=MockState.MENU, transitions=TRANSITIONS)
        sm.transition(MockState.BATTLE)  # No guard defined
        assert sm.state == MockState.BATTLE


class TestCallbacks:
    """Test on_enter and on_exit callbacks."""

    def test_on_exit_fires(self):
        called = []
        on_exit = {MockState.MENU: lambda: called.append("exit_menu")}
        sm = ScreenStateMachine(initial_state=MockState.MENU, transitions=TRANSITIONS, on_exit=on_exit)
        sm.transition(MockState.BUILDER)
        assert "exit_menu" in called

    def test_on_enter_fires(self):
        called = []
        on_enter = {MockState.BUILDER: lambda: called.append("enter_builder")}
        sm = ScreenStateMachine(initial_state=MockState.MENU, transitions=TRANSITIONS, on_enter=on_enter)
        sm.transition(MockState.BUILDER)
        assert "enter_builder" in called

    def test_on_exit_before_on_enter(self):
        order = []
        on_exit = {MockState.MENU: lambda: order.append("exit")}
        on_enter = {MockState.BUILDER: lambda: order.append("enter")}
        sm = ScreenStateMachine(
            initial_state=MockState.MENU, transitions=TRANSITIONS,
            on_exit=on_exit, on_enter=on_enter,
        )
        sm.transition(MockState.BUILDER)
        assert order == ["exit", "enter"]


class TestStateStack:
    """Test push/pop state stack for return-to-previous behavior."""

    def test_push_and_transition(self):
        sm = ScreenStateMachine(initial_state=MockState.MENU, transitions=TRANSITIONS)
        sm.push_and_transition(MockState.BUILDER)
        assert sm.state == MockState.BUILDER

    def test_pop_and_return(self):
        sm = ScreenStateMachine(initial_state=MockState.MENU, transitions=TRANSITIONS)
        sm.push_and_transition(MockState.BUILDER)
        sm.pop_and_return()
        assert sm.state == MockState.MENU

    def test_pop_empty_stack_raises(self):
        sm = ScreenStateMachine(initial_state=MockState.MENU, transitions=TRANSITIONS)
        with pytest.raises(StateException):
            sm.pop_and_return()

    def test_multiple_push_pop_lifo(self):
        sm = ScreenStateMachine(initial_state=MockState.MENU, transitions=TRANSITIONS)
        sm.push_and_transition(MockState.BUILDER)
        sm.push_and_transition(MockState.BATTLE)
        assert sm.state == MockState.BATTLE

        sm.pop_and_return()
        assert sm.state == MockState.BUILDER

        sm.pop_and_return()
        assert sm.state == MockState.MENU

    def test_push_validates_transition(self):
        sm = ScreenStateMachine(initial_state=MockState.BATTLE, transitions=TRANSITIONS)
        with pytest.raises(StateException):
            sm.push_and_transition(MockState.SETTINGS)  # BATTLE -> SETTINGS not allowed

    def test_pop_validates_return_transition(self):
        # Push MENU, go to BUILDER. Add a transition BUILDER->BATTLE but NOT BATTLE->BUILDER.
        # Then push BUILDER, go to BATTLE. Pop should fail because BATTLE->BUILDER isn't allowed.
        limited = frozenset({
            (MockState.MENU, MockState.BUILDER),
            (MockState.BUILDER, MockState.BATTLE),
            # No BATTLE -> BUILDER
        })
        sm = ScreenStateMachine(initial_state=MockState.MENU, transitions=limited)
        sm.push_and_transition(MockState.BUILDER)
        sm.push_and_transition(MockState.BATTLE)
        with pytest.raises(StateException):
            sm.pop_and_return()  # BATTLE -> BUILDER not in transitions
