"""PROJ-350 regression: TestRegistry must not break template class identity.

Background: `combat_lab/registry.py` previously discovered scenario files via
`importlib.util.spec_from_file_location` + `module_from_spec` + `exec_module`,
which bypasses Python's import cache. Because the glob included
`combat_lab/scenarios/templates.py` (the file defining the canonical template
base classes), discovery re-executed `templates.py` and overwrote
`sys.modules['combat_lab.scenarios.templates']` with a fresh module containing
brand-new `ComparisonScenario` / `StaticTargetScenario` / etc. class objects.

Modules imported earlier (notably `combat_lab/spec_compiler.py` via
`combat_lab/runner.py:20`) cached references to the *original* template
classes. Registry-discovered scenarios subclassed the *post-discovery* template
classes. `isinstance(scenario, ComparisonScenario)` in `spec_compiler` then
returned False, and dispatch fell through to `NotImplementedError`.

This test pins the invariant: after registry discovery runs, every registered
ComparisonScenario subclass must still be recognised by the spec compiler's
`ComparisonScenario`, and `build_test_battle_spec` must dispatch it without
raising.
"""
from __future__ import annotations

import combat_lab.spec_compiler as spec_compiler_mod
from combat_lab.registry import TestRegistry
from combat_lab.scenarios.templates import ComparisonScenario
from combat_lab.spec_compiler import build_test_battle_spec


def test_registry_discovery_preserves_template_class_identity() -> None:
    """Registry-discovered scenarios share class identity with the spec compiler.

    Reproduction recipe for the original bug:
      1. `combat_lab.spec_compiler` is imported (cached its template refs).
      2. `TestRegistry()` runs discovery, re-executing `templates.py`.
      3. Registered scenarios subclass the *new* template classes; spec_compiler
         still holds the *old* ones; isinstance returns False; dispatch raises.

    With the fix in place (`importlib.import_module`), step 2 no longer creates
    a duplicate module, so all template classes in the process remain identical
    objects.
    """
    # Force a fresh discovery run so this test reproduces the original
    # production flow (TestLabScreen.__init__ instantiating TestRegistry after
    # spec_compiler is already loaded), even if a prior test in the session
    # already populated the singleton.
    TestRegistry.reset()
    registry = TestRegistry()

    # TOHIT-ATK-001 (`SensorIncreasesAccuracyScenario`) is the scenario the
    # user crashed on. It extends `ComparisonScenario`.
    info = registry.scenarios.get("TOHIT-ATK-001")
    assert info is not None, "TOHIT-ATK-001 must be discovered by the registry"

    scenario_cls = info["class"]
    instance = scenario_cls()

    # Class-identity invariant: the spec compiler's `ComparisonScenario` must
    # be the same class object the registry-discovered scenario inherits from.
    assert isinstance(instance, ComparisonScenario), (
        "Registry-discovered ComparisonScenario subclass must be recognised "
        "by the template class the spec compiler imports. If this fails, "
        "TestRegistry has loaded a duplicate copy of "
        "combat_lab.scenarios.templates."
    )

    # And the compiler module itself must reference the same class object —
    # belt-and-suspenders against any future regression where someone reaches
    # into spec_compiler's globals directly.
    compiler_cs = spec_compiler_mod.ComparisonScenario  # type: ignore[attr-defined]
    assert compiler_cs is ComparisonScenario, (
        "spec_compiler.ComparisonScenario must be the same class object as "
        "combat_lab.scenarios.templates.ComparisonScenario."
    )

    # Functional check: the original crash site no longer fires
    # `NotImplementedError` for this scenario.
    spec = build_test_battle_spec(instance, registries=None)
    assert spec is not None
