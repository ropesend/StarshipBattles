# PROJ-447: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-18 | Project initialized | Starting point for Post-refactor residue: Simulation + AI + Research + LowLevelEngine + Docs (Bucket D supplemental) |
| 2026-05-18 | F-D-024 (fleet_speed_calculator.py:175 `EnvironmentalEffects` reference) DEFERRED to PROJ-445 F-B-016 | File lives in `game/strategy/services/`, owned by PROJ-445. PROJ-445's agent folds the fix into its F-B-016 sibling edit per the project partition. |
| 2026-05-18 | F-D-021 rename half is moot — `_pop_carried_vehicles_legacy` does not exist | Bucket D finding listed the symbol name incorrectly. Actual carrier-controller method is `_pop_cvs` (with sibling `_pop_fighter_cvs`); neither carries a "legacy" suffix. The stale-narration drop half of F-D-021 was applied to `_pop_cvs`'s docstring (PROJ-431 Phase 1e provenance block removed). No rename performed. |
| 2026-05-18 | F-D-001 + F-D-026 applied in one pass | The class docstring (F-D-001) and module docstring (F-D-026) are in the same file; both rewrites landed in Task 2.1's edit pair to avoid touching the file twice. |
