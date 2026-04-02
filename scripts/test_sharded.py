#!/usr/bin/env python3
"""
Sharded test runner: splits the test suite into N independent single-threaded
pytest processes for true parallel execution on multi-core machines.

Usage:
    python test_sharded.py              # auto-detect shards (= CPU count)
    python test_sharded.py --shards 8   # custom shard count
    python test_sharded.py --verbose     # show per-shard test lists

First run uses round-robin distribution. Subsequent runs use timing data
from previous runs (stored in .test_durations.json) to balance shards
by estimated execution time using a greedy least-loaded-bin algorithm.
"""

import argparse
import json
import os
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DURATIONS_FILE = PROJECT_ROOT / ".test_durations.json"
SHARD_RESULTS_DIR = PROJECT_ROOT / ".pytest_cache" / "shard_results"


def _physical_core_count():
    """Return the number of physical CPU cores (not logical/hyperthreaded)."""
    try:
        if sys.platform == "win32":
            result = subprocess.run(
                ["powershell", "-Command",
                 "(Get-CimInstance Win32_Processor).NumberOfCores"],
                capture_output=True, text=True, timeout=10,
            )
            if result.returncode == 0 and result.stdout.strip().isdigit():
                return int(result.stdout.strip())
        else:
            result = subprocess.run(
                ["nproc", "--all"],
                capture_output=True, text=True, timeout=10,
            )
            if result.returncode == 0 and result.stdout.strip().isdigit():
                # nproc returns logical count; /proc/cpuinfo is more reliable
                # but as a fallback, halve os.cpu_count if it looks hyperthreaded
                pass
            # Try reading from /proc/cpuinfo
            cpuinfo = Path("/proc/cpuinfo")
            if cpuinfo.exists():
                cores = set()
                phys_id = core_id = None
                for line in cpuinfo.read_text().splitlines():
                    if line.startswith("physical id"):
                        phys_id = line.split(":")[1].strip()
                    elif line.startswith("core id"):
                        core_id = line.split(":")[1].strip()
                    if phys_id is not None and core_id is not None:
                        cores.add((phys_id, core_id))
                        phys_id = core_id = None
                if cores:
                    return len(cores)
    except (OSError, ValueError, subprocess.TimeoutExpired):
        pass
    # Fallback: assume hyperthreading (2 threads per core)
    logical = os.cpu_count()
    if logical and logical > 1:
        return max(1, logical // 2)
    return 4

# ---------------------------------------------------------------------------
# Test collection
# ---------------------------------------------------------------------------

def collect_test_ids():
    """Run pytest --collect-only to get all test node IDs."""
    print("Collecting tests...", flush=True)
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "--collect-only", "-q",
         "--no-header", "-n", "0"],
        capture_output=True, text=True, cwd=str(PROJECT_ROOT), timeout=60
    )
    ids = [line.strip() for line in result.stdout.splitlines() if "::" in line]
    if not ids:
        print("ERROR: No tests collected!", file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        sys.exit(1)
    return ids


# ---------------------------------------------------------------------------
# Shard assignment
# ---------------------------------------------------------------------------

def load_durations():
    """Load timing data from previous runs, if available."""
    if DURATIONS_FILE.exists():
        try:
            with open(DURATIONS_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {}


def group_by_file(test_ids):
    """Group test IDs by their source file. Tests in the same file stay together."""
    file_groups = {}
    for tid in test_ids:
        file_path = tid.split("::")[0]
        file_groups.setdefault(file_path, []).append(tid)
    return file_groups


def assign_round_robin(test_ids, num_shards):
    """Round-robin distribution by file (first run, no timing data)."""
    file_groups = group_by_file(test_ids)
    # Sort files by test count descending (pack large files first)
    sorted_files = sorted(file_groups.values(), key=len, reverse=True)

    shard_sizes = [0] * num_shards
    shards = [[] for _ in range(num_shards)]

    for file_tests in sorted_files:
        min_idx = min(range(num_shards), key=lambda i: shard_sizes[i])
        shards[min_idx].extend(file_tests)
        shard_sizes[min_idx] += len(file_tests)

    return shards


def assign_by_duration(test_ids, num_shards, durations):
    """Greedy least-loaded-bin assignment by file using stored durations."""
    file_groups = group_by_file(test_ids)

    # Default duration for unknown tests: median of known durations
    known_times = [v for v in durations.values() if v > 0]
    default_duration = sorted(known_times)[len(known_times) // 2] if known_times else 0.01

    # Calculate total duration per file
    file_durations = []
    for file_path, tests in file_groups.items():
        total = sum(durations.get(tid, default_duration) for tid in tests)
        file_durations.append((tests, total))

    # Sort by duration descending (pack heavy files first for better balance)
    file_durations.sort(key=lambda x: -x[1])

    # Greedy: always assign whole file to the least-loaded shard
    shard_times = [0.0] * num_shards
    shards = [[] for _ in range(num_shards)]

    for file_tests, dur in file_durations:
        min_idx = min(range(num_shards), key=lambda i: shard_times[i])
        shards[min_idx].extend(file_tests)
        shard_times[min_idx] += dur

    return shards, shard_times


def assign_shards(test_ids, num_shards):
    """Assign tests to shards by file, using durations if available."""
    durations = load_durations()
    coverage = sum(1 for tid in test_ids if tid in durations)
    coverage_pct = (coverage / len(test_ids) * 100) if test_ids else 0

    file_count = len(group_by_file(test_ids))
    print(f"Grouping {len(test_ids)} tests from {file_count} files into {num_shards} shards (file-level cohesion)")

    if coverage_pct >= 50:
        print(f"Using timing data ({coverage}/{len(test_ids)} tests have durations, {coverage_pct:.0f}% coverage)")
        shards, shard_times = assign_by_duration(test_ids, num_shards, durations)
        min_t, max_t = min(shard_times), max(shard_times)
        print(f"Estimated shard times: {min_t:.1f}s - {max_t:.1f}s (balance ratio: {min_t/max_t:.2f})")
        return shards
    else:
        if durations:
            print(f"Timing data insufficient ({coverage_pct:.0f}% coverage). Using round-robin.")
        else:
            print("No timing data found. Using round-robin (durations will be recorded for next run).")
        return assign_round_robin(test_ids, num_shards)


# ---------------------------------------------------------------------------
# Shard execution
# ---------------------------------------------------------------------------

def run_shard(shard_id, test_ids):
    """Run a single shard as an independent pytest process. Returns (shard_id, returncode, elapsed, stdout, stderr)."""
    xml_path = SHARD_RESULTS_DIR / f"shard_{shard_id}.xml"

    # Write test IDs to a file (avoids Windows command-line length limits)
    id_file = SHARD_RESULTS_DIR / f"shard_{shard_id}_tests.txt"
    id_file.write_text("\n".join(test_ids), encoding="utf-8")

    # Use a small inline script that calls pytest.main() with the test list
    # This bypasses Windows' 32k command-line limit entirely
    # Set SDL_VIDEODRIVER=dummy BEFORE pytest imports conftest to ensure
    # headless Pygame initialization (matches what conftest.py line 3 does)
    runner_script = (
        "import os; os.environ['SDL_VIDEODRIVER']='dummy'; "
        "import sys, pytest; "
        f"test_file = r'{id_file}'; "
        "tests = open(test_file, encoding='utf-8').read().splitlines(); "
        "args = ["
        f"'--junitxml={xml_path}', "
        "'--override-ini=addopts=', "
        "'--tb=short', "
        "'-q', "
        f"'-n', '0'"
        "] + tests; "
        "sys.exit(pytest.main(args))"
    )

    cmd = [sys.executable, "-c", runner_script]

    start = time.perf_counter()
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT),
        timeout=600,
    )
    elapsed = time.perf_counter() - start

    return shard_id, result.returncode, elapsed, result.stdout, result.stderr


# ---------------------------------------------------------------------------
# Result aggregation
# ---------------------------------------------------------------------------

def parse_shard_xml(shard_id):
    """Parse JUnit XML for a shard, returning (tests, failures, errors, time, test_durations)."""
    xml_path = SHARD_RESULTS_DIR / f"shard_{shard_id}.xml"
    if not xml_path.exists():
        return 0, 0, 0, 0.0, {}

    tree = ET.parse(xml_path)
    root = tree.getroot()

    total_tests = 0
    total_failures = 0
    total_errors = 0
    total_time = 0.0
    durations = {}

    for suite in root.iter("testsuite"):
        total_tests += int(suite.get("tests", 0))
        total_failures += int(suite.get("failures", 0))
        total_errors += int(suite.get("errors", 0))
        total_time += float(suite.get("time", 0.0))

    for testcase in root.iter("testcase"):
        classname = testcase.get("classname", "")
        name = testcase.get("name", "")
        dur = float(testcase.get("time", 0.0))
        # Reconstruct the pytest node ID from classname and name
        # classname looks like "tests.unit.ui.test_foo.TestBar" → "tests/unit/ui/test_foo.py::TestBar"
        if classname:
            parts = classname.rsplit(".", 1)
            if len(parts) == 2:
                module_path = parts[0].replace(".", "/") + ".py"
                node_id = f"{module_path}::{parts[1]}::{name}"
            else:
                module_path = classname.replace(".", "/") + ".py"
                node_id = f"{module_path}::{name}"
            durations[node_id] = dur

    return total_tests, total_failures, total_errors, total_time, durations


def collect_failures_and_warnings(stdout_text):
    """Extract FAILURES and warnings sections from pytest output."""
    failures = []
    warnings = []

    lines = stdout_text.splitlines()
    in_failures = False
    in_warnings = False

    for line in lines:
        if "FAILURES" in line and "=" in line:
            in_failures = True
            in_warnings = False
            failures.append(line)
            continue
        if "warnings summary" in line.lower():
            in_failures = False
            in_warnings = True
            warnings.append(line)
            continue
        if line.startswith("=") and ("passed" in line or "failed" in line or "error" in line):
            in_failures = False
            in_warnings = False
            continue
        if in_failures:
            failures.append(line)
        if in_warnings:
            warnings.append(line)

    return failures, warnings


def save_durations(all_durations):
    """Save combined test durations to disk for future runs."""
    # Merge with existing durations (keep old entries for tests not in this run)
    existing = load_durations()
    existing.update(all_durations)
    with open(DURATIONS_FILE, "w") as f:
        json.dump(existing, f, indent=1)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Sharded test runner")
    physical_cores = _physical_core_count()
    parser.add_argument("--shards", type=int, default=physical_cores, help=f"Number of shards (default: {physical_cores}, auto-detected physical cores)")
    parser.add_argument("--verbose", action="store_true", help="Show per-shard test lists")
    args = parser.parse_args()

    num_shards = args.shards

    # Setup
    SHARD_RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # Collect
    test_ids = collect_test_ids()
    print(f"Collected {len(test_ids)} tests, distributing across {num_shards} shards\n")

    # Assign
    shards = assign_shards(test_ids, num_shards)

    # Print shard summary
    for i, shard in enumerate(shards):
        label = f"Shard {i:2d}: {len(shard):4d} tests"
        if args.verbose and shard:
            label += f"  (first: {shard[0][:60]}...)"
        print(label)
    print()

    # Verify no test is lost or duplicated
    all_assigned = []
    for s in shards:
        all_assigned.extend(s)
    assert len(all_assigned) == len(test_ids), f"Test count mismatch: {len(all_assigned)} assigned vs {len(test_ids)} collected"
    assert len(set(all_assigned)) == len(all_assigned), "Duplicate test assignments detected!"

    # Execute shards in parallel
    print(f"{'='*60}")
    print(f"Running {num_shards} shards in parallel (single-threaded each)...")
    print(f"{'='*60}\n")

    overall_start = time.perf_counter()
    shard_results = {}
    all_failures = []
    all_warnings = []

    with ProcessPoolExecutor(max_workers=num_shards) as executor:
        futures = {
            executor.submit(run_shard, i, shards[i]): i
            for i in range(num_shards)
        }

        for future in as_completed(futures):
            shard_id, returncode, elapsed, stdout, stderr = future.result()
            shard_results[shard_id] = (returncode, elapsed, stdout, stderr)

            # Brief progress line
            status = "PASSED" if returncode == 0 else "FAILED"
            test_count = len(shards[shard_id])
            print(f"  Shard {shard_id:2d}: {status:6s} ({test_count:4d} tests in {elapsed:5.1f}s)", flush=True)

    overall_elapsed = time.perf_counter() - overall_start

    # Aggregate results from JUnit XML
    total_tests = 0
    total_failures = 0
    total_errors = 0
    all_durations = {}

    for i in range(num_shards):
        tests, failures, errors, shard_time, durations = parse_shard_xml(i)
        total_tests += tests
        total_failures += failures
        total_errors += errors
        all_durations.update(durations)

    # Collect failures and warnings from stdout
    for i in range(num_shards):
        returncode, elapsed, stdout, stderr = shard_results[i]
        failures, warnings = collect_failures_and_warnings(stdout)
        if failures:
            all_failures.append(f"\n--- Shard {i} FAILURES ---")
            all_failures.extend(failures)
        if warnings:
            all_warnings.extend(warnings)

    # Save durations for next run
    if all_durations:
        save_durations(all_durations)
        print(f"\nSaved timing data for {len(all_durations)} tests to {DURATIONS_FILE.name}")

    # Print shard timing balance report
    print(f"\n{'='*60}")
    print("SHARD TIMING BALANCE")
    print(f"{'='*60}")
    shard_elapsed = []
    for i in range(num_shards):
        _, elapsed, _, _ = shard_results[i]
        shard_elapsed.append(elapsed)
        bar_len = int(elapsed / max(e for _, e, _, _ in shard_results.values()) * 40)
        bar = "#" * bar_len
        print(f"  Shard {i:2d}: {elapsed:5.1f}s  {bar}")

    min_t = min(shard_elapsed)
    max_t = max(shard_elapsed)
    balance_ratio = min_t / max_t if max_t > 0 else 1.0
    print(f"\n  Fastest: {min_t:.1f}s  Slowest: {max_t:.1f}s  Balance: {balance_ratio:.2f}")
    if balance_ratio < 0.7:
        print("  (Balance < 0.70 — next run will use timing data for better distribution)")

    # Print failures
    if all_failures:
        print(f"\n{'='*60}")
        print("FAILURES")
        print(f"{'='*60}")
        print("\n".join(all_failures))

    # Print warnings
    if all_warnings:
        # Deduplicate warnings
        unique_warnings = list(dict.fromkeys(all_warnings))
        print(f"\n{'='*60}")
        print("WARNINGS")
        print(f"{'='*60}")
        print("\n".join(unique_warnings))

    # Final summary
    total_passed = total_tests - total_failures - total_errors
    print(f"\n{'='*60}")
    print(f"TOTAL: {total_tests} tests | {total_passed} passed | {total_failures} failed | {total_errors} errors")
    print(f"Wall time: {overall_elapsed:.1f}s ({num_shards} shards)")
    print(f"{'='*60}")

    # Exit with failure if any shard failed
    if any(rc != 0 for rc, _, _, _ in shard_results.values()):
        sys.exit(1)


if __name__ == "__main__":
    main()
