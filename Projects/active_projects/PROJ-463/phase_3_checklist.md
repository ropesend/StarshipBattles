# Phase 3: Strict-mode migration (ai/simulation/strategy)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-463 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Migrate the domain layers to `mypy --strict` (lowest density first). Depends on PROJ-462 (foundation) Vector2 + core-protocol fixes having landed. Per-layer counts below are audit estimates; confirm the real per-layer count at the start of each task.

---

## Tasks

### Task 3.1: Adopt strict for the ai layer [Medium]
**File:** `game/ai/` (mypy config)
**Tests:** `mypy --strict game/ai/` then `pytest tests/ --testmon`

- [ ] Confirm current strict error count for ai (audit estimate: ~40, of which ~28 `no-any-return` largely cleared by Phase 2.4 controllable adapter; ~6 `assignment`; ~4 `has-type` cleared by PROJ-462 Vector2)
- [ ] Resolve residual errors
- [ ] Add `--strict` to the ai layer's mypy config
- [ ] Verify: pytest passes; `mypy --strict game/ai/` shows no errors

### Task 3.2: Adopt strict for the simulation layer [High]
**File:** `game/simulation/` (mypy config)
**Tests:** `mypy --strict game/simulation/` then `pytest tests/ --testmon`

- [ ] Confirm current count (audit estimate: ~417 — 130 `attr-defined` from Ship mixins, 65 `has-type` cleared by PROJ-462 Vector2, 63 `union-attr`, 62 `no-any-return`)
- [ ] Resolve the `Ship` mixin `attr-defined` cluster (declare attributes/protocol on `Ship`)
- [ ] Resolve `union-attr` (add None guards) and `no-any-return` (Phase 2 narrowing covers many)
- [ ] Add `--strict` to the simulation layer's mypy config
- [ ] Verify: pytest passes; `mypy --strict game/simulation/` shows no errors

### Task 3.3: Adopt strict for the strategy layer [High]
**File:** `game/strategy/` (mypy config)
**Tests:** `mypy --strict game/strategy/` then `pytest tests/ --testmon`

- [ ] Confirm current count (audit estimate: ~452 — 131 `no-any-return`, 77 `arg-type`, 65 `union-attr`, 50 `attr-defined`; GameSession ignores + engine lazy-defaults from Phase 1.2/2.5/2.6 account for ~30%)
- [ ] Resolve residual `no-any-return` / `arg-type` / `union-attr` clusters
- [ ] Add `--strict` to the strategy layer's mypy config
- [ ] Verify: pytest passes; `mypy --strict game/strategy/` shows no errors

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase

_Source audit: `Reviews/results/2026-05-19_223900_type-audit/`. See `findings/source_audit.md` for the link._
