# PROJ-197: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-25 | Project initialized | Starting point for Duplication Consolidation Completion |
| 2026-02-25 | ValidationResult in simulation_tests/ left as-is | These are completely different classes (different fields, different purpose) from game.core.ValidationResult. Not actual duplication. |
| 2026-02-25 | Global colors.py strategy for color consolidation | Add all semantic constants to game/ui/colors.py. One import source for all UI files. Simpler than per-screen theme files. |
| 2026-02-25 | Include test lab renderer.py fix | Quick win - constants already exist in theme.py, just need substitution in renderer.py. |
| 2026-02-25 | Font consolidation is complete - out of scope | Previous agent reduced from 81 to 13 instances. Remaining are internal/scripts only. |
| 2026-02-25 | Consolidate ALL tuples (not just common ones) | Complete elimination of magic color numbers. Domain-specific tuples (spectrum, gases, planets) also get constants. |
| 2026-02-25 | Normalize near-duplicate colors to existing constants | Use existing HP_HEALTHY/HP_DAMAGED/HP_CRITICAL. Minor visual changes acceptable for palette simplification. |
| 2026-02-25 | Phase order: palette first, then substitution by screen area | Phase 1 adds all constants. Phases 2-6 substitute by grouping. Phase 7 audits. |
