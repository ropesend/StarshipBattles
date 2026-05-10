# Logging Architecture Analysis Report

## Summary
- **Total issues found:** 10
- **Critical:** 1
- **Major:** 4
- **Minor:** 4
- **Info:** 1

---

## Findings

### CRITICAL: No Structured/Parseable Log Format for Machine Consumption
**ID:** LOG-01
**Location:** `game/core/logger.py:36-47`
**Issue:** The main Logger outputs plain text with format `%(asctime)s - %(levelname)s - %(message)s`. The message field is a free-form string. There is no structured logging format (JSON, key-value pairs, or tagged fields) that an agent can reliably parse. When `ScreenshotManager` logs `"Screenshot saved: {path}"`, the only way to extract the path is fragile string parsing.

Contrast with the simulation test framework which uses:
- JSONL format in `simulation_tests/output/combat_lab_test_log.jsonl`
- Pipe-delimited structured events in `tests/unit/simulation/test_logger.py`

The main game logger has none of this structure.
**Impact:** Agents cannot programmatically find screenshot entries in logs without brittle regex. A diagnostic screenshot system needs a reliable, parseable log format.
**Recommendation:** The diagnostic capture system should emit log entries with a fixed, parseable tag and key-value structure (e.g., `[DIAGNOSTIC_SCREENSHOT] reason="..." | screen="..." | path="..."`). This can be done within the existing string-based `log_info()` — no framework change needed.
**Effort:** Simple (design decision, not logger refactor)

### MAJOR: Single Event Handler Limitation
**ID:** LOG-02
**Location:** `game/core/logger.py:87-109`
**Issue:** The event logging system (`set_event_handler`/`log_event`) supports only one handler at a time. Setting a new handler replaces the previous one. If the diagnostic screenshot system wanted to use `log_event()` for structured events, it would conflict with any existing handler (e.g., simulation test logging).
**Impact:** Cannot use the event system for diagnostic screenshots without potentially breaking existing consumers.
**Recommendation:** Either:
(a) Don't use the event system — emit structured data via `log_info()` with a tagged format (simpler), or
(b) Upgrade to a handler registry (list of handlers) — but this is a broader change.
Option (a) is recommended for this integration.
**Effort:** N/A (design choice avoids the issue)

### MAJOR: battle.log Overwrites Each Session
**ID:** LOG-03
**Location:** `game/core/logger.py:43`
**Issue:** The FileHandler uses `mode='w'` (write), which overwrites `battle.log` every time the game starts. Diagnostic screenshot entries from a previous session are lost.
**Impact:** If an agent triggers diagnostic captures, restarts the game to verify a fix, and then wants to compare screenshots from both sessions, the first session's log entries are gone.
**Recommendation:** A dedicated diagnostic log file should use `mode='a'` (append) so entries persist across sessions. The main `battle.log` overwrite behavior is appropriate for its purpose (current session log) — but diagnostic data needs persistence.
**Effort:** Simple

### MAJOR: No Dedicated Diagnostic Log File
**ID:** LOG-04
**Location:** `game/core/paths.py:85-88`
**Issue:** The paths system defines `BATTLE_LOG`, `CRASH_LOG`, and `PROFILING_HISTORY`, but there is no path for a diagnostic screenshots log. For agents to efficiently find screenshot entries without scanning the entire `battle.log`, a dedicated log file is needed.
**Impact:** Without a dedicated file, agents must grep through a potentially large `battle.log` for `[DIAGNOSTIC_SCREENSHOT]` entries mixed with thousands of other log lines.
**Recommendation:** Add `DIAGNOSTIC_LOG` to `Paths` class pointing to `output/logs/diagnostic_screenshots.log`.
**Files Affected:** `game/core/paths.py`
**Effort:** Simple

### MAJOR: No Log Correlation Between Screenshot and Game State
**ID:** LOG-05
**Location:** `game/core/screenshot_manager.py:112`, `game/core/logger.py:49-63`
**Issue:** When a screenshot is saved, the log entry is simply `"Screenshot saved: {path}"`. There is no correlation to:
- Which screen/GameState was active
- What the user or agent was investigating
- Any bug ticket ID
- What rendered state the screenshot captured
- The frame number or tick count

The log entry is insufficient for an agent to understand what a screenshot shows without opening it.
**Impact:** Agents collecting diagnostic evidence cannot determine screenshot context from logs alone.
**Recommendation:** The diagnostic capture API should accept and log: `reason`, `screen_name`, `bug_id`, and optional `context` dict. These should appear in the log entry.
**Effort:** Medium (new API, not logger change)

### MINOR: Logger Has No Console Handler
**ID:** LOG-06
**Location:** `game/core/logger.py:36-47`
**Issue:** The main `Logger.setup()` only adds a `FileHandler`. There is no console/stream handler. Diagnostic events are invisible during interactive debugging sessions unless the agent reads the log file.
**Impact:** Minor — agents will read the log file anyway. But for interactive sessions, console visibility would be helpful.
**Recommendation:** Not required for this integration, but a future enhancement could add an optional console handler at INFO level.
**Effort:** Simple (future)

### MINOR: Event Handler Type Signature Is Loose
**ID:** LOG-07
**Location:** `game/core/logger.py:89`
**Issue:** `set_event_handler(handler: Optional[Callable[..., Any]])` accepts any callable with any signature. There's no protocol, interface, or documentation defining what arguments the handler should expect.
**Impact:** Minor for this integration since we're recommending not using the event system (LOG-02).
**Effort:** N/A

### MINOR: No Log Level Filtering at Runtime
**ID:** LOG-08
**Location:** `game/core/logger.py:65-66`
**Issue:** `set_enabled(enabled: bool)` is a binary on/off toggle. There's no way to change log level (e.g., set to WARNING to reduce noise while keeping diagnostic screenshot entries at INFO).
**Impact:** If the game is producing excessive DEBUG output, the diagnostic entries get buried. Not critical since the dedicated log file (LOG-04) addresses this.
**Effort:** Simple (future)

### MINOR: Profiling System Has Good Patterns to Follow
**ID:** LOG-09
**Location:** `game/core/profiling.py`
**Issue:** Not an issue — an observation. The Profiler singleton has a clean pattern with:
- Session IDs for correlation
- Metadata dict per record
- JSON persistence (`save_history`)
- Toggle (`start`/`stop`/`is_active`)
- Low overhead when disabled

The diagnostic screenshot system should follow similar patterns: session awareness, metadata, toggle, low overhead.
**Impact:** Positive — existing pattern to follow.
**Effort:** N/A (design guidance)

### INFO: Simulation Test Logging Has Structured Formats Worth Referencing
**ID:** LOG-10
**Location:**
- `tests/unit/simulation/test_logger.py` — Pipe-delimited event format
- `simulation_tests/logging_config.py` — Dual console+file output
- `simulation_tests/utils/test_log_analyzer.py` — JSONL parsing and comparison

**Issue:** Not an issue — these are reference implementations. The simulation test framework already solved structured logging for its domain. The diagnostic screenshot system should adopt similar patterns:
- Tagged prefix for grepping (`[DIAGNOSTIC_SCREENSHOT]` like `[TICK:N]`)
- Key-value pairs for parsing
- Dedicated log file for focused analysis
**Impact:** Positive reference material.
**Effort:** N/A
