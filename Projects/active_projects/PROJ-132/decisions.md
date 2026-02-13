# PROJ-132: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-13 | Project created from review | Review identified 221 findings; 24 selected for remediation |
| 2026-02-13 | Severity-based phasing | Critical findings in Phase 1, Major in Phase 2, etc. |
| 2026-02-13 | ADR-FND-001: Use DI for Camera in ResearchTreeScene | Moved Camera import to factory function, added optional camera parameter. Eliminates layer violation at module level. |
| 2026-02-13 | ADR-FND-002: Accept IControllable as-is | Interface is 477 lines but well-organized with 5 clear sections. All 36 methods are cohesive (ship control). Splitting would create coupling issues where controllers need multiple interfaces. Marking as acceptable design. |
| 2026-02-13 | ADR-FND-003: Accept protocols.py as-is | File is 547 lines (marginal 47-line overage). Contains cohesive set of Protocol definitions for cross-layer type safety. Splitting would fragment protocol discovery. Well-organized with section comments. Acceptable. |
