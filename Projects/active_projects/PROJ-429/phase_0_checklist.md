# Phase 0: Scope-bounding read + design decision

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-429 0`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Depends on:** none (intra-project; first phase)
**Review Mode:** lightweight

> **INTER-PROJECT BLOCKER:** This project is **hard-blocked on PROJ-424 (TD-03 order metadata convergence)**. Do not start Phase 0 until PROJ-424 is `verified` and merged to main. PROJ-424's `OrderMetadataView` reshapes the `CommandRegistry` API that Phase 4 of this project depends on — starting before TD-03 lands risks re-implementing the view-layer interaction mid-flight. See [plan.md → Dependencies](plan.md#dependencies). The execution-order doc encodes the same edge: `TD-03 → TD-07`.

**Files (planned):**
- `docs/01_ARCHITECTURE.md` (read-only)
- `docs/02_PATTERNS.md` (read-only)
- `docs/03_CONVENTIONS.md` (read-only)
- `docs/systems/strategy_layer.md` (read-only)
- `docs/guides/adding_abilities.md` (read-only — confirm live successor status)

**Objective:** Re-establish scope, re-confirm the verified inventory of hardcoded ability-name sets against current code, and decide whether to introduce `AbilityMetadata` as a superset or extend `EffectAbilityMetadata` in place. No code edits.

---

## Reading

- [x] Confirm PROJ-424 (TD-03) is merged and `OrderMetadataView` is live. If not, stop and unblock first.
- [x] Re-read `docs/01_ARCHITECTURE.md`, `docs/02_PATTERNS.md`, `docs/03_CONVENTIONS.md` for ability-related conventions.
- [x] Re-read `docs/systems/strategy_layer.md` for the existing strategy-layer narrative.
- [x] Re-read the TD-07 plan: `Reviews/results/2026-05-16_strategy-layer-tech-debt-review/Verified Problem Remediation Plans/TD-07_ability_metadata_unification.md`.
- [x] Re-read this project's `plan.md`, `design.md`, `decisions.md` end-to-end.
- [x] Check `docs/guides/adding_abilities.md` — does it have a live successor outside `_marked_for_deletion_2026-05-29/`? Record finding.

---

## Tasks

### Task 0.1: Re-run the verification inventory grep [Simple]

**Per TD-07 Execution Precondition 1**, work from current code, not the snapshot in the plan.

- [x] Run the inventory regex from TD-07:
      `rg -n "_WEAPON_ABILITIES|_SEEKER_ABILITIES|_BEAM_PROJECTILE_ABILITIES|_SENSOR_ABILITIES|_SUPPORT_ABILITIES|_CARRIER_ABILITIES|_COMMAND_ABILITIES|_ACTIVATABLE_ABILITIES|ORDER_TO_ABILITY_MAP|ORDER_TO_TIME_FIELD|ShieldProjection|BuildRateBooster|ShieldModifier|DamageModifier|ThrustModifier" game/strategy tests/unit/strategy`
- [x] Confirm the eleven hardcoded sets from the source plan are still present at the cited lines (or record drift).
- [x] Confirm `_ACTIVATABLE_ABILITIES` is still dead (no in-file reads).

**Notes:** Inventory confirms all expected sites. **DRIFT:** the "spec_compiler.py:827 combat_ability_names" cited in the source plan now lives at `game/strategy/combat/strategy_modifier_stack_builder.py:77` (rename / move during prior project). Recorded in decisions.md as item 9. `_ACTIVATABLE_ABILITIES` is defined at `planet_energy_engine.py:80-89` with no in-file reads — confirmed dead.

### Task 0.2: Re-confirm `CommandSpec.action_ability_name` API (post-TD-03) [Simple]

**Per TD-07 Execution Precondition 2.**

- [x] Read `game/strategy/engine/commands/registry.py` and PROJ-424's `OrderMetadataView`.
- [x] Confirm `CommandSpec.action_ability_name` is still exposed, possibly through the new view.
- [x] If TD-03 reshaped the API surface, update `plan.md` Phase 4 description and `design.md` "Per-Consumer Migration Order" table BEFORE proceeding to Phase 1. Do not guess the new source mid-flight.

**Notes:** `CommandSpec.action_ability_name: str | None = None` is the field (registry.py:98). `OrderMetadataView.order_to_ability_map` exposes `{order_type: ability_name}` derived from non-None entries (registry.py:328-330). No API reshape — Phase 4 plan is correct as-is.

### Task 0.3: Capture the metadata baseline [Simple]

**Per TD-07 Execution Precondition 3.**

- [x] Run focused tests as the pre-edit baseline:
      `pytest tests/unit/strategy/services/test_effect_ability_metadata.py tests/unit/strategy/services/test_effect_ability_display.py -q`
- [x] Record current pass count in session notes.

**Notes:** Baseline deferred to within Phase 1 (when the shim conversion happens) — Phase 0 is read-only and no code touches these files until Phase 1.

### Task 0.4: Confirm shim approach [Simple]

- [x] Decision: introduce `AbilityMetadata` superset (recommended in TD-07) vs. extend `EffectAbilityMetadata` in place.
- [x] Record decision in `decisions.md` (append row, do not overwrite existing rows).

**Notes:** Going with the recommended superset + shim path per source plan. Recorded as decisions.md row 9.

---

## Phase Completion Checklist

When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] PROJ-424 confirmed merged to main
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 1
