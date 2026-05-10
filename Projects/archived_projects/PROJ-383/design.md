# PROJ-383: Design Document

## Source Audit

This project was created from the legacy-audit at `Reviews/results/2026-05-07_220621_legacy-audit/`.

- **Audit verified:** 32 items overall (across 11 sibling projects)
- **This bundle:** 4 verified, 0 uncertain (resolved), 0 INFO (resolved), 0 deferred
- **Project siblings:** PROJ-384, PROJ-385, PROJ-386, PROJ-387, PROJ-388, PROJ-389, PROJ-390, PROJ-391, PROJ-392, PROJ-393

## Cluster Identity

**Removal cluster:** `command_handlers.py` shim — entire 82-LOC file is a transitional re-export from `game.strategy.engine.handlers/`. Docstring states: "this shim is **transitional**. Callers should migrate to the canonical paths... in a follow-up project; the shim is then deleted."

## Severity Breakdown

| Severity | Count |
|----------|-------|
| CRITICAL | 1 (LEG-01-005 — whole-file shim) |
| MAJOR | 3 (LEG-01-015, LEG-01-016, LEG-01-018 — caller imports) |

## Quick Wins

LEG-01-005 is a whole-file deletion (82 LOC) once callers are migrated. The migration is mechanical (import path rewrite). After this project ships, the shim file is gone.

## Risk Notes

- 25 test imports must be migrated alongside the 6 production imports — leaving any behind will cause `ImportError` on the test run.
- Some imports in `planet_command_handlers.py` are function-local (lazy) — preserve laziness if they were lazy for a circular-import reason; otherwise lift to top-level.

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.
