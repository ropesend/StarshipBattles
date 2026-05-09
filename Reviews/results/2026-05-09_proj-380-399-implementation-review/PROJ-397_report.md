# PROJ-397 Implementation Review

**Date:** 2026-05-09  
**Scope:** Skeptical post-implementation review of PROJ-397 against Protocol 04 principles and the requested extra criteria: plan goals, literal checklist execution, and initial plan gaps.

## Verdict

**FAIL - not audit-ready.**

The implementation commits referenced by `plan.md` exist, and the main code goals appear substantially implemented: the dead `BattleScreen` Combat Lab fields were removed, the dead `format_planet_info(view=None)` per-species branch was deleted, and the five F-07 `ResourceCatalog.from_json()` module-level targets were converted to cached helpers.

However, PROJ-397 cannot be accepted as audit-clean. `validate_audit_ready.py` fails hard because every phase checklist still says `Not Started` and all task subtasks remain unchecked, while `plan.md` simultaneously claims all phases are complete. The design and manifest files are still template placeholders. There are also literal execution gaps: the Phase 3 checklist still requires deleting `fleet_id`, but the recorded decision and code intentionally kept `fleet_id` and deleted `entity_type` instead; and the F-05 constructor test added for a MAJOR review finding checks the signature by introspection rather than exercising the real constructor.

## Validation Result

Command:

```text
python Projects/scripts/validate_audit_ready.py PROJ-397
```

Result: **FAILED** with 10 errors and 1 warning.

Reported blockers:

- Phase 1: `Not Started`
- Phase 2: `Not Started`
- Phase 3: `Not Started`
- Phase 1 tasks 1.1-1.5 have unchecked subtasks.
- Task completion check reports 11 tasks with incomplete subtasks.
- `Projects/projects_index.md` status warning: `Planning`

Additional phase validators:

- `python Projects/scripts/validate_phase.py PROJ-397 1` -> **FAILED**, 5 task errors.
- `python Projects/scripts/validate_phase.py PROJ-397 2` -> **FAILED**, 3 task errors.
- `python Projects/scripts/validate_phase.py PROJ-397 3` -> **FAILED**, 3 task errors.

Per Protocol 04, this means the project should be returned to implementation/closeout bookkeeping before any audit-pass claim.

## Tests Run

Focused pytest command:

```text
pytest tests/unit/ui/test_battle_screen.py tests/unit/ui/test_battle_screen_extended.py tests/unit/ui/test_battle_screen_simulation.py tests/unit/test_lab/test_visual_run.py tests/unit/ui/screens/test_strategy_detail_fmt.py tests/unit/ui/screens/test_planet_selection_window.py tests/unit/ui/screens/test_empire_build_queue_window.py tests/unit/strategy/engine/test_empire_economy_calculator.py tests/unit/strategy/engine/test_construction_forecast.py tests/unit/ui/panels/test_empire_treasury_panel.py tests/unit/ui/screens/test_planet_list_window.py tests/unit/strategy/data/test_planet_gen.py -q
```

Result:

```text
410 passed in 5.20s
```

Static checks performed:

- `rg` for `test_mode`, `test_scenario`, `test_tick_count`, `test_completed`, `headless_start_time` in the two Phase 1 production files found no live-field references, only a retirement note at `game/ui/screens/test_lab/screen.py:330`.
- `rg` for `entity_type: str = "fleet"` in the order-queue command DTOs found no current production hit.
- `rg` confirmed the five F-07 target files now call `ResourceCatalog.from_json()` inside cached helper functions.
- `rg` confirmed the deleted `format_planet_info()` branch is now only described in comments/tests, not implemented as an `elif view is None` runtime path.

Full sharded suite was **not run** because the required pre-audit validation failed; Protocol 04 says not to proceed as if this is an audit-ready project after that failure.

## Plan Goals Vs Actual Implementation

### Phase 1: CRITICAL F-01

**Goal:** Delete dead `BattleScreen` Combat Lab fields and remove dependent dead branches.

**Actual:** Code goal appears met.

Evidence:

- `game/ui/screens/battle_screen.py:117-119` retains only `headless_mode`.
- `game/ui/screens/battle_screen.py:481-483` delegates `is_battle_over()` directly to `_battle_service`.
- `game/ui/screens/battle_screen.py:667-669` no longer has a test-mode summary branch.
- `game/ui/screens/test_lab/screen.py:326-334` documents that the old `test_scenario` capture path was retired.

Checklist caveat: Phase 1 remains `Not Started` with every subtask unchecked in `Projects/active_projects/PROJ-397/phase_1_checklist.md:3` and `:14-49`.

### Phase 2: MAJOR F-02 Through F-07

**Goal:** Close all 6 MAJOR findings from the PROJ-393 review.

**Actual:** Mostly implemented in code, but literal evidence is incomplete.

Evidence:

- F-02/F-03/F-04: `game/strategy/engine/commands/__init__.py:96-106` rewrites `ClearOrdersCommand` around the fleet-only path, and `:283-308` shows `DeleteOrderCommand`/`ReorderOrderCommand` without the old `entity_type` field.
- F-05: `tests/unit/ui/screens/test_empire_build_queue_window.py:206-237` verifies `facade` is a required keyword-only constructor parameter.
- F-06: the old `# NOQA: legacy-retained` block is gone from `game/ui/screens/battle_screen.py:117-119`.
- F-07: the five named files now use cached helpers, for example `game/strategy/data/planet_gen.py:20-23`, `game/strategy/engine/construction_forecast.py:20-23`, `game/strategy/engine/empire_economy_calculator.py:19-22`, `game/ui/panels/empire_treasury_panel.py:23-31`, and `game/ui/screens/planet_list_window.py:26-29`.

Checklist caveat: Phase 2 remains `Not Started` with every subtask unchecked in `Projects/active_projects/PROJ-397/phase_2_checklist.md:3` and `:13-28`.

### Phase 3: Deferred Items

**Goal:** Close LEG-02-004 and LEG-02-006.

**Actual:** LEG-02-006 appears implemented; LEG-02-004 was materially redesigned but the plan/checklist were not updated.

Evidence:

- `Projects/active_projects/PROJ-397/decisions.md:10` records the decision to keep `fleet_id` and delete the dead `entity_type` field instead.
- `game/strategy/engine/commands/__init__.py:106`, `:292-293`, and `:306-308` show `fleet_id` remains on the fleet-order command DTOs.
- `game/ui/screens/strategy_detail_fmt.py:227-264` shows the old single-line per-species `view is None` branch is deleted; owned planets without a view now skip per-species lines.
- `game/ui/screens/planet_selection_window.py:216-227` fetches a demographic view from the facade for owned planets and passes it to `PlanetReportPanel`.
- Production callers pass the facade at `game/ui/screens/strategy_windows/selection_prompts.py:49-53` and `game/ui/screens/build_queue_screen.py:806-816`.

Checklist caveat: Phase 3 remains `Not Started` with every subtask unchecked in `Projects/active_projects/PROJ-397/phase_3_checklist.md:3` and `:25-53`.

## Literal Checklist Execution

The literal project records are not trustworthy enough to close:

- `Projects/active_projects/PROJ-397/plan.md:6-8` marks all phases `Complete`.
- `Projects/active_projects/PROJ-397/plan.md:12` says all three phase commits are complete.
- `phase_1_checklist.md:3`, `phase_2_checklist.md:3`, and `phase_3_checklist.md:3` all still say `Not Started`.
- Every phase checklist still has unchecked task and phase-completion boxes.
- `Projects/active_projects/PROJ-397/plan.md:45-48` leaves final verification unchecked.
- The phase checklists still require full sharded-suite verification, but no completed checklist evidence records that it ran.

This is not just bookkeeping noise: the audit validator correctly blocks the project because the authoritative completion artifacts disagree with `plan.md`.

## Plan Gaps And Missed Assumptions

1. **LEG-02-004 was misframed at the start.**  
   `plan.md:28` and `phase_3_checklist.md:21-31` frame the task as deleting `fleet_id` or migrating to `entity_id/entity_type`. Implementation analysis later found the actual dead field was `entity_type`, while `fleet_id` remained the canonical fleet-command identity. That decision is reasonable, but the plan/checklist were never revised to match it.

2. **Phase 2 was underspecified.**  
   `plan.md:24-25` says “themes likely include” rather than enumerating F-02 through F-07. `phase_2_checklist.md:13-17` similarly says to read the MAJOR items and apply recommendations without recording which findings were actually closed. That makes literal audit verification harder than necessary.

3. **The design and manifest artifacts never became real project artifacts.**  
   `design.md:8`, `:14`, `:20`, and `:23` still contain placeholders. `manifest.md:10` still contains `path/to/file.py`. The implementation touched many production and test files, but the manifest never recorded them.

4. **The initial plan did not explicitly require tests for the new `PlanetSelectionWindow` facade behavior.**  
   The code path exists at `planet_selection_window.py:216-227`, but `tests/unit/ui/screens/test_planet_selection_window.py` has no direct assertion that a facade is stored, queried for owned planets, skipped for unowned planets, and forwarded as `view=`.

## Findings

### BLOCKER: Audit readiness fails because phase artifacts are not complete

**Evidence:** `Projects/active_projects/PROJ-397/plan.md:6-12`, `phase_1_checklist.md:3`, `phase_2_checklist.md:3`, `phase_3_checklist.md:3`, plus the failed `validate_audit_ready.py` and `validate_phase.py` runs.

`plan.md` says all phases are complete, but every phase checklist says `Not Started` and all subtasks remain unchecked. Protocol 04 requires pre-audit validation to pass before an audit can proceed. This blocks project acceptance regardless of the current code state.

### MAJOR: Project design and manifest are stale templates

**Evidence:** `Projects/active_projects/PROJ-397/design.md:8`, `:14`, `:20`, `:23`; `Projects/active_projects/PROJ-397/manifest.md:10`; `Projects/active_projects/PROJ-397/plan.md:43`.

The project touched at least 17 files across three commits, but `manifest.md` still has placeholder rows and `design.md` still has placeholder analysis text. `plan.md` also leaves `PlanetSelectionWindow` as “TBD per Phase 3” even though Phase 3 implemented it. This undermines the project-system contract that plan, design, decisions, and manifest stay synchronized.

### MAJOR: Phase 3 checklist contradicts the implemented `fleet_id` decision

**Evidence:** `Projects/active_projects/PROJ-397/phase_3_checklist.md:21-31` and `:51`; `Projects/active_projects/PROJ-397/decisions.md:10`; `game/strategy/engine/commands/__init__.py:96-106`, `:283-308`.

The checklist still requires “Full `fleet_id` field deletion” and “field deleted, callers migrated.” The actual implementation intentionally kept `fleet_id` and removed `entity_type`. That may be the better technical answer, but the literal plan/checklist were not updated, so a future auditor cannot tell whether this is an approved scope correction or an incomplete task.

### MAJOR: F-05 test coverage does not literally exercise the real constructor

**Evidence:** Source review recommendation at `Reviews/results/2026-05-09_002247_code_proj-393-test-injection-legacy-fallbacks-comment-c_req-req_20260509_002246_bca19e/report.md:103-114`; implementation test at `tests/unit/ui/screens/test_empire_build_queue_window.py:206-237`; helper bypass at `tests/unit/ui/screens/test_empire_build_queue_window.py:63-65`.

F-05 said no test calls `EmpireBuildQueueWindow()` through the real constructor and recommended a test that asserts a `TypeError` when instantiated without `facade=`. The added test verifies the signature by introspection, which does pin the required keyword-only parameter, but it still does not instantiate the constructor. This closes the core signature risk, but not the literal review finding.

### MINOR: `PlanetSelectionWindow` facade threading lacks direct unit coverage

**Evidence:** implementation at `game/ui/screens/planet_selection_window.py:147`, `:216-227`; no matching `facade`/`get_colony_demographic_view` assertions in `tests/unit/ui/screens/test_planet_selection_window.py`.

The production code appears straightforward and the focused tests pass, but the new behavior that replaces the deleted `view=None` branch is not directly pinned at the window level. A regression could drop the facade lookup or pass `view=None` for owned planets while `format_planet_info` tests still pass.

## Residual Risks

- Full sharded suite was not run in this review because pre-audit validation failed.
- Several touched production files remain far over the 500 LOC convention: `build_queue_screen.py` 847 LOC, `test_lab/screen.py` 742 LOC, `strategy_detail_fmt.py` 674 LOC, and `battle_screen.py` 669 LOC. This review did not require decomposing them, but continued edits in those files carry maintainability risk.
- `game/ui/screens/builder/stat_rows_dynamic.py:177` and `game/ui/utils/resource_display.py:54` still call `ResourceCatalog.from_json()` at call time. These were outside PROJ-397's F-07 module-level target list, but they remain nearby cleanup candidates.

## Files Changed By This Review

- `Reviews/results/2026-05-09_proj-380-399-implementation-review/PROJ-397_report.md`
