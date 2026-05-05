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
