# Phase 2: Define CommandSpec + spec table

**Status:** Not Started
**Objective:** Land `CommandSpec` dataclass and `COMMAND_SPECS` tuple covering all 31 commands. The Phase 1 spec→handler and OrderType-coverage tests should turn green at the end of this phase. Other contract tests (category-sets, action-time, facade-helper) require Phase 3.

---

## Tasks

### Task 2.1: Create specs module [Medium]
**File:** `game/strategy/engine/commands/__init__.py` (new — empty package init)
**File:** `game/strategy/engine/commands/specs.py` (new)
**Tests:** `pytest tests/unit/strategy/engine/test_command_registry_contract.py::test_every_spec_has_registered_handler -v`

- [ ] Create `game/strategy/engine/commands/` package directory with empty `__init__.py`.
- [ ] In `specs.py`, define `CommandSpec`:
  ```python
  from __future__ import annotations
  from dataclasses import dataclass, field
  from typing import Type
  from game.strategy.data.order_types import OrderType
  from game.strategy.engine.commands import (
      IssueColonizeCommand, IssueMoveCommand, ...   # all 31
  )
  from game.strategy.engine.handlers.movement import (
      ColonizeCommandHandler, MoveCommandHandler, ...
  )
  # ...other handler imports

  @dataclass(frozen=True)
  class CommandSpec:
      command_class: type
      order_type: OrderType | None
      handler_class: type
      category: str
      subcategories: frozenset[str] = frozenset()
      action_ability_name: str | None = None
      execution_model: str = 'action'   # 'action' | 'production' | 'instant' | 'mission' | 'planet'
      facade_helper_name: str | None = None
      serializer_codec: str | None = None
  ```

**Notes:** _(filled during implementation)_

### Task 2.2: Populate COMMAND_SPECS for movement commands [Simple]
**File:** Same

- [ ] Add specs for the 5 movement commands:
  - `IssueMoveCommand` → MOVE, MoveCommandHandler, category='movement', execution_model='action'
  - `IssueColonizeCommand` → COLONIZE, ColonizeCommandHandler, category='movement+action' (Codex review may push category='action'; align with existing frozenset membership)
  - `IssueInterceptCommand` → MOVE_TO_FLEET, InterceptCommandHandler, category='movement'
  - `IssueJoinFleetCommand` → JOIN_FLEET, JoinCommandHandler, category='movement', execution_model='instant'
  - `IssueWarpCommand` → WARP, WarpCommandHandler, category='movement'
- [ ] Set `facade_helper_name` to match existing `dispatch_*` method names (e.g. `dispatch_issue_move_command`).

**Notes:** _(filled during implementation)_

### Task 2.3: Populate COMMAND_SPECS for action commands [Medium]
- [ ] Add specs for: `IssueTransferCommand`, `IssueLoadPopulationCommand`, `IssueUnloadPopulationCommand`, `IssueColonizeMissionCommand` (mission), `QueueColonizeMissionCommand` (mission), `IssueActivateAbilityCommand`, `IssueDeactivateAbilityCommand`.
- [ ] Mission commands: `order_type=None`, `execution_model='mission'`.

### Task 2.4: Populate COMMAND_SPECS for superweapon commands [Medium]
- [ ] Add specs for the 6 immediate superweapons: `IssueImplodePlanetCommand`, `IssueStellerateStarCommand`, `IssueOpenWarpPointCommand`, `IssueCloseWarpPointCommand`, `IssueCreateDysonSphereCommand`, `IssueSelfDestructCommand`.
- [ ] Add specs for the 5 mission variants: `Queue*MissionCommand`.
- [ ] All immediate: `category='superweapon'`, `execution_model='action'`. Mission variants: `execution_model='mission'`.
- [ ] Note: PROJ-364 will use `category='superweapon'` to drive its own dispatch table — keep this category stable.

### Task 2.5: Populate COMMAND_SPECS for build/queue/management commands [Simple]
- [ ] BUILD-related: `IssueBuildOrderCommand`, `RemoveBuildOrderCommand` — `category='build'`, `execution_model='production'` (for IssueBuildOrderCommand).
- [ ] Construction queue: `AddToConstructionQueueCommand`, `RemoveFromConstructionQueueCommand`, `ReorderConstructionQueueCommand`, `SetBuildQueuePausedCommand` — category='construction', execution_model='instant'.
- [ ] Fleet management: `SplitFleetCommand`, `DeleteOrderCommand`, `ReorderOrderCommand`, `ClearOrdersCommand` — category='fleet_management', execution_model='instant'.

### Task 2.6: Populate COMMAND_SPECS for planet commands [Simple]
- [ ] `IssuePlanetOrderCommand`, `ClearPlanetOrdersCommand`, `DeletePlanetOrderCommand`, `SetAtmosphereTargetCommand`, `SetGravityTargetCommand`, `SetWaterTargetCommand`, `SetRadiationShieldTargetCommand` — category='planet', execution_model='planet' or 'instant' as appropriate.

### Task 2.7: Verify contract tests for Phase 2 turn green [Simple]
- [ ] Run `pytest tests/unit/strategy/engine/test_command_registry_contract.py::test_every_spec_has_registered_handler tests/unit/strategy/engine/test_command_registry_contract.py::test_every_order_type_has_at_least_one_spec -v` — both pass.
- [ ] Other contract tests still fail (category-sets and action-time pending Phase 3, facade-helper pending Phase 4) — that's expected.
- [ ] Run existing `tests/unit/strategy/test_command_handlers.py` — all still pass (registry hasn't changed yet).

**Notes:** _(filled during implementation)_

---

## Phase Completion Checklist
- [ ] 31 specs in COMMAND_SPECS
- [ ] Spec→handler contract test green
- [ ] OrderType-coverage contract test green
- [ ] No production code outside specs.py changed
- [ ] Update plan.md phase table to `Complete`; Current State → Phase 3
