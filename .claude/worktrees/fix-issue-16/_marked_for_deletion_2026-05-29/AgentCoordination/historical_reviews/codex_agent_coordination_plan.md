# Codex Agent Coordination Plan

Author: Codex
Date: 2026-04-29

## Purpose

Starship Battles is now being worked on by multiple agent systems: Claude Code,
OpenCode with DeepSeek V4 Pro, Codex, and Google Antigravity. Each system has
its own instruction, skill, workflow, or configuration surface. The goal of this
coordination plan is to make those surfaces consistent now and keep them
consistent over time.

The intended model is simple:

- `AGENTS.md` is the shared source of truth for repo-wide agent behavior.
- Tool-specific files are adapter surfaces, not independent policy sources.
- Shared workflow knowledge should live once, then be referenced or adapted per
  agent system.
- Consistency checks should be automated enough that drift is caught before it
  becomes another manual cleanup project.

## Coordination File Naming

All files written under `AgentCoordination/` must identify the authoring agent in
the filename.

Use this convention:

```text
<agent-author>_<topic>.md
```

Examples:

- `codex_agent_coordination_plan.md`
- `claude_code_agent_coordination_comments.md`
- `opencode_deepseek_v4_pro_agent_coordination_comments.md`
- `antigravity_agent_coordination_comments.md`

Use lowercase snake_case for the author tag and topic. If an agent writes more
than one file, keep the same author tag across all files.

## Sources Consulted

The plan is based on local repository inspection plus current public docs:

- OpenCode rules: https://opencode.ai/docs/rules/
- OpenCode skills: https://opencode.ai/docs/skills/
- OpenCode agents: https://opencode.ai/docs/agents/
- Claude Code memory and `CLAUDE.md`: https://code.claude.com/docs/en/memory
- Claude Code skills: https://code.claude.com/docs/en/skills
- Claude Code settings: https://code.claude.com/docs/en/settings
- Codex AGENTS.md guidance: https://developers.openai.com/codex/guides/agents-md
- Codex skills: https://developers.openai.com/codex/skills
- Codex configuration: https://developers.openai.com/codex/config-advanced
- Agent Skills specification: https://agentskills.io/specification
- Google Antigravity product context: https://blog.google/products-and-platforms/products/gemini/gemini-3/

Local observations from this repo:

- `AGENTS.md` is compact and current enough to serve as the neutral shared entry.
- `CLAUDE.md` is much longer and contains stale duplicated project facts.
- `.agents/CODEX.md` is already a thin Codex adapter.
- `.codex/config.toml` points Codex at `AGENTS.md` with `CLAUDE.md` as a fallback.
- `opencode.json` already uses `AGENTS.md` as its instruction source.
- `.agent/` appears to be the Antigravity adapter surface in this repo.
- `.claude/skills/` and `.agent/skills/` contain overlapping legacy skill sets.
- `.agents/skills/` contains newer Codex-prefixed repo-local skills.
- `.opencode/skills/` currently contains the `audit-shrink` OpenCode skill.

## Current Drift To Fix

These are the concrete drift points observed during planning:

- `CLAUDE.md` references a `15405` test baseline, while `AGENTS.md` references
  `15477+`.
- `.claude/settings.local.json` is tracked and contains machine-local absolute
  paths under `c:\Dev\Starship Battles`, while the current workspace is
  `c:\Dev2\StarshipBattles`.
- `.agent/workflows/resolve_bug.md` references removed files
  `docs/bug_tracker.md` and `docs/lessons_learned.md`.
- `.agent/workflows/run-tests.md` still uses `python -m unittest discover`,
  while this repo's canonical test runner is
  `python Tools/test_sharded/test_sharded.py`.
- `.agent/workflows/generate_ship_theme.md` references
  `assets/tools/ship_background_remover.py`, while the tracked tool lives under
  `Tools/ship_background_remover/`.
- Some skill text treats `CLAUDE.md` as the authoritative repo instruction file,
  which conflicts with the current neutral `AGENTS.md` model.
- `.claude/skills/`, `.agent/skills/`, `.agents/skills/`, and
  `.opencode/skills/` are not managed by a shared manifest, so new or changed
  skills can easily drift.

## Proposed Structure

### Shared Instructions

Keep `AGENTS.md` as the always-on shared rule file for all agent systems that can
read it directly or indirectly. It should remain compact and should point agents
to `docs/README.md`, `docs/01_ARCHITECTURE.md`, `docs/02_PATTERNS.md`, and
`docs/03_CONVENTIONS.md` instead of duplicating full documentation.

`AGENTS.md` should own:

- Non-negotiable rules.
- Canonical commands.
- Current test baseline and known flakes.
- High-level architecture and conventions.
- Shared warnings such as not reading `docs/_ignore/`.

### Agent Adapters

Each tool-specific surface should contain only the differences needed by that
tool:

- `CLAUDE.md`: import `@AGENTS.md`, then add Claude Code-specific interaction,
  hooks, subagent, and settings guidance.
- `.claude/settings.json`: project-shared Claude Code settings only.
- `.claude/settings.local.json`: user-local only, not tracked.
- `.agents/CODEX.md`: Codex-specific routing and operating notes.
- `.codex/config.toml`: Codex project config and MCP/plugin settings.
- `opencode.json`: OpenCode model, instructions, permissions, commands, and
  OpenCode-specific config.
- `.agent/`: Antigravity workflows and skills where this repo needs them.
- `.opencode/`: OpenCode-native skills and commands where this repo needs them.
- `.agents/skills/`: Codex repo-local skills, preferably thin and
  Codex-prefixed.

### Coordination Docs

Use `AgentCoordination/` for cross-agent governance:

- Plans and review comments.
- Skill synchronization policy.
- Adapter mapping notes.
- Maintenance cadence.
- Future validator manifest design.

This folder is not a replacement for `docs/`. It exists only to coordinate the
agent-system surfaces.

## Maintenance Protocol

When creating or changing an agent instruction file, workflow, or skill:

1. Identify whether the change is shared behavior or agent-specific behavior.
2. If shared, update `AGENTS.md` or the relevant shared project protocol first.
3. Update every applicable adapter surface in the same change.
4. If a surface is intentionally not updated, record the reason in the
   coordination manifest or in the review notes.
5. Keep `SKILL.md` files compliant with the Agent Skills specification:
   `name`, `description`, valid lowercase-hyphen names, and directory-name match.
6. Keep Codex skills under `.agents/skills/` Codex-prefixed unless there is a
   deliberate shared-skill decision.
7. Keep large skill bodies split into referenced files when practical.
8. Run the future consistency validator before considering the maintenance pass
   complete.

## Future Validator

A later implementation task should add a validator using strict TDD:

```text
Tools/agent_coordination/validate_agent_surfaces.py
tests/unit/tools/test_agent_coordination_validator.py
AgentCoordination/agent_surfaces.json
```

The validator should be standard-library only unless a strong reason appears to
add a dependency. It should check:

- All discovered `SKILL.md` files have required frontmatter.
- Skill names match the parent folder and the Agent Skills naming regex.
- Known stale strings are absent.
- `CLAUDE.md` imports or clearly delegates to `AGENTS.md`.
- `.claude/settings.local.json` is not tracked.
- Every agent skill/workflow surface is listed in the manifest or explicitly
  ignored with a reason.
- OpenCode skill permissions intentionally hide incompatible skills.

Suggested first tests:

- Invalid or missing `SKILL.md` frontmatter fails.
- Stale baseline text such as `15405` fails.
- Old absolute paths such as `c:\Dev\Starship Battles` fail.
- Removed docs such as `docs/bug_tracker.md` fail.
- `python -m unittest discover` fails in agent workflow docs.
- Tracked `.claude/settings.local.json` fails.

Suggested verification commands:

```powershell
pytest tests/unit/tools/test_agent_coordination_validator.py -q
python Tools/agent_coordination/validate_agent_surfaces.py
python Tools/test_sharded/test_sharded.py
```

## Initial Implementation Phases

1. Create this Codex-authored plan in `AgentCoordination/`.
2. Ask Claude Code, OpenCode with DeepSeek V4 Pro, Codex, and Antigravity to
   review the plan using the shared prompt below.
3. Reconcile the review comments into a final coordination policy.
4. Normalize the current drift in existing agent files.
5. Add the manifest and validator with TDD.
6. Add a maintenance cadence, such as running the validator after agent-surface
   changes and during periodic documentation consistency passes.

## Shared Agent Review Prompt

Give each agent the same prompt. Each agent should write its own response under
`AgentCoordination/` using its agent or system name in the filename.

```text
You are reviewing a proposed multi-agent documentation and skill consistency plan for the Starship Battles repository.

High-level goal:
We use multiple agent systems on this codebase: Claude Code, OpenCode with DeepSeek V4 Pro, Codex, and Google Antigravity. The repository currently has multiple agent-specific instruction and skill surfaces, including AGENTS.md, CLAUDE.md, .claude/, .agent/, .agents/, .codex/, .opencode/, and related Markdown/config files. The goal is to make these surfaces consistent now and establish a maintainable process so future skill, workflow, and agent-doc updates do not drift.

Your tasks:
1. Research the current official documentation for Claude Code, OpenCode, Codex, Google Antigravity, and the Agent Skills standard. Prefer official/primary sources. Cite the links you used.
2. Inspect the local repository's relevant agent files, especially:
   - AGENTS.md
   - CLAUDE.md
   - opencode.json
   - .codex/config.toml
   - .agents/CODEX.md
   - .agents/skills/**
   - .claude/skills/**
   - .agent/skills/**
   - .agent/workflows/**
   - .opencode/skills/**
   - AgentCoordination/codex_agent_coordination_plan.md
3. Write your own response and comments on the Codex-authored plan.
4. Identify anything in the plan that is wrong, risky, incomplete, too heavy, too light, or likely to fail in your agent system.
5. Suggest concrete changes to the plan, including file naming, source-of-truth rules, skill synchronization, validation, maintenance cadence, and agent-specific adapter strategy.
6. Do not implement changes unless explicitly asked. This is a review/commentary pass.

Output requirements:
- Create one Markdown file in AgentCoordination/.
- The filename must identify you as the author, using lowercase snake_case, for example:
  - claude_code_agent_coordination_comments.md
  - opencode_deepseek_v4_pro_agent_coordination_comments.md
  - codex_agent_coordination_comments.md
  - antigravity_agent_coordination_comments.md
- Include these sections:
  - Summary Judgment
  - Sources Researched
  - Agreement With The Plan
  - Concerns Or Corrections
  - Recommended Changes
  - Agent-Specific Notes
  - Maintenance And Validation Suggestions
```

## Open Questions For Reviewers

Reviewers should comment specifically on these points:

- Should `CLAUDE.md` become a short import-and-adapter file, or should it keep
  longer Claude-specific guidance?
- Should legacy `.agent/skills/` and `.claude/skills/` remain mirrored, or
  should one become generated from the other?
- Should OpenCode use `.opencode/skills/` only, or intentionally consume some
  `.claude/skills/` or `.agents/skills/` compatibility surfaces?
- Should Codex continue to use only Codex-prefixed `.agents/skills/`, or should
  it share unprefixed skills with other tools?
- What is the right cadence for periodic consistency checks?

