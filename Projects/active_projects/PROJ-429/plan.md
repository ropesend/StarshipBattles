# PROJ-429: Ability metadata unification (TD-07)

**Execution Protocol:** 03c-phase-aware-execution

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-429` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-429 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status

| Phase | Status | Checklist |
|-------|--------|-----------|
| 0. Scope-bounding read + design decision | Complete | [phase_0_checklist.md](phase_0_checklist.md) |
| 1. Establish the unified `AbilityMetadataRegistry` skeleton | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Migrate `design_role` classification | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Migrate `planet_energy_engine` (delete dead `_ACTIVATABLE_ABILITIES`) | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Migrate `action_time_resolver` (TD-03 coupling) | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Migrate `combat_modifier_collector` and `spec_compiler` | Complete | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Migrate `build_queue_source`; stabilizer/superweapon parity contracts | Complete | [phase_6_checklist.md](phase_6_checklist.md) |
| 7. Documentation update and final validation | Complete | [phase_7_checklist.md](phase_7_checklist.md) |
| 8. Codex consult follow-ups (post-Phase 7) | Complete | [phase_8_checklist.md](phase_8_checklist.md) |

## Current State

**Last Updated:** 2026-05-17
**Active Phase:** Complete
**Last Action:** Phase 8 complete — Codex consult follow-ups landed: (1) reverse-direction parity tests for STABILIZER/SUPERWEAPON kind tags, (2) `planet_dto.shield_active` migrated to PLANETARY_SHIELD registry tag, (3) `action_time_resolver` fails fast on unregistered energy abilities (literal `'activation_time'`/`'deactivation_time'` fallback removed), (4) UI `_ACTIVATABLE_ABILITIES` migration spawned as PROJ-435 because the UI map mixes registered + unregistered abilities and carries UI-specific display labels that don't fit the registry shape. Three commits + one scaffold commit.
**Next Action:** Ready for final audit.
**Blockers:** None.

## Overview

Strategy-layer ability metadata is currently spread across at least eleven hardcoded ability-name sets in `game/strategy/` (one of which — `_ACTIVATABLE_ABILITIES` — is dead code). This project introduces a single **`AbilityMetadataRegistry`** as the authoritative source of truth for non-mechanical, strategy-layer facts about every ability (effect facet, role classification, energy/activation, action-time fields, strategic kind), and migrates each consumer to read from it. Mechanical behavior (stat contribution, simulation effect) stays with the ability implementation under `game/simulation/components/abilities/`.

## Goals

- One registry answers every "is ability X a Y?" question currently scattered across `design_role.py`, `planet_energy_engine.py`, `action_time_resolver.py`, `combat_modifier_collector.py`, `spec_compiler.py`, `build_queue_source.py`, `stabilizer_registry.py`, and `superweapon_registry.py`.
- The seven role-classification frozensets in `design_role.py` are deleted in favor of `abilities_with_role_tag(...)` queries.
- Dead constant `_ACTIVATABLE_ABILITIES` is removed (root-cause fix per CLAUDE.md rule 3).
- The combat-modifier name set has one answer rather than three (`spec_compiler.py:827`, `combat_modifier_collector.py:96,127`, and the existing three multipliers in `EFFECT_ABILITY_METADATA`).
- `ShieldProjection` — currently strategy-layer-only and unmodeled in any metadata registry — is represented in the new registry.
- Contract tests pin `STABILIZERS`, `SUPERWEAPONS`, and `CommandSpec.action_ability_name` to the unified registry; adding a command/stabilizer/superweapon without a matching metadata entry fails CI.
- `effect_ability_metadata.py` keeps its public helper API (`find_metadata`, `is_known_effect_ability`, `all_owner_aware_scopes`) as a stable shim.

## Scope

**In:**
- New module [`game/strategy/services/ability_metadata.py`](../../../game/strategy/services/ability_metadata.py) (registry + `RoleTag`, `StrategicKind`, `EnergyFacet`, `EffectFacet`, `AbilityMetadata`).
- Conversion of `effect_ability_metadata.py` into a thin shim that reads from the unified registry while preserving its public helper signatures.
- Migration of every strategy-layer consumer enumerated in TD-07's Concrete File Touch Plan.
- Deletion of dead `_ACTIVATABLE_ABILITIES`.
- Contract tests for stabilizer/superweapon/command parity.
- Documentation update in `docs/systems/strategy_layer.md`.

**Out:**
- Editing simulation-layer ability classes under `game/simulation/components/abilities/`.
- Collapsing `StabilizerSpec` / `SuperweaponSpec` into the unified registry (only parity contract tests; full collapse is a follow-up).
- Broadening to "all ability literals everywhere in the repo." This plan is for the strategy-layer consumers only.
- Modifying `data/` content files.

## Dependencies

**HARD predecessor: PROJ-424 (TD-03 order metadata convergence).** This project must not start — not even Phase 0 — until PROJ-424 completes. `ActionTimeResolver` already derives `ORDER_TO_ABILITY_MAP` from `CommandRegistry`, but PROJ-424's `OrderMetadataView` collapses one of the four metadata surfaces this project's Phase 4 has to coexist with. Starting TD-07 before TD-03 lands would force this project to either (a) re-implement the view layer mid-flight when TD-03 reshapes the `CommandRegistry` API, or (b) leave Phase 4's `ORDER_TO_TIME_FIELD` collapse half-done. Neither is acceptable.

**Shape rationale.** This project builds a **primary registry**, not a view. That intentionally differs from PROJ-424's `OrderMetadataView`, which wraps the pre-existing `CommandRegistry`. The difference is structural, not stylistic:

- Order metadata already has an authoritative source (`CommandRegistry`), so PROJ-424 only needs to expose it cycle-safely → **view**.
- Ability metadata has no upstream primary store, so PROJ-429 must **be** the store → **registry**.

Both projects converge on the same end-state property — one cycle-safe, lazily resolved access path per metadata domain — through the mechanism appropriate to each domain's existing topology. This rationale is documented in the source plan's Goal / End State section.

**Soft predecessors:** none.

**Related (back-link):** [PROJ-424 plan.md](../PROJ-424/plan.md).

## Key Files

| Component | File Path |
|-----------|-----------|
| **New** — unified registry | [`game/strategy/services/ability_metadata.py`](../../../game/strategy/services/ability_metadata.py) |
| Effect-aggregation metadata (becomes shim) | [`game/strategy/services/effect_ability_metadata.py`](../../../game/strategy/services/effect_ability_metadata.py) |
| Role classification (seven frozensets to delete) | [`game/strategy/data/design_role.py`](../../../game/strategy/data/design_role.py) |
| Planet energy engine (delete dead `_ACTIVATABLE_ABILITIES`, replace `"PlanetaryShield"` literal) | [`game/strategy/engine/planet_energy_engine.py`](../../../game/strategy/engine/planet_energy_engine.py) |
| Action-time resolver (TD-03 coupling — Phase 4) | [`game/strategy/services/action_time_resolver.py`](../../../game/strategy/services/action_time_resolver.py) |
| Combat modifier collector | [`game/strategy/services/combat_modifier_collector.py`](../../../game/strategy/services/combat_modifier_collector.py) |
| Spec compiler (combat-ability name set at :827) | [`game/strategy/combat/spec_compiler.py`](../../../game/strategy/combat/spec_compiler.py) |
| Build queue source (`"BuildRateBooster"` literal at :114) | [`game/strategy/data/build_queue_source.py`](../../../game/strategy/data/build_queue_source.py) |
| Stabilizer registry (parity contract) | [`game/strategy/services/stabilizer_registry.py`](../../../game/strategy/services/stabilizer_registry.py) |
| Superweapon registry (parity contract) | [`game/strategy/services/superweapon_registry.py`](../../../game/strategy/services/superweapon_registry.py) |
| Command spec (read for contract test, no edits) | [`game/strategy/engine/commands/registry.py`](../../../game/strategy/engine/commands/registry.py) |

## Phases

| Phase | Objective |
|-------|-----------|
| 0 | Re-read architecture/patterns/conventions and `docs/systems/strategy_layer.md`. Confirm `docs/guides/adding_abilities.md` successor status. Decide: extend `EffectAbilityMetadata` in place vs. introduce `AbilityMetadata` superset (recommended: superset). |
| 1 | Implement `game/strategy/services/ability_metadata.py` (registry + facets + tags). Add parity test asserting every currently-hardcoded name has at least one tag. Convert `effect_ability_metadata.py` to a thin shim preserving its public API. |
| 2 | Replace the seven role-classification frozensets in `design_role.py` with `abilities_with_role_tag(...)` calls. Delete the constants. Add new-ability classification test (`FooLaunchAbility` tagged CARRIER classifies as CARRIER without touching `design_role.py`). |
| 3 | Delete `_ACTIVATABLE_ABILITIES` (dead code, verified). Decide on `_is_ability_active` / `get_activatable_ability_info` (keep behind unified facet vs. delete). Replace literal `"PlanetaryShield"` at line 48 with a tag-driven lookup. |
| 4 | (**TD-03 coupling**) Drive `_extract_time`'s activation/deactivation field selection from the unified `EnergyFacet`. Delete the empty `ORDER_TO_TIME_FIELD`. Add contract test: every `CommandSpec.action_ability_name` exists in the unified registry. |
| 5 | Replace `combat_ability_names = {...}` at `spec_compiler.py:827` with a registry query. Replace the two iterated tuples + literal `"ShieldProjection"` in `combat_modifier_collector.py`. Add `ShieldProjection` to the registry with a `COMBAT_FLAT_BONUS`-style tag (not `COMBAT_MODIFIER`). |
| 6 | Replace literal `"BuildRateBooster"` at `build_queue_source.py:114` with a tag query. Add contract tests: every `STABILIZERS[*].ability_name` and `SUPERWEAPONS[*].ability_name` has the matching `kind_tag`. Do not collapse the spec tables themselves. |
| 7 | Update `docs/systems/strategy_layer.md` to make `AbilityMetadataRegistry` the canonical source of truth. Update `docs/guides/adding_abilities.md` (only if it has a live successor). Run the full sharded suite. Mark TD-07 source plan COMPLETED. |
| 8 | **Codex consult follow-ups** (post-Phase 7). Reverse-direction parity tests for STABILIZER / SUPERWEAPON. Migrate `planet_dto.shield_active` to PLANETARY_SHIELD tag. Fail-fast in `action_time_resolver` for unregistered energy abilities (delete literal `'activation_time'` / `'deactivation_time'` fallback). Decide UI `_ACTIVATABLE_ABILITIES` migration (executed inline OR spun off as PROJ-435). |

Phase-by-phase dependency edges (intra-project): `0 → 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8`. No parallelism within the project; this is a sequential consumer migration.

### Phase 8 — Codex consult follow-ups

The original eight-phase TD-07 plan ended at Phase 7 (docs + final sharded validation). After Phase 7 a Codex consult on the unified-registry migration surfaced four follow-up items not in the original plan; Phase 8 lands them so the registry-driven design is closed end-to-end before final audit:

1. **Two-way parity** (test-only). The existing contract proves every spec-table `ability_name` is registry-tagged, but not the reverse direction (every kind-tagged ability has a matching spec row). The reverse direction is a regression guard against "tag drifts after spec row removed". Implemented in `test_ability_metadata_contracts.py`. STELLERATE_STAR's `ability_name=None` row is documented in the test as an exception (`DestroyStar` is registry-tagged but has no spec row).
2. **`planet_dto.py:107` literal**. `shield_active` read `active_abilities.get('PlanetaryShield', False)` directly. Migrated to iterate `abilities_with_kind_tag(StrategicKind.PLANETARY_SHIELD)`, mirroring Phase 3's `planet_energy_engine.get_shield_info` pattern.
3. **`action_time_resolver._activate_time_field` fallback**. The historical literals `'activation_time'` / `'deactivation_time'` were the fallback for unregistered energy abilities. The fallback was safe today only because `EnergyFacet`'s default field names match the literals — drift would silently degrade. Replaced with `ValueError` raises with actionable messages. Two TDD test cases (unregistered + registered-but-no-EnergyFacet, plus the deactivate mirror). Three pre-existing test_planet_action_engine tests that used synthetic `AbilityA`/`AbilityB` names were updated to use real registered stabilizers.
4. **UI `_ACTIVATABLE_ABILITIES` in `stat_rows_dynamic.py:381-463`**. The UI map mixes registered (4) + unregistered (2) abilities and carries display labels with no current home in the registry; the closest kind tag has 4 of 6 members. Not a mechanical inline migration — spun off as PROJ-435 with a populated scaffold (plan, design, decisions, phase 1 checklist, phase_state.json).

## Related Documents

- [design.md](design.md) — `AbilityMetadataRegistry` schema, `EffectFacet` / `RoleTag` / `StrategicKind` / `EnergyFacet` taxonomy, per-consumer migration order.
- [decisions.md](decisions.md) — initialized decision log (primary registry vs. view, shim retention, one-consumer-per-phase).
- [manifest.md](manifest.md) — full touched-file list per phase.
- [findings_ledger.md](findings_ledger.md) — coordinator-owned review-finding ledger.
- **Source plan:** [TD-07 plan](../../../Reviews/results/2026-05-16_strategy-layer-tech-debt-review/Verified%20Problem%20Remediation%20Plans/TD-07_ability_metadata_unification.md)
- **Execution order:** [EXECUTION_ORDER.md](../../../Reviews/results/2026-05-16_strategy-layer-tech-debt-review/Verified%20Problem%20Remediation%20Plans/EXECUTION_ORDER.md) (this project is #8 of 10).
- **Hard predecessor:** [PROJ-424 plan.md](../PROJ-424/plan.md) (TD-03 order metadata convergence).

## Verification

- [x] PROJ-424 (TD-03) is complete and merged to main before any phase of this project starts.
- [x] All phase checklists complete (Phases 0 through 7).
- [x] No hardcoded ability-name set remains anywhere in `game/strategy/` outside the unified registry. (Sanity grep: the regex from TD-07's Execution Preconditions returns no matches outside `ability_metadata.py`, the simulation layer, and `data/`. Remaining hits in `game/strategy/` are docstring/comment references to deleted constants, not live definitions.)
- [x] `_ACTIVATABLE_ABILITIES` is gone; no module references it (in `game/strategy/`; UI-layer constant in `stat_rows_dynamic.py` is a separate concern out of scope).
- [x] `design_role.py` defines none of `_WEAPON_ABILITIES`, `_SEEKER_ABILITIES`, `_BEAM_PROJECTILE_ABILITIES`, `_SENSOR_ABILITIES`, `_SUPPORT_ABILITIES`, `_CARRIER_ABILITIES`, `_COMMAND_ABILITIES`.
- [x] `combat_modifier_collector.py` (COMBAT_FLAT_BONUS) and `strategy_modifier_stack_builder.py` (COMBAT_MODIFIER) derive their combat-ability sets from the unified registry (no duplicated literals across files). Per-accumulator dispatch within the collector is retained per decisions.md row 11.
- [x] `ShieldProjection` is represented in the unified registry with `StrategicKind.COMBAT_FLAT_BONUS`, distinct from the multiplier-style combat modifiers.
- [x] `effect_ability_metadata.py` still exports `find_metadata`, `is_known_effect_ability`, `all_owner_aware_scopes` with unchanged signatures.
- [x] Contract test: every `CommandSpec.action_ability_name` exists in the unified registry (`test_every_command_action_ability_name_exists_in_registry`).
- [x] Contract test: every `STABILIZERS[*].ability_name` and `SUPERWEAPONS[*].ability_name` has the matching `kind_tag`.
- [x] `python Tools/test_sharded/test_sharded.py` is green — **21079 / 21079 passed, 154s wall time**.
- [x] `docs/systems/strategy_layer.md` describes the unified registry as the strategy-facing source of truth (new "Ability Metadata Registry (PROJ-429 / TD-07)" section).
- [ ] User verified.
