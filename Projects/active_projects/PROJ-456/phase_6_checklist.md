# PROJ-456 Phase 6: Codex-audit polish (stale docstring sweep)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-456 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Refresh four module/class docstrings that codex flagged as
stale after PROJ-456 Phase 1, 3, and 5 deleted the property shims they
described. All Phase 6 edits are docstring-only — no behaviour changes.

Codex end-of-project audit (response.md at
`Projects/active_projects/PROJ-456/consults/20260519T064622Z_end-of-project-audit/`)
verified 13 of 14 findings closed and called out F-C-012 as
partially-closed per the documented Option B half-measure. Four
docstrings still claimed the deleted shims were preserved:

1. `game/ui/screens/new_game_setup_screen.py:34-37`
2. `game/ui/screens/battle_setup/screen.py:8-9`
3. `game/ui/screens/battle_setup_state.py:151-155`
4. `game/ui/screens/strategy_render/grid.py:4-6`

Per protocol PART 3 Step D ("trivial polish, skip the re-audit"), no
re-audit is dispatched.

---

## Tasks

### Task 6.1: Refresh new_game_setup_screen.py module docstring [Trivial]
**File:** `game/ui/screens/new_game_setup_screen.py:34-37`

- [x] Rewrote to describe `_view_model` as the canonical state owner
      and reference PROJ-456 Phase 5 as the retirement source.

### Task 6.2: Refresh battle_setup/screen.py module docstring [Trivial]
**File:** `game/ui/screens/battle_setup/screen.py:8-9`

- [x] Rewrote to describe panel builders reading through
      `screen.view_model.<X>` / `screen.state.<X>` /
      `screen.controller.<X>` and reference PROJ-456 Phase 5.

### Task 6.3: Refresh BattleSetupState class docstring [Trivial]
**File:** `game/ui/screens/battle_setup_state.py:151-155`

- [x] Rewrote to describe `state.sides[i]` / `state.get_side(team_id)`
      as canonical access patterns and reference PROJ-456 Phase 3.

### Task 6.4: Refresh strategy_render/grid.py module docstring [Trivial]
**File:** `game/ui/screens/strategy_render/grid.py:4-6`

- [x] Rewrote to describe `GridLayer.draw` as the only render path
      and reference PROJ-456 Phase 1.

---

## Phase Completion Checklist

- [x] All Task 6.x complete
- [x] `python Tools/test_sharded/test_sharded.py` — sharded suite green
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to "Project complete; ready for end-of-project merge to main"
