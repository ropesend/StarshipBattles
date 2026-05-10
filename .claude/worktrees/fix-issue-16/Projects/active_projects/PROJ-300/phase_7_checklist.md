# Phase 7: Eradicate `AreaEffectManager` + `EnvironmentalEffects` + `StormEffect`

**Status:** Complete (2026-04-27)
**Objective:** Delete the parallel system. Per CLAUDE.md Rule 3 + System Migration Policy, no fallback paths, no compatibility shims. Grep guard at the end confirms zero references remain.

---

## Tasks

### Task 7.1: Delete `area_effect_manager.py` and its test [Simple]
**File:** Delete `game/strategy/services/area_effect_manager.py`; delete `tests/unit/strategy/services/test_area_effect_manager.py`.

- [ ] Confirm no production code imports from `game.strategy.services.area_effect_manager`:
  ```bash
  grep -r "area_effect_manager" game/
  grep -r "AreaEffectManager" game/
  grep -r "EnvironmentalEffects" game/
  ```
- [ ] If grep finds any hits in `game/`, return to Phase 6 — those callers were missed.
- [ ] Delete both files.
- [ ] Run full suite: `pytest tests/ --testmon`. Expected result: clean (or only DI-wiring failures fixed in 7.2).

**Notes:**

### Task 7.2: Remove `area_effect_manager` from DI wiring [Simple]
**File:** `game/context.py`, possibly `game/strategy/facade/strategy_session_facade.py`

- [ ] Search for `AreaEffectManager` and `area_effect_manager` constructor wiring:
  ```bash
  grep -rn "AreaEffectManager\|area_effect_manager" game/
  ```
- [ ] In `game/context.py`: remove any `area_effect_manager` attribute, factory method, or argument. The DI container should no longer know about it.
- [ ] In any strategy facade or other service factory: remove the parameter.
- [ ] Update tests in `tests/unit/test_context.py` (or similar) that asserted on `AreaEffectManager` presence — delete those assertions.

**Notes:**

### Task 7.3: Confirm `_entries_from_environmental_effects` is gone [Simple]
**File:** `game/strategy/combat/spec_compiler.py`

- [ ] Phase 6 should have replaced this function with `_entries_from_sector_effects`. Verify the old function and its `environmental_effects: Any` parameter no longer exist anywhere.
- [ ] `grep -rn "_entries_from_environmental_effects\|environmental_effects" game/`. Allowed remaining hits: comments referencing legacy migration history (none expected after PROJ-300).

**Notes:**

### Task 7.4: Confirm `StormEffect` is gone [Simple]
**File:** N/A (verification step)

- [ ] `grep -rn "StormEffect" game/ tests/`. Expected: zero hits.
- [ ] If any test file still imports `StormEffect`, rewrite or delete.

**Notes:**

### Task 7.5: Update `IStorm` protocol (if not done in Phase 5) [Simple]
**File:** `game/core/protocols.py`

- [ ] Confirm `IStorm` exposes `abilities: Dict[str, Any]`, NOT `effects: StormEffect`.
- [ ] Confirm `is_storm` TypeGuard checks for `'storm_type'` and `'abilities'`.

**Notes:**

### Task 7.6: Final grep guard [Simple]
**File:** N/A (verification)

- [ ] Run:
  ```bash
  grep -rn "EnvironmentalEffects\|AreaEffectManager\|StormEffect\|_entries_from_environmental_effects\|area_effect_manager" game/ tests/
  ```
- [ ] Expected output: **zero hits** (or only the inside of [docs/refactoring/](docs/refactoring/) historical archives — those are reference, not production).
- [ ] If any production hit remains, return to the appropriate phase.

**Notes:**

---

## Phase Completion Checklist
- [ ] All tasks complete
- [ ] Grep guard returns zero hits in `game/` and `tests/`
- [ ] `pytest tests/ --testmon` clean
- [ ] `python Tools/test_sharded/test_sharded.py` clean (full suite)
- [ ] Update status to `Complete`
- [ ] Update plan.md
