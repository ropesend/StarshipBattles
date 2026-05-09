# Review Report: PROJ-390 — log_event Module-Level Shim Retirement

**Request ID:** req_20260509_023243_7fd457
**Review Type:** code (single-commit verification)
**Checkout SHA:** b2ffda5c5

**Report generated:** 2026-05-09T02:34:00Z
**Reviewer:** OpenCode (ocode-review-request)

---

## Summary

**Result: PASS — Retirement is total. All 7 verification items pass with zero findings at CRITICAL/MAJOR/MINOR severity.**

The commit `b2ffda5c5` correctly deletes the module-level `log_event()`, `set_event_handler()`, `get_event_handler()`, and `_event_handler` global from `game/core/event_logging.py`. The only remaining caller (projectile.py `_default_event_logger`) was correctly rewritten as a no-op. All 14 production import sites now import only `EventBus`. The conftest.py cleanup hook was removed. The deleted test file covered only the deprecated shim. The docs accurately reflect the retirement.

The architectural decision to keep EventBus session-scoped (NOT on ApplicationContext) is correct per PROJ-252's original design. Adding it to the process-scoped ApplicationContext would reintroduce the isolation problem this retirement fixes.

---

## Verification Matrix

| # | Verification Item | Status | Notes |
|---|---|---|---|
| 1 | Final grep verification (3 patterns) | PASS | Zero live references to deleted symbols. All current imports are `EventBus` only. |
| 2 | PROJ-382 'already-done' claim | PASS | empire.py, fleet.py, conflict_resolution_engine.py all use injected `event_bus`. No shim imports. |
| 3 | EventBus session-scoped decision | PASS | `GameSession` constructs its own bus (line 88). `ApplicationContext` has no EventBus reference. PROJ-252 design confirms. |
| 4 | projectile.py `_default_event_logger` no-op | PASS | No-op semantics correct. Injected `event_logger=` path exists for callers needing telemetry. 226 projectile tests pass. |
| 5 | conftest.py cleanup hook removal | PASS | Hook deleted. Replacement comment documents retirement rationale. No dangling references. |
| 6 | Deleted test file coverage | PASS | All 8 tests exercised only `log_event`/`set_event_handler`/`get_event_handler`. EventBus covered separately in `test_event_bus.py`. |
| 7 | docs/02_PATTERNS.md §10 update | PASS | Compat-shim sentence removed. Constructor injection documented as only supported pattern. "No fallback path" noted. |

---

## Detailed Findings

See `findings/verification_report.md` for full per-item analysis with code citations.

### Finding Highlights

**Item 1 — Grep verification:**
- `git grep -E 'from game\.core\.event_logging import (log_event|set_event_handler|get_event_handler)' game/ tests/ combat_lab/ Tools/` → **ZERO hits**
- `git grep '_event_handler' game/ tests/ combat_lab/ Tools/` → matches only `GameSession._create_event_handler()` (a different method) and documentation comments. The module-level `_event_handler` global is fully deleted.
- `git grep 'event_logging\.log_event' game/ tests/` → **ZERO hits**

**Item 2 — PROJ-382 migration:**
All 9-10 claimed migration sites confirmed. Each uses `event_bus.log_event(...)` through constructor/kwarg-injected EventBus. No site imports or references the deleted shim functions.

**Item 3 — Session scope:**
`GameSession.__init__` constructs `self._event_bus = EventBus(self._create_event_handler())`. The bus is passed to `TurnEngineConfig.create_default(event_bus=...)` which threads it to all sub-engines. `ApplicationContext` has zero references to EventBus. Placing EventBus on ApplicationContext would make it process-scoped, breaking session isolation — the exact problem PROJ-252 and PROJ-390 exist to fix.

---

## Findings Count

| Severity | Count |
|---|---|
| CRITICAL | 0 |
| MAJOR | 0 |
| MINOR | 0 |
| INFO | 7 (verification passes) |

---

## Limitations

- The PROJ-252 archived design (`Projects/deep_archive/PROJ-251-300/PROJ-252/decisions.md`) confirms EventBus session-scoping was the original intent; the decisions log explicitly notes `log_event()` was kept as a "deprecated convenience during migration" — this validates the retirement.
- No test suite re-run was performed (trusting the commit message report of 9671 passed, 1 skipped, 1 pre-existing failure).
- The grep for `_event_handler` matches `_create_event_handler()` as a false positive; this is a substring collision on a legitimate method name, not a reference to the deleted global.
