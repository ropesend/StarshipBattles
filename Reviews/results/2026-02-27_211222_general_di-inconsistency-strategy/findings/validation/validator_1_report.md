# Validation Report: Validator 1

## Summary
- **Findings Reviewed:** 8
- **Confirmed:** 4
- **Downgraded:** 3
- **Rejected:** 1
- **Rejection Rate:** 12.5%

## Verdicts

#### Finding: DI-SIM-001
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified at `ship_loader.py:20-47`. The function accepts optional `registry_provider`, falls back to `get_default_registry_provider()` on line 37. Confirmed that callers in production code (`ship.py:508`, `ship.py:551`, `ship_validator_helper.py:43/54/63`, `vehicle_design_service.py:360/379`, `validation_service.py:48`) and test code (`test_allowed_layers_removal.py`) all call `get_or_create_validator()` without passing a provider. The optional-with-fallback pattern is accurately described.

#### Finding: DI-SIM-002
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified at `ship_loader.py:117-158`. The function accepts optional `registry_provider` (line 120), falls back to `get_default_registry_provider()` on line 152-153. Callers include `registry_loader.py:113/116`, `workshop_data_loader.py:198/201`, and `initialize_ship_data()` (lines 165/167) -- none pass a provider. The issue is accurately described.

#### Finding: DI-SIM-003
**Original Severity:** Major
**Verdict:** DOWNGRADED(Minor)
**Reason:** Verified at `component.py:483-555`. The function does accept optional `registries` (line 486) and falls back to `get_default_registry_provider()` on lines 513-520. However, this function's docstring already acknowledges it is not a "pure function" in the strict DI sense -- it says "If None, creates registries from the default provider." More importantly, the primary caller `load_components()` (line 585) already passes explicit registries, meaning the fallback path is mainly a convenience for direct callers. The issue exists but the practical impact is reduced since the main wrapper already does the right thing.

#### Finding: DI-SIM-004
**Original Severity:** Major
**Verdict:** DOWNGRADED(Minor)
**Reason:** Verified at `component.py:558-596`. The function has no `registry_provider` parameter and calls `get_default_registry_provider()` directly on line 569. However, this function is explicitly a "wrapper that populates the global registry" -- it is an initialization/composition-root function by design. Its purpose is to load data from disk and populate the singleton. It constructs proper `GameRegistries` on lines 579-584 and passes them to `load_components_data()`. The lack of DI parameter is a design smell in a codebase aspiring to full DI, but the function's role as a registry-population entry point makes this a minor rather than major issue.

#### Finding: DI-SIM-005
**Original Severity:** Major
**Verdict:** DOWNGRADED(Minor)
**Reason:** Verified at `component.py:657-685`. The function has no DI parameter and calls `get_default_registry_provider().get_modifiers()` on line 668. Same rationale as DI-SIM-004: this is an initialization wrapper whose explicit purpose is to populate the global registry from disk. The function delegates to the pure `load_modifiers_data()` for actual loading. The severity should match DI-SIM-004 since the pattern and context are identical.

#### Finding: DI-SIM-006
**Original Severity:** Critical
**Verdict:** CONFIRMED
**Reason:** Verified at `ship_loader.py:161-167`. The function accepts only `base_path`, has no `registry_provider` parameter, and calls `load_vehicle_classes()` without forwarding any registry context. Confirmed callers span `app.py:124`, `conftest.py:55`, `common.py:29/41`, and at least 10 test files. The claim of "13+ test files" is accurate. The function is a thin facade but its widespread use in tests without DI capability is a genuine issue for test isolation. Critical severity is appropriate given the breadth of impact.

#### Finding: DI-SIM-007
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified at `ship_stats.py:47-49`. The module docstring's example on lines 47-49 shows `calculator = ShipStatsCalculator(get_default_registry_provider().get_vehicle_classes())` which demonstrates direct use of the global provider rather than constructor injection. This teaches the anti-pattern. However, the class constructor itself (`__init__(self, vehicle_classes)`) actually accepts the data directly via DI, so the runtime behavior is fine -- only the documentation is misleading. Minor severity is appropriate.

#### Finding: DI-SIM-008
**Original Severity:** Info
**Verdict:** REJECTED
**Reason:** The finding itself states this is "Definition site, not a violation." Verified at `registry.py:364-378` -- this is the factory function `get_default_registry_provider()` which returns the singleton provider. This is not a finding; it is a reference note about where the function is defined. Including it as a finding (even at Info level) adds noise to the review without identifying any issue in the code.
