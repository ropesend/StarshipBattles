# Phase 4: Retire `_legacy_provider_fields` (COMPLETE)

> **STATUS: COMPLETE (2026-05-05)** — phase reactivated and closed in a
> single pass. See `decisions.md` "Phase 4 Closure" and
> `findings/04_ui_migration_map.md` for the full audit + outcome.

**Status:** Complete (2026-05-05).
**Closure summary:** Re-audit (`findings/04_ui_migration_map.md`) of the
5 candidate consumers in `findings/02_dependencies.md` revealed only 1
real consumer (`system_tree_panel.py`); the other 4 were string-grep
false positives. Migrated the single consumer to read `source_label`
directly with a `"(unknown)"` defensive fallback, deleted the
`_legacy_provider_fields` function and the `**_legacy_provider_fields(source)`
spread in `_build_provider`, updated docstrings + test fixture comment,
and added a regression test class
(`TestProviderLegacyFieldsRetired`) pinning the absence of the 5 legacy
keys + the function itself.
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

- [x] User explicitly approves phase reactivation. (2026-05-05)
- [x] UI audit produces a per-consumer migration map: which legacy key → which new field on the provider DTO. → `findings/04_ui_migration_map.md`.
- [x] Decide: do consumers read directly from `provider['source_kind']`, `provider['source_label']`, etc., or do we introduce a UI-side view-model that preserves the old labels? → Direct read; no view-model needed.
- [x] New tests for each UI panel/screen verifying display text after migration. → `tests/unit/ui/panels/test_system_tree_panel_characterization.py::TestProviderLabelRendering` + updated fallback test.

## Tasks

### Task 4.1: UI consumer audit
- [x] Documented each of the 5 UI sites in `findings/04_ui_migration_map.md`. Result: 1 real consumer, 4 false positives.

### Task 4.2: Migrate UI consumers
- [x] `system_tree_panel.py` migrated to read `source_label` directly with `"(unknown)"` fallback.

### Task 4.3: Delete `_legacy_provider_fields`
- [x] Removed the function from `system_effects_collector.py`.
- [x] Removed the `**_legacy_provider_fields(source)` spread from the provider dict construction.
- [x] All UI tests still green (43/43 system_tree characterization+hazard; 168/168 collector+UI; 8026/8028 full unit suite).

---

## Phase Completion Checklist
- [x] All UI consumers migrated (1 real consumer migrated; 4 false positives confirmed not consumers).
- [x] `_legacy_provider_fields` deleted (function + spread + docstring references).
- [x] No regression in System Tree / Planet List rendering.
- [ ] User verified
