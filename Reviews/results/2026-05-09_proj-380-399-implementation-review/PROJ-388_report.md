# PROJ-388 Implementation Review

**Project:** PROJ-388 - Legacy removal: `ModifierLogic` deprecated class wrapper  
**Review date:** 2026-05-09  
**Reviewer:** Codex  
**Protocol:** Protocol 04 skeptical post-implementation review

## Verdict

**Pass with project-bookkeeping reservations.**

The implementation meets the core code goal: the deprecated `ModifierLogic` class is gone, live callers no longer import or call it, and the affected UI builder surfaces now receive `ModifierLogicService` through required constructor injection. Focused tests passed.

This is not perfectly audit-clean as a project artifact: the project index still says `Planning`, the plan's verification checklist is still unchecked, task notes are empty, and the manifest/checklist still point at a non-existent `game/ui/panels/modifier_editor_panel.py` path instead of the actual `game/ui/panels/builder_widgets.py` location.

## Validation Result

- `python Projects/scripts/validate_audit_ready.py PROJ-388`: **PASSED**
  - Warning: `Projects/projects_index.md:18` still marks PROJ-388 as `Planning`.
- `python Projects/scripts/validate_phase.py PROJ-388 1`: **PASSED**
  - Warnings: Task 1.1, 1.2, and 1.3 are complete but have empty notes.

## Tests And Checks Run

- `git status --short`
  - Pre-existing modified file: `AgentCoordination/generated/skill_usage/by_install/21f3651f7ffa42f8acdab05bd0a3c1bf.json`
  - Existing untracked review directory: `Reviews/results/2026-05-09_proj-380-399-implementation-review/`
- `rg -n "from game\.ui\.screens\.builder\.modifier_logic import ModifierLogic\b|class ModifierLogic\b" game tests combat_lab`
  - **Zero hits**
- `rg -n "ModifierLogic\.(init_service|set_service|_get_service|is_modifier_allowed|get_mandatory_modifiers|is_modifier_mandatory|get_initial_value|ensure_mandatory_modifiers|get_local_min_max|calculate_snap_value)" game tests combat_lab`
  - **Zero hits**
- `rg -n "\bModifierLogic\b" game tests combat_lab`
  - Only comments/docstrings remain; no live import, class definition, instantiation, or call.
- `pytest tests/unit/ui/panels/test_modifier_editor_panel.py tests/unit/ui/panels/test_builder_widgets.py tests/unit/ui/screens/builder/test_modifier_row.py tests/unit/ui/screens/builder/test_modifier_logic_service.py tests/unit/ui/screens/builder/test_modifier_logic_smart_floor.py tests/unit/ui/test_detail_panel_rendering.py`
  - **62 passed**
- `pytest tests/ -k modifier_editor`
  - **3 passed**

I did not rerun the full sharded suite in this review. The plan records a prior sharded result of `19084 passed / 3 pre-existing failures`, but this report only independently verifies the focused PROJ-388 surface.

## Plan Goals Vs Actual Implementation

### Goal: migrate `ModifierLogic` consumers to `ModifierLogicService`

**Met.** The initial project text names `ModifierEditorPanel`, and the actual implementation correctly handled the broader dependency chain:

- `game/ui/panels/builder_widgets.py:32` requires `modifier_logic: ModifierLogicService` in `ModifierEditorPanel.__init__`.
- `game/ui/panels/builder_widgets.py:232` passes the injected service into `ModifierControlRow`.
- `game/ui/screens/builder/modifier_row.py:41` requires `modifier_logic` in `ModifierControlRow.__init__`.
- `game/ui/screens/builder/detail_panel.py:31` requires keyword-only `modifier_logic` in `ComponentDetailPanel.__init__`.
- `game/ui/screens/workshop_screen.py:72` constructs one `ModifierLogicService(context.registries)`.
- `game/ui/screens/workshop_screen.py:260-266` wires it into `ModifierEditorPanel`.
- `game/ui/screens/workshop_screen.py:296-300` wires it into `ComponentDetailPanel`.

### Goal: delete the deprecated `ModifierLogic` class

**Met.** `game/ui/screens/builder/modifier_logic.py:34` now defines only `ModifierLogicService`; there is no `class ModifierLogic` in live code. Exact import/class/call searches across `game`, `tests`, and `combat_lab` returned zero live-code hits for the deleted class surface.

### Goal: resolve LEG-03-015 `calculate_snap_value`

**Met as scoped.** The original audit described `ModifierLogic.calculate_snap_value` as a pass-through wrapper to `ModifierLogicService.calculate_snap_value`. The wrapper call surface is gone. The retained `ModifierLogicService.calculate_snap_value` at `game/ui/screens/builder/modifier_logic.py:150` is the canonical UI-layer pure function, not the deleted compatibility wrapper.

### Out of scope: `ModifierService` vs `ModifierLogicService`

**Respected.** The implementation did not attempt the cross-system Pair 4 consolidation that `Projects/active_projects/PROJ-388/design.md:26` explicitly excludes.

## Literal Checklist Execution

- Task 1.1 is operationally satisfied: live references were enumerated well enough to migrate the actual three production consumers plus bootstrap. However, the checklist has no notes despite requiring additional sites to be recorded, and `validate_phase.py` warns about empty notes.
- Task 1.2 is satisfied: consumers use constructor-injected service instances, with no observed default/fallback dependency swallowing.
- Task 1.3 is satisfied: the `ModifierLogic` class is deleted and no old class imports remain.
- The plan-level verification checklist remains unchecked at `Projects/active_projects/PROJ-388/plan.md:51-54`, even though the current state says the phase is complete.

## Plan Gaps And Missed Assumptions

- The initial plan underestimated the call graph. It expected `1 prod + 1 test` and named `ModifierEditorPanel._build_panels`, but the actual migration needed `ModifierEditorPanel`, `ModifierControlRow`, `ComponentDetailPanel`, the workshop bootstrap, and multiple tests. The implementation handled this, but the manifest was not updated.
- `Projects/active_projects/PROJ-388/manifest.md:8` and `Projects/active_projects/PROJ-388/phase_1_checklist.md:23` name `game/ui/panels/modifier_editor_panel.py`, which does not exist. The actual `ModifierEditorPanel` class lives in `game/ui/panels/builder_widgets.py:25`.
- The plan did not explicitly require post-implementation synchronization of `Projects/projects_index.md`, so the audit-readiness validator only warns while the index remains stale.

## Findings

### Minor: project completion metadata is stale

**Evidence:** `Projects/projects_index.md:18`, `Projects/active_projects/PROJ-388/plan.md:51-54`  
**Impact:** The code is implemented, but the project artifacts are inconsistent: the index still says `Planning`, and the verification checklist still has unchecked items for phase completion, tests, and no remaining imports. This weakens audit traceability and makes automation under-report completion state.  
**Fix direction:** Sync the project index and mark verified checklist items after audit acceptance; leave `User verified` unchecked until the user actually verifies.

### Minor: manifest/checklist target path is stale

**Evidence:** `Projects/active_projects/PROJ-388/manifest.md:8`, `Projects/active_projects/PROJ-388/phase_1_checklist.md:23`, `game/ui/panels/builder_widgets.py:25`  
**Impact:** The initial plan points reviewers and future workers at a non-existent file. The implementation found and migrated the real class, so this is not a code blocker, but it is a plan-quality miss and should be corrected before archival if project artifacts are expected to remain authoritative.  
**Fix direction:** Update the manifest/checklist to reference `game/ui/panels/builder_widgets.py` and note the extra migrated consumers.

## Residual Risks

- Full-suite regression was not independently rerun for this review. Focused UI/builder tests passed, and the plan records a prior sharded run with only pre-existing failures.
- `ModifierLogicService` still has known out-of-scope overlap with simulation-layer `ModifierService`; that was intentionally excluded and remains a future architectural decision.
- `game/ui/screens/builder/modifier_logic.py` now contains only `ModifierLogicService`. This filename is slightly stale but not worth renaming inside PROJ-388 because it would expand the scope across many imports.
