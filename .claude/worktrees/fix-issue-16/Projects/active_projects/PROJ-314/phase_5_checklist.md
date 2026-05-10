# Phase 5: Atomic schema migration

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-314 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Migrate all ship-theme manifests to the canonical `assets:` schema in one atomic step.

---

## Tasks

### Task 5.1: Migrate all theme manifests [Medium]
**Files:** `assets/ShipThemes/*/theme.json`
**Tests:** `python -m Tools.regenerate_ship_portraits.audit`

- [x] Add `schema_version: 1`.
- [x] Add `image_sizes.skin` and `image_sizes.portrait`.
- [x] Replace legacy `images:` maps with `assets:` entries.
- [x] Preserve per-class `scale` values.
- [x] Declare available portrait paths.

**Notes:** Shipped via commit 0bbf9c36d (PROJ-314 Phase 5).

### Task 5.2: Update hardcoded-convention call sites [Medium]
**Files:** `game/ui/`
**Tests:** `pytest tests/integration/ui/test_race_setup_ships_smoke.py`

- [x] Route ship-theme portrait lookup through `ShipThemeManager`.
- [x] Remove loader dependence on `<Class>_Portrait.jpg`.
- [x] Add Race Setup smoke coverage for skin and portrait lookup.
- [x] Keep known deferred portrait gaps explicit.

**Notes:** Shipped via commit 0bbf9c36d (PROJ-314 Phase 5).

### Task 5.3: Validate migrated themes [Simple]
**Files:** `assets/ShipThemes/`
**Tests:** `python -m Tools.regenerate_ship_portraits.audit`

- [x] Confirm 9 themes load with the new schema.
- [x] Confirm canonical 19 ship-class keys are present per theme.
- [x] Confirm Race Setup smoke test exercises all themes.

**Notes:** Shipped via commit 0bbf9c36d (PROJ-314 Phase 5).

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] All 9 theme manifests migrated
- [x] Race Setup smoke test added
- [x] Commit: `feat(PROJ-314 Phase 5): atomic schema migration of all 9 themes`
