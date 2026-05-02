# Codex Agent Coordination System Review

Author: Codex
Date: 2026-04-30
Branch reviewed: `codex/agent-coordination-baseline-inventory`
Head reviewed: `dcdcec561c1137f8c90bbd724e892730fea96aca`

## Summary Judgment

Claude's "fully implemented" claim is mostly true for the core coordination
system, but I would not call the system fully finished yet.

Implemented and passing:

- Prefix migration is complete: all skill directories are prefixed with
  `claude-`, `anti-`, `ocode-`, or `codex-`.
- `.agent/workflows/` and `.agent/MIGRATION_PROGRESS.md` are gone.
- Generated artifacts exist for test baseline, skill inventory, and usage
  counters.
- Validator, prefix checker, sanitizer, renamer, inventory, and usage scripts
  exist.
- GitHub Actions enforcement exists at `.github/workflows/agent_coordination.yml`.
- The focused coordination test suite passes locally.

Remaining work is mostly drift cleanup and validator coverage. The most
important issue is that current user-facing docs still teach old unprefixed
slash commands, while the validator reports green.

## Verification Performed

Commands run:

```powershell
py -3.10 Tools/agent_coordination/check_skill_prefixes.py
py -3.10 Tools/agent_coordination/validate_agent_surfaces.py
py -3.10 Tools/agent_coordination/sanitize_claude_settings.py
py -3.10 Tools/agent_coordination/rename_skills_with_prefixes.py --dry-run
py -3.10 -m pytest tests/unit/tools/test_agent_surface_inventory.py tests/unit/tools/test_test_sharded_baseline.py tests/unit/tools/test_agent_skill_prefix_checker.py tests/unit/tools/test_agent_skill_prefix_renamer.py tests/unit/tools/test_sanitize_claude_settings.py tests/unit/tools/test_skill_usage_tracking.py tests/unit/tools/test_validate_agent_surfaces.py -q
```

Results:

- Prefix checker: pass.
- Full coordination validator: pass, 0 failures, 0 warnings.
- Sanitizer: pass, 0 dangerous/secret/external findings.
- Renamer dry-run: 0 renames planned, 0 references found.
- Focused tests: 118 passed.
- `git status --short`: clean before this review file was written.

I did not run the full sharded game test suite during this review.

## Findings

### 1. Current docs still teach old unprefixed skill commands

Severity: high.

The prefix migration is applied to the skill surfaces, but several current
README/tool docs still tell users and agents to invoke old names like
`/proj-start`, `/ticket-work`, `/qa-triage`, and `/audit-shrink`.

Evidence:

- `Projects/README.md:11-36` lists `/proj-*`, `/ticket-*`, `/qa-triage`,
  and `/triage-to-proj`.
- `Projects/README.md:77-90` describes the project lifecycle using
  `/proj-start`, `/proj-continue`, `/proj-review`, `/proj-audit`, and
  `/proj-close`.
- `Tracking/README.md:51-66` lists `/ticket-*` commands.
- `Tracking/README.md:100` says the user must invoke `/ticket-close`.
- `Tools/audit_shrink/README.md:73` says to run `/audit-shrink`.
- `Tools/check_context/README.md:53` calls this the `/proj-continue`
  workflow.

The validator misses this because `check_volatile_facts()` scans only
`AGENTS.md`, `CLAUDE.md`, `.agents/CODEX.md`, and `SKILL.md` files
(`Tools/agent_coordination/validate_agent_surfaces.py:323-334`). The renamer's
reference scope similarly included `Projects/protocols` and
`Tracking/protocols`, but not `Projects/README.md`, `Tracking/README.md`, or
tool READMEs (`Tools/agent_coordination/rename_skills_with_prefixes.py:44-57`).

Recommendation:

- Update current README/tool docs to use the post-migration names or an
  agent-neutral explanation that explicitly points to the prefixed skill names.
- Add a validator check for unprefixed legacy skill invocations in current docs.
- Exclude historical review artifacts and archived/deep-archive project files
  from that check, but include active/current READMEs and protocols.

### 2. Coordination docs still describe pre-completion states

Severity: medium.

Several coordination docs are stale relative to the code now on disk.

Evidence:

- `AgentCoordination/README.md:15` says `skill_rename_map.toml` is a plan for
  the "upcoming prefix rename", but the migration is already applied.
- `AgentCoordination/README.md:26` says the sanitizer is "dry-run only", but
  `Tools/agent_coordination/sanitize_claude_settings.py --help` exposes
  `--apply`.
- `AgentCoordination/README.md:40` says stale `.agent/workflows/` and
  `.agent/MIGRATION_PROGRESS.md` are scheduled for removal, but both are
  already removed.
- `Tools/agent_coordination/README.md:8-9` says the inventory is input to the
  "later validator and prefix migration work".
- `Tools/agent_coordination/README.md:66` says the sanitizer is dry-run only.
- `Tools/agent_coordination/README.md:81-83` says apply mode is not
  implemented yet.
- `sanitize_claude_settings.py:469-470` documents a real `--apply` option, and
  `tests/unit/tools/test_sanitize_claude_settings.py:261-337` tests apply
  behavior.

Recommendation:

- Update `AgentCoordination/README.md` and `Tools/agent_coordination/README.md`
  to describe the current post-migration state.
- Make the docs explicit about which files are historical audit artifacts and
  which are regenerated current-state artifacts.

### 3. CI omits the usage tracking unit tests

Severity: medium.

The usage counter scripts are part of the final plan and have a dedicated unit
test file, but the GitHub Actions workflow does not run that test file.

Evidence:

- `.github/workflows/agent_coordination.yml:36-43` runs six focused test files.
- It omits `tests/unit/tools/test_skill_usage_tracking.py`.
- The omitted test file covers `log_skill_usage.py` and
  `summarize_skill_usage.py`.

Recommendation:

- Add `tests/unit/tools/test_skill_usage_tracking.py` to the focused CI pytest
  command.

### 4. Inventory warnings and validator output are not aligned

Severity: low to medium.

The generated inventory records absolute paths in `.claude/settings.local.json`
as warnings, but the validator reports 0 warnings because the sanitizer
classifies the current paths as OK.

Evidence:

- `AgentCoordination/generated/agent_surface_inventory.json:4-60` contains
  eight `absolute_path` entries with `"severity": "warn"`.
- `sanitize_claude_settings.py` classifies current `Developer/StarshipBattles`
  paths and the pygame_gui site-packages path as OK.
- `validate_agent_surfaces.py` reports 0 warnings.

This is not necessarily wrong. The user explicitly accepted nonsensical or
nonexistent Starship Battles permission paths as non-blocking, and the
sanitizer is the more policy-aware tool. The problem is that the inventory calls
these findings `stale_references`, while the validator ignores them. That makes
the green validator output look cleaner than the generated inventory.

Recommendation:

- Either rename the inventory bucket from `stale_references` to something like
  `observations`, or have the validator surface selected inventory warnings.
- Document that accepted Starship Battles absolute permission paths are
  inventory observations, not validator failures.

### 5. The rename audit artifact no longer preserves the original migration map

Severity: low.

`SKILL_RENAMES.md` is described as an audit artifact, but after the migration
and a fresh dry-run it now records only already-compliant `old name == new name`
entries. That is useful as a current-state report, but it no longer documents
the original unprefixed-to-prefixed migration without consulting git history.

Evidence:

- `py -3.10 Tools/agent_coordination/rename_skills_with_prefixes.py --dry-run`
  reported `Renames planned: 0` and `References: 0`.
- `AgentCoordination/SKILL_RENAMES.md` now lists entries such as
  `claude-proj-start` to `claude-proj-start` with status "already compliant".

Recommendation:

- Decide whether `SKILL_RENAMES.md` is a current-state report or a historical
  migration audit.
- If it is historical, preserve the original before/after mapping in a separate
  non-regenerated file.
- If it is current-state only, rename or reword it so future agents do not
  expect it to explain the completed migration.

### 6. Usage tracking is implemented, but not automatically reliable

Severity: low.

The scripts are implemented and documented, but the current system still depends
on agents remembering to call `log_skill_usage.py` after skill invocation. That
matches the final plan's "agents call a script" policy, but it remains a known
accuracy limit.

Evidence:

- `AGENTS.md:84-94`, `.agents/CODEX.md:42-50`, and `CLAUDE.md:338-351`
  instruct agents to call the script.
- `.claude/settings.json` contains a `Stop` hook for context reporting, but no
  hook that logs skill usage.
- `Tools/agent_coordination/README.md:106-109` describes a Claude Code hook as
  the natural integration, not something currently installed.

Recommendation:

- Keep the current counters advisory only.
- If usage counts become important, prototype a Claude-specific hook or
  transcript scanner in a separate reviewed change.

## Checked And Acceptable

- `AgentCoordination/generated/test_baseline.json` records
  `git_sha = 63da33912e827eea1141cb64289931fa562c4291`, while current HEAD is
  `dcdcec561c1137f8c90bbd724e892730fea96aca`. This is acceptable because
  `Tools/test_sharded/README.md` documents that `git_sha` is HEAD at test run
  time, not the commit containing the baseline file.
- OpenCode permission ordering is correct for the documented last-match-wins
  model: `*` comes before `claude-*`, `codex-*`, `anti-*`, and `ocode-*` in
  `opencode.json:37-44`.
- `.agent/workflows/` and `.agent/MIGRATION_PROGRESS.md` are absent.
- `.claude/settings.json` and `.claude/settings.local.json` are parseable and
  contain no sanitizer-classified secrets, dangerous permissions, or unapproved
  external paths.

## Recommended Next Steps

1. Fix stale current docs that still advertise old unprefixed commands.
2. Extend the validator to catch those old invocations in current docs.
3. Refresh coordination READMEs to post-implementation wording.
4. Add `tests/unit/tools/test_skill_usage_tracking.py` to the CI workflow.
5. Decide whether `SKILL_RENAMES.md` should be historical or current-state.

After those are done, I would be comfortable calling the coordination system
implemented, with usage counters explicitly treated as advisory.
