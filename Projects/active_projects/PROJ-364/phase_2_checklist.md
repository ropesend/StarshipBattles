# Phase 2: Define SuperweaponSpec + SUPERWEAPONS table

**Status:** Complete
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

**Notes:** Landed exactly the spec from the plan; ability_name=None only for STELLERATE_STAR. Imports clean — no cycles.

### Task 2.2: Contract test [Simple]
**File:** `tests/unit/strategy/services/test_superweapon_registry_contract.py` (new)

- [x] `test_all_specs_have_valid_order_type` — every `spec.order_type` is an OrderType member.
- [x] `test_all_specs_have_valid_event_type` — every `spec.event_type` is an EventType member.
- [x] `test_all_specs_consume_ship_is_bool` — sanity.
- [x] `TestAbilityRegistryConsistency.test_ability_names_registered` — for each spec where `ability_name is not None`, assert that ability is registered in the component registry (uses `fresh_registries`). Excludes STELLERATE_STAR which has None.
- [x] `test_all_specs_stabilizer_blocks_are_order_types` — every entry's `stabilizer_blocks` member is a known OrderType.
- [x] All 15 tests pass.

**Notes:** Component registry stores ``Component`` instances (not raw dicts); test reads ``comp.abilities`` attribute directly.

### Task 2.3: Optional cross-link to PROJ-363 CommandSpec [Simple]
**File:** Same registry test file

- [x] PROJ-363 has landed: ``TestProj363CommandSpecCrossLink`` asserts the SUPERWEAPONS order types match the 'superweapon' CommandSpecs (excluding SELF_DESTRUCT) AND that ability_name fields agree with action_ability_name.

**Notes:** Cross-link landed and asserts both order-type subset and ability-name parity.

---

## Phase Completion Checklist
- [x] superweapon_registry.py exists with 5 specs
- [x] Contract test green (15 tests)
- [x] No production code outside the new module changed
- [x] Update plan.md phase table to `Complete`; Current State → Phase 3
