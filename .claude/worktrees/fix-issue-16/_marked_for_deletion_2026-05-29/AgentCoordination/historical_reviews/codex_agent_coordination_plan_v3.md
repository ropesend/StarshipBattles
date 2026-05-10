# Codex Agent Coordination Plan V3

Author: Codex
Date: 2026-04-29

## Purpose

Version 3 incorporates:

- Claude Code, OpenCode with DeepSeek V4 Pro, and Antigravity V2 review
  comments.
- The user's notes in `AgentCoordination/user_response.md`.
- A fresh local verification pass against the current Starship Battles repo.
- Current official documentation for OpenCode, Claude Code, Codex, Agent
  Skills, and Google Antigravity codelabs.

V3 keeps the central policy from V2: `AGENTS.md` is the shared source of truth,
and tool-specific surfaces are adapters. V3 changes the implementation strategy
around prefixes, automation, duplication, usage tracking, Antigravity priority,
and local settings.

## Sources Checked

- OpenCode skills: https://opencode.ai/docs/skills/
- OpenCode permissions: https://opencode.ai/docs/permissions/
- Claude Code settings: https://code.claude.com/docs/en/settings
- Claude Code skills: https://code.claude.com/docs/en/skills
- Codex skills: https://developers.openai.com/codex/skills
- Codex AGENTS.md guidance: https://developers.openai.com/codex/guides/agents-md
- Agent Skills specification: https://agentskills.io/specification
- Google Antigravity skills codelab: https://codelabs.developers.google.com/getting-started-with-antigravity-skills
- Google Antigravity getting-started codelab: https://codelabs.developers.google.com/getting-started-google-antigravity

## Verified Local State

Current skill counts must be generated in the future, but the verified snapshot
for this review is:

- `.claude/skills/`: 32 directories.
- `.agent/skills/`: 33 directories.
- `.agents/skills/`: 8 directories.
- `.opencode/skills/`: 1 directory.
- `.agent/skills/` contains 19 `SKILL.md` files with Claude-specific fields
  such as `disable-model-invocation` or `argument-hint`.
- `.claude/skills/` and `.agent/skills/` are not mirrors:
  - Claude-only: `debug-parallel`, `deep-dive-parallel`, `proj-parallel`.
  - Antigravity-only: `debug-sequential`, `deep-dive-sequential`,
    `proj-close`, `proj-sequential`.
- `.agent/workflows/` contains stale workflow files.
- `.agent/MIGRATION_PROGRESS.md` is stale and says 26 skills migrated.
- `.claude/settings.local.json` is tracked and contains absolute paths.
- `Tools/test_sharded/test_sharded.py` already aggregates total test results
  and writes `.test_durations.json`; it can be extended later to write a stable
  test baseline artifact.

## Pushback

### Do Not Track `.claude/settings.local.json`

I recommend against tracking `.claude/settings.local.json`, even for a solo
developer.

The reason is not team coordination. The reason is that Claude Code documents
`.claude/settings.local.json` as personal project settings that are not checked
in, and says Claude Code configures Git to ignore it when created. The local
file currently contains absolute machine paths and broad command permissions.
That creates stale path churn and accidental leak risk if the repo is ever
shared.

Better policy:

- Track `.claude/settings.json` for project-shared Claude behavior.
- Keep `.claude/settings.local.json` untracked.
- Add a tracked `AgentCoordination/claude_local_settings_notes.md` or
  `.claude/settings.local.example.json` later if you want a recoverable local
  setup recipe.
- If you still decide to track it, require no absolute paths and no secrets.

### Do Not Let Usage Counters Auto-Delete Skills

Skill usage counters are useful, but they should only flag candidates for human
review.

Counters will be incomplete across agents because each system exposes skill
loading differently. Some invocations are implicit, some are manual, and some
systems may not expose hooks. An unused counter can mean "not instrumented" or
"not used recently," not necessarily "safe to delete."

Better policy:

- Track usage in an ignored local JSONL file.
- Use usage age as one signal in a skill audit.
- Never auto-purge skills based only on counters.

### Do Not Duplicate Volatile Facts

I agree with deliberate reinforcement of stable rules such as strict TDD,
documentation-first work, root-cause fixes, and "do not read `docs/_ignore/`."

I do not agree with duplicating volatile facts such as exact test counts,
current stale path strings, or long command blocks across adapter files. Those
are exactly the facts that drift.

Better policy:

- Allow marked reinforcement blocks for stable rules.
- Keep volatile values in generated artifacts or `AGENTS.md`.
- Validator fails unmarked duplication of volatile values.

### Do Not Manually Mass-Rename Skills

Universal prefixes are reasonable, but manually renaming all skills first is
too risky. The repo has cross-skill references, OpenCode deny rules, adapter
docs, and skill bodies that refer to old names.

Better policy:

- Inventory first.
- Generate a rename map.
- Run a dry-run rewrite report.
- Apply the rename in one atomic implementation task with tests/validator.

## V3 Decisions

### 1. Source Of Truth

`AGENTS.md` remains the shared source of truth for repo-wide agent behavior.

Adapters may restate short, stable reinforcement blocks, but must not own
independent versions of volatile facts.

### 2. Agent Roles

Current practical role split:

- Claude Code: primary workhorse for long-context planning, ticket/project
  workflows, and historically most current skill content.
- Codex: workhorse for code, OpenAI/Codex integration, image generation, and
  Codex-specific repo skills.
- OpenCode with DeepSeek V4 Pro: workhorse for cheap high-token work and audits,
  governed through `opencode.json`.
- Antigravity: lower-priority adapter, mainly for tooling, asset generation,
  UI/browser-oriented workflows, and experimentation.

Antigravity should not drive the general coordination architecture until its
path behavior and reliability are better understood.

### 3. Prefix Policy

Adopt agent/system prefixes for all runtime skills:

- Claude Code: `claude-`
- Antigravity: `anti-`
- OpenCode with DeepSeek: `deep-` for now, pending the question below.
- Codex: `codex-`

This means the current unprefixed skills should eventually be renamed:

- `.claude/skills/proj-start` -> `.claude/skills/claude-proj-start`
- `.agent/skills/proj-start` -> `.agent/skills/anti-proj-start`
- `.opencode/skills/audit-shrink` -> `.opencode/skills/deep-audit-shrink`
- Existing `.agents/skills/codex-*` already conform.

Reserved exception:

- Future cross-agent portable skills may use `shared-` only if a manifest entry
  explicitly marks them portable and every target agent can load them safely.
- Do not use unprefixed runtime skill names.

### 4. Prefix Migration Approach

Do not hand-edit this migration.

Future implementation task:

- `Tools/agent_coordination/rename_skills_with_prefixes.py`
- `tests/unit/tools/test_agent_skill_prefix_renamer.py`
- `AgentCoordination/skill_rename_map.toml`
- `AgentCoordination/SKILL_RENAMES.md`

The renamer must:

1. Inventory all skill directories.
2. Build an old-name to new-name map.
3. Rename directories.
4. Update `name:` frontmatter.
5. Update slash-command references in skill bodies and adapter docs.
6. Update `opencode.json` skill permissions and command names.
7. Update `AGENTS.md` references to renamed skills.
8. Emit a human-readable rename guide.
9. Refuse to proceed if a rename would exceed Agent Skills name length or
   violate the name regex.

The migration should be one implementation task, not a series of partial
renames.

### 5. OpenCode Governance

OpenCode discovers skills from `.opencode/skills/`, `.claude/skills/`, and
`.agents/skills/`. It does not document `.agent/skills/`.

After prefixes, the OpenCode policy should become simpler:

- `deep-*`: allow by default.
- `claude-*`: deny by default unless explicitly marked OpenCode-compatible.
- `codex-*`: deny by default unless explicitly marked OpenCode-compatible.
- `shared-*`: allow only when validated.

Because OpenCode does not discover `.agent/skills/`, `anti-*` does not need an
OpenCode deny rule unless later testing proves OpenCode can see that surface.

### 6. Antigravity Policy

Use `.agent/skills/` as the current Antigravity surface in this repo because the
local repo already uses it and the Antigravity skills codelab documents
workspace skills at `.agent/skills/`.

However, keep path verification open because another Google codelab discusses
`.agents/skills`, `.agents/rules`, and `.agents/workflows`.

V3 priority:

- Do not invest heavily in Antigravity general-workflow parity.
- Keep or create only `anti-*` skills that support tooling, assets, browser/UI
  workflows, or other tasks where Antigravity is useful.
- Delete stale `.agent/workflows/` unless the next Antigravity-specific review
  produces a concrete reason to keep or migrate them.

### 7. Intentional Reinforcement Duplication

Adapters may include short reinforcement blocks for stable critical rules.

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

Validator behavior:

- Marked stable reinforcement is allowed.
- Duplicated volatile facts fail.
- Unmarked long duplication warns or fails depending on severity.

This keeps the memory benefit without letting stale details spread.

### 8. Automated Test Baseline

Exact test counts should not be maintained manually in human prose.

Future implementation task:

- Extend `Tools/test_sharded/test_sharded.py` to write a JSON summary after a
  full green run.
- Proposed path: `AgentCoordination/generated/test_baseline.json`.
- Proposed schema:

```json
{
  "total": 0,
  "passed": 0,
  "failed": 0,
  "errors": 0,
  "skipped": 0,
  "wall_time_seconds": 0.0,
  "shards": 0,
  "git_sha": "",
  "generated_at": ""
}
```

Do not let the sharded runner rewrite Markdown files. `AGENTS.md` and adapters
should point to the generated baseline file.

Open question: whether this generated file should be tracked. My default is
"tracked only after intentional full-suite baseline updates"; otherwise it
becomes local noise like `.test_durations.json`.

### 9. Automated Skill Inventory

Skill counts should be generated, not written in prose.

Future implementation task:

- `Tools/agent_coordination/inventory_agent_surfaces.py`
- `tests/unit/tools/test_agent_surface_inventory.py`
- Output: `AgentCoordination/generated/agent_surface_inventory.json`

The inventory should include:

- Surface path.
- Directory count.
- Skill names.
- Frontmatter name/description.
- Prefix compliance.
- Agent Skills spec compliance.
- Claude-specific frontmatter presence.
- OpenCode visibility.
- Stale references.

The manifest should record policy and exceptions; inventory should record
observed facts. Do not use a manual manifest for facts that can be derived.

### 10. Skill Usage Tracking

Add skill usage tracking as a research and prototype task, not as part of the
first cleanup.

Default design:

- Local ignored file: `AgentCoordination/local/skill_usage.jsonl`.
- Append-only records:

```json
{"timestamp":"","agent":"","skill":"","surface":"","source":"manual-or-hook"}
```

Rules:

- Usage logs are local operational telemetry and should not be tracked by
  default.
- Agents should be instructed to append when they explicitly invoke a skill.
- Hooks may be used only where a tool officially supports them.
- A future audit reports "unused or unlogged" skills, not "delete these."

### 11. `.agent/workflows/` And Migration Snapshot

`.agent/workflows/` is stale. `.agent/MIGRATION_PROGRESS.md` is stale.

V3 recommendation:

- Delete `.agent/workflows/` in the cleanup phase unless Antigravity provides a
  current, concrete reason to keep it.
- Delete `.agent/MIGRATION_PROGRESS.md` after the generated inventory and
  rename map exist.
- Do not repair stale workflows in place.

Git history is enough archive for these files.

### 12. `.claude/settings.local.json`

V3 recommendation remains: do not track `.claude/settings.local.json`.

Implementation:

- Add `/.claude/settings.local.json` to `.gitignore`.
- Move project-shared settings into `.claude/settings.json` when appropriate.
- Add a documented setup example if needed.
- Remove absolute paths from any tracked Claude settings.

If the user chooses to track local settings anyway, the validator must enforce:

- No absolute paths.
- No secrets.
- No machine-specific external directories.
- Explicit acknowledgment in `AgentCoordination/README.md`.

## V3 Implementation Phases

### Phase 0 - Confirm Open Questions

Answer the open questions at the end of this document.

### Phase 1 - Inventory Before Change

Build or manually produce a one-time inventory report:

- Current skills and prefixes.
- Cross-skill references.
- OpenCode-visible skills.
- Stale workflow files.
- Claude-specific frontmatter outside `.claude/skills/`.

No renames yet.

### Phase 2 - Remove Known Stale Surfaces

After user confirmation:

- Delete `.agent/workflows/`.
- Add `/.claude/settings.local.json` to `.gitignore`.
- Untrack `.claude/settings.local.json`.
- Remove or supersede `.agent/MIGRATION_PROGRESS.md` after inventory exists.

### Phase 3 - Prefix Rename

Implement the prefix renamer with strict TDD.

Run the renamer once, review the diff carefully, then update docs and adapter
references in the same change.

### Phase 4 - Generated Counts

Implement:

- Test baseline JSON output from the sharded runner.
- Agent surface inventory JSON output.

Update `AGENTS.md`, `CLAUDE.md`, `.agents/CODEX.md`, and `opencode.json`
references to avoid embedded exact counts.

### Phase 5 - Validator

Implement `Tools/agent_coordination/validate_agent_surfaces.py` with tests.

Required checks:

- Prefix compliance.
- Agent Skills spec compliance.
- OpenCode visibility and permissions.
- Generated inventory freshness.
- Test baseline artifact freshness.
- Marked reinforcement duplication only.
- No stale workflow references.
- No tracked local settings unless explicitly allowed.

### Phase 6 - Usage Tracking Prototype

Research per-agent support and prototype a local JSONL tracker.

Do not block the prefix/validator work on this.

## Questions For User

1. Do you want the OpenCode prefix to be `deep-` as stated, or would
   `opencode-` be more stable? My recommendation is `opencode-` because
   DeepSeek is the current model/provider while OpenCode is the tool surface.
   If your mental model is firmly "DeepSeek agent," `deep-` is acceptable.
2. Should the generated test baseline file be tracked after intentional full
   green runs, or always ignored as local output?
3. Should the skill usage log be local-only, or do you want a tracked aggregate
   summary such as "last reviewed usage" without raw per-run records?
4. Are you comfortable breaking old slash skill names in one atomic rename, or
   do you want a temporary `SKILL_RENAMES.md` cheat sheet to preserve the old
   names mentally during transition?
5. Should Antigravity keep any non-asset/non-tooling skills, or should `anti-*`
   be limited to tooling, browser/UI validation, and asset-generation workflows?

## Final V3 Recommendation

Adopt V3 with these priorities:

1. Inventory first.
2. Delete stale workflows and untrack local settings after confirmation.
3. Prefix all runtime skills with a scripted atomic rename.
4. Replace manual counts with generated artifacts.
5. Allow only marked stable reinforcement duplication.
6. Build the validator after the rename and generated inventory decisions are
   settled.
7. Treat skill usage counters as advisory telemetry, not deletion authority.
