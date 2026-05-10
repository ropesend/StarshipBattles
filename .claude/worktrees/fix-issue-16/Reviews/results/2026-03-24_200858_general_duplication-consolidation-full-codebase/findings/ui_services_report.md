# UI Services, Renderer, Orchestration & Research - Duplication Report

## Summary

Reviewed all 21 Python files across `game/ui/services/`, `game/ui/renderer/`, `game/ui/orchestration/`, and `game/ui/research/`. The codebase is generally well-factored -- prior PROJ-141 remediation (DUP-UI2-001, DUP-UI2-002, DUP-UI2-006) already consolidated major tkinter initialization, battle controller creation, and ship cloning duplication. Remaining findings are moderate in scope.

**Files reviewed:** 21
**Findings:** 6 (2 MAJOR, 4 MINOR)

---

## Findings

#### MAJOR: Repeated Registry Provider Null-Check + ValidationException Pattern
**ID:** DUP-UIS-001
**Location:** `game/ui/services/vehicle_class_service.py:46-53`, `game/ui/services/component_service.py:44-51`, `game/ui/services/ship_factory.py:49-56`, `game/ui/services/design_loader_adapter.py:49-54`
**Issue:** Four services repeat the identical registry_provider null-check guard:
```python
if registry_provider is None:
    raise ValidationException(
        "registry_provider is required",
        code=ErrorCode.MISSING_DEPENDENCY.value,
        context={"service": "<ServiceName>", "parameter": "registry_provider"}
    )
```
The only difference is the `"service"` value in the context dict. This 6-line pattern is duplicated 4 times (24 lines total).
**Impact:** Maintenance burden when changing validation behavior (e.g., error code, message format). Easy to introduce inconsistency -- `DesignLoaderAdapter` already has a slightly different condition (nested under `if design_loader is None`).
**Recommendation:** Extract a shared helper function, e.g., `validate_required_dependency(value, service_name, param_name)` in `game/core/exceptions.py` or a new `game/ui/services/_validation.py` helper. Each service reduces to a one-liner call.
**Effort:** Simple

---

#### MAJOR: Parallel _get_provider() / _get_registries() Accessor Pattern
**ID:** DUP-UIS-002
**Location:** `game/ui/services/vehicle_class_service.py:56-58`, `game/ui/services/component_service.py:54-56`, `game/ui/services/ship_factory.py:59-61`
**Issue:** Three services have a trivial one-line accessor that just returns `self._provider` or `self._registry_provider`. While small individually, these exist because all three services follow the same "store provider in __init__, expose via accessor" pattern. `VehicleClassService` and `ComponentService` are structurally near-identical -- both accept `IRegistryProvider`, store it, and provide registry data access methods through it.
**Impact:** Low immediate impact, but the structural duplication between `VehicleClassService` and `ComponentService` suggests they could share a base class. Both: (1) validate registry_provider in __init__, (2) store it, (3) expose a _get_provider() accessor, (4) delegate to provider.get_X() methods. If more registry-backed services are added, the boilerplate will grow.
**Recommendation:** Create a `RegistryBackedService` base class that handles the null-check, storage, and _get_provider() accessor. `VehicleClassService`, `ComponentService`, and `ShipFactory` extend it. This also resolves DUP-UIS-001 by centralizing the null-check.
**Effort:** Medium

---

#### MINOR: Bounding-Box Center Camera Pattern
**ID:** DUP-UIS-003
**Location:** `game/ui/research/research_scene.py:164-178` (`_center_camera`), `game/ui/renderer/camera.py:151-172` (`fit_objects`), also `game/ui/screens/galaxy_test/galaxy_mode.py:311-334`, `game/ui/screens/galaxy_test/system_mode.py:286-309`
**Issue:** The "find min/max bounds of objects, compute center, set camera position" pattern appears in 4+ places. The `Camera.fit_objects()` method already exists and does exactly this for objects with `.position` attributes, but `ResearchTreeScene._center_camera()` and the galaxy test modes re-implement it manually for different data structures (dict positions, hex coordinates).
**Impact:** Moderate -- the implementations are similar but not identical (different data sources), so a naive consolidation would require a more generic interface.
**Recommendation:** Extend `Camera.fit_objects()` to accept a list of `(x, y)` tuples (or add a `Camera.fit_to_bounds(min_x, min_y, max_x, max_y)` method). The research scene and galaxy modes can pre-compute bounds and call the shared method. Note: galaxy_mode and system_mode are outside the primary review scope but included for completeness.
**Effort:** Medium

---

#### MINOR: Ships Folder Path Construction Duplicated in ShipIO
**ID:** DUP-UIS-004
**Location:** `game/ui/services/ship_io.py:95` and `game/ui/services/ship_io.py:142`
**Issue:** The `ships_folder = os.path.join(os.getcwd(), ShipIO.default_ships_folder)` expression and the subsequent `os.makedirs` guard are duplicated between `save_ship()` and `load_ship()` within the same class.
**Impact:** Low -- it's within a single file, but violates DRY.
**Recommendation:** Extract a `_ensure_ships_folder()` classmethod that returns the path and creates the directory if needed.
**Effort:** Simple

---

#### MINOR: ShipIOAdapter is a Thin Pass-Through with Low Value
**ID:** DUP-UIS-005
**Location:** `game/ui/services/ship_io_adapter.py` (entire file, 103 lines)
**Issue:** `ShipIOAdapter` wraps `ShipIO` with methods that are pure pass-throughs: `save_ship()` calls `self._ship_io.save_ship()`, `load_ship()` calls `self._ship_io.load_ship()`, etc. Now that `ShipIO` has been moved to `game/ui/services/ship_io.py` (PROJ-113), both classes live in the same package. The adapter was created when `ShipIO` lived in the simulation layer to avoid direct UI->simulation imports, but that justification no longer applies.
**Impact:** 103 lines of indirection that adds complexity without providing abstraction benefit. Callers could use `ShipIO` directly.
**Recommendation:** Evaluate whether `ShipIOAdapter` can be removed and callers redirected to `ShipIO` directly. If the adapter is kept for testing seam purposes, document that rationale explicitly.
**Effort:** Medium (need to audit all call sites)

---

#### MINOR: BattleOrchestrator Overlap with battle_factories.py
**ID:** DUP-UIS-006
**Location:** `game/ui/orchestration/battle_orchestrator.py` (entire file, 98 lines) vs `game/ui/services/battle_factories.py`
**Issue:** `BattleOrchestrator` creates AI controllers for battle ships, while `battle_factories.py` creates `BattleController` instances (which internally handle AI creation via `AIControllerFactory`). Both modules serve the "set up a battle" concern but through different mechanisms. `BattleOrchestrator` is referenced in `BattleEngine` comments (PROJ-17) for pre-created AI controllers, while `battle_factories` uses the newer `BattleController.configure()` + `AIControllerFactory` pattern. A grep shows `BattleOrchestrator` is only referenced in `battle_engine.py` comments and its own module -- it may be a legacy artifact superseded by the `AIControllerFactory` approach.
**Impact:** Two parallel mechanisms for battle AI setup creates confusion about which to use. If `BattleOrchestrator` is unused, it's dead code.
**Recommendation:** Verify whether `BattleOrchestrator` is actually instantiated anywhere (grep suggests it is not). If confirmed unused, delete it per the project's "eradicate old systems" policy. If still needed, document the distinction from `battle_factories.py`.
**Effort:** Simple (if unused -- just delete)

---

## Top 5 Priority List

| Priority | ID | Title | Severity | Effort |
|----------|----|-------|----------|--------|
| 1 | DUP-UIS-006 | BattleOrchestrator potentially dead code | MINOR | Simple |
| 2 | DUP-UIS-001 | Registry provider null-check duplication (4x) | MAJOR | Simple |
| 3 | DUP-UIS-002 | RegistryBackedService base class extraction | MAJOR | Medium |
| 4 | DUP-UIS-004 | Ships folder path in ShipIO | MINOR | Simple |
| 5 | DUP-UIS-005 | ShipIOAdapter redundancy after PROJ-113 move | MINOR | Medium |

**Rationale:** DUP-UIS-006 is highest priority because dead code should be eradicated immediately (per project policy). DUP-UIS-001 and DUP-UIS-002 address the most widespread structural duplication. DUP-UIS-004 is a quick win. DUP-UIS-005 requires more investigation but could simplify the codebase significantly.
