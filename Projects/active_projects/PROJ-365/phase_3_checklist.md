# Phase 3: Replace `_process_tick` body with descriptor iteration

**Status:** Not Started
**Objective:** Replace the imperative phase sequence in `_process_tick` with a single iteration loop over `DEFAULT_TICK_PHASE_LIST`. Cross-phase state flows via TickContext. All Phase 1 characterization tests stay green.

---

## Tasks

### Task 3.1: Add `tick_phases` constructor kwarg [Simple]
**File:** `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/unit/strategy/turn_engine/ -v`

- [ ] Add to `TurnEngine.__init__` signature: `tick_phases: tuple[TickPhase, ...] | None = None`.
- [ ] Inside `__init__`: `self._tick_phases = tick_phases if tick_phases is not None else DEFAULT_TICK_PHASE_LIST`.
- [ ] No production behavior change yet.
- [ ] Run all tests; green.

**Notes:** _(filled during implementation)_

### Task 3.2: Replace `_process_tick` body [Complex]
**File:** Same

- [ ] Replace lines 703-782 with:
  ```python
  def _process_tick(self, tick: int, empires, galaxy, save_path=None) -> None:
      ctx = TickContext(
          tick=tick, empires=empires, galaxy=galaxy,
          component_registry=self._registries.components,
          save_path=save_path,
          progress_callback=self._progress_callback,
      )
      # Progress callback — preserve existing semantics (lines 696-701)
      if self._progress_callback is not None:
          try:
              self._progress_callback(tick, TICKS_PER_TURN)
          except Exception:  # Intentional broad catch: UI callback must not break tick processing (PROJ-308)
              logger.warning("progress_callback raised; suppressing", exc_info=True)
      
      for phase in self._tick_phases:
          # tick_gating
          if phase.tick_gating == 'only_tick_1' and tick != 1:
              # Hooks gated to tick 1 still want to run (e.g. log) — apply gate to the call too
              continue
          target = phase.callable_target(self)
          args, kwargs = phase.args_resolver(ctx)  # if args_resolver returns (args, kwargs) tuple
          bucket = phase.timing_bucket or phase.phase_key
          result = self._time_phase(bucket, target, *args, **kwargs)
          if phase.post_exec_hook is not None:
              phase.post_exec_hook(self, ctx, result)
      
      # Carry context fields back onto self where they're public state (e.g. last_environmental_events)
      self.last_environmental_events.extend(ctx.last_environmental_events)
  ```
- [ ] Run Phase 1 golden-list test: green.
- [ ] Run PROJ-320 movement-diff test: green.
- [ ] Run all turn_engine tests: green.
- [ ] Run integration tests: `pytest tests/integration/strategy/ --testmon`. Green.

**Notes:** _(filled during implementation)_

### Task 3.3: Confirm `_time_phase` semantics preserved [Simple]
**Tests:** `pytest tests/unit/strategy/turn_engine/test_turn_engine_phase_timing.py -v`

- [ ] All `_time_phase`-specific tests pass.
- [ ] `_phase_times` dict keys match the golden-list `phase_key` values.
- [ ] No double-wrapping of EnginePhaseError.

**Notes:** _(filled during implementation)_

### Task 3.4: Migrate or update phase-order pinning tests [Simple]
**File:** `tests/unit/strategy/turn_engine/test_turn_processing.py`

- [ ] If `test_tick_calls_phases_in_order` (lines 69-108) still passes via the new descriptor path: leave as-is.
- [ ] Otherwise: update to assert against `[p.phase_key for p in DEFAULT_TICK_PHASE_LIST]` rather than internal mocks.
- [ ] Add docstring referencing PROJ-365 + the golden-list test in test_default_tick_phase_list.py.

**Notes:** _(filled during implementation)_

### Task 3.5: Optional — hoist PlanetModifierEffectEngine lazy import [Simple]
**File:** `game/strategy/engine/turn_engine.py` (top of module)

- [ ] Try moving `from game.strategy.engine.planet_modifier_effect_engine import PlanetModifierEffectEngine` to module-level.
- [ ] If a circular import emerges, revert and document in decisions.md.
- [ ] If hoisting works: the descriptor's `callable_target` resolver returns `lambda e: PlanetModifierEffectEngine(registries=e._registries).process_modifier_effects_tick` (instance is created per call, matching current semantics).

**Notes:** _(filled during implementation)_

### Task 3.6: Final full focused suite [Simple]
**Tests:** `pytest tests/unit/strategy/turn_engine/ tests/integration/strategy/ -v`

- [ ] All green.
- [ ] LOC delta on `turn_engine.py`: `_process_tick` body shrinks from ~80 LOC to ~20 LOC.
- [ ] No constructor-related changes.
- [ ] End-of-turn engine block (lines 571-602) untouched.

**Notes:** _(filled during implementation)_

---

## Phase Completion Checklist
- [ ] `_process_tick` body ≤ 25 LOC
- [ ] Golden-list test green
- [ ] PROJ-320 invariant green
- [ ] All turn_engine + integration tests green
- [ ] Update plan.md phase table to `Complete`
- [ ] Update Current State: PROJ-365 ready for user verification
