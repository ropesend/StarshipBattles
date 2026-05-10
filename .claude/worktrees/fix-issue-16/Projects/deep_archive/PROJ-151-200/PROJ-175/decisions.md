# PROJ-175 Decision Log

## DEC-001: Migrate to Standard Logging (Option B)
**Date:** 2026-02-23 (updated)
**Status:** Accepted (supersedes prior Option C decision)
**Context:** Three options evaluated:
- (A) Migrate to `logging.getLogger(__name__)` — delete custom Logger
- (B) Keep custom Logger as-is — live with bugs
- (C) Modernize custom Logger — fix bugs, keep API

**Decision:** Option A — Migrate to standard logging.

**Rationale (from Consistency Review 2026-02-23_195305):**
- Custom Logger provides only one unique feature: event handler system (~25 lines)
- It introduces 2 critical bugs (import-time side effects, global state without lifecycle)
- 114 files are coupled to a non-standard API for minimal benefit
- Standard logging is thread-safe, has no import-time side effects, and is universally understood
- The event handler system can be preserved in a separate `game/core/event_logging.py` module
- Option C (prior decision) would fix bugs but perpetuate non-standard API coupling

**Consequences:**
- 114 files need mechanical migration (search-and-replace per file)
- `game/core/logger.py` deleted after migration
- `game/core/event_logging.py` created with event handler system
- Root logger configured in `app.py` and `conftest.py`

## DEC-002: Extract Event Handler to Separate Module
**Date:** 2026-02-23
**Status:** Accepted
**Context:** The event handler system (`log_event()`, `set_event_handler()`) is used by simulation/test infrastructure for structured event callbacks. This is the only feature not available in standard logging.
**Decision:** Create `game/core/event_logging.py` with the event handler functions.
**Rationale:** Clean separation of concerns — logging (standard library) vs. structured events (custom module). The event system is ~30 lines and has no dependency on the Logger class.
**Consequences:** Files importing `log_event`/`set_event_handler` will import from `game.core.event_logging` instead of `game.core.logger`.

## DEC-003: JSON Direct Calls — Migrate All File I/O
**Date:** 2026-02-23
**Status:** Accepted
**Context:** Only 3 file I/O calls bypass `json_utils`. Additionally, 2 files import `json` solely for `json.JSONDecodeError` exception reference.
**Decision:** Migrate all 3 file I/O calls to use `json_utils`. Clean up 2 exception-only imports.
**Rationale:** Consistency. json_utils provides error handling and logging that direct calls lack.
**Consequences:** Removes direct `json.load/dump` file I/O from game/ (except json_utils itself).

## DEC-004: No BaseJSONLoader Class
**Date:** 2026-02-23
**Status:** Accepted
**Context:** PC-015 found 9 loaders with duplicate file I/O. Loader Class Analyst evaluated BaseJSONLoader vs. "just use json_utils" vs. shared utility functions.
**Decision:** Do NOT create BaseJSONLoader. Loaders already use json_utils (9 of 11). The variation is in post-processing, not file I/O.
**Rationale:** A base class would need so many extension points it adds complexity without reducing code. Shared utility functions (file discovery, schema validation) could be extracted as future work.
**Consequences:** WorkshopDataLoader migrated to json_utils for I/O. No new base class.

## DEC-005: Tighten json_utils Exception Handling
**Date:** 2026-02-23
**Status:** Accepted
**Context:** MOD-CORE-015 found `IOError` catch is too broad in json_utils.
**Decision:** Split `IOError` into `FileNotFoundError` (already separate), `PermissionError`, and `OSError`.
**Rationale:** More specific exceptions improve debugging and error messages.
**Consequences:** Minor change to json_utils.py error handling.
