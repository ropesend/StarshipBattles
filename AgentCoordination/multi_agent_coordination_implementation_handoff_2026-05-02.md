# Multi-Agent Coordination Implementation Handoff

Status: implementation-ready plan
Date: 2026-05-02
Author: Codex

## Purpose

This document is a detailed handoff for a fresh agent implementing the next
Starship Battles multi-agent coordination cleanup.

The implementation should align Claude Code, Codex, OpenCode, and Antigravity
surfaces after the prefix migration. The work must preserve the existing
strengths of the coordination system while fixing remaining drift and unsafe
workflow instructions.

## Required Reading Before Work

Read these files first:

1. `AGENTS.md`
2. `.agents/CODEX.md` if the implementer is Codex
3. `docs/README.md`
4. `docs/01_ARCHITECTURE.md`
5. `docs/02_PATTERNS.md`
6. `docs/03_CONVENTIONS.md`
7. `AgentCoordination/README.md`
8. `Tools/agent_coordination/README.md`
9. `AgentCoordination/multi_agent_coordination_refinement_plan_2026-05-02.md`
10. `AgentCoordination/opencode_deepseek_v4_pro_refinement_plan_review.md`

Never read `docs/_ignore/`.

## Non-Negotiable Implementation Rules

- Follow strict TDD for code/tooling changes: write or update the failing test
  first, run it to confirm failure, then implement.
- Check `git status --short` before editing.
- Do not revert unrelated user changes.
- Keep generated artifacts consistent with tooling.
- Update docs and coordination docs in the same change as behavior changes.
- Use repo-local tooling where possible.

## User Decisions Already Made

These are settled decisions. Do not reopen them unless implementation uncovers
a hard blocker.

1. `CLAUDE.md` should remain a thin adapter, but it should still duplicate the
   critical hard rules because Claude Code reliably reads `CLAUDE.md` at
   startup.
2. `/anti-*` references outside Antigravity surfaces are migration errors.
3. Antigravity should be limited to tooling, asset processing, and the
   explicitly approved analysis/design-validation skills listed below.
4. All skill usage must be logged.
5. Triggering skill usage logging must update all usage artifacts in one script
   invocation.
6. Claude should enforce `claude-*` usage logging through hooks.
7. Codex, OpenCode, and Antigravity should explicitly run
   `Tools/agent_coordination/log_skill_usage.py`.
8. `.claude/settings.local.json` should no longer be tracked and can be
   ignored by validator content checks.
9. `AgentCoordination/agent_surface_policy.json` is accepted as the policy
   manifest location.
10. Add validators first and confirm they catch existing issues, then fix the
    issues.
11. For failed merge rollbacks, use `git revert`, not `git reset --hard`.
12. Require a clean worktree before merge/revert steps when dirty state could
    cause conflicts.
13. For reverting merge commits, use `git revert -m 1 <merge_commit_sha>
    --no-edit`.
14. Follow OpenCode's suggested `CLAUDE.md` keep/cut breakdown.
15. OpenCode supports the `Task` tool with `subagent_type`; OpenCode also has a
    `write` tool controlled by the `edit` permission. Do not rewrite
    `ocode-audit-shrink` solely because it says "Task tool" or "Write tool".

## Current Known Dirty State

At the time this handoff was written, the worktree had uncommitted coordination
artifacts from prior review/planning:

- Modified: `AgentCoordination/generated/skill_usage/summary.json`
- Untracked: `AgentCoordination/generated/skill_usage/by_install/d9797b649b724199879d59be61d9e432.json`
- Untracked: `AgentCoordination/multi_agent_coordination_refinement_plan_2026-05-02.md`
- Untracked: `AgentCoordination/opencode_deepseek_v4_pro_refinement_plan_review.md`
- Untracked: this handoff file

Do not discard these. Work with them.

## Approved Antigravity Keep List

After narrowing Antigravity, keep exactly these `.agent/skills` entries unless
the user gives new direction:

- `anti-analysis-complexity`
- `anti-analysis-dead-code`
- `anti-analysis-sweep`
- `anti-loc`
- `anti-validate-designs`

Retire all other `.agent/skills/anti-*` directories:

- `anti-debug-sequential`
- `anti-deep-dive-sequential`
- `anti-fix-crash`
- `anti-proj-*`
- `anti-qa-*`
- `anti-ticket-*`
- `anti-triage-to-proj`

Retirement means delete the directories, update/generated inventory, and remove
or rewrite live references. Do not preserve alias skills.

## Online OpenCode Verification

The previous review checked current OpenCode docs/source on 2026-05-02:

- OpenCode docs list built-in subagents and describe `permission.task`.
- OpenCode source `packages/opencode/src/tool/task.ts` includes parameters:
  `description`, `prompt`, `subagent_type`, optional `task_id`, and optional
  `command`.
- OpenCode docs list a `write` tool, controlled by the `edit` permission.

Conclusion: the OpenCode audit skill can keep `Task tool`,
`subagent_type`, and `Write tool` wording unless local testing proves a
configuration issue.

## Desired End State

1. `validate_agent_surfaces.py` enforces the new policy.
2. `AgentCoordination/agent_surface_policy.json` records the mutable policy.
3. Skill usage logging is atomic: one `log_skill_usage.py` invocation updates
   the per-install file and `summary.json`.
4. Wrong `/anti-*` and nonexistent skill-path references are fixed.
5. Antigravity contains only the approved keep-list skills.
6. `.claude/settings.local.json` is ignored and no longer tracked.
7. `CLAUDE.md` is reduced to a thin, reinforced adapter.
8. Parallel workflow rollback docs use `git revert`, with merge-commit
   `-m 1` guidance and clean-worktree preconditions.
9. Existing coordination validator, prefix checker, inventory freshness check,
   and focused tool tests pass.

## Phase 0: Preflight

Run:

```powershell
git status --short
python Tools/agent_coordination/validate_agent_surfaces.py
python Tools/agent_coordination/check_skill_prefixes.py
```

If invoking a skill, log usage:

```powershell
python Tools/agent_coordination/log_skill_usage.py --agent <codex|claude|ocode|anti> --skill <skill-name>
```

Until Phase 2 is implemented, also run:

```powershell
python Tools/agent_coordination/summarize_skill_usage.py
```

## Phase 1: Add Policy Manifest And Validator Tests First

### Goal

Add test coverage that currently fails against the live repo, proving the
validator can detect the known drift before the drift is fixed.

### Create Policy Manifest

Add:

```text
AgentCoordination/agent_surface_policy.json
```

Initial content:

```json
{
  "schema_version": 1,
  "skill_prefixes": {
    "claude": "claude-",
    "codex": "codex-",
    "ocode": "ocode-",
    "anti": "anti-"
  },
  "antigravity": {
    "allowed_skills": [
      "anti-analysis-complexity",
      "anti-analysis-dead-code",
      "anti-analysis-sweep",
      "anti-loc",
      "anti-validate-designs"
    ],
    "retired_patterns": [
      "anti-debug-*",
      "anti-deep-dive-*",
      "anti-fix-crash",
      "anti-proj-*",
      "anti-qa-*",
      "anti-ticket-*",
      "anti-triage-to-proj"
    ]
  },
  "cross_agent_references": {
    "default": "deny",
    "allowed": []
  },
  "claude_settings": {
    "tracked_files": [
      ".claude/settings.json"
    ],
    "ignored_files": [
      ".claude/settings.local.json"
    ],
    "validate_ignored_file_contents": false
  },
  "rollback": {
    "failed_merge_strategy": "revert",
    "merge_commit_revert_command": "git revert -m 1 <merge_commit_sha> --no-edit",
    "requires_clean_worktree": true
  }
}
```

Do not include `generated_at`; this is a human-maintained policy file. Avoid
timestamps unless the file is generated.

### Tests To Add

Edit `tests/unit/tools/test_validate_agent_surfaces.py`.

Add tests for:

1. **Policy manifest shape**
   - Missing `schema_version` fails.
   - Missing required sections fails.
   - Valid minimal policy passes.

2. **Cross-agent command references**
   - A `.claude/skills/claude-foo/SKILL.md` line containing
     `` `/anti-ticket-work` `` fails.
   - A `.agents/skills/codex-foo/SKILL.md` line containing
     `` `.claude/skills/anti-qa-triage/SKILL.md` `` fails because the path
     is both cross-agent and nonexistent.
   - Ordinary words like `anti-pattern`, `anti-reversion`, and
     `anti-aliasing` do not fail.
   - A same-surface reference such as `` `/claude-ticket-work` `` inside a
     Claude skill passes.

3. **Nonexistent skill path references**
   - Any live `SKILL.md` reference to `.claude/skills/<name>/SKILL.md`,
     `.agent/skills/<name>/SKILL.md`, `.agents/skills/<name>/SKILL.md`, or
     `.opencode/skills/<name>/SKILL.md` fails if the path does not exist.
   - Existing skill paths pass.

4. **Antigravity allowlist**
   - A `.agent/skills/anti-ticket-work/SKILL.md` fixture fails with
     `policy.antigravity_unapproved_skill`.
   - A `.agent/skills/anti-validate-designs/SKILL.md` fixture passes.

5. **Tracked local Claude settings**
   - If `.claude/settings.local.json` is tracked by git, validator fails.
   - Once ignored/untracked, validator skips content checks for that file.

6. **Rollback protocol guard**
   - A live protocol/skill file containing `git reset --hard HEAD~1` fails.
   - A file containing `git revert -m 1 <merge_commit_sha> --no-edit`
     passes.

### Implementation Notes

Add functions to `Tools/agent_coordination/validate_agent_surfaces.py`:

- `load_agent_surface_policy(repo_root: Path) -> dict[str, object]`
- `check_agent_surface_policy(repo_root: Path) -> list[Finding]`
- `check_cross_agent_references(repo_root: Path) -> list[Finding]`
- `check_nonexistent_skill_path_references(repo_root: Path) -> list[Finding]`
- `check_antigravity_policy(repo_root: Path) -> list[Finding]`
- `check_tracked_local_settings(repo_root: Path) -> list[Finding]`
- `check_rollback_policy(repo_root: Path) -> list[Finding]`

Add them to the validator `CHECKS` list.

For tracked-file detection, prefer:

```powershell
git ls-files -z
```

inside the validator, parsed into a path set. In unit tests, create a temporary
git repo with `git init` and `git add .claude/settings.local.json` to verify
tracked detection. If git is unavailable in a test environment, make the helper
return an empty set and test the pure path-set helper separately.

### Red Test Expectations

Before fixing live drift, running:

```powershell
python Tools/agent_coordination/validate_agent_surfaces.py
```

should fail because current live files still contain `/anti-*` references,
tracked `.claude/settings.local.json`, broad Antigravity skills, and rollback
reset instructions.

This failure is intentional. Commit only after later phases make it green.

## Phase 2: Make Skill Usage Logging Atomic

### Goal

One invocation of `log_skill_usage.py` updates:

- `AgentCoordination/generated/skill_usage/by_install/<install_id>.json`
- `AgentCoordination/generated/skill_usage/summary.json`

### Tests First

Edit `tests/unit/tools/test_skill_usage_tracking.py`.

Add or update tests:

- `test_log_updates_summary_on_first_use`
- `test_log_updates_summary_when_incrementing_existing_skill`
- `test_log_updates_summary_for_multiple_installs`
- `test_log_invalid_agent_writes_nothing`
- `test_log_invalid_skill_writes_nothing`

Existing tests for `summarize_skill_usage.py` should keep passing.

### Implementation

Options:

1. Import `summarize_skill_usage._aggregate()` from `log_skill_usage.py` and
   write `summary.json` after `_record_usage()`.
2. Better: expose a public helper in `summarize_skill_usage.py`:

   ```python
   def write_summary(repo_root: Path) -> None:
       ...
   ```

   Then call it from `log_skill_usage.py`.

Keep `summarize_skill_usage.py` as a standalone maintenance command. Do not
delete it.

### Docs To Update

Update:

- `AGENTS.md`
- `.agents/CODEX.md`
- `CLAUDE.md`
- `AgentCoordination/README.md`
- `Tools/agent_coordination/README.md`

Remove wording that implies the user or agent must manually run the summarizer
after logging. The summarizer may remain documented as a repair/regeneration
tool.

## Phase 3: Fix Cross-Agent Prefix Drift

### Goal

Eliminate erroneous `/anti-*` references outside Antigravity surfaces and fix
nonexistent skill path references.

### Known Live Drift

Run:

```powershell
rg -n "/anti-|\\.claude/skills/anti-|\\.agent/skills/anti-|\\.agents/skills/anti-" .claude .agents Projects Tracking AgentCoordination
```

Known examples to fix include:

- `.claude/skills/claude-analysis-sweep/SKILL.md`
- `.claude/skills/claude-proj-add-to-plan/SKILL.md`
- `.claude/skills/claude-proj-extract-phase/SKILL.md`
- `.claude/skills/claude-proj-parallel/SKILL.md`
- `.claude/skills/claude-proj-revise/SKILL.md`
- `.claude/skills/claude-qa-feedback/SKILL.md`
- `.claude/skills/claude-qa-triage/SKILL.md`
- `.claude/skills/claude-ticket-*.md` / `claude-ticket-*` skill files with
  `description:` examples using `/anti-ticket-*`
- `.agents/skills/codex-starship-qa-observer/SKILL.md`
- `Projects/protocols/03b_parallel_projects.md`
- `Projects/protocols/07_extract_phase.md`

### Rewrite Rules

- In `.claude/skills`, replace `/anti-...` with the matching `/claude-...`
  when the corresponding Claude skill exists.
- In shared protocol docs, prefer neutral wording such as "run the project
  start skill for your current agent surface" unless the protocol is explicitly
  Claude-only.
- In Codex skills, do not point to `.claude/skills/anti-*`. Prefer:
  - project/ticket/QA protocol docs, or
  - Codex-owned skill instructions, or
  - a short embedded workflow summary.
- Do not rewrite ordinary prose containing "anti" unless it is a skill
  invocation or skill path.

### Validation

After the fixes:

```powershell
python Tools/agent_coordination/validate_agent_surfaces.py
```

The cross-agent reference and nonexistent path checks should pass.

## Phase 4: Harden Rollback Protocols

### Goal

Remove destructive positional reset guidance and replace it with safe revert
guidance.

### Files To Edit

- `Tracking/protocols/02c_parallel_debug.md`
- `Tracking/protocols/02d_parallel_deep_dive.md`
- `Projects/protocols/03b_parallel_projects.md`
- `.claude/skills/claude-debug-parallel/SKILL.md`
- `.claude/skills/claude-deep-dive-parallel/SKILL.md`
- `.claude/skills/claude-proj-parallel/SKILL.md`

Search:

```powershell
rg -n "git reset --hard HEAD~1|git reset --hard" Tracking Projects .claude .agent .agents .opencode
```

### Required Replacement Policy

Use this wording, adapted to each file's style:

```text
Before merging a worker branch, require `git status --short` to be clean.
If the merge conflicts before a merge commit exists, use `git merge --abort`.
If tests fail after a merge commit is created, revert the merge commit instead
of rewriting history:

`git revert -m 1 <merge_commit_sha> --no-edit`

If the worktree is dirty, the merge commit SHA is unclear, or the revert
conflicts, stop and ask the user. Do not use `git reset --hard` for protocol
rollback.
```

For non-merge commits, the protocol may mention:

```powershell
git revert <commit_sha> --no-edit
```

but the parallel merge workflows should explicitly show the merge-commit form
with `-m 1`.

### Validation

The new rollback validator should fail on any remaining
`git reset --hard HEAD~1` in current agent/protocol surfaces.

## Phase 5: Thin `CLAUDE.md`

### Goal

Reduce stale duplicated content while keeping hard rules directly visible to
Claude Code.

### Keep

Keep these sections or concise equivalents:

- Three Non-Negotiable Rules
- Documentation First, including `docs/_ignore/`
- Project Overview tech stack and spatial terminology
- TDD workflow and canonical test commands
- Key conventions:
  - return-type annotations
  - file size ceiling
  - specific exceptions
  - no save-file migration
  - root-cause fixes
  - no unrelated reverts
- Git workflow, if short
- Skill usage logging and Claude hook behavior
- Subagent report output convention, if still Claude-specific

### Cut Or Replace With References

Remove or heavily compress:

- Architecture Principles section with stale layer summary.
- Pattern count claims.
- ApplicationContext service count claims.
- Large project structure tree.
- Common task walkthroughs such as adding abilities.
- Test worker-count details that belong in generated artifacts or `AGENTS.md`.

### Important

If duplicating hard rules from `AGENTS.md`, keep or add the accepted
reinforcement markers:

```html
<!-- agent-coordination:reinforcement tdd -->
<!-- agent-coordination:reinforcement docs-first -->
<!-- agent-coordination:reinforcement code-doc-consistency -->
<!-- agent-coordination:reinforcement root-cause -->
<!-- agent-coordination:reinforcement no-ignore-folder -->
<!-- agent-coordination:reinforcement no-revert-unrelated -->
```

Do not put reinforcement markers in `SKILL.md` files.

### Validation

Run:

```powershell
python Tools/agent_coordination/validate_agent_surfaces.py
```

Pay close attention to `reinforcement_markers` and `volatile_facts`.

## Phase 6: Retire Broad Antigravity Skills

### Goal

Make `.agent/skills` match the approved Antigravity scope.

### Delete Retired Directories

Delete every `.agent/skills/anti-*` directory not in the keep list.

Use PowerShell carefully. Before recursive deletion, verify paths resolve
inside `C:\Dev2\StarshipBattles\.agent\skills`.

Suggested safe pattern:

```powershell
$root = (Resolve-Path ".agent\skills").Path
$keep = @(
  "anti-analysis-complexity",
  "anti-analysis-dead-code",
  "anti-analysis-sweep",
  "anti-loc",
  "anti-validate-designs"
)
Get-ChildItem ".agent\skills" -Directory |
  Where-Object { $_.Name -like "anti-*" -and $_.Name -notin $keep } |
  ForEach-Object {
    $resolved = (Resolve-Path $_.FullName).Path
    if (-not $resolved.StartsWith($root)) {
      throw "Refusing to delete outside skill root: $resolved"
    }
    Remove-Item -LiteralPath $resolved -Recurse
  }
```

Do not use `cmd /c` or shell-composed delete commands.

### Update References

After deletion:

```powershell
rg -n "anti-proj|anti-ticket|anti-qa|anti-debug|anti-deep-dive|anti-fix-crash|anti-triage-to-proj" AGENTS.md CLAUDE.md .agents .claude .agent .opencode Projects Tracking AgentCoordination Tools
```

Rewrite or remove live references. Historical review files under
`AgentCoordination/*_comments.md`, older plans, and generated historical
reports may mention retired names. The validator should decide which paths are
current policy vs. history.

### Regenerate Inventory

Run:

```powershell
python Tools/agent_coordination/inventory_agent_surfaces.py
python Tools/agent_coordination/check_skill_prefixes.py
python Tools/agent_coordination/validate_agent_surfaces.py
```

Commit updated `AgentCoordination/generated/agent_surface_inventory.json`.

## Phase 7: Stop Tracking `.claude/settings.local.json`

### Goal

Keep local Claude permissions local and machine-specific.

### Implementation

1. Add to `.gitignore`:

   ```text
   .claude/settings.local.json
   ```

2. Remove the file from git tracking while preserving it locally:

   ```powershell
   git rm --cached .claude/settings.local.json
   ```

3. Add a tracked example:

   ```text
   .claude/settings.example.json
   ```

   Keep it conservative:

   - Shared hooks may be documented in `.claude/settings.json`.
   - Avoid absolute machine-local paths.
   - Avoid broad destructive permissions.
   - Include comments only if Claude settings JSON supports them. If not,
     keep comments in README docs instead.

4. Update:

   - `AgentCoordination/README.md`
   - `Tools/agent_coordination/README.md`
   - `sanitize_claude_settings.py`
   - `validate_agent_surfaces.py`
   - relevant tests

### Validator Policy

- Fail if `.claude/settings.local.json` is tracked.
- Skip content validation for ignored local settings by default.
- Continue validating `.claude/settings.json` and any tracked example settings.

Do not add a separate local audit mode unless the user asks later.

## Phase 8: Update OpenCode Notes If Needed

No required mechanical change is currently needed for `Task tool`,
`subagent_type`, or `Write tool` wording in
`.opencode/skills/ocode-audit-shrink/SKILL.md`.

Optional improvement:

- Add a short note to the refinement plan or `AgentCoordination/README.md`
  that current OpenCode docs/source were checked and support those terms.

Do not make this a large rewrite unless local OpenCode execution proves a
problem.

## Phase 9: Final Validation

Run these commands:

```powershell
python Tools/agent_coordination/check_skill_prefixes.py
python Tools/agent_coordination/inventory_agent_surfaces.py
python Tools/agent_coordination/validate_agent_surfaces.py
```

Run focused tests:

```powershell
python -m pytest tests/unit/tools -q
```

If the system Python lacks pytest, use the repo's configured environment if
available. If no `.venv` exists, report that focused tests could not run and
include the exact error.

If agent skill directories changed, verify the generated inventory is fresh:

```powershell
git diff -- AgentCoordination/generated/agent_surface_inventory.json
```

If usage logging was invoked during the work, the generated usage files should
be updated and validator should pass `usage_counter_shape`.

## Phase 10: Final Report To User

Final response should include:

- Summary of implemented changes.
- Validator and test results.
- Any tests that could not run and why.
- Any policy decisions still requiring user confirmation.
- Exact path of the policy manifest and any new/retired skill surfaces.

Keep the final response concise but specific.

## Suggested Commit/PR Breakdown

If doing this as multiple commits or PRs, use this order:

1. Policy manifest and validator tests/checks.
2. Atomic usage logging.
3. Prefix drift fixes.
4. Rollback protocol hardening.
5. `CLAUDE.md` thinning.
6. Antigravity retirement and inventory regeneration.
7. Claude local settings untracking.

The first commit/PR should intentionally introduce failing validator checks
only if the same PR also fixes the live drift before merge. Do not leave `main`
with a failing validator.

## Quick Reference: Files Likely To Change

Tooling:

- `Tools/agent_coordination/validate_agent_surfaces.py`
- `Tools/agent_coordination/log_skill_usage.py`
- `Tools/agent_coordination/summarize_skill_usage.py`
- `Tools/agent_coordination/sanitize_claude_settings.py`

Tests:

- `tests/unit/tools/test_validate_agent_surfaces.py`
- `tests/unit/tools/test_skill_usage_tracking.py`
- `tests/unit/tools/test_sanitize_claude_settings.py`

Policy/docs:

- `AgentCoordination/agent_surface_policy.json`
- `AgentCoordination/README.md`
- `Tools/agent_coordination/README.md`
- `AGENTS.md`
- `.agents/CODEX.md`
- `CLAUDE.md`
- `.gitignore`
- `.claude/settings.example.json`

Generated:

- `AgentCoordination/generated/agent_surface_inventory.json`
- `AgentCoordination/generated/skill_usage/summary.json`
- `AgentCoordination/generated/skill_usage/by_install/*.json`

Skills/protocols:

- `.claude/skills/**/SKILL.md`
- `.agents/skills/codex-starship-qa-observer/SKILL.md`
- `.agent/skills/**/SKILL.md`
- `Tracking/protocols/02c_parallel_debug.md`
- `Tracking/protocols/02d_parallel_deep_dive.md`
- `Projects/protocols/03b_parallel_projects.md`
- `Projects/protocols/07_extract_phase.md`

## Do Not Do

- Do not read `docs/_ignore/`.
- Do not delete user-local `.claude/settings.local.json`; only untrack it.
- Do not use `git reset --hard` for workflow rollback.
- Do not preserve retired Antigravity skills as aliases.
- Do not leave generated inventory stale after skill deletion.
- Do not turn `CLAUDE.md` into a bare one-line pointer; keep hard rules
  visible for Claude Code.
- Do not remove OpenCode `Task tool`, `subagent_type`, or `Write tool` wording
  solely based on the prior review claim.
