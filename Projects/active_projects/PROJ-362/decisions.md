# PROJ-362: Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-04 | Project initialized | Strategy Layer Tech Debt Review finding #2 (P1 hotspot — `_aggregate` CC 47, 150+ LOC, hardcoded ability metadata) |
| 2026-05-04 | Renumbered from PROJ-352 to PROJ-362 | Merge-conflict collision on PROJ-351..360 from commit 97a96e7d0; user chose to leave existing IDs alone |
| 2026-05-04 | Phase 1 = characterization tests, no production change | Refactoring CC-47 code without baseline coverage would silently change behavior. Findings/03 identified 5 specific coverage gaps that must close first. |
| 2026-05-04 | `EffectAbilityMetadata` is a frozen dataclass + tuple registry | Mirrors the proven `stabilizer_registry.py:54-70` pattern (PROJ-300). Immutable, hashable, ergonomic. |
| 2026-05-04 | Component data is the source of truth — no data migration | Per findings/01, every ability entry already carries the fields needed (`resource_type`, `damage_type`, `rate`, `multiplier`, `activation_time`, `scope`). The registry is purely a code refactor. |
| 2026-05-04 | Do NOT unify with `combat_modifier_collector` | Per findings/02, it is a parallel consumer using a different aggregation model (PROJ-272 ownership-aware scope routing). Unification is a separate project, if ever. |
| 2026-05-04 | `make_group_key` and `make_display_name` keep their signatures | Public API per FEAT-16; planet list UI imports both. Bodies become metadata-driven, signatures stay. |
| 2026-05-04 | `_legacy_provider_fields` deletion deferred to Phase 4 | 5 UI files consume the legacy keys (`facility_name`, `planet_name`, etc.). Removal requires UI migration audit; out of scope for the metadata/decomposition core work. Phase 4 is documented but explicitly deferred. |

## Audit Remediation

OpenCode review (req_20260505_061729_30913a) flagged 0 CRIT, 1 MAJ, 3 MIN, 3 NIT. Only the MAJ is addressed here per remediation policy.

| Date | Finding | Verdict | Action |
|------|---------|---------|--------|
| 2026-05-04 | MAJ-001 — `system_effects_collector.py` 569 LOC > 500-LOC ceiling (docs/02_PATTERNS.md) | **Fix** | Extracted display/grouping/format helpers (`make_group_key`, `make_display_name`, `format_intrinsic_ability_magnitude`) plus internal helpers (`_ability_kind`, `_format_status`, `_is_activatable`) into new module `game/strategy/services/effect_ability_display.py`. Re-imported them in `system_effects_collector.py` and added an `__all__` block to preserve the public import surface (UI consumers in `planet_list_filters.py`, `planet_list_window.py`, `system_tree_panel.py`, plus tests, continue to import from the collector unchanged). Collector now 442 LOC; new display module 168 LOC. Opportunistically swapped one `Optional[Dict[str, Any]]` for `Dict[str, Any] | None` (per docs/03_CONVENTIONS.md PEP 604, MIN-003 partial). Tests: `tests/unit/strategy/services/` PROJ-362 scope (123 tests) green; full unit suite for the package green except for unrelated component-registry failures owned by a parallel agent's branch state (`test_ship_instance_damage`, `test_design_validator`, `test_design_cost_calculator`, `test_ship_stats_cargo_storage`). Verified by stashing this change and confirming the failures vanish, then restoring. |
| 2026-05-05 | REG-001 — dead `_ability_kind` import in `system_effects_collector.py` line 45 | **Fix** | Removed the unused name from the `effect_ability_display` import block. The collector body never referenced it after the PROJ-362 audit-remediation move; only the inline display module continues to call `_ability_kind`. Verified: `grep -n "_ability_kind" game/strategy/services/system_effects_collector.py` returns nothing. No behavior change; tightens import surface. |

## Phase 4 Closure (2026-05-05)

Phase 4 was deferred per the original plan because the dependency map at
`findings/02_dependencies.md` listed 5 UI consumers of
`_legacy_provider_fields`. A re-audit (`findings/04_ui_migration_map.md`)
showed only **1 of the 5 sites is a real consumer**; the other 4 were
string-grep false positives — they read `facility_id` / `planet_name` /
`facility_name` from independent local code paths that never touch the
collector's provider DTO. Phase 4 was reactivated and closed in a single
pass.

### Per-site outcome

| Site | Status | Action |
|------|--------|--------|
| `game/ui/panels/system_tree_panel.py` (`_legacy_provider_label`, `:552`, `:582`) | **Migrated** | Deleted `_legacy_provider_label` helper; replaced both `p.get('source_label') or _legacy_provider_label(p)` calls with `p.get('source_label') or "(unknown)"`. Pinned by `tests/unit/ui/panels/test_system_tree_panel_characterization.py::TestProviderLabelRendering` (new) and `TestSetItemsEffects::test_add_effects_group_falls_back_to_unknown_when_source_label_missing` (rewrite of the legacy fallback test). |
| `game/ui/screens/planet_abilities_window.py:107-109` | **Not a consumer** | Reads from `PlanetAbilitiesController.scan_abilities()` — controller builds dicts directly from `facility.instance_id` / `facility.name`. Independent code path; values are real entity IDs used for command dispatch (`IssuePlanetOrderCommand`). No change needed. |
| `game/ui/screens/planet_abilities_controller.py:161-163` | **Not a consumer** | Producer of (2) above. Sets `facility_id` / `facility_name` / `component_key` from facility attributes; never reads from the collector shim. No change needed. |
| `game/ui/panels/planet_report_panel.py:474-483` | **Not a consumer** | `facility_name` is a local variable populated from `(f.name for f in self.planet.facilities ...)`. Counts complexes by `design_id`. No provider-DTO read. No change needed. |
| `game/ui/screens/strategy_detail_fmt.py:435-436` | **Not a consumer** | `result[ability_key] = {'planet_name': planet.name}` is a local dict populated from `planet.name`. Different code path from the collector's emitted `planet_name`. No change needed. |

### Shim deletion

- Deleted `_legacy_provider_fields(source)` function at the end of
  `game/strategy/services/system_effects_collector.py`.
- Removed the `**_legacy_provider_fields(source),` spread from the
  provider dict in `_build_provider`.
- Updated the module docstring + `_build_provider` docstring to reflect
  the removal.
- Updated the test fixture comment in
  `tests/unit/strategy/services/test_system_effects_collector_aggregate_characterization.py`.
- Replaced the legacy-keys assertion in
  `test_system_effects_collector.py::TestProviderUniversalFields` with
  an absent-keys assertion (loop over the 5 retired keys).

### Regression pin

New `TestProviderLegacyFieldsRetired` class in
`tests/unit/strategy/services/test_system_effects_collector.py` pins:
1. Provider DTOs from `collect_system_effects` do not contain the 5
   retired keys (`planet_name`, `planet_id`, `facility_name`,
   `facility_id`, `component_key`).
2. The `_legacy_provider_fields` function is gone from the
   `system_effects_collector` module (re-import would fail).

### View-model helpers introduced

**None.** The new DTO already carries everything `system_tree_panel`
needs. The 11-line `_legacy_provider_label` helper collapsed to a single
inline `or "(unknown)"` fallback — strong preference of reading new
fields directly satisfied without any UI-side bridge.

### Tests

- `tests/unit/strategy/services/test_system_effects_collector*.py` +
  `tests/unit/strategy/services/test_effect_ability_metadata.py` +
  `tests/unit/ui/panels/test_system_tree_panel*.py` — 168/168 green.
- Full unit `tests/unit/strategy/` + `tests/unit/ui/` — 8026 pass, 2
  skipped (unrelated).
- Integration `tests/integration/ui/test_system_tree_panel_smoke.py` —
  7/7 green.
