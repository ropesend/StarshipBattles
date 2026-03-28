"""
Combat Lab Test Runner

Discovers and runs all simulation test scenarios without pytest.
Replaces the simulation_tests/tests/ directory.

Usage:
    python -m simulation_tests.run_tests                # Run all
    python -m simulation_tests.run_tests BEAM           # Filter by ID prefix
    python -m simulation_tests.run_tests PROP-001       # Run specific test
    python -m simulation_tests.run_tests --list         # List all tests
"""

import sys
import os
import time
import argparse
import importlib

# Ensure project root is on path
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_THIS_DIR)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)


def init_environment():
    """Initialize pygame and validate test data schemas."""
    import pygame
    pygame.init()

    from simulation_tests.data.schema_validator import validate_test_data
    _passed, failed = validate_test_data(verbose=False)
    if failed > 0:
        print(f"FATAL: {failed} schema validation errors. Fix before running tests.")
        sys.exit(1)


def discover_scenarios():
    """
    Import all scenario modules and return a sorted list of scenario classes.

    Returns:
        List of (test_id, scenario_class) tuples sorted by test_id.
    """
    from simulation_tests.scenarios.base import TestScenario

    # Import all scenario modules to register subclasses
    scenario_modules = [
        'simulation_tests.scenarios.beam_scenarios',
        'simulation_tests.scenarios.projectile_scenarios',
        'simulation_tests.scenarios.seeker_scenarios',
        'simulation_tests.scenarios.propulsion_scenarios',
        'simulation_tests.scenarios.resource_scenarios',
        'simulation_tests.scenarios.defense_scenarios',
        'simulation_tests.scenarios.modifier_scenarios',
    ]

    for module_name in scenario_modules:
        try:
            importlib.import_module(module_name)
        except Exception as e:
            print(f"WARNING: Failed to import {module_name}: {e}")

    # Collect all concrete scenario classes (those with metadata)
    scenarios = []
    _collect_subclasses(TestScenario, scenarios)
    scenarios.sort(key=lambda pair: pair[0])
    return scenarios


def _collect_subclasses(base_cls, result):
    """Recursively collect concrete scenario classes."""
    for cls in base_cls.__subclasses__():
        if hasattr(cls, 'metadata') and cls.metadata is not None:
            result.append((cls.metadata.test_id, cls))
        _collect_subclasses(cls, result)


def run_scenario(scenario_cls, runner):
    """
    Run a single scenario with isolated registry.

    Returns:
        (test_id, passed, skip_reason, duration, failure_detail)
    """
    from game.core.registry import RegistryManager

    test_id = scenario_cls.metadata.test_id

    # Check skip
    if getattr(scenario_cls, 'skip_test', False):
        reason = getattr(scenario_cls, 'skip_reason', '')
        return test_id, None, reason, 0.0, None

    start = time.time()
    try:
        scenario = runner.run_scenario(scenario_cls, headless=True, log_results=False)
        duration = time.time() - start

        if scenario.passed:
            return test_id, True, None, duration, None

        # Build failure detail from validation report
        report = scenario.results.get('validation', {})
        phase = report.get('failed_phase', '?')
        failed_checks = [c for c in report.get('checks', []) if not c['passed']]
        lines = [f"phase: {phase}"]
        for c in failed_checks:
            lines.append(f"  [{c['phase']}] {c['name']}: expected={c['expected']}, actual={c['actual']}")
            if c.get('detail'):
                lines.append(f"    {c['detail']}")
        if not failed_checks and not report:
            lines = [f"results: {scenario.results}"]
        return test_id, False, None, duration, "\n".join(lines)

    except Exception as e:
        duration = time.time() - start
        return test_id, False, None, duration, f"CRASH: {e}"
    finally:
        RegistryManager.instance().clear()


def format_result(test_id, passed, skip_reason, duration, detail):
    """Format a single test result line."""
    if skip_reason is not None:
        return f"  SKIP  {test_id}  ({skip_reason})"
    elif passed:
        return f"  PASS  {test_id}  ({duration:.2f}s)"
    else:
        return f"  FAIL  {test_id}  ({duration:.2f}s)"


def main():
    parser = argparse.ArgumentParser(description="Combat Lab Test Runner")
    parser.add_argument('filter', nargs='?', default=None,
                        help="Filter tests by ID prefix (e.g., BEAM, PROP-001)")
    parser.add_argument('--list', action='store_true',
                        help="List all tests without running them")
    args = parser.parse_args()

    init_environment()
    scenarios = discover_scenarios()

    # Apply filter
    if args.filter:
        prefix = args.filter.upper()
        scenarios = [(tid, cls) for tid, cls in scenarios if tid.upper().startswith(prefix)]

    if not scenarios:
        print("No tests matched." if args.filter else "No tests found.")
        sys.exit(1)

    # List mode
    if args.list:
        print(f"\n{len(scenarios)} tests:")
        for test_id, cls in scenarios:
            skip = " (SKIP)" if getattr(cls, 'skip_test', False) else ""
            print(f"  {test_id}: {cls.metadata.name}{skip}")
        sys.exit(0)

    # Run tests
    from test_framework.runner import TestRunner
    runner = TestRunner()

    print(f"\nRunning {len(scenarios)} tests...\n")

    results = []
    pass_count = 0
    fail_count = 0
    skip_count = 0

    for test_id, cls in scenarios:
        result = run_scenario(cls, runner)
        results.append(result)
        tid, passed, skip_reason, duration, detail = result

        line = format_result(*result)
        print(line)

        if skip_reason is not None:
            skip_count += 1
        elif passed:
            pass_count += 1
        else:
            fail_count += 1

    # Summary
    total = len(results)
    print(f"\n{'=' * 60}")
    print(f"  {pass_count} passed, {fail_count} failed, {skip_count} skipped  ({total} total)")
    print(f"{'=' * 60}")

    # Print failure details
    failures = [(tid, detail) for tid, passed, _, _, detail in results if passed is False]
    if failures:
        print(f"\nFailures:\n")
        for tid, detail in failures:
            print(f"  {tid}:")
            for line in detail.split('\n'):
                print(f"    {line}")
            print()

    sys.exit(1 if fail_count > 0 else 0)


if __name__ == '__main__':
    main()
