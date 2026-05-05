# Phase 3: Spec-driven dispatch + per-weapon effect closures

**Status:** Not Started
**Objective:** Replace each `process_*` method's prologue with a single `execute_superweapon(spec, ...)` shared dispatcher; per-weapon mutation becomes a small effect closure. SELF_DESTRUCT remains untouched. All Phase 1 characterization tests stay green.

---

## Tasks

### Task 3.1: Add `execute_superweapon` dispatcher to SuperweaponOrderProcessor [Medium]
**File:** `game/strategy/engine/superweapon_order_processor.py`
**Tests:** `pytest tests/unit/strategy/engine/test_superweapon* tests/integration/strategy/test_superweapon_integration.py -v`

- [ ] Add new method on `SuperweaponOrderProcessor`:
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
- [ ] Body sequence (the shared prologue):
  1. `order = fleet.get_current_order()`; if `order is None or order.type != spec.order_type`: return failure with appropriate message.
  2. Resolve target per `spec.target_type`:
     - 'planet': `target = order.target`; check `is None` → pop + return failure.
     - 'dict': `params = order.target`; check `isinstance(params, dict)` → pop + return failure.
     - 'none': no target resolution.
  3. Call `_check_blocking_stabilizer` with `spec.order_type`. If blocked, pop + return.
  4. If `spec.ability_name is not None`: call `SuperweaponValidator.find_ship_with_ability(fleet, spec.ability_name, component_registry)`. If None: pop + return failure.
  5. Call `event_kwargs = effect_fn(fleet=fleet, empire=empire, galaxy=galaxy, empires=empires, order=order, ship=ship)` — returns the kwargs to pass to `_finalize_superweapon` (event_message, log_message, plus event-specific kwargs).
  6. Call `self._finalize_superweapon(fleet=fleet, empire=empire, ship=ship, event_type=spec.event_type, consume_ship=spec.consume_ship, **event_kwargs)`.
- [ ] Run Phase 1 characterization tests to ensure the new dispatcher's prologue logic matches; these should all pass once Task 3.2 routes through it.

**Notes:** _(filled during implementation)_

### Task 3.2: Refactor each strategic process_* into spec lookup + effect closure [Complex]
**File:** Same

- [ ] Refactor `process_implode_planet`:
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
- [ ] Same pattern for: `process_open_warp_point`, `process_close_warp_point`, `process_create_dyson_sphere`.
- [ ] `process_stellerate_star`: spec ability_name=None, so step 4 is skipped. The effect closure still calls `system_destroyer` directly.
- [ ] After refactor, each strategic `process_*` method should be < 30 LOC (mostly the effect closure).
- [ ] `process_self_destruct` is UNCHANGED (out of spec).
- [ ] Run Phase 1 + existing test suites — all green.

**Notes:** _(filled during implementation)_

### Task 3.3: Update order_processor.py dispatch [Simple]
**File:** `game/strategy/engine/order_processor.py:704-730`

- [ ] Optionally simplify the `superweapon_handlers` dict to be derived from `SUPERWEAPONS` automatically — though since each strategic `process_*` still exists as a public method on `SuperweaponOrderProcessor`, the existing lambda dict can stay unchanged. (Decision: leave it as-is for now; the win is inside `superweapon_order_processor.py`.)
- [ ] Run integration tests under `tests/integration/strategy/` — green.

**Notes:** _(filled during implementation)_

### Task 3.4: Final full focused suite [Simple]
**Tests:** `pytest tests/unit/strategy/ tests/integration/strategy/ --testmon`

- [ ] All green.
- [ ] Compute LOC delta on `superweapon_order_processor.py` (expect ~660 → ~400 or less).
- [ ] Verify no behavioral regression via `tests/integration/strategy/test_superweapon_integration.py`.

**Notes:** _(filled during implementation)_

---

## Phase Completion Checklist
- [ ] Each strategic `process_*` method ≤ 30 LOC
- [ ] Phase 1 characterization tests still green
- [ ] All existing superweapon tests green
- [ ] Update plan.md phase table to `Complete`
- [ ] Update Current State: PROJ-364 ready for user verification
