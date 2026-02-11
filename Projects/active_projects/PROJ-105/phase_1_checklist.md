# Phase 1: Core Infrastructure

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-105 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Create the directory structure, conftest, and image comparison engine

---

## Tasks

### Task 1.1: Create Directory Structure [Simple]
**Files:** New directories and init files
**Tests:** N/A

- [ ] Create `tests/visual_regression/` directory
- [ ] Create `tests/visual_regression/__init__.py` (empty)
- [ ] Create `tests/visual_regression/baselines/` directory (add `.gitkeep`)
- [ ] Create `tests/visual_regression/diffs/` directory (add `.gitkeep`)
- [ ] Add `tests/visual_regression/diffs/` to `.gitignore`
- [ ] Add `Pillow>=9.0` to `requirements.txt` (line 7, after `pytest-testmon`)

**Notes:**

---

### Task 1.2: Create Local conftest.py [Medium]
**File:** `tests/visual_regression/conftest.py` (NEW)
**Tests:** `pytest tests/visual_regression/ --collect-only` should work without errors

- [ ] Add `pytest_addoption` hook for `--update-baselines` flag (action="store_true", default=False)
- [ ] Add `update_baselines` fixture that reads the flag via `request.config.getoption("--update-baselines")`
- [ ] Add xdist safety guard: if `os.environ.get("PYTEST_XDIST_WORKER")` is set AND `update_baselines` is True, `pytest.skip("Use -n 1 when updating baselines")`
- [ ] Add `render_surface` fixture: factory function `_factory(width, height) -> pygame.Surface` that creates `pygame.Surface((width, height), pygame.SRCALPHA)`
- [ ] Verify: root conftest's `reset_game_state` and `enforce_headless` fixtures are inherited (no need to re-initialize Pygame)

**Notes:** The root conftest handles all Pygame/registry initialization. We only need visual-regression-specific fixtures here.

---

### Task 1.3: Create Image Comparison Engine [Medium]
**File:** `tests/visual_regression/image_compare.py` (NEW)
**Tests:** `pytest tests/visual_regression/test_image_compare.py` (created in Task 1.4)

- [ ] Create `ComparisonResult` dataclass with fields: `match` (bool), `total_pixels` (int), `changed_pixels` (int), `change_percentage` (float), `max_channel_diff` (int), `diff_image_path` (Optional[str])
- [ ] Create `compare_images(baseline_path, actual_path, diff_output_path=None, pixel_threshold=2, change_threshold=0.1) -> ComparisonResult`
  - [ ] Load both images with `PIL.Image.open().convert("RGBA")`
  - [ ] Raise `ValueError` if sizes differ
  - [ ] Use `PIL.ImageChops.difference()` to compute per-pixel diff
  - [ ] Iterate pixels: count those where `max(r, g, b, a) > pixel_threshold`
  - [ ] Calculate `change_percentage = changed_pixels / total_pixels * 100`
  - [ ] Set `match = change_percentage <= change_threshold`
- [ ] Create `_generate_diff_image(baseline, actual, diff, output_path, pixel_threshold) -> str`
  - [ ] Create side-by-side composite: `[BASELINE] | [ACTUAL] | [DIFF HIGHLIGHT]`
  - [ ] Width = 3 * original width, height = original height
  - [ ] Changed pixels shown in red `(255, 0, 0, 255)` on the diff panel
  - [ ] Add text labels "BASELINE", "ACTUAL", "DIFF" using `PIL.ImageDraw`
  - [ ] Save composite to `output_path`
  - [ ] Only generate diff image if `not match` and `diff_output_path` is provided
- [ ] Verify: `os.makedirs(dirname, exist_ok=True)` before saving

**Notes:** Pure-Python per-pixel loop is fine for panel sizes (300-450px wide). No numpy needed.

---

### Task 1.4: Create Image Comparison Tests [Simple]
**File:** `tests/visual_regression/test_image_compare.py` (NEW)
**Tests:** `pytest tests/visual_regression/test_image_compare.py -v`

- [ ] Test: identical images → `match=True`, `changed_pixels=0`
- [ ] Test: one pixel changed above threshold → `match=False`
- [ ] Test: small change below threshold → `match=True`
- [ ] Test: size mismatch raises `ValueError`
- [ ] Test: diff image is generated when `not match` and `diff_output_path` provided
- [ ] Use `PIL.Image.new("RGBA", (10, 10), ...)` for test images (small, fast)
- [ ] Clean up temp files in fixture teardown

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/visual_regression/test_image_compare.py -v` passes
- [ ] `pytest tests/visual_regression/ --collect-only` shows no import errors
- [ ] `pytest tests/ -n 12` still passes (no regressions)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
