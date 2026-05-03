# Migration Planner Report (Inconsistency Hunter)

## Summary
- Total inconsistencies identified: 15 (from 4 agent reports)
- Recommended phases: 4
- Total estimated files to modify: 119 (Option B) or 7 (Option A)
- Quick wins (< 2 hours): JSON standardization (5 files)
- Major decisions needed: Logger migration path (Option A: fix bugs vs Option B: migrate to stdlib)

## Executive Summary

**Overall Consistency Assessment:**
- JSON operations: **95% standardized** — only 3 file I/O calls + 2 exception imports remain
- Logger usage: **Fragmented** — 114 custom, 6 standard, 4 dual usage
- Loaders: **Well-aligned** — 9 of 11 use json_utils

**Recommended Strategy: Option B (Migrate to standard logging)**
Custom Logger provides minimal value over stdlib (only unique feature: event handler system, which can be extracted). Critical flaws in test isolation and resource management make it more liability than asset.

## Migration Plan

### Phase 1: JSON Quick Wins (1-2 hours, LOW risk)

| # | File | Change | Difficulty |
|---|------|--------|-----------|
| 1 | `game/ui/screens/formation_editor.py` | Replace `json.dump()` → `save_json()`, `json.load()` → `load_json_required()` | Easy |
| 2 | `game/ui/screens/builder/stats_config.py` | Replace `json.load()` → `load_json(path, default={})` | Easy |
| 3 | `game/strategy/systems/save_game_service.py` | Change `import json` → `from json import JSONDecodeError` | Trivial |
| 4 | `game/strategy/systems/design_library.py` | Change `import json` → `from json import JSONDecodeError` | Trivial |
| 5 | `game/ui/screens/workshop_data_loader.py` | Migrate file I/O calls to json_utils | Medium |

**Success:** Zero direct json.load/dump for file I/O in game/. All tests pass.

### Phase 2: Logger Architecture Decision (0 hours — planning only)

**Option A: Fix Custom Logger** — 6-8 hours, 2 files, keeps custom pattern forever
**Option B: Migrate to Standard Logging** — 10-14 hours, 114+ files, eliminates custom code

**Recommendation:** Option B. Custom Logger is thin wrapper with critical flaws. Event handler system (~30 lines) is only unique feature and can be extracted.

### Phase 3b: Logger Migration (10-14 hours, MEDIUM-HIGH risk)

| Sub-phase | Description | Files | Hours |
|-----------|-------------|-------|-------|
| B1 | Extract event handler → `game/core/event_logging.py` | 1 new + 2 updates | 2-3 |
| B2 | Migrate core module (6 files) | 6 | 2-3 |
| B3 | Migrate simulation module (12 files) | 12 | 2-3 |
| B4 | Migrate strategy module (38 files) | 38 | 2-3 |
| B5 | Migrate AI (3) + UI (43) + other (4) | 50 | 1-2 |
| B6 | Configure root logger in conftest.py + app.py | 2 | 1 |
| B7 | Delete game/core/logger.py | 1 | 1 |
| B8 | Testing and verification | 0 | 1-2 |

**Per-file pattern (mechanical):**
```python
# BEFORE
from game.core.logger import log_info, log_error, log_warning

# AFTER
import logging
logger = logging.getLogger(__name__)
# log_info("msg") → logger.info("msg")
# log_error("msg") → logger.error("msg")
# log_warning("msg") → logger.warning("msg")
```

### Phase 4: Guardrails & Documentation (2-3 hours)

1. Create `docs/LOGGING_GUIDELINES.md` — when to use each log level, event system
2. Add linting rules to prevent regression (ban old imports, ban direct json file I/O)
3. Update `docs/ERROR_HANDLING_GUIDELINES.md` with logging cross-references

## Risk Assessment

| Phase | Risk | Mitigation |
|-------|------|------------|
| 1 (JSON) | LOW | Small scope, all UI layer, easy rollback |
| 2 (Decision) | NONE | Planning only |
| 3b (Logger) | MEDIUM-HIGH | Mechanical replacement, full test suite verification, incremental sub-phases |
| 4 (Guardrails) | LOW | Documentation and linting only |

**Highest-risk files:**
- `game/core/logger.py` deletion (ensure nothing references it)
- `conftest.py` root logger configuration (affects all tests globally)
- Event logging module (new code path for system events)

## Dependencies

- Phase 1 (JSON) is **independent** — can start immediately
- Phase 3 depends on Phase 2 decision
- Phase 4 can start after Phase 1 for JSON portion; logger portion depends on Phase 3

## Total Effort Estimate

| Path | Duration | Files Modified |
|------|----------|---------------|
| **Option A (Fix Logger)** | 9-13 hours | ~7 files |
| **Option B (Migrate Logger)** | 13-19 hours | ~119 files |

**Recommendation:** Option B — higher upfront cost but eliminates ongoing maintenance burden of custom logging system.
