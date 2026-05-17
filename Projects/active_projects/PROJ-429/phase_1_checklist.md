# Phase 1: Establish the unified `AbilityMetadataRegistry` skeleton

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-429 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** none (intra-project — Phase 0 is read-only scope-bounding; Phase 1 is the first code-producing phase)
**Review Mode:** standard

> **INTER-PROJECT BLOCKER:** This project is **hard-blocked on PROJ-424 (TD-03 order metadata convergence)**. Even though Phase 1's intra-project dependency list is `none`, Phase 1 must not start until PROJ-424 is `verified` and merged to main. PROJ-424's `OrderMetadataView` reshapes the `CommandRegistry` API that Phase 4 of this project depends on; starting Phase 1 before TD-03 lands risks landing a registry shape that has to be reshaped mid-project when TD-03 finishes. See [plan.md → Dependencies](plan.md#dependencies) and [decisions.md](decisions.md) row 8. The execution-order doc encodes the same edge: `TD-03 → TD-07`.

**Files (planned):**
- `game/strategy/services/ability_metadata.py` (NEW)
- `game/strategy/services/effect_ability_metadata.py` (modify — becomes a shim)
- `tests/unit/strategy/services/test_ability_metadata_registry.py` (NEW — failing tests added FIRST)
- `tests/unit/strategy/services/test_ability_metadata_contracts.py` (NEW — stub created here; extended in Phase 4 and Phase 6)

**Objective:** Stand up the unified registry as a leaf module in `game/strategy/services/`. Mirror every name currently in any hardcoded set so the parity test passes. Convert `effect_ability_metadata.py` to a thin shim preserving its public API. No consumer migrated in this phase.

---

## Reading

- [ ] Confirm PROJ-424 (TD-03) is merged to main.
- [ ] Read `Projects/active_projects/PROJ-429/plan.md`, `design.md`, `decisions.md` end-to-end.
- [ ] Read `game/strategy/services/effect_ability_metadata.py` lines 110-141 (current `EFFECT_ABILITY_METADATA` tuple).
- [ ] Read the existing role-classification frozensets at `game/strategy/data/design_role.py:56-70` (inventory the names).
- [ ] Read `game/strategy/services/stabilizer_registry.py:54-70` and `game/strategy/services/superweapon_registry.py:70-111` (inventory the ability_name fields).
- [ ] Read `game/strategy/services/combat_modifier_collector.py:96-127` (inventory the three multiplier names + `ShieldProjection`).

---

## Tasks

### Task 1.1: Add the failing parity + API tests (TDD red) [Medium]

**File:** `tests/unit/strategy/services/test_ability_metadata_registry.py`
**Tests:** `pytest tests/unit/strategy/services/test_ability_metadata_registry.py -q`

- [ ] Add import: `from game.strategy.services.ability_metadata import (...)` — this will fail at collection because the module does not yet exist. Confirm the failure mode is `ModuleNotFoundError`.
- [ ] Add `test_get_ability_metadata_returns_effect_facet_for_shield_modifier`:
      `assert get_ability_metadata('ShieldModifier').effect is not None`
      `assert get_ability_metadata('ShieldModifier').effect.kind == 'multiplier'`
- [ ] Add `test_ability_has_role_tag_carrier_for_known_carrier_ability` covering at least one name from `_CARRIER_ABILITIES`.
- [ ] Add `test_ability_has_kind_tag_stabilizer_for_geologic_stabilizer`:
      `assert ability_has_kind_tag('GeologicStabilizer', StrategicKind.STABILIZER)`
- [ ] Add **parity test** `test_every_hardcoded_name_has_at_least_one_tag` that imports the current hardcoded sets from `design_role.py`, `stabilizer_registry.py`, `superweapon_registry.py`, and `combat_modifier_collector.py`, plus the three combat multipliers and `ShieldProjection`, and asserts each name has at least one tag (role_tag or kind_tag) in the unified registry. **This test stays in place permanently as a regression guard.**

**Notes:** [Filled during implementation]

### Task 1.2: Implement `ability_metadata.py` (TDD green) [Complex]

**File:** `game/strategy/services/ability_metadata.py` (NEW)
**Tests:** `pytest tests/unit/strategy/services/test_ability_metadata_registry.py -q`

- [ ] Define `RoleTag` (Enum): `WEAPON`, `SEEKER`, `BEAM_PROJECTILE`, `SENSOR`, `SUPPORT`, `CARRIER`, `COMMAND`.
- [ ] Define `StrategicKind` (Enum): `COMBAT_MODIFIER`, `COMBAT_FLAT_BONUS`, `STABILIZER`, `SUPERWEAPON`, `ENVIRONMENTAL`, `RESOURCE_BOOSTER`, `BUILD_RATE_BOOSTER`, `PLANETARY_SHIELD`, `ENERGY_DRAINING` (last is optional pending Phase 3 decision).
- [ ] Define frozen dataclasses `EffectFacet`, `EnergyFacet`, `AbilityMetadata` per [design.md → Schema](design.md#schema).
- [ ] Build `_REGISTRY: dict[str, AbilityMetadata]` from a single tuple literal that mirrors `EFFECT_ABILITY_METADATA` (11 entries) plus role tags for every name currently in any of the seven `design_role` frozensets, plus `STABILIZER`/`SUPERWEAPON`/`BUILD_RATE_BOOSTER`/`PLANETARY_SHIELD` kind tags for the names in those tables/literals, plus a `ShieldProjection` entry with `kind_tag=COMBAT_FLAT_BONUS`.
- [ ] Export public API: `get_ability_metadata`, `ability_has_role_tag`, `ability_has_kind_tag`, `abilities_with_role_tag`, `abilities_with_kind_tag`, `ability_action_time_field`, `ability_drains_energy`.
- [ ] **Do not** import from `game/simulation/components/abilities/`. Names are strings; the module stays a leaf.
- [ ] Verify: `pytest tests/unit/strategy/services/test_ability_metadata_registry.py` is green.

**Notes:** [Filled during implementation]

### Task 1.3: Convert `effect_ability_metadata.py` to a shim [Medium]

**File:** `game/strategy/services/effect_ability_metadata.py`
**Tests:** `pytest tests/unit/strategy/services/test_effect_ability_metadata.py tests/unit/strategy/services/test_effect_ability_display.py -q`

- [ ] Replace internal `EFFECT_ABILITY_METADATA` tuple literal with a derivation from the unified registry (iterate `_REGISTRY` values where `effect is not None`; preserve iteration order).
- [ ] Re-export `EffectAbilityMetadata` as an alias of `EffectFacet` (or wrap if shape requires).
- [ ] Keep `find_metadata`, `is_known_effect_ability`, `all_owner_aware_scopes` signatures unchanged.
- [ ] Verify: existing tests stay green — `test_effect_ability_metadata.py` and `test_effect_ability_display.py`.

**Notes:** Per [decisions.md](decisions.md) row 2, this shim is non-negotiable until a follow-up project collapses it.

### Task 1.4: Stub `test_ability_metadata_contracts.py` [Simple]

**File:** `tests/unit/strategy/services/test_ability_metadata_contracts.py` (NEW)

- [ ] Create the file with module docstring noting it is extended in Phase 4 (CommandSpec contract) and Phase 6 (stabilizer/superweapon contracts).
- [ ] Add a trivial passing test importing the unified registry so the file is non-empty and collected.

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist

When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/unit/strategy/services/test_ability_metadata_registry.py tests/unit/strategy/services/test_ability_metadata_contracts.py tests/unit/strategy/services/test_effect_ability_metadata.py tests/unit/strategy/services/test_effect_ability_display.py` is fully green
- [ ] Parity test confirms every currently-hardcoded name has at least one tag
- [ ] `effect_ability_metadata.py` public API unchanged (no caller broken)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
