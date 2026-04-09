"""Generic screen state machine with transition table, guards, and state stack.

Provides a declarative way to manage screen transitions with validation.
States are any hashable type (typically IntEnum). Transitions must be
explicitly declared in a transition table. Guards provide conditional
transition logic. The state stack enables push/pop for return-to-previous.

PROJ-259: Created to formalize the 23 ad-hoc _switch_scene() calls in app.py.

Usage:
    from game.core.constants import GameState

    transitions = frozenset({
        (GameState.MENU, GameState.BUILDER),
        (GameState.BUILDER, GameState.MENU),
        ...
    })

    sm = ScreenStateMachine(
        initial_state=GameState.MENU,
        transitions=transitions,
        guards={(GameState.MENU, GameState.BATTLE): lambda: has_teams()},
        on_enter={GameState.BATTLE: lambda: start_music()},
        on_exit={GameState.BATTLE: lambda: stop_music()},
    )

    sm.transition(GameState.BUILDER)        # Direct transition
    sm.push_and_transition(GameState.BUILDER)  # Push current, transition
    sm.pop_and_return()                     # Return to pushed state
"""
import logging
from typing import Any, Callable, Dict, FrozenSet, List, Optional, Tuple

from game.core.exceptions import StateException

logger = logging.getLogger(__name__)

__all__ = ['ScreenStateMachine']


class ScreenStateMachine:
    """State machine with transition table, guards, callbacks, and state stack.

    Args:
        initial_state: The starting state.
        transitions: Set of (from_state, to_state) tuples defining valid transitions.
        guards: Optional dict mapping (from, to) to a callable returning bool.
            If the guard returns False, the transition is blocked.
        on_enter: Optional dict mapping state to a callback fired on entry.
        on_exit: Optional dict mapping state to a callback fired on exit.
    """

    def __init__(
        self,
        initial_state: Any,
        transitions: FrozenSet[Tuple[Any, Any]],
        guards: Optional[Dict[Tuple[Any, Any], Callable[[], bool]]] = None,
        on_enter: Optional[Dict[Any, Callable]] = None,
        on_exit: Optional[Dict[Any, Callable]] = None,
    ):
        self._state = initial_state
        self._transitions = transitions
        self._guards = guards or {}
        self._on_enter = on_enter or {}
        self._on_exit = on_exit or {}
        self._stack: List[Any] = []

    @property
    def state(self) -> Any:
        """The current state."""
        return self._state

    def can_transition(self, to_state: Any) -> bool:
        """Check if a transition from the current state to to_state is valid.

        Returns True if the transition is in the table AND the guard (if any) passes.
        Pure check — no side effects.
        """
        key = (self._state, to_state)
        if key not in self._transitions:
            return False
        guard = self._guards.get(key)
        if guard is not None and not guard():
            return False
        return True

    def transition(self, to_state: Any) -> None:
        """Transition to a new state.

        Validates the transition, runs guards, fires on_exit then on_enter callbacks.

        Raises:
            StateException: If the transition is not allowed or a guard blocks it.
        """
        key = (self._state, to_state)
        if key not in self._transitions:
            raise StateException(
                f"Transition {self._state!r} -> {to_state!r} is not allowed"
            )
        guard = self._guards.get(key)
        if guard is not None and not guard():
            raise StateException(
                f"Transition {self._state!r} -> {to_state!r} blocked by guard"
            )

        old_state = self._state

        # Fire on_exit for old state
        exit_cb = self._on_exit.get(old_state)
        if exit_cb is not None:
            exit_cb()

        self._state = to_state

        # Fire on_enter for new state
        enter_cb = self._on_enter.get(to_state)
        if enter_cb is not None:
            enter_cb()

        logger.debug(f"State transition: {old_state!r} -> {to_state!r}")

    def push_and_transition(self, to_state: Any) -> None:
        """Push the current state onto the stack, then transition to to_state.

        Used for "return to previous" patterns (e.g., STRATEGY -> BUILDER -> STRATEGY).

        Raises:
            StateException: If the transition is not allowed.
        """
        self._stack.append(self._state)
        self.transition(to_state)

    def pop_and_return(self) -> Any:
        """Pop the previous state from the stack and transition back to it.

        Returns:
            The state that was returned to.

        Raises:
            StateException: If the stack is empty or the return transition is not allowed.
        """
        if not self._stack:
            raise StateException("Cannot pop: state stack is empty")
        return_state = self._stack.pop()
        self.transition(return_state)
        return return_state
