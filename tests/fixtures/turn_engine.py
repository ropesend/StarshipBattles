"""Test helpers for constructing TurnEngine instances.

PROJ-369 Phase 3: TurnEngine ctor requires ``config`` (a fully populated
``TurnEngineConfig``). The lazy-fallback fields are gone; construction
must go through ``TurnEngineConfig.create_default(...)``. This helper
collapses the two-line invocation to a single call and supports the
dataclasses.replace-based per-test override pattern.

Usage:
    from tests.fixtures.turn_engine import build_test_turn_engine

    engine = build_test_turn_engine(registries)
    engine = build_test_turn_engine(registries, ai_factory=mock_ai_factory)
    engine = build_test_turn_engine(
        registries,
        movement_engine=mock_movement,  # config-field overrides
        conflict_engine=mock_conflict,
    )
"""
from __future__ import annotations

import dataclasses
from typing import Any
from unittest.mock import MagicMock

from game.core.registry import GameRegistries
from game.strategy.engine.turn_engine import TurnEngine
from game.strategy.engine.turn_engine_config import TurnEngineConfig


# Names of fields on TurnEngineConfig — used to split overrides between
# config (consumed by `dataclasses.replace`) and TurnEngine ctor kwargs.
_CONFIG_FIELDS = {f.name for f in dataclasses.fields(TurnEngineConfig)}


_AI_FACTORY_DEFAULT = object()  # sentinel: distinguishes "omitted" from "explicit None"


def build_test_turn_engine(
    registries: GameRegistries,
    *,
    ai_factory: Any = _AI_FACTORY_DEFAULT,
    race_registry: Any = None,
    event_bus: Any = None,
    battle_resolver: Any = None,
    tick_phases: Any = None,
    end_of_turn_phases: Any = None,
    **engine_overrides: Any,
) -> TurnEngine:
    """Construct a TurnEngine with eager-default config and per-test overrides.

    PROJ-369 Phase 3 helper. When ``ai_factory`` is omitted, it defaults
    to ``MagicMock()`` so combat resolves in tests that don't otherwise
    wire AI; pass ``ai_factory=None`` *explicitly* to opt into the
    no-combat path (combat raises clearly from ConflictResolutionEngine).

    ``engine_overrides`` may contain any field name on
    ``TurnEngineConfig`` (e.g. ``movement_engine=mock``); they are
    applied via ``dataclasses.replace`` over the eager default config.

    Args:
        registries: GameRegistries to thread into sub-engine construction.
        ai_factory: Optional AI factory. Default-omitted behavior wires
            a MagicMock so a SimulationBattleResolver is constructed;
            explicit ``ai_factory=None`` opts into no-resolver path.
        race_registry: Optional race registry forwarded to
            create_default and TurnEngine.
        event_bus: Optional event bus forwarded similarly.
        battle_resolver: Optional override forwarded to TurnEngine
            (does not affect the resolver bound at config-construction).
        tick_phases / end_of_turn_phases: Optional descriptor-list overrides.
        **engine_overrides: Sub-engine field overrides applied to config
            via ``dataclasses.replace``.

    Returns:
        Constructed TurnEngine ready for use in tests.
    """
    if ai_factory is _AI_FACTORY_DEFAULT:
        ai_factory_resolved: Any = MagicMock()
    else:
        ai_factory_resolved = ai_factory  # explicit None preserved

    # Defensive: any unknown overrides surface as a clear error.
    unknown = set(engine_overrides) - _CONFIG_FIELDS
    if unknown:
        raise TypeError(
            f"build_test_turn_engine got unknown engine override(s): "
            f"{sorted(unknown)}. Allowed: {sorted(_CONFIG_FIELDS)}."
        )

    cfg = TurnEngineConfig.create_default(
        registries,
        ai_factory=ai_factory_resolved,
        race_registry=race_registry,
        event_bus=event_bus,
    )

    # When the caller passes an explicit ``battle_resolver``, swap it
    # into the conflict_engine that ``create_default`` just built. This
    # preserves the pre-Phase-3 contract where
    # ``TurnEngine(battle_resolver=mock)`` overrode the auto-wired
    # ``SimulationBattleResolver``.
    if battle_resolver is not None:
        cfg.conflict_engine._battle_resolver = battle_resolver

    if engine_overrides:
        cfg = dataclasses.replace(cfg, **engine_overrides)

    return TurnEngine(
        registries=registries,
        config=cfg,
        ai_factory=ai_factory_resolved,
        race_registry=race_registry,
        event_bus=event_bus,
        battle_resolver=battle_resolver,
        tick_phases=tick_phases,
        end_of_turn_phases=end_of_turn_phases,
    )
