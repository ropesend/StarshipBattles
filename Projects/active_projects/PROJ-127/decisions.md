# PROJ-127: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-13 | Project created from review | Review identified 245 findings; 36 selected for remediation |
| 2026-02-13 | Severity-based phasing | Critical findings in Phase 1, Major in Phase 2, etc. |
| 2026-02-13 | Phase 2 tasks ACCEPTABLE/INFO | 8 findings analyzed - all are necessary patterns or natural similarity, no code changes needed |
| 2026-02-13 | DUP-SIM-001 ACCEPTABLE | Dataclass to_dict/from_dict is necessary boilerplate for serialization - each class has unique fields |
| 2026-02-13 | DUP-SIM-002 ACCEPTABLE | Resource ability classes (Consumption/Storage/Generation) are semantically different with different behaviors |
| 2026-02-13 | DUP-SIM-003 ACCEPTABLE | Team iteration pattern is simple comprehension, each use has different conditions |
| 2026-02-13 | DUP-SIM-004 ACCEPTABLE | Vector2 conversion is defensive interop code for pygame/game Vector2 compatibility |
| 2026-02-13 | DUP-SIM-005 ACCEPTABLE | Color mapping in get_ui_rows is context-specific, centralizing adds complexity |
| 2026-02-13 | DUP-SIM-006 ACCEPTABLE | ship_id_map is necessary for object-to-ID translation in serialization |
| 2026-02-13 | DUP-SIM-007 ACCEPTABLE | Validation functions share pattern but validate different schemas |
| 2026-02-13 | DUP-SIM-008 INFO | Natural similarity in dataclass state classes - acknowledged, no action |
