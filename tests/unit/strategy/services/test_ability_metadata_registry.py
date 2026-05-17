"""Contract tests for the unified ``AbilityMetadataRegistry`` (PROJ-429 / TD-07).

These tests pin the registry's public API and the parity invariant that
every name currently hardcoded in any strategy-layer ability-name set has
at least one tag in the unified registry. The parity test is permanent —
it is the regression guard that prevents future drift between consumers
and the registry.

Cycle-safety: a separate hardened AST guard pins
``ability_metadata.py`` to import nothing from
``game.simulation.components.abilities`` at module load (top-level
imports, class-body imports, dynamic ``importlib.import_module(...)`` and
``__import__(...)`` calls at module scope). The guard mirrors the
PROJ-424 ``OrderMetadataView`` and PROJ-428 ``TurnPhaseRegistry`` guards.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

from game.strategy.services.ability_metadata import (
    AbilityMetadata,
    EffectFacet,
    EnergyFacet,
    RoleTag,
    StrategicKind,
    abilities_with_kind_tag,
    abilities_with_role_tag,
    ability_action_time_field,
    ability_drains_energy,
    ability_has_kind_tag,
    ability_has_role_tag,
    get_ability_metadata,
)


# ---------------------------------------------------------------------------
# Public-API smoke tests.
# ---------------------------------------------------------------------------


def test_get_ability_metadata_returns_effect_facet_for_shield_modifier() -> None:
    meta = get_ability_metadata("ShieldModifier")
    assert meta is not None
    assert isinstance(meta, AbilityMetadata)
    assert meta.effect is not None
    assert meta.effect.kind == "multiplier"


def test_get_ability_metadata_unknown_returns_none() -> None:
    assert get_ability_metadata("NotAnAbilityName_xyz") is None


def test_ability_has_role_tag_carrier_for_tactical_fighter_launch() -> None:
    assert ability_has_role_tag("TacticalFighterLaunch", RoleTag.CARRIER)


def test_ability_has_role_tag_weapon_for_beam_weapon() -> None:
    assert ability_has_role_tag("BeamWeaponAbility", RoleTag.WEAPON)


def test_ability_has_kind_tag_stabilizer_for_geologic_stabilizer() -> None:
    assert ability_has_kind_tag("GeologicStabilizer", StrategicKind.STABILIZER)


def test_ability_has_kind_tag_superweapon_for_destroy_planet() -> None:
    assert ability_has_kind_tag("DestroyPlanet", StrategicKind.SUPERWEAPON)


def test_abilities_with_role_tag_carrier_matches_legacy_carrier_set() -> None:
    expected_carriers = {
        "TacticalFighterLaunch",
        "StrategicFighterLaunch",
        "TacticalSatelliteLaunch",
        "StrategicSatelliteLaunch",
    }
    assert abilities_with_role_tag(RoleTag.CARRIER) == frozenset(expected_carriers)


def test_abilities_with_kind_tag_combat_modifier_matches_three_multipliers() -> None:
    assert abilities_with_kind_tag(StrategicKind.COMBAT_MODIFIER) == frozenset({
        "ShieldModifier", "DamageModifier", "ThrustModifier",
    })


def test_shield_projection_is_flat_bonus_not_modifier() -> None:
    """``ShieldProjection`` accumulates as a flat bonus, not a multiplier.

    See decisions.md row 4: lumping it with COMBAT_MODIFIER would route it
    through ``aggregate_multipliers`` and change behavior.
    """
    assert ability_has_kind_tag("ShieldProjection", StrategicKind.COMBAT_FLAT_BONUS)
    assert not ability_has_kind_tag("ShieldProjection", StrategicKind.COMBAT_MODIFIER)


def test_ability_action_time_field_defaults_to_action_time() -> None:
    # ColonizePlanet is a generic action-time order.
    assert ability_action_time_field("ColonizePlanet") == "action_time"


def test_ability_action_time_field_planetary_shield_uses_activation_time() -> None:
    meta = get_ability_metadata("PlanetaryShield")
    assert meta is not None and meta.energy is not None
    assert meta.energy.activation_time_field == "activation_time"


def test_ability_drains_energy_planetary_shield() -> None:
    assert ability_drains_energy("PlanetaryShield") is True


def test_ability_drains_energy_unknown_is_false() -> None:
    assert ability_drains_energy("NotAnAbility_xyz") is False


def test_effect_facet_geologic_stabilizer_is_activatable_multiplier() -> None:
    meta = get_ability_metadata("GeologicStabilizer")
    assert meta is not None and meta.effect is not None
    assert isinstance(meta.effect, EffectFacet)
    assert meta.effect.kind == "multiplier"
    assert meta.effect.is_activatable_hint is True


def test_energy_facet_typed() -> None:
    meta = get_ability_metadata("PlanetaryShield")
    assert meta is not None
    assert isinstance(meta.energy, EnergyFacet)


def test_gravity_modifier_is_energy_draining(
) -> None:
    """PROJ-435: ``GravityModifier`` is a real planet-scope activatable
    energy-draining ability (component class
    ``GravityModifierAbility``; queried by
    ``planet_modifier_effect_engine._has_active_ability``). It must
    appear in ``AbilityMetadataRegistry`` with the ``ENERGY_DRAINING``
    kind tag and an ``EnergyFacet(drains_energy=True)`` so the UI can
    iterate it from the registry instead of from a hardcoded literal.
    """
    meta = get_ability_metadata("GravityModifier")
    assert meta is not None, "GravityModifier must be registered (PROJ-435)"
    assert ability_has_kind_tag("GravityModifier", StrategicKind.ENERGY_DRAINING)
    assert ability_drains_energy("GravityModifier") is True
    assert "GravityModifier" in abilities_with_kind_tag(StrategicKind.ENERGY_DRAINING)


def test_radiation_shield_is_energy_draining() -> None:
    """PROJ-435: companion to ``test_gravity_modifier_is_energy_draining``.
    Same rationale — ``RadiationShield`` is a real activatable
    energy-draining planet ability and must be registered.
    """
    meta = get_ability_metadata("RadiationShield")
    assert meta is not None, "RadiationShield must be registered (PROJ-435)"
    assert ability_has_kind_tag("RadiationShield", StrategicKind.ENERGY_DRAINING)
    assert ability_drains_energy("RadiationShield") is True
    assert "RadiationShield" in abilities_with_kind_tag(StrategicKind.ENERGY_DRAINING)


# ---------------------------------------------------------------------------
# Parity: every name currently hardcoded in any strategy-layer ability-name
# set has at least one tag in the unified registry. PERMANENT regression
# guard.
# ---------------------------------------------------------------------------


def _hardcoded_role_names() -> set[str]:
    """Names currently used by `design_role.py` for role classification."""
    return {
        # _WEAPON_ABILITIES
        "BeamWeaponAbility", "ProjectileWeaponAbility", "SeekerWeaponAbility",
        # _SENSOR_ABILITIES
        "SensorAbility", "ECMAbility",
        # _SUPPORT_ABILITIES
        "ShipRepair", "SpaceShipyard", "ResourceGeneration",
        # _CARRIER_ABILITIES
        "TacticalFighterLaunch", "StrategicFighterLaunch",
        "TacticalSatelliteLaunch", "StrategicSatelliteLaunch",
        # _COMMAND_ABILITIES + inline literal at design_role.py:105
        "TacticalDataLinkAbility", "CommandAndControl",
    }


def _hardcoded_stabilizer_names() -> set[str]:
    """Names from STABILIZERS in stabilizer_registry.py."""
    from game.strategy.services.stabilizer_registry import STABILIZERS

    return {s.ability_name for s in STABILIZERS}


def _hardcoded_superweapon_names() -> set[str]:
    """Non-None ability names from SUPERWEAPONS in superweapon_registry.py."""
    from game.strategy.services.superweapon_registry import SUPERWEAPONS

    return {s.ability_name for s in SUPERWEAPONS if s.ability_name is not None}


def _hardcoded_combat_modifier_names() -> set[str]:
    """The three multiplier abilities + ShieldProjection."""
    return {"ShieldModifier", "DamageModifier", "ThrustModifier", "ShieldProjection"}


def _hardcoded_other_literals() -> set[str]:
    """Other strategy-layer hardcoded literals: BuildRateBooster, PlanetaryShield."""
    return {"BuildRateBooster", "PlanetaryShield"}


@pytest.mark.parametrize("ability_name", sorted(
    _hardcoded_role_names()
    | _hardcoded_stabilizer_names()
    | _hardcoded_superweapon_names()
    | _hardcoded_combat_modifier_names()
    | _hardcoded_other_literals()
))
def test_every_hardcoded_name_has_at_least_one_tag(ability_name: str) -> None:
    """Permanent regression guard: every strategy-layer-hardcoded ability
    name must have at least one tag in the unified registry.

    If you add a new hardcoded ability literal anywhere in
    ``game/strategy/`` and a consumer pattern matches the existing
    inventory categories, extend this helper's name sets — do not loosen
    the parity test."""
    meta = get_ability_metadata(ability_name)
    assert meta is not None, (
        f"{ability_name!r} not registered in AbilityMetadataRegistry "
        "but is a strategy-layer hardcoded name"
    )
    has_role = bool(meta.role_tags)
    has_kind = bool(meta.kind_tags)
    has_effect = meta.effect is not None
    has_energy = meta.energy is not None
    assert has_role or has_kind or has_effect or has_energy, (
        f"{ability_name!r} has no tags / facets in AbilityMetadataRegistry"
    )


# ---------------------------------------------------------------------------
# Cycle-safety AST guard (mirror of PROJ-424 / PROJ-428).
# ---------------------------------------------------------------------------


_FORBIDDEN_SIMULATION_PATH = "game.simulation.components.abilities"


def _module_load_evaluated_imports(source: str) -> set[str]:
    """Return modules imported / evaluated at module load (top-level
    ``import``, top-level class-body ``import``, top-level
    ``importlib.import_module(...)`` / ``__import__(...)`` calls).

    Imports inside function or method bodies are deferred and not
    collected — that is the lazy-import contract the registry relies on
    for cycle safety.
    """
    tree = ast.parse(source)
    names: set[str] = set()

    def _collect_dynamic_from_call(call: ast.Call) -> None:
        target: str | None = None
        func = call.func
        if isinstance(func, ast.Attribute) and func.attr == "import_module":
            target = "import_module"
        elif isinstance(func, ast.Name) and func.id == "__import__":
            target = "__import__"
        if target is None:
            return
        if not call.args:
            return
        first = call.args[0]
        if isinstance(first, ast.Constant) and isinstance(first.value, str):
            names.add(first.value)

    def _scan_statement_list(stmts: list[ast.stmt]) -> None:
        for node in stmts:
            if isinstance(node, ast.Import):
                for alias in node.names:
                    names.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module is not None:
                    names.add(node.module)
            elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                _collect_dynamic_from_call(node.value)
            elif isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
                _collect_dynamic_from_call(node.value)
            elif isinstance(node, ast.AnnAssign) and isinstance(node.value, ast.Call):
                _collect_dynamic_from_call(node.value)

    _scan_statement_list(tree.body)
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            _scan_statement_list(node.body)
    return names


def _module_level_imports(source_path: Path) -> set[str]:
    return _module_load_evaluated_imports(source_path.read_text(encoding="utf-8"))


def test_guard_detects_class_body_import_of_simulation_abilities() -> None:
    source = (
        "class _R:\n"
        "    from game.simulation.components.abilities import foo\n"
        "    pass\n"
    )
    found = _module_load_evaluated_imports(source)
    assert _FORBIDDEN_SIMULATION_PATH in found


def test_guard_detects_top_level_importlib_import_module_call() -> None:
    source = (
        "import importlib\n"
        "importlib.import_module(\"game.simulation.components.abilities\")\n"
    )
    found = _module_load_evaluated_imports(source)
    assert _FORBIDDEN_SIMULATION_PATH in found


def test_guard_detects_top_level_dunder_import_call() -> None:
    source = "__import__(\"game.simulation.components.abilities\")\n"
    found = _module_load_evaluated_imports(source)
    assert _FORBIDDEN_SIMULATION_PATH in found


def test_guard_ignores_function_body_import() -> None:
    source = (
        "def helper():\n"
        "    from game.simulation.components.abilities import foo\n"
        "    return foo\n"
    )
    found = _module_load_evaluated_imports(source)
    assert _FORBIDDEN_SIMULATION_PATH not in found


def test_ability_metadata_module_does_not_import_simulation_abilities() -> None:
    """``ability_metadata`` must remain a leaf module — no module-load
    evaluation of ``game.simulation.components.abilities`` by any
    mechanism. Names are strings; metadata is pure data.

    The registry's job is categorization, not instantiation. Importing
    simulation-layer ability classes here would create a cycle (strategy
    layer depends on simulation, and a number of simulation abilities
    are queried via strategy services). The lazy-import contract is the
    single linchpin.
    """
    import game.strategy.services.ability_metadata as ability_metadata_mod

    source_path = Path(ability_metadata_mod.__file__)
    module_load_imports = _module_level_imports(source_path)
    forbidden_prefix = "game.simulation"
    offenders = sorted(
        name for name in module_load_imports if name.startswith(forbidden_prefix)
    )
    assert not offenders, (
        f"ability_metadata.py must not evaluate any simulation-layer "
        f"import at module load; observed: {offenders}"
    )
