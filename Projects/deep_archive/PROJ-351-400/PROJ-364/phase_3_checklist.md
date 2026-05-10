# Phase 3: Spec-driven dispatch + per-weapon effect closures

**Status:** Complete
**Objective:** Replace each `process_*` method's prologue with a single `execute_superweapon(spec, ...)` shared dispatcher; per-weapon mutation becomes a small effect closure. SELF_DESTRUCT remains untouched. All Phase 1 characterization tests stay green.

---

## Tasks

### Task 3.1: Add `execute_superweapon` dispatcher to SuperweaponOrderProcessor [Medium]
**File:** `game/strategy/engine/superweapon_order_processor.py`
**Tests:** `pytest tests/unit/strategy/engine/test_superweapon* tests/integration/strategy/test_superweapon_integration.py -v`

- [x] Add new method on `SuperweaponOrderProcessor`:
  ```python
  def execute_superweapon(
      self,
      fleet: Fleet,
      empire: 'Empire',
      galaxy: Galaxy,
      empires: List['Empire'],
      spec: SuperweaponSpec,
      effect_fn: Callable[..., dict],   # returns event_kwargs dict
      component_registry: Optional[Dict[str, Any]] = None,
  ) -> SuperweaponResult:
  ```
- [x] Body sequence (the shared prologue):
  1. `order = fleet.get_current_order()`; if `order is None or order.type != spec.order_type`: return failure with appropriate message.
  2. Resolve target per `spec.target_type`:
     - 'planet': `target = order.target`; check `is None` → pop + return failure.
     - 'dict': `params = order.target`; check `isinstance(params, dict)` → pop + return failure.
     - 'none': no target resolution.
  3. Call `_check_blocking_stabilizer` with `spec.order_type`. If blocked, pop + return.
  4. If `spec.ability_name is not None`: call `SuperweaponValidator.find_ship_with_ability(fleet, spec.ability_name, component_registry)`. If None: pop + return failure.
  5. Call `event_kwargs = effect_fn(fleet=fleet, empire=empire, galaxy=galaxy, empires=empires, order=order, ship=ship)` — returns the kwargs to pass to `_finalize_superweapon` (event_message, log_message, plus event-specific kwargs).
  6. Call `self._finalize_superweapon(fleet=fleet, empire=empire, ship=ship, event_type=spec.event_type, consume_ship=spec.consume_ship, **event_kwargs)`.
- [x] Run Phase 1 characterization tests to ensure the new dispatcher's prologue logic matches; these all pass.

**Notes:** Dispatcher signature ended up needing an additional `precheck_fn` callback to preserve pre-refactor failure-message ordering (e.g. "Fleet not at a star system" must beat "No ship with X ability" — see `test_processor_fails_when_fleet_not_at_star_system`, `test_open_warp_point_target_system_not_found`). Per-weapon precheck closures handle "fleet at system?", "system has stars?", "destination_id present?", "target system exists?". Stabilizer + ability-ship checks remain in the dispatcher. Effect closures handle weapon-specific mutation + return event_kwargs.

### Task 3.2: Refactor each strategic process_* into spec lookup + effect closure [Complex]
**File:** Same

- [x] Refactor `process_implode_planet`:
  ```python
  def process_implode_planet(self, fleet, empire, galaxy, empires, component_registry=None):
      spec = find_superweapon_spec(OrderType.IMPLODE_PLANET)

      def _effect(*, fleet, empire, galaxy, empires, order, ship):
          target_planet = order.target
          if target_planet.owner_id is not None:
              for emp in empires:
                  if target_planet in emp.colonies:
                      emp.colonies.remove(target_planet)
          galaxy.unregister_planet(target_planet)
          return {
              'event_message': f"Planet {target_planet.name} destroyed",
              'log_message': f"Planet {target_planet.name} destroyed by fleet {fleet.id}",
              'planet_id': target_planet.id,
              'planet_name': target_planet.name,
          }
      return self.execute_superweapon(fleet, empire, galaxy, empires, spec, _effect, component_registry)
  ```
- [x] Same pattern for: `process_open_warp_point`, `process_close_warp_point`, `process_create_dyson_sphere`.
- [x] `process_stellerate_star`: spec ability_name=None, so ability-ship lookup is skipped. The effect closure delegates to `system_destroyer`. Suicide path: dispatcher emits the STAR_DESTROYED event ad-hoc with `consume_ship=True` and skips `_finalize_superweapon` to keep the order un-popped (matches Phase 1 characterization).
- [~] LOC target: each `process_*` is now (precheck closure + effect closure + spec lookup + dispatch call). Method bodies are 34/52/69/74/96 lines respectively — larger than the 30-LOC target because the effect closures retain weapon-specific code (race_config preferences for Dyson Sphere; warp-point math for OPEN_WARP_POINT; legacy back-compat for CLOSE_WARP_POINT). The duplicated PROLOGUE is gone, which was the actual goal.
- [x] `process_self_destruct` is UNCHANGED (out of spec).
- [x] Run Phase 1 + existing test suites — all green (163/163 superweapon tests, 4298/4298 strategy tests, 17645/17645 full suite via direct pytest run).

**Notes:** Final design: dispatcher = order/target-shape check → precheck_fn → stabilizer → ability-ship → effect_fn → finalize-or-suicide-emit. Effect closures may return either a dict (event_kwargs) or a `SuperweaponResult(success=False, ...)` to short-circuit (e.g. CLOSE_WARP_POINT wrong-sector check stays in effect closure since it requires expected_hex parsed from order.target).

### Task 3.3: Update order_processor.py dispatch [Simple]
**File:** `game/strategy/engine/order_processor.py:704-730`

- [x] Per the plan's own decision, `order_processor.py:704-725` lambda dict is left as-is — each strategic `process_*` still exists as a public method on `SuperweaponOrderProcessor`, so the dispatch table is fine.
- [x] Run integration tests under `tests/integration/strategy/` — green.

**Notes:** Decision deferred to a follow-up if desired. Today's win is the eliminated prologue duplication inside `superweapon_order_processor.py`.

### Task 3.4: Final full focused suite [Simple]
**Tests:** `pytest tests/unit/strategy/ tests/integration/strategy/ --testmon`

- [x] All green.
- [~] LOC delta: 772 → 780 (slight increase). The dispatcher adds ~115 LOC; per-weapon prologue removal saves comparable LOC; net is roughly flat. The structural win is duplicate-prologue removal (5 copies → 1 dispatcher), not raw LOC reduction.
- [x] No behavioral regression — integration test green.

**Notes:** Direct pytest run of full suite: 17645 passed, 4 skipped, 0 failed. Sharded runner shows occasional transient errors on shards (different shards each run) that are concurrency artifacts of the parallel PROJ-359 agent's activity, not Phase 3 regressions — confirmed by the clean direct-pytest run.

---

## Phase Completion Checklist
- [~] Each strategic `process_*` method ≤ 30 LOC — partially: prologue duplication is GONE (the actual structural goal). Method bodies are 34-96 LOC due to retained weapon-specific code (race_config, hex math, legacy back-compat) inside effect closures.
- [x] Phase 1 characterization tests still green
- [x] All existing superweapon tests green
- [x] Update plan.md phase table to `Complete`
- [x] Update Current State: PROJ-364 ready for user verification
