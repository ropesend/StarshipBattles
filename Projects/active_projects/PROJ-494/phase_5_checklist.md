# Phase 5: Audit remediation (Codex consult 2026-05-23)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-494 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Address verified in-scope findings from the Codex mid-project review. See `findings/audit_verification.md` for the full verification table and `AgentCoordination/Scratchpad/Consult/20260523T144314Z_audit-PROJ-494/response.md` for the raw audit.

---

## Tasks

### Task 5.1: T3.14 — parametrize battle-over winner cluster
**File:** `tests/unit/ui/test_battle_screen_simulation.py`
**Tests:** `pytest tests/unit/ui/test_battle_screen_simulation.py`

PROJ-480 T3.14 named "3 clusters" — the original implementation parametrized only the speed-key cluster. The 3 single-target winner-determination tests at lines 175-195 share a clean `(kill_team_lambda, expected_winner)` shape and should be parametrized. The `test_is_battle_over_with_partial_deaths` test at line 197 needs extra ship setup and stays distinct. The 5 input-handler-event tests at lines 289-369 also stay distinct (each tests a different event-branch with different mocks).

- [x] Parametrize the 3 winner-determination tests (`test_get_winner_returns_1_when_team0_all_dead`, `test_get_winner_returns_0_when_team1_all_dead`, `test_draw_condition_all_ships_dead`) into one `test_get_winner_for_team_deaths` on `(kill_indices, expected_winner, expect_battle_over)`. Use `pytest.param(..., id=...)` for readable IDs.
- [x] Keep `test_is_battle_over_with_partial_deaths` separate (different setup, different observable).
- [x] Keep all 5 `TestBattleScreenEventHandling` tests separate (heterogeneous event-handler branches).
- [x] Update `Projects/active_projects/PROJ-494/phase_3_checklist.md` Task 3.14 note to read accurately: "Speed cluster parametrized into 4 cases; 3 winner-determination tests added as parametrize (Phase 5); input-handler cluster left distinct (each tests a different event-branch with different mocks/setup)."
- [x] Verify: tests pass; expected ~35-36 tests (down from 37 by ~2 method count, parametrize cases preserve coverage).

### Task 5.2: T3.15 — parametrize directional margin cluster
**File:** `tests/unit/research/test_research_renderer.py`
**Tests:** `pytest tests/unit/research/test_research_renderer.py`

PROJ-480 T3.15 named "10 + 7 visibility/margin tests". The visibility cluster was parametrized in Phase 3. The 4 directional margin tests at lines 149-184 (`test_margin_extends_visibility_{left,right,top,bottom}`) share the same shape: each asserts `_is_visible(pos, margin=0) is False` AND `_is_visible(pos, margin=50) is True`, with one (`left`/`right`) also asserting the far-outside case. These are clean parametrize candidates. The remaining 3 margin tests (`all_corners`, `zero_margin_is_exact_bounds`, `large_margin_includes_far_positions`) are heterogeneous and stay distinct.

- [x] Parametrize the 4 directional margin tests on `(near_outside_pos, far_outside_pos_or_none, margin)` — the test body asserts: without margin near_outside is False, with margin near_outside is True, and (if far_outside_pos provided) with margin far_outside is False.
- [x] Use `pytest.param(..., id='left')` / `'right'` / `'top'` / `'bottom'` for readable IDs. Top and bottom currently lack the far-outside check; either include `None` for that param or extend the parametrize to cover all four symmetrically (the test wording in PROJ-480 doesn't restrict — implementer's call). Chose symmetric: added far-outside cases for top (y=-51) and bottom (y=651) mirroring left/right.
- [x] Keep `test_margin_extends_visibility_all_corners`, `test_zero_margin_is_exact_bounds`, `test_large_margin_includes_far_positions` separate (different shapes).
- [x] Update `Projects/active_projects/PROJ-494/phase_3_checklist.md` Task 3.15 note to read accurately: "Visibility cluster parametrized in Phase 3; 4 directional margin tests parametrized in Phase 5; 3 heterogeneous margin tests (corners/zero/large) kept distinct."
- [x] Verify: tests pass; expected ~28 tests after parametrize (3 fewer method count).

### Task 5.3: T4.6 — tighten workshop bridge-mass assertion to relative ratio
**File:** `tests/unit/ui/screens/test_workshop_event_router_select_component.py`
**Tests:** `pytest tests/unit/ui/screens/test_workshop_event_router_select_component.py`

PROJ-480 T4.6 explicitly asked for `mass > 50` AND `mass / expected_base in [0.9, 1.1]` (`Projects/archived_projects/PROJ-480/phase_4_checklist.md:54`). The current implementation at lines 99-100 uses `mass > 50` AND `mass < 150`, which loses the relative-ratio contract — a 30%+ calculation error against the bridge formula `50 * sqrt(budget/1000)` could still pass.

- [x] Replace `assert mass < 150` with the relative-ratio band. The bridge formula evaluated at budget=2000 is `50 * sqrt(2.0)` ≈ 70.71. Use: `expected_base = 50 * math.sqrt(2.0)` (compute via `import math`, NOT hardcode the literal) and assert `0.9 <= mass / expected_base <= 1.1`.
- [x] Add an `import math` at the top of the file if not already present.
- [x] Keep `assert mass > 50` as a separate sanity check (it guards the "bridge mass exceeds the baseline" property independently of the formula).
- [x] Update the docstring at lines 82-90 to describe the assertion correctly — the comment says "scales with budget" but the new assertion pins to a *specific* budget's expected value within 10%. Keep the "PROJ-494 T4.2" reference but replace the rationale block with: "Asserts (1) bridge mass exceeds the baseline (50.0) — a basic property; (2) bridge mass for the given design budget is within ±10% of the formula's expected output. The ±10% tolerance allows minor formula tweaks (rounding, baseline shift) without rewriting the test, while still catching meaningful calculation regressions. Task wording: PROJ-480 T4.6."
- [x] Verify: tests pass; LOC delta ≈ +2.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to "Phases 0-5 Complete" (no Phase 6 planned)
