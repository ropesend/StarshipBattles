# PROJ-175: Logger & JSON Loading Pattern Standardization

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-175` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-175 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. JSON Quick Wins | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Logger Core Migration (event system + core + simulation) | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Logger Remaining Migration (strategy + AI + UI + other) | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Guardrails & Documentation | Complete | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-02-23
**Active Phase:** PROJECT COMPLETE
**Last Action:** Completed Phase 4 - Updated ERROR_HANDLING_GUIDELINES.md with standard logging patterns, documented event_logging.py and json_utils.py, ran all verification checks.
**Next Action:** AUDIT (trigger Protocol 04)
**Blockers:** None
**Context for Next Agent:** All 4 phases complete. Project ready for audit. Logger migration COMPLETE. Old logger.py eradicated. 123 files use standard logging.getLogger(__name__). Event logging in game/core/event_logging.py. json_utils.py is canonical JSON utility. Test baseline: 11968 passed, 1 skipped.

## Overview
Standardize logging and JSON loading patterns across the codebase by migrating from the custom Logger singleton to Python's standard `logging` module, and completing the JSON utilities standardization.

Currently:
- **114 files** import from custom `game.core.logger` (~849 log calls)
- **6 files** use standard `logging.getLogger(__name__)`
- **4 files** use both (dual usage from incomplete migration)
- **3 file I/O calls** bypass `json_utils` (+ 2 exception-only imports)

## Goals
- ONE logging pattern (`logging.getLogger(__name__)`) used across all of `game/`
- Event handler system preserved in `game/core/event_logging.py`
- Custom `game/core/logger.py` DELETED
- ZERO direct `json.load/dump` file I/O calls outside `json_utils.py`
- Test isolation clean (no Logger state bleed)
- Logging level guidelines documented

## Scope
**In:**
- `game/core/logger.py` — DELETE entirely after migration
- `game/core/event_logging.py` — CREATE (extract event handler system)
- 114 files importing from `game.core.logger` — migrate to `logging.getLogger(__name__)`
- 6 files using standard `logging` — keep, remove any dual-usage custom imports
- 2 files using direct `json.load/dump` — migrate to `json_utils`
- 2 files importing `json` for exception type only — clean up
- 1 file (WorkshopDataLoader) bypassing json_utils — migrate
- `conftest.py` — configure root logger, clean up Logger fixture
- `game/app.py` — configure root logger for app startup
- `docs/ERROR_HANDLING_GUIDELINES.md` — add logging level guidelines

**Out:**
- `tests/` and `simulation_tests/` logging patterns (test lab logger is separate)
- Error handling patterns beyond logging (separate PROJ-170)
- BaseJSONLoader class (not warranted per review)

## Key Files
| Component | File Path | Action |
|-----------|-----------|--------|
| Custom Logger | `game/core/logger.py` (109 lines) | DELETE |
| Event logging | `game/core/event_logging.py` | CREATE (~40 lines) |
| JSON utilities | `game/core/json_utils.py` (144 lines) | Tighten error handling |
| App entry point | `game/app.py` | Add root logger configuration |
| Test config | `conftest.py` | Update logger fixture |
| Error handling guide | `docs/ERROR_HANDLING_GUIDELINES.md` | Add logging guidelines |

## Source Review
**Review:** [Consistency Review: Logger & JSON Pattern Standardization](../../Reviews/results/2026-02-23_195305_consistency_logger-json-pattern-standardization/report.md)

**Findings (15 total — 2 Critical, 5 Major, 5 Minor, 3 Info):**
| ID | Agent | Severity | Summary |
|----|-------|----------|---------|
| LOG-001 | Logger Analyst | Critical | Import-time side effects (creates files on first import) |
| LOG-002 | Logger Analyst | Critical | Module-level _event_handler global without lifecycle |
| LOG-003 | Logger Analyst | Major | No resource cleanup on reset (handlers accumulate) |
| LOG-004 | Logger Analyst | Major | File handler never stored, never closed |
| LOG-005 | Logger Analyst | Minor | Event handler persists across test boundaries |
| LOG-006 | Logger Analyst | Minor | Custom Logger is thin wrapper, minimal value over stdlib |
| LOG-007 | Logger Analyst | Minor | Insufficient error handling in event handler |
| LC-001 | Logger Census | Major | Three competing logger patterns (114/6/4 files) |
| LC-002 | Logger Census | Minor | Dual usage files indicate incomplete migration |
| LC-003 | Logger Census | Minor | Event handler system may be unused/vestigial |
| JC-001 | JSON Census | Minor | 3 file I/O calls bypass json_utils |
| JC-002 | JSON Census | Info | json_utils adoption is 95% complete |
| JC-003 | JSON Census | Minor | json import for exception type reference only |
| LDR-001 | Loader Analyst | Major | Path resolution duplication across loaders |
| LDR-002 | Loader Analyst | Major | File discovery pattern duplication |

## Architecture Decision: Migrate to Standard Logging (Option B)

**Decision:** Replace custom Logger with Python standard `logging.getLogger(__name__)`. Extract event handler system to separate module.

**Rationale:** The custom Logger provides only one unique feature (event handler system, ~25 lines) while introducing import-time side effects, resource leaks, and broken test isolation across 114 files. Standard logging eliminates all these issues.

**Migration pattern (mechanical, per-file):**
```python
# BEFORE
from game.core.logger import log_info, log_error, log_warning, log_debug

# AFTER
import logging
logger = logging.getLogger(__name__)
# log_info("msg") → logger.info("msg")
```

## Risk Assessment
- **JSON migration: VERY LOW** — 5 files, mechanical replacement
- **Logger migration: MEDIUM** — 114 files, but mechanical (search-and-replace per file)
- **Event handler: LOW** — Small module (~40 lines), well-understood
- **Test risk: MEDIUM** — Root logger config in conftest affects all tests
- **Mitigation:** Incremental sub-phases with full test suite runs between modules

## Effort Estimate
| Phase | Duration | Files |
|-------|----------|-------|
| 1: JSON Quick Wins | 1-2 hours | 5 |
| 2: Logger Core Migration | 4-6 hours | ~25 |
| 3: Logger Remaining Migration | 4-6 hours | ~55 |
| 4: Guardrails & Documentation | 1-2 hours | ~5 |
| **Total** | **10-16 hours** | **~90** |
