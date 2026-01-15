"""
Test Log Analyzer - Compare UI vs Headless Test Results

Reads combat_lab_test_log.jsonl and checks for discrepancies between
UI mode and headless mode test executions.

Usage:
    python simulation_tests/utils/test_log_analyzer.py
"""

import json
from pathlib import Path
from typing import Dict, List
from datetime import datetime


def load_test_log(log_file="combat_lab_test_log.jsonl") -> List[Dict]:
    """Load all test log entries from JSONL file."""
    entries = []
    log_path = Path(log_file)
    if log_path.exists():
        with open(log_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line:  # Skip empty lines
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError as e:
                        print(f"Warning: Failed to parse log line: {e}")
    return entries


def compare_test_modes(test_id: str, log_entries: List[Dict]) -> Dict:
    """
    Compare UI vs headless results for a specific test.

    Args:
        test_id: Test ID to compare (e.g., "BEAM-001")
        log_entries: All log entries from the log file

    Returns:
        Dictionary with comparison results
    """
    # Filter entries for this test
    test_entries = [e for e in log_entries if e['test_id'] == test_id]

    ui_runs = [e for e in test_entries if e['mode'] == 'ui']
    headless_runs = [e for e in test_entries if e['mode'] == 'headless']

    if not ui_runs or not headless_runs:
        return {
            'test_id': test_id,
            'status': 'incomplete',
            'message': f"Missing runs (UI: {len(ui_runs)}, Headless: {len(headless_runs)})"
        }

    # Compare most recent runs
    latest_ui = sorted(ui_runs, key=lambda e: e['timestamp'])[-1]
    latest_headless = sorted(headless_runs, key=lambda e: e['timestamp'])[-1]

    discrepancies = []

    # Check pass/fail match
    if latest_ui['passed'] != latest_headless['passed']:
        discrepancies.append(
            f"Pass/Fail mismatch: UI={'PASS' if latest_ui['passed'] else 'FAIL'}, "
            f"Headless={'PASS' if latest_headless['passed'] else 'FAIL'}"
        )

    # Check damage dealt (within tolerance)
    ui_dmg = latest_ui.get('damage_dealt', 0)
    headless_dmg = latest_headless.get('damage_dealt', 0)
    if abs(ui_dmg - headless_dmg) > 1.0:  # Allow 1 damage difference
        discrepancies.append(
            f"Damage mismatch: UI={ui_dmg}, Headless={headless_dmg}"
        )

    # Check tick count (within tolerance)
    ui_ticks = latest_ui.get('ticks_run', 0)
    headless_ticks = latest_headless.get('ticks_run', 0)
    if abs(ui_ticks - headless_ticks) > 1:  # Allow 1 tick difference
        discrepancies.append(
            f"Tick count mismatch: UI={ui_ticks}, Headless={headless_ticks}"
        )

    if discrepancies:
        return {
            'test_id': test_id,
            'status': 'mismatch',
            'discrepancies': discrepancies,
            'ui_run': latest_ui,
            'headless_run': latest_headless
        }
    else:
        return {
            'test_id': test_id,
            'status': 'match',
            'message': 'UI and headless results match within tolerance'
        }


def generate_comparison_report(log_file="combat_lab_test_log.jsonl"):
    """Generate full comparison report for all tests."""
    entries = load_test_log(log_file)

    if not entries:
        print(f"\nNo test log entries found in {log_file}")
        print("Run some tests to generate log data.\n")
        return

    # Get unique test IDs
    test_ids = sorted(set(e['test_id'] for e in entries))

    print(f"\n{'='*70}")
    print(f"Combat Lab Test Log Comparison Report")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}\n")
    print(f"Total Tests: {len(test_ids)}")
    print(f"Total Log Entries: {len(entries)}\n")

    matches = 0
    mismatches = 0
    incomplete = 0

    for test_id in test_ids:
        result = compare_test_modes(test_id, entries)

        if result['status'] == 'match':
            matches += 1
            print(f"✓ {test_id}: Results match")
        elif result['status'] == 'mismatch':
            mismatches += 1
            print(f"✗ {test_id}: MISMATCH DETECTED")
            for disc in result['discrepancies']:
                print(f"    - {disc}")
        else:
            incomplete += 1
            print(f"? {test_id}: {result['message']}")

    print(f"\n{'='*70}")
    print(f"Summary:")
    print(f"  Matching: {matches}")
    print(f"  Mismatches: {mismatches}")
    print(f"  Incomplete: {incomplete}")
    print(f"{'='*70}\n")

    if mismatches > 0:
        print("⚠ WARNING: Discrepancies detected between UI and headless modes!")
        print("Review the mismatched tests above to investigate.\n")
    elif matches > 0:
        print("✓ All tested scenarios match between UI and headless modes.\n")


def show_test_history(test_id: str, log_file="combat_lab_test_log.jsonl"):
    """Show execution history for a specific test."""
    entries = load_test_log(log_file)
    test_entries = [e for e in entries if e['test_id'] == test_id]

    if not test_entries:
        print(f"\nNo log entries found for test {test_id}\n")
        return

    test_entries = sorted(test_entries, key=lambda e: e['timestamp'])

    print(f"\n{'='*70}")
    print(f"Test Execution History: {test_id}")
    print(f"{'='*70}\n")

    for i, entry in enumerate(test_entries, 1):
        timestamp = datetime.fromisoformat(entry['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
        mode = entry['mode'].upper()
        result = 'PASS' if entry['passed'] else 'FAIL'
        ticks = entry.get('ticks_run', 0)
        damage = entry.get('damage_dealt', 0)

        print(f"{i}. {timestamp} | {mode:8s} | {result:4s} | {ticks:4d} ticks | {damage:6.1f} dmg")

    print(f"\n{'='*70}\n")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        # Show history for specific test
        test_id = sys.argv[1]
        show_test_history(test_id)
    else:
        # Generate full comparison report
        generate_comparison_report()
