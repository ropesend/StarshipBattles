# PROJ-18: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-01-25 | Project initialized | Starting point for Standardize Registry Access |
| 2026-01-25 | Delete DataService entirely | Not used in any production code - only exported and tested. Contains 9 wrapper methods with no value. User confirmed deletion after analysis showed zero usage. |
| 2026-01-25 | Add new utility functions (freeze_registry, set_validator, clear_registry) | User requested to add missing utilities for API completeness. Follows existing pattern of Tier 1 utility functions. |
| 2026-01-25 | Focus on production code anti-patterns only | 275 occurrences in test code mostly use `.clear()` which is acceptable. Production code has 5 anti-pattern locations to fix. |
| 2026-01-25 | Pre-existing test failures are out of scope | 5 tests fail due to `builder._workshop` reference - unrelated to registry access. Should be addressed separately. |

## Questions Asked & Answers

**Q1: DataService has 9 wrapper methods and 4 filtering methods. It's NOT used in production. Remove completely or keep filtering methods?**
- User asked: "Are you sure it is not used anywhere?"
- Confirmed: Zero production imports. Only used in:
  - `game/simulation/services/__init__.py` (export)
  - `tests/unit/services/test_data_service.py` (test)
- User Answer: Remove completely (implied after confirmation)

**Q2: Should we add missing utility functions (freeze_registry, set_validator, clear_registry)?**
- User Answer: "Add missing utilities too"
