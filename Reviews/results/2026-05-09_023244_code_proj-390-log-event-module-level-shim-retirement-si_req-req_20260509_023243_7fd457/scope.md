# Review Scope: PROJ-390 — log_event Module-Level Shim Retirement

**Type:** code (delegated by Claude Code)
**Request ID:** req_20260509_023243_7fd457
**Review directory:** `Reviews/results/2026-05-09_023244_code_proj-390-log-event-module-level-shim-retirement-si_req-req_20260509_023243_7fd457/`
**Checkout SHA:** b2ffda5c5 (single commit)

**Scope:**
- `game/core/event_logging.py` — module-level `log_event()`, `set_event_handler()`, `get_event_handler()` + `_event_handler` global DELETED
- `game/core/__init__.py` — re-exports stripped, `__all__` updated
- `game/simulation/entities/projectile.py` — `_default_event_logger` rewritten as no-op
- `conftest.py` — cleanup hook for deleted global removed
- `tests/unit/core/event_logging/test_event_logging.py` — DELETED
- `docs/02_PATTERNS.md` §10 — retirement note replacing compat-shim sentence

**Instructions:**
1. Final grep verification (3 grep patterns → must be zero hits)
2. Verify PROJ-382 'already-done' claim (empire.py, fleet.py, conflict_resolution_engine.py)
3. Verify architectural decision (EventBus session-scoped, NOT on ApplicationContext)
4. Verify projectile.py `_default_event_logger` no-op semantics
5. Verify conftest.py cleanup hook removal
6. Verify deleted test file covered only deprecated shim
7. Verify docs/02_PATTERNS.md §10 update

**Context:** Ninth of 11 sequential PROJ runs. Stage 3 second project. PROJ-382 had already migrated 9-10 callers; this commit finishes the last one.
