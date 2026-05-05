# Phase 4: Retire `_legacy_provider_fields` (DEFERRED)

> **STATUS: DEFERRED** — Do not begin without explicit user direction.
> This phase touches UI; it is out of the original scope of PROJ-362 and should be planned with a separate UI consumer audit.

**Status:** Deferred
**Objective:** Eliminate the `_legacy_provider_fields` compatibility shim by migrating the 5 UI consumers to the new provider DTO shape (or deleting the legacy keys after consumers stop reading them).

---

## Why deferred

Per `findings/02_dependencies.md`, these UI files read the legacy keys (`facility_name`, `planet_name`, `facility_id`, `planet_id`, `component_key`):
- `game/ui/panels/system_tree_panel.py` (lines 9-20: `_legacy_provider_label`)
- `game/ui/screens/planet_abilities_window.py:109`
- `game/ui/screens/planet_abilities_controller.py:129`
- `game/ui/panels/planet_report_panel.py:474+`
- `game/ui/screens/strategy_detail_fmt.py:435-436`

Removing the shim requires migrating all 5 consumers in lockstep, which expands scope into the UI layer — a separate concern from the metadata-registry decomposition (Phases 1-3).

## Pre-work checklist (when phase is unparked)

- [ ] User explicitly approves phase reactivation.
- [ ] UI audit produces a per-consumer migration map: which legacy key → which new field on the provider DTO.
- [ ] Decide: do consumers read directly from `provider['source_kind']`, `provider['source_label']`, etc., or do we introduce a UI-side view-model that preserves the old labels?
- [ ] New tests for each UI panel/screen verifying display text after migration.

## Tasks (skeleton)

### Task 4.1: UI consumer audit
- [ ] Document each of the 5 UI sites: what legacy field is read, what label is shown, whether the new shape (source_kind/source_label/source_id) suffices.

### Task 4.2: Migrate UI consumers
- [ ] One PR per consumer (or one batch with characterization tests for each). Replace legacy-field reads with new DTO field reads.

### Task 4.3: Delete `_legacy_provider_fields`
- [ ] Remove the function from `system_effects_collector.py`.
- [ ] Remove the `**_legacy_provider_fields(source)` spread from the provider dict construction.
- [ ] Verify all UI tests still green.

---

## Phase Completion Checklist
- [ ] All UI consumers migrated
- [ ] `_legacy_provider_fields` deleted
- [ ] No regression in System Tree / Planet List rendering
- [ ] User verified
