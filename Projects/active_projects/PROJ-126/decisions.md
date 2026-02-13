# PROJ-126: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-13 | Project created from review | Review identified 245 findings; 29 selected for remediation |
| 2026-02-13 | Severity-based phasing | Critical findings in Phase 1, Major in Phase 2, etc. |
| 2026-02-13 | ADR-FND-003: No change required | behaviors.py (521 lines) is well-organized, test behaviors clearly separated with comment, 4 test files provide coverage. Minor severity advisory finding - acceptable state. |
| 2026-02-13 | ADR-SIM-003: FALSE POSITIVE | BattleController (873 lines) uses proper Strategy pattern (BattleModeHandler), delegation to RetreatManager, BattleStateManager, BattleService. Per PROJ-122 analysis. |
| 2026-02-13 | ADR-SIM-004: FALSE POSITIVE | Ship entity (810 lines) uses proper composition (ShipFormation, ShipStatsCalculator, ShipCombatEngine), mixins (ShipPhysicsMixin), delegation. Per PROJ-122 analysis. |
| 2026-02-13 | ADR-SIM-005: ACCEPTABLE | Documented late import in Ship.add_component() breaks circular dependency with services/__init__.py. Standard pattern with clear documentation. |
| 2026-02-13 | ADR-SIM-006: ACCEPTABLE | Late imports in ship_stat_querier.py, ship_stats.py documented as "INTENTIONAL LATE IMPORT" with architecture doc reference. Standard pattern. |
| 2026-02-13 | ADR-SIM-007: INFO ONLY | Heavy use of TYPE_CHECKING is standard Python practice. Severity "Info", Effort "N" - no action required. |
