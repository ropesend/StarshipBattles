# PROJ-492: HLP mechanical sweeps and setup_tmpdir strategy

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-492` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-492 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. HLP-002 — nested MockPlanetType migration (8 files, ~40 sites) | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. HLP-004 — _make_fleet 37-file sweep (exact match only) | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. HLP-005 — setup_tmpdir strategy decision + implementation | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-05-23
**Active Phase:** Planning
**Last Action:** Project scaffolded from PROJ-479 deferred HLP cluster per Codex consult 20260523T125621Z_plan-PROJ-479-followthrough
**Next Action:** Start Phase 1 — pick the highest-density file (`tests/integration/ui/test_colonization_facade.py` has 9 inline copies) and migrate to canonical `tests/fixtures/colonization_fixtures.py::MockPlanetType`.
**Blockers:** None — Phase 3 contains a strategy decision but does NOT block Phases 1 or 2.
**Context:** Canonical helpers for HLP-002 (`MockPlanetType`) and HLP-004 (`_make_mock_fleet`) already exist in `tests/fixtures/colonization_fixtures.py` and `tests/conftest.py` respectively (created in PROJ-479 Phases 5-6). This project completes the mechanical migration of call sites.

## Overview
Complete the cross-shard helper consolidation deferred by PROJ-479. The canonical homes exist; what remains is the mechanical migration of consumer sites. Also resolves HLP-005 (save-path tmpdir strategy decision) by standardizing on the production `Paths.SAVES_DIR` contract.

## Goals
- Migrate ~12+ nested method-local `MockPlanetType(Enum)` definitions to import from `tests/fixtures/colonization_fixtures.py` (Phase 1)
- Migrate 37 `_make_fleet` / `make_fleet` / `_make_mock_fleet` (exact word boundary) definitions to consume the canonical helper at `tests/conftest.py` (Phase 2). Note: helpers named `_make_fleet_pair`, `_make_fleet_at`, `_make_fleet_with_ship`, etc. are OUT — they're different families.
- Decide: standardize save-path tests on patching `Paths.SAVES_DIR`; rewrite the `chdir`-based `test_auto_save.py` harness; consolidate `setup_tmpdir` (Phase 3)

## Scope
**In:**
- PROJ-479 Phase 6 Task 6.2 — full nested-copy migration
- PROJ-479 Phase 6 Task 6.4 — full 43+ file `_make_fleet` sweep
- PROJ-479 Phase 6 Task 6.5 — setup_tmpdir strategy decision + implementation

**Out:**
- CAT-6 test-side rewrites — see PROJ-491
- Production DI seam work (SuperweaponValidator) — see PROJ-493
- CAT-5 mutation-isolation deferrals — permanently deferred pending user decision (see PROJ-491 decisions.md)

## Key Files
| Component | File Path |
|-----------|-----------|
| Canonical MockPlanetType | `tests/fixtures/colonization_fixtures.py` |
| Canonical _make_mock_fleet | `tests/conftest.py` |
| Canonical setup_tmpdir (Paths.SAVES_DIR variant) | `tests/unit/strategy/save_game_service/conftest.py:48` |
| Save path production code | `game/strategy/systems/save_game_service.py:107-121` |
| Paths constant | `game/core/paths.py:46-60` |
| chdir-based variant (to rewrite) | `tests/unit/strategy/test_auto_save.py:26-33` |

## Related Documents
- [design.md](design.md) - Approach + Codex consult evidence
- [decisions.md](decisions.md) - HLP-005 strategy decision + reconciliation reasoning
- [manifest.md](manifest.md) - Full file list (~50 files)
- [findings/source_review.md](findings/source_review.md) - Pointer to PROJ-479 + Codex consult

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing (`python Tools/test_sharded/test_sharded.py`)
- [ ] LOC reclaimed: ~400-500 (migrated copies → imports)
- [ ] Audit passed
- [ ] User verified
