# PROJ-11: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-01-24 | Project created from review | Review identified 18 architectural findings for remediation |
| 2026-01-24 | Phase 1 focuses on circular dependencies | Must establish clean dependency graph before safe refactoring |
| 2026-01-24 | Phase 2 targets god objects | StrategyInterface, Ship, app.py are the biggest blockers |
| 2026-01-24 | Use simple DI container, not framework | Over-engineering risk; simple service locator is sufficient |
| 2026-01-24 | Extract components incrementally | Small changes with tests after each reduces risk |
| 2026-01-24 | Depends on PROJ-10 completion | Security fixes should not be blocked by refactoring |
