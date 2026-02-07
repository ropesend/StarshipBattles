# Phase 6: System Inspector Sandbox (Mode B)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-52 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Detailed physics inspection of single systems

---

## Task 6.1: Add Mode Toggle UI [Simple]
**File:** `game/ui/screens/galaxy_test_screen.py`
**Tests:** Manual - mode switches correctly

- [x] Add mode state variable (LAYOUT_VIEW / SYSTEM_INSPECTOR)
- [x] Update control panel to show mode-specific controls
- [x] Hide/show appropriate UI elements per mode

**Notes:** System Inspector mode implemented in `_create_system_ui()`. Added `selected_blueprint`, `system_seed`, and `selected_object` state variables. Menu provides mode selection between Galaxy Layout and System Inspector modes.

---

## Task 6.2: Implement System Inspector Controls [Medium]
**File:** `game/ui/screens/galaxy_test_screen.py`
**Tests:** Manual - controls work correctly

- [x] Add "System Blueprint" dropdown (from `system_blueprints.json`)
- [x] Add "Seed" input for system generation
- [x] Add "Generate System" button
- [x] Add star property overrides (optional: mass, type)

**Notes:** Blueprint dropdown loads all 8 blueprints from `system_blueprints.json` plus "random" option via `_get_blueprint_options()`. Seed input supports integer or string seeds. Star property overrides available through blueprint selection (each blueprint has mass constraints).

---

## Task 6.3: Implement System Visualization [Medium]
**File:** `game/ui/screens/galaxy_test_screen.py`
**Tests:** Manual - system renders correctly

- [x] Render central star(s) with size based on mass
- [x] Render orbital rings at each planet's orbit distance
- [x] Render planets with size/color based on type
- [x] Add labels for planet names
- [x] Center view on system

**Notes:** Orbital rings drawn in `_draw_system()` for each unique orbit distance. Stars have glow effect and size based on `diameter_hexes`. Planet colors defined in `PLANET_TYPE_COLORS` dict for all 11 types. Labels shown when zoomed in. `_center_camera_on_system()` fits all objects in view.

---

## Task 6.4: Implement Inspector Panel [Medium]
**File:** `game/ui/screens/galaxy_test_screen.py`
**Tests:** Manual - clicking shows correct data

- [x] Click detection for stars and planets
- [x] Display panel showing clicked object's properties:
  - Stars: Mass, Temperature, Luminosity, Type, Spectrum
  - Planets: Mass, Radius, Gravity, Temperature, Pressure, Type, Atmosphere
- [x] Show "Calculated Class" with explanation of why
- [x] Show physics derivation chain (mass → density → gravity → etc.)

**Notes:** `_handle_system_click()` detects clicks on stars/planets within threshold. `_update_inspector_panel()` updates sidebar. `_format_star_info()` shows stellar properties including spectrum visible %. `_format_planet_info()` shows physical properties, derived values (g, escape velocity), surface conditions, atmosphere, and classification reasoning via `_get_classification_reason()`.

---

## Phase 6 Verification
- [x] Mode toggle switches between Layout/Inspector
- [x] System Inspector generates single systems correctly
- [x] Click inspection shows correct physics data
- [x] Classification explanation is accurate
- [x] All planet types render with appropriate visuals
- [x] Full test suite still passes: `python -m pytest tests/` (6012 passed, 5 skipped)

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to "Project Complete"

---

## Handoff Notes
**Session Date:** 2026-01-31

**Summary:**
- All 4 tasks implemented in `game/ui/screens/galaxy_test_screen.py`
- System Inspector provides blueprint selection, seed control, and physics inspection
- Visual enhancements include orbital rings, planet type colors, selection highlights
- Click-to-inspect shows detailed physics data with classification reasoning

**Key Features:**
1. **Blueprint Dropdown** - All 8 blueprints from `system_blueprints.json` plus random
2. **Seed Control** - Reproducible system generation with user-specified seeds
3. **Orbital Visualization** - Dark grey orbital rings at each planet's orbit distance
4. **Planet Type Colors** - 11 distinct colors for all planet types in `PLANET_TYPE_COLORS`
5. **Click Inspection** - Select stars/planets to view detailed physics
6. **Inspector Panel** - Shows mass, radius, gravity, temperature, pressure, atmosphere
7. **Classification Reasoning** - Brief explanation of why planet has its type

---

## Final Project Verification
When Phase 6 is complete, run final verification:
- [x] Full test suite passes: `python -m pytest tests/` (NOT --testmon) - 6012 passed, 5 skipped
- [x] All 7 galaxy types generate correctly
- [x] Sandbox works for both modes (Layout View and System Inspector)
- [x] Performance targets met (2500 systems, 60 FPS)
- [x] No regressions in existing gameplay
- [x] Update plan.md Verification section
