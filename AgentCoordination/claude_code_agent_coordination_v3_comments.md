# Claude Code V3 Review

Author: Claude Code (Opus 4.7, 1M context)
Date: 2026-04-28
Reviews: [codex_agent_coordination_plan_v3.md](codex_agent_coordination_plan_v3.md)

## User Discussion Summary

Discussed the disagreements with the user before writing this file. Confirmed positions:

1. Track the generated test baseline and skill inventory in git (V3 default of "ignored" reversed). User agrees.
2. Reinforcement-duplication rules need a closed marker allowlist, a concrete similarity threshold, and an explicit volatile-fact pattern set before the validator can be implemented. User agrees.
3. Renamer must rewrite cross-references repo-wide, including `Projects/protocols/`, `Tracking/protocols/`, `AGENTS.md`, and the Codex `agents/openai.yaml` metadata files. User wants metadata files in scope for consistency.
4. OpenCode prefix is `ocode-`.
5. No transitional cheat sheet — atomic rename.
6. Delete `.agent/workflows/` and `.agent/MIGRATION_PROGRESS.md` outright; git history is the archive.
7. `.claude/settings.local.json` is tracked **only if** the renamer/sanitizer can strip everything before `StarshipBattles\` from every absolute path. Otherwise untracked.
8. Usage counters: hooks for Claude Code, scripts for agents without hook support. Open to other approaches.

## Material Disagreements

### 1. Track generated artifacts in git

V3 §8 leans toward "tracked only after intentional full-suite baseline updates" and §9 doesn't commit. Both should be tracked by default. `.test_durations.json` is per-machine timing, not analogous repo truth. Tracking gives:

- Fresh-clone visibility (multi-agent reviews start from the same baseline).
- Diff-as-regression-detector (a sudden drop from 15477 → 15400 surfaces in PR review).
- Stable cross-tool reference (the inventory becomes the citation for "do we have this skill?").

Tracked artifacts must include `git_sha` and `generated_at` so staleness is visible. The sharded runner refuses to overwrite a tracked baseline with a non-green run.

### 2. Reinforcement-duplication rules under-specified

V3 §7 lacks three things needed for an implementable validator:

- **Closed marker allowlist.** Free-form tags drift. Permitted set: `tdd`, `docs-first`, `code-doc-consistency`, `root-cause`, `no-ignore-folder`, `no-revert-unrelated`. Anything else fails parse.
- **Similarity threshold.** Concrete rule: ≥5 consecutive non-blank, non-trivial lines (>20 chars) byte-identical to a span in `AGENTS.md` without a marker = fail. Below threshold = pass.
- **Volatile-fact pattern set.** Closed regex list the validator owns: `\b1[0-9]{4}\b` near "test"/"baseline", absolute Windows paths (`[a-zA-Z]:\\`), `python -m unittest`, `15405`, removed-doc paths from V2's drift list, hardcoded version numbers. Match outside generated artifacts = fail.

### 3. Renamer scope must be repo-wide and include Codex YAML

V3 §4 lists "skill bodies and adapter docs." Verified additional reference sites:

- `AGENTS.md` line 72 contains the literal path `.opencode/skills/audit-shrink/SKILL.md`.
- `Projects/protocols/03b_parallel_projects.md`, `Projects/protocols/07_extract_phase.md`, `Tracking/protocols/02c_parallel_debug.md` reference skill names by slash command.
- `.agents/skills/codex-*/agents/openai.yaml` files contain `default_prompt` strings with `$skill-name` references (e.g. `$codex-starship-project-system`). Existing `codex-` skills don't change name, but these YAML files must still be parsed so the renamer can update any cross-references and so non-Codex prefixes never sneak into `interface.display_name` or `default_prompt` later.

Per user: the renamer is in scope for the YAML metadata for consistency-validation, even when the current file would not be modified.

### 4. `.claude/settings.local.json` — conditional tracking

User is willing to track if absolute paths are normalized. The current file has 200+ allow rules, many with `c:\\Dev\\Starship Battles\\...` literals embedded inside `Bash(...)` patterns. Stripping the prefix is **not** a simple regex replace:

- `Bash(if not exist "c:\\Dev\\Starship Battles\\tests\\unit\\services" mkdir ...)` becomes `Bash(if not exist "tests\\unit\\services" mkdir ...)` — semantically different (relative vs absolute test). Some shells will not match the pattern at runtime.
- `Read(//c/Dev/Starship Battles/**)` is a glob path; stripping leaves `Read(**)` which over-grants.
- A few patterns embed `Starship Battles\\` (with the space, old folder name) — those entries are stale references to a previous workspace name and should be deleted, not normalized.

V3 should treat sanitization as a **lossy** transform that must be reviewed by the user, not a pure rewrite. Recommend: a one-shot `Tools/agent_coordination/sanitize_claude_settings_local.py` that prints proposed deletions, proposed rewrites, and unrewriteable entries (manual decision required) — does not auto-apply. If the residue after the user's review is empty of absolute paths, track it. Otherwise leave it ignored.

## Implementation Risks

- **Atomic rename PR will be very large.** ~33 directories renamed, 19+ frontmatter edits, dozens of cross-reference rewrites, plus AGENTS.md/CLAUDE.md/opencode.json updates. Reviewer (you) has to read the diff in one sitting. Mitigate: the renamer emits a structured report (`AgentCoordination/SKILL_RENAMES.md`) with per-file change counts so review can prioritize.
- **`opencode.json` permission rules become wrong mid-rename.** Until the rename and the `opencode.json` patterns commit together, OpenCode will see (rename-applied) skill names that no longer match (rename-not-yet-applied) deny patterns. Renamer must update `opencode.json` in the same commit.
- **Validator built before rename will encode old patterns.** V3 phases (Phase 3 rename → Phase 5 validator) are in the right order. Don't reverse them.
- **Usage-counter scripts are still self-report.** A user-invokable `track-skill-usage.py` is technically "automation" but practically equivalent to manual logging — agents that forget to call it produce gaps. Where Claude Code hooks work, prefer hooks. For others, an alternative worth prototyping: a transcript-scanning script that parses agent session logs after the fact (Codex/OpenCode write transcripts to known locations) and emits usage records without the agent doing anything.

## New Suggestions

1. **Renamer dry-run mode is mandatory.** First invocation must produce a diff report and refuse to write. User confirms, second invocation applies.
2. **Inventory generator runs in pre-commit.** Cheap to compute; keeps `agent_surface_inventory.json` always current. CI verifies the committed file matches a fresh generation.
3. **Validator emits a `waivers.toml`** for any duplication or pattern that fails but the user explicitly accepts. Keeps the rule set strict and the exceptions explicit.
4. **Test-baseline write is gated on green run only.** Sharded runner writes the JSON only if `failed == 0 and errors == 0`. Otherwise leaves the previous baseline untouched.
5. **`AgentCoordination/local/` directory is gitignored** by adding `/AgentCoordination/local/` to `.gitignore` in the same Phase 2 commit that adds the settings.local.json ignore.
6. **Transcript-scanning prototype for usage counters** before committing to per-agent hook+script split. Codex transcripts and Claude Code session logs both exist in known locations; one parser handles both.

## Evidence

- Skill counts (verified locally 2026-04-28): `.claude/skills/` = 32, `.agent/skills/` = 33, `.agents/skills/` = 8, `.opencode/skills/` = 1.
- Cross-protocol references confirmed via `grep -rln "proj-start\|ticket-work\|qa-triage\|audit-shrink\|debug-parallel" Projects/protocols/ Tracking/protocols/ docs/` → 3 matches in `Projects/protocols/03b_parallel_projects.md`, `Projects/protocols/07_extract_phase.md`, `Tracking/protocols/02c_parallel_debug.md`.
- AGENTS.md line 72: `See \`.opencode/skills/audit-shrink/SKILL.md\` for the agent-driven Phase 2 workflow.` — confirms the renamer must touch AGENTS.md.
- Codex skill metadata format: `.agents/skills/codex-starship-project-system/agents/openai.yaml` contains `default_prompt: "Use $codex-starship-project-system to start..."` — confirms cross-reference syntax in YAML.
- `.gitignore` currently has `.test_durations.json` but **not** `.claude/settings.local.json` or `AgentCoordination/local/` — both need adding in Phase 2.
- Agent Skills spec name regex `^[a-z0-9]+(-[a-z0-9]+)*$` and 64-char limit ([agentskills.io/specification](https://agentskills.io/specification)) — `claude-proj-extract-phase` (25 chars) and similar all comfortably fit.
- Claude Code skill hooks: [code.claude.com/docs/en/skills](https://code.claude.com/docs/en/skills) documents `hooks:` frontmatter — supports the usage-counter hook approach for the Claude side.

## Final Recommendation

Adopt V3 with these amendments before tooling work begins:

1. Track the generated test baseline and skill inventory; reverse V3's default-ignored stance.
2. Lock down the reinforcement-duplication rules (closed marker tags, ≥5-line similarity threshold, closed volatile-fact pattern set) in V3 §7 before anyone writes the validator.
3. Expand renamer scope explicitly: repo-wide grep+rewrite, including `Projects/protocols/`, `Tracking/protocols/`, `AGENTS.md`, and parsing of `.agents/skills/codex-*/agents/openai.yaml`.
4. Treat `.claude/settings.local.json` sanitization as lossy: produce a review report first, track only if the residue is path-clean.
5. Order: inventory → delete stale → rename → generated artifacts → validator → usage-counter prototype. V3's phasing is correct; just lock the rename PR atomic with the `opencode.json` deny-list update so OpenCode never sees a half-renamed state.
