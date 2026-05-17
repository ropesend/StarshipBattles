# TD-07: Strategy Ability Metadata Is Only Partially Registry-Driven

**Status:** VERIFIED
**Verified:** 2026-05-16
**Source review:** `Reviews/results/2026-05-16_strategy-layer-tech-debt-review/report.md` (TD-07, lines 208-230)

---

## Verification Findings

Every claimed hardcoded ability-name set was located, and several additional
sets — not called out in the report — were discovered during the cross-check
sweep. The good registry (`EffectAbilityMetadata`) only covers the
"strategic effect" axis; design-role classification, energy-drain
classification, action-time mapping, combat-modifier filtering, and the
stabilizer/superweapon tables all live in their own one-off frozensets,
dicts, or tuples.

### Hardcoded ability-name sets confirmed at the report-cited locations

| Set | File:Line | Shape | Purpose |
|-----|-----------|-------|---------|
| `_WEAPON_ABILITIES` | `game/strategy/data/design_role.py:56` | `set[str]` | "Does this design have weapons?" |
| `_SEEKER_ABILITIES` | `game/strategy/data/design_role.py:57` | `set[str]` | Seeker-only weapon detection |
| `_BEAM_PROJECTILE_ABILITIES` | `game/strategy/data/design_role.py:58` | `set[str]` | Non-missile weapon detection |
| `_SENSOR_ABILITIES` | `game/strategy/data/design_role.py:59` | `set[str]` | Sensor/ECM-only detection |
| `_SUPPORT_ABILITIES` | `game/strategy/data/design_role.py:60` | `set[str]` | Repair/shipyard/resource detection |
| `_CARRIER_ABILITIES` | `game/strategy/data/design_role.py:66-69` | `set[str]` | Fighter/satellite-launch detection |
| `_COMMAND_ABILITIES` | `game/strategy/data/design_role.py:70` | `set[str]` | Data-link detection (+ inline `"CommandAndControl"` literal at :105) |
| `_ACTIVATABLE_ABILITIES` | `game/strategy/engine/planet_energy_engine.py:80-89` | `list[str]` | "Activatable energy-draining abilities" |
| `ORDER_TO_ABILITY_MAP` | `game/strategy/services/action_time_resolver.py:50` | `dict[OrderType, str]` | Order → ability-name for action-time lookup |
| `ORDER_TO_TIME_FIELD` | `game/strategy/services/action_time_resolver.py:54-55` | `dict[OrderType, str]` (currently empty) | Order → non-default time-field name |
| Inline activate/deactivate field choice | `game/strategy/services/action_time_resolver.py:89-93` | `if/else` literal | `'activation_time' if … else 'deactivation_time'` |

### Additional hardcoded ability-name sets found during cross-check

| Set | File:Line | Shape | Purpose | Reason it belongs in TD-07 |
|-----|-----------|-------|---------|-------------------------|
| `combat_ability_names` | `game/strategy/combat/spec_compiler.py:827` | inline `set[str]` | Filter sector effects to the three combat modifiers | Same "is this ability a combat modifier?" question; same three names as `EFFECT_ABILITY_METADATA` lines 132-134 |
| Iterated tuple `("ShieldModifier","DamageModifier")` | `combat_modifier_collector.py:96, 127` | inline tuple | Loop over multiplier-style fleet abilities | Same names; same axis (combat modifier) |
| Literal `"ShieldProjection"` | `combat_modifier_collector.py:109, 113` | string literal | Separate flat-bonus accumulation | Not in `EFFECT_ABILITY_METADATA` at all (only the three multipliers are) — ShieldProjection is strategy-layer-only and currently unmodeled in metadata |
| `STABILIZERS` table | `game/strategy/services/stabilizer_registry.py:54-70` | `tuple[StabilizerSpec, ...]` | Stabilizer ability → blocked order types + scopes | Already declarative, but ability-name lives in a separate registry from the effect/role/energy ones |
| `SUPERWEAPONS` table | `game/strategy/services/superweapon_registry.py:70-111` | `tuple[SuperweaponSpec, ...]` | Order type → ability-name for superweapon dispatch | Same — separate declarative table, same ability vocabulary |
| Hardcoded `"PlanetaryShield"` | `game/strategy/engine/planet_energy_engine.py:48` | string literal in `get_shield_info` | Shield-specific extraction | Same activatable-energy-draining axis as `_ACTIVATABLE_ABILITIES` |
| Hardcoded `"BuildRateBooster"` scope sweep | `game/strategy/data/build_queue_source.py:114` | inline scope loop `["planet","sector","system","empire"]` | Strategic build-rate booster aggregation | The ability is already in `EFFECT_ABILITY_METADATA` (line 123) but the scope-sweep behavior is duplicated |

### Dead code surfaced during verification

`_ACTIVATABLE_ABILITIES` in `planet_energy_engine.py:80-89` is defined but
**never referenced** in the module (grep confirms no in-file reads; no
external imports apart from documentation calling it out as not the
discovery surface). `_compute_activation_drain` (lines 270-282) iterates
`facility.component_states` and reads each entry's
`ComponentActivationState.is_draining_energy` — the list of names is
inert. The user-facing doc at `docs/guides/adding_abilities.md:416`
already advises "do not treat `_ACTIVATABLE_ABILITIES` as the discovery
surface."

This is a leftover from the pre-`ComponentActivationState` discovery path
and should be deleted as part of this work (root-cause fix per CLAUDE.md
rule 3).

### The good registry: `EffectAbilityMetadata`

`game/strategy/services/effect_ability_metadata.py:110-141` defines
`EFFECT_ABILITY_METADATA` — 11 entries spanning multiplier-style
stabilizers, resource boosters, combat modifiers, and rate-style
environmental hazards. Each entry answers four questions:

- display name (and grouping rule when `None`)
- kind (`'rate'` vs `'multiplier'`)
- is-activatable hint
- `value_field_primary` / `value_field_fallback` for value extraction

It does **not** answer:

- design-role classification (`_CARRIER_ABILITIES` etc.)
- energy-draining classification (`_ACTIVATABLE_ABILITIES`)
- order-type → ability-name (lives in `CommandRegistry.action_ability_name`)
- action-time-field name (`activation_time` / `deactivation_time` / `action_time`)
- which abilities are *strategic-superweapon* abilities
- which abilities are *stabilizer* abilities
- which abilities are *combat modifiers* (it lists three, but
  `spec_compiler.py:827` re-encodes the same three in a literal set)
- which abilities are *strategic-fleet combat boosters/suppressors*
  (`ShieldProjection` is missing entirely from the metadata registry)

The architecture is genuinely inconsistent: one ability family
(`ShieldModifier`) is currently authored across at least four files
(`effect_ability_metadata.py`, `combat_modifier_collector.py`,
`spec_compiler.py`, `system_effects_collector.py` consumer chains) and
the cross-file equality of those mentions is enforced by tests, not by a
single source of truth.

### Verdict

**VERIFIED** — and broader than the report suggested. The report
identified four hardcoded surfaces; the verification sweep located **at
least eleven** distinct hardcoded ability-name sets in `game/strategy/`,
of which one is dead code. The unification opportunity is real and the
metadata vocabulary needed is the union of the questions enumerated by
the report plus the combat-modifier / superweapon / stabilizer /
shield-projection axes surfaced above.

---

## Affected Code

### Existing registries (to absorb / coordinate with)

- `game/strategy/services/effect_ability_metadata.py` — current
  effect-aggregation metadata. Will become a *facet* of the unified
  registry, or be extended in-place to cover the new axes.
- `game/strategy/services/stabilizer_registry.py` — declarative table
  keyed by ability_name. Specs add scope/blocks vocabulary.
- `game/strategy/services/superweapon_registry.py` — declarative table
  keyed by `OrderType` but referencing `ability_name`. Specs add
  target_type/consume_ship/event_type vocabulary.
- `game/strategy/engine/commands/registry.py` — `CommandSpec` already
  carries `action_ability_name`. `ActionTimeResolver` already derives
  `ORDER_TO_ABILITY_MAP` from this (`action_time_resolver.py:39-50`).
  Couples this plan to TD-03.

### Consumers of the hardcoded sets

- `game/strategy/data/design_role.py:77-129` — `classify_design_role`
  uses the six role-classification frozensets and `_LIGHT_SHIP_MASS` /
  `_HEAVY_SHIP_MASS` thresholds.
- `game/strategy/data/design_role.py:132-167` —
  `classify_from_design_data` walks design layers + component registry,
  then calls `classify_design_role`. (No name-set reads itself but is
  the only public entry point in some callers.)
- `game/strategy/engine/planet_energy_engine.py:80-100` — currently
  dead `_ACTIVATABLE_ABILITIES`; the live drain path at lines 270-282
  is already metadata-free (uses `ComponentActivationState.is_draining_energy`).
- `game/strategy/services/action_time_resolver.py:50-119` — derives
  `ORDER_TO_ABILITY_MAP` from `CommandRegistry`; `ORDER_TO_TIME_FIELD`
  is empty; literal `activation_time`/`deactivation_time` at lines 89-93
  for the toggle path.
- `game/strategy/combat/spec_compiler.py:827` — `combat_ability_names`
  inline set.
- `game/strategy/services/combat_modifier_collector.py:96-127` —
  two iterated lists of ability tuples + literal `"ShieldProjection"`.
- `game/strategy/engine/planet_energy_engine.py:48` — literal
  `"PlanetaryShield"` in `get_shield_info`.
- `game/strategy/data/build_queue_source.py:114` — literal
  `"BuildRateBooster"` + inline scope sweep.

### Tests that will move with the implementation

- `tests/unit/strategy/data/test_design_role.py` — classification cases
  per role; will need to migrate to the unified registry's role-hint
  predicate.
- `tests/unit/strategy/services/test_effect_ability_metadata.py` — keep
  green; extend with new facets.
- `tests/unit/strategy/services/test_effect_ability_display.py` — keep
  green.
- `tests/unit/strategy/engine/test_planet_energy_engine.py` — `_ACTIVATABLE_ABILITIES`
  is imported indirectly via the module; deleting it must not break
  imports. Check `from game.strategy.engine.planet_energy_engine import (
  PlanetEnergyEngine, _is_ability_active, get_activatable_ability_info,
  get_shield_info,)` at `test_planet_energy_engine.py:5`.
- `tests/unit/strategy/services/test_action_time_resolver.py` — verify
  derived `ORDER_TO_ABILITY_MAP` matches CommandRegistry once unification
  lands.
- `tests/unit/strategy/services/test_planet_query_service.py:59-65` —
  `is_ability_active` characterization.

---

## Goal / End State

One **AbilityMetadataRegistry** that is the single source of truth for
all *strategy-layer* facts about an ability. The new registry should be
the only place a new ability needs to be declared for *non-mechanical*
behavior; mechanical behavior (stat contribution, simulation effect)
continues to live with the ability implementation in
`game/simulation/components/abilities/`.

**Shape rationale (cross-plan note):** This plan introduces a *registry*
(primary store), not a *view* over an existing one. That intentionally
differs from TD-03's `OrderMetadataView`, which is a lazy live reader
over the pre-existing `CommandRegistry`. The difference is structural,
not stylistic: order metadata already has an authoritative source
(`CommandRegistry`) so TD-03 only needs to expose it cycle-safely;
ability metadata has no upstream primary store, so TD-07 must *be* the
store. Both plans converge on the same end-state property — one cycle-
safe, lazily resolved access path per metadata domain — through the
mechanism appropriate to each domain's existing topology.

### Schema (target)

```python
@dataclass(frozen=True)
class AbilityMetadata:
    # Identity
    name: str                              # e.g. "ShieldModifier"

    # Effect / display facet (existing EffectAbilityMetadata)
    effect: Optional[EffectFacet]          # None if not an aggregated effect

    # Design-role classification facet (NEW)
    role_tags: frozenset[RoleTag]          # {WEAPON, SEEKER, SENSOR,
                                           #  SUPPORT, CARRIER, COMMAND,
                                           #  BEAM_PROJECTILE, ...}

    # Energy / activation facet (NEW)
    energy: Optional[EnergyFacet]          # is_activatable, drains_energy,
                                           #   activation_time_field,
                                           #   deactivation_time_field

    # Action-time facet (NEW)
    action_time_field: str                 # default 'action_time'

    # Strategic kind tag (NEW)
    kind_tags: frozenset[StrategicKind]    # {COMBAT_MODIFIER, STABILIZER,
                                           #  SUPERWEAPON, ENVIRONMENTAL,
                                           #  RESOURCE_BOOSTER, ...}
```

`StabilizerSpec` / `SuperweaponSpec` continue to exist as ability-name
keyed views of the unified registry — they own the *operation-specific*
data (`scopes`, `blocks`, `target_type`, `consume_ship`, `event_type`)
which is not generic ability metadata. The unified registry only owns
the *categorization* (`kind_tags`).

### Public API (target)

```python
get_ability_metadata(name) -> AbilityMetadata | None
ability_has_role_tag(name, tag) -> bool
ability_has_kind_tag(name, tag) -> bool
abilities_with_role_tag(tag) -> frozenset[str]
abilities_with_kind_tag(tag) -> frozenset[str]
ability_action_time_field(name) -> str
ability_drains_energy(name) -> bool
```

### What stops being possible

- Adding a new carrier-class launch ability without updating any
  classification table (it is just a new entry with `CARRIER` in
  `role_tags`).
- Adding a new energy-draining facility ability without touching
  `_ACTIVATABLE_ABILITIES` (it's deleted; the facet drives drain
  detection, but the runtime path keeps using `ComponentActivationState`).
- Adding a new combat-modifier ability without re-encoding its name
  in `spec_compiler.py:827` and `combat_modifier_collector.py:96`.
- Name-keyed `if ability_name == 'EnvironmentalDamage'` branches in
  `effect_ability_display.py:88, 152` keep working but become
  metadata-readable (`metadata.effect.legacy_fallback_label`).

---

## Execution Preconditions

Before implementation starts:

1. Re-run the exact inventory grep used by verification so the executor is
   working from current code rather than this document's snapshot:
   ```text
   rg -n "_WEAPON_ABILITIES|_SEEKER_ABILITIES|_BEAM_PROJECTILE_ABILITIES|_SENSOR_ABILITIES|_SUPPORT_ABILITIES|_CARRIER_ABILITIES|_COMMAND_ABILITIES|_ACTIVATABLE_ABILITIES|ORDER_TO_ABILITY_MAP|ORDER_TO_TIME_FIELD|ShieldProjection|BuildRateBooster|ShieldModifier|DamageModifier|ThrustModifier" game/strategy tests/unit/strategy
   ```
2. Confirm `game/strategy/engine/commands/registry.py` still exposes
   `CommandSpec.action_ability_name` and that
   `game/strategy/services/action_time_resolver.py` still derives
   `ORDER_TO_ABILITY_MAP` from it. If TD-03 has already changed that API,
   update this plan before coding; do not guess the new source mid-flight.
3. Capture the current metadata baseline before any edit:
   ```text
   pytest tests/unit/strategy/services/test_effect_ability_metadata.py tests/unit/strategy/services/test_effect_ability_display.py -q
   ```
4. Do not start by editing simulation-layer ability classes. This plan is
   strategy metadata consolidation only.

## Concrete File Touch Plan

Use this as the authoritative touch list. Do not invent extra modules unless a
failing test proves they are necessary.

### Phase 1

- New file: `game/strategy/services/ability_metadata.py`
- Existing file: `game/strategy/services/effect_ability_metadata.py`
- New tests:
  - `tests/unit/strategy/services/test_ability_metadata_registry.py`
  - `tests/unit/strategy/services/test_ability_metadata_contracts.py`

### Phase 2

- `game/strategy/data/design_role.py`
- `tests/unit/strategy/data/test_design_role.py`

### Phase 3

- `game/strategy/engine/planet_energy_engine.py`
- `tests/unit/strategy/engine/test_planet_energy_engine.py`
- `tests/unit/strategy/services/test_planet_query_service.py`

### Phase 4

- `game/strategy/services/action_time_resolver.py`
- `tests/unit/strategy/services/test_action_time_resolver.py`
- `tests/unit/strategy/services/test_ability_metadata_contracts.py`

### Phase 5

- `game/strategy/combat/spec_compiler.py`
- `game/strategy/services/combat_modifier_collector.py`
- `tests/unit/strategy/services/test_combat_modifier_collector.py`
- Existing combat-modifier integration tests covering `ShieldModifier`,
  `DamageModifier`, `ThrustModifier`, and `ShieldProjection`

### Phase 6

- `game/strategy/data/build_queue_source.py`
- `game/strategy/services/stabilizer_registry.py`
- `game/strategy/services/superweapon_registry.py`
- `tests/unit/strategy/services/test_ability_metadata_contracts.py`

### Phase 7

- `docs/systems/strategy_layer.md`
- The live "adding abilities" guide only if it is still the supported project
  guide. Do not update an archived or deletion-bound doc just because a stale
  reference exists.

## Weak-LLM Guardrails

- Do not import concrete ability classes into the unified registry. The registry
  is pure strategy metadata keyed by strings.
- Do not collapse `StabilizerSpec` or `SuperweaponSpec` into the new registry in
  this plan. Only add contract tests proving their `ability_name` fields are
  tagged correctly.
- Do not delete `find_metadata`, `is_known_effect_ability`, or
  `all_owner_aware_scopes` in the same change. Existing callers keep that API.
- Do not broaden scope to "fix all ability literals everywhere in the repo."
  This plan is only for the strategy-layer consumers enumerated here.
- If `ShieldProjection` needs separate handling from multiplier-style combat
  modifiers, model that with a distinct tag. Do not force it into the same
  aggregation path as `ShieldModifier`.

## Per-Phase Success Criteria

- Phase 1 is done only when every currently-known hardcoded name maps to
  metadata or an explicitly-documented exemption.
- Phase 2 is done only when `design_role.py` contains no role-classification
  ability-name sets.
- Phase 3 is done only when `_ACTIVATABLE_ABILITIES` is gone and the remaining
  public helpers still satisfy existing tests.
- Phase 4 is done only when no local `ORDER_TO_TIME_FIELD` mapping remains.
- Phase 5 is done only when `spec_compiler.py` and
  `combat_modifier_collector.py` derive their combat-ability sets from shared
  metadata rather than duplicated literals.
- Phase 6 is done only when stabilizer and superweapon contract tests prove
  metadata parity.
- Phase 7 is done only after the focused tests are green and the full shard
  suite passes.

## Remediation Plan

Phased, strict TDD. Each phase migrates **one consumer at a time** so
intermediate states are green. Test infra: shard runner is the
canonical gate; each phase adds focused tests first and re-runs the
relevant slice before declaring done.

### Phase 0 — Scope-bounding read

- Re-read `docs/01_ARCHITECTURE.md`, `docs/02_PATTERNS.md`,
  `docs/03_CONVENTIONS.md`, `docs/systems/strategy_layer.md` for
  ability-related conventions.
- Confirm `docs/guides/adding_abilities.md` (currently under
  `_marked_for_deletion_2026-05-29/`) does not have a live successor;
  if it does, update it in the same change set per CLAUDE.md rule 2.
- Decide whether to extend `EffectAbilityMetadata` in place or
  introduce a new `AbilityMetadata` superset. Recommended: introduce
  `AbilityMetadata` and make `EffectAbilityMetadata` a facet inside it
  (preserves the existing test surface; existing helpers
  `find_metadata` / `is_known_effect_ability` keep working).

### Phase 1 — Establish the unified registry skeleton

TDD order:

1. Write `tests/unit/strategy/services/test_ability_metadata_registry.py`:
   - `get_ability_metadata('ShieldModifier').effect is not None`
   - `get_ability_metadata('ShieldModifier').effect.kind == 'multiplier'`
   - `ability_has_role_tag('TacticalFighterLaunch', RoleTag.CARRIER)`
   - `ability_has_kind_tag('GeologicStabilizer', StrategicKind.STABILIZER)`
   - parity: every name currently in any hardcoded set has at least
     one matching tag.
2. Run; confirm fail (registry not introduced yet).
3. Implement `game/strategy/services/ability_metadata.py` (new module).
   - Define `RoleTag`, `StrategicKind`, `EnergyFacet`, `EffectFacet`,
     `AbilityMetadata`.
   - Build `_REGISTRY` from a single tuple literal mirroring the
     existing `EFFECT_ABILITY_METADATA` plus the additional axes.
   - Export the public API listed in "Goal / End State".
4. Keep `effect_ability_metadata.py` as a thin shim: `EFFECT_ABILITY_METADATA`,
   `find_metadata`, `is_known_effect_ability`, and `all_owner_aware_scopes`
   stay; `EffectAbilityMetadata` becomes a re-export of `EffectFacet`
   (or a `@dataclass` wrapper that reads from the unified registry).
5. Run the new test + existing
   `test_effect_ability_metadata.py` + `test_effect_ability_display.py`;
   all green.

Phase-1 exit criteria: unified registry exists, effect facet round-trips
to the old API, no consumer migrated yet.

### Phase 2 — Migrate `design_role` classification

TDD order:

1. Add tests to `test_design_role.py`:
   - Same role outcomes for every existing fixture *after*
     classification reads from the unified registry.
   - New test that a hypothetical `FooLaunchAbility` tagged
     `RoleTag.CARRIER` in the registry classifies as `CARRIER` without
     touching `design_role.py`.
2. Run; confirm new test fails.
3. Replace `_WEAPON_ABILITIES`, `_SEEKER_ABILITIES`,
   `_BEAM_PROJECTILE_ABILITIES`, `_SENSOR_ABILITIES`,
   `_SUPPORT_ABILITIES`, `_CARRIER_ABILITIES`, `_COMMAND_ABILITIES`
   with calls into `abilities_with_role_tag(...)`.
4. Add `RoleTag` entries to `AbilityMetadata` definitions for every
   ability currently in any of the seven sets.
5. Delete the seven module-level constants.
6. Run focused tests + the design-role registry tests; green.

Phase-2 exit criteria: `design_role.py` has no hardcoded ability names.

### Phase 3 — Migrate `planet_energy_engine`

TDD order:

1. Add a test to `test_planet_energy_engine.py` that imports
   `PlanetEnergyEngine` and asserts the module no longer exports
   `_ACTIVATABLE_ABILITIES` (or that it is empty / unused). Optional:
   simply delete the constant and rely on test_planet_energy_engine
   import-clean.
2. Remove `_ACTIVATABLE_ABILITIES` (dead code, confirmed in Verification).
3. Either:
   - delete `_is_ability_active` and `get_activatable_ability_info` if
     truly unused outside tests, OR
   - keep them but back them with the unified registry's
     `EnergyFacet`. Check `tests/unit/strategy/engine/test_planet_energy_engine.py:5-10`
     for usage — `_is_ability_active`, `get_activatable_ability_info`,
     `get_shield_info` are imported in tests, so the public surface
     must be preserved.
4. Replace the literal `"PlanetaryShield"` at line 48 with a query
   `abilities_with_kind_tag(StrategicKind.PLANETARY_SHIELD)` — or, if
   only one such ability is ever expected, keep the literal but mark
   `PlanetaryShield` with the appropriate tag for symmetry with the
   stabilizer family.
5. Run focused + cache tests; green.

Phase-3 exit criteria: no hardcoded activatable-ability list in
`planet_energy_engine.py`.

### Phase 4 — Migrate `action_time_resolver`

This phase has direct coupling to TD-03. The current
`ORDER_TO_ABILITY_MAP` already derives from `CommandRegistry`, so the
*ability name* axis is already declarative. What remains is:

- `ORDER_TO_TIME_FIELD` (currently empty)
- Literal `'activation_time'` / `'deactivation_time'` in the
  `ACTIVATE_ABILITY` / `DEACTIVATE_ABILITY` branch (lines 89-93)

TDD order:

1. Add test that asserts `ability_action_time_field('PlanetaryShield')`
   == `'activation_time'` (or whichever fields the ability declares).
2. Make `ActionTimeResolver._extract_time` read the time-field name
   from the unified registry rather than the resolver's local dict.
3. Delete the empty `ORDER_TO_TIME_FIELD`.
4. The inline activate/deactivate branch (lines 89-93) reads the
   ability's *activation* time-field for ACTIVATE and the
   *deactivation* time-field for DEACTIVATE — represent this in the
   `EnergyFacet` as `(activation_time_field, deactivation_time_field)`
   tuple, and have the branch resolve via the facet.
5. Run focused tests; green.

Phase-4 exit criteria: action-time field selection is metadata-driven;
no inline `'activation_time' if … else 'deactivation_time'` literal.

### Phase 5 — Migrate `combat_modifier_collector` and `spec_compiler`

TDD order:

1. Add tests:
   - `combat_modifier_collector` iterates exactly the abilities in
     `abilities_with_kind_tag(StrategicKind.COMBAT_MODIFIER)`.
   - `spec_compiler._entries_from_sector_effects` filters by the same
     set (no name divergence between the two callers).
2. Replace `combat_ability_names = {"ShieldModifier", "DamageModifier",
   "ThrustModifier"}` at `spec_compiler.py:827` with the registry
   query.
3. Replace the two literal tuples in
   `combat_modifier_collector.py:96, 127` and the literal
   `"ShieldProjection"` at lines 109, 113.
4. Add `ShieldProjection` to the unified registry as a
   `StrategicKind.COMBAT_FLAT_BONUS` ability (or whichever kind tag
   distinguishes flat-bonus accumulation from multiplier-aggregation).
5. Run integration tests under `tests/integration/` that touch combat
   modifier paths; green.

Phase-5 exit criteria: the "is this a combat modifier?" question has
one answer.

### Phase 6 — Migrate `build_queue_source` and confirm stabilizer/superweapon parity

TDD order:

1. Replace the literal `"BuildRateBooster"` at
   `build_queue_source.py:114` with a query for the appropriate
   `kind_tag`. (Optional: the scope sweep itself
   `["planet","sector","system","empire"]` could be the ability's own
   "supported scopes" facet — out of scope for this plan unless cheap.)
2. Audit `STABILIZERS` and `SUPERWEAPONS` tuples. Decide:
   - Keep both as-is, but assert via contract test that every
     ability_name in either table also has the corresponding
     `kind_tag` in the unified registry.
   - Or: migrate both to read ability_name → facet from the unified
     registry, and keep only the operation-specific columns (scopes,
     blocks, target_type, etc.) in the per-table specs.
3. Run focused tests; green.

Phase-6 exit criteria: no ability_name literal outside the unified
registry except (a) the unified registry itself, (b) ability
implementations under `game/simulation/components/abilities/`, and (c)
the data files under `data/`.

### Phase 7 — Documentation update and final validation

- Update `docs/systems/strategy_layer.md` to describe
  `AbilityMetadataRegistry` as the single strategy-facing source of
  truth for ability metadata. Remove or rewrite any prose that
  referenced `_ACTIVATABLE_ABILITIES`, the design-role frozensets, or
  `ORDER_TO_TIME_FIELD`.
- Update `docs/guides/adding_abilities.md` (or its live successor) to
  point at the new registry as the *first* edit when adding a new
  ability.
- Run `python Tools/test_sharded/test_sharded.py` end-to-end.
- Run `python -m radon cc game/strategy -s -a` to confirm no
  regression in average complexity.
- Update this plan's status header to **COMPLETED** with the date.

---

## Test Strategy

- **Unit tests per phase**, written before code, as enumerated above.
- **Parity test** in Phase 1 that walks every existing hardcoded set
  and asserts the new registry tags every name correctly. This test
  remains in place permanently as a regression guard.
- **Contract test** between the unified registry and the
  `CommandRegistry` (Phase 4): every `CommandSpec.action_ability_name`
  must exist in the unified registry. Pinned via
  `tests/unit/strategy/services/test_ability_metadata_contracts.py`
  (new).
- **Contract test** for `STABILIZERS` and `SUPERWEAPONS` (Phase 6):
  every `ability_name` in either tuple must have the corresponding
  `kind_tag`. Same file as above.
- **Integration tests** continue to exercise turn-loop and battle
  paths via the existing `tests/integration/test_fms_*` suites — these
  catch regressions in the activate/deactivate field selection,
  combat-modifier filtering, and superweapon dispatch.

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Cycle on import: `ability_metadata.py` references abilities defined in `game/simulation/components/abilities/` | Don't import from simulation. Names are strings; metadata is pure data. The registry is in `game/strategy/services/` and stays a leaf. |
| Duplication between `CommandSpec.action_ability_name` and the unified registry | Phase 4 contract test makes this an *enforced* relationship, not a duplication. Adding a command without an ability metadata entry fails CI. |
| `_ACTIVATABLE_ABILITIES` deletion breaks an unknown consumer | Verification confirmed no in-repo readers besides documentation. Mitigation: grep one more time before deletion; if discovered, replace with `abilities_with_kind_tag(StrategicKind.ENERGY_DRAINING)`. |
| `EffectAbilityMetadata` re-export shape changes break callers | Keep `find_metadata`, `is_known_effect_ability`, `all_owner_aware_scopes` signatures stable. Internal storage moves; public API does not. |
| `ShieldProjection` is currently not in the metadata registry — adding it might affect aggregation | Add only with `kind_tag=COMBAT_FLAT_BONUS` (or similar) and no `EffectFacet` (or a facet that is explicitly excluded from `aggregate_multipliers`). Verify by re-running `tests/integration/test_combat_modifier_*` (if present) before declaring Phase 5 done. |
| `STABILIZERS` / `SUPERWEAPONS` migration scope-creeps the plan | Phase 6 explicitly leaves both tables in place and only adds a contract test. Full collapse of the three registries is a follow-up. |

---

## Dependencies / Order

Verified execution guidance:

- Hard order: `TD-03` should land before this plan.
- Soft only: `TD-08` and `TD-09`.
- Independent at plan level: `TD-01`, `TD-02`, `TD-04`, `TD-05`, `TD-06`, `TD-10`.
- Execution-order impact: keep `TD-03 -> TD-07` as a hard edge and do not introduce any new hard edge from TD-07 to TD-08 or TD-09.
- Owned-only queue recommendation: `TD-09 -> TD-07`, with `TD-08` later only
  after its external blockers are stable, and `TD-10` last.

- **TD-03 (command/order metadata fragmentation)** — direct coupling.
  `ActionTimeResolver` already derives `ORDER_TO_ABILITY_MAP` from
  `CommandRegistry`, but the larger TD-03 work (single
  `OrderMetadataView`) overlaps with this plan's Phase 4. Recommended
  order: **TD-03 first** (it removes one of the four metadata surfaces
  that Phase 4 has to coexist with), then this plan. If TD-03 is not
  funded in the same arc, Phase 4 can still complete using the current
  `CommandRegistry` API; it just does not get to collapse
  `ORDER_TO_TIME_FIELD` quite as cleanly.
- **TD-08 (oversized facade)** — soft coupling. The report's
  "Residual Risks" section notes TD-03, TD-07, TD-08 are easier as
  one architecture arc. This plan does not block on TD-08; the
  unified registry has no facade surface.
- No coupling to TD-01, TD-02, TD-04, TD-05, TD-06, TD-09, TD-10.

---

## Acceptance Criteria

- [ ] Every hardcoded strategy-layer ability-name set retired by this plan has either been deleted or reduced to a clearly temporary shim with removal inside the same plan.
- [ ] `effect_ability_metadata.py` still exports the same public helper names until the final convergence phase.
- [ ] `ActionTimeResolver` reads action-time metadata from the unified registry or a live TD-03-derived view, not from a frozen import-time table.
- [ ] `design_role.py`, `planet_energy_engine.py`, and the combat-modifier consumers no longer own local hardcoded ability-name classification sets.
- [ ] `StabilizerSpec` and `SuperweaponSpec` still have contract parity with the unified registry after migration.
- [ ] Focused ability-metadata and affected consumer suites are green before the sharded run.
- [ ] `python Tools/test_sharded/test_sharded.py` is green.

---

## Estimated Scope

LLM-time estimates (per CLAUDE.md "Estimate in LLM time, not human time"):

| Phase | Estimate | Notes |
|-------|----------|-------|
| 0 | a few minutes | doc read + design decision |
| 1 | 10-20 minutes including test runs | new module + parity test + shim |
| 2 | 5-10 minutes | mechanical replacement of seven constants |
| 3 | a couple of minutes | mostly deleting dead code; one literal swap |
| 4 | 10-15 minutes | TD-03 coupling means careful test alignment |
| 5 | 10-20 minutes | three call sites + `ShieldProjection` modeling decision |
| 6 | 5-10 minutes | contract tests + one literal swap |
| 7 | 5-10 minutes | docs + full shard run |
| **Total** | **~1 hour of focused work + one full shard run** | The shard run itself is the dominant wall-clock cost. |

If TD-03 is bundled into the same arc, add ~20-30 minutes for the
shared design and one more shard run.
