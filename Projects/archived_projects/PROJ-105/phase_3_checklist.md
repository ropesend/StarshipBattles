# Phase 3: Image Comparison & Test Runner

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-105 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Create the parametrized pytest test runner that ties panels, rendering, and image comparison together

---

## Tasks

### Task 3.1: Create Test Runner [Medium]
**File:** `tests/visual_regression/test_visual_regression.py` (NEW)
**Tests:** `pytest tests/visual_regression/test_visual_regression.py --collect-only`

- [ ] Import `get_all_panels`, `PANEL_REGISTRY` from `panel_registry`
- [ ] Import `compare_images` from `image_compare`
- [ ] Define path constants:
  - `BASELINES_DIR = Path(__file__).parent / "baselines"`
  - `DIFFS_DIR = Path(__file__).parent / "diffs"`
  - `CAPTURES_DIR = Path(__file__).parent / "diffs" / "_captures"`

- [ ] Create helper `_save_surface_as_png(surface, path)`:
  - `os.makedirs(os.path.dirname(path), exist_ok=True)`
  - `pygame.image.save(surface, path)`

- [ ] Create `_get_panel_ids()` function for parametrize:
  - Import `panel_registry` module (triggers registration)
  - Return `[name for name, _ in get_all_panels()]`

- [ ] Create parametrized test `test_panel_visual_regression(panel_name, render_surface, update_baselines)`:
  - Decorated with `@pytest.mark.parametrize("panel_name", _get_panel_ids())`
  - Get `spec = PANEL_REGISTRY[panel_name]`
  - Create surface via `render_surface(spec.width, spec.height)`
  - Fill surface with solid black `(0, 0, 0, 255)` for consistent background
  - Call `spec.render_fn(surface)`
  - Compute paths: `baseline_path`, `capture_path`, `diff_path` (all under panel_name subdirectory)

  - **Update-baselines mode** (`if update_baselines`):
    - Save surface to baseline_path
    - `pytest.skip(f"Baseline updated: {baseline_path}")`

  - **Compare mode** (default):
    - Save surface to capture_path
    - If baseline doesn't exist: `pytest.skip("No baseline. Run with --update-baselines")`
    - Call `compare_images(baseline_path, capture_path, diff_path, pixel_threshold=2, change_threshold=0.1)`
    - If `not result.match`: `pytest.fail()` with stats (changed_pixels, change_percentage, max_channel_diff, diff_image_path)

**Notes:**

---

### Task 3.2: Verify Test Collection [Simple]
**Tests:** Various pytest commands

- [ ] `pytest tests/visual_regression/ --collect-only` — should list 5 test items (one per panel)
- [ ] `pytest tests/visual_regression/ --collect-only -v` — shows parametrized names
- [ ] `pytest tests/ --collect-only -q 2>&1 | tail -5` — visual regression tests appear in full collection
- [ ] No import errors or collection warnings

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/visual_regression/ --collect-only` shows 5 test items
- [ ] `pytest tests/ -n 12` still passes (no regressions — visual tests skip due to missing baselines)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
