"""PROJ-426 Phase 3 — tests for `PreTickBattleSetupRegistry`.

The registry owns the ordered list of pre-tick setup callbacks that
`run_battle` invokes via its single `pre_tick_loop_callback` parameter.
It replaces the bespoke `_compose_setup_callbacks` helper that used to
live on the adapter.
"""
from __future__ import annotations

from typing import Any, List

import pytest

from game.strategy.combat.pre_tick_setup_registry import (
    PreTickBattleSetupRegistry,
)


def test_registry_returns_none_when_empty():
    """An empty registry must hand back `None` so the adapter passes
    a falsy value straight through to `run_battle`.
    """
    registry = PreTickBattleSetupRegistry()
    assert registry.composed_callback() is None


def test_registry_composes_callbacks_in_registration_order():
    """Two setups registered in known order fire in that order."""
    calls: List[str] = []
    registry = PreTickBattleSetupRegistry()

    def first(engine: Any, _spec: Any) -> None:
        calls.append("first")

    def second(engine: Any, _spec: Any) -> None:
        calls.append("second")

    registry.register("first", first)
    registry.register("second", second)

    composed = registry.composed_callback()
    assert composed is not None
    composed(object(), None)
    assert calls == ["first", "second"]


def test_mine_and_reboard_setups_register_without_knowing_about_each_other():
    """Both setups can register in either order; both fire."""
    fired: List[str] = []
    registry = PreTickBattleSetupRegistry()

    def mine_setup(engine: Any) -> None:
        fired.append("mine")

    def reboard_setup(engine: Any) -> None:
        fired.append("reboard")

    # Legacy (engine,)-only signature is accepted via the registry's
    # adapter shim — Phase 3 setup builders use this shape.
    registry.register("reboard", reboard_setup)
    registry.register("mine", mine_setup)

    composed = registry.composed_callback()
    composed(object(), None)
    assert fired == ["reboard", "mine"]


def test_duplicate_registration_raises():
    """A second registration under the same name must fail loudly."""
    registry = PreTickBattleSetupRegistry()
    registry.register("solo", lambda engine, spec: None)
    with pytest.raises(ValueError):
        registry.register("solo", lambda engine, spec: None)


def test_names_returns_registration_order():
    registry = PreTickBattleSetupRegistry()
    registry.register("a", lambda e, s: None)
    registry.register("b", lambda e, s: None)
    assert registry.names() == ("a", "b")
