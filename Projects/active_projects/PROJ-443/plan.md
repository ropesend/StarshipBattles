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
| 0. Capture hidden-test baseline (all 6 hidden dirs) | Not Started | [phase_0_checklist.md](phase_0_checklist.md) |
| 1. Triage `test_cargo_tracking.py` (~30 PROJ-431-flagged failures) | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Triage `test_mutator_boundary_ast_guard.py` (~9 AST guard drift failures) | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Triage remaining `tests/unit/strategy/data/` failures + 5 smaller hidden dirs | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. `pytest.ini` config flip (remove `data` + `combat_lab` + `Assets`) + regression guard + docs + testmon wipe | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Bundled hygiene: PROJ-436 deferred items | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Codex consult + verified-finding remediation | Not Started | [phase_6_checklist.md](phase_6_checklist.md) |

## Current State
**Last Updated:** 2026-05-18
**Active Phase:** Planning (charter revised per Codex consult)
**Last Action:** Project scaffolded; Codex pre-execution consult at `AgentCoordination/Scratchpad/Consult/20260518T034917Z_proj443-charter-review/response.md` surfaced two must-fix issues: (1) scope was too narrow — `pytest.ini` has THREE problematic tokens (`data`, `combat_lab`, `Assets`), not just `data`, collectively hiding **126 test files across 6 directories** (95 + 24 + 3 + 1 + 2 + 1); (2) the proposed `--ignore=./data` is cwd-relative per `_pytest/pathlib.py:998-1004`, not config-root anchored — and `pytest.ini` already sets `testpaths = tests` so no `--ignore` is needed at all. Charter revised to: expand scope to all 3 tokens, switch to removal-only config change, rename Phase 4 regression guard scope to "no hidden test files," add `docs/guides/testing_infrastructure.md` snippet update and `.testmondata` wipe to Phase 4.
**Next Action:** Phase 0 — run `pytest <dir> -q -n 4` against each of the 6 hidden test directories to capture the current baseline failure ledger.
**Blockers:** None.

## Overview
A pre-existing project-wide pytest configuration bug silently hides 126 tests in 6 directories from the canonical sharded suite (`python Tools/test_sharded/test_sharded.py`). `pytest.ini` has:

```ini
norecursedirs = .* build dist CVS _darcs {arch} *.egg venv env .venv data ShipThemes Assets combat_lab
```

Per `_pytest/main.py:455-458`, `norecursedirs` is a list of glob-style patterns matched against directory **basenames** at any depth — not anchored to repo root. Three of the tokens collide with real test directories:

| Token | Hidden test directories | `test_*.py` count |
|---|---|---|
| `data` | `tests/integration/data/` (1), `tests/unit/data/` (3), `tests/unit/research/data/` (0), `tests/unit/strategy/data/` (95) | 99 |
| `combat_lab` | `tests/unit/combat_lab/` | 24 |
| `Assets` | `tests/unit/assets/` (2), `tests/unit/ui/assets/` (1) — case-insensitive `fnmatch` on Windows matches lowercase `assets` | 3 |
| `ShipThemes` | (none — no matches) | 0 |
| **Total hidden** | **6 directories** | **126** |

Phase 0 captures the current pass/fail baseline across all 6 hidden directories. Phases 1-3 triage the failures, with Phase 1/2/3 focused on `tests/unit/strategy/data/` (the largest cluster — 95 files, ~65 known failures from the PROJ-436 Phase 2 audit) and Phase 3 also covering the 5 smaller hidden directories (combat_lab + data + assets + ui/assets + integration/data; 31 files). Phase 4 flips the config by **removing** the three problematic tokens from `norecursedirs` (no `--ignore` needed because `testpaths = tests` already prevents pytest from descending into the top-level `data/` / `Assets/` / `combat_lab/` directories that the tokens were trying to skip). Phase 5 bundles the 4 PROJ-436 deferred items. Phase 6 is the end-of-project Codex consult.

## Goals
- Eliminate the silent test-collection gap: every test file under `tests/` runs in the canonical sharded suite.
- Fix or appropriately mark every hidden test that fails today, so the flipped config doesn't introduce a sharded-suite regression.
- Remove `data`, `combat_lab`, and `Assets` from `norecursedirs`. The `testpaths = tests` directive already prevents the top-level `data/` / `Assets/` / `combat_lab/` from being scanned during normal runs, so no additional `--ignore` flag is needed.
- Bundle PROJ-436's 4 deferred non-blocker items (Phase 3 finding (d) dataclass introspection drift, Phase 3 finding (e) legacy-kwarg constructor wrapper smell, Phase 5 D2 caching follow-up if ever needed, Phase 6 finding test-mock residue across 4 production_engine test files) under one cleanup phase.
- Update `docs/guides/testing_infrastructure.md` if it references the current `norecursedirs` policy.
- End-of-project Codex consult to verify nothing else is silently hidden.

## Scope
**In:** triage + fix of all hidden-test failures across 6 directories (`tests/unit/strategy/data/`, `tests/unit/combat_lab/`, `tests/unit/data/`, `tests/unit/assets/`, `tests/unit/ui/assets/`, `tests/integration/data/`); `pytest.ini` config change (remove 3 tokens from `norecursedirs`); regression guard `tests/static_guards/test_no_hidden_test_files.py` (file-level: every on-disk `test_*.py` under `tests/` is in the collection set); `docs/guides/testing_infrastructure.md` snippet refresh; `.testmondata` wipe documentation; PROJ-436 deferred-item cleanup (4 bundled items); end-of-project Codex consult.

**Out:** changing the behavior of the tests themselves beyond what's needed to make them pass against the current codebase (no scope creep into refactoring the storage / cargo / planet / combat_lab code that the hidden tests cover); fixing PROJ-436 Phases 8/9 (those are PROJ-436's own remaining work); changing the sharded runner itself; cross-tree test reorganization; broadening the regression guard to catch `python_functions` / `python_classes` / collection-hook drift (file-level guard only; that's "no hidden test files," not "all collection drift").

## Dependencies
**No hard predecessor.** PROJ-436 Phases 0-7 complete (last sharded baseline: 21233 visible tests). PROJ-436 Phases 8/9 may run in parallel with this project — they touch different surfaces.

**Soft adjacency:** PROJ-436 Phase 8 (`ProductionEngine.context_type` deletion) and PROJ-436 Phase 9 (`_CarriedItemsProxy` final cutover) may shift the hidden-test failure count further. If those phases land while this project is in flight, recapture the baseline at Phase 0 close.

**No worktrees** per user standing preference. Serial execution in main checkout.

## Key Files
| Component | File Path |
|-----------|-----------|
| pytest config | `pytest.ini` |
| Largest hidden test cluster | `tests/unit/strategy/data/` (95 files; ~65 known failures) |
| Other hidden test directories | `tests/unit/combat_lab/` (24), `tests/unit/data/` (3), `tests/unit/assets/` (2), `tests/unit/ui/assets/` (1), `tests/integration/data/` (1) |
| Testing-infra doc | `docs/guides/testing_infrastructure.md` (embeds a `norecursedirs` snippet) |
| Testmon cache | `.testmondata` (one-time wipe in Phase 4) |
| PROJ-436 finding-(d) cleanup | `game/strategy/data/ship_instance.py` introspection seam |
| PROJ-436 finding-(e) cleanup | ~24 `ShipInstance(consumable_levels=...)` / `cargo_contents=...` call sites in ~7 test files |
| PROJ-436 Phase 6 mock residue | `tests/unit/strategy/engine/test_production_engine_{queue,consumption,refactor}.py` + `test_harvesting_engine.py` |

Full enumeration in [manifest.md](manifest.md).

## Phases

### Phase 0: Capture hidden-test baseline (all 6 hidden directories)
For each of the 6 hidden directories, run `pytest <dir> -q -n 4 --no-header` and capture pass/fail counts plus exact failing test IDs. Tag each failure cluster (cargo_tracking vs ast_guard vs other vs combat_lab vs assets vs data vs integration_data). Establish the baseline at the current `main` HEAD. **Checkpoint:** baseline ledger committed to `findings/hidden_test_baseline.md`; no code changes.

### Phase 1: Triage `test_cargo_tracking.py`
~30 tests flagged by PROJ-431's completion report as pre-existing failures (cited in [Projects/active_projects/PROJ-436/plan.md:34-37](../PROJ-436/plan.md) and the post-435 discussion [AgentCoordination/Scratchpad/Discussion/20260517T230029Z_post-435-project-creation/arc01_001_claude_to_codex.md:56-61](../../../AgentCoordination/Scratchpad/Discussion/20260517T230029Z_post-435-project-creation/arc01_001_claude_to_codex.md)). After PROJ-436 Phase 3 (cargo manager API migration), many may now naturally pass. Per Codex's sample of the file ([tests/unit/strategy/data/test_cargo_tracking.py:98-264](../../../tests/unit/strategy/data/test_cargo_tracking.py)), most tests now exercise the manager API; only a few legacy `cargo_contents` assertions remain (lines 185-247). Run the file, classify each failure: (a) now passing — done; (b) test assertion wrong against current contract — fix the test; (c) test exposes a real bug — fix the production code; (d) test obsolete — delete with rationale in `decisions.md`. Commit per category. **Checkpoint:** zero failures in `test_cargo_tracking.py` via direct invocation.

### Phase 2: Triage `test_mutator_boundary_ast_guard.py`
~9 AST static-guard failures (`test_mutator_boundary[Fleet|Planet|Empire|ShipInstance]` etc.). Per Codex's sample ([tests/unit/strategy/data/test_mutator_boundary_ast_guard.py:52-216](../../../tests/unit/strategy/data/test_mutator_boundary_ast_guard.py)), this is an allowlist/AST-policy file. Audit each guard: is the invariant still valid post-PROJ-436? If yes, fix the code/test to satisfy it. If the invariant no longer applies, rewrite the guard. **Checkpoint:** zero failures in `test_mutator_boundary_ast_guard.py`.

### Phase 3: Triage remaining `tests/unit/strategy/data/` failures + 5 smaller hidden directories
Two clusters:
- (a) Long-tail in `tests/unit/strategy/data/` after Phases 1-2 (~26 failures expected; actual count from Phase 0 ledger).
- (b) The 5 smaller hidden directories: `tests/unit/combat_lab/` (24 files), `tests/unit/data/` (3), `tests/unit/assets/` (2), `tests/unit/ui/assets/` (1), `tests/integration/data/` (1). 31 files total. Failure counts captured by Phase 0.

Sub-phases per cluster of related failures. May surface that some combat_lab tests are unrelated to PROJ-436 surfaces and need their own triage. **Checkpoint:** `pytest <each of 6 hidden directories> -q -n 4` returns zero failures across the board.

### Phase 4: `pytest.ini` config flip + regression guard + docs + testmon wipe
- Edit `pytest.ini`:
  - Remove `data`, `combat_lab`, and `Assets` from `norecursedirs`. Keep the other tokens (`.*`, `build`, `dist`, `CVS`, `_darcs`, `{arch}`, `*.egg`, `venv`, `env`, `.venv`, `ShipThemes`) — they don't match any test directory.
  - **No `--ignore` flag is added.** `pytest.ini`'s `testpaths = tests` already prevents pytest from descending into the top-level `data/` / `Assets/` / `combat_lab/` directories during normal runs. Verified against `_pytest/main.py:455-458` (norecursedirs is basename glob, not anchored) and `_pytest/main.py:433-437` + `_pytest/pathlib.py:998-1004` (`--ignore` is cwd-relative, not config-root-relative). Removing the tokens is sufficient and avoids the cwd-relativity foot-gun.
- Add regression guard `tests/static_guards/test_no_hidden_test_files.py`: structural file-level check that every on-disk `test_*.py` under `tests/` is in the `pytest tests/ --collect-only` output set. **Scope note:** this is a "no hidden test files" guard, NOT a "catches all collection drift" guard — it can't detect `python_functions` / `python_classes` / collection-hook drops at the function level.
- Update `docs/guides/testing_infrastructure.md`: refresh the embedded `pytest.ini` snippet (around lines 187-194) to reflect the new `norecursedirs` value. Add a note explaining the rationale.
- One-time `.testmondata` rebuild: document in `decisions.md` and post-flip notes that the testmon persistence file may need a clean rebuild (`rm .testmondata && pytest tests/ --testmon`). `[unverified — testmon's docs don't mandate this, but a clean rebuild is the safe default after collection-membership changes.]`
- Run sharded suite. Expect count to jump from ~21233 to ~21359+ (21233 + 126 newly-collected, minus any tests already counted under other names). 

**Checkpoint:** sharded suite green at the new higher count; the regression guard green; doc snippet refreshed.

### Phase 5: PROJ-436 deferred-item bundle
Four small items deferred by PROJ-436 consults:
- **5a — Phase 3 finding (d) dataclass-introspection drift on `ShipInstance`**: clean up the seam if it's worth it; document as accepted if not.
- **5b — Phase 3 finding (e) legacy-kwarg constructor wrapper**: ~24 sites in ~7 test files. Mechanical sweep migrating `ShipInstance(consumable_levels=..., cargo_contents=...)` test fixtures to the manager-API path. Delete the wrapper at the end.
- **5c — Phase 6 production_engine test-mock residue**: ~6 inert `MagicMock` attributes for deleted Empire methods across 4 test files. Delete.
- **5d — Phase 5 D2 large-empire profiling**: only execute if a real perf signal emerges. Otherwise document as "no signal observed; deferred indefinitely."

Each lands as its own commit. **Checkpoint:** all four sub-items resolved or documented as accepted-tradeoff.

### Phase 6: Codex consult + verified-finding remediation
Per the standing end-of-project workflow. Frame: "Review PROJ-443's pytest.ini token removals + hidden-test triage + regression guard. Verify (a) all 126 hidden tests now run in the sharded suite; (b) no other `norecursedirs` token quietly hides anything else; (c) the regression guard correctly catches future drift of this class; (d) Phase 5 bundled cleanups landed cleanly; (e) the `.testmondata` and `docs/guides/testing_infrastructure.md` follow-ups are sound." Verify findings against code, remediate as needed.

## Verification
- [ ] All phase checklists complete
- [ ] Sharded suite collects every test under `tests/` (regression guard green)
- [ ] Sharded suite green at the new test count (~21359+)
- [ ] PROJ-436 deferred-item bundle resolved or documented
- [ ] `docs/guides/testing_infrastructure.md` snippet refreshed
- [ ] `.testmondata` rebuild documented
- [ ] Audit passed
- [ ] User verified
