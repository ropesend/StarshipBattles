# Claude Code Review: Codex Agent Coordination Plan

Author: Claude Code (Opus 4.7, 1M context)
Date: 2026-04-28
Reviews: [codex_agent_coordination_plan.md](codex_agent_coordination_plan.md)

## Summary Judgment

The Codex plan is directionally correct and I broadly endorse it: `AGENTS.md` should be the neutral source of truth, tool-specific files should be thin adapters, and a manifest-plus-validator pattern is the right way to stop drift. The structural call ("rules live once; adapters reference them") is the right one.

That said, the plan has several issues that would bite us if implemented as written:

1. The plan's "current drift" list is partially wrong about this workspace. The path it cites (`c:\Dev2\StarshipBattles`) is not the actual workspace (`c:\Developer\StarshipBattles`), so any validator written against that string would be checking the wrong thing.
2. The plan misreads how OpenCode discovers skills. OpenCode actively reads `.claude/skills/` and `.agents/skills/` as fallbacks. Treating them as adapter-isolated is incorrect — they are shared surfaces by default.
3. The plan does not acknowledge Antigravity's exact surface (`.agent/skills/` singular vs `.agents/` plural) and the codebase has both. That asymmetry is the highest-priority drift, not the test-baseline string.
4. The "shrink CLAUDE.md to import + adapter" recommendation is reasonable but underestimates how much of `CLAUDE.md` is duplicated content vs Claude-specific guidance. Most of `CLAUDE.md` is duplicated rule text; the actually-Claude-specific portion is small.
5. The proposed validator URL list cites `https://code.claude.com/docs/en/...`. That host is correct but the canonical URL pattern most users hit is `https://docs.claude.com/en/docs/claude-code/...` (which 301s). Either is acceptable; just record the canonical one.
6. The plan offers no concrete answer to its own open question about whether `.claude/skills/` and `.agent/skills/` should be mirrors. They currently *are* mirrors (per `.agent/MIGRATION_PROGRESS.md`), and the plan should explicitly endorse one of: (a) keep them as mirrors with one-way sync, (b) collapse to one canonical surface and symlink/junction, or (c) generate one from the other. Leaving this open guarantees drift.

Net: approve the structural plan, reject the specific drift list and validator scope until corrected, demand concrete answers on the Open Questions before any tooling lands.

## Sources Researched

Official sources I read while preparing this review:

- Claude Code skills: [https://code.claude.com/docs/en/skills](https://code.claude.com/docs/en/skills) (also reachable via the redirected `https://docs.claude.com/en/docs/claude-code/skills`)
- OpenCode rules: [https://opencode.ai/docs/rules/](https://opencode.ai/docs/rules/)
- OpenCode skills: [https://opencode.ai/docs/skills/](https://opencode.ai/docs/skills/)
- Codex AGENTS.md guidance: [https://developers.openai.com/codex/guides/agents-md](https://developers.openai.com/codex/guides/agents-md)
- Codex skills: [https://developers.openai.com/codex/skills](https://developers.openai.com/codex/skills)
- Agent Skills specification: [https://agentskills.io/specification](https://agentskills.io/specification)
- Google Antigravity skills (search-summarized; the live docs page returned no body via WebFetch): [https://antigravity.google/docs/skills](https://antigravity.google/docs/skills) and [Google Codelabs: Authoring Antigravity Skills](https://codelabs.developers.google.com/getting-started-with-antigravity-skills) and [Google Cloud Community: Where to put your Agent Skills](https://medium.com/google-cloud/confused-about-where-to-put-your-agent-skills-ea778f3c64f3)

Key facts pulled from these sources, relevant to the plan:

- **Agent Skills spec** ([agentskills.io](https://agentskills.io/specification)): `name` regex `^[a-z0-9]+(-[a-z0-9]+)*$`, max 64 chars, must match parent directory name. `description` 1–1024 chars. Optional fields: `license`, `compatibility`, `metadata`, `allowed-tools`. The spec is the floor every adapter must satisfy.
- **Claude Code** explicitly states it follows the Agent Skills standard and adds extensions: `disable-model-invocation`, `user-invocable`, `allowed-tools`, `argument-hint`, `paths`, `model`, `effort`, `context: fork`, `agent`, `hooks`. Project skills live at `.claude/skills/<name>/SKILL.md`. Plugin skills are namespaced `plugin:skill`. Permission rules: `Skill(name)` and `Skill(name *)`.
- **OpenCode** ([opencode.ai/docs/skills](https://opencode.ai/docs/skills/)) explicitly *discovers* skills from `.opencode/skills/`, `.claude/skills/`, **and** `.agents/skills/` (project-local) plus their `~` equivalents. This is the load-bearing fact the plan misses.
- **OpenCode** ([opencode.ai/docs/rules](https://opencode.ai/docs/rules/)): `AGENTS.md` is canonical and supersedes `CLAUDE.md` when both exist. Our `opencode.json` `instructions: ["./AGENTS.md"]` is consistent with the docs.
- **Codex** ([developers.openai.com/codex/skills](https://developers.openai.com/codex/skills)): scans `.agents/skills` (plural) only — not `.claude/skills/`, not `.agent/skills/`. The Codex plan is correct on this point.
- **Codex** ([developers.openai.com/codex/guides/agents-md](https://developers.openai.com/codex/guides/agents-md)): Codex docs do **not** mention CLAUDE.md as a documented fallback. `project_doc_fallback_filenames` is the user-supplied fallback list. Our `.codex/config.toml` listing `["CLAUDE.md"]` is fine — but the Codex plan's framing ("`.codex/config.toml` points Codex at `AGENTS.md` with `CLAUDE.md` as a fallback") is true *because we configured it*, not because Codex defaults to it.
- **Antigravity** uses `.agent/skills/` (singular `agent`) for workspace skills and `~/.gemini/antigravity/skills/` for global. It also reads `AGENTS.md`.

## Agreement With The Plan

I agree with these positions in the plan:

- `AGENTS.md` should be the single shared source of truth.
- `CLAUDE.md`, `.agents/CODEX.md`, `opencode.json`, `.codex/config.toml`, and Antigravity's surface should be thin adapters that reference `AGENTS.md` rather than duplicate its rules.
- A manifest plus a stdlib-only validator is the right enforcement mechanism.
- TDD-first validator construction is consistent with this repo's Rule 1.
- `.claude/settings.local.json` should not be tracked (it currently *is* tracked — confirmed via `git ls-files`).
- Codex skills under `.agents/skills/` should remain `codex-` prefixed when their content is Codex-specific. (Note: the Agent Skills spec allows this; the prefix is just a name choice.)
- OpenCode's permission allowlist in `opencode.json` is the right way to hide incompatible skills (matches the OpenCode docs).
- Coordination files belong in `AgentCoordination/`, not `docs/`.

## Concerns Or Corrections

### 1. The cited workspace path is wrong

The plan says: *"current workspace is `c:\Dev2\StarshipBattles`"*. The actual workspace at the time of this review is `c:\Developer\StarshipBattles` (verified with `pwd`). The stale path the plan flags in `.claude/settings.local.json` is `c:\Dev\Starship Battles` (with a space, single `Dev`). Any validator we write must be told the correct current path or it will pass a check it should fail.

**Action:** correct the plan's drift section. The validator should not hardcode workspace paths at all — flag *any* Windows absolute path under `Bash(...)` permissions in tracked `settings.local.json` regardless of which one. Tracking `settings.local.json` itself is the bug; the specific path is incidental.

### 2. OpenCode actively reads `.claude/skills/` and `.agents/skills/`

The plan implies each tool has its own adapter directory and Codex stays in `.agents/`, Claude in `.claude/`, OpenCode in `.opencode/`. Per [OpenCode skills docs](https://opencode.ai/docs/skills/), OpenCode discovers skills from `.opencode/skills/`, `.claude/skills/`, **and** `.agents/skills/` simultaneously. That's why our existing `opencode.json` has the long deny list (`proj-*`, `ticket-*`, `codex-*`, `analysis-*`, etc.) — it's compensating for the fact that all three skill trees are visible to OpenCode.

This has two consequences:

- The plan should explicitly state that OpenCode-visible skill surfaces include `.claude/skills/` and `.agents/skills/`, not just `.opencode/skills/`. The current `opencode.json` deny list is therefore load-bearing and needs to be in the validator: any new skill added to `.claude/skills/`, `.agent/skills/`, or `.agents/skills/` that doesn't fit the OpenCode allow pattern must either be explicitly denied in `opencode.json` or marked as OpenCode-compatible in the manifest.
- The "Should OpenCode use `.opencode/skills/` only?" open question already has a forced answer: no, it can't, because OpenCode discovers the others by default. The right policy choice is: OpenCode-native skills go in `.opencode/skills/`, every other directory is governed by the deny pattern.

### 3. `.agent/` vs `.agents/` collision is not flagged

This repo has both:

- `.agent/skills/` (singular) — Antigravity's workspace skill location, currently mirroring the Claude skill set per `.agent/MIGRATION_PROGRESS.md`.
- `.agents/skills/` (plural) — Codex's workspace skill location.

These are two different agent systems with confusingly close directory names. The plan refers to `.agents/skills/` as Codex (correct) and `.agent/` as "the Antigravity adapter surface in this repo" (correct), but doesn't call out that the singular/plural distinction is fragile and easy to typo. A validator must hard-fail on the wrong directory existing, e.g. `.agent/skills/codex-...` (Codex skill in Antigravity dir) or `.agents/skills/proj-start` (a Claude/Antigravity-style skill in Codex dir).

### 4. Claude Code-specific `CLAUDE.md` content is small; most of it is duplicated

I read [`CLAUDE.md`](../CLAUDE.md) (353 lines) and [`AGENTS.md`](../AGENTS.md) (80 lines). The "Three Non-Negotiable Rules", documentation reading order, project structure, conventions, and architecture sections in `CLAUDE.md` are restatements of `AGENTS.md` with more prose. Truly Claude-specific content is limited to:

- The "Technical Consultant" interactive-mode framing.
- Claude Code subagent / report directory conventions (`.agent_reports/`, the override paragraph).
- A few VS Code-vs-CLI distinctions.

Recommendation: the plan should be more directive — `CLAUDE.md` should `@AGENTS.md` (Claude Code import syntax) at the top and reduce to ≤80 lines of strictly Claude-Code-specific guidance. The plan says "import and add Claude-specific" but doesn't commit to a target size or list which sections survive the trim. Without that, the next maintainer will keep it long because each paragraph is individually defensible.

### 5. The validator scope is too narrow

The validator section calls out:

- Frontmatter validity, name regex, directory match.
- Stale strings (`15405`, `c:\Dev\Starship Battles`).
- Workflow strings (`python -m unittest discover`, `docs/bug_tracker.md`).
- `.claude/settings.local.json` not tracked.

Missing checks I would add:

- **Skill name uniqueness across surfaces:** if `.claude/skills/proj-start/` and `.agent/skills/proj-start/` both exist, their `SKILL.md` content must either be byte-identical or explicitly diverge with a recorded reason. Today they diverge silently (Claude has `disable-model-invocation: true` and `argument-hint`, Antigravity does not). That's not a bug — Antigravity may not support those fields — but it should be a deliberate, manifest-recorded decision, not a coincidence.
- **Description length:** Agent Skills spec caps `description` at 1024 chars; Claude Code displays the first 1536 across `description`+`when_to_use`. Validator should warn over 1024 to keep cross-tool portability.
- **`disable-model-invocation`, `argument-hint`, `paths`, `context: fork` are Claude-specific extensions.** Skills that use them but live in `.agent/skills/` (Antigravity) or `.agents/skills/` (Codex) should be flagged; either the field should be removed from the non-Claude copy or the skill should be marked Claude-only in the manifest.
- **Permission deny coverage:** every top-level directory under `.claude/skills/`, `.agent/skills/`, `.agents/skills/` whose name does not match an OpenCode allow pattern must appear in `opencode.json`'s skill deny list. Today the deny list is hand-maintained; this should be derived or asserted.
- **`AGENTS.md` content drift:** the test baseline (`15477+`), the canonical commands, and the architecture description in `AGENTS.md` should be the only place those strings appear. Validator should flag any duplication into `CLAUDE.md`, `.agents/CODEX.md`, or skill bodies.
- **`.codex/config.toml` `project_doc_fallback_filenames`:** the order matters. If `CLAUDE.md` is in this list, the validator should confirm it doesn't carry separate authoritative content; otherwise Codex will read it as a layered project doc when `AGENTS.md` is missing in a subdirectory.

### 6. The plan does not commit to a mirror policy for `.claude/skills/` ↔ `.agent/skills/`

`.agent/MIGRATION_PROGRESS.md` documents that 26 skills were copied from `.claude/skills/` to `.agent/skills/` on 2026-03-14. They have been editable independently since. This is the textbook drift surface and the plan must take a position. Three viable options:

- **(a) One canonical, one symlinked.** Keep `.claude/skills/` canonical, replace `.agent/skills/` skill subdirs with junctions/symlinks. Windows-friendly with `mklink /J`. Risk: Antigravity-specific tweaks become impossible.
- **(b) One canonical, one generated.** A script mirrors `.claude/skills/` to `.agent/skills/`, stripping Claude-specific frontmatter fields. Run in CI. This is the cleanest answer if Antigravity rejects unknown frontmatter.
- **(c) Both canonical, same content asserted.** The validator demands byte-equivalence (or content-equivalence after frontmatter normalization). No automation, but drift fails CI.

My recommendation: **(b)**, with `.claude/skills/` as canonical and a `Tools/agent_coordination/sync_antigravity_skills.py` step. The reason for (b) over (a): Antigravity's frontmatter tolerance is not documented well enough to bet on it accepting Claude-specific fields silently. (a) saves disk but breaks the moment one tool diverges. (c) is fragile because mirror-by-discipline reliably fails.

### 7. Antigravity surface verification is light

The plan says "`.agent/` appears to be the Antigravity adapter surface in this repo." That's right, but the plan doesn't lock in:

- Where the Antigravity equivalent of CLAUDE.md / .agents/CODEX.md lives. (It's `AGENTS.md` directly — Antigravity reads the project's `AGENTS.md`, no adapter file. So `.agent/` is *only* skills/workflows, no instruction file. The plan should state this explicitly.)
- Whether `.agent/workflows/` is an Antigravity concept or a legacy Claude artifact. The three workflow files (`generate_ship_theme.md`, `modify_codebase.md`, `resolve_bug.md`, `run-tests.md`) reference removed docs and use `python -m unittest discover` — they look abandoned, not actively used by Antigravity. The plan should propose a hard decision: revive or delete. Drift fixes should not preserve files we've stopped using.

## Recommended Changes

Concrete changes I want to see in a v2 of the Codex plan before tooling lands:

1. **Fix the cited workspace path.** Replace `c:\Dev2\StarshipBattles` with `c:\Developer\StarshipBattles`, or — better — drop the absolute path from the plan entirely and rely on `git rev-parse --show-toplevel` in any validator.

2. **Document OpenCode's multi-surface discovery.** Add a paragraph to "Proposed Structure → Agent Adapters" stating that OpenCode reads `.opencode/skills/`, `.claude/skills/`, and `.agents/skills/`, and that `opencode.json` permission rules are the only thing keeping Codex/Antigravity skill names out of the OpenCode `/menu`.

3. **Commit to a `.claude/skills/` ↔ `.agent/skills/` policy.** I recommend option (b) above (canonical Claude, generated Antigravity mirror, frontmatter normalized). Delete `.agent/MIGRATION_PROGRESS.md` once the generator exists — it's a snapshot, not a living document.

4. **Audit and decide `.agent/workflows/`.** Either rewrite each file to current commands and docs, or delete it entirely. The plan currently only flags the workflow files for content fixes, not for whether they should exist at all.

5. **Tighten the `CLAUDE.md` adapter spec.** State a target line count (~80 lines max), name the sections that survive (Claude Code subagent conventions, `.agent_reports/` policy, VS Code interactive-mode framing), and require an `@AGENTS.md` import at the top. Everything else moves into `AGENTS.md` or gets deleted.

6. **Make `.claude/settings.local.json` untracked.** Plan must say *delete from tracking* (not just "should not be tracked"), and add `.claude/settings.local.json` to `.gitignore`. The current `.gitignore` only handles `.codex/*` and `.agent_reports/`. Also: Claude Code's `settings.json` (project-shared) is fine to track; the plan should make this distinction explicit.

7. **Expand the validator manifest schema.** It needs at minimum:
   - Per-skill fields: `path`, `name`, `surfaces` (which dirs it must appear in), `canonical_surface`, `mirror_policy` (`generated` / `manual` / `symlink`), `tool_compat` (claude/opencode/codex/antigravity), `claude_extensions_allowed` (bool).
   - Per-instruction-file fields: `path`, `role` (`source-of-truth` / `adapter`), `imports` (which files it must `@`-import or reference).
   - A top-level `known_stale_strings` list with reasons.

8. **Add a maintenance cadence with teeth.** Manual cadence drifts. Recommend the validator runs:
   - As a pre-commit hook (locally; opt-in initially).
   - In CI on every PR that touches `AGENTS.md`, `CLAUDE.md`, `opencode.json`, `.codex/config.toml`, or any `**/SKILL.md`.
   - As a periodic check (weekly) over the whole repo, run by the same agent that runs the documentation consistency pass.

9. **Update the source URLs.** Replace `https://code.claude.com/docs/en/...` with the canonical `https://docs.claude.com/en/docs/claude-code/...` (the former 301-redirects to a different host structure). Add the Agent Skills spec URL ([https://agentskills.io/specification](https://agentskills.io/specification)) as the floor every SKILL.md must satisfy.

10. **Resolve the open questions.** Don't ship a coordination plan with five unresolved questions. My answers:
    - **Q1 (CLAUDE.md size):** Short import-and-adapter, ≤80 lines, Claude-Code-specific only.
    - **Q2 (skill mirroring):** Generated mirror, Claude canonical.
    - **Q3 (OpenCode skill scope):** OpenCode-native in `.opencode/skills/`; everything else governed by `opencode.json` deny rules; manifest must enumerate which `.claude/`/`.agents/` skills are intentionally OpenCode-compatible.
    - **Q4 (Codex prefix):** Keep `codex-` prefix on Codex-specific skills. If a skill is genuinely shared, put it in `.claude/skills/` and let the generator mirror it; don't share via `.agents/`.
    - **Q5 (cadence):** Pre-commit + CI on touch + weekly full sweep.

## Agent-Specific Notes

These are observations about how this plan affects me (Claude Code) specifically.

- **`disable-model-invocation` and `paths`:** Many of our `.claude/skills/` use `disable-model-invocation: true` and `argument-hint` — Claude-Code-specific frontmatter. The mirrored `.agent/skills/` versions do not, which is correct per Antigravity's likely tolerance. The validator should not enforce frontmatter equivalence; it should enforce *content* equivalence after stripping known Claude-only fields.
- **Skill subagents (`context: fork`, `agent`):** These are Claude-Code-only. Any skill that uses them is, by definition, not portable. The manifest should mark such skills with `tool_compat: [claude]` and the mirror generator should refuse to produce a non-Claude copy.
- **Hooks scoped to skills:** `.claude/settings.json` already wires a `Stop` hook. Skills can also declare `hooks:` in frontmatter. The validator should read both and warn if a skill-scoped hook references files not in the skill directory (a portability hazard).
- **`/skill-name` invocation namespace:** Claude Code matches by `name` field with strict regex; Codex matches similarly per its docs. Cross-tool name collisions (e.g., `proj-start` exists in three places) are by design here, but if we ever introduce divergent content under the same name, Claude Code users invoking `/proj-start` will get one behavior and Antigravity users will get another. The mirror generator must keep the user-facing behavior identical.
- **`@AGENTS.md` import:** Claude Code supports `@path/to/file` imports in `CLAUDE.md`. Use that. (The Codex plan says "import" without naming the syntax.)
- **Bundled skills overlap:** Claude Code ships bundled skills (`/simplify`, `/loop`, `/security-review`, etc.) that this repo does not own. Repo skills that share a name with a bundled skill (e.g., a hypothetical `simplify` here) would have ambiguous resolution — bundled wins per the docs, but the validator should still flag the collision.

## Maintenance And Validation Suggestions

Concrete recommendations layered on the plan's "Future Validator" section:

- **Validator location and language:** `Tools/agent_coordination/validate_agent_surfaces.py`, stdlib only, Python 3.13+ to match repo. Tests at `tests/unit/tools/test_agent_coordination_validator.py`. Both paths are consistent with the plan.

- **Validator outputs:** human-readable summary to stdout, machine-readable JSON to `Reviews/results/{DATE}_AGENT_SURFACES/results.json` so the doc-consistency pass and project audits can consume it.

- **Manifest format:** YAML, not JSON. Easier to diff in PRs and the validator can use `tomllib` (stdlib) for `.codex/config.toml` plus `yaml` would add a dependency — better to write a tiny YAML parser or use TOML for the manifest too. If the plan insists on stdlib-only, use TOML for the manifest.

- **TDD test cases the plan should require (in addition to its list):**
  - A skill present in `.claude/skills/` but missing in `.agent/skills/` fails (when `mirror_policy: generated`).
  - A skill with `disable-model-invocation: true` in `.agent/skills/` fails (Claude-only field bled into a non-Claude surface).
  - A `SKILL.md` with `name` mismatched to its parent directory fails.
  - A `SKILL.md` with `description` over 1024 chars fails.
  - A `SKILL.md` with `name` violating `^[a-z0-9]+(-[a-z0-9]+)*$` fails.
  - `AGENTS.md` test-baseline string duplicated in `CLAUDE.md` fails.
  - A skill name added to `.claude/skills/` without a corresponding entry in `opencode.json` permissions fails (when not on the OpenCode allowlist).
  - `.claude/settings.local.json` tracked in git fails.

- **Cadence enforcement:** add a `pre-commit` hook config in the plan (separate file, not in `.git/hooks/`) so contributors opt in cleanly. Add a GitHub Actions workflow at `.github/workflows/agent_coordination.yml` that runs the validator on PRs touching the relevant paths.

- **One-time cleanup before validator goes green:**
  - Untrack `.claude/settings.local.json`, add to `.gitignore`.
  - Update or delete `.agent/workflows/*.md` (they are stale).
  - Decide and apply the mirror policy (option b above).
  - Trim `CLAUDE.md` to its adapter form.
  - Replace any `15405` references with `15477+` (only `CLAUDE.md` has them — the AGENTS.md baseline is current).
  - Reconcile `c:\Dev\Starship Battles` paths in `.claude/settings.local.json` (which then shouldn't be tracked anyway).

- **Documentation:** add a short `AgentCoordination/README.md` explaining the source-of-truth rule, the mirror policy, and how to add a new skill. New contributors will hit this folder first; the README should answer "where does this skill go?" in <60 seconds of reading.

- **Out of scope for this plan but worth tracking:** the `Projects/refactor_loop/WORKER.md` file is referenced from `CLAUDE.md` as "for automated CLI loop execution". I did not verify whether that file exists or is current. If it's a third agent surface (CLI-loop-mode worker instructions), it belongs in this coordination plan too.
