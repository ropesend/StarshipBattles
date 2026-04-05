# PROJ-239: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-05 | Project created from review | Review identified 77 validated findings; 14 selected (top 10 priority issues) for remediation |
| 2026-04-05 | 4-phase structure by category | Phase 1: Critical fixes, Phase 2: Architecture boundaries, Phase 3: Code quality & dead code, Phase 4: Documentation. Grouped by category (not severity alone) for coherent work sessions |
| 2026-04-05 | AR-002 (facade bypass) deferred | Complex cross-cutting refactor affecting 6+ UI files. Tracked as a goal but not in active scope — too large for this remediation project |
| 2026-04-05 | Dead code removal: grep-verify before delete | All dead method removals must confirm zero callers via codebase-wide grep before deletion |
