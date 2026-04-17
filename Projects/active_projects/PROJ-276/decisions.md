# PROJ-276: Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-16 | Project initialized | User was unaware of dual-tracking until combat-system review. Clean-Sheet Rule + System Migration Policy in CLAUDE.md mandate eradication. |
| 2026-04-16 | Delete the field, do not deprecate | Clean-Sheet Rule 3 + CLAUDE.md System Migration Policy. "When a new system replaces an old one, ERADICATE the old system completely." |
| 2026-04-16 | No save migration code | `CLAUDE.md`: "Save files are disposable. Old saves are not migrated — they are discarded." |
| 2026-04-16 | `components: Dict[str, ComponentState]` is the sole source of truth | Matches PROJ-269 Phase 2 design intent that was never closed. |
| 2026-04-16 | Multi-instance behavior CHANGE is expected | Ships with 2+ identical components no longer flatten HP across instances. This is a bug FIX, not a regression. Flag in user verification — the seeker scenarios in Combat Lab may need recalibration. |
| 2026-04-16 | Phase order: stat_calc (20 sites) first | The biggest migration is ALSO the most load-bearing. Getting it right early means subsequent phases have a stable foundation. |
| 2026-04-16 | TDD per migration group | Each site gets a failing test before the read/write is migrated. Parity tests for single-instance behavior. |
| 2026-04-16 | Field deletion is its own phase (Phase 6) | The pass-point where backward compat is severed. Must be atomic — either `component_damage` exists or it doesn't; no half-state allowed. |
| 2026-04-16 | Independent of PROJ-273/274/275 | Can run in parallel. No shared files with other combat-review projects. |
