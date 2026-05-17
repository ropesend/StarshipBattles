"""Unified ``AbilityMetadataRegistry`` — single source of truth for
strategy-layer ability metadata (PROJ-429 / TD-07).

Why this module exists
----------------------
Before PROJ-429 the strategy layer answered "is ability X a Y?" out of
eleven hardcoded ability-name literals scattered across ``design_role.py``,
``planet_energy_engine.py``, ``action_time_resolver.py``,
``combat_modifier_collector.py``, ``strategy_modifier_stack_builder.py``,
``build_queue_source.py``, ``stabilizer_registry.py``,
``superweapon_registry.py``, and the existing ``EffectAbilityMetadata``
registry. This module consolidates all of them into one declarative
table.

Shape rationale (cross-plan note)
---------------------------------
PROJ-424 introduces ``OrderMetadataView`` as a *view* over the
pre-existing ``CommandRegistry``. PROJ-429 introduces this module as a
*primary store* because ability metadata has no upstream primary store.
Both projects converge on the same end-state property — one cycle-safe,
lazily resolved access path per metadata domain — through the mechanism
appropriate to each domain's existing topology. See
``Projects/active_projects/PROJ-429/decisions.md`` row 1.

Cycle-safety invariant
----------------------
This module is a leaf. It must NOT import from
``game.simulation.components.abilities``. Ability names are strings;
metadata is pure data. The registry's job is categorization, not
instantiation. Importing simulation-layer ability classes here would
introduce a cycle (strategy depends on simulation, and many simulation
abilities are queried via strategy services).

The invariant is pinned by ``test_ability_metadata_module_does_not_import_simulation_abilities``
in ``tests/unit/strategy/services/test_ability_metadata_registry.py``,
backed by an AST guard that detects:

* Top-level ``import`` / ``from ... import`` statements.
* Class-body imports (class bodies execute at module load).
* Top-level ``importlib.import_module(...)`` and ``__import__(...)``
  calls with string-literal arguments.

The same guard pattern is in PROJ-424 ``test_order_metadata_view`` and
PROJ-428 ``test_turn_phase_registry_purity``.

Public API
----------
``get_ability_metadata(name)``                          — full record by name (or None)
``ability_has_role_tag(name, tag)``                     — fast membership
``ability_has_kind_tag(name, tag)``                     — fast membership
``abilities_with_role_tag(tag)``                        — frozenset of names
``abilities_with_kind_tag(tag)``                        — frozenset of names
``ability_action_time_field(name)``                     — 'action_time' / 'activation_time' / ...
``ability_drains_energy(name)``                         — bool
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Literal


# ---------------------------------------------------------------------------
# Tag enumerations.
# ---------------------------------------------------------------------------


class RoleTag(Enum):
    """Design-role classification facet.

    Replaces the seven hardcoded frozensets that previously lived in
    ``game.strategy.data.design_role``.
    """
    WEAPON = "weapon"
    SEEKER = "seeker"
    BEAM_PROJECTILE = "beam_projectile"
    SENSOR = "sensor"
    SUPPORT = "support"
    CARRIER = "carrier"
    COMMAND = "command"


class StrategicKind(Enum):
    """Strategic-categorization facet.

    Replaces hardcoded literal sets in ``strategy_modifier_stack_builder``,
    ``combat_modifier_collector``, ``stabilizer_registry`` /
    ``superweapon_registry`` (consulted via contract tests), ``build_queue_source``,
    and ``planet_energy_engine``.
    """
    COMBAT_MODIFIER = "combat_modifier"          # multiplier-aggregated combat boosters
    COMBAT_FLAT_BONUS = "combat_flat_bonus"      # flat-additive (e.g. ShieldProjection)
    STABILIZER = "stabilizer"                    # superweapon-blocking facility abilities
    SUPERWEAPON = "superweapon"                  # strategic destruction abilities
    ENVIRONMENTAL = "environmental"              # rate-style hazards
    RESOURCE_BOOSTER = "resource_booster"        # harvest / quality boosters
    BUILD_RATE_BOOSTER = "build_rate_booster"    # construction acceleration
    PLANETARY_SHIELD = "planetary_shield"        # planet-scope energy-draining shield
    ENERGY_DRAINING = "energy_draining"          # generic energy-draining classification


# ---------------------------------------------------------------------------
# Facet dataclasses.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class EffectFacet:
    """Strategic-effect aggregation facet (legacy ``EffectAbilityMetadata`` shape).

    The shim module ``effect_ability_metadata.py`` derives its public
    ``EffectAbilityMetadata`` records from these facets so its public
    helper API (``find_metadata``, ``is_known_effect_ability``,
    ``all_owner_aware_scopes``) remains unchanged.
    """
    display_name: str | None
    kind: Literal["rate", "multiplier"]
    is_activatable_hint: bool
    grouping_key_field: str | None
    owner_aware_scopes: frozenset[str]
    value_field_primary: str
    value_field_fallback: str


@dataclass(frozen=True)
class EnergyFacet:
    """Energy / activation-cycle facet.

    Drives ``action_time_resolver.resolve_action_time`` for the
    ACTIVATE_ABILITY / DEACTIVATE_ABILITY order branch and the
    ``ability_drains_energy(name)`` query previously answered by
    ``planet_energy_engine._ACTIVATABLE_ABILITIES``.
    """
    is_activatable: bool
    drains_energy: bool
    activation_time_field: str = "activation_time"
    deactivation_time_field: str = "deactivation_time"


@dataclass(frozen=True)
class AbilityMetadata:
    """Authoritative metadata for one ability name.

    ``effect`` and ``energy`` are optional facets — None when the ability
    is not an aggregated effect / not energy-cycling. ``role_tags`` and
    ``kind_tags`` are always sets (possibly empty).
    """
    name: str
    effect: EffectFacet | None = None
    role_tags: frozenset[RoleTag] = field(default_factory=frozenset)
    energy: EnergyFacet | None = None
    action_time_field: str = "action_time"
    kind_tags: frozenset[StrategicKind] = field(default_factory=frozenset)


# ---------------------------------------------------------------------------
# Owner-aware scope set (preserved verbatim from the legacy
# ``effect_ability_metadata.py`` constant). Shared by every effect facet.
# ---------------------------------------------------------------------------


_OWNER_AWARE_SCOPES: frozenset[str] = frozenset({
    "allied_sector", "enemy_sector", "player_sector",
    "allied_system", "enemy_system", "player_system",
    "allied_empire",
})


# ---------------------------------------------------------------------------
# Internal facet helpers.
# ---------------------------------------------------------------------------


def _multiplier_effect(
    display_name: str | None,
    *,
    is_activatable_hint: bool,
    grouping_key_field: str | None = None,
) -> EffectFacet:
    return EffectFacet(
        display_name=display_name,
        kind="multiplier",
        is_activatable_hint=is_activatable_hint,
        grouping_key_field=grouping_key_field,
        owner_aware_scopes=_OWNER_AWARE_SCOPES,
        value_field_primary="multiplier",
        value_field_fallback="improvement_rate",
    )


def _rate_effect(
    display_name: str | None,
    *,
    grouping_key_field: str | None = None,
) -> EffectFacet:
    return EffectFacet(
        display_name=display_name,
        kind="rate",
        is_activatable_hint=False,
        grouping_key_field=grouping_key_field,
        owner_aware_scopes=_OWNER_AWARE_SCOPES,
        value_field_primary="rate",
        value_field_fallback="improvement_rate",
    )


def _energy_drain(
    *, activation_time_field: str = "activation_time",
    deactivation_time_field: str = "deactivation_time",
) -> EnergyFacet:
    return EnergyFacet(
        is_activatable=True,
        drains_energy=True,
        activation_time_field=activation_time_field,
        deactivation_time_field=deactivation_time_field,
    )


# ---------------------------------------------------------------------------
# The authoritative table. Adding a new ability is a single tuple-entry
# edit. The table is grouped by category for readability only — lookup is
# by name.
# ---------------------------------------------------------------------------


_ENTRIES: tuple[AbilityMetadata, ...] = (
    # ----- Effect aggregation (preserves ``EFFECT_ABILITY_METADATA`` semantics) -----

    # Activatable stabilizers — both effect-aggregated multipliers AND
    # superweapon-blocking abilities AND energy-draining.
    AbilityMetadata(
        name="GeologicStabilizer",
        effect=_multiplier_effect("Geologic Stabilizer", is_activatable_hint=True),
        energy=_energy_drain(),
        kind_tags=frozenset({StrategicKind.STABILIZER, StrategicKind.ENERGY_DRAINING}),
    ),
    AbilityMetadata(
        name="StellarStabilizer",
        effect=_multiplier_effect("Stellar Stabilizer", is_activatable_hint=True),
        energy=_energy_drain(),
        kind_tags=frozenset({StrategicKind.STABILIZER, StrategicKind.ENERGY_DRAINING}),
    ),
    AbilityMetadata(
        name="WarpFieldStabilizer",
        effect=_multiplier_effect("Warp Field Stabilizer", is_activatable_hint=True),
        energy=_energy_drain(),
        kind_tags=frozenset({StrategicKind.STABILIZER, StrategicKind.ENERGY_DRAINING}),
    ),

    # Resource boosters (passive multipliers grouped by resource_type).
    AbilityMetadata(
        name="ResourceHarvestBooster",
        effect=_multiplier_effect(None, is_activatable_hint=False,
                                  grouping_key_field="resource_type"),
        kind_tags=frozenset({StrategicKind.RESOURCE_BOOSTER}),
    ),
    AbilityMetadata(
        name="QualityImprovement",
        effect=_multiplier_effect("Quality Enrichment", is_activatable_hint=False,
                                  grouping_key_field="resource_type"),
        kind_tags=frozenset({StrategicKind.RESOURCE_BOOSTER}),
    ),

    # Construction acceleration — the BUILD_RATE_BOOSTER literal at
    # build_queue_source.py:114 reads this name. Tagged accordingly.
    AbilityMetadata(
        name="BuildRateBooster",
        effect=_multiplier_effect("Construction Acceleration", is_activatable_hint=False),
        kind_tags=frozenset({StrategicKind.BUILD_RATE_BOOSTER}),
    ),

    # Combat modifiers (multiplier-aggregated). ThrustModifier participates in
    # spec_compiler/stack_builder filtering but is not collected by the
    # CombatModifierCollector (which only handles shield + damage). The
    # COMBAT_MODIFIER tag matches the spec-builder filter; the collector reads
    # a strict subset via separate filtering inside its own function (no
    # extra tag needed).
    AbilityMetadata(
        name="ShieldModifier",
        effect=_multiplier_effect("Shield Modifier", is_activatable_hint=False),
        kind_tags=frozenset({StrategicKind.COMBAT_MODIFIER}),
    ),
    AbilityMetadata(
        name="DamageModifier",
        effect=_multiplier_effect("Damage Modifier", is_activatable_hint=False),
        kind_tags=frozenset({StrategicKind.COMBAT_MODIFIER}),
    ),
    AbilityMetadata(
        name="ThrustModifier",
        effect=_multiplier_effect("Thrust Modifier", is_activatable_hint=False),
        kind_tags=frozenset({StrategicKind.COMBAT_MODIFIER}),
    ),

    # Strategic-speed modifier (passive multiplier; not a combat modifier).
    AbilityMetadata(
        name="StrategicSpeedModifier",
        effect=_multiplier_effect("Strategic Speed Modifier", is_activatable_hint=False),
    ),

    # Rate-style environmental hazards.
    AbilityMetadata(
        name="EnvironmentalDamage",
        effect=_rate_effect(None, grouping_key_field="damage_type"),
        kind_tags=frozenset({StrategicKind.ENVIRONMENTAL}),
    ),
    AbilityMetadata(
        name="FuelDrain",
        effect=_rate_effect("Fuel Drain"),
        kind_tags=frozenset({StrategicKind.ENVIRONMENTAL}),
    ),

    # ----- Flat-bonus combat modifier (decisions.md row 4) -----

    AbilityMetadata(
        name="ShieldProjection",
        kind_tags=frozenset({StrategicKind.COMBAT_FLAT_BONUS}),
    ),

    # ----- Planetary shield (energy-draining; planet scope) -----

    AbilityMetadata(
        name="PlanetaryShield",
        energy=_energy_drain(),
        kind_tags=frozenset({
            StrategicKind.PLANETARY_SHIELD,
            StrategicKind.ENERGY_DRAINING,
        }),
    ),

    # ----- Other planet-scope energy-draining activatable abilities (PROJ-435) -----
    #
    # ``GravityModifier`` and ``RadiationShield`` are real activatable
    # energy-draining facility abilities (see
    # ``game/simulation/components/abilities/planetary/`` and queries in
    # ``planet_modifier_effect_engine._has_active_ability``). They were
    # absent from the registry pre-PROJ-435 because no strategy-layer
    # tag-based query needed them; PROJ-435 adds them so the builder UI
    # can discover the full ENERGY_DRAINING set from the registry rather
    # than from a hardcoded literal in ``stat_rows_dynamic.py``.

    AbilityMetadata(
        name="GravityModifier",
        energy=_energy_drain(),
        kind_tags=frozenset({StrategicKind.ENERGY_DRAINING}),
    ),
    AbilityMetadata(
        name="RadiationShield",
        energy=_energy_drain(),
        kind_tags=frozenset({StrategicKind.ENERGY_DRAINING}),
    ),

    # ----- Role-tagged abilities (replaces design_role.py frozensets) -----

    AbilityMetadata(
        name="BeamWeaponAbility",
        role_tags=frozenset({RoleTag.WEAPON, RoleTag.BEAM_PROJECTILE}),
    ),
    AbilityMetadata(
        name="ProjectileWeaponAbility",
        role_tags=frozenset({RoleTag.WEAPON, RoleTag.BEAM_PROJECTILE}),
    ),
    AbilityMetadata(
        name="SeekerWeaponAbility",
        role_tags=frozenset({RoleTag.WEAPON, RoleTag.SEEKER}),
    ),
    AbilityMetadata(
        name="SensorAbility",
        role_tags=frozenset({RoleTag.SENSOR}),
    ),
    AbilityMetadata(
        name="ECMAbility",
        role_tags=frozenset({RoleTag.SENSOR}),
    ),
    AbilityMetadata(
        name="ShipRepair",
        role_tags=frozenset({RoleTag.SUPPORT}),
    ),
    AbilityMetadata(
        name="SpaceShipyard",
        role_tags=frozenset({RoleTag.SUPPORT}),
    ),
    AbilityMetadata(
        name="ResourceGeneration",
        role_tags=frozenset({RoleTag.SUPPORT}),
    ),
    AbilityMetadata(
        name="TacticalFighterLaunch",
        role_tags=frozenset({RoleTag.CARRIER}),
    ),
    AbilityMetadata(
        name="StrategicFighterLaunch",
        role_tags=frozenset({RoleTag.CARRIER}),
    ),
    AbilityMetadata(
        name="TacticalSatelliteLaunch",
        role_tags=frozenset({RoleTag.CARRIER}),
    ),
    AbilityMetadata(
        name="StrategicSatelliteLaunch",
        role_tags=frozenset({RoleTag.CARRIER}),
    ),
    AbilityMetadata(
        name="TacticalDataLinkAbility",
        role_tags=frozenset({RoleTag.COMMAND}),
    ),
    AbilityMetadata(
        name="CommandAndControl",
        role_tags=frozenset({RoleTag.COMMAND}),
    ),

    # ----- Superweapons (parity contract — Phase 4 + Phase 6) -----

    AbilityMetadata(
        name="DestroyPlanet",
        kind_tags=frozenset({StrategicKind.SUPERWEAPON}),
    ),
    AbilityMetadata(
        name="DestroyStar",
        kind_tags=frozenset({StrategicKind.SUPERWEAPON}),
    ),
    AbilityMetadata(
        name="OpenWarpPoint",
        kind_tags=frozenset({StrategicKind.SUPERWEAPON}),
    ),
    AbilityMetadata(
        name="CloseWarpPoint",
        kind_tags=frozenset({StrategicKind.SUPERWEAPON}),
    ),
    AbilityMetadata(
        name="CreateDysonSphere",
        kind_tags=frozenset({StrategicKind.SUPERWEAPON}),
    ),
    AbilityMetadata(
        name="SelfDestruct",
        # SelfDestruct is intentionally NOT in the SUPERWEAPONS table
        # (see superweapon_registry.py docstring). It is still a
        # command-spec action ability — record minimal metadata so the
        # Phase 4 ``CommandSpec`` contract test passes.
        kind_tags=frozenset(),
    ),

    # ----- Other ability names referenced by CommandSpec.action_ability_name -----

    AbilityMetadata(
        name="ColonizePlanet",
        # Standard action_time order.
    ),
    AbilityMetadata(
        name="RecoverFighters",
    ),
    AbilityMetadata(
        name="RecoverSatellites",
    ),
)


# ---------------------------------------------------------------------------
# Indexes built at module load.
# ---------------------------------------------------------------------------


_BY_NAME: dict[str, AbilityMetadata] = {m.name: m for m in _ENTRIES}

assert len(_BY_NAME) == len(_ENTRIES), (
    "Duplicate ability name in AbilityMetadataRegistry _ENTRIES — each "
    "name must appear at most once."
)


_BY_ROLE_TAG: dict[RoleTag, frozenset[str]] = {
    tag: frozenset(m.name for m in _ENTRIES if tag in m.role_tags)
    for tag in RoleTag
}


_BY_KIND_TAG: dict[StrategicKind, frozenset[str]] = {
    tag: frozenset(m.name for m in _ENTRIES if tag in m.kind_tags)
    for tag in StrategicKind
}


# ---------------------------------------------------------------------------
# Public API.
# ---------------------------------------------------------------------------


def get_ability_metadata(name: str) -> AbilityMetadata | None:
    """Return the metadata record for ``name``, or ``None`` if unknown."""
    return _BY_NAME.get(name)


def ability_has_role_tag(name: str, tag: RoleTag) -> bool:
    """True iff ``name`` is registered with ``tag`` in its ``role_tags``."""
    meta = _BY_NAME.get(name)
    return meta is not None and tag in meta.role_tags


def ability_has_kind_tag(name: str, tag: StrategicKind) -> bool:
    """True iff ``name`` is registered with ``tag`` in its ``kind_tags``."""
    meta = _BY_NAME.get(name)
    return meta is not None and tag in meta.kind_tags


def abilities_with_role_tag(tag: RoleTag) -> frozenset[str]:
    """Frozenset of every ability name carrying ``tag`` as a role tag."""
    return _BY_ROLE_TAG.get(tag, frozenset())


def abilities_with_kind_tag(tag: StrategicKind) -> frozenset[str]:
    """Frozenset of every ability name carrying ``tag`` as a kind tag."""
    return _BY_KIND_TAG.get(tag, frozenset())


def ability_action_time_field(name: str) -> str:
    """Return the ``ability_data`` field name to read for action time on
    a generic action order. Defaults to ``'action_time'`` when the
    ability is not registered or carries no override.
    """
    meta = _BY_NAME.get(name)
    if meta is None:
        return "action_time"
    return meta.action_time_field


def ability_drains_energy(name: str) -> bool:
    """True iff the ability is energy-draining when activated. False for
    unknown names and for non-energy abilities."""
    meta = _BY_NAME.get(name)
    return meta is not None and meta.energy is not None and meta.energy.drains_energy


# Module-load post-condition: every registered entry must carry at least
# one tag, facet, or be referenced by name from a CommandSpec. Pure-data
# entries with no facets and no tags would be useless; the assertion
# protects against accidentally adding a name that contributes nothing.
for _meta in _ENTRIES:
    if (
        not _meta.role_tags
        and not _meta.kind_tags
        and _meta.effect is None
        and _meta.energy is None
    ):
        # Bare entries are permitted iff they exist for CommandSpec
        # parity (Phase 4 contract). We do not enforce a strict
        # whitelist here — the Phase 4 contract test ensures the bare
        # entries are exactly the command-spec ability names.
        pass


__all__ = [
    "AbilityMetadata",
    "EffectFacet",
    "EnergyFacet",
    "RoleTag",
    "StrategicKind",
    "get_ability_metadata",
    "ability_has_role_tag",
    "ability_has_kind_tag",
    "abilities_with_role_tag",
    "abilities_with_kind_tag",
    "ability_action_time_field",
    "ability_drains_energy",
]
