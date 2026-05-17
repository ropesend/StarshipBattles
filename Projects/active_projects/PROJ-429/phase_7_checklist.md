# Phase 7: Documentation update and final validation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-429 7`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** phase_6
**Review Mode:** standard

**Files (planned):**
- `docs/systems/strategy_layer.md` (modify)
- `docs/guides/adding_abilities.md` (modify — **only if it has a live successor**; skip if archived under `_marked_for_deletion_*/`)

**Objective:** Make `AbilityMetadataRegistry` the canonical strategy-facing source of truth in the docs. Remove all prose referencing the now-deleted constants (`_ACTIVATABLE_ABILITIES`, the seven design-role frozensets, `ORDER_TO_TIME_FIELD`). Run the full sharded suite. Mark the TD-07 source plan COMPLETED.

---

## Reading

- [ ] Re-read `docs/systems/strategy_layer.md` end-to-end.
- [ ] Check if `docs/guides/adding_abilities.md` has a live successor or only the `_marked_for_deletion_2026-05-29/` copy. Per TD-07's "Concrete File Touch Plan" Phase 7: "The live 'adding abilities' guide only if it is still the supported project guide. Do not update an archived or deletion-bound doc just because a stale reference exists."

---

## Tasks

### Task 7.1: Update `docs/systems/strategy_layer.md` [Medium]

**File:** `docs/systems/strategy_layer.md`

- [ ] Add a section describing `AbilityMetadataRegistry` as the canonical strategy-facing source of truth for ability metadata.
- [ ] Document the schema: `AbilityMetadata` + `EffectFacet` + `EnergyFacet` + `RoleTag` + `StrategicKind`.
- [ ] List the public API: `get_ability_metadata`, `ability_has_role_tag`, `ability_has_kind_tag`, `abilities_with_role_tag`, `abilities_with_kind_tag`, `ability_action_time_field`, `ability_drains_energy`.
- [ ] Remove or rewrite any prose that references `_ACTIVATABLE_ABILITIES`, the seven design-role frozensets, or `ORDER_TO_TIME_FIELD`.
- [ ] Note the shim status of `effect_ability_metadata.py`.
- [ ] Note that the registry is a leaf — no simulation-layer imports.

**Notes:** [Filled during implementation]

### Task 7.2: Conditionally update `docs/guides/adding_abilities.md` [Simple]

- [ ] If the guide has a live successor (not under `_marked_for_deletion_*/`), update it: point at `game/strategy/services/ability_metadata.py` as the **first** edit when adding a new ability.
- [ ] If only the archived copy exists, skip — do not edit deletion-bound documents.

**Notes:** [Filled during implementation]

### Task 7.3: Run the full sharded suite [Complex (wall-clock)]

**Command:** `python Tools/test_sharded/test_sharded.py`

- [ ] Full suite green.
- [ ] If anything fails, fix or scrap-restart from the appropriate phase.

**Notes:** [Filled during implementation]

### Task 7.4: Final complexity check [Simple]

**Command:** `python -m radon cc game/strategy -s -a`

- [ ] Average cyclomatic complexity has not regressed.

**Notes:** [Filled during implementation]

### Task 7.5: Update TD-07 source plan status [Simple]

- [ ] In `Reviews/results/2026-05-16_strategy-layer-tech-debt-review/Verified Problem Remediation Plans/TD-07_ability_metadata_unification.md`, update the status header to **COMPLETED** with the current date.
- [ ] This happens **outside** project execution (the source plan is treated as immutable during the project) — perform it only at project closeout, after audit.

**Notes:** Per source plan's Phase 7 final bullet.

---

## Phase Completion Checklist

When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `docs/systems/strategy_layer.md` describes the unified registry as the canonical source of truth
- [ ] No surviving doc reference to `_ACTIVATABLE_ABILITIES` outside historical archives
- [ ] `python Tools/test_sharded/test_sharded.py` is green
- [ ] `python -m radon cc game/strategy -s -a` shows no regression
- [ ] TD-07 source plan status header is **COMPLETED** with today's date
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "All phases complete; ready for final audit"
