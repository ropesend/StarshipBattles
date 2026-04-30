# OpenCode / DeepSeek — Baseline Inventory Review

Author: OpenCode with DeepSeek V4 Pro
Date: 2026-04-30
Commit: 22f17ba16 — "Add agent coordination baseline inventory"

## Summary Judgment

Clean implementation. Every required behavior from the final plan is present:
baseline gating, skip-count parsing, inventory generation, stale-reference
scanning, and doc updates removing manual test counts. Tests cover the
policy edges well. No blocking issues. Proceed with three non-blocking
cleanup items and one question.

## Blocking Issues

None.

## Non-Blocking Issues

### 1. `parse_shard_xml` return-type change is an internal API break

The function changed from returning a 5-tuple to a 6-tuple (added `skipped`).
The only caller in `main()` was updated. No external users, so this is safe,
but the type annotation now serves as the canonical contract. If any helper
script or test elsewhere unpacks the old 5-tuple shape it will raise at
runtime. Confirmed via grep: no other callers exist.

### 2. `_find_project_root` heuristic is fragile

The function walks up looking for `game/` and `data/` directories. If
`data/` is ever removed or renamed, inventory generation breaks. Two
alternatives for a future refactor:

- `git rev-parse --show-toplevel` (already used elsewhere in the runner)
- Check for `pyproject.toml` or `AGENTS.md` at the root

Not a blocker — the 10-level fallback and clear error message are fine for
this slice.

### 3. `CLAUDE_FRONTMATTER_KEYS` is incomplete

The set tracks `allowed-tools`, `argument-hint`, `disable-model-invocation`,
and `model`. Missing from Claude Code's documented skill extensions:
`paths`, `hooks`, `shell`. The `context`, `agent`, and `effort` fields are
also Claude-specific but less commonly used in skills.

The `audit-shrink` skill uses `argument-hint`, which IS detected. The
missing fields mean some Claude-specific frontmatter would be silently
omitted from inventory metadata. Since the inventory is "observed facts,
not enforcement" (per the final plan), this is a completeness gap, not a
correctness bug. Fix before the validator phase.

### 4. Stdout format change may surprise CI scripts

The summary line changed from:
```
TOTAL: N tests | N passed | N failed | N errors
```
to:
```
TOTAL: N tests | N passed | N failed | N errors | N skipped
```

Any script parsing the sharded runner's stdout by column position will
break. Low risk (this output is human-facing), but worth noting in the
`Tools/test_sharded/README.md` if CI glues are known to exist.

## Questions

### `git_sha` is pre-commit HEAD — is that the intended contract?

The baseline records the SHA of HEAD *when the runner executed*, not the
SHA of the commit that contains this baseline file. For commit 22f17ba16,
the baseline records `2f34d174` (the parent). This is documented as a
known point.

If the contract is "SHA at time of generation," this is correct. The Phase
7 validator should not fail when baseline SHA != commit SHA — that would be
a misuse. Recommend adding a one-line note to the baseline schema (or
`AgentCoordination/generated/README.md`) stating: "git_sha is HEAD at run
time, not necessarily the commit containing this file."

## Evidence

- **Skipped-count parsing**: `parse_shard_xml` at `Tools/test_sharded/test_sharded.py:268`
  sums `suite.get("skipped", 0)` per XML suite. Hit count `16063 - 16060 - 0 - 0 = 3`
  matches the known 3 skipped.
- **Baseline gating**: `_write_test_baseline_if_needed` returns `"skipped"` when
  `full_suite_success=False`, regardless of `refresh_baseline_timestamp`. Tested
  in `test_failed_or_partial_run_never_updates_baseline`.
- **`verified_at` refresh**: `test_refresh_baseline_timestamp_updates_verified_at_only`
  confirms unchanged `baseline_changed_at` and updated `verified_at`.
- **Count change**: `test_count_change_updates_baseline_changed_at` confirms both
  timestamps update on count delta.
- **Inventory determinism**: `json.dumps(..., sort_keys=True)` and sorted directory
  iteration produce consistent output for tracking.
- **stale_references detection**: Inventory correctly flags 11 stale references
  across `.agent/workflows/`, `.agent/MIGRATION_PROGRESS.md`, removed doc paths,
  `python -m unittest discover`, and stale Starship Battles paths in settings.
- **Doc updates**: `AGENTS.md:67` and `CLAUDE.md:146,319` no longer contain manual
  test counts. Both reference `AgentCoordination/generated/test_baseline.json`.
- **OpenCode visibility**: `.agent/skills/` correctly has `opencode_visible: false`
  with `opencode_permission: "not_visible"`. All others have `opencode_visible: true`.
- **Prefix compliance**: All 74 unprefixed skills correctly show
  `prefix_compliant: false` with their expected future prefix. The 8 Codex
  skills correctly show `prefix_compliant: true`.

## Final Recommendation

Approve and merge. The three non-blocking items can be addressed in the next
coordination slice or during the Phase 7 validator implementation. The
`git_sha` contract clarification is the only item worth deciding before the
validator spec is finalized.
