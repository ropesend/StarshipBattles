# PROJ-379: Deterministic Golden-Save Fixture (PROJ-377 MIN-002)

> **Execution Protocol:** 03c-phase-aware-execution

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-379` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-379 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist | Depends on |
|-------|--------|-----------|------------|
| 1. TDD-first hand-built fixture builder (tests + builder + JSONs + field-coverage guard) | Complete | [phase_1_checklist.md](phase_1_checklist.md) | — |
| 2. Cross-process determinism (PYTHONHASHSEED + subprocess) | Complete | [phase_2_checklist.md](phase_2_checklist.md) | Phase 1 |
| 3. Delete `_capture_baseline.py` + cleanup | Complete | [phase_3_checklist.md](phase_3_checklist.md) | Phase 2 |
| 4. Closeout + cross-links + review cycle | Not Started | [phase_4_checklist.md](phase_4_checklist.md) | Phase 3 |

## Current State
**Last Updated:** 2026-05-08
**Active Phase:** Planning complete (Codex peer review applied); awaiting user "Plan Approved" before implementation begins.
**Last Action:** Codex inter-agent review (`AgentCoordination/Scratchpad/Discussion/20260508T022447Z_proj-379-plan-review/`) flagged 6 issues; all verified with evidence and applied. Specifically: (1) added `phase_state.json` + `findings_ledger.md` for real 03c compliance; (2) restructured Phase 1 as TDD-first (failing tests before builder); (3) fixed `_FIXTURE_PATH` typo (`parent.parent.parent / "fixtures" / "saves"`, no `"tests"` segment); (4) replaced dataclass-defaults introspection with serialized-baseline pattern (`planet_to_dict(_minimal_planet())` is the source of truth); (5) added cross-process `PYTHONHASHSEED` subprocess tests (Phase 2) plus committed-fixture-vs-builder-output staleness check (Phase 1); (6) made `system.planets.append(planet) + register_planet(...)` explicit in Phase 1 Task 1.4. Plan revision recorded at `plans/proj379_revisions_r001.md` in the discussion folder.
**Next Action:** User confirms "Plan Approved". Implementation starts in a fresh session via "Continue Project" prompt; first task is Phase 1 Task 1.1 (add failing byte-determinism tests).
**Blockers:** None.
**Context for Next Agent:** This project resolves PROJ-377 review MIN-002 ("double-seed pattern is fragile" — `tests/fixtures/saves/_capture_baseline.py` produces non-deterministic output across re-runs). The locked approach replaces generation-then-normalize with hand-built `Galaxy` objects (StarSystem/Planet/WarpPoint constructed directly via `__init__`, registered through the production `_registry` paths). Zero production-code changes. Field-coverage guard at `tests/integration/strategy/test_golden_fixture_field_coverage.py` (NEW) calls `planet_to_dict(_minimal_planet())` to obtain both the emitted-keys set and the per-key default baseline, then asserts every key (modulo `image_id`/`image_rotation` skiplist) has a non-default value somewhere in the populated fixture.

## Overview

PROJ-377 Phase 1 shipped two JSON golden-save fixtures (`tests/fixtures/saves/galaxy_proj372_baseline.json`, `..._populated.json`) plus a capture script (`tests/fixtures/saves/_capture_baseline.py`). The script was originally specified as deterministic — re-running it should produce byte-identical JSON. It does not. Re-runs differ in star image_ids, planet image_ids/rotations, warp_type rolls, warp-point intrinsic abilities, planet body shapes (mass, density, temperature), and system names. The OpenCode review of PROJ-377 (req_20260507_044410_7cfefd) flagged this as MIN-002; the verifier confirmed it; we deferred a fix on the grounds that the docstring documented the trade-off and CI's contract is round-trip identity, not byte-equality.

PROJ-379 closes that gap. The capture script is replaced by a hand-built fixture builder (deterministic by construction); a new field-coverage guard (calling `planet_to_dict()` against a minimal `Planet` for the per-key default baseline — see Phase 1 Task 1.2 for the implementation outline) asserts the populated fixture exercises every key emitted by `planet_to_dict` with a non-default value. Future re-captures (e.g., when a developer adds a `Planet` field) produce byte-identical output across processes; any fixture diff is fully attributable to either an intentional schema change or a regression — never RNG drift.

## Goals

- **G1.** Re-running the fixture builder produces byte-identical JSON across processes (including under random `PYTHONHASHSEED`).
- **G2.** The populated fixture exercises every field in `game/strategy/data/planet_serde.py::planet_to_dict` with a non-default value, asserted by a Phase 1 guard that calls `planet_to_dict()` on a minimal `Planet` for the per-key default baseline, then asserts every key (modulo `image_id`/`image_rotation` skiplist) has a non-default value somewhere in the populated fixture.
- **G3.** The existing 7 round-trip tests in `tests/integration/strategy/test_save_round_trip.py` continue to pass (the new fixtures pass `Galaxy.from_dict(fixture).to_dict() == fixture`).
- **G4.** PROJ-377 review MIN-002 is closed; a cross-link row in PROJ-377 `decisions.md` notes the resolution.
- **G5.** Zero production-code changes. The fixture builder is a pure test artifact.
- **G6.** `_capture_baseline.py`, its `_normalize_image_fields` function, and the double-seed pattern are deleted; future maintainers see one canonical fixture-build path.

## Scope

**In:**
- `tests/fixtures/saves/_build_galaxy_fixture.py` — **new file, ~80-150 LOC.** Two factory functions: `build_baseline()` (5-system + warp lanes, no planets) and `build_populated()` (10-system + planets + decorated owned planet exercising every Planet field with a non-default value).
- `tests/fixtures/saves/galaxy_proj372_baseline.json` — regenerated.
- `tests/fixtures/saves/galaxy_proj372_populated.json` — regenerated.
- `tests/integration/strategy/test_save_round_trip.py` — extended with **6 new tests** (Phase 1: 2 in-process determinism + 2 committed-fixture-vs-builder-output staleness checks; Phase 2: 2 cross-process subprocess + `PYTHONHASHSEED` tests).
- `tests/integration/strategy/test_golden_fixture_field_coverage.py` — **new file, ~50-80 LOC.** Field-coverage guard using the serialized-baseline pattern (`planet_to_dict(_minimal_planet())` is the source of truth for emitted keys + per-key defaults).
- `tests/fixtures/saves/_capture_baseline.py` — **deleted** at Phase 3.
- `Projects/active_projects/PROJ-377/decisions.md` — appended with "MIN-002 resolved by PROJ-379" cross-link row at Phase 4.

**Out:**
- **Full rng threading through `StarGenerator` / `PlanetGenerator` / image registries / `NameRegistry` / `GalaxyWarpGenerator`** (Option A from exploration). ~40 module-level `random.*` calls would need conversion. If a future need arises (e.g., "replay any galaxy from its seed"), spin up a separate project that extends the existing PROJ-301/302/303/304 child-rng pattern at `game/strategy/data/galaxy_system_generator.py:158-169`.
- **Storm round-trip drift.** Out of scope per PROJ-372; the new builder doesn't generate storms (no `_strip_storms` workaround needed).
- **Migrating other capture scripts** (combat lab `test_history.json`, save/load round-trip tests for `Empire` / `GameSession`). Each is a separate concern.
- **Performance regression bench updates.** PROJ-379 doesn't change runtime paths.

## Key Files Reference

| Component | File Path | Class/Function | Notes |
|-----------|-----------|----------------|-------|
| **NEW** Hand-built fixture builder | `tests/fixtures/saves/_build_galaxy_fixture.py` | `build_baseline`, `build_populated`, `_strip_storms` (kept), helper builders | Replaces `_capture_baseline.py` |
| Existing round-trip test | `tests/integration/strategy/test_save_round_trip.py` | 7 existing tests + 4 new in-process tests (Phase 1) + 2 new subprocess tests (Phase 2) | Extended across Phases 1 and 2 |
| **NEW** Field-coverage guard | `tests/integration/strategy/test_golden_fixture_field_coverage.py` | `test_populated_fixture_exercises_every_planet_field` | Calls `planet_to_dict(_minimal_planet())` for the serialized-baseline; no AST walk |
| Galaxy stub (PROJ-378) | `tests/fixtures/galaxy_fixtures.py` | `make_galaxy_stub` | Reused as the starting point for fixture builder |
| Strategy entity factories | `tests/fixtures/strategy_entities.py` | `create_test_planet`, `create_test_star`, `create_test_warp_point`, etc. | Reused for hand-built specs |
| Production registration paths | `game/strategy/data/galaxy_entity_registry.py` | `add_system`, `register_planet` | Read-only — fixtures route through these |
| Galaxy facade | `game/strategy/data/galaxy.py` | `to_dict`, `from_dict` | Read-only — round-trip passes through this |
| Planet serde | `game/strategy/data/planet_serde.py` | `planet_to_dict`, `planet_from_dict_kwargs` | Read-only — Phase 1 guard calls `planet_to_dict()` against a minimal `Planet` to obtain the emitted-keys set and per-key serialized defaults |
| Existing baseline JSON | `tests/fixtures/saves/galaxy_proj372_baseline.json` | (data) | Regenerated in Phase 1 |
| Existing populated JSON | `tests/fixtures/saves/galaxy_proj372_populated.json` | (data) | Regenerated in Phase 1 |
| **DELETED** Old capture script | `tests/fixtures/saves/_capture_baseline.py` | `capture_baseline`, `capture_populated`, `_normalize_image_fields` | Removed in Phase 3 |
| Cross-link target | `Projects/active_projects/PROJ-377/decisions.md` | (doc) | Phase 4 appends MIN-002 resolution row |

## Decisions Log

The full log lives at [decisions.md](decisions.md). The summary below is a pointer; refer to `decisions.md` for the canonical, dated rows including the 2026-05-08 Codex peer review fixes (TDD ordering, serialized-baseline guard pattern, cross-process determinism, planet append/register, real 03c metadata).

## Initial Analysis (from exploration agents)

### Non-determinism sources, ranked by severity (full table in [design.md](design.md))

| Source | Site | Severity |
|---|---|---|
| **Star generation** | `game/strategy/generation/star_generator.py` (~20 module-level `random.*` calls) | CRITICAL — `StarGenerator` has no `rng` param at any level |
| **Planet generation** | `game/strategy/data/planet_gen.py` (~20 module-level `random.*` calls) | CRITICAL — `PlanetGenerator.generate_system_bodies` has no `rng` param |
| **NameRegistry shuffle** | `game/strategy/data/naming.py:42` (`random.shuffle` during `Galaxy.__init__`) | HIGH |
| **Image registries** | `PlanetImageRegistry.get_random_image / rotation` and `StarImageRegistry.get_random_image` default to fresh unseeded `Random()` | HIGH |
| **Warp generation** | `GalaxyWarpGenerator._calculate_warp_distance:46`, `_should_add_density_edge:272`, `_apply_warp_point_intrinsic_abilities:410` | MEDIUM |

The hand-built approach side-steps all five categories: by constructing `StarSystem` / `Planet` / `WarpPoint` directly (no generators invoked), the fixture has zero RNG-bound paths.

### Existing utilities to reuse

- `tests/fixtures/galaxy_fixtures.py::make_galaxy_stub()` — PROJ-378's `Galaxy.__new__()` + manual `_state` / `_registry` / `_spatial` wiring.
- `tests/fixtures/strategy_entities.py::create_test_*` factories — already accept `**overrides` for explicit field control.
- `tests/integration/strategy/test_save_round_trip.py::_build_minimal_planet` — direct `Planet(**fields)` constructor pattern.
- `Galaxy._registry.add_system()` and `Galaxy._registry.register_planet()` — production registration paths.

### Existing rng-threading convention (mature, reused if Option A is later pursued)

The codebase has an established pattern at `game/strategy/data/galaxy_system_generator.py:158-169` (PROJ-301/302/303/304):
1. `def generator(..., rng: Optional[random.Random] = None)`
2. `if rng is None: rng = random.Random()` fallback
3. Spawn child rngs: `child_seed = rng.randint(0, 2**32 - 1); child_rng = random.Random(child_seed)`

PROJ-379 does NOT extend this pattern (Option B sidesteps generation entirely), but if a follow-up project later pursues Option A, this is the model.

## Verification Checklist

### Project Start (REQUIRED)
- [ ] Read `docs/01_ARCHITECTURE.md`, `docs/02_PATTERNS.md`, `docs/03_CONVENTIONS.md`
- [ ] Read `Projects/protocols/03c_phase_aware_execution.md`
- [ ] Read [design.md](design.md) and [decisions.md](decisions.md) end-to-end
- [ ] Read `tests/fixtures/saves/_capture_baseline.py` (the file being replaced) and the OpenCode review at `Reviews/results/2026-05-07_044412_code_proj-377-.../report.md` (MIN-002 section) for context
- [ ] Run `python Tools/test_sharded/test_sharded.py` — pin baseline pass count

### After Each Phase
- [ ] Run targeted phase tests (per phase checklist's `Tests:` lines)
- [ ] Run `python Tools/test_sharded/test_sharded.py` — sharded suite green; pass count grows monotonically
- [ ] Update Current State in plan.md with handoff context

### Final Verification (Phase 4)
- [ ] `md5sum tests/fixtures/saves/*.json` produces a stable hash across two consecutive `python tests/fixtures/saves/_build_galaxy_fixture.py` invocations.
- [ ] All 7 existing round-trip tests + 4 Phase 1 in-process determinism tests (2 byte-determinism + 2 committed-fixture-vs-builder-output staleness) + 1 Phase 1 field-coverage test + 2 Phase 2 cross-process subprocess tests pass.
- [ ] Sharded suite green; pass count = baseline + 7.
- [ ] `_capture_baseline.py` no longer exists; `grep -r _capture_baseline` (over `tests/`, `Tools/`, `docs/`) returns zero matches.
- [ ] PROJ-377 `decisions.md` includes the "MIN-002 resolved by PROJ-379" cross-link row.
- [ ] OpenCode review + verifier subagent + remediations applied per established cycle.

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

## Completion Checklist
- [ ] All Phase 1 tasks checked off
- [ ] All Phase 2 tasks checked off
- [ ] All Phase 3 tasks checked off
- [ ] All Phase 4 tasks checked off
- [ ] All tests passing (sharded suite green)
- [ ] PROJ-377 cross-link backfilled
- [ ] OpenCode review + verifier passed
- [ ] User verified
