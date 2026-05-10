# Legacy Pattern Analyst - Data Formats Report

## Summary
- Total issues found: 5
- Critical: 2, Major: 2, Minor: 1, Info: 0

---

## Findings

### CRITICAL: load_combat_strategies() Has Module-Level Side Effect
**ID:** LDF-01
**Location:** `game/ai/core/system.py:72-86`
**Issue:** `filepath` parameter marked as "legacy/optional override" but module-level call (line 86) initializes global STRATEGY_MANAGER on import.

**Impact:**
- Global state initialization at import time
- Inconsistent with lazy-loading architecture
- Parameter adds maintenance burden

**Recommendation:** Refactor to remove optional filepath parameter; remove module-level call

**Effort:** Medium

---

### CRITICAL: GameSession Legacy Parameters Bypass Config
**ID:** LDF-02
**Location:** `game/strategy/engine/game_session.py:60-69`
**Issue:** `galaxy_radius` and `system_count` parameters override config values, creating dual code paths. Used extensively in tests (5+ test files).

**Impact:**
- Config immutability violated post-construction
- Tests cannot migrate to config-only without refactoring 10+ files
- Source of truth unclear

**Recommendation:** Deprecate parameters; require configured GameConfig. Create factory method if quick initialization needed.

**Effort:** Complex (affects 10+ test files)

---

### MAJOR: Legacy CrewCapacity Fallback Logic
**ID:** LDF-03
**Location:** `game/ui/screens/builder/stats_config.py:62-92, 318-322`
**Issue:** Pattern `abs(min(0, ship.get_ability_total('CrewCapacity')))` repeated 3 times. Treats negative CrewCapacity as legacy crew requirements with unclear semantics.

**Impact:**
- DRY violation (3 occurrences)
- Semantically confusing
- Bug risk from duplication

**Recommendation:** Extract to named function; document why negative values exist; migrate to CrewRequired ability

**Effort:** Medium

---

### MAJOR: Design Metadata Dual Format Support
**ID:** LDF-04
**Location:** `game/strategy/data/design_metadata.py:150-212`
**Issue:** Supports both old `{"components": [...]}` dict and new list format with silent fallback to empty list.

**Impact:**
- Silent data loss if old format encountered
- No validation warnings
- Migration status unclear

**Recommendation:** Verify no old-format designs remain; remove fallback logic; add error for old format

**Effort:** Simple

---

### MINOR: Legacy Resource Properties in Renderer
**ID:** LDF-05
**Location:** `game/ui/renderer/renderer.py:177-184`
**Issue:** Directly accesses `ship.current_fuel`, `ship.max_fuel`, etc. instead of using ResourceRegistry.

**Impact:** Potential AttributeError if properties missing; code duplication

**Recommendation:** Add compatibility layer with @property mappings; update renderer long-term

**Effort:** Simple

---

## Top 5 Priority Issues

1. **LDF-02: GameSession legacy parameters** - CRITICAL, affects 10+ test files
2. **LDF-01: load_combat_strategies() side effects** - CRITICAL, global state
3. **LDF-03: CrewCapacity fallback** - MAJOR, DRY violation
4. **LDF-04: Design metadata format** - MAJOR, silent fallback
5. **LDF-05: Renderer properties** - MINOR, potential crashes

## Recommended Cleanup Order

1. Phase 1: LDF-04 (verify, remove fallback)
2. Phase 2: LDF-05 (compatibility layer)
3. Phase 3: LDF-03 (refactor validation)
4. Phase 4: LDF-01 (remove filepath parameter)
5. Phase 5: LDF-02 (ongoing test migration)
