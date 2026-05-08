# PROJ-390 — Verification Report

**Source audit:** `Reviews/results/2026-05-07_220621_legacy-audit/`
**Run date:** 2026-05-08
**Cluster:** `log_event` module-level compat shim retirement
**Batch summary:** 1 verified (dedup) / 0 rejected / 0 uncertain / 0 INFO / 2 out-of-scope (other singleton patterns)

## Verified

| ID | File | Symbol | Replaces | Call sites | Recommendation | Severity |
|---|---|---|---|---|---|---|
| LEG-02-016 / LEG-03-021 (dedup) | `game/core/event_logging.py:57-88` | module-level `log_event`, `set_event_handler`, `get_event_handler`, `_event_handler` global | injected `EventBus` (Pattern 1 / ApplicationContext) | ~12 prod | migrate_callers_then_delete | MAJOR |

## Rejected

None — Sonnet confirmed against current source. The pattern doc itself confesses to the shim status.

## Uncertain (resolved)

None for this bundle.

## INFO (resolved)

None for this bundle.

## Out of Scope

| ID | Reason |
|---|---|
| LEG-04-014 (`policy_manager` auto-create singleton) | User excluded during Phase D Step 4 — large scope, separate project. Same shape (module-level singleton) but different module. |
| LEG-04-015 (`registry.py` module-level singleton) | Same as LEG-04-014. |
