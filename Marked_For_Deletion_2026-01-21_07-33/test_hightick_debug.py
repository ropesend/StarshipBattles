"""Debug script to investigate high-tick test discrepancy."""
import sys
import time
from simulation_tests.scenarios.beam_scenarios import BeamLowAccuracyPointBlankHighTickScenario
from game.simulation.systems.battle_engine import BattleEngine
from test_framework.runner import TestRunner

def run_test():
    """Run high-tick test with debug logging."""
    scenario = BeamLowAccuracyPointBlankHighTickScenario()

    print("\n" + "="*80)
    print("HIGH-TICK TEST DEBUG RUN")
    print("="*80)
    print(f"Test: {scenario.metadata.test_id}")
    print(f"Expected hit rate: {scenario.metadata.validation_rules[5].expected_probability:.4f} (55.36%)")
    print(f"Equivalence margin: ±{scenario.metadata.validation_rules[5].equivalence_margin:.2%}")

    # Load data
    runner = TestRunner()
    runner.load_data_for_scenario(scenario)

    # Setup engine
    engine = BattleEngine()
    engine.start([], [])
    scenario.setup(engine)

    print(f"\nShip Configuration:")
    print(f"  Attacker: {scenario.attacker.name}")
    print(f"    - Mass: {scenario.attacker.mass}")
    print(f"    - Sensor score: {scenario.attacker.get_total_sensor_score()}")
    print(f"  Target: {scenario.target.name}")
    print(f"    - Mass: {scenario.target.mass}")
    print(f"    - Defense score: {scenario.target.total_defense_score}")
    print(f"    - HP: {scenario.target.hp}/{scenario.target.max_hp}")

    print(f"\nTest expectation calculation:")
    print(f"  Expected defense for mass={scenario.target.mass}: {scenario.expected_hit_chance:.4f}")

    # Run just 1000 ticks for quick debug
    print(f"\nRunning 1000 ticks for quick validation...")
    print("(Watch for DEBUG HIT CALC output on first hit)\n")

    start_time = time.time()
    tick_count = 0
    max_ticks = 1000

    while tick_count < max_ticks:
        scenario.update(engine)
        engine.update()
        tick_count += 1
        if engine.is_battle_over():
            break

    elapsed_time = time.time() - start_time

    # Quick results
    damage_dealt = scenario.initial_hp - scenario.target.hp
    hit_rate = damage_dealt / tick_count

    print(f"\nQuick Test Results ({tick_count} ticks):")
    print(f"  Damage dealt: {damage_dealt}")
    print(f"  Observed hit rate: {hit_rate:.4f} ({hit_rate*100:.2f}%)")
    print(f"  Expected hit rate: {scenario.expected_hit_chance:.4f} ({scenario.expected_hit_chance*100:.2f}%)")
    print(f"  Deviation: {(hit_rate - scenario.expected_hit_chance)*100:+.2f}%")
    print(f"  Tick rate: {tick_count / elapsed_time:.0f} ticks/sec")

if __name__ == "__main__":
    run_test()
