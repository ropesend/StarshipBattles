# Codex Agent Coordination Final Plan

Author: Codex
Date: 2026-04-29

## Purpose

This is the final coordination plan for aligning Starship Battles agent
instructions, skills, workflows, settings, and generated coordination artifacts
across Claude Code, OpenCode with DeepSeek, Codex, and Antigravity.

This plan supersedes Codex V1-V4 coordination plans.

## Final Decisions

### Source Of Truth

`AGENTS.md` is the shared source of truth for repo-wide agent behavior.

Adapter files may repeat short stable rules for reinforcement, but they must
not own independent volatile facts such as exact test counts, path prefixes, or
long command blocks.

### Agent Roles

- Claude Code: primary long-context workhorse for project/ticket workflows and
  historically most current repo workflow knowledge.
- Codex: workhorse for code changes, OpenAI/Codex docs, image generation, and
  Codex-specific repo skills.
- OpenCode with DeepSeek: workhorse for cheap high-token work, audits, and
  OpenCode-native flows.
- Antigravity: lower-priority adapter focused on tooling, browser/UI
  workflows, asset generation, and experimentation.

Antigravity should not drive the general coordination architecture until its
local path behavior and reliability are better understood.

### Skill Prefixes

All runtime skills must be prefixed by their agent/system surface:

- `claude-` for Claude Code skills.
- `anti-` for Antigravity skills.
- `ocode-` for OpenCode skills.
- `codex-` for Codex skills.

Unprefixed runtime skill names are not allowed after migration.

Future portable cross-agent skills may use `shared-`, but only with an explicit
manifest entry and validation proving every target tool can load the skill
safely.

### Prefix Migration

The prefix migration must be scripted, dry-run first, and applied atomically
after review. Do not manually rename skills one by one.

Planned files:

- `Tools/agent_coordination/rename_skills_with_prefixes.py`
- `Tools/agent_coordination/check_skill_prefixes.py`
- `tests/unit/tools/test_agent_skill_prefix_renamer.py`
- `tests/unit/tools/test_agent_skill_prefix_checker.py`
- `AgentCoordination/skill_rename_map.toml`
- `AgentCoordination/SKILL_RENAMES.md`

The renamer must:

1. Inventory all skill directories.
2. Generate an old-name to new-name map.
3. Dry-run first and emit a review report.
4. Rename skill directories.
5. Update `name:` frontmatter.
6. Rewrite skill references repo-wide, including:
   - `AGENTS.md`
   - `CLAUDE.md`
   - `.agents/CODEX.md`
   - `opencode.json` command keys and template text bodies
   - `.agents/skills/*/agents/openai.yaml`
   - `.claude/skills/**`
   - `.agent/skills/**`
   - `.opencode/skills/**`
   - `Projects/protocols/**`
   - `Tracking/protocols/**`
7. Update OpenCode allow/deny patterns before or in the same atomic write as
   directory renames.
8. Refuse names that violate Agent Skills naming rules.
9. Emit `AgentCoordination/SKILL_RENAMES.md` as an audit artifact only, not a
   compatibility shim.

Old skill names are not preserved as aliases.

The prefix checker is a small early enforcement script. Run it during the rename
phase and later fold it into the full validator. It must be runnable directly;
pre-commit integration is optional and must not be the only enforcement path.

### OpenCode Governance

OpenCode discovers project skills from `.opencode/skills/`, `.claude/skills/`,
and `.agents/skills/`. It does not currently document `.agent/skills/` as a
project skill surface.

After prefix migration:

- `ocode-*`: allowed by default.
- `claude-*`: denied by default unless explicitly marked OpenCode-compatible.
- `codex-*`: denied by default unless explicitly marked OpenCode-compatible.
- `anti-*`: denied defensively, even though OpenCode does not currently
  document `.agent/skills/` discovery.
- `shared-*`: allowed only if validated.

The defensive `anti-*` deny rule costs little and protects against future
OpenCode discovery changes.

### Generated Test Baseline

Exact test counts must be produced by tooling, not maintained manually by
agents.

Tracked file:

- `AgentCoordination/generated/test_baseline.json`

The sharded test runner should update this file automatically after successful
whole-suite runs using this policy:

- Failed, errored, interrupted, partial, or targeted runs never update the
  baseline.
- A normal successful whole-suite run updates counts only when the suite shape
  changes.
- When counts change, update `baseline_changed_at`.
- With `--refresh-baseline-timestamp`, a successful whole-suite run updates
  `verified_at` even when counts are unchanged.
- Agents should use `--refresh-baseline-timestamp` during final pre-commit
  verification when instructed.

Proposed schema:

```json
{
  "schema_version": 1,
  "command": "python Tools/test_sharded/test_sharded.py",
  "total": 0,
  "passed": 0,
  "failed": 0,
  "errors": 0,
  "skipped": 0,
  "baseline_changed_at": "",
  "verified_at": "",
  "git_sha": ""
}
```

Implementation note: the current sharded runner aggregates tests, failures, and
errors. It must explicitly add skipped-count parsing before writing this schema.

After this artifact exists, rewrite `AGENTS.md` and adapter docs to reference
`AgentCoordination/generated/test_baseline.json` instead of carrying exact test
counts in prose.

Agents working inside a project may still record temporary project/phase
baselines in project files. Those are local work baselines, not repo-wide truth.

### Generated Skill Inventory

Skill counts and surface facts must be generated, not maintained manually in
prose.

Tracked file:

- `AgentCoordination/generated/agent_surface_inventory.json`

Planned files:

- `Tools/agent_coordination/inventory_agent_surfaces.py`
- `tests/unit/tools/test_agent_surface_inventory.py`

The inventory schema must include `schema_version`.

The inventory should include:

- Surface path.
- Directory count.
- Skill names.
- Frontmatter name and description.
- Prefix compliance.
- Agent Skills spec compliance.
- Claude-specific frontmatter presence.
- OpenCode visibility.
- Stale references.

The inventory records observed facts. A later manifest or waiver file records
policy decisions and approved exceptions.

### Claude Settings Tracking

Preferred outcome: track a sanitized `.claude/settings.local.json` if it can be
made safe and stable.

Guardrails:

- Build a sanitizer/report first.
- Sanitization must be dry-run before it can apply changes.
- It must classify entries as:
  - `OK`: current repo-relative or accepted Starship Battles path.
  - `STALE_WARN`: old/nonexistent Starship Battles path. Allowed, but reported.
  - `EXTERNAL_REVIEW`: path outside known Starship Battles roots.
  - `DANGEROUS`: broad/destructive command permission needing manual approval.
- It must remove or reject secrets.
- It must not broaden permissions by converting absolute globs into overly
  broad relative globs.
- Nonsensical or nonexistent Starship Battles paths are not hard blockers for a
  permissions allowlist, but they should be reported as warnings.
- If tracking causes constant churn, stop tracking the real file and track an
  example or notes file instead.

Planned file:

- `Tools/agent_coordination/sanitize_claude_settings.py`

The sanitizer and validator must cover both:

- `.claude/settings.local.json`
- `.claude/settings.json`

If the real sanitized local file is tracked, the validator must fail on secrets,
unapproved external paths, and dangerous broad permissions. It should warn, not
fail, on stale Starship Battles paths.

### Skill Usage Tracking

Skill usage tracking should be script-driven, not hand-written by agents.

Use a per-repo-copy ID, not a machine ID, because multiple repo copies can exist
on one machine.

Planned local and generated structure:

```text
AgentCoordination/local/install_id.json
AgentCoordination/generated/skill_usage/by_install/<install_id>.json
AgentCoordination/generated/skill_usage/summary.json
```

Policy:

- `AgentCoordination/local/` is ignored.
- Each repo copy updates only its own `by_install/<install_id>.json` file.
- `summary.json` is generated by summing all per-install files.
- Agents call a script; they do not write JSON directly.
- Usage counters identify cleanup candidates only. They must never auto-delete
  skills.
- Implement usage counters after prefix migration so logs use final skill names.

Planned files:

- `Tools/agent_coordination/log_skill_usage.py`
- `Tools/agent_coordination/summarize_skill_usage.py`
- Tests under `tests/unit/tools/`

Example agent command:

```powershell
python Tools/agent_coordination/log_skill_usage.py --agent codex --skill codex-starship-project-system
```

Claude Code hooks may be used where officially supported. Other agents should
call the script explicitly or use transcript parsing if that proves reliable.

### Intentional Reinforcement Duplication

Short duplication of stable critical rules is allowed when it helps agents keep
important constraints in context.

Allowed reinforcement topics:

- Strict TDD.
- Read docs before coding.
- Keep docs and code consistent.
- Root-cause fixes only.
- Never read `docs/_ignore/`.
- Do not revert unrelated changes.

Required marker:

```html
<!-- agent-coordination:reinforcement tdd -->
```

Closed marker tags:

- `tdd`
- `docs-first`
- `code-doc-consistency`
- `root-cause`
- `no-ignore-folder`
- `no-revert-unrelated`

Validator policy:

- Marked stable reinforcement is allowed in adapter files.
- Reinforcement markers are validator policy, not instructions agents must see.
- Reinforcement markers should not appear in `SKILL.md` unless later approved.
- Unmarked duplication of 5 or more consecutive non-blank, non-trivial lines
  from `AGENTS.md` fails.
- Volatile facts fail outside generated artifacts or approved waivers.

Volatile facts include:

- Exact test counts in prose.
- Absolute Windows or WSL path prefixes outside approved settings warnings.
- `python -m unittest discover`.
- Removed paths such as `docs/bug_tracker.md`, `docs/lessons_learned.md`, and
  `assets/tools/ship_background_remover.py`.
- Hardcoded stale baselines such as `15405`.

### Stale Surfaces

After inventory and replacement artifacts exist, remove:

- `.agent/workflows/`
- `.agent/MIGRATION_PROGRESS.md`

These are stale. Git history is sufficient archive. Do not repair them in
place.

### CI And Local Enforcement

Add enforcement after the validator exists.

Preferred CI behavior:

- Run `validate_agent_surfaces.py` on PRs touching agent surfaces.
- Regenerate `agent_surface_inventory.json` and fail if the committed file is
  stale.
- Run the prefix checker on skill changes.

Keep CI provider details flexible unless the repository standardizes on one
system. GitHub Actions is acceptable if this repo uses GitHub, but the plan
should not require GitHub-specific assumptions before implementation.

Local enforcement:

- Provide direct commands for every checker.
- Optional pre-commit hooks may call those commands.
- Do not make correctness depend solely on local hooks being installed.

## Implementation Order

### Phase 1 - Inventory

Build or manually produce the initial surface inventory:

- Skills by surface.
- Existing prefixes.
- Cross-skill references.
- OpenCode-visible skills.
- Claude-specific frontmatter outside `.claude/skills/`.
- Stale workflow files.

No renames yet.

### Phase 2 - Generated Baseline And Inventory

Implement:

- Sharded runner baseline writing.
- `--refresh-baseline-timestamp`.
- Skipped-count parsing.
- Agent surface inventory generation.

Track:

- `AgentCoordination/generated/test_baseline.json`
- `AgentCoordination/generated/agent_surface_inventory.json`

Rewrite `AGENTS.md` and adapter docs to reference generated baseline/inventory
artifacts instead of exact counts.

### Phase 3 - Settings Sanitizer

Implement the Claude settings sanitizer as dry-run first.

Decide whether the real sanitized `.claude/settings.local.json` can be tracked.
If not, track an example/notes file and ignore the real local file.

### Phase 4 - Prefix Renamer Dry Run

Implement and run the prefix renamer dry-run.

Review:

- Proposed directory renames.
- Frontmatter changes.
- Reference rewrites.
- OpenCode config changes.
- `SKILL_RENAMES.md`.

Run the prefix-only checker against the dry-run output or generated map.

### Phase 5 - Atomic Prefix Rename

Apply the prefix rename in one reviewed change.

Do not leave the repository in a half-renamed state.

Run the prefix-only checker before and after the rename commit.

### Phase 6 - Usage Counter Prototype

Implement per-repo-copy install IDs and usage counter scripts after skill names
are final.

Track per-install counter files and summary if the format is stable enough for
review. Keep local install identity ignored.

### Phase 7 - Validator

Implement `Tools/agent_coordination/validate_agent_surfaces.py` with strict TDD.

Required checks:

- Prefix compliance.
- Agent Skills spec compliance.
- OpenCode visibility and permissions.
- Generated inventory freshness.
- Test baseline artifact validity.
- Reinforcement marker rules.
- Volatile fact checks.
- No stale workflow references.
- Claude settings policy for both settings files.
- Usage counter file shape if tracking is enabled.

### Phase 8 - CI And Local Hooks

Wire the validator and inventory freshness checks into CI if available.

Add optional pre-commit hook configuration or documented setup, but keep every
checker runnable directly from the command line.

### Phase 9 - Remove Stale Surfaces

After replacement artifacts exist and the prefix migration is stable, delete:

- `.agent/workflows/`
- `.agent/MIGRATION_PROGRESS.md`

## Final Policy Summary

1. `AGENTS.md` is the shared source of truth.
2. Runtime skills use `claude-`, `anti-`, `ocode-`, or `codex-` prefixes.
3. Prefix migration is scripted, dry-run first, and atomic.
4. Generated baseline and inventory files are tracked.
5. The test baseline updates automatically only on successful whole-suite runs
   according to the baseline policy above.
6. Sanitized Claude local settings may be tracked if path safety is acceptable.
7. Stale Starship Battles permission paths are warnings, not hard blockers.
8. Usage counters are per-repo-copy and script-driven.
9. Stable reinforcement duplication is allowed with closed markers.
10. Volatile facts belong in generated artifacts or one source of truth.
11. OpenCode gets a defensive `anti-*` deny rule.
12. Antigravity remains lower priority and focused on tooling/assets.
13. Stale `.agent` workflow/migration files should be removed after replacement
    artifacts exist.
14. Validator and inventory checks must be wired into CI/local commands after
    implementation.
