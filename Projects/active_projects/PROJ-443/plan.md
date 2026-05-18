# PROJ-443: Pytest norecursedirs Fix and Hidden-Test Triage

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-443` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-443 [phase]` before stopping
> - Update Current State with specific handoff context

**Execution Protocol:** 03c-phase-aware-execution

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 0. Capture hidden-test baseline | Not Started | [phase_0_checklist.md](phase_0_checklist.md) |
| 1. Triage `test_cargo_tracking.py` (30 known PROJ-431-flagged failures) | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Triage `test_mutator_boundary_ast_guard.py` failures | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Triage remaining `tests/unit/strategy/data/` failures | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Switch `pytest.ini` from `norecursedirs = data` to `--ignore=./data` | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Bundled hygiene: PROJ-436 deferred items | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Codex consult + verified-finding remediation | Not Started | [phase_6_checklist.md](phase_6_checklist.md) |

## Current State
**Last Updated:** 2026-05-18
**Active Phase:** Planning (charter just created)
**Last Action:** Project scaffold created via `python Projects/scripts/create_project.py "Pytest norecursedirs Fix and Hidden-Test Triage"`. Discovered during PROJ-436 Phase 2 — `pytest.ini` `norecursedirs = ... data ...` matches any directory named `data` anywhere in the tree (not just the intended top-level `data/`), silently hiding 1575 tests in `tests/unit/strategy/data/` from the sharded suite. Baseline: 1510 pass / 65 fail in that hidden directory as of PROJ-436 Phase 2 close. PROJ-436 Phases 3-7 may have shifted that count further (Phase 3 cutover, Phase 4 cutover, etc., touched code those hidden tests cover) — Phase 0 of this project captures the current baseline.
**Next Action:** Phase 0 — run `pytest tests/unit/strategy/data/ -q -n 4` and scan for any other `tests/**/data/` directories to capture the current hidden-test failure ledger.
**Blockers:** None.

## Overview
A pre-existing project-wide pytest configuration bug silently hides 1575 tests in `tests/unit/strategy/data/` from the canonical sharded suite (`python Tools/test_sharded/test_sharded.py`). `pytest.ini` has `norecursedirs = .* build dist CVS _darcs {arch} *.egg venv env .venv data ShipThemes Assets combat_lab` — the `data` token is intended to skip the top-level `data/` game-asset directory but matches any directory named `data` at any depth. Result: the entire `tests/unit/strategy/data/` directory (and any similarly named test directories under other layers) has been untested in CI for an unknown duration.

Phase 0 captures the current baseline. Phases 1-3 triage and fix the freshly-exposed failures by class. Phase 4 flips the config from glob-based `norecursedirs` to path-anchored `--ignore=./data` in `addopts`. Phase 5 bundles the small follow-up items deferred by PROJ-436 (Phases 3/4/5/6 consult findings). Phase 6 is the end-of-project Codex consult.

## Goals
- Eliminate the silent test-collection gap: every test file under `tests/` runs in the canonical sharded suite.
- Fix or appropriately mark every hidden test that fails today, so the flipped config doesn't introduce a sharded-suite regression.
- Replace `norecursedirs = ... data ...` with `--ignore=./data` so only the top-level `data/` directory is excluded.
- Bundle PROJ-436's 4 deferred non-blocker items (Phase 3 finding (d) dataclass introspection drift, Phase 3 finding (e) legacy-kwarg constructor wrapper smell, Phase 5 D2 caching follow-up if ever needed, Phase 6 finding test-mock residue across 4 production_engine test files) under one cleanup phase.
- End-of-project Codex consult to verify nothing else is silently hidden by other `norecursedirs` tokens.

## Scope
**In:** triage + fix of all hidden-test failures in `tests/unit/strategy/data/` (PROJ-431 audit estimated ~65 at PROJ-436 Phase 2; current count to be captured in Phase 0); `pytest.ini` config change; PROJ-436 deferred-item cleanup (4 bundled items); end-of-project Codex consult.

**Out:** changing the behavior of the tests themselves beyond what's needed to make them pass against the current codebase (i.e., no scope creep into refactoring the storage / cargo / planet code that the hidden tests cover); fixing PROJ-436 Phases 8/9 (those are PROJ-436's own remaining work); changing the sharded runner itself; cross-tree test reorganization.

## Dependencies
**No hard predecessor.** PROJ-436 Phases 0-7 complete (last sharded baseline: 21233 visible tests). PROJ-436 Phases 8/9 may run in parallel with this project — they touch different surfaces.

**Soft adjacency:** PROJ-436 Phase 8 (`ProductionEngine.context_type` deletion) and PROJ-436 Phase 9 (`_CarriedItemsProxy` final cutover) may shift the hidden-test failure count further. If those phases land while this project is in flight, recapture the baseline at Phase 0 close.

**No worktrees** per user standing preference. Serial execution in main checkout.

## Key Files
| Component | File Path |
|-----------|-----------|
| pytest config | `pytest.ini` |
| Hidden test baseline directory | `tests/unit/strategy/data/` (1575 tests) |
| Likely also affected | Any other `tests/.../data/` if present |
| PROJ-436 finding-(d) cleanup | `game/strategy/data/ship_instance.py` introspection seam |
| PROJ-436 finding-(e) cleanup | ~24 `ShipInstance(consumable_levels=...)` / `ShipInstance(cargo_contents=...)` call sites in ~7 test files |
| PROJ-436 Phase 6 mock residue | `tests/unit/strategy/engine/test_production_engine_{queue,consumption,refactor}.py` + `test_harvesting_engine.py` |

Full enumeration in [manifest.md](manifest.md).

## Phases

### Phase 0: Capture hidden-test baseline
Run `pytest tests/unit/strategy/data/ -q -n 4` and also scan for any other `tests/**/data/` directories. Record current pass/fail count and the exact list of failing test IDs. Establish the baseline at the current `main` HEAD. **Checkpoint:** baseline ledger committed to `findings/hidden_test_baseline.md`; no code changes.

### Phase 1: Triage `test_cargo_tracking.py`
30 tests flagged by PROJ-431's completion report as pre-existing failures. After PROJ-436 Phase 3 (cargo manager API migration), many may now naturally pass. Run the file, classify each failure: (a) now passing — done; (b) test was wrong, fix the test; (c) test exposes a real bug, fix the production code; (d) test is obsolete, delete it. Commit per category. **Checkpoint:** zero failures in `test_cargo_tracking.py` via direct invocation.

### Phase 2: Triage `test_mutator_boundary_ast_guard.py`
~9 failures per PROJ-436 Phase 2 audit. These are AST static guards that drifted. Audit each: is the guard checking a still-valid invariant? If yes, fix the code/test to satisfy it. If the invariant no longer applies (e.g., post-Phase-3 architecture), rewrite the guard. **Checkpoint:** zero failures in `test_mutator_boundary_ast_guard.py`.

### Phase 3: Triage remaining `tests/unit/strategy/data/` failures
The remaining ~26 failures after Phases 1 and 2 (count updated from Phase 0 ledger). One-by-one classification + fix. May produce small sub-phases per cluster of related failures. **Checkpoint:** `pytest tests/unit/strategy/data/ -q -n 4` returns zero failures.

### Phase 4: Switch `pytest.ini` config
- Change `pytest.ini`:
  - Remove `data` from `norecursedirs`.
  - Add `--ignore=./data` to `addopts` (anchored to repo root, only matches the top-level `data/` directory).
- Run sharded suite. Expect count to jump from ~21233 to ~22700+ collected.
- Add a regression-guard test under `tests/static_guards/test_no_hidden_test_directories.py` that asserts `pytest tests/ --collect-only -q` collects every `test_*.py` file under `tests/` recursively (sanity check for future drift).
**Checkpoint:** sharded suite green at the new higher count; no new failures.

### Phase 5: PROJ-436 deferred-item bundle
Four small items deferred by PROJ-436 consults:
- **5a — Phase 3 finding (d) dataclass-introspection drift on `ShipInstance`**: clean up the seam if it's worth it; document as accepted if not.
- **5b — Phase 3 finding (e) legacy-kwarg constructor wrapper**: ~24 sites in ~7 test files. Mechanical sweep migrating `ShipInstance(consumable_levels=...)` / `ShipInstance(cargo_contents=...)` test fixtures to the new manager-API path. Delete the wrapper at the end.
- **5c — Phase 6 production_engine test-mock residue**: 6 inert MagicMock attributes for deleted Empire methods across 4 test files. Delete.
- **5d — Phase 5 D2 large-empire profiling**: only execute this sub-phase if a real perf signal emerges. Otherwise document as "no signal observed; deferred indefinitely."

Each lands as its own commit. **Checkpoint:** all four sub-items either resolved or documented as accepted-tradeoff.

### Phase 6: Codex consult + verified-finding remediation
Per the standing end-of-project workflow. Frame the consult: "Review PROJ-443's `pytest.ini` change and the hidden-test triage. Verify (a) the new `--ignore=./data` correctly excludes only the top-level `data/`; (b) no other `norecursedirs` tokens are silently hiding tests elsewhere; (c) Phase 5 bundled cleanups landed cleanly; (d) the regression guard against future test-directory hiding is sufficient." Verify findings against code, remediate as needed.

## Verification
- [ ] All phase checklists complete
- [ ] Sharded suite collects every test under `tests/` (no silent skips)
- [ ] Sharded suite green at the new test count
- [ ] PROJ-436 deferred-item bundle resolved or documented
- [ ] Audit passed
- [ ] User verified
