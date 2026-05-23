# Phase 5: Audit remediation (Codex consult 2026-05-23)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-491 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Resolve the three VERIFIED + IN-SCOPE findings from the Codex mid-project-review audit (response.md in `AgentCoordination/Scratchpad/Consult/20260523T144503Z_audit-PROJ-491/`). Verification table at `findings/audit_verification.md`.

---

## Tasks

### Task 5.1: Restore `Game(args)` positional-call coverage [Simple]
**File:** `tests/unit/test_app_public_api.py`
**Tests:** `pytest tests/unit/test_app_public_api.py -v`

- [x] Add a second behavioral test (e.g. `test_game_constructs_with_args_positional`) that constructs `Game(<some-args>)` positionally to lock the `args=None`-default-but-accepting-an-arg contract that the file header still documents at lines 8-9. Use the same headless-safe pygame setup + cleanup pattern as `test_game_constructs_with_no_args`.
- [x] Pass a minimal args object (e.g. `argparse.Namespace()` or `None` explicitly) — whatever production accepts; cross-reference how `main()` calls it at `game/app.py:510-513`.
- [x] Verify: `pytest tests/unit/test_app_public_api.py -v` passes both `test_game_constructs_with_no_args` and the new positional test.
- [x] Update the docstring rationale to note that BOTH calling conventions are now exercised behaviorally.

**Notes:** Added `test_game_constructs_with_args_positional` mirroring the no-args variant. Initial attempt with a bare `argparse.Namespace()` failed because `_detect_resolution` reads `args.force_resolution`; switched to using production `parse_args()` (the same object `main()` passes), which guarantees the exact attribute surface production expects. Updated `test_game_constructs_with_no_args` docstring to point to the sibling test. Result: 32 passed.

---

### Task 5.2: Tighten fast_panel assertion to match production contract [Simple]
**File:** `tests/unit/ui/screens/test_build_queue_panel_factory.py`
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_panel_factory.py -v`

- [x] Production currently gives every `UIPanel` in `build_queue_panel_factory.py` the `object_id="@fast_panel"` (verified at `game/ui/screens/build_queue_panel_factory.py:213-217,262-267,340-345,382-387,401-408,463-468,551-556`). The migrated test relaxed this to a `>= int(0.8 * total)` floor with a `warnings.warn` fallback, which (a) makes the documented ≥80% claim weaker than advertised due to floor math, and (b) demotes a real perf regression to a non-fatal warning.
- [x] Tighten the assertion in `test_majority_of_factory_uipanels_use_fast_panel_class_id` to assert 100% of UIPanel constructions use `object_id="@fast_panel"` (matching the actual current contract).
- [x] Drop the `warnings.warn` fallback for non-fast-panel calls. If a deliberately-themed panel is added later, the test should be updated explicitly at that time — silent warnings hide the regression.
- [x] Rename the test if appropriate (e.g. `test_all_factory_uipanels_use_fast_panel_class_id`) to reflect the tightened contract.
- [x] Update the test docstring to drop the "great majority" / "≥80%" language and instead document the actual 100% production contract.
- [x] Verify: `pytest tests/unit/ui/screens/test_build_queue_panel_factory.py -v` passes.

**Notes:** Renamed to `test_all_factory_uipanels_use_fast_panel_class_id`. Hard 100% assertion via `assert not non_fast_panel_calls` with a descriptive error listing the offending object_ids. Removed the `warnings.warn` soft-fallback and the `import warnings` block. Docstring rewritten around the actual 100% production contract and the Phase 5 rationale. Result: 5 passed.

---

### Task 5.3: Correct stale docstring on `_disable_pygame_gui_kill_side_effect` [Simple]
**File:** `tests/unit/ui/screens/test_build_queue_list_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_list_window.py -v`

- [x] The module docstring at lines 12-16 and the helper docstring at lines 35-49 claim the helper avoids directly patching `pygame_gui.elements.UIWindow.kill`. Line 50 does exactly that: `patch.object(pygame_gui.elements.UIWindow, "kill", MagicMock())`. Update the docstrings to describe what the helper actually does — it is a SCOPED context-manager wrapper around the patch, so it limits the patch lifetime to a single call site rather than leaving it open across an arbitrary test body. (The patch is process-wide while it's active either way; what changes is how easily an in-line patch leaks across multiple operations in a test body.)
- [x] Verify: `pytest tests/unit/ui/screens/test_build_queue_list_window.py -v` passes.

**Notes:** Rewrote both the module-level docstring and the `_disable_pygame_gui_kill_side_effect` helper docstring to describe what the helper actually provides — *scope* around the `patch.object(pygame_gui.elements.UIWindow, "kill", ...)` call, not a different patch target. Explicitly notes the patch is process-wide while active and that the bounded `with` lifetime is what prevents accidental side-effect chaining. Result: 18 passed.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
