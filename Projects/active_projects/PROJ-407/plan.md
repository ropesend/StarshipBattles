# PROJ-407: Tier 3 — Stale docs + architecture wording sweep (D-01..D-09)

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Sweep stale docs/comments + non-modern type annotations | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |

## Current State
**Last Updated:** 2026-05-09
**Active Phase:** Phase 1
**Last Action:** Project skeleton created from REMEDIATION_PLAN Tier 3 (D-01..D-09)
**Next Action:** Implement the 9 doc/wording fixes
**Blockers:** None

## Overview
The PROJ-380..399 review found multiple cases where deletions changed current architecture or public guidance, but docs/comments/typing were left stale. This project does a single mechanical sweep that closes all 9 Tier 3 items, then runs the focused suite to make sure the typing changes (D-06, D-07) don't break anything.

## Goals — D-01..D-09 from REMEDIATION_PLAN

- **D-01 (PROJ-383)**: `grep -rn "game.strategy.engine.command_handlers" docs/` — update each match to point at `game.strategy.engine.handlers/`.
- **D-02 (PROJ-390)**: `grep -rn "log_event\|set_event_handler\|get_event_handler" docs/` — update to reflect EventBus is session-scoped via constructor injection (PROJ-252).
- **D-03 (PROJ-395)**: `docs/05_ERROR_HANDLING.md` still contradicts the EventBus architecture. Hand off scope to a doc-sweep — the agent should read `05_ERROR_HANDLING.md` AND the current EventBus code, identify the exact contradictions, and reconcile.
- **D-04 (PROJ-380)**: stale `pixel_to_hex` import-comment crumbs after migration to `Camera.hex_at_screen`. Search `grep -rn "pixel_to_hex" game/ui/screens/strategy_*` for comments and remove.
- **D-05 (PROJ-394)**: `game/strategy/data/galaxy.py:67` still labels migrated forwarders as "public + grandfathered private API". Update wording — the 5 spatial private forwarders were intentionally removed.
- **D-06 (PROJ-396)**: New `superweapon_handlers/` package modules use legacy `Optional[...]` typing. Convert to `X | None` syntax.
- **D-07 (PROJ-380 + 391 + 396)**: Several new modules use legacy `Optional[...]`. Sweep all three sets together.
- **D-08 (PROJ-391)**: `FormationSpec` serialization preserves a loose `object` slot — drops invalid formations silently. Tighten the type and add a regression that asserts unknown shapes raise.
- **D-09 (PROJ-380)**: Touched production files still over 500-LOC ceiling. Run `find game/ -name "*.py" -exec wc -l {} \; | awk '$1 > 500'` (or equivalent) on the project's manifest files. **For files that are over 500, raise a deferral note** — splitting them is real refactor work, not a doc sweep. Don't start a new refactor here. Just document what's over.

## Scope
**In:**
- All doc files (`docs/`) referenced in D-01..D-04.
- One docstring in `game/strategy/data/galaxy.py:67` (D-05).
- Modern type-syntax sweep across `superweapon_handlers/` + new modules from PROJ-380/391/396 (D-06, D-07).
- One real type tightening in `FormationSpec` serialization (D-08) — and a regression test for it.
- D-09: read-only audit + deferral list.

**Out:**
- D-09 LOC-ceiling refactor work (logged as deferral).
- Any feature change.
- `docs/_ignore/` — never touch.

## Source Evidence (REMEDIATION_PLAN Tier 3)
- D-01: PROJ-383 review.
- D-02: PROJ-390 review.
- D-03: PROJ-395 review.
- D-04: PROJ-380 review.
- D-05: PROJ-394 review (Minor finding 3).
- D-06: PROJ-396 review.
- D-07: PROJ-380/391/396 reviews.
- D-08: PROJ-391 review.
- D-09: PROJ-380 review.

## Verification
- [ ] All 9 D-items addressed (or D-09 documented as deferral)
- [ ] `pytest tests/ -k formation_spec or quickstart -q` passes (D-08 regression + general type-sweep impact)
- [ ] `python Projects/scripts/validate_audit_ready.py PROJ-407` passes
- [ ] User verified
