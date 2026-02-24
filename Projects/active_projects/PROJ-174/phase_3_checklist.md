# Phase 3: Migrate TIER 2 Production Code to TIER 1

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-174 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Replace all `get_default_registries()` calls in `game/` with `get_default_registry_provider()` or constructor DI. After this phase, zero production code uses the service locator pattern.

---

## Tasks

### Task 3.1: Migrate fleet_capability_calculator.py [Simple]
**File:** `game/strategy/data/fleet_capability_calculator.py`
**Tests:** `pytest tests/unit/strategy/ -v`

- [ ] Replace `_get_default_component_registry()` function (lines 14-17):
  ```python
  # BEFORE:
  def _get_default_component_registry() -> Dict[str, Any]:
      from game.core.registry import get_default_registries
      return get_default_registries().components

  # AFTER:
  def _get_default_component_registry() -> Dict[str, Any]:
      from game.core.registry import get_default_registry_provider
      return get_default_registry_provider().get_components()
  ```
- [ ] Update import at top of file if `get_default_registries` was imported there
- [ ] Verify: Tests pass

**Notes:**

### Task 3.2: Migrate turn_engine.py [Simple]
**File:** `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/unit/strategy/ tests/integration/ -v`

- [ ] Replace import (line 54): change `get_default_registries` to `get_default_registry_provider`
- [ ] Replace fallback (lines 152-155): change `get_default_registries()` to construct a GameRegistries from provider, OR store provider directly:
  ```python
  # Option A (minimal change - keep GameRegistries type):
  if registries is not None:
      self._registries = registries
  else:
      provider = get_default_registry_provider()
      self._registries = GameRegistries(
          components=provider.get_components(),
          modifiers=provider.get_modifiers(),
          vehicle_classes=provider.get_vehicle_classes(),
          resources=provider.get_resources(),
      )
  ```
- [ ] Verify: Tests pass

**Notes:** TurnEngine stores `self._registries` as GameRegistries type. If callers access `.components` etc. directly, keep this type for now. Full GameRegistries removal is out of scope.

### Task 3.3: Migrate ship_instance.py [Simple]
**File:** `game/strategy/data/ship_instance.py`
**Tests:** `pytest tests/unit/strategy/ -v`

- [ ] Replace `get_default_registries()` call (line 233):
  ```python
  # BEFORE:
  registries = get_default_registries()
  service = ShipStatsCalculator(registries=registries)

  # AFTER:
  from game.core.registry import get_default_registry_provider
  provider = get_default_registry_provider()
  service = ShipStatsCalculator(registries=GameRegistries(
      components=provider.get_components(),
      modifiers=provider.get_modifiers(),
      vehicle_classes=provider.get_vehicle_classes(),
      resources=provider.get_resources(),
  ))
  ```
  OR if ShipStatsCalculator accepts a provider directly, use that.
- [ ] Update imports accordingly
- [ ] Verify: Tests pass

**Notes:** Check what ShipStatsCalculator's `registries` param type is. If it accepts GameRegistries, build one from provider. If it could accept IRegistryProvider, even better.

### Task 3.4: Migrate ship_stats.py [Simple]
**File:** `game/simulation/entities/ship_stats.py`
**Tests:** `pytest tests/unit/simulation/ -v`

- [ ] Replace `get_default_registries()` call (line 48):
  ```python
  # BEFORE:
  calculator = ShipStatsCalculator(get_default_registries().vehicle_classes)

  # AFTER:
  calculator = ShipStatsCalculator(get_default_registry_provider().get_vehicle_classes())
  ```
- [ ] Update imports: replace `get_default_registries` with `get_default_registry_provider`
- [ ] Verify: Tests pass

**Notes:** Check if ShipStatsCalculator.__init__ takes full registries or just vehicle_classes dict.

### Task 3.5: Migrate empire_economy_calculator.py [Simple]
**File:** `game/strategy/engine/empire_economy_calculator.py`
**Tests:** `pytest tests/unit/strategy/ -v`

- [ ] Check if `get_default_registries()` is actually called here (may only be passed in from callers)
- [ ] If a static factory method uses it, replace with provider pattern
- [ ] Update imports if needed
- [ ] Verify: Tests pass

**Notes:** Review report indicated this file already uses DI parameter. Verify and skip if no changes needed.

### Task 3.6: Migrate ship_factory.py [Simple]
**File:** `game/ui/services/ship_factory.py`
**Tests:** `pytest tests/unit/builder/ -v`

- [ ] Replace `_get_registries()` fallback (line 56):
  ```python
  # BEFORE:
  from game.core.registry import get_default_registries
  return get_default_registries()

  # AFTER:
  from game.core.registry import get_default_registry_provider, GameRegistries
  provider = get_default_registry_provider()
  return GameRegistries(
      components=provider.get_components(),
      modifiers=provider.get_modifiers(),
      vehicle_classes=provider.get_vehicle_classes(),
      resources=provider.get_resources(),
  )
  ```
- [ ] Update imports
- [ ] Verify: Tests pass

**Notes:** This returns GameRegistries type. Callers access `.components` etc. Keep return type for now.

### Task 3.7: Migrate design_loader_adapter.py [Simple]
**File:** `game/ui/services/design_loader_adapter.py`
**Tests:** `pytest tests/unit/builder/ -v`

- [ ] Replace `get_default_registries()` fallback (line ~42):
  ```python
  # BEFORE:
  registry_provider = get_default_registries()

  # AFTER:
  from game.core.registry import get_default_registry_provider, GameRegistries
  provider = get_default_registry_provider()
  registry_provider = GameRegistries(
      components=provider.get_components(),
      modifiers=provider.get_modifiers(),
      vehicle_classes=provider.get_vehicle_classes(),
      resources=provider.get_resources(),
  )
  ```
- [ ] Update imports
- [ ] Verify: Tests pass

**Notes:** Check what type `registry_provider` is expected to be by its consumers.

### Task 3.8: Migrate planet_report_panel.py [Medium]
**File:** `game/ui/panels/planet_report_panel.py`
**Tests:** `pytest tests/unit/ui/panels/ -v`

- [ ] Replace `get_default_registries()` call (line 469):
  ```python
  # BEFORE:
  registries = get_default_registries()

  # AFTER:
  from game.core.registry import get_default_registry_provider
  provider = get_default_registry_provider()
  # Then use provider.get_components() etc. instead of registries.components
  ```
- [ ] Update all usages of `registries.components`, `registries.modifiers` etc. in surrounding code to use `provider.get_components()`, `provider.get_modifiers()` etc.
- [ ] Update imports
- [ ] Verify: Tests pass

**Notes:** Read surrounding context to understand what registries fields are accessed.

### Task 3.9: Migrate empire_panel_window.py [Simple]
**File:** `game/ui/screens/empire_panel_window.py`
**Tests:** `pytest tests/unit/ui/screens/ -v`

- [ ] Replace `get_default_registries()` call (line 183):
  ```python
  # BEFORE:
  calculator = EmpireEconomyCalculator(registries=get_default_registries())

  # AFTER:
  from game.core.registry import get_default_registry_provider, GameRegistries
  provider = get_default_registry_provider()
  calculator = EmpireEconomyCalculator(registries=GameRegistries(
      components=provider.get_components(),
      modifiers=provider.get_modifiers(),
      vehicle_classes=provider.get_vehicle_classes(),
      resources=provider.get_resources(),
  ))
  ```
- [ ] Update imports
- [ ] Verify: Tests pass

**Notes:** Check what type EmpireEconomyCalculator expects for `registries` param.

### Task 3.10: Migrate workshop_context.py [Medium]
**File:** `game/ui/screens/workshop_context.py`
**Tests:** `pytest tests/unit/builder/test_workshop_context_di.py -v`

- [ ] Replace `__post_init__` method (lines 66-74):
  ```python
  # BEFORE:
  def __post_init__(self):
      if self.registries is None:
          from game.core.registry import get_default_registries
          ...
          object.__setattr__(self, 'registries', get_default_registries())

  # AFTER:
  def __post_init__(self):
      if self.registries is None:
          from game.core.registry import get_default_registry_provider, GameRegistries
          from game.core.exceptions import StateException
          try:
              provider = get_default_registry_provider()
              object.__setattr__(self, 'registries', GameRegistries(
                  components=provider.get_components(),
                  modifiers=provider.get_modifiers(),
                  vehicle_classes=provider.get_vehicle_classes(),
                  resources=provider.get_resources(),
              ))
          except (RuntimeError, StateException):
              pass
  ```
- [ ] Update imports
- [ ] Verify: Tests pass

**Notes:** This is the import-time risk site. The try/except already handles failure gracefully. Keep defensive pattern.

### Task 3.11: Grep verification [Simple]
**Tests:** N/A

- [ ] Run: `grep -r "get_default_registries()" game/ --include="*.py"` — should only match `game/core/registry.py` (definition + docstring)
- [ ] If any other files still reference it, migrate those too
- [ ] Verify: Zero production callers outside registry.py

**Notes:**

### Task 3.12: Full suite verification [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] Run full test suite: 12,023+ passed, 0 failed
- [ ] Verify no regressions

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
