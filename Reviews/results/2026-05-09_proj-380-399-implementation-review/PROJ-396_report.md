# PROJ-396 Implementation Review

**Date:** 2026-05-09  
**Reviewer:** Codex  
**Scope:** Skeptical post-implementation review of PROJ-396 against Protocol 04 principles and the user's additional criteria.

## Verdict

**Not audit-ready.** The implementation goals mostly appear met in code, and focused tests passed, but the project cannot pass audit because the project artifacts still say the phases are not started, the phase subtasks are unchecked, the manifest/design artifacts are placeholders, and `Projects/projects_index.md` still marks PROJ-396 as `Planning`.

This is not just cosmetic bookkeeping. Protocol 04 makes `validate_audit_ready.py` the pre-audit gate, and PROJ-396 fails that gate.

## Validation Result

Command:

```powershell
python Projects/scripts/validate_audit_ready.py PROJ-396
```

Result: **FAILED** with **10 errors, 1 warning**.

Key failures:

- Phase 1, 2, and 3 are reported as `Not Started`.
- 9 tasks have incomplete subtasks.
- `Projects/projects_index.md` status is still `Planning`.

Additional phase validation:

- `python Projects/scripts/validate_phase.py PROJ-396 1` -> failed, 3 errors.
- `python Projects/scripts/validate_phase.py PROJ-396 2` -> failed, 3 errors.
- `python Projects/scripts/validate_phase.py PROJ-396 3` -> failed, 3 errors after rerunning with `PYTHONIOENCODING=utf-8` to avoid a Windows console encoding issue on the `<=` symbol.

## Tests Run

Passed:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
pytest -p no:cacheprovider tests/static_guards/test_facade_bypass_guard.py tests/unit/strategy/engine/test_game_session_from_dict.py tests/unit/ui/panels/test_build_queue_portraits.py tests/unit/ui/screens/test_build_queue_panel_factory.py tests/unit/ui/screens/test_strategy_build_queue_manager.py -q
```

Result: **691 passed**.

Passed:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
pytest -p no:cacheprovider tests/ -k superweapon -q
```

Result: **394 passed**.

Not run:

- `python Tools/test_sharded/test_sharded.py`

Reason: this review was constrained to a single write target. The sharded runner has no no-write mode and writes duration/baseline/shard artifacts under the repo, including `AgentCoordination/generated/test_baseline/...`, so I did not run it.

## Plan Goals vs Actual Implementation

### Phase 1: CRITICAL Findings

**CRIT-001: Extend facade-bypass guard to `_session.handle_command(...)`**  
Status: **Met in code.**

Evidence:

- `tests/static_guards/test_facade_bypass_guard.py:63-80` defines `_SESSION_ATTR_NAMES = {"session", "_session"}` and matches both forms.
- `tests/static_guards/test_facade_bypass_guard.py:167-205` adds the targeted `strategy_screen.py` `self._session.handle_command(...)` check.
- `tests/static_guards/test_facade_bypass_guard.py:208-235` adds a positive-control matcher test for the private `_session` form.

**CRIT-002: Restore mutator services in `GameSession.from_dict()`**  
Status: **Met in code.**

Evidence:

- Constructor pattern remains at `game/strategy/engine/game_session.py:104-123`.
- `from_dict()` now mirrors that pattern at `game/strategy/engine/game_session.py:486-523`, constructing fleet, planet, empire, and ship mutators and passing them to `TurnEngineConfig.create_default()`.
- Regression coverage exists at `tests/unit/strategy/engine/test_game_session_from_dict.py:100-145`.

Literal caveat: Task 1.2 asked for a deserialized-session command-handler call, e.g. `add_move_order_if_needed`. The regression test directly exercises `restored.fleet_mutator.set_path(...)`; that covers the missing mutator service but is not the exact command-handler path specified in the checklist.

### Phase 2: MAJOR Findings

Status: **Mostly met in code, not auditable from project artifacts.**

Supported observations:

- MAJ-001 appears fixed: `StrategyScreen.session` setter rebuilds the facade at `game/ui/screens/strategy_screen.py:247-248`.
- MAJ-002 appears fixed: `BuildQueueScreen` takes `theme_id_supplier`, not `portrait_session`, at `game/ui/screens/build_queue_screen.py:60-64` and wires `BuildQueuePortraitLoader(design_library, self._theme_id_supplier)` at `game/ui/screens/build_queue_screen.py:126-130`.
- MAJ-002 loader side appears fixed: `BuildQueuePortraitLoader` stores a narrow callable at `game/ui/panels/build_queue_portraits.py:77-99`.
- MAJ-003 appears fixed: `BuildQueuePanelFactory` requires `facade` and `empire`, with no `session` parameter, at `game/ui/screens/build_queue_panel_factory.py:92-129`.
- MAJ-004 named build-queue manager paths appear fixed: `StrategyBuildQueueManager` passes `theme_id_supplier=self._active_theme_id` at `game/ui/screens/strategy_build_queue_manager.py:111-124` and uses `facade.get_save_path()` at `game/ui/screens/strategy_build_queue_manager.py:268-274`.
- MAJ-006 appears fixed: Pattern #36 now explicitly forbids facade-bypass shims and renamed kwargs at `docs/02_PATTERNS.md:770-777`.
- MAJ-008/009 appear fixed or already resolved: `rg` found no live `game.strategy.engine.command_handlers` imports under `game/` or `tests/`.

Project-artifact caveat: Phase 2 has no per-MAJOR checklist entries, and all Phase 2 checkboxes remain unchecked, so the plan does not provide a literal execution trail for the 9 findings.

### Phase 3: Deferred Task 5.4 Superweapon Decomposition

Status: **Met in code, with plan wording drift.**

Evidence:

- `game/strategy/engine/superweapon_order_processor.py` is now **434 LOC**, under the 500 LOC ceiling.
- Five extracted handler modules exist under `game/strategy/engine/superweapon_handlers/`.
- `game/strategy/engine/superweapon_order_processor.py:370-440` now delegates each `process_*` method to the handler package.
- `game/strategy/engine/superweapon_handlers/__init__.py:1-8` documents the explicit `processor` parameter approach.
- `pytest tests/ -k superweapon -q` passed with 394 tests.

Plan wording caveat: `phase_3_checklist.md` frames Option B as a state-bag/dispatcher class, while the implementation uses free functions taking the processor as an explicit first parameter. That matches the source review's MAJ-005 recommendation, but the plan should have been revised to make this literal execution path explicit.

## Literal Checklist Execution

This is the main audit blocker.

- `plan.md:6-8` marks all three phases `Complete`.
- `plan.md:11-12` says the project is in Closeout and all three phases are complete.
- `phase_1_checklist.md:3`, `phase_2_checklist.md:3`, and `phase_3_checklist.md:3` still say `Status: Not Started`.
- Every listed task checkbox in the phase checklists remains unchecked.
- `plan.md:43-45` still leaves the overall completion checklist unchecked.
- `manifest.md:10-11` still contains placeholder rows (`path/to/file.py`, `tests/path/to/test_file.py`) instead of the touched files.
- `design.md:7-23` still contains template placeholders for analysis, architecture, risks, and opportunities.
- `Projects/projects_index.md:10` still marks PROJ-396 as `Planning`.

## Plan Gaps and Missed Assumptions

- The initial `design.md` was never filled in. That means the plan lacked a real architecture/risk baseline for a remediation project touching UI facade boundaries, save/load reconstruction, docs, and turn-order superweapon execution.
- Phase 2 collapsed 9 MAJOR review findings into one broad "address each MAJOR" task. That made literal execution hard to audit; each major finding should have had its own checklist item and evidence target.
- The manifest was never updated, even though the project touched production, tests, and docs. That undermines conflict detection and post-implementation traceability.
- The plan assumed full-suite verification could be represented in `plan.md`, but it did not preserve a receipt or update checklists. Under a review-only single-write constraint, I could not safely rerun the sharded suite because the runner writes repo artifacts.
- Phase 3's accepted implementation path was not one of the two options as written in the checklist. It is defensible, but the plan should have been updated when the project chose the explicit-processor free-function extraction.

## Findings

### BLOCKER: Audit readiness fails because project state and checklists contradict the implementation

Protocol 04 requires `validate_audit_ready.py` before audit. PROJ-396 fails with 10 errors, and the failure is consistent with the files: `plan.md` claims all phases complete while every phase checklist still says `Not Started` and has unchecked subtasks. This prevents a clean audit verdict even though the code changes are largely present.

Evidence:

- `Projects/active_projects/PROJ-396/plan.md:6-12`
- `Projects/active_projects/PROJ-396/phase_1_checklist.md:3-38`
- `Projects/active_projects/PROJ-396/phase_2_checklist.md:3-33`
- `Projects/active_projects/PROJ-396/phase_3_checklist.md:3-49`
- `Projects/projects_index.md:10`

### MAJOR: Project evidence artifacts were not maintained

The manifest and design document are still templates. That means the project lacks the basic evidence needed to understand intended file scope, implementation risk, and architectural rationale. This is especially problematic for a remediation project whose goal was to close prior audit findings.

Evidence:

- `Projects/active_projects/PROJ-396/manifest.md:10-11`
- `Projects/active_projects/PROJ-396/design.md:7-23`

### MAJOR: Full regression claim is unsupported by checked project evidence

`plan.md` says full regression preserved baseline with one unrelated failure, but the phase checklists still leave the full-suite subtasks unchecked. I did not find a project-local receipt. Since the canonical sharded runner writes repo artifacts, I did not rerun it under this review's single-write constraint.

Evidence:

- `Projects/active_projects/PROJ-396/plan.md:12`
- `Projects/active_projects/PROJ-396/phase_2_checklist.md:27`
- `Projects/active_projects/PROJ-396/phase_3_checklist.md:42`

### MINOR: `from_dict()` regression test does not literally exercise a command-handler path

The implementation restores the mutators, and the direct `set_path` regression passed. However, Task 1.2 asked for a deserialized session followed by a command handler call that uses `session.fleet_mutator.set_path(...)`. The current PROJ-396 test directly calls `restored.fleet_mutator.set_path(...)`, which is close but not the literal path the checklist asked for.

Evidence:

- `Projects/active_projects/PROJ-396/phase_1_checklist.md:25`
- `tests/unit/strategy/engine/test_game_session_from_dict.py:119-145`

### MINOR: New superweapon handler modules use legacy typing syntax on exported functions

The newly introduced `game/strategy/engine/superweapon_handlers/` package exports process functions, but those signatures still use `Optional[List[...]]` and `Optional[Dict[...]]` rather than PEP 604 syntax. The project convention requires modern syntax in new/touched public signatures.

Evidence:

- `game/strategy/engine/superweapon_handlers/__init__.py:18-24`
- `game/strategy/engine/superweapon_handlers/open_warp_point.py:8`
- `game/strategy/engine/superweapon_handlers/open_warp_point.py:24-31`

## Residual Risks

- I did not run the full sharded suite because of the single-write-target constraint and the runner's repo writes.
- Focused tests support the core code changes, but they do not substitute for the project audit gate.
- Broader UI facade session reads still exist outside the PROJ-396 named build-queue scope; `StrategyScreen.session` itself documents those as deferred migration work. I did not treat them as PROJ-396 failures.
- The project could be functionally correct but still fail closure or future audit automation until the checklists, manifest, design document, and index are synchronized.
