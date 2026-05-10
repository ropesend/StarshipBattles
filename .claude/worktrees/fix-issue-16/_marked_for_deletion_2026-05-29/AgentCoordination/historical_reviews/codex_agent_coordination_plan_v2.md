# Codex Agent Coordination Plan V2

Author: Codex
Date: 2026-04-29

## Purpose

Starship Battles is worked on by Claude Code, OpenCode with DeepSeek V4 Pro,
Codex, and Google Antigravity. The repository has several instruction, skill,
workflow, and configuration surfaces. The goal is to make those surfaces
consistent now and keep them consistent when future skills or agent docs change.

Version 2 incorporates review comments from Claude Code, OpenCode with DeepSeek
V4 Pro, and Antigravity, plus a fresh verification pass against local files and
current primary documentation.

## Source Links Used

- OpenCode rules: https://opencode.ai/docs/rules/
- OpenCode skills: https://opencode.ai/docs/skills/
- OpenCode permissions: https://opencode.ai/docs/permissions/
- Claude Code memory and imports: https://code.claude.com/docs/en/memory
- Claude Code skills: https://code.claude.com/docs/en/skills
- Claude Code settings: https://code.claude.com/docs/en/settings
- Codex AGENTS.md guidance: https://developers.openai.com/codex/guides/agents-md
- Codex skills: https://developers.openai.com/codex/skills
- Codex config reference: https://developers.openai.com/codex/config-reference
- Agent Skills specification: https://agentskills.io/specification
- Google Antigravity product context: https://blog.google/products-and-platforms/products/gemini/gemini-3/
- Google Antigravity skills codelab: https://codelabs.developers.google.com/getting-started-with-antigravity-skills
- Google Antigravity getting-started codelab: https://codelabs.developers.google.com/getting-started-google-antigravity

## Coordination File Naming

All files written under `AgentCoordination/` must identify the authoring agent
in the filename.

Use this convention:

```text
<agent-author>_<topic>.md
```

Examples:

- `codex_agent_coordination_plan.md`
- `codex_agent_coordination_plan_v2.md`
- `codex_agent_coordination_claim_responses.md`
- `claude_code_agent_coordination_comments.md`
- `opencode_deepseek_v4_pro_agent_coordination_comments.md`
- `antigravity_agent_coordination_comments.md`

## Core Decision

`AGENTS.md` is the shared source of truth for repo-wide agent behavior.

Tool-specific files are adapters. They may contain discovery mechanics,
permissions, local tool syntax, model/tool configuration, and tool-specific
workflow details. They must not restate shared rules, commands, architecture,
test baselines, or project policy except as short references back to
`AGENTS.md`.

This is the governing model:

- Shared repo policy lives in `AGENTS.md`.
- Long architecture, patterns, and conventions live in `docs/` as already
  required by `AGENTS.md`.
- Agent coordination governance lives in `AgentCoordination/`.
- Agent-specific files stay in their documented native locations.
- Skill consistency is enforced by a manifest and validator, not by trusting
  parallel directories to stay manually synchronized.

## Important Correction About Paths

Do not use absolute workspace prefixes as source-of-truth evidence.

The current Codex workspace is `C:\Dev2\StarshipBattles`, but other agents may
operate from different parent directories that still end in `StarshipBattles`.
That is acceptable. Validators must derive the repository root dynamically with
Git, not hardcode `C:\Dev2`, `C:\Developer`, or any other parent path.

The actual path-related bug is narrower:

- `.claude/settings.local.json` is tracked.
- It contains absolute machine-local paths.
- A local settings file should not be tracked at all.

Future validation should fail tracked local settings and absolute paths in
tracked local settings. It should not fail merely because an agent's parent
workspace directory differs.

## Agent Surface Model

| Surface | Role | V2 Policy |
| --- | --- | --- |
| `AGENTS.md` | Shared source of truth | Owns repo-wide rules, canonical commands, test baseline, architecture summary, and coordination expectations. |
| `CLAUDE.md` | Claude Code adapter | Use Claude Code import syntax to reference `AGENTS.md`; keep only Claude-specific behavior. Target 80-120 lines; hard cap 200 lines unless justified. |
| `.claude/settings.json` | Shared Claude project settings | May be tracked when project-wide. Keep hooks and shared Claude settings here. |
| `.claude/settings.local.json` | Local Claude user settings | Must be untracked and ignored. Do not validate specific path prefixes after it is untracked. |
| `.claude/skills/` | Claude Code skill adapter | Claude-native skills may use Claude Code extensions. Treat as canonical for the existing Claude/Antigravity shared skill family until a manifest says otherwise. |
| `opencode.json` | OpenCode adapter | `instructions: ["./AGENTS.md"]` and `permission.skill` are coordinated policy. Model/provider/compaction/autoupdate are operational config. |
| `.opencode/skills/` | OpenCode-native skills | Use for OpenCode-specific or OpenCode-approved shared skills. Current local skill is `audit-shrink`. |
| `.codex/config.toml` | Codex adapter config | Project-scoped Codex config. `project_doc_fallback_filenames = ["CLAUDE.md"]` is a configured fallback, not a Codex default. |
| `.agents/CODEX.md` | Codex adapter doc | Keep thin. It should reference `AGENTS.md` and list only Codex-specific routing and operating notes. |
| `.agents/skills/` | Codex repo skills | Codex scans this repo skill path. Keep Codex-specific skills prefixed `codex-` unless a manifest entry explicitly marks a shared skill compatible across tools. |
| `.agent/skills/` | Antigravity skill adapter in this repo | Treat as the current local Antigravity skill surface, but verify the current Antigravity client's expected path before adding tooling. Google codelabs show both `.agent/skills` and `.agents/skills` in different contexts. |
| `.agent/workflows/` | Legacy or unverified workflow surface | Current files contain stale commands and removed doc references. Default plan is to deprecate/delete or convert into skills after Antigravity path/workflow behavior is confirmed. |
| `Projects/*/WORKER.md` | Automated loop worker prompts | These are separate automation instruction surfaces. They are not general agent adapters, but the validator inventory should list them so they do not drift silently. |

## OpenCode Visibility Is Load-Bearing

OpenCode is the main correction in V2.

Per OpenCode documentation, project-local skills are discovered from:

- `.opencode/skills/`
- `.claude/skills/`
- `.agents/skills/`

OpenCode does not document `.agent/skills/` singular as a project skill search
location. This means `.claude/skills/` and `.agents/skills/` are not isolated
from OpenCode. The `permission.skill` rules in `opencode.json` are governed
infrastructure.

Policy:

1. Every skill in `.claude/skills/` or `.agents/skills/` must be either denied
   by `opencode.json` or recorded in the future manifest as intentionally
   OpenCode-compatible.
2. `opencode.json` may keep `* = allow`, but every non-OpenCode-compatible
   visible skill must be covered by a deny rule.
3. A validator must check this coverage whenever a visible skill is added,
   renamed, or removed.
4. OpenCode-native skills should live in `.opencode/skills/`.

Current local state:

- `.opencode/skills/` contains `audit-shrink`.
- `.claude/skills/` contains 32 skill directories.
- `.agents/skills/` contains 8 Codex-prefixed skill directories.
- Current deny patterns cover the observed `.claude/skills/` and
  `.agents/skills/` names.

## Antigravity Path Policy

Antigravity pathing must be handled carefully.

The local repo has:

- `.agent/skills/`
- `.agent/workflows/`
- `.agents/skills/` for Codex

The official Google sources checked during V2 are not fully consistent:

- The Antigravity skills codelab shows workspace skills under `.agent/skills/`.
- The Antigravity getting-started codelab discusses `.agents/skills`,
  `.agents/rules`, and `.agents/workflows`.

V2 policy:

1. Do not rename or collapse Antigravity surfaces until the current
   Antigravity client behavior is confirmed in this repository.
2. Treat `.agent/skills/` as the current local Antigravity adapter because that
   is what this repo already uses.
3. Treat `.agents/skills/` as Codex-owned in this repo unless the manifest later
   records shared Antigravity visibility.
4. Keep Codex-specific skill names prefixed `codex-` so accidental visibility in
   another tool is obvious.
5. Do not treat `.agent/workflows/` as a healthy current surface. The local
   files contain stale commands and removed references, and official Google
   examples point to `.agents/workflows` rather than `.agent/workflows`.

## Skill Strategy

Do not move all skills into a root `Skills/` or `.shared_skills/` directory as
the direct runtime location. The official tools discover skills from their
native locations; a root shared directory would not be enough by itself.

Instead, use a manifest-controlled adapter model:

1. A future `AgentCoordination/agent_surfaces.toml` records every instruction,
   settings, skill, and workflow surface.
2. Each skill entry declares:
   - `name`
   - `canonical_surface`
   - `mirrors`
   - `tool_compat`
   - `opencode_policy`
   - `frontmatter_extensions`
   - `mirror_policy`
   - `sync_notes`
3. Claude/Antigravity shared skills should initially use `.claude/skills/` as
   canonical and generated `.agent/skills/` mirrors, with Claude-specific
   frontmatter stripped or normalized when Antigravity requires it.
4. Codex-specific skills remain in `.agents/skills/` and keep the `codex-`
   prefix.
5. OpenCode-specific skills remain in `.opencode/skills/`.
6. Truly shared portable skills are allowed, but only after they satisfy the
   Agent Skills spec, have no incompatible tool-specific frontmatter, and have a
   manifest entry describing visibility in each tool.

## Current Drift To Fix

Verified local drift:

1. `CLAUDE.md` duplicates shared policy and still says `15405` tests, while
   `AGENTS.md` says `15477+`.
2. `.claude/settings.local.json` is tracked and contains absolute machine-local
   paths.
3. `.gitignore` does not ignore `.claude/settings.local.json`.
4. `.agent/workflows/run-tests.md` uses `python -m unittest discover`.
5. `.agent/workflows/resolve_bug.md` references missing
   `docs/bug_tracker.md` and `docs/lessons_learned.md`.
6. `.agent/workflows/generate_ship_theme.md` references missing
   `assets/tools/ship_background_remover.py`; the local tool is under
   `Tools/ship_background_remover/`.
7. `.agent/MIGRATION_PROGRESS.md` says 26 skills migrated, but the current
   local state is 32 `.claude/skills/` directories and 32 `.agent/skills/`
   directories.
8. `.claude/skills/` and `.agent/skills/` are not exact mirrors:
   - Claude-only names: `debug-parallel`, `deep-dive-parallel`,
     `proj-parallel`.
   - Antigravity-only names: `debug-sequential`, `deep-dive-sequential`,
     `proj-close`, `proj-sequential`.
9. Some `.agent/skills/` files still contain Claude-specific fields such as
   `disable-model-invocation` and `argument-hint`, so the claim that the
   Antigravity mirror has already stripped those fields is not true locally.
10. The original Codex plan counted 7 Codex skills; current local state has 8.

## Maintenance Protocol For Agent Skill Changes

Every new or changed skill must follow this sequence:

1. Classify the skill:
   - Shared portable
   - Claude-only
   - Antigravity-only
   - Codex-only
   - OpenCode-only
   - Shared between a defined subset
2. Update the manifest first once it exists.
3. Choose the canonical surface:
   - Claude/Antigravity shared family: `.claude/skills/` initially.
   - Codex-only: `.agents/skills/`, with `codex-` prefix.
   - OpenCode-only: `.opencode/skills/`.
   - Antigravity-only: `.agent/skills/`, pending path confirmation.
4. Update or generate all applicable adapter copies.
5. Update `opencode.json` allow/deny policy for every skill visible to
   OpenCode.
6. Update adapter docs if invocation or routing changes.
7. Run the future validator.
8. If no adapter update is needed for a tool, record the reason in the
   manifest.

## Future Validator

Implement this only in a later task using strict TDD.

Proposed files:

- `Tools/agent_coordination/validate_agent_surfaces.py`
- `tests/unit/tools/test_agent_coordination_validator.py`
- `AgentCoordination/agent_surfaces.toml`

Use standard-library Python where possible. TOML is preferred for the manifest
because Python 3.13 includes `tomllib`, and TOML supports comments. If writing
the manifest also needs stdlib-only output, keep generation simple or edit the
TOML manually.

Required validator checks:

- `AGENTS.md` exists and is the only shared source-of-truth file.
- `CLAUDE.md` imports or references `AGENTS.md`, stays under the configured
  adapter size threshold, and does not duplicate canonical test baselines or
  command blocks.
- `.claude/settings.local.json` is not tracked.
- Tracked local settings files do not contain absolute machine-specific paths.
- OpenCode-visible skills in `.claude/skills/` and `.agents/skills/` are
  covered by `opencode.json` allow/deny policy or manifest compatibility.
- Skill `name` matches its directory.
- Skill names match `^[a-z0-9]+(-[a-z0-9]+)*$` and stay under 64 characters.
- Skill descriptions exist and stay within the Agent Skills spec limit.
- Claude-specific frontmatter does not appear in non-Claude adapters unless the
  manifest explicitly allows it.
- Codex-specific repo skills under `.agents/skills/` keep the `codex-` prefix
  unless a manifest entry marks them shared.
- Mirror pairs satisfy the configured mirror policy after frontmatter
  normalization.
- `.agent/workflows/` is either absent, explicitly documented as active, or has
  no stale references.
- Known stale strings such as `15405`, `python -m unittest discover`,
  `docs/bug_tracker.md`, `docs/lessons_learned.md`, and
  `assets/tools/ship_background_remover.py` fail outside historical archives
  unless explicitly waived.

Suggested validator outputs:

- Human-readable summary to stdout.
- Optional JSON report under `Reviews/results/{DATE}_AGENT_SURFACES/`.

## Implementation Phases

### Phase 0 - Review V2

Use this V2 plan and `codex_agent_coordination_claim_responses.md` as the basis
for the next agent review round.

### Phase 1 - Manual Cleanup

Do this before writing the validator:

1. Confirm current Antigravity path behavior with the actual Antigravity client.
2. Trim `CLAUDE.md` into a Claude adapter that imports `AGENTS.md`.
3. Replace duplicated test baseline references in `CLAUDE.md`.
4. Add `/.claude/settings.local.json` to `.gitignore`.
5. Untrack `.claude/settings.local.json`.
6. Decide whether `.agent/workflows/` should be deleted, replaced by
   `.agents/workflows/`, or converted into skills.
7. Replace `.agent/MIGRATION_PROGRESS.md` with a living manifest once the
   manifest exists.
8. Add `AgentCoordination/README.md` or a shorter skill-update protocol after
   the team agrees on V2.

### Phase 2 - Manifest And Sync Design

Create `AgentCoordination/agent_surfaces.toml` and define the skill mirror
policy before writing sync code. Start with inventory only, then add generation
or normalization rules after the inventory matches reality.

### Phase 3 - Validator With TDD

Write failing tests first, then implement
`Tools/agent_coordination/validate_agent_surfaces.py`.

Minimum test cases:

- Tracked `.claude/settings.local.json` fails.
- `15405` duplicated in `CLAUDE.md` fails.
- New `.claude/skills/` skill without OpenCode policy fails.
- New `.agents/skills/` skill without OpenCode policy fails.
- Invalid skill name fails.
- Skill name mismatch with directory fails.
- Description over 1024 characters fails.
- Claude-only frontmatter in non-Claude adapter fails unless waived.
- Stale `.agent/workflows/` references fail.
- Mirror policy mismatch fails.

### Phase 4 - Cadence

After the validator is stable:

- Run it manually before committing agent-surface changes.
- Add an opt-in local pre-commit hook recipe.
- Add CI for PRs touching `AGENTS.md`, `CLAUDE.md`, `opencode.json`,
  `.codex/config.toml`, `.agents/CODEX.md`, any `**/SKILL.md`, and agent
  workflow files.
- Add a weekly or release-gate sweep that archives validator output under
  `Reviews/results/`.

## Remaining Questions For Reviewers

1. Which Antigravity path does the current installed client actually scan in
   this repo: `.agent/skills`, `.agents/skills`, or both?
2. Should `.agent/workflows/` be deleted, migrated to `.agents/workflows/`, or
   converted into skills?
3. Should `.claude/skills/` remain the initial canonical surface for the
   Claude/Antigravity shared skill family, or should a neutral generated source
   directory be introduced later?
4. Which existing skills, if any, should become intentionally OpenCode-compatible
   instead of denied?
5. Should validator output be archived on every run or only on scheduled/release
   sweeps?
