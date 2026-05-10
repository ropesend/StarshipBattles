# Consolidated Review: PROJ-380 Through PROJ-399

Date: 2026-05-09

Scope: one subagent reviewed each active project from PROJ-380 through PROJ-399. Each report evaluated plan goals, implementation evidence, literal checklist execution, and plan gaps or missed assumptions. Per-project reports are linked in the table below.

## Executive Verdict

The project arc is not audit-clean as a whole.

Most projects appear to have implemented their narrow code-removal or remediation goals, and many focused test runs passed. The consistent failure is project-system execution: plans, phase checklists, manifests, design docs, decisions logs, and `Projects/projects_index.md` frequently contradict the claimed completion state. Several projects also have real implementation or test failures that need code changes, not just bookkeeping.

Highest-priority implementation blockers:

1. PROJ-392: `NewGameSetupScreen._create_ui()` still calls a deleted `generate_default_save_name()` wrapper, creating a production `AttributeError` path.
2. PROJ-393: passenger-load validation still accepts missing `species_id`, while execution now no-ops that case.
3. PROJ-381: `SimulationBattleResolver` does not preserve battle context when `run_battle` raises `ValidationException`.
4. PROJ-382: audit readiness fails and the reviewer confirmed failing `GalaxySpatialIndex` tests, incomplete projectile event logging injection, facade registry-access drift, and a surviving `StrategyScreen.session` chain.
5. PROJ-386: save-format compatibility behavior remains in touched files despite the project goal of migration eradication.
6. PROJ-387 and PROJ-394: Galaxy state/delegate test doubles were not migrated; broad Galaxy data selectors still fail.

Most common plan/execution gap:

The plans often scoped the code edit but did not allocate enough explicit work for the protocol evidence: updating checklists, manifests, design docs, project index status, docs, full-suite receipts, and broad selectors that prove the deletion did not leave stale tests or docs behind.

## Per-Project Summary

| Project | Report | Consolidated Status | Key Findings |
|---|---|---|---|
| PROJ-380 | [PROJ-380_report.md](PROJ-380_report.md) | Pass with reservations | Dead import/static cleanup/consolidation goals appear met and focused tests passed. Not clean because touched production files remain over the 500 LOC ceiling, tracking artifacts are stale, stale import notes remain, and new provider code uses legacy `Optional[...]` typing. |
| PROJ-381 | [PROJ-381_report.md](PROJ-381_report.md) | Needs follow-up | Audit readiness passed, but `SimulationBattleResolver` misses `ValidationException` context preservation. Checklist test references are stale/non-runnable, and the UI still accepts raw engine errors in one path. |
| PROJ-382 | [PROJ-382_report.md](PROJ-382_report.md) | Fail, audit blocked | `validate_audit_ready.py` failed. Required focused `GalaxySpatialIndex` tests fail, projectile event logging injection is incomplete, facade registry access conflicts with current docs, and a public `StrategyScreen.session` chain survived. |
| PROJ-383 | [PROJ-383_report.md](PROJ-383_report.md) | Not audit-clean | Code migration and shim deletion goals appear met. Docs still describe the deleted `command_handlers.py` shim as current, and the project index still says `Planning`. |
| PROJ-384 | [PROJ-384_report.md](PROJ-384_report.md) | Not audit-ready | Deprecated static wrappers appear deleted and focused tests passed, but audit readiness fails because the final regression task remains unchecked and stale blocker text remains in `plan.md`. |
| PROJ-385 | [PROJ-385_report.md](PROJ-385_report.md) | Narrow implementation pass with caveats | Formula alias deletion and caller migration goals appear met. Checklist verification overclaims the grep/full-suite evidence, the initial zero-hit symbol check was too broad, and manifest paths are too imprecise. |
| PROJ-386 | [PROJ-386_report.md](PROJ-386_report.md) | Not audit-clean | The four named deletions landed, but old-save tolerance remains in touched files. Verification evidence is weaker than claimed, and the project index still says `Planning`. |
| PROJ-387 | [PROJ-387_report.md](PROJ-387_report.md) | Not audit-clean | Production private-index forwarders appear removed, but state/delegate unit tests still fail because test doubles were not migrated to the `GalaxyState` field shape. Metadata and manifest entries are stale. |
| PROJ-388 | [PROJ-388_report.md](PROJ-388_report.md) | Pass with bookkeeping reservations | `ModifierLogic` class removal and service injection goals appear met, with focused tests passing. Project completion metadata and a manifest/checklist path remain stale. |
| PROJ-389 | [PROJ-389_report.md](PROJ-389_report.md) | Not audit-ready | `score_planet_for_race` wrapper removal appears complete, but audit readiness fails because Task 1.6 remains partially unchecked, verification checklist items remain unchecked, and the project index says `Planning`. |
| PROJ-390 | [PROJ-390_report.md](PROJ-390_report.md) | Not audit-clean | Runtime/event logging API removal appears complete and the full sharded suite passed, but docs still tell agents/developers to use the deleted API and comments/checklist evidence are stale. |
| PROJ-391 | [PROJ-391_report.md](PROJ-391_report.md) | Pass with reservations | Consolidation goals appear substantially met and focused tests passed. The formation contract still preserves a loose `object` slot, new `FormationSpec` public methods use legacy typing, and completion evidence overstates literal grep/test status. |
| PROJ-392 | [PROJ-392_report.md](PROJ-392_report.md) | Fail, implementation bug | Audit readiness passed, but production code still calls a deleted New Game setup wrapper. Focused tests are green, so this is a coverage gap. The pathfinding deletion checklist and zero-hit assertions also conflict with current required strings. |
| PROJ-393 | [PROJ-393_report.md](PROJ-393_report.md) | Fail, audit blocked | Audit readiness and phase validators fail. Passenger-load validation accepts missing `species_id` even though execution now no-ops it. Phase 3 treated live contracts as legacy deletions and closed with deferrals. |
| PROJ-394 | [PROJ-394_report.md](PROJ-394_report.md) | Not audit-clean | `Galaxy.state` production goal mostly landed, but the project's own Galaxy data selector still fails due stale delegate test doubles. Manifest/checklist paths and facade wording remain stale. |
| PROJ-395 | [PROJ-395_report.md](PROJ-395_report.md) | Fail, not audit-ready | Phase 1 goals appear implemented and focused tests passed, but audit readiness fails. Phase 2 did not fully meet its stated goal because two of fourteen MAJOR findings were explicitly deferred. Required artifacts were not maintained. |
| PROJ-396 | [PROJ-396_report.md](PROJ-396_report.md) | Not audit-ready | Code goals mostly appear met and broad focused tests passed. Audit readiness fails because phase checklists, manifest, design doc, and project index were not kept in sync. Full regression claims are unsupported by checked project evidence. |
| PROJ-397 | [PROJ-397_report.md](PROJ-397_report.md) | Fail, not audit-ready | Code goals appear mostly implemented, but every phase checklist still says `Not Started` with unchecked tasks. Design/manifest are templates, Phase 3 contradicts the implemented `fleet_id` decision, and one test verifies a constructor only by introspection. |
| PROJ-398 | [PROJ-398_report.md](PROJ-398_report.md) | Not audit-ready | Five MAJOR remediation code/test goals appear addressed and focused tests passed. Audit validation fails because the checklist remains unchecked while the plan claims completion, and project artifacts are skeletal. |
| PROJ-399 | [PROJ-399_report.md](PROJ-399_report.md) | Fail, not audit-ready | Focused implementation goals pass, including UI/workshop collection. Audit readiness and phase validation fail because Phase 1 tasks are entirely unchecked and the project index still says `Planning`. |

## Cross-Project Findings

### 1. Literal project execution repeatedly failed

Many projects have code that appears substantially done, but the plan execution record is not trustworthy. The recurring failures are:

- `validate_audit_ready.py` or `validate_phase.py` failing after the project claims completion.
- Phase checklists marked `Complete` while subtasks remain unchecked.
- Phase checklists still marked `Not Started` after implementation.
- Empty task notes for completed work.
- `manifest.md`, `design.md`, and `decisions.md` left skeletal or stale.
- `Projects/projects_index.md` still reporting projects as `Planning`.
- Verification checklists claiming greps, full-suite runs, or zero-hit searches that were not literally true.

This affects PROJ-382, PROJ-384, PROJ-389, PROJ-393, PROJ-395, PROJ-396, PROJ-397, PROJ-398, and PROJ-399 most severely, and appears as lesser drift in many other projects.

### 2. Several plans scoped deletions too narrowly

Some projects removed the named wrapper or shim but did not account for adjacent compatibility behavior, docs, tests, or production callers:

- PROJ-386 removed named save migration targets but left old-save tolerance paths in touched files.
- PROJ-392 deleted a wrapper but missed a production call site.
- PROJ-393 removed fallback behavior without tightening validation to reject now-no-op orders.
- PROJ-390 removed the API but left docs and comments instructing current use.
- PROJ-383 removed the shim but left docs describing it as current.

### 3. Test updates were often too focused

The reviewers found multiple cases where narrow tests passed but broader selectors or real production paths failed:

- PROJ-392's focused tests missed the New Game setup path that still calls a deleted wrapper.
- PROJ-387 and PROJ-394 focused production checks passed, but Galaxy delegate/data selectors still fail.
- PROJ-382 has focused passing groups but a failing `GalaxySpatialIndex` batch.
- PROJ-397 has a constructor test that inspects signature shape without exercising construction.

### 4. Documentation consistency was not treated as part of completion

Several deletions changed current architecture or public/internal guidance, but docs were left stale:

- PROJ-383: docs still describe `game/strategy/engine/command_handlers.py` shim as current.
- PROJ-390: docs still direct use of deleted module-level event logging helpers.
- PROJ-395: error-handling docs still contradict EventBus architecture.
- PROJ-380: stale `pixel_to_hex` import notes remain after migration.

### 5. Initial plans often missed evidence and protocol work

The plans tended to define code targets, but did not always make these completion conditions explicit:

- Update `Projects/projects_index.md` and project current state.
- Regenerate or update manifests after actual touched files change.
- Keep design/decision docs synchronized with implementation choices.
- Verify broad selectors, not only target files.
- Re-run or explicitly document full-suite status when claiming full regression.
- Update docs when removing a current API or architecture path.

## Recommended Follow-Up Order

1. Fix direct code/behavior blockers:
   - PROJ-392 deleted wrapper call in New Game setup.
   - PROJ-393 passenger-load validation for missing `species_id`.
   - PROJ-381 `ValidationException` context preservation.
   - PROJ-382 implementation issues and failing focused tests.
   - PROJ-386 remaining save compatibility paths.
   - PROJ-387/PROJ-394 stale Galaxy delegate test doubles.

2. Reconcile project-system artifacts for failed audit gates:
   - PROJ-382, PROJ-384, PROJ-389, PROJ-393, PROJ-395, PROJ-396, PROJ-397, PROJ-398, PROJ-399.

3. Repair stale docs and manifests:
   - PROJ-383, PROJ-390, PROJ-395, PROJ-380, plus any project whose report flags stale `manifest.md`.

4. Re-run audit readiness and focused selectors after fixes:
   - `python Projects/scripts/validate_audit_ready.py PROJ-XXX`
   - `python Projects/scripts/validate_phase.py PROJ-XXX <phase>`
   - The focused commands listed in each subagent report.

5. Only after the direct blockers and project artifacts are clean, run the canonical full suite:
   - `python Tools/test_sharded/test_sharded.py`

