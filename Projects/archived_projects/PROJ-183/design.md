# PROJ-183: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

Independent 7-agent audit swarm of PROJ-175 (Logger & JSON Loading Pattern Standardization) revealed that the core migration was thorough but left several secondary issues:

### What PROJ-175 Got Right
- Old `game/core/logger.py` completely eradicated (zero imports, file deleted)
- 134/135 files in `game/` use standard `logging.getLogger(__name__)` at module level
- All `json.load/dump` file I/O in `game/` uses centralized `json_utils.py`
- Event logging cleanly extracted to `game/core/event_logging.py` (58 lines, 31 tests)
- Root logger configuration in `game/app.py` is correct
- Test isolation via NullHandler in conftest.py works for the "game" namespace

### What PROJ-175 Missed
1. **strategy_renderer.py** has inline `import logging` + inline `logging.getLogger(__name__).warning(...)` inside `_draw_fleets()` - should use module-level logger
2. **7 files** use `import traceback` + `traceback.format_exc()` instead of `logger.exception()` - the standard pattern that auto-captures traceback
3. **3 files** log errors/failures at INFO level instead of WARNING

## Swarm Findings Summary

### Architecture
All changes are mechanical, leaf-node modifications. No architectural concerns.

### Key Patterns to Reuse
- **logger.exception()**: `game/core/json_utils.py:72` - proper exception logging with auto-traceback capture. This is the pattern to follow when replacing `traceback.format_exc()`.

### Dependencies & Risks
1. **LOW** - `logger.exception()` includes full traceback automatically. Some existing code includes both `{e}` and `{traceback.format_exc()}` - replacing with `logger.exception(f"message: {e}")` will produce slightly different output format (traceback on separate lines rather than inline) but captures the same information.

### Opportunities Discovered
- None beyond the stated scope. The PROJ-175 migration was otherwise well-executed.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
