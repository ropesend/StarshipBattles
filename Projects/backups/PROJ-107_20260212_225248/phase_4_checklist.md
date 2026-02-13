# Phase 4: UI Service DI & Return Type Standardization

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-107 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Standardize UI service DI patterns to a single convention. Standardize ShipIOAdapter return type semantics.

**Findings:** CON-UI2-001, CON-UI2-005, CON-UI2-007

---

## Tasks

### Task 4.1: Document Standard DI Pattern for UI Services [Simple]
**File:** Create or update service-level documentation
**Tests:** No code changes - documentation only

The 4 services use different DI patterns:
1. **ComponentService** - `registry_provider: Optional[IRegistryProvider] = None` (lazy default)
2. **VehicleClassService** - `registry_provider: IRegistryProvider` (strict required, raises ValueError if None)
3. **ShipFactory** - `*, registries: Optional[GameRegistries] = None` (keyword-only, lazy default)
4. **DesignLoaderAdapter** - `design_loader: Optional[Any] = None, *, registries: Optional[Any] = None` (dual parameters)

Decision: Standardize on the **ComponentService** pattern (optional with lazy default) as the baseline. VehicleClassService strict pattern is acceptable since PROJ-50 explicitly made it required.

- [x] Add docstring to ComponentService.__init__ clarifying this is the standard DI pattern
- [x] Rename `registries` parameter in ShipFactory to `registry_provider` for naming consistency with ComponentService/VehicleClassService
- [x] Update ShipFactory._get_registries to match new param name
- [x] Grep for all `ShipFactory(registries=` call sites and update to `ShipFactory(registry_provider=`
  - Note: ShipFactory uses keyword-only args so all call sites use the keyword form
  - Updated: docstring example only, other call sites use no kwargs
- [x] Rename DesignLoaderAdapter `registries` kwarg to `registry_provider`
- [x] Update DesignLoaderAdapter.__init__ body to use new param name
- [x] Grep for all `DesignLoaderAdapter(` call sites and update keyword args
  - Updated: workshop_screen.py (only call site using registries kwarg)
- [x] Verify: `pytest tests/ -n 12 -k "ship_factory or design_loader or component_service or vehicle_class"` passes

**Notes:** We're standardizing the *parameter name* (registry_provider) not the pattern (strict vs optional). Each service can still choose strict or optional based on its PROJ-50 status.

---

### Task 4.2: Standardize ShipIOAdapter Return Type Semantics [Medium]
**File:** `game/ui/services/ship_io_adapter.py`
**Tests:** `pytest tests/unit/ui/ -v -k ship_io`

Current inconsistency:
- `save_ship()` -> `Tuple[bool, Optional[str]]` (bool = success)
- `load_ship()` -> `Tuple[Optional[Any], Optional[str]]` (None ship = failure)

Decision: Keep both signatures as-is (they represent genuinely different semantics: save returns success flag, load returns the loaded object). Instead, add clear docstring documentation of the contract.

- [x] Verify save_ship docstring clearly documents the three cases: success, failure, cancel
- [x] Verify load_ship docstring clearly documents the three cases: success, failure, cancel
- [x] Add a class-level docstring section documenting the return value contract:
  ```
  Return Value Convention:
      - save operations: Tuple[bool, Optional[str]] where bool=success
      - load operations: Tuple[Optional[T], Optional[str]] where T=loaded object
      - For both: message=None means user cancelled the dialog
  ```
- [x] Verify: `pytest tests/unit/ui/ -v` passes (1407 passed)

**Notes:** The different return types are intentional - save has no object to return. Documenting the convention is sufficient.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run full test suite: `pytest tests/ -n 12` (8185 passed)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
