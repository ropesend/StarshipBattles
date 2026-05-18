# PROJ-446 Phase 5: Deferred UIWindow retrofit closure (SPIN-OUT CANDIDATE)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-446 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started — **STRONG RECOMMENDATION TO SPIN OUT before starting**
**Depends on:** Phases 1-4 complete
**Objective:** Apply the dedicated behavior-locking characterization-test pass + two-stage retrofit recipe to 5 UIWindow subclasses that PROJ-329A deferred. Codex 2026-05-18 verified incidental coverage exists (modal-window and registrar contract suites), but no DEDICATED retrofit tests exist for any of the 5 windows.

**RECOMMENDATION: SPIN OUT before starting.** This phase is genuinely 5 mini-projects in a trench coat. Each window needs its own characterization-test pass + retrofit, mirroring how PROJ-329A handled its retrofit pass. Recommended new project IDs: **PROJ-448 / PROJ-448A-E** (or whatever the next available IDs are at the time — PROJ-447 was consumed by the Bucket D supplemental). The work below is the spin-out plan.

**Cross-bucket file-ownership rule:** Only edit `game/ui/screens/` and tests under `tests/unit/ui/screens/`.

**Source-of-truth findings:** [`findings/bucket_c_ui_core_tests_scan.md`](findings/bucket_c_ui_core_tests_scan.md) — F-C-017.

**Existing incidental coverage (verified by Codex 2026-05-18):**
- 4 PlanetTargetEditor subclasses: `tests/unit/ui/screens/test_strategy_modal_window.py:367-398` (explicit-window-manager contract suite)
- SettingsWindow: `tests/unit/ui/screens/strategy_windows/test_empire_panel_ctrl.py:100-127` (via SettingsRegistrar)

---

## Tasks (if executed inline rather than spun out)

### Task 5.1: SettingsWindow retrofit (smallest, best starter) [Medium]
**File:** `game/ui/screens/settings_window.py` (109 LOC)
**Tests (new):** `tests/unit/ui/screens/test_settings_window.py`

- [ ] Read the 6 retrofitted windows that PROJ-329A and follow-ups completed (`RaceSetupScreen`, `NewGameSetupScreen`, etc.) — these are the templates
- [ ] Read `docs/02_PATTERNS.md` Pattern #33 (two-stage UIWindow bypass-init)
- [ ] Write characterization tests against the bypass-init shell for `SettingsWindow`: instantiate via the factory, drive each user-facing interaction (slider change, ok/cancel), assert on state changes
- [ ] Once characterization tests pass: apply the two-stage retrofit recipe
- [ ] Run targeted + full sharded suite

### Task 5.2-5.5: Apply same recipe to 4 PlanetTargetEditor subclasses [Medium each]
**Files:**
- `game/ui/screens/atmosphere_target_editor.py` (273 LOC) — Task 5.2
- `game/ui/screens/gravity_target_editor.py` (220 LOC) — Task 5.3
- `game/ui/screens/water_target_editor.py` (227 LOC) — Task 5.4
- `game/ui/screens/radiation_shield_editor.py` (231 LOC) — Task 5.5

For each:
- [ ] Read the editor; identify state transitions, validation rules, ok/cancel paths
- [ ] Write characterization tests in `tests/unit/ui/screens/test_<editor_name>.py`
- [ ] Apply the two-stage retrofit
- [ ] Run targeted + sharded suite

---

## Phase Completion Checklist (if executed inline)

- [ ] All 5 windows have dedicated test files with characterization passes
- [ ] All 5 windows retrofitted via Pattern #33
- [ ] Run `python Tools/test_sharded/test_sharded.py` — full sharded suite green
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-446 5` — PASSED
- [ ] Update status to `Complete`; plan.md all phases Complete; Current State → "Project complete — awaiting verification"

## SPIN-OUT plan (if spun out instead)

1. Create PROJ-448 via `python Projects/scripts/create_project.py "UIWindow retrofit completion (PROJ-329A follow-up)"` (or whatever ID is next available)
2. The new project's plan owns the F-C-017 finding; PROJ-446 Phase 5 is marked `Spun Out` rather than `Complete`
3. PROJ-448 has 5 phases (one per window) or 1 phase with 5 tasks — author's choice
4. PROJ-446 closes with Phases 1-4 verified

## Decision

Before starting Phase 5: open [decisions.md](decisions.md), record the inline-vs-spinout decision with rationale. The default recommendation is SPIN OUT.
