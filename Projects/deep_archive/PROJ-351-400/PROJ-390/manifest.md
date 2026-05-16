# PROJ-390 File Manifest

## Files

| File | Type | Action | Notes |
|------|------|--------|-------|
| `game/core/event_logging.py` | Production | Edit | LEG-02-016 / LEG-03-021 — delete module-level `log_event`, `set_event_handler`, `get_event_handler`, and `_event_handler` global at lines 57-88 |
| `game/context.py` | Production | Edit | Confirm/add `EventBus` accessor on `ApplicationContext` (Pattern 1) |
| `game/` (~12 caller sites) | Production | Migrate-callers | Enumerated in Task 1.1; each replaces module-level call with `ctx.event_bus.log(...)` |
| `tests/` | Test | Migrate-callers | Replace module-level imports with fixture-injected `EventBus` |
| `docs/02_PATTERNS.md` | Doc | Edit | Update §10 — remove "compatibility shim" tag |
