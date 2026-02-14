# PROJ-148: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-14 | Project created from review | Review identified 241 findings; 27 selected for remediation |
| 2026-02-14 | Severity-based phasing | Critical findings in Phase 1, Major in Phase 2, etc. |
| 2026-02-14 | DUP-FND-001: Remove StrategyMetadataService.load_data() | Duplicated StrategyManager.load_data() logic. WorkshopDataLoader now uses StrategyManager directly, which populates StrategyMetadataService via set_strategies(). |
| 2026-02-14 | DUP-FND-002: Accept singleton clear() pattern as-is | Each singleton has unique fields requiring custom clear() logic. Adding abstraction overhead (e.g., registering clearable fields in SingletonMeta) would add complexity without proportional benefit. Pattern is consistent across ~4 singletons. |
