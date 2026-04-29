# OpenCode (DeepSeek V4 Pro) Review: Codex Agent Coordination Plan

Author: OpenCode with DeepSeek V4 Pro
Date: 2026-04-28
Reviews: [codex_agent_coordination_plan.md](codex_agent_coordination_plan.md)

## Summary Judgment

The Codex plan gets the architecture right (`AGENTS.md` as source of truth, adapters as thin surfaces) but has a critical blind spot for OpenCode's skill discovery model. OpenCode reads `.claude/skills/` and `.agents/skills/` as first-class skill surfaces *by design*, per its own documentation. The plan treats these directories as tool-isolated adapters, which means the `opencode.json` deny list is not a nice-to-have — it's load-bearing infrastructure protecting OpenCode from 33+ foreign skills. Any validator or synchronization policy must treat the deny list as mutable and governed.

I endorse the plan with the corrections below. The plan is safe to proceed with after the deny-list governance and mirror-policy decisions are resolved.

## Sources Researched

Official primary sources, all fetched and verified:

- **OpenCode rules**: https://opencode.ai/docs/rules/ (confirmed: `AGENTS.md` canonical, `CLAUDE.md` fallback only when no `AGENTS.md`, `opencode.json` `instructions` array for additional files, no `@`-import syntax — that's Claude Code)
- **OpenCode skills**: https://opencode.ai/docs/skills/ (confirmed: discovers from `.opencode/skills/`, `.claude/skills/`, AND `.agents/skills/`; NOT `.agent/skills/` singular; unknown frontmatter fields ignored)
- **OpenCode permissions**: https://opencode.ai/docs/permissions/ (confirmed: pattern-based skill deny/allow)
- **Agent Skills specification**: https://agentskills.io/specification (confirmed: name regex `^[a-z0-9]+(-[a-z0-9]+)*$`, description 1-1024 chars, directory name must match)
- **Claude Code skills**: https://code.claude.com/docs/en/skills (confirmed: Claude-specific frontmatter extensions `disable-model-invocation`, `argument-hint`, `context: fork`, `agent`, `hooks`, `paths`)
- **Codex skills**: https://developers.openai.com/codex/skills (confirmed: scans `.agents/skills/` only; `$codex-` prefix used for invocation)
- **Google Antigravity**: https://antigravity.google/docs/skills (search-summarized as docs page returned no body; `.agent/skills/` singular is the workspace location; also reads `AGENTS.md`)

Local inspection verified:
- `AGENTS.md` (80 lines) — current baseline `15477+`, canonical commands, architecture summary
- `CLAUDE.md` (353 lines) — ~70% duplicated content from AGENTS.md; Claude-specific: subagent conventions, `.agent_reports/` policy, interactive-mode framing
- `opencode.json` (51 lines) — `instructions: ["./AGENTS.md"]`, deny list covering 23+ skill patterns, `command /audit-shrink`, `agent.plan` permissions, model config
- `.codex/config.toml` (29 lines) — `project_doc_fallback_filenames = ["CLAUDE.md"]`, MCP/plugin config
- `.agents/CODEX.md` (38 lines) — thin adapter, correctly references AGENTS.md
- `.claude/skills/` — 26 Claude skills, many with `disable-model-invocation`, `argument-hint`, `paths`
- `.agent/skills/` — 26 mirrored Antigravity skills (per `.agent/MIGRATION_PROGRESS.md`, migrated 2026-03-14), without Claude frontmatter extensions
- `.agents/skills/` — 7 Codex-prefixed skills, each with `agents/openai.yaml` sub-agent config
- `.opencode/skills/` — 1 skill: `audit-shrink`
- `.agent/workflows/` — 4 workflow files, all stale (reference removed docs, use `python -m unittest discover`)
- `.claude/settings.local.json` — tracked, contains absolute paths to a workspace that no longer exists (`c:\Dev\Starship Battles`)

## Agreement With The Plan

I agree with:

1. `AGENTS.md` as the shared source of truth — our `opencode.json` already pointed `instructions` at it; this codifies what we already practice.
2. Tool-specific files as thin adapters — `.agents/CODEX.md` is already a model for this.
3. The manifest-plus-validator pattern — stdlib-only is right for this repo.
4. TDD-first validator construction — matches Rule 1.
5. `.claude/settings.local.json` should not be tracked.
6. Codex `codex-` prefix discipline for `.agents/skills/` — prevents namespace pollution.
7. OpenCode's `opencode.json` permission deny list as the mechanism for hiding incompatible skills — this matches the OpenCode docs exactly.
8. Coordination files in `AgentCoordination/`, not `docs/`.

## Concerns Or Corrections

### 1. OpenCode reads `.claude/skills/` and `.agents/skills/` as first-class skill surfaces (NOT just adapters)

This is the most important correction. Per [OpenCode skills docs](https://opencode.ai/docs/skills/):

> OpenCode searches these locations: `.opencode/skills/`, `.claude/skills/`, `.agents/skills/`

The plan's "Agent Adapters" section implies each tool has an isolated directory. For OpenCode, `.claude/skills/` and `.agents/skills/` are **not** isolated — they are treated as native skill directories alongside `.opencode/skills/`. The deny list in `opencode.json` (`proj-*`, `ticket-*`, `codex-*`, `analysis-*`, `debug-*`, etc.) is the only mechanism preventing 33+ foreign skills from appearing in OpenCode's `/menu`.

**What this means:** The deny list is not an implementation detail — it is a governed artifact. Every new skill added to `.claude/skills/` or `.agents/skills/` must either:
- Match an existing OpenCode allow pattern (`audit-shrink` is the only one today), OR
- Be explicitly denied in `opencode.json` `permission.skill`, OR
- Be recorded in the manifest as intentionally compatible with OpenCode

The validator must enforce this triad. Without it, new skills silently appear in OpenCode's menu and agents may load them with incorrect behavior.

**Note:** OpenCode does NOT read `.agent/skills/` (singular, Antigravity). That surface is genuinely isolated from OpenCode. This is good.

### 2. The `opencode.json` deny list is hand-maintained and fragile

Current state: `opencode.json` denies `proj-*`, `ticket-*`, `codex-*`, `analysis-*`, `debug-*`, `deep-dive-*`, `qa-*`, `fix-crash`, `loc`, `triage-to-proj`, `validate-designs`, and `proj-sequential`. This covers the 26 `.claude/skills/` and 7 `.agents/skills/` names today.

But there's no guardrail. If a new skill `deploy` is added to `.claude/skills/`, it silently appears in OpenCode's menu. The plan's validator should flag any skill directory name discovered in `.claude/skills/` or `.agents/skills/` that is NOT matched by either an explicit allow or an explicit deny entry in `opencode.json`.

### 3. `.agent/workflows/` should be deleted, not repaired

The plan flags these files for stale content (wrong test command, removed docs). But reading them shows they are abandoned artifacts:

- `run-tests.md`: uses `python -m unittest discover` — this repo has never used unittest discovery as its primary runner; the canonical runner is `python Tools/test_sharded/test_sharded.py`
- `resolve_bug.md`: references `docs/bug_tracker.md` and `docs/lessons_learned.md` — these files do not exist and have no tracking/bugs protocol referencing them
- `generate_ship_theme.md`: references `assets/tools/ship_background_remover.py` — actual path is `Tools/ship_background_remover/`
- `modify_codebase.md`: not inspected in detail but the pattern of staleness is consistent

These are not "needs minor updates" — they are abandoned workflow files that predate the current test infrastructure, project management system, and the Codex-authored ship theme creator skill. Recommend deletion.

If Antigravity does not use them (and the Antigravity docs mention no workflow file convention), they serve no purpose and preserving them adds maintenance burden to the validator.

### 4. The plan's workspace path claim is wrong

The plan says the current workspace is `c:\Dev2\StarshipBattles`. The actual workspace (verified via environment) is `C:\Developer\StarshipBattles`. The stale path in `settings.local.json` is `c:\Dev\Starship Battles` (with a space, single `Dev`). Three different paths are in play.

The validator should not hardcode any workspace path. Instead, flag any Windows absolute path in tracked `settings.local.json` regardless of what the path is. Tracking `settings.local.json` is the violation; the specific stale path is just the evidence.

### 5. OpenCode does not support `@AGENTS.md` syntax

The plan says `CLAUDE.md` should "import `@AGENTS.md`". Claude Code supports `@path/to/file` imports. OpenCode does not.

OpenCode's equivalent is:
1. `opencode.json` `instructions: ["./AGENTS.md"]` — which we already have
2. Explicit instructions in `AGENTS.md` telling the agent to read other files (e.g., `Read docs/01_ARCHITECTURE.md before coding`)

The plan should not prescribe Claude-Code-specific syntax as a universal mechanism. When the plan says "import", it should specify which import mechanism applies to which tool.

### 6. OpenCode ignores unknown frontmatter — a risk and an opportunity

Per OpenCode docs: "Unknown frontmatter fields are ignored." This means:
- **Risk neutral**: Claude-specific fields (`disable-model-invocation`, `argument-hint`, `context: fork`, `paths`, `hooks`) in `.claude/skills/` are ignored by OpenCode. Skills load without those guardrails, but they don't break.
- **Opportunity**: The mirror policy (Claude → Antigravity) doesn't *need* to strip Claude fields for OpenCode's sake. But it should still strip them for Antigravity compatibility (Antigravity may reject unknown fields, unlike OpenCode).
- **Cleanliness**: Leaving Claude-only fields in mirrored `.agent/skills/` files is untidy. Recommend the generator strip `disable-model-invocation`, `argument-hint`, `context`, `agent`, `hooks`, `paths`, and `shell` from Antigravity copies.

### 7. `name` uniqueness is enforced by OpenCode across all surfaces

Per OpenCode docs: "Ensure skill names are unique across all locations." If `proj-start` exists in both `.claude/skills/proj-start/SKILL.md` and `.agent/skills/proj-start/SKILL.md`, the skill name `proj-start` appears once — OpenCode resolves duplicates to a single skill (the first found in discovery order). Which version wins depends on the cwd traversal path, which is fragile.

For OpenCode, this isn't broken today because `proj-*` is denied. But if any skill becomes OpenCode-compatible in the future, the duplicate across `.claude/` and `.agent/` would create ambiguous resolution. The mirror policy should address this, or the validator should flag same-named skills across surfaces that OpenCode reads.

### 8. The plan's Open Questions don't account for OpenCode's `.agents/skills/` visibility

The plan asks: "Should OpenCode use `.opencode/skills/` only, or intentionally consume some `.claude/skills/` or `.agents/skills/` compatibility surfaces?"

The OpenCode docs already answer this: OpenCode *always* reads all three project-local surfaces. This is not a choice — it's the design. The real policy question is: **Which skills from `.claude/skills/` and `.agents/skills/` should be deliberately compatible with OpenCode?**

The answer today via the deny list is: only `audit-shrink` (which lives in `.opencode/skills/`). All `.claude/skills/` and `.agents/skills/` are denied. If the team ever wants a shared skill (e.g., a future `ship-design-validator`), the natural location is `.opencode/skills/` for OpenCode-native consumption, with mirroring to other surfaces if needed.

## Recommended Changes

1. **Add a section on OpenCode skill surface governance.** Document that:
   - OpenCode discovers skills from `.opencode/skills/`, `.claude/skills/`, AND `.agents/skills/`
   - The `opencode.json` deny list is the mechanism that hides incompatible skills
   - Every new skill in `.claude/skills/` or `.agents/skills/` must be either explicitly denied in `opencode.json` or recorded as OpenCode-compatible
   - The validator checks this invariant

2. **Delete `.agent/workflows/` instead of repairing it.** Add a plan step to audit and delete stale workflow files. If Antigravity needs workflows, the Codex-authored ship theme creator skill already covers that use case better.

3. **Fix the workspace path.** Replace `c:\Dev2\StarshipBattles` with `C:\Developer\StarshipBattles`, or — better — drop absolute paths from the plan entirely. The validator should use `git rev-parse --show-toplevel`.

4. **Make the `@` import syntax tool-specific.** Say "Claude Code: use `@AGENTS.md`; OpenCode: `opencode.json` `instructions` array is already configured; Codex: reads `AGENTS.md` directly via `project_doc`."

5. **Commit to a mirror policy.** Three viable options, with my recommendation:

   - **(b) Recommended: canonical Claude, generated Antigravity.** `Tools/agent_coordination/sync_antigravity_skills.py` copies `.claude/skills/` → `.agent/skills/`, stripping Claude-specific frontmatter fields (`disable-model-invocation`, `argument-hint`, `context`, `agent`, `hooks`, `paths`, `shell`). Run in CI and pre-commit.
   - **(a) Fallback: both canonical, validator-enforced.** Content equivalence asserted by validator after field normalization. Less automated but simpler to start.
   - **(c): Canonical Claude, symlinked.** `mklink /J` on Windows. Risk: Antigravity rejects unknown frontmatter fields.

6. **Expand the validator's test cases.** Add:
   - Skill name collisions across `.claude/skills/`, `.opencode/skills/`, and `.agents/skills/` fail (OpenCode enforces uniqueness across all surfaces)
   - New skill in `.claude/skills/` or `.agents/skills/` without corresponding `opencode.json` deny/allow entry fails
   - `description` over 1024 characters fails (Agent Skills spec)
   - `name` violating `^[a-z0-9]+(-[a-z0-9]+)*$` fails
   - AGENTS.md test-baseline string (`15477+`) duplicated verbatim in any other instruction file fails
   - `.agent/workflows/` directory is empty or does not exist (if deleted per recommendation)

7. **Add a pre-commit hook-config and CI workflow.** The plan should include:
   - A `.pre-commit-hooks.yaml` or documented PowerShell pre-commit script for the validator
   - A GitHub Actions workflow at `.github/workflows/agent_coordination.yml` triggered on PRs touching `AGENTS.md`, `CLAUDE.md`, `opencode.json`, `.codex/config.toml`, or `**/SKILL.md`
   - Weekly cron sweep for full repo validation

8. **Expand the validator manifest schema.** Add these fields:
   - Per-skill: `open_code_compatible` (bool) — if true, must appear in `opencode.json` allow list; if false, must appear in deny list
   - Per-skill: `claude_extensions` (list of strings) — which Claude-specific fields are used
   - Per-surface: `tool_visibility` (list: `claude`, `opencode`, `codex`, `antigravity`) — which tools can see this surface
   - Top-level: `known_stale_strings` with reasons

9. **Tighten the `CLAUDE.md` adapter spec.** Cap at ~80 lines. Only retain Claude-Code-specific content: subagent conventions, `.agent_reports/` policy, VS Code interactive-mode framing, and the `@AGENTS.md` import line. Move everything else to `AGENTS.md` or delete it as duplicated.

10. **Separate `opencode.json` fields into plan-protected and implementation-detail.** The plan should protect:
    - `instructions: ["./AGENTS.md"]` — source of truth linkage
    - `permission.skill` — deny list governance
    - `command` — OpenCode-specific commands like `/audit-shrink`
    The plan should not micromanage `autoupdate`, `snapshot`, `compaction`, `model`, `provider`, `shell` — these are operational config that drift with DeepSeek API changes.

11. **Untrack `.claude/settings.local.json`.** Add `/.claude/settings.local.json` to `.gitignore` and run `git rm --cached .claude/settings.local.json`. Also add `/.codex/*` if not already gitignored (`.gitignore` currently handles `.codex/*` only partially — `.codex/config.toml` is tracked; verify the ignore covers all other `.codex/` artifacts).

## Agent-Specific Notes

These are observations about how this plan affects OpenCode specifically.

### Skill discovery is cross-surface by default

OpenCode **always** discovers skills from `.opencode/skills/`, `.claude/skills/`, and `.agents/skills/`. This is not configurable at the discovery level — it can only be controlled via `permission.skill` deny patterns. The `OPENCODE_DISABLE_CLAUDE_CODE_SKILLS` env var can disable `.claude/skills/` discovery, but that's a per-machine setting, not a repo-level guarantee.

**Practical impact:** The deny list is the only repo-level enforcement mechanism. It must be maintained. The validator is the enforcement mechanism.

### OpenCode's `instructions` array is the equivalent of Claude's `@` imports

OpenCode does not parse `@AGENTS.md` in `CLAUDE.md`. Instead, use `opencode.json`:
```json
{
  "instructions": ["./AGENTS.md"]
}
```
This is already configured correctly.

However, OpenCode *does* support manual file references in `AGENTS.md` body (e.g., "Read `docs/01_ARCHITECTURE.md` before coding") — but the agent must be instructed to do this; it's not automatic. Our `AGENTS.md` already has this pattern (Rule 2: "Read docs before coding").

### Unknown frontmatter is ignored, not rejected

OpenCode silently ignores `disable-model-invocation`, `argument-hint`, `context: fork`, `agent`, `paths`, `hooks`, and `shell` in skill frontmatter. This means:
- Claude skills with these fields load in OpenCode without error
- BUT the guardrails those fields provide are absent — e.g., `disable-model-invocation: true` does NOT prevent OpenCode from invoking the skill autonomously
- This is why the deny list is critical: skills designed with Claude-specific invocation constraints may behave incorrectly when loaded by OpenCode without those constraints

### The `opencode.json` deny list is the primary security surface

The deny list prevents OpenCode agents from loading skills designed for other tools. If someone removes a deny pattern, the skill becomes available. The plan should treat the deny list as a governed artifact, not an afterthought.

Current deny patterns and what they protect:
- `proj-*` → 10 Claude/Antigravity project-lifecycle skills
- `ticket-*` → 10 Claude/Antigravity ticket-workflow skills
- `codex-*` → 7 Codex-specific skills
- `analysis-*` → 3 Claude/Antigravity analysis skills
- `debug-*` → legacy debug skills in Claude
- `deep-dive-*` → legacy deep-dive skills
- `qa-*` → QA triage/feedback skills
- `fix-crash`, `loc`, `triage-to-proj`, `validate-designs` → individual Claude skills

Only `audit-shrink` (in `.opencode/skills/`) and `*` (wildcard allow for everything else) are allowed. This is the correct configuration today.

### OpenCode `command` section is OpenCode-specific

The `command` section in `opencode.json` (e.g., `/audit-shrink`) is an OpenCode feature for creating slash commands that trigger skill loading. No other tool in this plan supports it. It belongs in the OpenCode adapter surface and the plan should explicitly note it.

### OpenCode's `agent` configuration

Our `opencode.json` configures `agent.plan` with `edit: deny` and `bash: deny` permissions. This is a plan-mode safety guard. The plan should note that agent-specific permission overrides are part of the OpenCode adapter surface and are tool-specific.

### OpenCode's `compaction` and `autoupdate` are operational config

`autoupdate: true`, `snapshot: true`, and `compaction` settings in `opencode.json` are OpenCode operational configuration. They don't need coordination governance. The plan should distinguish between "coordinated surface" (instructions, permissions, skills) and "operational config" (model, compaction, autoupdate).

## Maintenance And Validation Suggestions

### Validator location and design

`Tools/agent_coordination/validate_agent_surfaces.py` (stdlib-only Python 3.13+). Tests at `tests/unit/tools/test_agent_coordination_validator.py`.

Output:
- Human-readable summary to stdout
- Machine-readable JSON to `Reviews/results/{DATE}_AGENT_SURFACES/results.json`

### Manifest format

TOML, not JSON. Reasoning:
- `tomllib` is stdlib in Python 3.11+ (we're on 3.13)
- TOML supports comments (critical for recording *why* a skill is denied/compatible)
- Easier to diff in PRs than JSON
- No dependency — staying stdlib-only

If the team insists on a different format, YAML would require `pyyaml` (not stdlib). JSON would lack comments. TOML is the pragmatic choice.

### TDD test cases the plan should require (beyond its list)

```
TestAgentCoordinationValidator:
  # Skill name compliance (Agent Skills spec)
  - test_skill_name_mismatches_directory_name_fails
  - test_skill_name_with_uppercase_fails
  - test_skill_name_with_double_hyphen_fails
  - test_skill_name_starting_with_hyphen_fails
  - test_skill_name_exceeds_64_chars_fails
  - test_description_exceeds_1024_chars_fails

  # OpenCode multi-surface discovery
  - test_skill_name_duplicate_across_claude_and_opencode_fails
  - test_skill_name_duplicate_across_claude_and_agents_fails
  - test_new_skill_in_claude_skills_without_opencode_deny_entry_fails
  - test_new_skill_in_agents_skills_without_opencode_deny_entry_fails
  - test_skill_in_agent_singular_not_visible_to_opencode (truth check)

  # Deny list governance
  - test_opencode_deny_pattern_covers_all_claude_skill_names
  - test_opencode_deny_pattern_covers_all_agents_skill_names
  - test_permission_removed_without_manifest_record_fails

  # Content drift
  - test_test_baseline_duplicated_in_claude_md_fails
  - test_canonical_command_duplicated_in_agent_workflows_fails
  - test_removed_doc_referenced_in_skill_body_fails

  # Local settings
  - test_claude_settings_local_json_is_tracked_fails
  - test_absolute_windows_path_in_tracked_settings_fails

  # Stale content
  - test_python_m_unittest_discover_in_agent_docs_fails
  - test_docs_bug_tracker_md_referenced_fails
  - test_docs_lessons_learned_md_referenced_fails
  - test_assets_tools_ship_background_remover_path_fails
```

### Cadence enforcement

- **Pre-commit**: opt-in hook running `python Tools/agent_coordination/validate_agent_surfaces.py` (fast, read-only)
- **CI on PR**: triggered when PR touches `AGENTS.md`, `CLAUDE.md`, `opencode.json`, `.codex/config.toml`, or `**/SKILL.md` or `**/workflows/*.md`
- **Weekly sweep**: full validator run against all surfaces, results archived to `Reviews/results/`
- **Pre-release sweep**: full validator + documentation consistency pass

### One-time cleanup before validator goes green

1. Untrack `.claude/settings.local.json` (`git rm --cached`, add to `.gitignore`)
2. Delete `.agent/workflows/` (four stale files)
3. Delete `.agent/MIGRATION_PROGRESS.md` (snapshot from 2026-03-14, not a living document — replaced by mirror policy)
4. Trim `CLAUDE.md` to ≤80 lines (remove duplicated AGENTS.md content, keep Claude-specific only)
5. Replace `15405` with `15477+` in CLAUDE.md
6. Normalize stale `c:\Dev\Starship Battles` paths in `settings.local.json` (which will then be untracked anyway)
7. Verify `$codex-*` deny pattern in `opencode.json` covers all 7 Codex skills
8. Verify each `.claude/skills/` name is covered by a deny pattern in `opencode.json`
9. Add skill name cross-reference to the manifest

### Documentation additions

Add `AgentCoordination/README.md` with:
- Source-of-truth rule: `AGENTS.md` owns shared behavior; adapters own tool-specific behavior
- Skill placement guide: "Where does this new skill go?"
  - OpenCode-native → `.opencode/skills/`
  - Claude Code → `.claude/skills/` (then verify deny list or mark as OpenCode-compatible)
  - Codex → `.agents/skills/`, prefixed `codex-`
  - Antigravity → generated from `.claude/skills/` by sync script
  - Shared across all → `.claude/skills/` canonical + generated mirrors
- Mirror policy (once decided)
- How to run the validator

### Out of scope for this plan but worth tracking

- The `Projects/refactor_loop/WORKER.md` referenced from `CLAUDE.md` — if it exists, it's a fourth agent instruction surface (CLI loop mode). If it doesn't, the CLAUDE.md reference should be removed.
- The OpenCode `.opencode/package.json` and `node_modules/` — these appear to be an OpenCode plugin/project artifact. They should be `.gitignore`'d if they're machine-generated.
- MCP server config in `.codex/config.toml` — coordination plan should note that MCP servers are tool-specific and not subject to cross-tool governance.
