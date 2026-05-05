# Phase 2: Define SuperweaponSpec + SUPERWEAPONS table

**Status:** Not Started
**Objective:** Land the `SuperweaponSpec` dataclass, the `SUPERWEAPONS` tuple, and a contract test. Production code dispatch is unchanged in this phase — Phase 3 wires it in.

---

## Tasks

### Task 2.1: Create superweapon_registry module [Medium]
**File:** `game/strategy/services/superweapon_registry.py` (new)
**Tests:** `pytest tests/unit/strategy/services/test_superweapon_registry_contract.py -v`

- [ ] Module docstring referencing PROJ-364 Phase 2 + the stabilizer_registry pattern.
- [ ] Define:
  ```python
  from __future__ import annotations
  from dataclasses import dataclass
  from game.strategy.data.order_types import OrderType
  from game.strategy.events import EventType   # find correct import path

  @dataclass(frozen=True)
  class SuperweaponSpec:
      order_type: OrderType
      ability_name: str | None
      target_type: str               # 'planet' | 'dict' | 'none'
      consume_ship: bool
      event_type: EventType
      stabilizer_blocks: tuple[OrderType, ...]

  SUPERWEAPONS: tuple[SuperweaponSpec, ...] = (
      SuperweaponSpec(OrderType.IMPLODE_PLANET, "DestroyPlanet", "planet", False,
                      EventType.PLANET_DESTROYED, (OrderType.IMPLODE_PLANET,)),
      SuperweaponSpec(OrderType.STELLERATE_STAR, None, "none", True,
                      EventType.STAR_DESTROYED, (OrderType.STELLERATE_STAR,)),
      SuperweaponSpec(OrderType.OPEN_WARP_POINT, "OpenWarpPoint", "dict", False,
                      EventType.WARP_POINT_OPENED, (OrderType.OPEN_WARP_POINT,)),
      SuperweaponSpec(OrderType.CLOSE_WARP_POINT, "CloseWarpPoint", "dict", False,
                      EventType.WARP_POINT_CLOSED, (OrderType.CLOSE_WARP_POINT,)),
      SuperweaponSpec(OrderType.CREATE_DYSON_SPHERE, "CreateDysonSphere", "none", False,
                      EventType.DYSON_SPHERE_CREATED, (OrderType.CREATE_DYSON_SPHERE,)),
  )

  def find_superweapon_spec(order_type: OrderType) -> SuperweaponSpec | None:
      return next((s for s in SUPERWEAPONS if s.order_type == order_type), None)
  ```

**Notes:** _(filled during implementation)_

### Task 2.2: Contract test [Simple]
**File:** `tests/unit/strategy/services/test_superweapon_registry_contract.py` (new)

- [ ] `test_all_specs_have_valid_order_type` — every `spec.order_type` is an OrderType member.
- [ ] `test_all_specs_have_valid_event_type` — every `spec.event_type` is an EventType member.
- [ ] `test_all_specs_consume_ship_is_bool` — sanity.
- [ ] `test_all_specs_with_ability_name_match_component_registry` — for each spec where `ability_name is not None`, assert that ability is registered in the component registry (use `fresh_registries`). Excludes STELLERATE_STAR which has None.
- [ ] `test_all_specs_have_matching_stabilizer_or_documented_exception` — every entry's `stabilizer_blocks` member is a known OrderType.
- [ ] All tests pass.

**Notes:** _(filled during implementation)_

### Task 2.3: Optional cross-link to PROJ-363 CommandSpec [Simple]
**File:** Same registry test file or extend test_command_registry_contract.py

- [ ] If PROJ-363 has landed: assert `{spec.order_type for spec in SUPERWEAPONS}` is a subset of `{cmd.order_type for cmd in COMMAND_SPECS if cmd.category == 'superweapon'}`. Skip with `pytest.skip` if PROJ-363 hasn't landed yet.

**Notes:** _(filled during implementation)_

---

## Phase Completion Checklist
- [ ] superweapon_registry.py exists with 5 specs
- [ ] Contract test green
- [ ] No production code outside the new module changed
- [ ] Update plan.md phase table to `Complete`; Current State → Phase 3
