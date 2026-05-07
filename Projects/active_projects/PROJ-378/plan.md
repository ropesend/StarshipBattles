# PROJ-378: Galaxy Cleanup Test Pattern Update (post-PROJ-372 facade-delegate)

> **Execution Protocol:** 03c-phase-aware-execution

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-378` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-378 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Shared `make_galaxy_stub()` fixture + migrate `test_galaxy_cleanup.py` | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Sweep remaining `Galaxy.__new__` callers + opportunistic doc cleanup | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |

**Depends on:** none — PROJ-372 is closed; this cleans up its trailing test debt.

## Current State
**Last Updated:** 2026-05-07
**Active Phase:** Phase 1 complete; ready for Phase 2.
**Last Action:** Phase 1 shipped — `tests/fixtures/galaxy_fixtures.py::make_galaxy_stub()` added + `tests/unit/strategy/data/conftest.py` thin bridge added; 3 fixtures in `test_galaxy_cleanup.py` migrated. 18/18 passing (was 3/18 with 15 setup errors). One incidental fix: `planet.radius_hexes = 0` on the `MagicMock` planet in `TestGalaxyGetAllFleetsInSystem` (post-PROJ-372 `_spatial` reads this field; pre-PROJ-372 inline method didn't).
**Next Action:** Phase 2 — sweep `tests/integration/strategy/test_empire.py` (5 sites) and `tests/integration/strategy/test_fleet_registration_lifecycle.py` (1 inline factory); optional doc note in `docs/02_PATTERNS.md`.
**Blockers:** None.

## Overview

PROJ-372 Phase 3 turned 11 mutable indexes + 2 ID counters + `radius` into property forwarders backed by a `GalaxyState` dataclass on `Galaxy._state`. **15 setup-errors** in `tests/unit/strategy/data/test_galaxy_cleanup.py` use the legacy pre-PROJ-372 pattern (`Galaxy.__new__(Galaxy)` + direct attribute assignment) and crash with `AttributeError: 'Galaxy' object has no attribute '_state'` when the very first line — `galaxy.radius = 100` — invokes the new setter at `galaxy.py:74-75`.

PROJ-378 is the bounded follow-up: introduce a single shared `make_galaxy_stub()` fixture that constructs a minimal post-PROJ-372 galaxy compatible with the property-forwarder architecture, migrate the failing test file to use it, and sweep the two other test files that still use the legacy pattern (`test_empire.py`, `test_fleet_registration_lifecycle.py`) for consistency. Mechanical, low-risk; one-pass-of-LLM-time work.

## Goals

- **All 15 errors in `tests/unit/strategy/data/test_galaxy_cleanup.py` resolved.** Suite at this path goes from `3 passed, 15 errors` (18 collected) → `18 passed`.
- **One canonical fixture** (`tests/fixtures/galaxy_fixtures.py::make_galaxy_stub`) replaces the three near-duplicate `Galaxy.__new__(Galaxy)` setup blocks at `test_galaxy_cleanup.py:62-103`, `:166-189`, `:248-273`.
- **No new tests slow down by > 50 ms each.** Real `Galaxy(radius=100)` measured at ~33 ms per construction (118 ms first import); the stub avoids both, keeping each test setup < 1 ms.
- **No production code changes** — `_ensure_state()` (`galaxy.py:96-105`) stays as the lazy escape hatch for legacy code paths it already supports.
- **Sweep consistency:** `test_empire.py` and `test_fleet_registration_lifecycle.py` use the same pattern but happen to work today; migrate them in Phase 2 so the codebase has one obvious way to stub a galaxy.
- **Optional Phase 2 cleanup:** if the migration sweep leaves zero remaining `Galaxy.__new__(Galaxy)` call sites, document the stub fixture as the canonical pattern in the `make_galaxy_stub` docstring + a one-line note in `docs/02_PATTERNS.md`. (Doc-only; no production behavior.)

## Scope

**In:**
- `tests/fixtures/galaxy_fixtures.py` — **new file**, canonical implementation module: holds the `make_galaxy_stub()` factory. Importable cross-tree per the `tests.fixtures.*` convention.
- `tests/unit/strategy/data/conftest.py` — **new file (optional)**, thin pytest fixture bridge: imports `make_galaxy_stub` from `tests.fixtures.galaxy_fixtures` and exposes a `galaxy_stub` `@pytest.fixture` wrapper.
- `tests/unit/strategy/data/test_galaxy_cleanup.py` — migrate 3 fixtures (`galaxy_with_planet`, `galaxy_with_warp_link`, `galaxy_with_fleets`) to call `make_galaxy_stub()` then layer test-specific state on top.
- `tests/integration/strategy/test_empire.py` — migrate 5 `Galaxy.__new__(Galaxy)` call sites (lines 11, 19, 26, 37, 45) to `make_galaxy_stub()`.
- `tests/integration/strategy/test_fleet_registration_lifecycle.py` — migrate the inline factory at lines 75-80 to use `make_galaxy_stub()`. (The fixture is already the post-PROJ-372 shape; this is consolidation, not correction.)
- Optional: `docs/02_PATTERNS.md` — short note documenting `make_galaxy_stub()` as the canonical "minimal galaxy for unit tests" pattern.

**Out:**
- Any change to `game/strategy/data/galaxy.py`, `galaxy_state.py`, or any production source.
- Removal of `Galaxy._ensure_state()` — it's a public-shaped lazy initializer used by the per-test fixture pattern; keep it for any future `__new__` use cases. (Optional follow-up project if a sweep proves zero remaining callers.)
- Any test outside the three files listed above. The legacy-pattern grep was exhaustive: the only three matches in `tests/` are listed.
- Any change to `Galaxy(radius=N)` callers (24 files); they construct real galaxies and that's correct.
- `MockGalaxy` test doubles (used in 6 UI test files); they're a different concern — small, hand-rolled mocks for UI fixtures that don't exercise galaxy state.

## Key Files

| Component | File Path | Role |
|-----------|-----------|------|
| Galaxy facade (post-PROJ-372) | `game/strategy/data/galaxy.py` | Read-only reference (no edits). `__init__` at `:42`, property forwarders at `:69-141`, `_ensure_state` at `:96-105`, `radius.setter` at `:73-75`. |
| GalaxyState dataclass | `game/strategy/data/galaxy_state.py` | Read-only reference. 11 dict fields + 2 ID counters + `radius`, all renamed without leading underscore. |
| Service delegates | `game/strategy/data/galaxy_entity_registry.py`, `galaxy_spatial_index.py`, `galaxy_warp_generator.py`, `galaxy_system_generator.py` | Take `GalaxyState` as the constructor argument; the stub wires both. |
| **NEW** Shared stub fixture (canonical implementation) | `tests/fixtures/galaxy_fixtures.py` | Defines `make_galaxy_stub()` (importable cross-tree). |
| **NEW** Optional pytest fixture bridge | `tests/unit/strategy/data/conftest.py` | Thin `@pytest.fixture` wrapper named `galaxy_stub` that delegates to the implementation module. |
| Failing test file (15 errors) | `tests/unit/strategy/data/test_galaxy_cleanup.py` | Three setup fixtures migrated. |
| Working but legacy-pattern caller | `tests/integration/strategy/test_empire.py` | 5 `__new__` sites migrated for consistency. |
| Working post-PROJ-372 fixture | `tests/integration/strategy/test_fleet_registration_lifecycle.py` | Inline factory consolidated to import the shared stub. |
| Pattern reference | `tests/integration/strategy/test_fleet_registration_lifecycle.py:62-80` | Already does the right thing post-PROJ-372 (sets `gal._state = GalaxyState(...)`); this is the model the new fixture generalizes. |

## Related Documents

- [design.md](design.md) — Pattern catalogue, fix-option analysis, recommendation rationale.
- [decisions.md](decisions.md) — Decisions log (fix option chosen, scope decisions).
- [manifest.md](manifest.md) — File table for parallel-conflict detection.
- [findings/initial_review.md](findings/initial_review.md) — Pattern catalogue + perf finding.
- **PROJ-372 plan:** `Projects/archived_projects/PROJ-372/plan.md` (if archived) or `Projects/active_projects/PROJ-372/plan.md`.
- **PROJ-372 design (`__init__` heavy I/O analysis):** see Risk R5 in `Projects/active_projects/PROJ-372/design.md`.
- **PROJ-372 review note:** the verifier called out this exact gap — "These tests were written before PROJ-372 and use the old pattern. The PROJ-372 agent didn't update them because they're not in the focused test paths it was working on."

## Verification Checklist

### Project Start
- [ ] Read `docs/01_ARCHITECTURE.md`, `docs/02_PATTERNS.md`, `docs/03_CONVENTIONS.md`.
- [ ] Read PROJ-372 design doc — facade-delegate pattern + `GalaxyState` extraction rationale.
- [ ] Run `python -m pytest tests/unit/strategy/data/test_galaxy_cleanup.py --tb=line -q` — capture baseline (3 passed, 15 errors expected; 18 collected per `pytest --collect-only`).
- [ ] Read `findings/initial_review.md` for the full pattern catalogue.

### After Each Phase
- [ ] Run `pytest tests/unit/strategy/data/test_galaxy_cleanup.py -v` — target file all-pass.
- [ ] Run `pytest tests/integration/strategy/test_empire.py tests/integration/strategy/test_fleet_registration_lifecycle.py -v` — neighbours still pass.
- [ ] Update Current State in this plan.

### Final Verification
- [ ] `tests/unit/strategy/data/test_galaxy_cleanup.py` — 18 / 18 passing (was 3 / 18, with 15 setup errors).
- [ ] `tests/integration/strategy/test_empire.py` — 5 / 5 still passing.
- [ ] `tests/integration/strategy/test_fleet_registration_lifecycle.py` — full file still passing.
- [ ] `python Tools/test_sharded/test_sharded.py` — sharded suite green; pass count = baseline + 15 (the 15 setup errors → 15 new passes).
- [ ] Zero `Galaxy.__new__(Galaxy)` call sites remain in `tests/` (verified via `Grep`).
- [ ] Zero `patch.object(Galaxy, '__init__'` call sites remain in `tests/` (verified via `Grep`).
- [ ] `make_galaxy_stub()` is the only shared stub helper; no duplicate "minimal galaxy" factories drift back in.
- [ ] (Optional) `docs/02_PATTERNS.md` references `make_galaxy_stub()` as the canonical minimal-galaxy pattern.

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

## Completion Checklist
- [ ] All Phase 1 tasks checked off.
- [ ] All Phase 2 tasks checked off.
- [ ] Sharded suite green.
- [ ] User verified.
