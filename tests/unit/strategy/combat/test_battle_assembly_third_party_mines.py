"""PROJ-431 Phase 5 (Finding 2) — third-party mine owners get tactical team IDs.

Codex-consult-driven fix. The Phase 4 pipeline gives every mine an
``_owner_team_id`` ONLY when its owner appears in ``owner_to_team_id``,
which is currently keyed off combat-fleet owners. A third-party empire
that owns mines at the contested hex but has NO combat fleet present
gets:

- ``_collect_mine_groups_at_hex`` collects its mines (✓)
- ``build_mine_resolver_setup`` skips them: ``owner_id not in owner_map``
- ``BattleEngine._run_mine_resolver_tick`` would skip resolvers with
  ``_owner_team_id = None`` anyway.

Result: the third-party mines are inert. They should still detonate
against the actual combatants.

Fix: ``StrategyBattleAssembler`` allocates synthetic team IDs for any
mine-owners not represented in combat fleets. The synthetic team has no
ships in the ``BattleSpec`` (no enemy-side filter ever runs against it),
so all combatant ships read as enemies of the mine — exactly the
intended semantics.
"""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

from game.core.hex_math import HexCoord
from game.strategy.combat.battle_assembly import build_strategy_battle_assembly
from game.strategy.data.deployed_group import MineGroup


def _make_combat_fleet(fleet_id: int, owner_id: int, location, ships) -> MagicMock:
    fleet = MagicMock(spec_set=[
        "id", "owner_id", "ships", "task_forces", "location",
    ])
    fleet.id = fleet_id
    fleet.owner_id = owner_id
    fleet.ships = list(ships)
    fleet.task_forces = []
    fleet.location = location
    return fleet


def _make_ship(instance_id: str) -> MagicMock:
    ship = MagicMock()
    ship.instance_id = instance_id
    ship.design_id = "qs_corvette"
    ship.name = instance_id
    ship.design_data = {"theme_id": "Federation"}
    ship.components = {}
    return ship


def test_third_party_mine_owner_gets_synthetic_team_id(fresh_registries):
    """A mine-only empire (no combat fleets at the hex) must receive a
    team-id entry so its mines are not inert.

    Empires 10 and 20 are the actual combatants (one fleet each). Empire 99
    has mines at the contested hex but NO fleet. Pre-fix, owner_to_team_id
    is {10: 0, 20: 1} and empire 99 is missing — so the mine_setup callback
    skips its mines. Post-fix, empire 99 receives a synthetic team_id (2)
    so the mine resolver gets wired and the mines tick against combatants.
    """
    hex_c = HexCoord(0, 0)

    fleet_10 = _make_combat_fleet(1, owner_id=10, location=hex_c, ships=[_make_ship("a")])
    fleet_20 = _make_combat_fleet(2, owner_id=20, location=hex_c, ships=[_make_ship("b")])

    mg_third_party = MineGroup(group_id=999, owner_id=99, location=hex_c)
    # Give it at least one mine so it isn't an empty-inventory edge case.
    mg_third_party.mines = [object()]

    empire_10 = SimpleNamespace(id=10, deployed_groups=[])
    empire_20 = SimpleNamespace(id=20, deployed_groups=[])
    empire_99 = SimpleNamespace(id=99, deployed_groups=[mg_third_party])

    assembly = build_strategy_battle_assembly(
        [fleet_10, fleet_20],
        empires={10: empire_10, 20: empire_20, 99: empire_99},
        registries=fresh_registries,
        seed=1,
    )

    # The third-party mine is collected.
    assert mg_third_party in assembly.extensions.mine_groups

    # The fix: owner 99 must have a team-id entry, distinct from the
    # combatant team IDs.
    owner_map = assembly.extensions.owner_to_team_id
    assert 99 in owner_map, (
        "Third-party mine owner 99 has no team-id entry; its mines will "
        "be inert in tactical combat. owner_to_team_id={!r}".format(owner_map)
    )
    assert owner_map[99] not in {owner_map[10], owner_map[20]}, (
        "Third-party mine owner reused a combatant team-id; mine team-id "
        "must be distinct so all combatants register as enemies."
    )


def test_third_party_mine_resolver_setup_wires_resolver_with_team_id(
    fresh_registries, monkeypatch,
):
    """End-to-end through ``pre_tick_setup``: when the mine setup runs
    against a fake BattleEngine, the third-party mine's resolver must be
    appended (i.e., not skipped) and must carry an ``_owner_team_id``.

    Stubs ``TacticalMineResolver.from_mine_group`` so the test does not
    depend on CarriedVehicle inventory shape — the assertion is purely
    "did the mine_setup callback append a resolver and set its team id?".
    """
    hex_c = HexCoord(0, 0)

    fleet_10 = _make_combat_fleet(1, owner_id=10, location=hex_c, ships=[_make_ship("a")])
    fleet_20 = _make_combat_fleet(2, owner_id=20, location=hex_c, ships=[_make_ship("b")])

    mg_third_party = MineGroup(group_id=999, owner_id=99, location=hex_c)
    # mines list must be truthy so battle_assembly collects it. Content
    # is irrelevant because we stub the resolver constructor below.
    mg_third_party.mines = [object()]

    empire_10 = SimpleNamespace(id=10, deployed_groups=[])
    empire_20 = SimpleNamespace(id=20, deployed_groups=[])
    empire_99 = SimpleNamespace(id=99, deployed_groups=[mg_third_party])

    assembly = build_strategy_battle_assembly(
        [fleet_10, fleet_20],
        empires={10: empire_10, 20: empire_20, 99: empire_99},
        registries=fresh_registries,
        seed=1,
    )

    # Stub the resolver constructor so we don't need real CarriedVehicle.
    import game.simulation.systems.tactical_mine_resolver as tmr_mod

    def _fake_from_mine_group(cls, mg, **kwargs):
        stub = SimpleNamespace(mine_group_id=mg.id, owner_id=mg.owner_id)
        return stub

    monkeypatch.setattr(
        tmr_mod.TacticalMineResolver,
        "from_mine_group",
        classmethod(_fake_from_mine_group),
    )

    fake_engine = SimpleNamespace(mine_resolvers=[])
    callback = assembly.pre_tick_setup.composed_callback()
    assert callback is not None
    callback(fake_engine)

    # At least one resolver from the third-party mine must be attached.
    assert fake_engine.mine_resolvers, (
        "Third-party mine resolver was skipped — mine_setup did not wire "
        "the mine owner that lacked a combat fleet."
    )
    # Every attached resolver must have a non-None team id.
    for resolver in fake_engine.mine_resolvers:
        assert getattr(resolver, "_owner_team_id", None) is not None, (
            "TacticalMineResolver attached without _owner_team_id; "
            "BattleEngine._run_mine_resolver_tick will skip it silently."
        )
    # The third-party owner specifically — team_id must be distinct from
    # combatant team_ids 0 and 1.
    third_party_resolvers = [
        r for r in fake_engine.mine_resolvers if r.owner_id == 99
    ]
    assert third_party_resolvers, (
        "No resolver attached for owner 99 (third-party mine owner)."
    )
    for r in third_party_resolvers:
        assert r._owner_team_id not in (0, 1), (
            "Third-party mine reused a combatant team-id; combatants would "
            "register as same-team and the mine would not detonate."
        )
