# Multi-Agent Coordination Refinement Plan

Status: Draft for cross-agent review
Date: 2026-05-02
Author: Codex

## Purpose

This plan refines the existing Starship Battles multi-agent setup after a
read-only review of the current Claude Code, Codex, OpenCode, and Antigravity
surfaces.

The goal is not to replace `AgentCoordination/codex_agent_coordination_plan_final.md`.
It is a follow-up cleanup plan for issues discovered after the prefix migration
and validator work had already landed.

## Confirmed Decisions

These decisions come from user review of the initial findings:

1. `CLAUDE.md` should remain a thin adapter, but it must still carry enough
   critical instruction text because Claude Code reliably loads `CLAUDE.md`
   at startup while follow-on files may be less consistently read by the
   model during work.
2. `/anti-*` references outside Antigravity surfaces were migration errors.
3. Antigravity should be limited to tooling and asset-processing work, not
   general project, ticket, QA, or debugging workflows.
4. All skill usage should be logged. Claude Code should use hooks where
   available. Codex, OpenCode, and Antigravity should explicitly run the
   logging script at skill start.
5. `.claude/settings.local.json` should no longer be tracked. Shared safe
   settings should be represented by a tracked example or recommended file.
6. Rollback behavior in parallel workflows should adopt the safer merge
   recovery policy described below.

## Current Strengths To Preserve

- `AGENTS.md` is the neutral shared entry point.
- Runtime skill names are prefixed by surface: `claude-`, `codex-`,
  `ocode-`, and `anti-`.
- `Tools/agent_coordination/validate_agent_surfaces.py` currently passes.
- OpenCode skill permissions use the correct last-match-wins ordering:
  `*` first, then specific deny and allow patterns.
- Generated inventory and test baseline artifacts avoid hardcoded volatile
  facts in prose.
- Claude Code already has hooks for automatic `claude-*` usage logging.

## Problems To Fix

### 1. Claude Adapter Drift

`CLAUDE.md` still contains stale copied facts from older architecture docs:

- Pattern count and pattern descriptions are stale.
- Layer dependency summaries are stale.
- `ApplicationContext` service count is stale.

Because Claude Code loads `CLAUDE.md` at startup, stale facts here are more
dangerous than stale facts in secondary docs.

### 2. Wrong `anti-*` References

Several `.claude/skills` files and at least one Codex skill still reference
`/anti-*` commands or `.claude/skills/anti-*` paths. These are migration
errors, not intended handoffs.

This creates three failure modes:

- Claude may suggest a command that does not match its own skill surface.
- Codex may try to read nonexistent skill paths.
- The prefix system looks clean to the validator while user-facing examples
  still point at the wrong agent.

### 3. Antigravity Surface Is Too Broad

The policy says Antigravity is lower-priority and focused on tooling/assets,
but the current `.agent/skills` surface includes broad project, ticket,
debugging, QA, and triage workflows.

That broad surface invites drift because most of those workflows mirror Claude
or historical Antigravity behavior rather than current intended ownership.

### 4. Skill Usage Logging Is Not Fully Atomic

Current behavior:

- `log_skill_usage.py` updates the per-install counter.
- `summarize_skill_usage.py` must be run separately to update the aggregate
  summary.

Desired behavior:

- Once a skill usage logging script is triggered, all generated usage artifacts
  update together.

### 5. Tracked Claude Local Settings Are Machine-Specific

`.claude/settings.local.json` is tracked but contains machine-local paths and
per-session permissions. On a multi-machine, single-developer repository, that
file is a churn source and can encode incorrect paths for another checkout.

It also contains broad permissions that may be acceptable in one trusted local
setup but are not appropriate as shared repo policy.

### 6. Parallel Rollback Instructions Are Too Destructive

Several parallel protocols say to use `git reset --hard HEAD~1` after a failed
post-merge test run.

That is only safe when all of these are true:

- The current checkout is a disposable worker worktree.
- The worktree is clean before the merge.
- The merge commit is definitely the current `HEAD`.
- No unrelated local edits, generated artifacts, usage logs, or user changes
  exist in the worktree.

In the main checkout or a dirty worktree, this can destroy unrelated work.

## Target End State

### `CLAUDE.md`

Keep it under roughly 200 lines and make it a bootloader:

- Restate the non-negotiable rules in concise form.
- Point to `AGENTS.md` as the shared policy.
- Point to `docs/README.md` for documentation reading order.
- Point to `.claude/skills` for Claude-specific workflows.
- Avoid volatile architecture summaries, exact counts, long command blocks,
  and copied sections that drift.

Do not rely only on a bare "read `AGENTS.md`" instruction. Keep the rules that
Claude must never miss directly in `CLAUDE.md`.

### Agent Skill Ownership

- Claude owns broad project, ticket, QA, review, and parallel workflows.
- Codex owns Codex-specific repo-local skills in `.agents/skills`.
- OpenCode owns OpenCode-native high-token audit workflows.
- Antigravity owns only tooling/assets/browser/UI-adjacent workflows that the
  user explicitly wants to run in Antigravity.

### Skill Usage Logging

Every skill invocation logs usage.

- Claude: automatic hooks for `claude-*`.
- Codex: run `python Tools/agent_coordination/log_skill_usage.py --agent codex --skill <skill>`.
- OpenCode: run `python Tools/agent_coordination/log_skill_usage.py --agent ocode --skill <skill>`.
- Antigravity: run `python Tools/agent_coordination/log_skill_usage.py --agent anti --skill <skill>`.

`log_skill_usage.py` should update both the per-install file and
`summary.json` in one command.

### Claude Settings

- Track `.claude/settings.json` if it contains shared hooks and safe common
  permissions.
- Stop tracking `.claude/settings.local.json`.
- Add `.claude/settings.local.json` to `.gitignore`.
- Optionally add `.claude/settings.example.json` with conservative,
  repo-relative examples.

### Rollback Policy

Replace `git reset --hard HEAD~1` instructions with a guarded rollback
contract:

1. Before any merge, require `git status --short` to be clean.
2. Record `PRE_MERGE_SHA=$(git rev-parse HEAD)`.
3. Merge the worker branch.
4. If a conflict happens before the merge commit exists, use
   `git merge --abort`.
5. If tests fail after a local merge commit:
   - Confirm the worktree is clean.
   - Confirm `HEAD` is the merge commit just created by the protocol.
   - Confirm the merge has not been pushed or shared.
   - Reset to the recorded SHA, not positional `HEAD~1`.
6. If any condition is unclear, stop and ask the user.
7. If the merge was shared or pushed, use a normal revert strategy instead of
   history rewriting.

## Implementation Plan

### Phase 1: Add Guard Rails With Tests

Add tests before implementation for these new validator behaviors:

- A Claude skill that references `/anti-*` fails unless explicitly allowlisted.
- A Codex skill that references a nonexistent skill path fails.
- `.claude/settings.local.json` being tracked fails after the policy change.
- Usage `summary.json` must match all per-install counters after any logging
  operation.
- Antigravity skill inventory must match an explicit allowlist or policy
  manifest.

Recommended new policy artifact:

```text
AgentCoordination/agent_surface_policy.json
```

Suggested contents:

- Allowed skill prefixes per surface.
- Allowed skill names or skill categories per surface.
- Allowed cross-agent command references, default deny.
- Antigravity allowed-scope list.

This avoids hardcoding all policy into validator source.

### Phase 2: Fix Usage Logging Atomically

Change `log_skill_usage.py` so one invocation:

1. Ensures the local install ID exists.
2. Updates the per-install counter.
3. Rebuilds `summary.json`.
4. Writes both generated artifacts deterministically.

Tests should cover:

- First invocation creates install ID, per-install file, and summary.
- Repeated invocation increments both files.
- Malformed existing counter file is handled consistently with current
  summarizer behavior.
- Invalid agent or skill name still exits nonzero and writes nothing.

Update `AGENTS.md`, `.agents/CODEX.md`, `CLAUDE.md`, and
`Tools/agent_coordination/README.md` so the logging instruction is one command,
not a two-step mental model.

### Phase 3: Convert `CLAUDE.md` To A Thin Bootloader

Rewrite `CLAUDE.md` to keep only:

- Claude-specific role and collaboration expectations.
- The non-negotiable rules.
- The docs-first reading order.
- The canonical command list by reference to `AGENTS.md`.
- Skill usage logging and hook behavior.
- Subagent report convention, if still Claude-specific.

Remove copied volatile architecture summaries from `CLAUDE.md`. Let `docs/`
own architecture and let `AGENTS.md` own shared quick reference.

Run validator after the rewrite to make sure reinforcement markers still cover
intentional duplication.

### Phase 4: Repair Prefix Drift

Rewrite wrong references:

- In `.claude/skills`, replace `/anti-*` examples with matching `/claude-*`
  names when a Claude skill exists.
- In Claude project protocols, replace `/anti-proj-start` style references
  with the correct owning command or neutral text.
- In Codex skills, remove references to `.claude/skills/anti-*` paths. Prefer
  protocol files or Codex-owned skill text.

Add validator coverage so this does not regress.

Important exception:

- The word "anti" in ordinary prose, such as "anti-pattern" or
  "anti-reversion", is not a skill prefix and must not be flagged.

### Phase 5: Narrow Antigravity Surface

Decide the Antigravity allowlist before deleting anything.

Candidate keep list:

- `anti-validate-designs`
- Asset-processing skills that are actively useful in Antigravity.
- Browser/UI tooling skills only if Antigravity is actually used for those.

Candidate retire list:

- `anti-proj-*`
- `anti-ticket-*`
- `anti-qa-*`
- `anti-triage-to-proj`
- `anti-debug-sequential`
- `anti-deep-dive-sequential`
- `anti-fix-crash`

After the allowlist is approved:

1. Delete retired `.agent/skills` directories.
2. Regenerate `AgentCoordination/generated/agent_surface_inventory.json`.
3. Update `AgentCoordination/SKILL_RENAMES.md` or replace it with a current
   retirement report.
4. Run validator and focused tool tests.

### Phase 6: Stop Tracking Claude Local Settings

Implementation steps:

1. Add `.claude/settings.local.json` to `.gitignore`.
2. Remove it from the git index while preserving the user's local file.
3. Add a tracked `.claude/settings.example.json` or
   `.claude/settings.recommended.json`.
4. Update `sanitize_claude_settings.py` and validator policy:
   - Shared files are enforced.
   - Ignored local files are either skipped by default or reported only under
     an explicit local audit flag.
5. Update `AgentCoordination/README.md` and `Tools/agent_coordination/README.md`.

Question for reviewers:

- Should local settings be ignored completely by CI, or should the validator
  support a separate local-only mode for developer hygiene?

### Phase 7: Harden Rollback Protocols

Update all parallel workflow docs and skills that currently recommend
positional hard reset after a failed merge.

Files to audit include:

- `Tracking/protocols/02c_parallel_debug.md`
- `Tracking/protocols/02d_parallel_deep_dive.md`
- `Projects/protocols/03b_parallel_projects.md`
- `.claude/skills/claude-debug-parallel/SKILL.md`
- `.claude/skills/claude-deep-dive-parallel/SKILL.md`
- `.claude/skills/claude-proj-parallel/SKILL.md`

Replacement text should require:

- Clean worktree precondition.
- Recorded pre-merge SHA.
- Reset only to the recorded SHA.
- Stop-and-ask behavior when the preconditions are not satisfied.
- Revert instead of reset when history has been shared.

### Phase 8: Review OpenCode Audit Skill Executability

The OpenCode audit skill currently describes a Claude-like `Task tool`,
`subagent_type`, and `Write tool` workflow.

Review and decide:

- If OpenCode supports the equivalent workflow, rewrite terms to OpenCode's
  native interface.
- If not, make the OpenCode skill sequential or explicitly require a human to
  launch the subreviews.

This is a lower-priority cleanup than prefix drift and rollback safety.

## Validation Commands

Run these after each implementation phase that touches agent surfaces:

```powershell
python Tools/agent_coordination/check_skill_prefixes.py
python Tools/agent_coordination/inventory_agent_surfaces.py
python Tools/agent_coordination/validate_agent_surfaces.py
python -m pytest tests/unit/tools -q
```

When skill directories change, commit the regenerated inventory in the same
change.

## Open Questions For Reviewer Agents

1. Should `CLAUDE.md` import `AGENTS.md` with explicit import syntax, or should
   it duplicate only the hard rules and point to `AGENTS.md` without import?
2. What exact Antigravity skills should remain after narrowing to
   tooling/assets?
3. Should `agent_surface_policy.json` be introduced, or should the validator
   keep policy embedded in Python tests and constants?
4. Should ignored `.claude/settings.local.json` be skipped by validator by
   default, or audited locally with a non-CI command?
5. For rollback, should the protocols prefer `git revert` even for local merge
   commits, accepting a noisier history to avoid history rewriting entirely?

## Recommended Initial PR Scope

Keep the first implementation PR small:

1. Make usage logging atomic.
2. Add validator checks for wrong cross-agent skill references.
3. Fix the existing wrong `/anti-*` and nonexistent skill-path references.

Then follow with separate PRs for:

- `CLAUDE.md` thinning.
- Antigravity surface retirement.
- Local settings tracking removal.
- Rollback protocol hardening.

This sequencing reduces risk because the first PR adds automated guard rails
before larger content deletions.
