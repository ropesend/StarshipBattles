# Sharded Test Runner

Splits the full pytest suite into independent single-threaded shards and runs them in parallel across CPU cores.

## Purpose

Running the entire test suite sequentially is slow on multi-core machines. This tool distributes tests across N parallel pytest processes (one per physical CPU core by default) for significantly faster full-suite execution. On subsequent runs, it uses recorded timing data to balance shard workloads via a greedy least-loaded-bin algorithm.

## Requirements

No additional dependencies beyond the base project (`pytest`, `pytest-xdist`).

## Usage

```bash
python Tools/test_sharded/test_sharded.py              # auto-detect shards (= physical CPU cores)
python Tools/test_sharded/test_sharded.py --shards 8    # custom shard count
python Tools/test_sharded/test_sharded.py --verbose     # show per-shard test lists
python Tools/test_sharded/test_sharded.py --refresh-baseline-timestamp
```

There is also a PowerShell convenience wrapper:

```powershell
.\Tools\test_sharded\test.ps1
```

### Arguments

| Argument    | Description                                                        |
|-------------|--------------------------------------------------------------------|
| `--shards N`| Number of parallel shards (default: auto-detected physical cores). |
| `--verbose` | Show the first test ID in each shard for debugging distribution.   |
| `--refresh-baseline-timestamp` | Refresh `verified_at` in the generated test baseline after a successful whole-suite run, even when counts are unchanged. |

## How It Works

1. **Collect** -- Runs `pytest --collect-only` to gather all test node IDs.
2. **Group** -- Groups tests by source file (tests in the same file always stay together).
3. **Assign** -- Distributes file groups across shards:
   - **First run**: Round-robin by file, largest files assigned first.
   - **Subsequent runs**: Greedy least-loaded-bin using per-test durations from `.test_durations.json` (requires >= 50% coverage).
4. **Execute** -- Runs each shard as an independent `pytest.main()` subprocess with JUnit XML output.
5. **Aggregate** -- Parses JUnit XML results, merges timing data, and prints a combined report.
6. **Baseline** -- After a successful whole-suite run, updates `AgentCoordination/generated/test_baseline.json` only when counts change. With `--refresh-baseline-timestamp`, also refreshes `verified_at` on unchanged counts.

## Output

- Per-shard pass/fail status with test counts and elapsed time.
- Shard timing balance report (bar chart with balance ratio).
- Aggregated failure details and deduplicated warnings.
- Final summary: total tests, passed, failed, errors, and wall-clock time.
- Saves per-test timing data to `.test_durations.json` for future runs.
- Updates `AgentCoordination/generated/test_baseline.json` only after successful whole-suite runs. Failed, partial, or interrupted runs leave the baseline unchanged.

## Exit Code

- `0` if all shards pass.
- `1` if any shard has failures or errors.
