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
python Tools/test_sharded/test_sharded.py --refresh-baseline-timestamp  # compatibility flag
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
| `--refresh-baseline-timestamp` | Compatibility flag. Green whole-suite runs now always refresh the per-install verification receipt. |

## How It Works

1. **Collect** -- Runs `pytest --collect-only` to gather all test node IDs.
2. **Group** -- Groups tests by source file (tests in the same file always stay together).
3. **Assign** -- Distributes file groups across shards:
   - **First run**: Round-robin by file, largest files assigned first.
   - **Subsequent runs**: Greedy least-loaded-bin using rolling per-file medians from `.test_file_duration_history.json` when available, with per-test durations from `.test_durations.json` filling gaps (requires >= 50% per-test coverage).
4. **Execute** -- Runs each shard as an independent `pytest.main()` subprocess with JUnit XML output.
5. **Aggregate** -- Parses JUnit XML results, merges timing data, and prints a combined report.
6. **Diagnose** -- Prints shard-level estimate/actual timing columns, per-shard file min/median/max timing, slowest files, and file timing variability when history is available.
7. **Baseline** -- After a successful whole-suite run, updates `AgentCoordination/generated/test_baseline.json` only when canonical counts change or the schema is migrated. It also records the local green-run receipt in `AgentCoordination/generated/test_baseline/by_install/<install_id>.json`.

## Output

- Per-shard pass/fail status with test counts and elapsed time.
- Shard timing balance report with wall time, estimated time, actual testcase time, estimate error, test/file counts, known-duration coverage, per-shard file min/median/max time, and historical file variability.
- File timing diagnostics listing the slowest files in the current run, the largest file-level estimate errors, and the most variable files once at least two runs of history exist.
- Aggregated failure details and deduplicated warnings.
- Final summary: total tests, passed, failed, errors, and wall-clock time.
- Saves exact pytest node-id timing data to `.test_durations.json` for future runs. Each shard writes a local `shard_<N>_durations.json` sidecar from pytest's `report.nodeid`; JUnit XML timing remains a fallback for older or interrupted shard results.
- Saves rolling per-file timing samples to `.test_file_duration_history.json` for local variability diagnostics. The file is ignored because it is machine- and shard-configuration-specific.
- Updates `AgentCoordination/generated/test_baseline.json` only after successful whole-suite runs when canonical counts change. Failed, partial, or interrupted runs leave the baseline and verification receipts unchanged.
- Updates `AgentCoordination/generated/test_baseline/by_install/<install_id>.json` after every successful whole-suite run. The install ID comes from `AgentCoordination/local/install_id.json`, shared with skill-usage tracking.

## Test baseline schema

The generated `AgentCoordination/generated/test_baseline.json` records the canonical repo-wide test count baseline. Field semantics:

- `baseline_changed_at` — timestamp updated whenever any of `total`, `passed`, `failed`, `errors`, `skipped` change.
- `schema_version` — bumped only on breaking schema changes.

Volatile verification data lives in per-install receipts at
`AgentCoordination/generated/test_baseline/by_install/<install_id>.json`.
Each receipt records `verified_at`, `git_sha`, `command`, and the counts from
that machine's latest green whole-suite run. Use
`python Tools/agent_coordination/summarize_test_baseline.py` to aggregate the
canonical counts with every per-install verification receipt into the
gitignored derived summary at
`AgentCoordination/generated/test_baseline/summary.json`.

The summary line in stdout includes a `skipped` column:

```
TOTAL: N tests | N passed | N failed | N errors | N skipped
```

CI scripts that parse this line by column position must account for the trailing `skipped` field added in the baseline tooling slice.

## Exit Code

- `0` if all shards pass.
- `1` if any shard has failures or errors.
