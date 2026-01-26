"""Quick script to test TOST implementation on BEAM360-001 and BEAM360-001-HT."""
import sys
import time
from simulation_tests.scenarios.beam_scenarios import (
    BeamLowAccuracyPointBlankScenario,
    BeamLowAccuracyPointBlankHighTickScenario
)
from game.simulation.systems.battle_engine import BattleEngine
from test_framework.runner import TestRunner

def run_headless_test(scenario):
    """Run test scenario headlessly and return results."""
    print(f"\nRunning {scenario.metadata.test_id}...")
    print(f"Name: {scenario.metadata.name}")
    print(f"Summary: {scenario.metadata.summary}")
    print(f"Max ticks: {scenario.max_ticks}")

    # Load data for scenario (critical step!)
    runner = TestRunner()
    runner.load_data_for_scenario(scenario)

    # Setup engine
    engine = BattleEngine()
    engine.start([], [])
    scenario.setup(engine)

    # Run simulation
    start_time = time.time()
    tick_count = 0
    max_ticks = scenario.max_ticks

    while tick_count < max_ticks:
        scenario.update(engine)
        engine.update()
        tick_count += 1

        if engine.is_battle_over():
            print(f"Battle ended early at tick {tick_count}")
            break

    elapsed_time = time.time() - start_time

    # Verify and get results
    scenario.results['ticks_run'] = tick_count
    scenario.passed = scenario.verify(engine)

    print(f"\nTest completed in {elapsed_time:.2f}s ({tick_count} ticks)")
    print(f"Tick rate: {tick_count / elapsed_time:.0f} ticks/sec")
    print(f"\nTest Result: {'PASSED' if scenario.passed else 'FAILED'}")

    # Print metrics
    print("\n=== Metrics ===")
    for key, value in scenario.results.items():
        if key != 'validation_results':
            print(f"  {key}: {value}")

    # Print validation results
    print("\n=== Validation Results ===")
    if 'validation_results' in scenario.results:
        for result in scenario.results['validation_results']:
            status_symbol = "[PASS]" if result['status'] == 'PASS' else "[FAIL]"
            print(f"\n{status_symbol} {result['name']}")
            # Print simplified message without symbols
            message = result['message'].replace('✓', '[PASS]').replace('✗', '[FAIL]')
            print(f"  {message}")
            if result['p_value'] is not None:
                print(f"  P-value: {result['p_value']:.4f}")
                print(f"  Threshold: {result['tolerance']}")

    return scenario.passed

if __name__ == "__main__":
    print("=" * 80)
    print("TOST EQUIVALENCE TESTING - VALIDATION")
    print("=" * 80)

    # Test 1: Regular 500-tick test with ±6% margin
    print("\n\n### TEST 1: BEAM360-001 (500 ticks, ±6% margin) ###")
    scenario_500 = BeamLowAccuracyPointBlankScenario()
    test_500_passed = run_headless_test(scenario_500)

    # Test 2: High-tick 100k test with ±1% margin
    print("\n\n### TEST 2: BEAM360-001-HT (100,000 ticks, ±1% margin) ###")
    scenario_100k = BeamLowAccuracyPointBlankHighTickScenario()
    test_100k_passed = run_headless_test(scenario_100k)

    # Summary
    print("\n\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"BEAM360-001 (500 ticks):    {'PASSED' if test_500_passed else 'FAILED'}")
    print(f"BEAM360-001-HT (100k ticks): {'PASSED' if test_100k_passed else 'FAILED'}")

    sys.exit(0 if (test_500_passed and test_100k_passed) else 1)
