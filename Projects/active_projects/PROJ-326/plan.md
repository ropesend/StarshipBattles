# PROJ-326: Test linter + SystemTreePanel coverage + StrategySessionFacade contract guard

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-326` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-326 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Linter for zero-game-import test files (preventive) | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. SystemTreePanel coverage check + StrategySessionFacade contract guard | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Audit zero-game-import survivors flagged by the linter | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-05-04
**Active Phase:** Planning complete — ready for Phase 1 (parallel-safe with PROJ-324 + PROJ-325)
**Last Action:** Project created from continuation review of PROJ-321/322/323
**Next Action:** Begin Phase 1 (linter implementation) — file-disjoint from PROJ-324 + PROJ-325, no blockers.
**Blockers:** None

## Overview

PROJ-321 deleted `tests/unit/test_modifier_logic.py` (103 LOC) because it had **zero `from game.*` imports** and reimplemented production modifier logic locally — testing nothing real. Both PROJ-321's design.md and the OpenCode 321-review independently flagged this as a class of bug worth preventing systematically: a linter rule. This project implements that linter, plus two smaller follow-ups also surfaced by the OpenCode 321-review: verify SystemTreePanel has integration coverage (replacing the deleted 664-LOC unit test), and restore the StrategySessionFacade public-API contract guard that was deleted alongside its trivial-pass tests.

## Goals

- **Phase 1:** Implement a pre-commit / CI hook that flags any new test file under `tests/` (excluding `tests/unit/tools/`, `tests/unit/combat_lab/`, `tests/data/`, etc. — see Phase 1 design for the exact exclusion list) with zero `from game.*` or `import game.*` statements. Add a tracked allowlist for legitimately-zero-game-import test files (testing tools or test infrastructure itself). Also migrate the 8 skipped TODO tests in [`tests/unit/data/test_test_infrastructure.py`](tests/unit/data/test_test_infrastructure.py) — the same pattern, currently held in pytest with TODO markers — into the new linter, closing both the prevention gap and the documented test debt.
- **Phase 2:** (a) Verify `SystemTreePanel` has adequate integration coverage now that PROJ-321 deleted its 664-LOC bypass-init unit test (PROJ-321 review MAJ-001). If missing, add minimal smoke coverage. (b) Restore the StrategySessionFacade public-API contract guard test that PROJ-321 deleted as part of `test_strategy_session_facade_public_api.py` (PROJ-321 review MIN-002).
- **Phase 3:** Run the new linter against the existing tree. Audit the ~41 zero-game-import test files PROJ-321's review found, focusing on the largest (`tests/unit/tools/test_validate_agent_surfaces.py` at 1102 LOC). Most are legitimate infrastructure tests; document each as either allowlisted or flagged for cleanup.

## Scope

**In:**
- New test linter (Phase 1)
- Migration of `tests/unit/data/test_test_infrastructure.py` 8 skipped TODOs into the linter (Phase 1)
- Allowlist file under `Tools/` (Phase 1)
- SystemTreePanel integration smoke coverage (Phase 2, only if missing)
- StrategySessionFacade public-API contract guard test (Phase 2)
- Audit of existing zero-game-import test files (Phase 3)

**Out:**
- UIWindow `bypass_init` flag — owned by PROJ-324
- LLMBackgroundCall completion Event — owned by PROJ-324
- 14 PROJ-322 deferral migrations — owned by PROJ-324
- PROJ-323 documentation corrections + Tasks 3.34/3.37 + RaceSetupScreen — owned by PROJ-325
- Test runtime reduction (Task 3.14 virtual_table sweep + mutable-mock fixture rescopes + Task 3.25 strategy_screen + DUP-001 / HLP-001 reconsideration) — owned by PROJ-327
- Pre-existing `tests/integration/strategy/test_mutual_join_rendezvous.py` flakiness — out of scope (separate ticket)

## Key Files

### Phase 1 (linter)

| File | Type | Change |
|------|------|--------|
| `Tools/lint_test_files.py` (NEW) | Production (tooling) | Linter script: scan `tests/` for files with zero `from game.*` / `import game.*` imports, comparing to allowlist. Exit non-zero with file list on flag. |
| `Tools/lint_test_files_allowlist.txt` (NEW) | Config | Initial allowlist of legitimately-zero-game-import test files. Identified by Phase 3 audit. |
| `tests/unit/tools/test_lint_test_files.py` (NEW) | Test | Smoke tests for the linter. |
| `.git/hooks/pre-commit` (USER-LOCAL) | Hook | Add a call to the linter. Note: pre-commit hooks are user-local; document the install procedure in `docs/guides/pre_commit_hooks.md` (or wherever the existing hook docs live). |
| `tests/unit/data/test_test_infrastructure.py` | Test | Remove the 8 skipped TODO tests (logic moved into the linter). |

### Phase 2 (SystemTreePanel + Facade contract)

| File | Type | Change |
|------|------|--------|
| `tests/integration/ui/test_system_tree_panel_smoke.py` (potentially NEW) | Test | Only added if Phase 2 Task 2.1 audit finds existing integration coverage inadequate. |
| `tests/unit/strategy/facade/test_strategy_session_facade_contract.py` (NEW) | Test | Restore the public-API contract guard test from PROJ-321 review MIN-002. Lightweight (~30 LOC) — exercises 3-5 public methods to retain regression value. |

### Phase 3 (audit)

| File | Type | Change |
|------|------|--------|
| (existing test files) | Audit | Categorize each linter-flagged file as allowlist (tools / infrastructure) or candidate for deletion / rewrite. Add to allowlist as appropriate. |
| `tests/unit/tools/test_validate_agent_surfaces.py` (1102 LOC) | Audit | OpenCode 321-review specifically flagged this for closer review. |

## Cross-Project Coordination

**Single source of truth for parallelism + file conflicts:** [`AgentCoordination/Scratchpad/plans/proj_324_325_326_327_parallelism_map.md`](AgentCoordination/Scratchpad/plans/proj_324_325_326_327_parallelism_map.md)

**Branch:** Same as PROJ-324 (`feat/03c-phase-aware-execution` unless user directs otherwise).

**Quick summary (full detail in the parallelism map):**

- **Fully parallel-safe with PROJ-324 entirely** (file-disjoint).
- **Fully parallel-safe with PROJ-325 entirely** (file-disjoint).
- Within PROJ-326: Phase 1 produces the linter; Phase 2 is independent of Phase 1; Phase 3 requires Phase 1 done.
- **Phase ordering preference:** Phase 1 first → Phase 2 + Phase 3 in parallel.

## Related Documents

- [design.md](design.md) — linter design + allowlist strategy + SystemTreePanel audit approach
- [decisions.md](decisions.md) — full decisions log
- [manifest.md](manifest.md) — per-task file manifest
- [`Reviews/results/2026-05-04_015902_consistency_proj-321-p0-dead-trivial-test-cleanup-completion-c_req-req_20260504_015901_0ba42a/report.md`](Reviews/results/2026-05-04_015902_consistency_proj-321-p0-dead-trivial-test-cleanup-completion-c_req-req_20260504_015901_0ba42a/report.md) — OpenCode review with MAJ-001 (SystemTreePanel) + MIN-002 (Facade contract) + linter recommendation
- [`AgentCoordination/Scratchpad/plans/proj_321_322_323_continuation_plan.md`](AgentCoordination/Scratchpad/plans/proj_321_322_323_continuation_plan.md) — original continuation plan

## Verification

- [ ] All phase checklists complete
- [ ] All tests passing (`python Tools/test_sharded/test_sharded.py`)
- [ ] Linter installed and runs cleanly against the current tree (with allowlist)
- [ ] `tests/unit/data/test_test_infrastructure.py` 8 TODO tests removed
- [ ] SystemTreePanel coverage gap closed (if any was found)
- [ ] StrategySessionFacade public-API contract guard restored
- [ ] User verified
