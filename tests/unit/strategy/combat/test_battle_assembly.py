"""PROJ-426 Phase 1 — tests for the typed battle-assembly seam.

These tests pin the contract that replaces the four
`object.__setattr__(spec, ...)` side-channels on `BattleSpec`:

- `BattleSpecExtensions` exposes the four fields as typed attributes.
- `StrategyBattleAssembly` wraps `spec`, `extensions`, and `pre_tick_setup`.
- `build_strategy_battle_assembly(...)` returns a typed wrapper whose
  `.spec` is identical to the result of `build_strategy_battle_spec(...)`
  for the same inputs, and whose `.extensions.*` mirror the current
  side-channels.

Phase 1 is a compat layer: `build_strategy_battle_assembly` may read the
side-channels off the already-built spec to populate `extensions`. Phase 4
removes the side-channels entirely; this test file then reads from
`extensions` directly without any side-channel coupling.
"""
from __future__ import annotations

from dataclasses import fields, is_dataclass
from typing import Any
from unittest.mock import MagicMock

import pytest

from game.strategy.combat.battle_assembly import (
    BattleSpecExtensions,
    StrategyBattleAssembly,
    build_strategy_battle_assembly,
)


def _make_fleet(
    fleet_id: int,
    owner_id: int,
    *,
    group_kind: str = "fleet",
    ships: tuple[Any, ...] = (),
) -> MagicMock:
    """Build a Fleet-shaped mock the spec compiler accepts."""
    fleet = MagicMock(spec_set=[
        "id", "owner_id", "ships", "task_forces", "group_kind", "location",
    ])
    fleet.id = fleet_id
    fleet.owner_id = owner_id
    fleet.ships = list(ships)
    fleet.task_forces = []
    fleet.group_kind = group_kind
    fleet.location = None
    return fleet


def _make_ship(instance_id: str, design_id: str = "qs_corvette") -> MagicMock:
    ship = MagicMock()
    ship.instance_id = instance_id
    ship.design_id = design_id
    ship.name = instance_id
    ship.design_data = {"theme_id": "Federation"}
    ship.components = {}
    return ship


def test_strategy_battle_assembly_holds_spec_extensions_and_setup_registry():
    """`StrategyBattleAssembly` is a frozen DTO with exactly 3 fields."""
    assert is_dataclass(StrategyBattleAssembly)
    names = {f.name for f in fields(StrategyBattleAssembly)}
    assert names == {"spec", "extensions", "pre_tick_setup"}


def test_battle_spec_extensions_exposes_all_four_current_side_channel_fields():
    """`BattleSpecExtensions` exposes the four current side-channel fields.

    The `engine_ref` field is a mutable list inside an otherwise frozen
    dataclass — the one-slot pattern documented in design.md. The pre-tick
    callback populates it with the live `BattleEngine` so the post-battle
    hook can call `apply_reboard`.
    """
    assert is_dataclass(BattleSpecExtensions)
    names = {f.name for f in fields(BattleSpecExtensions)}
    assert names == {
        "mine_groups",
        "owner_to_team_id",
        "combat_fleets",
        "engine_ref",
    }

    # Mutable one-slot list contract: engine_ref must be a list so the
    # pre-tick callback can append the engine to it.
    ext = BattleSpecExtensions(
        mine_groups=(),
        owner_to_team_id={},
        combat_fleets=(),
        engine_ref=[],
    )
    assert isinstance(ext.engine_ref, list)
    ext.engine_ref.append("engine_sentinel")
    assert ext.engine_ref == ["engine_sentinel"]


def test_build_strategy_battle_assembly_returns_typed_wrapper_around_existing_spec(
    fresh_registries,
):
    """`build_strategy_battle_assembly` returns the typed wrapper.

    `.spec` is the same `BattleSpec` shape `build_strategy_battle_spec`
    produces for the same inputs; `.extensions.*` mirror the four
    current side-channels (combat_fleets, mine_groups, owner_to_team_id,
    engine_ref).
    """
    fleet_a = _make_fleet(1, owner_id=10, ships=(_make_ship("a-1"),))
    fleet_b = _make_fleet(2, owner_id=20, ships=(_make_ship("b-1"),))

    assembly = build_strategy_battle_assembly(
        [fleet_a, fleet_b],
        registries=fresh_registries,
        seed=42,
    )

    assert isinstance(assembly, StrategyBattleAssembly)
    assert isinstance(assembly.extensions, BattleSpecExtensions)

    # Two combat fleets, no mine_groups in this scenario.
    assert assembly.extensions.combat_fleets == (fleet_a, fleet_b)
    assert assembly.extensions.mine_groups == ()

    # Owner→team mapping reflects insertion order of unique owners.
    assert assembly.extensions.owner_to_team_id == {10: 0, 20: 1}

    # engine_ref is the mutable one-slot list; starts empty.
    assert assembly.extensions.engine_ref == []

    # The spec is a BattleSpec with the same teams/seed.
    assert assembly.spec.seed == 42
    assert len(assembly.spec.teams) == 2


def test_build_strategy_battle_assembly_includes_mine_group_extension(
    fresh_registries,
):
    """Mine-groups now arrive via ``empire.deployed_groups``, NOT via the
    fleets list. PROJ-431 Phase 2 collapses the former
    ``mine_group_filter`` partitioning step.
    """
    from types import SimpleNamespace
    from game.core.hex_math import HexCoord
    from game.strategy.data.deployed_group import MineGroup

    hex_c = HexCoord(0, 0)
    fleet = _make_fleet(1, owner_id=10, ships=(_make_ship("a-1"),))
    fleet.location = hex_c
    enemy = _make_fleet(2, owner_id=20, ships=(_make_ship("b-1"),))
    enemy.location = hex_c
    mg = MineGroup(group_id=3, owner_id=10, location=hex_c)

    empire10 = SimpleNamespace(id=10, deployed_groups=[mg])
    empire20 = SimpleNamespace(id=20, deployed_groups=[])

    assembly = build_strategy_battle_assembly(
        [fleet, enemy],
        empires={10: empire10, 20: empire20},
        registries=fresh_registries,
        seed=1,
    )

    assert assembly.extensions.combat_fleets == (fleet, enemy)
    assert assembly.extensions.mine_groups == (mg,)
    assert assembly.extensions.owner_to_team_id == {10: 0, 20: 1}


def test_owner_to_team_mapping_is_single_sourced_between_assembler_and_hook(
    fresh_registries,
):
    """Codex consult follow-up: the owner->team mapping must be derived
    once and shared between `StrategyBattleAssembler` and
    `PostBattleHookBuilder`. Previously each side re-derived the mapping
    from its own iteration over fleets — a drift risk if either side's
    derivation algorithm changes (e.g. sort order, dedup rule).

    The structural assertion: the assembler must inject the *same* mapping
    object (identity, not equality) into both `BattleSpecExtensions` and
    the post-battle hook closure. We capture the hook builder's input via
    a spy so the test fails if the assembler re-derives the mapping
    independently for the hook.
    """
    from game.strategy.combat import battle_assembly as ba_module
    from game.strategy.combat.post_battle_hook_builder import (
        PostBattleHookBuilder,
    )

    captured: dict = {}
    original_build = PostBattleHookBuilder.build

    def _spy_build(self, fleets, empires, **kwargs):
        captured["owner_to_team_id"] = kwargs.get("owner_to_team_id")
        return original_build(self, fleets, empires, **kwargs)

    fleet_a = _make_fleet(1, owner_id=10, ships=(_make_ship("a-1"),))
    fleet_b = _make_fleet(2, owner_id=20, ships=(_make_ship("b-1"),))

    monkeypatched = False
    try:
        PostBattleHookBuilder.build = _spy_build  # type: ignore[method-assign]
        monkeypatched = True
        assembly = ba_module.build_strategy_battle_assembly(
            [fleet_a, fleet_b],
            registries=fresh_registries,
            seed=1,
        )
    finally:
        if monkeypatched:
            PostBattleHookBuilder.build = original_build  # type: ignore[method-assign]

    # The post-battle hook builder must be passed an explicit
    # owner_to_team_id argument — not re-derive it from fleets.
    assert "owner_to_team_id" in captured
    assert captured["owner_to_team_id"] is not None, (
        "PostBattleHookBuilder.build must receive an explicit "
        "owner_to_team_id kwarg from the assembler so the mapping has a "
        "single source of truth."
    )

    # Identity: the mapping injected into the hook must be the exact
    # same Python object the extensions expose. Equality alone would
    # allow two re-derivations to drift apart over time.
    assert (
        captured["owner_to_team_id"]
        is assembly.extensions.owner_to_team_id
    ), (
        "Owner->team mapping in BattleSpecExtensions and the mapping "
        "passed to PostBattleHookBuilder must be the same object."
    )
