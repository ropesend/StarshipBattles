# PROJ-429 Design — Ability Metadata Unification

**Source:** [TD-07 plan](../../../Reviews/results/2026-05-16_strategy-layer-tech-debt-review/Verified%20Problem%20Remediation%20Plans/TD-07_ability_metadata_unification.md)
**Status:** Initialized 2026-05-16. **Execution blocked on PROJ-424 (TD-03) completing.**

---

## Problem

Strategy-layer ability metadata is fragmented. The verification sweep located **at least eleven** distinct hardcoded ability-name sets across `game/strategy/`, of which one (`_ACTIVATABLE_ABILITIES` in `planet_energy_engine.py:80-89`) is dead code. The one good registry (`EffectAbilityMetadata` at `game/strategy/services/effect_ability_metadata.py:110-141`) covers only one axis — strategic-effect aggregation — and answers four of the many questions consumers ask about an ability.

What `EffectAbilityMetadata` does NOT answer today:

- Design-role classification (`_CARRIER_ABILITIES`, `_WEAPON_ABILITIES`, etc.)
- Energy-draining classification (`_ACTIVATABLE_ABILITIES`)
- Order-type → ability-name (lives in `CommandRegistry.action_ability_name`)
- Action-time-field name (`activation_time` / `deactivation_time` / `action_time`)
- Which abilities are strategic superweapons (`SUPERWEAPONS` tuple)
- Which abilities are stabilizers (`STABILIZERS` tuple)
- Which abilities are combat modifiers (the three multipliers are listed, but re-encoded as a literal set in `spec_compiler.py:827` and again in `combat_modifier_collector.py:96,127`)
- Which abilities are strategic fleet combat boosters/suppressors (`ShieldProjection` is **not** in `EffectAbilityMetadata` at all)

One ability family (`ShieldModifier`) is currently authored across at least four files. Cross-file name equality is enforced by tests, not by structure.

---

## Why a Primary Registry, Not a View (cross-plan note)

PROJ-424 introduces an `OrderMetadataView` — a lazy live reader over the pre-existing `CommandRegistry`. PROJ-429 introduces an `AbilityMetadataRegistry` — a **primary store**. The shape choice is structural:

| Domain | Existing primary store? | Therefore... |
|--------|-------------------------|--------------|
| Order metadata | **Yes** — `CommandRegistry` | PROJ-424 builds a **view** (don't duplicate truth). |
| Ability metadata | **No** — fragmented across 11+ literals | PROJ-429 builds **the registry** (be the truth). |

Both projects converge on the same end-state property — one cycle-safe, lazily resolved access path per metadata domain. The mechanism differs because the domain topologies differ. This was the verified rationale in the source plan and is the load-bearing justification for the registry-not-view choice in this project.

---

## Schema

The unified registry exposes the following dataclasses (immutable, hashable, pure data — no imports from `game/simulation/`):

```python
@dataclass(frozen=True)
class EffectFacet:
    """The existing EFFECT_ABILITY_METADATA shape, lifted into a facet."""
    display_name: str | None
    kind: Literal['rate', 'multiplier']
    is_activatable_hint: bool
    value_field_primary: str
    value_field_fallback: str | None
    # legacy_fallback_label hook for effect_ability_display.py:88,152 branches

@dataclass(frozen=True)
class EnergyFacet:
    """Energy/activation behavior."""
    is_activatable: bool
    drains_energy: bool
    activation_time_field: str         # default 'activation_time'
    deactivation_time_field: str       # default 'deactivation_time'

@dataclass(frozen=True)
class AbilityMetadata:
    name: str                                  # canonical key, e.g. "ShieldModifier"
    effect: EffectFacet | None                 # None if not an aggregated effect
    role_tags: frozenset[RoleTag]              # design-role classification
    energy: EnergyFacet | None                 # None if not activatable/draining
    action_time_field: str                     # default 'action_time'
    kind_tags: frozenset[StrategicKind]        # strategic-categorization
```

### `RoleTag` (design-role classification facet)

Replaces the seven frozensets in `design_role.py:56-70`:

| Tag | Replaces |
|-----|----------|
| `WEAPON` | `_WEAPON_ABILITIES` |
| `SEEKER` | `_SEEKER_ABILITIES` |
| `BEAM_PROJECTILE` | `_BEAM_PROJECTILE_ABILITIES` |
| `SENSOR` | `_SENSOR_ABILITIES` |
| `SUPPORT` | `_SUPPORT_ABILITIES` |
| `CARRIER` | `_CARRIER_ABILITIES` |
| `COMMAND` | `_COMMAND_ABILITIES` + the inline `"CommandAndControl"` literal at `design_role.py:105` |

### `StrategicKind` (strategic-categorization facet)

| Tag | Use site |
|-----|----------|
| `COMBAT_MODIFIER` | `combat_modifier_collector.py:96,127` and `spec_compiler.py:827` (the three multiplier abilities) |
| `COMBAT_FLAT_BONUS` | `ShieldProjection` (currently a literal at `combat_modifier_collector.py:109,113`; missing from any metadata registry) |
| `STABILIZER` | Each `STABILIZERS[*].ability_name` in `stabilizer_registry.py:54-70` |
| `SUPERWEAPON` | Each `SUPERWEAPONS[*].ability_name` in `superweapon_registry.py:70-111` |
| `ENVIRONMENTAL` | Rate-style hazards already in `EFFECT_ABILITY_METADATA` |
| `RESOURCE_BOOSTER` | Resource-boost abilities already in `EFFECT_ABILITY_METADATA` |
| `BUILD_RATE_BOOSTER` | `"BuildRateBooster"` literal at `build_queue_source.py:114` |
| `PLANETARY_SHIELD` | `"PlanetaryShield"` literal at `planet_energy_engine.py:48`; symmetric with stabilizers |
| `ENERGY_DRAINING` | (Optional) — replaces the inert `_ACTIVATABLE_ABILITIES` semantics if any consumer still needs the question answered after deletion. The live drain path uses `ComponentActivationState.is_draining_energy` and remains metadata-free at runtime. |

`StabilizerSpec` and `SuperweaponSpec` continue to exist; they own the **operation-specific** data (`scopes`, `blocks`, `target_type`, `consume_ship`, `event_type`) which is not generic ability metadata. The unified registry only owns the **categorization**.

---

## Public API

```python
get_ability_metadata(name: str) -> AbilityMetadata | None
ability_has_role_tag(name: str, tag: RoleTag) -> bool
ability_has_kind_tag(name: str, tag: StrategicKind) -> bool
abilities_with_role_tag(tag: RoleTag) -> frozenset[str]
abilities_with_kind_tag(tag: StrategicKind) -> frozenset[str]
ability_action_time_field(name: str) -> str
ability_drains_energy(name: str) -> bool
```

The registry is a **string-keyed pure-data table**. It must not import from `game/simulation/components/abilities/` — names are strings, metadata is data, the registry stays a leaf in the dependency graph.

---

## Shim: `effect_ability_metadata.py`

Becomes a thin re-export layer. Preserved public surface:

- `EFFECT_ABILITY_METADATA` — derived from the unified registry at import time, same iteration order as today.
- `find_metadata(name)` — returns `EffectAbilityMetadata`-shaped result (now backed by `EffectFacet`).
- `is_known_effect_ability(name)`
- `all_owner_aware_scopes()`
- `EffectAbilityMetadata` — re-exported (alias of `EffectFacet`, or a `@dataclass` wrapper that delegates).

This shim retention is non-negotiable in the early phases: existing callers (`effect_ability_display.py:88,152`, `system_effects_collector.py`, etc.) must continue to import the same names with unchanged behavior. Final convergence (collapsing the shim) is out of scope for this project.

---

## Per-Consumer Migration Order

**One consumer per phase.** Each phase keeps intermediate states green and bounded. The order is chosen so that the easiest, most-mechanical migrations land first, and the TD-03-coupled migration (`action_time_resolver`) lands after the unified registry is fully populated.

| Phase | Consumer | Action | Risk |
|-------|----------|--------|------|
| 1 | (new) `ability_metadata.py` | Build registry from a single tuple literal mirroring `EFFECT_ABILITY_METADATA` plus the additional axes. Parity test asserts every currently-hardcoded name has a tag. | Low. Pure additive. |
| 2 | `design_role.py` | Replace seven frozensets with `abilities_with_role_tag(...)` calls. Delete the constants. | Low. Mechanical. |
| 3 | `planet_energy_engine.py` | Delete dead `_ACTIVATABLE_ABILITIES`. Replace `"PlanetaryShield"` literal at line 48 with `abilities_with_kind_tag(StrategicKind.PLANETARY_SHIELD)`. Preserve `_is_ability_active`, `get_activatable_ability_info`, `get_shield_info` public surface (imported by `test_planet_energy_engine.py:5`). | Low. Dead-code deletion + one literal swap. |
| 4 | `action_time_resolver.py` | Read activation/deactivation time-field name from `EnergyFacet`. Delete empty `ORDER_TO_TIME_FIELD`. Add contract test: every `CommandSpec.action_ability_name` exists in the unified registry. | Medium. Direct TD-03 coupling — re-confirm `CommandSpec.action_ability_name` API shape on entry to this phase per TD-07 Execution Precondition 2. |
| 5 | `combat_modifier_collector.py` + `spec_compiler.py` | Replace `combat_ability_names = {...}` at `spec_compiler.py:827` with `abilities_with_kind_tag(StrategicKind.COMBAT_MODIFIER)`. Replace tuples + literal `"ShieldProjection"` in `combat_modifier_collector.py:96,109,113,127`. Add `ShieldProjection` to the registry as `COMBAT_FLAT_BONUS`, **not** `COMBAT_MODIFIER`, so it stays out of the multiplier aggregation path. | Medium. Three call sites + `ShieldProjection` modeling decision. Re-run integration tests under `tests/integration/` that touch combat-modifier paths before phase exit. |
| 6 | `build_queue_source.py` + stabilizer/superweapon contracts | Replace `"BuildRateBooster"` literal at line 114 with a kind-tag query. Add contract tests: every `STABILIZERS[*].ability_name` has `kind_tag=STABILIZER`, every `SUPERWEAPONS[*].ability_name` has `kind_tag=SUPERWEAPON`. Do not collapse the spec tables. | Low. Mostly contract tests. |
| 7 | `docs/systems/strategy_layer.md` | Make registry the canonical strategy-facing source of truth. Update `docs/guides/adding_abilities.md` only if it has a live successor (TD-07 notes the current copy may be under `_marked_for_deletion_2026-05-29/`). Run full sharded suite. | Low. Doc + full validation. |

---

## What Stops Being Possible (end-state)

- Adding a new carrier-class launch ability without updating any classification table — it is just a new entry with `CARRIER` in `role_tags`.
- Adding a new energy-draining facility ability without touching `_ACTIVATABLE_ABILITIES` — that constant is deleted; the facet drives drain detection; the live runtime path still uses `ComponentActivationState`.
- Adding a new combat-modifier ability without re-encoding its name in `spec_compiler.py:827` and `combat_modifier_collector.py:96`.
- Diverging names between `combat_modifier_collector` and `spec_compiler` — the registry is the single answer.
- Adding a stabilizer to `STABILIZERS` or a superweapon to `SUPERWEAPONS` without a matching metadata entry — contract tests fail.

---

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Import cycle: `ability_metadata.py` references abilities defined in `game/simulation/components/abilities/`. | Don't import from simulation. Names are strings. Registry is in `game/strategy/services/` and stays a leaf. |
| Duplication between `CommandSpec.action_ability_name` and the unified registry. | Phase 4 contract test makes this an **enforced** relationship, not a duplication. Adding a command without an ability metadata entry fails CI. |
| `_ACTIVATABLE_ABILITIES` deletion breaks an unknown consumer. | Verification confirmed no in-repo readers besides documentation. Mitigation: grep once more before deletion. If discovered, swap to `abilities_with_kind_tag(StrategicKind.ENERGY_DRAINING)`. |
| Shim shape changes break callers. | Keep `find_metadata`, `is_known_effect_ability`, `all_owner_aware_scopes` signatures stable. Internal storage moves; public API does not. |
| `ShieldProjection` aggregation drift. | Tag it `COMBAT_FLAT_BONUS` (not `COMBAT_MODIFIER`); no `EffectFacet` or one explicitly excluded from `aggregate_multipliers`. Verify with `tests/integration/test_combat_modifier_*` before Phase 5 exit. |
| `STABILIZERS` / `SUPERWEAPONS` migration scope-creeps. | Phase 6 leaves both tables in place; only contract tests added. Full collapse is a follow-up. |
| **TD-03 not yet landed when execution begins.** | Project is hard-blocked on PROJ-424. Phase 4 explicitly re-confirms `CommandSpec.action_ability_name` API shape per TD-07 Execution Precondition 2 before coding. |
