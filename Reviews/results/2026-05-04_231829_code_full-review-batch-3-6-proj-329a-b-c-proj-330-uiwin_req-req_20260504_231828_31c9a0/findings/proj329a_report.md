# PROJ-329A Phase 2 — Code Review Report

**Date:** 2026-05-04
**Reviewer:** OpenCode (batch 3b — PROJ-329A Phase 2 review)
**Status:** PASS — no CRITICAL or MAJOR findings

## CRITICAL

*None.*

## MAJOR

*None.*

## PASS

- **Behavioral parity (FleetSelectionWindow):** Compared `5a3acb260` (post-refactor) against `41f799174` (pre-refactor). The refactor moves cheap state (`_display_labels`, `_label_to_fleet`, callback) before `super().__init__()` and extracts widget construction into `FleetSelectionUiBuilder.build()`. The widget code is byte-for-byte identical. `update()` and `kill()` are unchanged. No observable behavior difference.
- **Behavioral parity (FoodAllocationEditor):** Compared `cd7f84b59` (post-refactor) against `dd06b8d7b` (pre-refactor). `_build_ui` / `_build_row` migrated to `FoodAllocationEditorUiBuilder` with mechanical `self` → `screen` substitution — logic unchanged. `update()`, `process_event()`, `_on_apply()`, `_on_cancel()`, `collect_allocations()` untouched.
- **Behavioral parity (PlanetSelectionWindow):** Compared `2bbb260f6` (post-refactor) against `41f799174` (pre-refactor). Widget construction extracted to `PlanetSelectionUiBuilder` with identical layout constants. `update()` and `kill()` unchanged except `list_width` local → `LIST_WIDTH` module constant (same value 300). `_list_label` / `_show_any_button` stored as internal attrs, consumed identically by builder.
- **Pattern §33 conformance — Stage 1 (cheap state before guard):** All 3 classes set only pure-Python state (strings, lists, dicts, data classes, scalars) before `super().__init__()`. No `pygame_gui` widget creation above the `_window_init_bypassed` check.
- **Pattern §33 conformance — `ui_builder` parameter:** All 3 classes accept `ui_builder: Optional[BuilderType] = None`. Production default is the corresponding `*UiBuilder()` class invoked via `(ui_builder or DefaultBuilder()).build(self)`.
- **Pattern §33 conformance — Null/Mock fixture pair:** All 3 fixture modules provide `Null*UiBuilder` (no-op) + `Mock*UiBuilder` (MagicMock-populated slots). All `build()` signatures match `tests/fixtures/ui_builder_protocol.py:UiBuilder`. Mock builders validate Stage 1 attributes exist before populating.
- **Pattern §33 conformance — bypass_init guard:** `getattr(type(self), 'bypass_init', False)` correctly lives in `StrategyModalWindow.__init__` (base class), honoring subclass-level flag settings. The subclasses check `getattr(self, '_window_init_bypassed', False)` after `super().__init__()` to skip widget construction — the correct two-stage adaptation for StrategyModalWindow subclasses.
- **Pattern §33 conformance — guard placement:** `UIWindow.__init__` is avoided inside `StrategyModalWindow.__init__` via `getattr(type(self), 'bypass_init', False)`, which is the first point the chain can be short-circuited. Subclasses always call `super().__init__()` unconditionally; the bypass happens inside the base class.
- **Concurrent-commit contamination:** Verified `git diff cd7f84b59..HEAD -- game/ui/screens/food_allocation_editor.py` is empty (394 LOC matches). Verified `git diff 2bbb260f6..HEAD -- game/ui/screens/planet_selection_window.py` is empty (232 LOC matches). File content in both commits is identical to HEAD. The audit document's conclusion holds: the only issue is commit attribution/bundling, not content correctness.
- **LOC ceilings:** FleetSelectionWindow 152 LOC, FoodAllocationEditor 394 LOC, PlanetSelectionWindow 232 LOC. All three fixture files < 80 LOC. Well under the 500 LOC ceiling.
- **Import hygiene:** `Optional` import added to FleetSelectionWindow and PlanetSelectionWindow (needed for `ui_builder` parameter). `import pygame_gui` removed from PlanetSelectionWindow (was unused — `pygame_gui` constants not referenced directly in that module). No orphaned imports.
- **`_build_ui` removal:** The `_build_ui` method on `FoodAllocationEditor` was mechanically moved to `FoodAllocationEditorUiBuilder.build()`. No external production callers — `_build_ui` references in test files are archival comments documenting the migration, not active code.
