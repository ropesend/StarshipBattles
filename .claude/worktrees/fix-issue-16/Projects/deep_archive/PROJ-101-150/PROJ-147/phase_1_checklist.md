# Phase 1: Foundation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-147 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Address findings in the Foundation module (2 findings, 0 critical)
**Priority:** Normal

---

## Tasks

### Task 1.1: ADR-FND-001 - Research UI imports game.ui.renderer.cam [Medium]
**File:** `game/research/ui/research_scene.py` (OLD) -> `game/ui/research/research_scene.py` (NEW)
**Tests:** `pytest tests/unit/research/ tests/unit/ui/test_scene_protocol.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** PROJ-147 fix: Moved entire `game/research/ui/` directory to `game/ui/research/`.
This properly places the research UI in the UI layer where it belongs. The module now
directly imports Camera from game.ui.renderer.camera without any layer violation since
it's now within the UI layer. The late import workaround (`_create_default_camera`)
was removed as it's no longer needed.

### Task 1.2: ADR-FND-002 - Research UI subpackage uses pygame direc [Medium]
**File:** `game/research/ui/` (OLD) -> `game/ui/research/` (NEW)
**Tests:** `pytest tests/unit/research/`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** Fixed as part of Task 1.1. The research UI files now correctly reside in
`game/ui/research/` which is the canonical location for UI code. Using pygame directly
is now appropriate since the code is in the UI layer. Updated test files to reference
new module paths and removed outdated references to `_create_default_camera`.

---

## Files Changed

### New Files
- `game/ui/research/__init__.py`
- `game/ui/research/research_scene.py`
- `game/ui/research/research_renderer.py`
- `game/ui/research/research_controls.py`

### Deleted Files
- `game/research/ui/__init__.py`
- `game/research/ui/research_scene.py`
- `game/research/ui/research_renderer.py`
- `game/research/ui/research_controls.py`

### Updated Files
- `game/app.py` - Updated import path
- `tests/unit/research/test_research_scene_di.py` - Updated paths and test assertions
- `tests/unit/research/test_research_renderer.py` - Updated file path
- `tests/unit/research/research_scene/conftest.py` - Updated module path
- `tests/unit/research/research_scene/test_callbacks.py` - Updated patch paths
- `tests/unit/research/research_scene/test_initialization.py` - Updated patch paths
- `tests/unit/research/research_scene/test_interaction.py` - Updated patch paths
- `tests/unit/research/research_controls/conftest.py` - Updated module path
- `tests/unit/ui/test_scene_protocol.py` - Updated import path

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
