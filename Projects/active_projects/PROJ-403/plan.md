# PROJ-403: Tier 1 B-04 — Migrate stale `_MockGalaxy` doubles to `GalaxyState`

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Replace `_MockGalaxy` fixtures with canonical `GalaxyState` | Complete | [phase_1_checklist.md](phase_1_checklist.md) |

## Current State
**Last Updated:** 2026-05-09
**Active Phase:** Phase 1 (Complete)
**Last Action:** Migrated `_MockGalaxy` → real `GalaxyState` in both test files; broad selector `pytest tests/unit/strategy/data/ -k galaxy -q` shows 192 passed (was 36 failed / 21 passed on the focused selector).
**Next Action:** Awaiting user verification.
**Blockers:** None

## Overview
PROJ-387/394 migrated production `Galaxy` private-state forwarders to a public `Galaxy.state` property and renamed the underlying fields (e.g. `_global_hex_planets` → `state.global_hex_planets`, `_planet_to_system` → `state.planet_to_system`, `_next_planet_id` → `state.next_planet_id`). Two unit test files still define `_MockGalaxy` with the deleted private-field shape, then pass that mock directly into `GalaxyEntityRegistry` / `GalaxySpatialIndex`. The delegates now read the canonical fields and raise `AttributeError`. **36 failures** in `pytest tests/unit/strategy/data/ -k galaxy -q`.

## Goals
- Replace `_MockGalaxy` in `test_galaxy_entity_registry.py` and `test_galaxy_spatial_index.py` with real `GalaxyState` instances (or a shared `make_galaxy_stub()` helper) using canonical field names.
- Verify production callers pass `galaxy.state` rather than `galaxy` itself.
- Run the focused selector and confirm 0 failures: `pytest tests/unit/strategy/data/ -k galaxy -q`.

## Scope
**In:**
- `tests/unit/strategy/data/test_galaxy_entity_registry.py` — `_MockGalaxy` definition (~lines 16-27) and one or more constructor call sites (~lines 73-75).
- `tests/unit/strategy/data/test_galaxy_spatial_index.py` — `_MockGalaxy` definition (~lines 16-27) and constructor call sites (~lines 78-80).
- A shared helper (optional) under `tests/fixtures/` or test-local module if both files would benefit.

**Out:**
- PROJ-394 manifest path drift — covered by Tier 2 PROJ-406.
- Other `Galaxy` facade docstring wording — covered by Tier 3 PROJ-407 (D-05).

## Key Files
| Component | File Path |
|-----------|-----------|
| Test file 1 | `tests/unit/strategy/data/test_galaxy_entity_registry.py` |
| Test file 2 | `tests/unit/strategy/data/test_galaxy_spatial_index.py` |
| Production delegate (read-only) | `game/strategy/data/galaxy_entity_registry.py` |
| Production delegate (read-only) | `game/strategy/data/galaxy_spatial_index.py` |
| Canonical field shape | `game/strategy/data/galaxy_state.py` |

## Source Evidence (REMEDIATION_PLAN B-04)
- `tests/unit/strategy/data/test_galaxy_entity_registry.py:16-27` + `:73-75` — stale `_MockGalaxy`.
- `tests/unit/strategy/data/test_galaxy_spatial_index.py:16-27` + `:78-80` — stale `_MockGalaxy`.
- `game/strategy/data/galaxy_entity_registry.py:30-36`, `:75-88` — delegate reads canonical fields.
- `game/strategy/data/galaxy_spatial_index.py:26-28`, `:49-66` — delegate reads canonical fields.
- Reviewer-confirmed 36 failures in `pytest tests/unit/strategy/data/test_galaxy_spatial_index.py tests/unit/strategy/data/test_galaxy_entity_registry.py`.
- PROJ-387/394 reviews (in `Reviews/results/2026-05-09_proj-380-399-implementation-review/`).

## Verification
- [x] Phase 1 checklist complete
- [x] `pytest tests/unit/strategy/data/test_galaxy_entity_registry.py tests/unit/strategy/data/test_galaxy_spatial_index.py -v` — 0 failures (57 passed; was 36 failed / 21 passed)
- [x] `pytest tests/unit/strategy/data/ -k galaxy -q` — 0 failures (192 passed)
- [x] `python Projects/scripts/validate_audit_ready.py PROJ-403` passes
- [ ] User verified
