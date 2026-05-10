# Consistency Review Report: Logger & JSON Pattern Standardization

## Metadata
- **Date:** 2026-02-23
- **Type:** Consistency Review
- **Scope:** `game/` directory (~370 files, ~96K lines)
- **Agents Used:** 5 (Logger Analyst, Logger Census, JSON Census, Loader Class Analyst, Migration Planner)

## Executive Summary

- **Total Findings:** 15
- **Critical:** 2 | **Major:** 5 | **Minor:** 5 | **Info:** 3
- **Overall Consistency:** JSON = 95% (excellent), Logger = Fragmented (3 competing patterns)
- **Top Recommendation:** Migrate to standard Python logging; complete JSON standardization

### Key Numbers

| Metric | Value |
|--------|-------|
| Files using custom Logger | 114 |
| Files using standard logging | 6 |
| Files with dual logging usage | 4 |
| Custom logger calls | ~849 |
| JSON file I/O calls via json_utils | 51 |
| JSON file I/O calls bypassing json_utils | 3 |
| Legitimate direct json (string ops) | 17 |
| Loader classes identified | 12 |
| Loaders using json_utils | 9 |

---

## Priority Findings (Top 10)

### 1. CRITICAL: Logger Import-Time Side Effects
**ID:** LOG-001
**Agent:** Logger Analyst
**Location:** `game/core/logger.py:27-41`
**Issue:** `Logger.__init__()` calls `setup()` which creates directories and opens file handlers on first import. Creates files on disk during test collection.
**Impact:** Tests in headless/CI fail unexpectedly. File handles accumulate. `Paths.BATTLE_LOG` must be writable at import time.
**Recommendation:** Defer file handler creation to explicit initialization. Make file logging optional.
**Effort:** Medium

### 2. CRITICAL: Module-Level Global State Without Lifecycle Management
**ID:** LOG-002
**Agent:** Logger Analyst
**Location:** `game/core/logger.py:87-92`
**Issue:** `_event_handler` global persists independently of Logger singleton. Never auto-resets. Requires explicit cleanup in conftest.py.
**Impact:** Test pollution — handler from one test leaks into another. No guaranteed cleanup.
**Recommendation:** Make event handler instance-scoped, or extract to separate module with proper lifecycle.
**Effort:** Medium

### 3. MAJOR: Three Competing Logger Patterns
**ID:** LC-001
**Agent:** Logger Census
**Location:** Across 120 files in `game/`
**Issue:** 114 files use custom Logger, 6 use standard `logging`, 4 use both. No documented decision.
**Impact:** Developers don't know which pattern to follow. Inconsistent evolution.
**Recommendation:** Standardize on one pattern. Option B (standard logging) recommended.
**Effort:** Complex (114 files to migrate)

### 4. MAJOR: No Resource Cleanup on Logger Reset
**ID:** LOG-003
**Agent:** Logger Analyst
**Location:** `game/core/logger.py:9-41`
**Issue:** FileHandler is never stored, never closed, never removed. After multiple resets in tests, Python logger accumulates duplicate handlers.
**Impact:** Resource leak, log duplication, memory leak, broken test isolation.
**Recommendation:** Store handler, add `cleanup()` method.
**Effort:** Simple

### 5. MAJOR: File Handler Never Closed
**ID:** LOG-004
**Agent:** Logger Analyst
**Location:** `game/core/logger.py:37-41`
**Issue:** FileHandler is a local variable — never stored, never closed. On Windows, open handles prevent file deletion.
**Impact:** File handle resource leak. Log file not flushed on crash.
**Recommendation:** Store as instance variable, close in cleanup.
**Effort:** Simple

### 6. MAJOR: Path Resolution Duplication Across Loaders
**ID:** LDR-001
**Agent:** Loader Class Analyst
**Location:** Multiple loaders in `game/strategy/generation/loaders/`, `game/simulation/services/`
**Issue:** 3+ loaders implement their own path resolution logic independently.
**Impact:** Inconsistent path handling, duplicated code.
**Recommendation:** Extract shared `resolve_path()` utility.
**Effort:** Medium

### 7. MAJOR: File Discovery Pattern Duplication
**ID:** LDR-002
**Agent:** Loader Class Analyst
**Location:** `workshop_data_loader.py`, `registry_loader.py`, `tech_preset_loader.py`
**Issue:** 3 loaders implement `test_` prefix fallback file discovery independently (~90 lines total).
**Impact:** Duplicated logic, risk of divergent behavior.
**Recommendation:** Extract shared `find_file_with_test_prefix()` utility.
**Effort:** Medium

### 8. MINOR: Event Handler Persists Across Test Boundaries
**ID:** LOG-005
**Agent:** Logger Analyst
**Location:** `game/core/logger.py:87-108`, `conftest.py:92-97`
**Issue:** `_event_handler` requires explicit reset in conftest — a signal the pattern is broken.
**Impact:** Fragile, fixture-order-dependent test cleanup.
**Recommendation:** Make event handler instance-scoped (see LOG-002).
**Effort:** Medium

### 9. MINOR: Dual Usage Files Indicate Incomplete Migration
**ID:** LC-002
**Agent:** Logger Census
**Location:** `game/ai/controller.py`, `game/ai/combat_utils.py`, `game/simulation/components/modifier_effects.py`, `game/simulation/components/modifiers.py`
**Issue:** 4 files have BOTH `logging.getLogger(__name__)` AND custom logger imports.
**Impact:** Confusion about which logger is active. Possible double-logging.
**Recommendation:** Resolve to one pattern per file.
**Effort:** Simple

### 10. MINOR: 3 File I/O Calls Bypass json_utils
**ID:** JC-001
**Agent:** JSON Census
**Location:** `game/ui/screens/formation_editor.py`, `game/ui/screens/builder/stats_config.py`
**Issue:** 3 file-based JSON operations use direct `json.load()`/`json.dump()` instead of json_utils.
**Impact:** Inconsistent error handling. Missing logging on load failures.
**Recommendation:** Migrate to `load_json()`/`save_json()`.
**Effort:** Simple

---

## All Findings by Severity

### Critical (2)
| ID | Title | Location | Agent | Effort |
|----|-------|----------|-------|--------|
| LOG-001 | Import-time side effects | `game/core/logger.py:27-41` | Logger Analyst | Medium |
| LOG-002 | Global state without lifecycle | `game/core/logger.py:87-92` | Logger Analyst | Medium |

### Major (5)
| ID | Title | Location | Agent | Effort |
|----|-------|----------|-------|--------|
| LC-001 | Three competing logger patterns | 120 files | Logger Census | Complex |
| LOG-003 | No resource cleanup on reset | `game/core/logger.py` | Logger Analyst | Simple |
| LOG-004 | File handler never closed | `game/core/logger.py:37-41` | Logger Analyst | Simple |
| LDR-001 | Path resolution duplication | Multiple loaders | Loader Analyst | Medium |
| LDR-002 | File discovery duplication | 3 loaders | Loader Analyst | Medium |

### Minor (5)
| ID | Title | Location | Agent | Effort |
|----|-------|----------|-------|--------|
| LOG-005 | Event handler persists across tests | `logger.py` + `conftest.py` | Logger Analyst | Medium |
| LC-002 | Dual usage files (incomplete migration) | 4 files | Logger Census | Simple |
| JC-001 | 3 file I/O calls bypass json_utils | 2 files | JSON Census | Simple |
| JC-003 | json import for exception type only | 2 files | JSON Census | Simple |
| LDR-003 | Schema validation duplication | 5+ loaders | Loader Analyst | Simple |

### Info (3)
| ID | Title | Location | Agent | Effort |
|----|-------|----------|-------|--------|
| LOG-006 | Custom Logger is thin wrapper | `game/core/logger.py` | Logger Analyst | Info |
| LOG-007 | Insufficient error handling in event handler | `game/core/logger.py:104-108` | Logger Analyst | Simple |
| JC-002 | json_utils adoption is 95% complete | Codebase-wide | JSON Census | N/A |
| LDR-004 | WorkshopDataLoader bypasses json_utils | `workshop_data_loader.py` | Loader Analyst | Medium |
| LDR-005 | Inconsistent return types across loaders | All loaders | Loader Analyst | Simple |

---

## Pattern Inventory

### Logging Patterns

| Pattern | File Count | Call Count | Percentage |
|---------|-----------|------------|-----------|
| Custom Logger (log_info, log_error, etc.) | 114 | ~849 | 95% of logged files |
| Standard logging (logging.getLogger) | 6 | ~4 | 5% of logged files |
| Dual usage (both) | 4 | ~15 | 3% overlap |
| No logging | 253 | N/A | 69% of all files |

**Recommended Standard:** `logging.getLogger(__name__)` (Python standard library)

### JSON Patterns

| Pattern | File Count | Call Count | Percentage |
|---------|-----------|------------|-----------|
| json_utils.load_json | 13 | 27 | |
| json_utils.load_json_required | 11 | 15 | |
| json_utils.save_json | 6 | 9 | |
| **json_utils total** | **~29** | **51** | **94% of file I/O** |
| Direct json (file I/O) | 2 | 3 | **6% — MIGRATE** |
| Direct json (string ops) | 5 | 17 | Legitimate |

**Recommended Standard:** `game.core.json_utils` for all file I/O. Direct `json.dumps()`/`json.loads()` acceptable for string serialization.

---

## Recommended Migration Plan

### Phase 1: JSON Quick Wins (1-2 hours, LOW risk)

| File | Change |
|------|--------|
| `formation_editor.py` | `json.dump()` → `save_json()`, `json.load()` → `load_json_required()` |
| `builder/stats_config.py` | `json.load()` → `load_json(path, default={})` |
| `save_game_service.py` | `import json` → `from json import JSONDecodeError` |
| `design_library.py` | `import json` → `from json import JSONDecodeError` |
| `workshop_data_loader.py` | Migrate file I/O to json_utils |

### Phase 2: Logger Architecture Decision

**Option A: Fix Custom Logger** — 6-8 hours, 2 files modified
- Fix LOG-001 through LOG-007
- Keep 114-file dependency on custom API
- Long-term cost: maintaining custom logging forever

**Option B: Migrate to Standard Logging** (RECOMMENDED) — 10-14 hours, 114+ files
- Extract event handler → `game/core/event_logging.py`
- Replace `from game.core.logger import log_info` → `import logging; logger = logging.getLogger(__name__)`
- Delete `game/core/logger.py`
- All 7 Logger issues resolved by elimination

### Phase 3: Logger Migration (grouped by module)

| Sub-phase | Files | Hours |
|-----------|-------|-------|
| Extract event handler system | 3 | 2-3 |
| Migrate core/ (6 files) | 6 | 2-3 |
| Migrate simulation/ (12 files) | 12 | 2-3 |
| Migrate strategy/ (38 files) | 38 | 2-3 |
| Migrate AI (3) + UI (43) + other (4) | 50 | 1-2 |
| Configure root logger + delete old | 3 | 2 |
| Testing & verification | — | 1-2 |

### Phase 4: Guardrails (2-3 hours)

- Create `docs/LOGGING_GUIDELINES.md`
- Add linting rules (ban old imports, ban direct json file I/O)
- Update `docs/ERROR_HANDLING_GUIDELINES.md`

### Total Effort

| Path | Duration | Files |
|------|----------|-------|
| Option A (fix Logger) | 9-13 hours | ~7 |
| **Option B (migrate to stdlib)** | **13-19 hours** | **~119** |

---

## Agent Reports

- [Logger Analyst Report](findings/logger_analyst_report.md) — Deep analysis of custom Logger (7 findings)
- [Logger Census Report](findings/logger_census_report.md) — Complete 368-file inventory (3 findings)
- [JSON Census Report](findings/json_census_report.md) — Complete JSON operation inventory (3 findings)
- [Loader Class Analyst Report](findings/loader_analyst_report.md) — Analysis of 12 loader classes (5 findings)
- [Migration Planner Report](findings/migration_planner_report.md) — Synthesized migration plan

---

*Report compiled: 2026-02-23*
