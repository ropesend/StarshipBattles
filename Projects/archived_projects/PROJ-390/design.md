# PROJ-390: Design Document

## Source Audit

This project was created from the legacy-audit at `Reviews/results/2026-05-07_220621_legacy-audit/`.

- **Audit verified:** 32 items overall (across 11 sibling projects)
- **This bundle:** 1 verified (2 IDs, dedup'd to 1 finding), 0 uncertain, 0 INFO, 0 deferred
- **Project siblings:** PROJ-383..PROJ-389, PROJ-391..PROJ-393

## Cluster Identity

**Removal cluster:** `log_event` module-level compat shim. Process-global `_event_handler` plus three module-level functions (`log_event`, `set_event_handler`, `get_event_handler`) bypass session-scoped isolation. The pattern doc itself (`docs/02_PATTERNS.md` §10) tags these as a "compatibility shim" — this is a self-documented violation that nobody got around to removing.

LEG-02-016 (Shard 02) and LEG-03-021 (Shard 03) are the same finding from two shards' perspectives. Treated as one item.

## Severity Breakdown

| Severity | Count |
|----------|-------|
| MAJOR | 1 (LEG-02-016 / LEG-03-021 dedup) |

## Risk Notes

- The module-level API is also a `state-audit` concern (process-global mutable state). After this project, no global remains.
- The migration is invasive: ~12 callers across `game/` plus an unknown number of test sites. Threading `ctx.event_bus` through call paths is the bulk of the work, not the deletion itself.
- A separate concern (`policy_manager` and `registry.py` module-level singletons, LEG-04-014/LEG-04-015) was deferred by the user as out-of-scope — that remains a future project.

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.
