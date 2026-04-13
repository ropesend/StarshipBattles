# Phase 12: Dead Scaffolding + Type-Model Cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-270 12`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Risk:** LOW (deletes / refactors with no behavior change)
**Depends On:** Phases 9 + 10 + 11 (contract + tests + docs must be clean first)
**Objective:** Delete the "scaffolding for future work" DTOs that have zero consumers, fix the `UnboundedRegion.closest_edge_point` type-model flaw, wire the half-implemented `ComponentStateSpec.is_active` round-trip (or delete the field), clean up small residual items.

## Context (from skeptic audit)

- **`AIPolicy`** is a zero-field `pass` dataclass. Grep for `ai_policy.` returns **zero attribute access sites**. Pure "scaffolding for future fields" — textbook YAGNI violation per CLAUDE.md Rule 3.
- **`TaskForceOutcome`** carries only `task_force_id`. `TeamOutcome.fleet_hierarchy` is constructed by compilers and never read by any production consumer.
- **`ComponentStateSpec.is_active`** has a read path in `battle_runner.py:498` but the write path in `strategy/combat/spec_compiler.py:282` doesn't populate from the live `comp.is_active`. It round-trips the field's default value, not the ship's actual state.
- **`UnboundedRegion.closest_edge_point` raises `NotImplementedError`** at runtime. Per-call `isinstance(boundary, UnboundedRegion)` check in `RetreatManager.request_retreat` is a type-dispatch bandaid that Rule 3 forbids. Proper fix: split protocol into `Region` + `BoundedRegion(Region)`.
- **Stale docstring** at `game/ui/screens/test_lab/test_executor.py:113-115` — claims `_switch_to_battle handles engine.start + scenario.setup`. Wrong on both counts.
- **`FORBIDDEN_FIELDS` regression guards have no sunset dates.** Will accumulate indefinitely as a ledger of past sins.

---

## Tasks

### Task 12.1: Delete `AIPolicy` [Simple]
**File:** `game/simulation/battle_spec.py:67-79`, plus `TeamSpec.ai_policy` field + all compiler call sites

- [ ] Grep for `AIPolicy` + `ai_policy` — confirm zero attribute reads (only constructions)
- [ ] Delete `AIPolicy` class
- [ ] Delete `TeamSpec.ai_policy` field
- [ ] Remove `ai_policy=AIPolicy()` from all 3 spec compilers (`build_test_battle_spec`, `build_manual_battle_spec`, `build_strategy_battle_spec`)
- [ ] Run `pytest tests/` — passes

**Notes:** Reintroduce when a concrete consumer exists. Follow YAGNI.

---

### Task 12.2: Delete `TaskForceOutcome` [Simple]
**File:** `game/simulation/battle_outcome.py:155-160`, `TeamOutcome.fleet_hierarchy`

- [ ] Grep for `TaskForceOutcome` + `fleet_hierarchy` — confirm zero production reads
- [ ] Delete `TaskForceOutcome` class
- [ ] Delete `TeamOutcome.fleet_hierarchy` field
- [ ] Update `extract_outcome()` in `battle_runner.py` to stop populating the field
- [ ] Run `pytest tests/` — passes

---

### Task 12.3: Resolve `ComponentStateSpec.is_active` half-wiring [Medium]
**File:** `game/simulation/battle_spec.py:114`, `game/strategy/combat/spec_compiler.py:282`, `game/simulation/battle_runner.py:498`

Pick one:
- [ ] Option A: **Finish the round-trip** — have all 3 spec compilers populate `is_active` from the live `comp.is_active` attribute, and wire the engine's disable/enable flow from the spec at `materialize_spec_ships` time
- [ ] Option B: **Delete the field** — have the engine compute `is_active` from damage state at tick time (existing behavior). Field was never carrying information.

Document choice in decisions.md.

---

### Task 12.4: Split `BoundaryRegion` protocol [Medium]
**File:** `game/simulation/combat/boundary.py`, `game/simulation/managers/retreat_manager.py`

- [ ] Introduce `Region` protocol with: `exit_policy`, `contains(pos)`, `closest_inside_point(pos)`
- [ ] Introduce `BoundedRegion(Region)` protocol adding: `closest_edge_point(pos)`, `distance_to_edge(pos)`
- [ ] `RectBoundary` + `CircleBoundary` implement `BoundedRegion`
- [ ] `UnboundedRegion` implements only `Region` (no `closest_edge_point` method at all)
- [ ] `RetreatManager.__init__(boundary: Optional[BoundedRegion])` — None-or-BoundedRegion, not a Region that might-or-might-not raise
- [ ] Delete the `isinstance(self.boundary, UnboundedRegion)` branch in `request_retreat`
- [ ] Delete the `raise NotImplementedError` from `UnboundedRegion.closest_edge_point` (method simply doesn't exist)

---

### Task 12.5: Fix stale `test_executor.py` docstring [Simple]
**File:** `game/ui/screens/test_lab/test_executor.py:113-115`

- [ ] Update comment from `# (_switch_to_battle handles engine.start + scenario.setup)` to `# (_switch_to_battle compiles spec, calls controller.start_from_spec, wires scenario)`

---

### Task 12.6: Add sunset dates to `FORBIDDEN_FIELDS` regression guards [Simple]
**File:** `tests/unit/simulation/test_battle_config.py:70-79`; similar tests in `test_unified_entry_guard.py`

- [ ] Add a `SUNSET_DATES` dict alongside `FORBIDDEN_FIELDS` mapping each forbidden field to a removal date (e.g., `"test_scenario": "2026-10-01"`)
- [ ] Add a test or fixture that fails-loudly when today's date passes a sunset date, forcing re-evaluation of whether the guard is still needed
- [ ] Alternative: remove fields from `FORBIDDEN_FIELDS` entirely if they've been gone for 6+ months; the regression guard's utility has expired

---

### Task 12.7: Phase 12 regression gate
**Tests:** Full suites + grep audits

- [ ] `pytest tests/` — green
- [ ] Combat Lab fast + full green
- [ ] Grep audits: no `AIPolicy`, no `TaskForceOutcome`, no `fleet_hierarchy` in production code
- [ ] Grep audit: no `isinstance(boundary, UnboundedRegion)` anywhere (type-model split eliminated the need)

---

## Phase Completion Checklist

- [ ] All task checkboxes above are checked
- [ ] Dead DTOs deleted (AIPolicy, TaskForceOutcome)
- [ ] `BoundaryRegion` protocol split into `Region` + `BoundedRegion` — no more `raise NotImplementedError` at runtime
- [ ] `ComponentStateSpec.is_active` either fully wired or deleted
- [ ] `FORBIDDEN_FIELDS` guards tagged with sunset dates
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] PROJ-270 genuinely ready for archival — all 12 phases Complete + manual smoke green
