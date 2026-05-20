# Phase 1: Critical (foundation root causes)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-462 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Fix the CRITICAL foundation root causes verified by audit `2026-05-19_223900_type-audit` — the Vector2 implicit-Optional cascade, the core enum-validation Any return, and the engine collision None-guard.

---

## Tasks

### Task 1.1: Fix Vector2 implicit-Optional [Medium]
**File:** `game/core/math.py`
**Tests:** `pytest tests/ --testmon` and `mypy game/core/math.py`

- [ ] Fix `Vector2.__init__` (line 22) `y: float = None` → `y: float | None = None` (or refactor to explicit `x: float`, `y: float` with a proper constructor) so mypy can determine `self.x`/`self.y` as `float`
- [ ] Confirm the ~130 `has-type` cascade clears in core (50), engine (~10), simulation (~65), AI (~6) when re-run later by downstream projects
- [ ] Verify: pytest passes; `mypy game/core/math.py` shows no new errors

### Task 1.2: Narrow validate_enum [Medium]
**File:** `game/core/validation_helpers.py`
**Tests:** `pytest tests/ --testmon` and `mypy game/core/validation_helpers.py`

- [ ] Resolve `validate_enum` (lines 69, 86) `return enum_class[value]` `no-any-return`: either `cast(T, enum_class[value])`, or change param to `type[Enum]`, or add an isinstance guard — keep the `-> T` contract
- [ ] Verify: pytest passes; `mypy game/core/validation_helpers.py` shows no new errors

### Task 1.3: Add beam ability None-guard [Simple]
**File:** `game/engine/collision.py`
**Tests:** `pytest tests/ --testmon` and `mypy game/engine/collision.py`

- [ ] Add a None guard for `beam_ab` (line 116, from `beam_comp.get_ability('BeamWeaponAbility')`) before `beam_ab.calculate_hit_chance` (line 133) and `beam_ab.get_damage` (line 140)
- [ ] Verify: pytest passes; `mypy game/engine/collision.py` shows no new errors

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase

_Source audit: `Reviews/results/2026-05-19_223900_type-audit/`. See `findings/source_audit.md` for the link._
