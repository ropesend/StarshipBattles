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
| 2026-02-13 | ADR-SIM-001: Move factory functions to UI layer | Created `game/ui/services/battle_factories.py` with `create_manual_battle`, etc. These functions import from AI layer, which is not allowed in simulation layer. Eliminates bidirectional coupling. |
| 2026-02-13 | ADR-SIM-002: Use protocol types only in battle_engine.py | Removed `AIController` concrete type import, now uses only `IAIController` protocol. Maintains proper layer isolation in type annotations. |
| 2026-02-13 | ADR-SIM-005: Accept late import for ModifierService as-is | ARCHITECTURE.md documents this as intentional design. Real import cycle that cannot be moved to module level. Edge operation (component addition only). Complex restructuring for minimal benefit. |
| 2026-02-13 | ADR-SIM-007: Accept Component.py as-is (monitor only) | INFO severity (lowest). File at 723 lines, below 800-line extraction threshold. Significant delegation already exists. Review recommends monitoring. |
