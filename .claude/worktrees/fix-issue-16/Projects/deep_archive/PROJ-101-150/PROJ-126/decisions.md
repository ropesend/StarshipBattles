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
| 2026-02-13 | ADR-UI1-001: ACCEPTABLE | test_framework is intentionally dual-purpose (pytest + Combat Lab). Docstrings explicitly state "bridges pytest and Combat Lab". Not a layer violation. |
| 2026-02-13 | ADR-UI1-002: ACCEPTABLE | Defensive import with try/except in battle_screen.py:455-460. Already DOWNGRADED to MAJOR in validation. |
| 2026-02-13 | ADR-UI1-003, 004, 006: DEFER | God Class findings for TestLabScreen (1908), StrategyScreen (811), BuildQueueScreen (1098) require separate refactoring projects. Beyond Phase 4 scope. |
| 2026-02-13 | ADR-UI1-005: ALREADY RESOLVED | builder/main.py deleted in PROJ-121 Phase 4 (git: 1ac7c81b - Legacy UI eradication). |
| 2026-02-13 | ADR-UI1-007: DEFER | Late imports for circular deps require architecture changes. |
| 2026-02-13 | ADR-UI1-008, 009: DEFER | Private callback methods (_on_*_closed) are passed to window constructors - public API usage. Renaming requires coordinated change across multiple files. |
| 2026-02-13 | ADR-UI1-010: DEFER | ViewModel state mutation requires interface design. |
| 2026-02-13 | ADR-UI1-011: INFO ONLY | TYPE_CHECKING imports are standard Python practice. MINOR severity. |
| 2026-02-13 | ADR-UI1-012, 013: ACCEPTABLE | Performance optimization patterns (_temp_* attrs) for cached values. Documented and intentional. |
| 2026-02-13 | ADR-UI1-014, 015: ALREADY RESOLVED | _ship_has_ability and _extract_modifiers no longer exist in codebase. |
| 2026-02-13 | ADR-UI1-016, 017, 018: INFO ONLY | Severity INFO findings - no action required per validation. |
