# Phase 6: Cleanup + documentation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-314 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Remove obsolete image assets and document the new ship-theme schema.

---

## Tasks

### Task 6.1: Delete obsolete legacy portrait files [Simple]
**Files:** `assets/ShipThemes/`
**Tests:** `python -m Tools.regenerate_ship_portraits.audit`

- [x] Remove migrated legacy portrait JPGs from active theme asset paths.
- [x] Keep source/original art only where intentionally outside the loader contract.
- [x] Confirm manifests point to PNG assets.

**Notes:** Shipped via commit e26f00f74 (PROJ-314 Phase 6).

### Task 6.2: Update architecture and convention docs [Simple]
**Files:** `docs/01_ARCHITECTURE.md`, `docs/03_CONVENTIONS.md`
**Tests:** Documentation review.

- [x] Document `game/ui/services/image/`.
- [x] Add ship-theme asset conventions section.
- [x] Document canonical `theme.json` schema.
- [x] Document PNG, 2048x2048, and lowercase filename rules.

**Notes:** Shipped via commit e26f00f74 (PROJ-314 Phase 6). `docs/02_PATTERNS.md`, `docs/README.md`, and `AGENTS.md` were not updated; PROJ-318 Phase 2 addresses that follow-up.

### Task 6.3: Close out PROJ-314 plan state [Simple]
**File:** `Projects/active_projects/PROJ-314/plan.md`
**Tests:** Documentation review.

- [x] Mark PROJ-314 phases complete.
- [x] Record deferred user-run generation for remaining portrait gaps.
- [x] Record final sharded-suite baseline.

**Notes:** Shipped via commit e26f00f74 (PROJ-314 Phase 6).

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Legacy loader assets cleaned up
- [x] Architecture and convention docs updated
- [x] Commit: `feat(PROJ-314 Phase 6): docs + plan close-out`
