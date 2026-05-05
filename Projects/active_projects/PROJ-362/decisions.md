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
