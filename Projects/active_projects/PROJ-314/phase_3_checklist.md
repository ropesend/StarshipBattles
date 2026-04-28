# Phase 3: Loader rewrite

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-314 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Rewrite `ShipThemeManager` around the canonical `assets:` schema.

---

## Tasks

### Task 3.1: Rewrite theme discovery for `assets:` schema [Medium]
**File:** `game/ui/assets/ship_theme_manager.py`
**Tests:** `pytest tests/unit/ui/test_theme_discovery.py`

- [x] Require `assets` manifest block.
- [x] Read display-form ship-class keys.
- [x] Load per-class `skin`, optional `portrait`, and `scale`.
- [x] Validate declared image sizes against actual files.
- [x] Remove `_ship_class_to_portrait_name()` convention logic.

**Notes:** Shipped via commit 48de788da (PROJ-314 Phase 3).

### Task 3.2: Update loader tests for new schema [Medium]
**Files:** `tests/unit/ui/test_ship_theme_logic.py`, `tests/unit/ui/test_theme_discovery.py`
**Tests:** `pytest tests/unit/ui/test_ship_theme_logic.py tests/unit/ui/test_theme_discovery.py`

- [x] Update fixtures to write `assets:` manifests.
- [x] Delete legacy portrait-name helper tests.
- [x] Add missing/extra key coverage.
- [x] Add declared-size validation coverage.

**Notes:** Shipped via commit 48de788da (PROJ-314 Phase 3).

### Task 3.3: Pin portrait-image return contract [Simple]
**File:** `tests/unit/ui/test_ship_theme_logic.py`
**Tests:** `pytest tests/unit/ui/test_ship_theme_logic.py`

- [x] `get_portrait_image()` returns a `pygame.Surface`.
- [x] Missing portraits return the synthetic fallback.
- [x] Loaded portraits are cached.

**Notes:** Shipped via commit 48de788da (PROJ-314 Phase 3).

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Loader reads canonical schema
- [x] Legacy portrait-name helper removed from loader
- [x] Contract tests updated
- [x] Commit: `feat(PROJ-314 Phase 3): rewrite ShipThemeManager for new assets: schema`
