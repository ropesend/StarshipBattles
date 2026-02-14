# PROJ-146: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-13 | Project created from review | Review identified 145 findings; 35 selected for remediation |
| 2026-02-13 | Severity-based phasing | Critical findings in Phase 1, Major in Phase 2, etc. |
| 2026-02-14 | CON-FND-009 INTENTIONAL DESIGN | clear() empties registry contents, reset() destroys singleton - distinct concepts per SingletonMeta design |
| 2026-02-14 | CON-FND-011 INTENTIONAL DESIGN | __all__ exports match all public items; Colors/FONT_MAIN moved to ui.colors per PROJ-113 (documented) |
| 2026-02-14 | CON-FND-013 INTENTIONAL DESIGN | ErrorCode enum gaps (V002, C003) are reserved for future use - standard enum practice |
| 2026-02-14 | ADR-FND-004 POSITIVE | Informational finding confirming good architecture - core layer isolates strategy |
| 2026-02-14 | DUP-FND-008 POSITIVE | Informational finding confirming SingletonMeta provides consistent singleton pattern |
| 2026-02-14 | DUP-FND-009 POSITIVE | PROJ-108 already consolidated combat_utils - this finding documents success, not problem |
