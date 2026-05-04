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
import statistics
import subprocess
import sys
import time
import uuid
import xml.etree.ElementTree as ET
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

def _find_project_root():
    """Find project root by looking for game/ and data/ directories."""
    current = Path(__file__).resolve().parent
    for _ in range(10):
        if (current / "game").is_dir() and (current / "data").is_dir():
            return current
        current = current.parent
    raise RuntimeError("Could not find project root")


PROJECT_ROOT = _find_project_root()
DURATIONS_FILE = PROJECT_ROOT / ".test_durations.json"
FILE_DURATION_HISTORY_FILE = PROJECT_ROOT / ".test_file_duration_history.json"
SHARD_RESULTS_DIR = PROJECT_ROOT / ".pytest_cache" / "shard_results"
TEST_BASELINE_FILE = PROJECT_ROOT / "AgentCoordination" / "generated" / "test_baseline.json"
TEST_BASELINE_BY_INSTALL_DIR = PROJECT_ROOT / "AgentCoordination" / "generated" / "test_baseline" / "by_install"
LOCAL_INSTALL_ID_FILE = PROJECT_ROOT / "AgentCoordination" / "local" / "install_id.json"
BASELINE_COMMAND = "python Tools/test_sharded/test_sharded.py"
BASELINE_COUNT_KEYS = ("total", "passed", "failed", "errors", "skipped")
TEST_BASELINE_SCHEMA_VERSION = 2
TEST_BASELINE_VERIFICATION_SCHEMA_VERSION = 1
FILE_DURATION_HISTORY_SCHEMA_VERSION = 1
MAX_FILE_HISTORY_SAMPLES = 30


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


def _test_file_path(test_id: str) -> str:
    return test_id.split("::", 1)[0]


def _mean_known_duration(durations: dict[str, float]) -> float:
    known_times = [float(v) for v in durations.values() if isinstance(v, (int, float)) and v > 0]
    if not known_times:
        return 0.01
    return sum(known_times) / len(known_times)


def group_by_file(test_ids):
    """Group test IDs by their source file. Tests in the same file stay together."""
    file_groups = {}
    for tid in test_ids:
        file_path = _test_file_path(tid)
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


def assign_by_duration(test_ids, num_shards, durations, file_history=None):
    """Greedy least-loaded-bin assignment by file using stored durations."""
    file_groups = group_by_file(test_ids)

    # Calculate total duration per file
    file_durations = []
    for file_path, tests in file_groups.items():
        total = _estimate_file_duration(file_path, tests, durations, file_history or {})
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


def assign_shards(test_ids, num_shards, durations=None, file_history=None):
    """Assign tests to shards by file, using durations if available."""
    durations = load_durations() if durations is None else durations
    file_history = _load_file_duration_history() if file_history is None else file_history
    coverage = sum(1 for tid in test_ids if tid in durations)
    coverage_pct = (coverage / len(test_ids) * 100) if test_ids else 0

    file_groups = group_by_file(test_ids)
    file_count = len(file_groups)
    print(f"Grouping {len(test_ids)} tests from {file_count} files into {num_shards} shards (file-level cohesion)")

    if coverage_pct >= 50:
        print(f"Using timing data ({coverage}/{len(test_ids)} tests have durations, {coverage_pct:.0f}% coverage)")
        history_files = _file_history_match_count(file_groups, file_history)
        if history_files:
            print(f"Using file history for {history_files}/{file_count} files; per-test durations fill gaps")
        shards, shard_times = assign_by_duration(test_ids, num_shards, durations, file_history)
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
    duration_path = SHARD_RESULTS_DIR / f"shard_{shard_id}_durations.json"

    # Write test IDs to a file (avoids Windows command-line length limits)
    id_file = SHARD_RESULTS_DIR / f"shard_{shard_id}_tests.txt"
    id_file.write_text("\n".join(test_ids), encoding="utf-8")

    # Use a small inline script that calls pytest.main() with the test list
    # This bypasses Windows' 32k command-line limit entirely
    # Set SDL_VIDEODRIVER=dummy BEFORE pytest imports conftest to ensure
    # headless Pygame initialization (matches what conftest.py line 3 does)
    id_file_arg = json.dumps(id_file.as_posix())
    xml_arg = json.dumps(f"--junitxml={xml_path.as_posix()}")
    duration_path_arg = json.dumps(duration_path.as_posix())
    runner_script = f"""
import json
import os
from pathlib import Path
import sys

os.environ["SDL_VIDEODRIVER"] = "dummy"
import pytest

test_file = Path({id_file_arg})
duration_file = Path({duration_path_arg})
tests = test_file.read_text(encoding="utf-8").splitlines()
args = [
    {xml_arg},
    "--override-ini=addopts=",
    "--tb=short",
    "-q",
    "-n",
    "0",
] + tests


class _TimingPlugin:
    def __init__(self):
        self.durations = {{}}

    def pytest_runtest_logreport(self, report):
        duration = float(getattr(report, "duration", 0.0) or 0.0)
        self.durations[report.nodeid] = self.durations.get(report.nodeid, 0.0) + duration

    def pytest_sessionfinish(self, session, exitstatus):
        duration_file.write_text(
            json.dumps(self.durations, indent=1, sort_keys=True),
            encoding="utf-8",
        )


sys.exit(pytest.main(args, plugins=[_TimingPlugin()]))
"""

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

def _load_shard_duration_sidecar(shard_id: int) -> dict[str, float]:
    duration_path = SHARD_RESULTS_DIR / f"shard_{shard_id}_durations.json"
    if not duration_path.exists():
        return {}
    try:
        raw = json.loads(duration_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    if not isinstance(raw, dict):
        return {}

    durations: dict[str, float] = {}
    for node_id, duration in raw.items():
        if not isinstance(node_id, str):
            continue
        try:
            durations[node_id] = float(duration)
        except (TypeError, ValueError):
            continue
    return durations


def parse_shard_xml(shard_id: int) -> tuple[int, int, int, int, float, dict[str, float]]:
    """Parse JUnit XML for a shard."""
    xml_path = SHARD_RESULTS_DIR / f"shard_{shard_id}.xml"
    if not xml_path.exists():
        return 0, 0, 0, 0, 0.0, {}

    tree = ET.parse(xml_path)
    root = tree.getroot()

    total_tests = 0
    total_failures = 0
    total_errors = 0
    total_skipped = 0
    total_time = 0.0
    durations = {}

    for suite in root.iter("testsuite"):
        total_tests += int(suite.get("tests", 0))
        total_failures += int(suite.get("failures", 0))
        total_errors += int(suite.get("errors", 0))
        total_skipped += int(suite.get("skipped", 0))
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

    exact_durations = _load_shard_duration_sidecar(shard_id)
    if exact_durations:
        durations = exact_durations

    return total_tests, total_failures, total_errors, total_skipped, total_time, durations


def _load_file_duration_history() -> dict[str, object]:
    if not FILE_DURATION_HISTORY_FILE.exists():
        return {"schema_version": FILE_DURATION_HISTORY_SCHEMA_VERSION, "files": {}}
    try:
        data = json.loads(FILE_DURATION_HISTORY_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"schema_version": FILE_DURATION_HISTORY_SCHEMA_VERSION, "files": {}}
    if not isinstance(data, dict) or not isinstance(data.get("files"), dict):
        return {"schema_version": FILE_DURATION_HISTORY_SCHEMA_VERSION, "files": {}}
    data["schema_version"] = FILE_DURATION_HISTORY_SCHEMA_VERSION
    return data


def _save_file_duration_history(history: dict[str, object]) -> None:
    FILE_DURATION_HISTORY_FILE.write_text(
        json.dumps(history, indent=1, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _file_duration_totals(test_ids: list[str], durations: dict[str, float]) -> dict[str, float]:
    totals: dict[str, float] = {}
    for test_id in test_ids:
        if test_id not in durations:
            continue
        file_path = _test_file_path(test_id)
        totals[file_path] = totals.get(file_path, 0.0) + float(durations[test_id])
    return totals


def _file_test_counts(shards: list[list[str]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for shard in shards:
        for test_id in shard:
            file_path = _test_file_path(test_id)
            counts[file_path] = counts.get(file_path, 0) + 1
    return counts


def _file_shard_map(shards: list[list[str]]) -> dict[str, int | list[int]]:
    shard_map: dict[str, set[int]] = {}
    for shard_id, shard in enumerate(shards):
        for test_id in shard:
            shard_map.setdefault(_test_file_path(test_id), set()).add(shard_id)
    return {
        file_path: next(iter(shard_ids)) if len(shard_ids) == 1 else sorted(shard_ids)
        for file_path, shard_ids in shard_map.items()
    }


def _record_file_duration_history(
    history: dict[str, object],
    shards: list[list[str]],
    durations: dict[str, float],
    shard_count: int,
    recorded_at: str,
) -> dict[str, object]:
    files = history.setdefault("files", {})
    if not isinstance(files, dict):
        files = {}
        history["files"] = files

    all_tests = [test_id for shard in shards for test_id in shard]
    totals = _file_duration_totals(all_tests, durations)
    counts = _file_test_counts(shards)
    shard_map = _file_shard_map(shards)

    for file_path, duration in totals.items():
        samples = files.setdefault(file_path, [])
        if not isinstance(samples, list):
            samples = []
            files[file_path] = samples
        samples.append(
            {
                "duration": round(duration, 6),
                "test_count": counts.get(file_path, 0),
                "shards": shard_count,
                "shard": shard_map.get(file_path, -1),
                "recorded_at": recorded_at,
            }
        )
        del samples[:-MAX_FILE_HISTORY_SAMPLES]

    history["schema_version"] = FILE_DURATION_HISTORY_SCHEMA_VERSION
    return history


def _file_variability_pct(file_path: str, history: dict[str, object]) -> float | None:
    files = history.get("files")
    if not isinstance(files, dict):
        return None
    samples = files.get(file_path)
    if not isinstance(samples, list):
        return None
    values: list[float] = []
    for sample in samples:
        if not isinstance(sample, dict):
            continue
        try:
            duration = float(sample.get("duration", 0.0))
        except (TypeError, ValueError):
            continue
        if duration > 0:
            values.append(duration)
    if len(values) < 2:
        return None
    mean = sum(values) / len(values)
    if mean <= 0:
        return None
    return statistics.stdev(values) / mean * 100.0


def _history_sample_count(file_path: str, history: dict[str, object]) -> int:
    files = history.get("files")
    if not isinstance(files, dict):
        return 0
    samples = files.get(file_path)
    if not isinstance(samples, list):
        return 0
    return sum(1 for sample in samples if isinstance(sample, dict) and "duration" in sample)


def _matching_file_history_values(
    file_path: str,
    test_count: int,
    history: dict[str, object],
) -> list[float]:
    files = history.get("files")
    if not isinstance(files, dict):
        return []
    samples = files.get(file_path)
    if not isinstance(samples, list):
        return []

    values: list[float] = []
    for sample in samples:
        if not isinstance(sample, dict) or sample.get("test_count") != test_count:
            continue
        try:
            duration = float(sample.get("duration", 0.0))
        except (TypeError, ValueError):
            continue
        if duration > 0:
            values.append(duration)
    return values


def _file_history_match_count(
    file_groups: dict[str, list[str]],
    history: dict[str, object],
) -> int:
    return sum(
        1
        for file_path, tests in file_groups.items()
        if _matching_file_history_values(file_path, len(tests), history)
    )


def _estimate_file_duration(
    file_path: str,
    tests: list[str],
    durations: dict[str, float],
    file_history: dict[str, object],
) -> float:
    history_values = _matching_file_history_values(file_path, len(tests), file_history)
    if history_values:
        return float(statistics.median(history_values))

    default_duration = _mean_known_duration(durations)
    return sum(float(durations.get(test_id, default_duration)) for test_id in tests)


def _estimate_shard_duration(
    test_ids: list[str],
    durations: dict[str, float],
    file_history: dict[str, object],
) -> float:
    return sum(
        _estimate_file_duration(file_path, tests, durations, file_history)
        for file_path, tests in group_by_file(test_ids).items()
    )


def _file_estimate_errors(
    shards: list[list[str]],
    actual_durations: dict[str, float],
    historical_durations: dict[str, float],
    file_history: dict[str, object],
) -> list[dict[str, object]]:
    errors: list[dict[str, object]] = []
    for shard_id, test_ids in enumerate(shards):
        for file_path, tests in group_by_file(test_ids).items():
            actual_time = sum(float(actual_durations.get(test_id, 0.0)) for test_id in tests)
            estimated_time = _estimate_file_duration(file_path, tests, historical_durations, file_history)
            error = actual_time - estimated_time
            errors.append(
                {
                    "shard_id": shard_id,
                    "file_path": file_path,
                    "actual_time": actual_time,
                    "estimated_time": estimated_time,
                    "error": error,
                    "abs_error": abs(error),
                    "test_count": len(tests),
                }
            )
    errors.sort(key=lambda item: float(item["abs_error"]), reverse=True)
    return errors


def _build_shard_diagnostics(
    shards: list[list[str]],
    actual_durations: dict[str, float],
    historical_durations: dict[str, float],
    shard_elapsed: list[float],
    file_history: dict[str, object],
    estimate_file_history: dict[str, object] | None = None,
) -> list[dict[str, object]]:
    estimate_history = file_history if estimate_file_history is None else estimate_file_history
    diagnostics: list[dict[str, object]] = []
    for shard_id, test_ids in enumerate(shards):
        file_groups = group_by_file(test_ids)
        file_totals = _file_duration_totals(test_ids, actual_durations)
        file_times = list(file_totals.values())
        known_count = sum(1 for test_id in test_ids if test_id in historical_durations)
        variabilities = [
            variability
            for file_path in file_groups
            if (variability := _file_variability_pct(file_path, file_history)) is not None
        ]
        diagnostics.append(
            {
                "shard_id": shard_id,
                "wall_time": shard_elapsed[shard_id] if shard_id < len(shard_elapsed) else 0.0,
                "case_time": sum(float(actual_durations.get(test_id, 0.0)) for test_id in test_ids),
                "estimated_time": _estimate_shard_duration(test_ids, historical_durations, estimate_history),
                "test_count": len(test_ids),
                "file_count": len(file_groups),
                "known_pct": (known_count / len(test_ids) * 100.0) if test_ids else 0.0,
                "file_min": min(file_times) if file_times else 0.0,
                "file_median": statistics.median(file_times) if file_times else 0.0,
                "file_max": max(file_times) if file_times else 0.0,
                "variability_median_pct": statistics.median(variabilities) if variabilities else None,
                "variability_max_pct": max(variabilities) if variabilities else None,
            }
        )
    return diagnostics


def _format_seconds(value: object) -> str:
    try:
        return f"{float(value):5.1f}s"
    except (TypeError, ValueError):
        return "  n/a"


def _format_optional_pct(value: object) -> str:
    if value is None:
        return " n/a"
    try:
        return f"{float(value):4.0f}%"
    except (TypeError, ValueError):
        return " n/a"


def _print_shard_timing_balance(
    shard_results: dict[int, tuple[int, float, str, str]],
    shards: list[list[str]],
    actual_durations: dict[str, float],
    historical_durations: dict[str, float],
    file_history: dict[str, object],
    estimate_file_history: dict[str, object] | None = None,
) -> list[float]:
    print(f"\n{'='*60}")
    print("SHARD TIMING BALANCE")
    print(f"{'='*60}")
    shard_elapsed = [shard_results[i][1] for i in range(len(shards))]
    diagnostics = _build_shard_diagnostics(
        shards,
        actual_durations,
        historical_durations,
        shard_elapsed,
        file_history,
        estimate_file_history,
    )
    max_elapsed = max(shard_elapsed) if shard_elapsed else 0.0
    print("  id    wall    est   case    err tests files known file min/med/max  var med/max")
    for item in diagnostics:
        elapsed = float(item["wall_time"])
        case_time = float(item["case_time"])
        estimated_time = float(item["estimated_time"])
        err = case_time - estimated_time
        bar_len = int(elapsed / max_elapsed * 30) if max_elapsed > 0 else 0
        bar = "#" * bar_len
        file_range = (
            f"{float(item['file_min']):.1f}/"
            f"{float(item['file_median']):.1f}/"
            f"{float(item['file_max']):.1f}s"
        )
        var_range = (
            f"{_format_optional_pct(item['variability_median_pct']).strip()}/"
            f"{_format_optional_pct(item['variability_max_pct']).strip()}"
        )
        print(
            f"  {int(item['shard_id']):2d} "
            f"{_format_seconds(elapsed)} "
            f"{_format_seconds(estimated_time)} "
            f"{_format_seconds(case_time)} "
            f"{err:+6.1f}s "
            f"{int(item['test_count']):5d} "
            f"{int(item['file_count']):5d} "
            f"{float(item['known_pct']):5.0f}% "
            f"{file_range:>16s} "
            f"{var_range:>11s}  {bar}"
        )

    min_t = min(shard_elapsed) if shard_elapsed else 0.0
    max_t = max(shard_elapsed) if shard_elapsed else 0.0
    balance_ratio = min_t / max_t if max_t > 0 else 1.0
    print(f"\n  Fastest: {min_t:.1f}s  Slowest: {max_t:.1f}s  Balance: {balance_ratio:.2f}")
    if balance_ratio < 0.7:
        print("  (Balance < 0.70 - next run will use timing data for better distribution)")
    return shard_elapsed


def _print_file_timing_diagnostics(
    shards: list[list[str]],
    actual_durations: dict[str, float],
    historical_durations: dict[str, float],
    file_history: dict[str, object],
    estimate_file_history: dict[str, object] | None = None,
) -> None:
    all_tests = [test_id for shard in shards for test_id in shard]
    file_totals = _file_duration_totals(all_tests, actual_durations)
    if not file_totals:
        return
    counts = _file_test_counts(shards)
    shard_map = _file_shard_map(shards)

    print(f"\n{'='*60}")
    print("FILE TIMING DIAGNOSTICS")
    print(f"{'='*60}")
    print("Slowest files this run:")
    for file_path, duration in sorted(file_totals.items(), key=lambda item: -item[1])[:10]:
        variability = _file_variability_pct(file_path, file_history)
        sample_count = _history_sample_count(file_path, file_history)
        print(
            f"  {_format_seconds(duration)}  "
            f"tests={counts.get(file_path, 0):4d}  "
            f"shard={shard_map.get(file_path, '?')}  "
            f"var={_format_optional_pct(variability).strip()} "
            f"n={sample_count:2d}  {file_path}"
        )

    estimate_history = file_history if estimate_file_history is None else estimate_file_history
    estimate_errors = _file_estimate_errors(
        shards,
        actual_durations,
        historical_durations,
        estimate_history,
    )
    if estimate_errors:
        print("\nLargest file estimate errors:")
        for item in estimate_errors[:10]:
            print(
                f"  err={float(item['error']):+5.1f}s  "
                f"actual={_format_seconds(item['actual_time'])}  "
                f"est={_format_seconds(item['estimated_time'])}  "
                f"tests={int(item['test_count']):4d}  "
                f"shard={int(item['shard_id']):2d}  {item['file_path']}"
            )

    variable_files = [
        (variability, file_path)
        for file_path in file_totals
        if (variability := _file_variability_pct(file_path, file_history)) is not None
    ]
    if not variable_files:
        print("\nMost variable files: need at least two runs of history.")
        return

    print("\nMost variable files in this run's assignment:")
    for variability, file_path in sorted(variable_files, reverse=True)[:10]:
        sample_count = _history_sample_count(file_path, file_history)
        print(
            f"  var={variability:5.0f}%  "
            f"last={_format_seconds(file_totals[file_path])}  "
            f"tests={counts.get(file_path, 0):4d}  "
            f"n={sample_count:2d}  {file_path}"
        )


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


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _git_sha() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return ""
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def _load_test_baseline() -> dict[str, object] | None:
    if not TEST_BASELINE_FILE.exists():
        return None
    try:
        data = json.loads(TEST_BASELINE_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    if not isinstance(data, dict):
        return None
    return data


def _baseline_counts_changed(
    existing: dict[str, object] | None,
    counts: dict[str, int],
) -> bool:
    if existing is None:
        return True
    return any(existing.get(key) != counts[key] for key in BASELINE_COUNT_KEYS)


def _write_test_baseline(payload: dict[str, object]) -> None:
    TEST_BASELINE_FILE.parent.mkdir(parents=True, exist_ok=True)
    TEST_BASELINE_FILE.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _ensure_install_id() -> str:
    if LOCAL_INSTALL_ID_FILE.exists():
        try:
            data = json.loads(LOCAL_INSTALL_ID_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            data = {}
        if isinstance(data, dict):
            install_id = data.get("install_id")
            if isinstance(install_id, str) and install_id:
                return install_id

    install_id = uuid.uuid4().hex
    LOCAL_INSTALL_ID_FILE.parent.mkdir(parents=True, exist_ok=True)
    LOCAL_INSTALL_ID_FILE.write_text(
        json.dumps({"install_id": install_id, "created_at": _utc_timestamp()}, indent=2) + "\n",
        encoding="utf-8",
    )
    return install_id


def _write_test_baseline_verification(
    counts: dict[str, int],
    *,
    verified_at: str,
    git_sha: str,
) -> Path:
    install_id = _ensure_install_id()
    TEST_BASELINE_BY_INSTALL_DIR.mkdir(parents=True, exist_ok=True)
    file_path = TEST_BASELINE_BY_INSTALL_DIR / f"{install_id}.json"
    payload: dict[str, object] = {
        "schema_version": TEST_BASELINE_VERIFICATION_SCHEMA_VERSION,
        "install_id": install_id,
        "command": BASELINE_COMMAND,
        **counts,
        "verified_at": verified_at,
        "git_sha": git_sha,
    }
    file_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return file_path


def _canonical_baseline_needs_rewrite(
    existing: dict[str, object] | None,
    counts_changed: bool,
) -> bool:
    if existing is None or counts_changed:
        return True
    if existing.get("schema_version") != TEST_BASELINE_SCHEMA_VERSION:
        return True
    return "verified_at" in existing or "git_sha" in existing


def _write_test_baseline_if_needed(
    summary: dict[str, int],
    *,
    full_suite_success: bool,
    refresh_baseline_timestamp: bool,
) -> str:
    if not full_suite_success:
        return "skipped"

    counts = {key: int(summary[key]) for key in BASELINE_COUNT_KEYS}
    existing = _load_test_baseline()
    counts_changed = _baseline_counts_changed(existing, counts)
    canonical_needs_rewrite = _canonical_baseline_needs_rewrite(existing, counts_changed)

    # Kept for CLI compatibility; verification is now per-install and refreshed
    # after every green whole-suite run.
    del refresh_baseline_timestamp
    now = _utc_timestamp()
    git_sha = _git_sha()
    status = "verified"

    if canonical_needs_rewrite:
        baseline_changed_at = now if counts_changed else str(existing.get("baseline_changed_at", ""))
        status = "created" if existing is None else "updated"
        if existing is not None and not counts_changed:
            status = "migrated"
        payload: dict[str, object] = {
            "schema_version": TEST_BASELINE_SCHEMA_VERSION,
            "command": BASELINE_COMMAND,
            **counts,
            "baseline_changed_at": baseline_changed_at,
        }
        _write_test_baseline(payload)

    _write_test_baseline_verification(counts, verified_at=now, git_sha=git_sha)
    return status


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Sharded test runner")
    physical_cores = _physical_core_count()
    parser.add_argument("--shards", type=int, default=physical_cores, help=f"Number of shards (default: {physical_cores}, auto-detected physical cores)")
    parser.add_argument("--verbose", action="store_true", help="Show per-shard test lists")
    parser.add_argument(
        "--refresh-baseline-timestamp",
        action="store_true",
        help="Compatibility flag; green whole-suite runs always refresh per-install verification",
    )
    args = parser.parse_args(argv)

    num_shards = args.shards

    # Setup
    SHARD_RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # Collect
    test_ids = collect_test_ids()
    print(f"Collected {len(test_ids)} tests, distributing across {num_shards} shards\n")

    # Assign
    historical_durations = load_durations()
    historical_file_history = _load_file_duration_history()
    shards = assign_shards(test_ids, num_shards, historical_durations, historical_file_history)

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
    total_skipped = 0
    all_durations = {}

    for i in range(num_shards):
        tests, failures, errors, skipped, shard_time, durations = parse_shard_xml(i)
        total_tests += tests
        total_failures += failures
        total_errors += errors
        total_skipped += skipped
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
    file_history = _load_file_duration_history()
    if all_durations:
        save_durations(all_durations)
        print(f"\nSaved timing data for {len(all_durations)} tests to {DURATIONS_FILE.name}")
        file_history = _record_file_duration_history(
            file_history,
            shards,
            all_durations,
            num_shards,
            _utc_timestamp(),
        )
        _save_file_duration_history(file_history)
        print(f"Updated file timing history: {FILE_DURATION_HISTORY_FILE.name}")

    # Print shard timing balance report
    _print_shard_timing_balance(
        shard_results,
        shards,
        all_durations,
        historical_durations,
        file_history,
        historical_file_history,
    )
    _print_file_timing_diagnostics(
        shards,
        all_durations,
        historical_durations,
        file_history,
        historical_file_history,
    )

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
    total_passed = total_tests - total_failures - total_errors - total_skipped
    print(f"\n{'='*60}")
    print(f"TOTAL: {total_tests} tests | {total_passed} passed | {total_failures} failed | {total_errors} errors | {total_skipped} skipped")
    print(f"Wall time: {overall_elapsed:.1f}s ({num_shards} shards)")
    print(f"{'='*60}")

    full_suite_success = (
        total_tests == len(test_ids)
        and total_failures == 0
        and total_errors == 0
        and not any(rc != 0 for rc, _, _, _ in shard_results.values())
    )
    baseline_status = _write_test_baseline_if_needed(
        {
            "total": total_tests,
            "passed": total_passed,
            "failed": total_failures,
            "errors": total_errors,
            "skipped": total_skipped,
        },
        full_suite_success=full_suite_success,
        refresh_baseline_timestamp=args.refresh_baseline_timestamp,
    )
    if baseline_status in {"created", "updated", "migrated"}:
        print(f"Test baseline {baseline_status}: {TEST_BASELINE_FILE}")
    elif baseline_status == "verified":
        print(f"Test baseline verification recorded: {TEST_BASELINE_BY_INSTALL_DIR}")

    # Exit with failure if any shard failed
    if any(rc != 0 for rc, _, _, _ in shard_results.values()):
        sys.exit(1)


if __name__ == "__main__":
    main()
