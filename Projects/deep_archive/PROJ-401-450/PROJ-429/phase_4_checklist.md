# Phase 4: Migrate `action_time_resolver` (TD-03 coupling)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-429 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Depends on:** phase_3
**Review Mode:** standard

> **TD-03 COUPLING CHECK:** This is the phase with direct dependency on PROJ-424. Before writing any code, re-confirm `CommandSpec.action_ability_name` is still exposed (possibly through PROJ-424's `OrderMetadataView`) and that `action_time_resolver.py` still derives `ORDER_TO_ABILITY_MAP` from it. If TD-03 reshaped the API surface, **stop** and update `plan.md` Phase 4 description before coding.

**Files (planned):**
- `game/strategy/services/action_time_resolver.py` (modify — drop empty `ORDER_TO_TIME_FIELD`, drive activate/deactivate from facet)
- `tests/unit/strategy/services/test_action_time_resolver.py` (modify — facet-driven test FIRST)
- `tests/unit/strategy/services/test_ability_metadata_contracts.py` (modify — add CommandSpec contract test)
- `game/strategy/engine/commands/registry.py` (read-only — confirm API)

**Objective:** Drive activation/deactivation time-field selection from the unified `EnergyFacet`. Delete the empty `ORDER_TO_TIME_FIELD`. Add a contract test asserting every `CommandSpec.action_ability_name` exists in the unified registry.

---

## Reading

- [ ] Confirm TD-03 (PROJ-424) is verified-and-merged (re-check, since multiple weeks may have elapsed since Phase 0).
- [ ] Read `game/strategy/engine/commands/registry.py` — confirm `CommandSpec.action_ability_name` shape (or its `OrderMetadataView` projection).
- [ ] Read `game/strategy/services/action_time_resolver.py` — lines 39-119, focusing on the empty `ORDER_TO_TIME_FIELD` at lines 54-55 and the inline `activation_time`/`deactivation_time` branch at lines 89-93.
- [ ] Read `tests/unit/strategy/services/test_action_time_resolver.py`.

---

## Tasks

### Task 4.1: Add the failing facet-driven test (TDD red) [Simple]

**File:** `tests/unit/strategy/services/test_action_time_resolver.py`

- [ ] Add `test_ability_action_time_field_planetary_shield`:
      `assert ability_action_time_field('PlanetaryShield') == 'activation_time'` (or whichever field the ability declares — verify against current `PlanetaryShield` definition under `game/simulation/components/abilities/`).
- [ ] Add `test_activate_branch_reads_facet_not_literal`: with a mock activate-ability order, assert the resolver looks up `EnergyFacet.activation_time_field` rather than hard-coding `'activation_time'`.
- [ ] Confirm failure: resolver still uses inline literal → tests fail.

**Notes:** [Filled during implementation]

### Task 4.2: Add the failing CommandSpec contract test (TDD red) [Simple]

**File:** `tests/unit/strategy/services/test_ability_metadata_contracts.py`

- [ ] Add `test_every_command_action_ability_name_exists_in_registry`:
      For each `CommandSpec` in `CommandRegistry` (or `OrderMetadataView`), assert `get_ability_metadata(spec.action_ability_name) is not None` whenever `action_ability_name` is set.
- [ ] Confirm test reflects the current `CommandRegistry` truth and that any missing entries cause failure.

**Notes:** [Filled during implementation]

### Task 4.3: Drive activate/deactivate branch from `EnergyFacet` (TDD green) [Medium]

**File:** `game/strategy/services/action_time_resolver.py`

- [ ] Replace inline `'activation_time' if ... else 'deactivation_time'` at lines 89-93 with a facet read: look up `get_ability_metadata(ability_name).energy.activation_time_field` (or `.deactivation_time_field`).
- [ ] Delete empty `ORDER_TO_TIME_FIELD` at lines 54-55.
- [ ] Have `_extract_time` consult `ability_action_time_field(name)` as the source of truth.
- [ ] Verify: focused tests green, derived `ORDER_TO_ABILITY_MAP` still matches `CommandRegistry`.

**Notes:** [Filled during implementation]

### Task 4.4: Backfill missing registry entries (if contract test surfaces gaps) [Simple]

- [ ] If `test_every_command_action_ability_name_exists_in_registry` reveals abilities present in `CommandRegistry` but absent from the unified registry, add minimal `AbilityMetadata` entries for them (name + `action_time_field` at minimum).
- [ ] Re-run contract test; confirm green.

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist

When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] No `ORDER_TO_TIME_FIELD` constant remains in `action_time_resolver.py`
- [ ] No inline `activation_time` / `deactivation_time` literal in the activate/deactivate branch
- [ ] `test_every_command_action_ability_name_exists_in_registry` is green and pinned
- [ ] `pytest tests/unit/strategy/services/test_action_time_resolver.py tests/unit/strategy/services/test_ability_metadata_contracts.py` is fully green
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 5
