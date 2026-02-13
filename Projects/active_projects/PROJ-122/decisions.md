# PROJ-122: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-13 | Project created from review | Review identified 273 findings; 23 selected for remediation |
| 2026-02-13 | Severity-based phasing | Critical findings in Phase 1, Major in Phase 2, etc. |
| 2026-02-13 | ADR-SIM-003 (BattleController) - FALSE POSITIVE | Analyzed: 849 lines with proper Strategy pattern (BattleModeHandler), delegation to RetreatManager, BattleStateManager, BattleService. Factory functions at module level. Well-architected, not a god class. |
| 2026-02-13 | ADR-SIM-004 (Ship) - FALSE POSITIVE | Analyzed: 811 lines with proper composition (ShipFormation, ShipStatsCalculator, ShipCombatEngine), mixins (ShipPhysicsMixin), delegation (ShipStatQuerier, ShipValidatorHelper, ShipSerializer). Well-architected, not a god class. |
| 2026-02-13 | ADR-STR-003 (Galaxy) - FALSE POSITIVE | Analyzed: 837 lines. Galaxy is a data container/registry with proper composition (StarGenerator, PlanetGenerator, NameRegistry). Uses spatial indexing for O(1) lookups. Warp lane generation factored into helper methods (_build_edge_candidates, _apply_mst_edges, _add_density_edges). Single responsibility: galaxy map management. Not a god class. |
| 2026-02-13 | ADR-UI2-002 (ShipThemeManager) - FALSE POSITIVE | Analyzed: 314 lines - well under 500 line threshold. Single responsibility: managing ship visual themes. Clean separation: discovery, image loading, portrait loading, caching, helpers. Thread-safe with proper locking. Uses composition (Paths, load_json, profile_block). Not a god class. |
