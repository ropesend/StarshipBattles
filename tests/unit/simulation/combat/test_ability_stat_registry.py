"""Tests for the shared ability -> stat_key registry (PROJ-273).

This module tests both:
- `ABILITY_STAT_REGISTRY` — the canonical mapping of ability class name to
  (stat_key, operation, value_field)
- `emit_entries_for_ability` — the helper that produces `ModifierEntry`
  objects from ability data, with team-scope routing (own vs enemy teams).

The registry is the single source of truth for both Battle Setup and
Strategy spec compilers. Tests here lock the behavior both compilers will
consume.
"""
from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest


# ---------------------------------------------------------------------------
# Registry tests (Task 1.1)
# ---------------------------------------------------------------------------


def test_registry_module_imports():
    """The registry module exists and exposes the canonical names."""
    from game.simulation.combat import ability_stat_registry

    assert hasattr(ability_stat_registry, "ABILITY_STAT_REGISTRY")
    assert hasattr(ability_stat_registry, "AbilityStatMapping")
    assert hasattr(ability_stat_registry, "emit_entries_for_ability")
    assert hasattr(ability_stat_registry, "OPPONENT_SCOPES")


def test_registry_has_known_keys():
    """Known mappings (PROJ-273 + PROJ-300 D14)."""
    from game.simulation.combat.ability_stat_registry import ABILITY_STAT_REGISTRY

    assert set(ABILITY_STAT_REGISTRY.keys()) == {
        "ShieldProjection",
        "ShieldModifier",
        "DamageModifier",
        "ThrustModifier",  # PROJ-300 D14
    }


def test_thrust_modifier_mapping():
    """ThrustModifier -> thrust_mult / multiply / multiplier (PROJ-300 D14)."""
    from game.simulation.combat.ability_stat_registry import ABILITY_STAT_REGISTRY

    mapping = ABILITY_STAT_REGISTRY["ThrustModifier"]
    assert mapping.ability_class_name == "ThrustModifier"
    assert mapping.stat_key == "thrust_mult"
    assert mapping.operation == "multiply"
    assert mapping.value_field == "multiplier"


def test_shield_projection_mapping():
    """ShieldProjection -> shield_bonus_add / add / value."""
    from game.simulation.combat.ability_stat_registry import ABILITY_STAT_REGISTRY

    mapping = ABILITY_STAT_REGISTRY["ShieldProjection"]
    assert mapping.ability_class_name == "ShieldProjection"
    assert mapping.stat_key == "shield_bonus_add"
    assert mapping.operation == "add"
    assert mapping.value_field == "value"


def test_shield_modifier_mapping():
    """ShieldModifier -> shield_capacity_mult / multiply / multiplier."""
    from game.simulation.combat.ability_stat_registry import ABILITY_STAT_REGISTRY

    mapping = ABILITY_STAT_REGISTRY["ShieldModifier"]
    assert mapping.ability_class_name == "ShieldModifier"
    assert mapping.stat_key == "shield_capacity_mult"
    assert mapping.operation == "multiply"
    assert mapping.value_field == "multiplier"


def test_damage_modifier_mapping():
    """DamageModifier -> damage_mult / multiply / multiplier."""
    from game.simulation.combat.ability_stat_registry import ABILITY_STAT_REGISTRY

    mapping = ABILITY_STAT_REGISTRY["DamageModifier"]
    assert mapping.ability_class_name == "DamageModifier"
    assert mapping.stat_key == "damage_mult"
    assert mapping.operation == "multiply"
    assert mapping.value_field == "multiplier"


def test_ability_stat_mapping_is_frozen():
    """AbilityStatMapping must be a frozen dataclass."""
    from game.simulation.combat.ability_stat_registry import AbilityStatMapping

    mapping = AbilityStatMapping(
        ability_class_name="Foo",
        stat_key="bar_mult",
        operation="multiply",
        value_field="multiplier",
    )
    with pytest.raises(FrozenInstanceError):
        mapping.stat_key = "other"  # type: ignore[misc]


def test_opponent_scopes_constant():
    """OPPONENT_SCOPES is the canonical set of scopes routing to enemies."""
    from game.simulation.combat.ability_stat_registry import OPPONENT_SCOPES

    assert OPPONENT_SCOPES == frozenset({"enemy_sector", "enemy_system"})


def test_known_external_stat_keys_contains_all_registry_values():
    """Every `ABILITY_STAT_REGISTRY` value's `stat_key` must appear in
    `KNOWN_EXTERNAL_STAT_KEYS`. Otherwise the runtime warning in
    `FleetAuraManager` would false-positive on a legitimate entry.
    """
    from game.simulation.combat.ability_stat_registry import (
        ABILITY_STAT_REGISTRY,
        KNOWN_EXTERNAL_STAT_KEYS,
    )

    missing = [
        m.stat_key
        for m in ABILITY_STAT_REGISTRY.values()
        if m.stat_key not in KNOWN_EXTERNAL_STAT_KEYS
    ]
    assert not missing, (
        f"Registry values missing from KNOWN_EXTERNAL_STAT_KEYS: {missing}"
    )


def test_known_external_stat_keys_is_frozen():
    """KNOWN_EXTERNAL_STAT_KEYS must be a frozenset."""
    from game.simulation.combat.ability_stat_registry import KNOWN_EXTERNAL_STAT_KEYS

    assert isinstance(KNOWN_EXTERNAL_STAT_KEYS, frozenset)


# ---------------------------------------------------------------------------
# emit_entries_for_ability tests (Task 1.2)
# ---------------------------------------------------------------------------


def _call_emit(
    ability_name,
    ability_data,
    *,
    scope="self",
    owner_team=0,
    num_teams=2,
    source="test:source",
    source_modifier_id="test_design",
    source_modifier_name="Test Design",
    stack_group=None,
):
    """Helper to reduce boilerplate in tests."""
    from game.simulation.combat.ability_stat_registry import emit_entries_for_ability

    return emit_entries_for_ability(
        ability_name,
        ability_data,
        scope=scope,
        owner_team=owner_team,
        num_teams=num_teams,
        source=source,
        source_modifier_id=source_modifier_id,
        source_modifier_name=source_modifier_name,
        stack_group=stack_group,
    )


def test_unknown_ability_returns_empty_list():
    """Abilities not in the registry are silently ignored (returns [])."""
    result = _call_emit("NotARealAbility", {"multiplier": 1.5}, scope="self")
    assert result == []


def test_self_scope_routes_to_owner():
    """`self` scope emits one entry, routed to the owner_team."""
    result = _call_emit(
        "ShieldModifier", {"multiplier": 1.5}, scope="self", owner_team=0, num_teams=2,
    )
    assert len(result) == 1
    team_id, entry = result[0]
    assert team_id == 0
    assert entry.effect.stat_key == "shield_capacity_mult"
    assert entry.effect.value == 1.5
    assert entry.effect.operation == "multiply"


def test_enemy_sector_scope_routes_to_opponent_2_teams():
    """`enemy_sector` with owner=0, num_teams=2 emits one entry for team 1."""
    result = _call_emit(
        "DamageModifier",
        {"multiplier": 0.5},
        scope="enemy_sector",
        owner_team=0,
        num_teams=2,
    )
    assert len(result) == 1
    team_id, entry = result[0]
    assert team_id == 1
    assert entry.effect.stat_key == "damage_mult"
    assert entry.effect.value == 0.5


def test_enemy_system_scope_routes_to_opponent_2_teams():
    """`enemy_system` with owner=0, num_teams=2 emits one entry for team 1."""
    result = _call_emit(
        "ShieldModifier",
        {"multiplier": 0.8},
        scope="enemy_system",
        owner_team=0,
        num_teams=2,
    )
    assert len(result) == 1
    team_id, _ = result[0]
    assert team_id == 1


def test_shield_projection_reads_value_field():
    """ShieldProjection uses `value` field, not `multiplier`."""
    result = _call_emit(
        "ShieldProjection",
        {"value": 500.0, "scope": "allied_sector"},
        scope="allied_sector",
        owner_team=0,
    )
    assert len(result) == 1
    _, entry = result[0]
    assert entry.effect.stat_key == "shield_bonus_add"
    assert entry.effect.value == 500.0
    assert entry.effect.operation == "add"


def test_shield_modifier_reads_multiplier_field():
    """ShieldModifier uses `multiplier`."""
    result = _call_emit(
        "ShieldModifier",
        {"multiplier": 2.0},
        scope="self",
        owner_team=0,
    )
    assert len(result) == 1
    _, entry = result[0]
    assert entry.effect.value == 2.0


def test_shield_projection_primitive_numeric_input():
    """ShieldProjection accepts a raw numeric ability_data value."""
    result = _call_emit(
        "ShieldProjection",
        250.0,  # primitive, not a dict
        scope="self",
        owner_team=0,
    )
    assert len(result) == 1
    _, entry = result[0]
    assert entry.effect.value == 250.0


def test_zero_value_returns_empty_list():
    """A zero / falsy value produces no entry (nothing to apply)."""
    # Dict-shape zero
    result = _call_emit(
        "ShieldProjection",
        {"value": 0.0},
        scope="allied_sector",
        owner_team=0,
    )
    assert result == []


def test_zero_multiplier_returns_empty_list():
    """Zero multiplier is falsy — no entry."""
    result = _call_emit(
        "ShieldModifier",
        {"multiplier": 0.0},
        scope="self",
        owner_team=0,
    )
    assert result == []


def test_stack_group_threads_through():
    """stack_group parameter is placed on the emitted ModifierEntry."""
    result = _call_emit(
        "ShieldModifier",
        {"multiplier": 1.5},
        scope="self",
        owner_team=0,
        stack_group="team0_shield_mult",
    )
    _, entry = result[0]
    assert entry.stack_group == "team0_shield_mult"


def test_stack_group_defaults_to_none():
    """Without explicit stack_group, the entry has None."""
    result = _call_emit(
        "ShieldModifier",
        {"multiplier": 1.5},
        scope="self",
        owner_team=0,
    )
    _, entry = result[0]
    assert entry.stack_group is None


def test_source_threads_through():
    """source parameter is placed on the emitted ModifierEntry.source."""
    result = _call_emit(
        "ShieldModifier",
        {"multiplier": 1.5},
        scope="self",
        owner_team=0,
        source="sector:complex:foo:ShieldModifier",
    )
    _, entry = result[0]
    assert entry.source == "sector:complex:foo:ShieldModifier"


def test_source_modifier_id_and_name_thread_through():
    """source_modifier_id and source_modifier_name populate the ModifierEffect."""
    result = _call_emit(
        "ShieldModifier",
        {"multiplier": 1.5},
        scope="self",
        owner_team=0,
        source_modifier_id="qs_sector_shield_booster_complex",
        source_modifier_name="Shield Booster Complex",
    )
    _, entry = result[0]
    assert entry.effect.source_modifier_id == "qs_sector_shield_booster_complex"
    assert entry.effect.source_modifier_name == "Shield Booster Complex"


def test_enemy_scope_3_teams_fans_out_to_all_opponents():
    """N-team forward-compat: `enemy_sector` with num_teams=3, owner=0 emits TWO entries (teams 1 and 2).

    Note: This exercises the N-team fan-out behavior that PROJ-275 will rely on.
    Even though current compilers all pass num_teams=2, the helper supports N.
    """
    result = _call_emit(
        "DamageModifier",
        {"multiplier": 0.5},
        scope="enemy_sector",
        owner_team=0,
        num_teams=3,
    )
    assert len(result) == 2
    team_ids = sorted(tid for tid, _ in result)
    assert team_ids == [1, 2]


def test_enemy_scope_3_teams_from_team_1():
    """N-team fan-out with owner=1, num_teams=3 emits to teams 0 and 2."""
    result = _call_emit(
        "DamageModifier",
        {"multiplier": 0.5},
        scope="enemy_sector",
        owner_team=1,
        num_teams=3,
    )
    team_ids = sorted(tid for tid, _ in result)
    assert team_ids == [0, 2]


def test_enemy_scope_2_teams_from_team_1():
    """2-team with owner=1, num_teams=2 emits only to team 0."""
    result = _call_emit(
        "DamageModifier",
        {"multiplier": 0.5},
        scope="enemy_sector",
        owner_team=1,
        num_teams=2,
    )
    assert len(result) == 1
    team_id, _ = result[0]
    assert team_id == 0


def test_allied_scope_routes_to_owner():
    """Non-`enemy_*` scopes like `allied_system` route to owner_team."""
    result = _call_emit(
        "ShieldProjection",
        {"value": 500.0},
        scope="allied_system",
        owner_team=0,
    )
    assert len(result) == 1
    team_id, _ = result[0]
    assert team_id == 0


# ---------------------------------------------------------------------------
# Glob-driven coverage (Phase 4)
# ---------------------------------------------------------------------------


def _iter_design_components(design_data):
    """Yield every `{id: ..., abilities: ...}` component dict across all
    layers of a design JSON. Mirrors the helper in
    `battle_setup/spec_compiler.py::_iter_components`.
    """
    layers = design_data.get("layers") or {}
    for layer_components in layers.values():
        if not layer_components:
            continue
        for comp in layer_components:
            if isinstance(comp, dict):
                yield comp


def _design_has_any_registered_ability(design_data, components_registry):
    """Does the design reference any component whose abilities dict
    contains a key in `ABILITY_STAT_REGISTRY`? Registry-driven — no
    hardcoded component-ID allowlist.
    """
    from game.simulation.combat.ability_stat_registry import ABILITY_STAT_REGISTRY

    for component_data in _iter_design_components(design_data):
        comp_id = component_data.get("id")
        if not comp_id:
            continue
        comp_def = components_registry.get(comp_id)
        if comp_def is None:
            continue
        abilities = (
            comp_def.get("abilities")
            if isinstance(comp_def, dict)
            else getattr(comp_def, "abilities", None)
        ) or {}
        for ability_name in abilities:
            if ability_name in ABILITY_STAT_REGISTRY:
                return True
    return False


@pytest.fixture(scope="module")
def _registries():
    """Load the real GameRegistries once for glob tests.

    Uses the same pattern as `test_unified_entry_guard.py` — pull the
    default registry provider and construct a GameRegistries bundle.
    """
    from game.core.registry import GameRegistries, get_default_registry_provider

    provider = get_default_registry_provider()
    return GameRegistries(
        components=provider.get_components(),
        modifiers=provider.get_modifiers(),
        vehicle_classes=provider.get_vehicle_classes(),
        resources=provider.get_resources(),
        resource_catalog=provider.get_resource_catalog(),
    )


@pytest.fixture(scope="module")
def _complex_designs():
    """Glob every `data/designs/qs_*_complex.json` file, loaded as dicts.

    Returns a list of `(design_id, design_data)` tuples sorted by design_id.
    Any new complex JSON added to disk is automatically picked up.
    """
    import json
    from pathlib import Path

    repo_root = Path(__file__).resolve().parents[4]
    complex_dir = repo_root / "data" / "designs"
    files = sorted(complex_dir.glob("qs_*_complex.json"))
    designs = []
    for path in files:
        with open(path, "r", encoding="utf-8") as f:
            designs.append((path.stem, json.load(f)))
    return designs


def test_glob_finds_at_least_one_complex_design(_complex_designs):
    """If the glob returns nothing, the pattern drifted or files were moved."""
    assert _complex_designs, (
        "No qs_*_complex.json designs found — pattern drift or repo layout change?"
    )


def test_no_placeholder_from_any_complex_via_registry(_complex_designs, _registries):
    """Every qs_*_complex.json whose components carry a registry-mapped
    ability must produce zero placeholder entries.

    Registry-driven (not a hardcoded component-ID allowlist). If a future
    author adds a new complex JSON whose components include a mapped
    ability, this test picks it up automatically.
    """
    from game.simulation.combat.ability_stat_registry import (
        ABILITY_STAT_REGISTRY,
        emit_entries_for_ability,
    )

    components_registry = _registries.get_components()
    failures = []
    for design_id, design in _complex_designs:
        if not _design_has_any_registered_ability(design, components_registry):
            continue
        for component_data in _iter_design_components(design):
            comp_id = component_data.get("id")
            if not comp_id:
                continue
            comp_def = components_registry.get(comp_id)
            if comp_def is None:
                continue
            abilities = (
                comp_def.get("abilities")
                if isinstance(comp_def, dict)
                else getattr(comp_def, "abilities", None)
            ) or {}
            for ability_name, ability_data in abilities.items():
                if ability_name not in ABILITY_STAT_REGISTRY:
                    continue
                # Exercise every likely scope variant to surface
                # misconfigurations. For the purposes of this guard we
                # only need to ensure NO placeholder stat_keys ever leak out.
                scope = (
                    ability_data.get("scope")
                    if isinstance(ability_data, dict)
                    else "self"
                )
                if not isinstance(scope, str):
                    scope = "self"
                entries = emit_entries_for_ability(
                    ability_name,
                    ability_data,
                    scope=scope,
                    owner_team=0,
                    num_teams=2,
                    source=f"test:{design_id}:{comp_id}:{ability_name}",
                    source_modifier_id=design_id,
                    source_modifier_name=design.get("display_name", design_id),
                )
                for _, entry in entries:
                    if entry.effect.stat_key == "placeholder":
                        failures.append(
                            f"{design_id}/{comp_id}/{ability_name}: "
                            f"emitted placeholder stat_key"
                        )
    assert not failures, "Placeholder emissions detected:\n" + "\n".join(failures)


def test_all_complex_abilities_have_registry_coverage(_complex_designs, _registries):
    """Forward-compat: if a complex design references a combat-class
    ability that is NOT in `ABILITY_STAT_REGISTRY`, fail loudly so the
    registry is updated before the feature lands silently.

    "Combat-class" is currently defined as the three class names
    {ShieldProjection, ShieldModifier, DamageModifier}. If a new combat-
    effect ability class is introduced (e.g., ThrustModifier), add it
    to `ABILITY_STAT_REGISTRY` — this test catches the omission.
    """
    from game.simulation.combat.ability_stat_registry import ABILITY_STAT_REGISTRY

    # Maintainer-controlled allowlist of ability-class names that the
    # registry deliberately skips (non-combat abilities that happen to
    # appear on complex components). Empty for now; add as needed to
    # keep this test distinguishable from intentional omissions.
    KNOWN_NON_COMBAT_ABILITIES: set[str] = set()

    components_registry = _registries.get_components()
    missing = []  # list of (design_id, comp_id, ability_name) triples
    for design_id, design in _complex_designs:
        for component_data in _iter_design_components(design):
            comp_id = component_data.get("id")
            if not comp_id:
                continue
            comp_def = components_registry.get(comp_id)
            if comp_def is None:
                continue
            abilities = (
                comp_def.get("abilities")
                if isinstance(comp_def, dict)
                else getattr(comp_def, "abilities", None)
            ) or {}
            for ability_name in abilities:
                # Combat-class heuristic: any ability class name ending
                # with "Modifier" or "Projection" that isn't in the
                # registry is flagged. Narrow enough to catch new
                # combat abilities, loose enough to ignore economy /
                # strategic-only abilities.
                looks_combat = ability_name.endswith(
                    ("Modifier", "Projection")
                )
                if not looks_combat:
                    continue
                if ability_name in KNOWN_NON_COMBAT_ABILITIES:
                    continue
                if ability_name not in ABILITY_STAT_REGISTRY:
                    missing.append((design_id, comp_id, ability_name))
    assert not missing, (
        "Combat-looking abilities NOT in ABILITY_STAT_REGISTRY:\n"
        + "\n".join(f"  {d}/{c}/{a}" for d, c, a in missing)
        + "\n\nAdd the ability to ABILITY_STAT_REGISTRY in "
        "`game/simulation/combat/ability_stat_registry.py`, or add it "
        "to KNOWN_NON_COMBAT_ABILITIES in this test if it intentionally "
        "doesn't affect combat."
    )
