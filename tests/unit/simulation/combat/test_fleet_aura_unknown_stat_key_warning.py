"""Tests for FleetAuraManager's unknown-stat_key warning (PROJ-273 Phase 5).

When a `ModifierEntry` enters the manager with a `stat_key` that isn't in
`KNOWN_EXTERNAL_STAT_KEYS`, the manager emits a WARN log once per
(stat_key, source) pair. This catches silent-drop bugs where a compiler
emits an entry no reader picks up.

Placeholder entries (`stat_key == "placeholder"`) are handled by the
existing `_log_placeholder_once` path and are NOT the target of this
warning.
"""
from __future__ import annotations

import logging
from types import SimpleNamespace

from game.simulation.combat.fleet_aura_manager import FleetAuraManager
from game.simulation.combat.modifier_stack import ModifierEntry, ModifierStack
from game.simulation.components.modifier_effects import ModifierEffect


def _ship(team_id: int):
    return SimpleNamespace(
        team_id=team_id,
        is_alive=True,
        is_derelict=False,
        fleet_attack_bonus=0.0,
        fleet_defense_bonus=0.0,
        external_stats={},
        get_all_components=lambda: [],
    )


def _entry(source: str, stat_key: str, value: float) -> ModifierEntry:
    return ModifierEntry(
        source=source,
        stack_group=None,
        effect=ModifierEffect(
            stat_key=stat_key,
            value=value,
            operation="multiply",
            target_ability=None,
            source_modifier_id="mod",
            source_modifier_name="Mod",
            formula_str="",
            param_value=value,
        ),
    )


def _stack_per_team(team_id: int, entries: list) -> ModifierStack:
    return ModifierStack(per_team={team_id: tuple(entries)}, global_=())


def test_known_stat_key_emits_no_warning(caplog):
    """A known stat_key produces no warning."""
    manager = FleetAuraManager()
    stack = _stack_per_team(0, [_entry("test:known", "damage_mult", 1.5)])
    with caplog.at_level(logging.WARNING, logger="game.simulation.combat.fleet_aura_manager"):
        manager.initialize([_ship(0)], modifier_stack=stack)
    unknown_warnings = [
        r for r in caplog.records
        if "unknown stat_key" in r.getMessage().lower()
    ]
    assert not unknown_warnings


def test_unknown_stat_key_emits_warning(caplog):
    """An unknown stat_key triggers a WARN log."""
    manager = FleetAuraManager()
    stack = _stack_per_team(
        0, [_entry("test:made_up_src", "totally_made_up_stat", 2.0)]
    )
    with caplog.at_level(logging.WARNING, logger="game.simulation.combat.fleet_aura_manager"):
        manager.initialize([_ship(0)], modifier_stack=stack)
    matches = [
        r for r in caplog.records
        if "totally_made_up_stat" in r.getMessage()
    ]
    assert len(matches) == 1
    # The warning must mention both the stat_key and the source for diagnosis.
    assert "test:made_up_src" in matches[0].getMessage()


def test_unknown_stat_key_same_source_warns_once(caplog):
    """Two entries with the same (stat_key, source) pair produce ONE warning.

    Mirrors the existing `_log_placeholder_once` once-per-source pattern.
    """
    manager = FleetAuraManager()
    stack = _stack_per_team(0, [
        _entry("test:same_src", "made_up_stat", 2.0),
        _entry("test:same_src", "made_up_stat", 3.0),
    ])
    with caplog.at_level(logging.WARNING, logger="game.simulation.combat.fleet_aura_manager"):
        manager.initialize([_ship(0)], modifier_stack=stack)
    matches = [
        r for r in caplog.records
        if "made_up_stat" in r.getMessage()
    ]
    assert len(matches) == 1


def test_unknown_stat_key_different_sources_warn_separately(caplog):
    """Same stat_key but different sources produces TWO distinct warnings."""
    manager = FleetAuraManager()
    stack = _stack_per_team(0, [
        _entry("test:src_a", "made_up_stat", 2.0),
        _entry("test:src_b", "made_up_stat", 3.0),
    ])
    with caplog.at_level(logging.WARNING, logger="game.simulation.combat.fleet_aura_manager"):
        manager.initialize([_ship(0)], modifier_stack=stack)
    matches = [
        r for r in caplog.records
        if "made_up_stat" in r.getMessage()
    ]
    assert len(matches) == 2


def test_placeholder_still_uses_existing_placeholder_path(caplog):
    """Placeholder entries use the existing `_log_placeholder_once` path,
    NOT the new unknown-stat_key warning.
    """
    manager = FleetAuraManager()
    stack = _stack_per_team(0, [_entry("test:placeholder_src", "placeholder", 1.0)])
    with caplog.at_level(logging.WARNING, logger="game.simulation.combat.fleet_aura_manager"):
        manager.initialize([_ship(0)], modifier_stack=stack)
    # Placeholder warning is emitted (pre-existing behavior)
    placeholder_warnings = [
        r for r in caplog.records
        if "placeholder" in r.getMessage().lower()
    ]
    assert len(placeholder_warnings) >= 1
    # The "unknown stat_key" warning must NOT fire — the placeholder path
    # handles this case with its own dedicated message.
    unknown_warnings = [
        r for r in caplog.records
        if "unknown stat_key" in r.getMessage().lower()
    ]
    assert not unknown_warnings
