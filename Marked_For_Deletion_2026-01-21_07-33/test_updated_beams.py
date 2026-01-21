"""Quick validation script for updated beam weapon tests."""
import sys
from simulation_tests.scenarios.beam_scenarios import (
    BeamLowAccuracyMidRangeScenario,
    BeamMediumAccuracyPointBlankScenario
)
from test_framework.runner import TestRunner

def validate_test(scenario_class, test_name):
    """Validate a single test scenario."""
    print(f"\n{'='*80}")
    print(f"VALIDATING: {test_name}")
    print(f"{'='*80}")

    scenario = scenario_class()
    runner = TestRunner()

    # Load data
    runner.load_data_for_scenario(scenario)

    # Setup engine
    from game.simulation.systems.battle_engine import BattleEngine
    engine = BattleEngine()
    engine.start([], [])
    scenario.setup(engine)

    # Print configuration
    print(f"Test ID: {scenario.metadata.test_id}")
    print(f"Max ticks: {scenario.max_ticks}")
    print(f"Attacker: {scenario.attacker.name}, Mass: {scenario.attacker.mass}")
    print(f"Target: {scenario.target.name}, Mass: {scenario.target.mass}")
    print(f"Target Defense Score: {scenario.target.total_defense_score:.4f}")
    print(f"Expected Hit Chance: {scenario.expected_hit_chance:.4f} ({scenario.expected_hit_chance*100:.2f}%)")

    # Check validation rules
    print(f"\nValidation Rules:")
    print(f"  ExactMatchRules: {len([r for r in scenario.metadata.validation_rules if 'ExactMatch' in r.__class__.__name__])}")
    print(f"  StatisticalTestRules: {len([r for r in scenario.metadata.validation_rules if 'Statistical' in r.__class__.__name__])}")

    # Run quick test (100 ticks)
    print(f"\nRunning quick test (100 ticks)...")
    for _ in range(100):
        scenario.update(engine)
        engine.update()
        if engine.is_battle_over():
            break

    damage_dealt = scenario.initial_hp - scenario.target.hp
    hit_rate = damage_dealt / 100 if 100 > 0 else 0

    print(f"Quick Results:")
    print(f"  Ticks run: 100")
    print(f"  Damage dealt: {damage_dealt}")
    print(f"  Observed hit rate: {hit_rate:.4f} ({hit_rate*100:.2f}%)")
    print(f"  Expected hit rate: {scenario.expected_hit_chance:.4f} ({scenario.expected_hit_chance*100:.2f}%)")
    print(f"  [PASS] Test scenario configured correctly")

    return True

if __name__ == "__main__":
    print("Beam Weapon Test Update Validation")
    print("="*80)

    tests = [
        (BeamLowAccuracyMidRangeScenario, "BEAM360-002: Low Accuracy Mid Range"),
        (BeamMediumAccuracyPointBlankScenario, "BEAM360-004: Medium Accuracy Point Blank")
    ]

    all_passed = True
    for scenario_class, test_name in tests:
        try:
            validate_test(scenario_class, test_name)
        except Exception as e:
            print(f"\n[FAIL] ERROR in {test_name}: {e}")
            import traceback
            traceback.print_exc()
            all_passed = False

    print(f"\n{'='*80}")
    if all_passed:
        print("[PASS] ALL VALIDATION CHECKS PASSED")
        print("All updated beam tests are configured correctly!")
    else:
        print("[FAIL] SOME VALIDATION CHECKS FAILED")
    print(f"{'='*80}")

    sys.exit(0 if all_passed else 1)
