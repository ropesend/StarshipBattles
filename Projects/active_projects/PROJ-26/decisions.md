# PROJ-26 Decisions Log

## Decision 1: Create Paths class in paths.py
**Date:** 2026-01-27
**Context:** Need to choose the structure for centralized path management
**Options Considered:**
1. Module-level constants (like current constants.py)
2. Paths class with class attributes
3. Configuration object with instance methods

**Decision:** Option 2 - Paths class with class attributes

**Rationale:**
- Mirrors successful pattern in `tests/fixtures/paths.py`
- Provides namespacing (`Paths.DATA_DIR` vs `DATA_DIR`)
- Allows adding classmethods for pathlib.Path accessors
- Still supports backward-compatible module-level exports

---

## Decision 2: Use marker-based root detection
**Date:** 2026-01-27
**Context:** Need reliable method to find project root

**Options Considered:**
1. Relative path from `__file__` (current approach)
2. Marker-based detection (look for game/ and data/ dirs)
3. Environment variable
4. Configuration file

**Decision:** Option 2 - Marker-based detection

**Rationale:**
- More reliable than counting dirname() levels
- Works regardless of module location changes
- Already proven in `tests/fixtures/paths.py`
- No external configuration required

---

## Decision 3: Export backward-compatible constants
**Date:** 2026-01-27
**Context:** Existing code imports from constants.py

**Options Considered:**
1. Update all imports immediately
2. Keep constants.py as-is, create parallel paths.py
3. Have constants.py import from paths.py
4. Export module-level aliases in paths.py

**Decision:** Options 3 + 4 combined

**Rationale:**
- constants.py imports from paths.py (single source of truth)
- paths.py also exports module-level aliases
- Existing code continues to work during migration
- New code can import from either module

---

## Decision 4: Full 5-phase implementation
**Date:** 2026-01-27
**Context:** Review identified 47+ hardcoded paths; need to decide scope

**Options Considered:**
1. Core only (Phases 1-2) - 6 tasks
2. Core + Strategy (Phases 1-3) - 9 tasks
3. Full implementation (Phases 1-5) - 14 tasks

**Decision:** Option 3 - Full implementation

**Rationale:**
- Complete remediation eliminates all technical debt
- Partial migration leaves inconsistent patterns
- Better to do it once thoroughly than incrementally
- All tasks are straightforward find-and-replace operations
