# Codex Responses To Agent Coordination Review Claims

Author: Codex
Date: 2026-04-29

## Method

I reviewed these files:

- `AgentCoordination/antigravity_agent_coordination_comments.md`
- `AgentCoordination/claude_code_agent_coordination_comments.md`
- `AgentCoordination/opencode_deepseek_v4_pro_agent_coordination_comments.md`
- Local agent surfaces under `AGENTS.md`, `CLAUDE.md`, `opencode.json`,
  `.codex/`, `.agents/`, `.agent/`, `.claude/`, and `.opencode/`

I also checked current primary or official docs where available. Repeated claims
from multiple agents were treated as stronger evidence, but still checked
against local files and current documentation.

User note applied: different agents may use different parent workspace paths,
as long as they end in `StarshipBattles\...`. Therefore path-prefix differences
alone are not drift.

## Sources Used

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

## Summary

Most structural claims were verified:

- `AGENTS.md` should be the shared source of truth.
- Tool-specific files should be thin adapters.
- OpenCode's multi-surface skill discovery must be governed.
- `.claude/settings.local.json` should not be tracked.
- `CLAUDE.md` has stale duplicated content.
- `.agent/workflows/` contains stale references.
- A manifest plus TDD-built validator is the right enforcement mechanism.

Important corrections:

- The claim that the actual workspace is `C:\Developer\StarshipBattles` is
  false for this Codex session. The current root is `C:\Dev2\StarshipBattles`.
  More importantly, validators should not hardcode either prefix.
- The claim that `.claude/skills/` and `.agent/skills/` are 26-skill mirrors is
  stale. Current local state is 32 and 32, with mismatched names.
- The claim that Antigravity pathing is definitely `.agent/skills/` only is too
  strong. Google codelabs show both `.agent/skills` and `.agents/skills` in
  different contexts.
- The claim that `.agent/skills/` has stripped Claude frontmatter is false
  locally; several `.agent/skills/*/SKILL.md` files still contain
  `disable-model-invocation` or `argument-hint`.
- A root `Skills/` directory is not supported as a direct discovery location by
  the checked official docs. It can be a future source-generation directory, not
  the runtime adapter location.

## Claim Responses

### 1. `AGENTS.md` should be the shared source of truth.

Verdict: Verified and accepted.

Evidence:

- Codex documents `AGENTS.md` as the project instruction discovery file:
  https://developers.openai.com/codex/guides/agents-md
- OpenCode states `AGENTS.md` is standard and uses `CLAUDE.md` only as a
  fallback when `AGENTS.md` is absent: https://opencode.ai/docs/rules/
- Local `opencode.json` already has `instructions: ["./AGENTS.md"]`.
- Local `.agents/CODEX.md` already says to read `AGENTS.md` first.

V2 response: Keep this as the central decision.

### 2. Tool-specific files should be thin adapters.

Verdict: Verified and accepted.

Evidence:

- Local `CLAUDE.md` is 353 lines and duplicates rules, commands, architecture,
  and test baseline content already present in `AGENTS.md`.
- Local `.agents/CODEX.md` is 38 lines and is a better adapter model.

V2 response: `CLAUDE.md` should import/reference `AGENTS.md` and retain only
Claude-specific behavior. `opencode.json`, `.codex/config.toml`, and
`.agents/CODEX.md` should stay tool-specific.

### 3. `CLAUDE.md` has stale test baseline content.

Verdict: Verified.

Evidence:

- `CLAUDE.md` line 147 says `15405 tests baseline`.
- `CLAUDE.md` line 319 says `15405 passed, 2 skipped`.
- `AGENTS.md` line 67 says `15477+ tests baseline`.

V2 response: Replace or remove the duplicated baseline from `CLAUDE.md`; keep
the baseline in `AGENTS.md`.

### 4. `.claude/settings.local.json` is tracked and should not be.

Verdict: Verified.

Evidence:

- `git ls-files .claude/settings.local.json` returns the file.
- `.gitignore` does not contain `/.claude/settings.local.json`.
- Claude Code settings docs distinguish project settings and local settings:
  https://code.claude.com/docs/en/settings

V2 response: Add `/.claude/settings.local.json` to `.gitignore` and untrack the
file.

### 5. The specific path prefix in `.claude/settings.local.json` proves the file is stale.

Verdict: Refuted as stated; narrowed.

Evidence:

- The current Codex session root is `C:\Dev2\StarshipBattles`.
- Claude Code claimed the actual workspace was `C:\Developer\StarshipBattles`,
  which is not true for this session.
- The user explicitly noted that multiple parent paths can be valid as long as
  they end in `StarshipBattles\...`.

V2 response: The bug is not the exact prefix. The bug is that a tracked local
settings file contains absolute machine-local paths. The validator must derive
repo root dynamically and must not hardcode `C:\Dev2`, `C:\Developer`, or
`C:\Dev`.

### 6. OpenCode reads `.opencode/skills/`, `.claude/skills/`, and `.agents/skills/`.

Verdict: Verified.

Evidence:

- OpenCode skills docs list project skills from `.opencode/skills/`,
  `.claude/skills/`, and `.agents/skills/`: https://opencode.ai/docs/skills/

V2 response: The OpenCode deny list is a governed artifact, not a convenience.
Every visible non-compatible skill must be denied or explicitly marked
compatible.

### 7. OpenCode does not read `.agent/skills/` singular.

Verdict: Verified against the checked OpenCode docs.

Evidence:

- OpenCode skill docs list `.opencode/skills/`, `.claude/skills/`, and
  `.agents/skills/`, not `.agent/skills/`: https://opencode.ai/docs/skills/

V2 response: `.agent/skills/` is not an OpenCode-visible surface under the
documented model. OpenCode governance applies to `.claude/skills/` and
`.agents/skills/`.

### 8. The `opencode.json` deny list is load-bearing.

Verdict: Verified and accepted.

Evidence:

- Local `opencode.json` has `permission.skill` with `* = allow` and explicit
  deny patterns for `proj-*`, `ticket-*`, `codex-*`, `analysis-*`, `debug-*`,
  `deep-dive-*`, `qa-*`, `fix-crash`, `loc`, `triage-to-proj`, and
  `validate-designs`.
- OpenCode permissions docs cover pattern-based permission rules:
  https://opencode.ai/docs/permissions/

V2 response: Validator must enforce deny/allow coverage for all OpenCode-visible
skills.

### 9. Only `audit-shrink` is intentionally OpenCode-native today.

Verdict: Verified locally.

Evidence:

- `.opencode/skills/` contains only `audit-shrink`.
- Current `.claude/skills/` and `.agents/skills/` names are covered by deny
  patterns in `opencode.json`.

V2 response: Keep `audit-shrink` as the only known OpenCode-native skill unless
the manifest intentionally marks another skill compatible.

### 10. OpenCode does not use Claude `@AGENTS.md` import syntax.

Verdict: Verified.

Evidence:

- OpenCode docs use `AGENTS.md` discovery and `opencode.json` `instructions`;
  they do not document Claude-style `@path` imports:
  https://opencode.ai/docs/rules/
- Claude Code memory docs document imports in Claude memory files:
  https://code.claude.com/docs/en/memory

V2 response: The plan now treats import mechanisms as tool-specific:
Claude Code can use `@AGENTS.md`; OpenCode uses `opencode.json`
`instructions`.

### 11. OpenCode ignores unknown frontmatter fields.

Verdict: Verified.

Evidence:

- OpenCode skills docs state unknown frontmatter fields are ignored:
  https://opencode.ai/docs/skills/

V2 response: This reduces breakage risk but increases behavioral risk, because
Claude-specific guardrails may silently not apply in OpenCode. Deny-list
governance remains required.

### 12. OpenCode requires unique skill names across all locations.

Verdict: Verified for OpenCode-visible locations.

Evidence:

- OpenCode skills docs say to ensure skill names are unique across all
  locations: https://opencode.ai/docs/skills/

V2 response: The validator should check duplicate names across OpenCode-visible
surfaces: `.opencode/skills/`, `.claude/skills/`, and `.agents/skills/`.
Duplicates involving `.agent/skills/` are not OpenCode duplicates unless the
current OpenCode behavior changes.

### 13. Codex scans `.agents/skills/`.

Verdict: Verified, with nuance.

Evidence:

- Codex skills docs say repo skills are discovered under `.agents/skills` from
  the current directory up to the repo root, plus user/admin/system locations:
  https://developers.openai.com/codex/skills

V2 response: `.agents/skills/` remains Codex-owned in this repo. The word
"only" should be avoided unless scoped to repo-local Starship Battles adapter
surfaces.

### 14. Codex does not document `CLAUDE.md` as a default fallback.

Verdict: Verified.

Evidence:

- Codex AGENTS.md docs say fallback names come from
  `project_doc_fallback_filenames`:
  https://developers.openai.com/codex/guides/agents-md
- Codex config reference documents `project_doc_fallback_filenames`:
  https://developers.openai.com/codex/config-reference
- Local `.codex/config.toml` sets
  `project_doc_fallback_filenames = ["CLAUDE.md"]`.

V2 response: The fallback is repo-configured, not a Codex default.

### 15. `.agents/skills/` contains 7 Codex skills.

Verdict: Refuted locally.

Evidence:

- Local `.agents/skills/` currently contains 8 directories:
  `codex-ship-theme-creator`, `codex-starship-analysis-review`,
  `codex-starship-combat-lab`, `codex-starship-design-assets`,
  `codex-starship-performance-profiling`, `codex-starship-project-system`,
  `codex-starship-qa-observer`, and `codex-starship-ticket-system`.

V2 response: V2 uses the current count of 8.

### 16. Each Codex skill has `agents/openai.yaml`.

Verdict: Verified locally.

Evidence:

- Each of the 8 `.agents/skills/codex-*` directories contains
  `agents/openai.yaml`.

V2 response: Keep this as a Codex skill convention and validate it if Codex UI
metadata remains required.

### 17. Codex-specific skills should keep the `codex-` prefix.

Verdict: Verified as a good repo policy, not an official requirement.

Evidence:

- Codex docs require skill `name` and `description`, but do not require a
  `codex-` prefix: https://developers.openai.com/codex/skills
- Local `.agents/CODEX.md` already states Codex-specific skills are prefixed
  `codex-`.
- OpenCode sees `.agents/skills/`, so the prefix helps deny and identify
  Codex-specific skills.

V2 response: Keep the prefix for Codex-specific skills. Shared portable skills
may use generic names only with manifest-backed compatibility.

### 18. The Agent Skills spec sets name and description constraints.

Verdict: Verified.

Evidence:

- Agent Skills spec: https://agentskills.io/specification
- The reviewed claims about lowercase kebab-case names, directory/name match,
  max name length, and description length align with the spec.

V2 response: The validator should enforce those constraints.

### 19. Claude Code supports Agent Skills plus Claude-specific extensions.

Verdict: Verified.

Evidence:

- Claude Code skills docs: https://code.claude.com/docs/en/skills
- Local `.claude/skills/*/SKILL.md` files use Claude-specific fields such as
  `disable-model-invocation` and `argument-hint`.

V2 response: Claude-specific fields are allowed in `.claude/skills/` but should
not leak into other adapters unless explicitly supported or waived.

### 20. `.claude/skills/` and `.agent/skills/` are 26-skill mirrors.

Verdict: Refuted locally; this is stale.

Evidence:

- Local `.claude/skills/` has 32 directories.
- Local `.agent/skills/` has 32 directories.
- `.agent/MIGRATION_PROGRESS.md` says 26 migrated, so that file is stale.
- The sets are not identical:
  - Claude-only: `debug-parallel`, `deep-dive-parallel`, `proj-parallel`.
  - Antigravity-only: `debug-sequential`, `deep-dive-sequential`,
    `proj-close`, `proj-sequential`.

V2 response: Replace migration snapshot tracking with a living manifest and
mirror policy.

### 21. `.agent/skills/` has stripped Claude-specific frontmatter.

Verdict: Refuted locally.

Evidence:

- Local `.agent/skills/qa-triage/SKILL.md`,
  `.agent/skills/ticket-work/SKILL.md`, and many other `.agent/skills/` files
  still contain `disable-model-invocation` and/or `argument-hint`.

V2 response: If `.agent/skills/` remains the Antigravity adapter, a generator or
validator should normalize frontmatter according to confirmed Antigravity
support.

### 22. Antigravity uses `.agent/skills/` singular.

Verdict: Partially verified, but not stable enough for a hard policy.

Evidence:

- The Google Antigravity skills codelab shows `.agent/skills/`:
  https://codelabs.developers.google.com/getting-started-with-antigravity-skills
- The Google Antigravity getting-started codelab discusses `.agents/skills`,
  `.agents/rules`, and `.agents/workflows`:
  https://codelabs.developers.google.com/getting-started-google-antigravity
- The local repo uses `.agent/skills/` and `.agent/workflows/`, while
  `.agents/skills/` is already Codex-owned.

V2 response: Treat Antigravity pathing as an explicit open question. Do not
rename or collapse these surfaces until the installed Antigravity client
behavior is confirmed.

### 23. Antigravity already consumes `.agents/skills/` in this repo.

Verdict: Unverified from this Codex session.

Evidence:

- Antigravity's own review claims it sees `.agents/skills/`.
- Google codelabs conflict, as noted above.
- Codex cannot inspect Antigravity's live runtime state from this session.

V2 response: Do not base repository policy on an unverified runtime claim.
Record it as something Antigravity must confirm with a reproducible command or
current official source.

### 24. Antigravity reads `AGENTS.md`.

Verdict: Plausible but not fully verified by the sources I could confirm.

Evidence:

- Antigravity review and other agents claimed this.
- Google Antigravity getting-started codelab discusses rules/workflows under
  `.agents/`, but the verified excerpts did not settle every repo instruction
  discovery detail.

V2 response: Keep `AGENTS.md` as source of truth anyway, because Codex and
OpenCode verify it and because Antigravity reviewers can read it directly.
Require Antigravity to confirm exact automatic discovery behavior.

### 25. A root `Skills/` or `.shared_skills/` directory should replace all skill surfaces.

Verdict: Refuted as a direct runtime plan.

Evidence:

- Claude Code docs use `.claude/skills/` for project skills:
  https://code.claude.com/docs/en/skills
- OpenCode docs use `.opencode/skills/`, `.claude/skills/`, and
  `.agents/skills/`: https://opencode.ai/docs/skills/
- Codex docs use `.agents/skills/`: https://developers.openai.com/codex/skills
- Google codelabs point to `.agent/skills` or `.agents/skills`, not root
  `Skills/`.

V2 response: A neutral source directory could be introduced later for
generation, but native adapter directories must remain the runtime locations.

### 26. Remove all agent prefixes from skills.

Verdict: Refuted as a blanket rule.

Evidence:

- Agent Skills allows generic skill names, but does not require them:
  https://agentskills.io/specification
- OpenCode sees `.agents/skills/`, so `codex-*` names help keep Codex-specific
  skills identifiable and denyable.

V2 response: Keep `codex-` for Codex-only skills. Use generic names only for
skills intentionally designed and validated as shared.

### 27. `.agent/workflows/` files are stale.

Verdict: Verified.

Evidence:

- `.agent/workflows/run-tests.md` uses `python -m unittest discover -s tests -v`
  instead of the canonical sharded runner in `AGENTS.md`.
- `.agent/workflows/resolve_bug.md` references missing
  `docs/bug_tracker.md` and `docs/lessons_learned.md`.
- `.agent/workflows/generate_ship_theme.md` references missing
  `assets/tools/ship_background_remover.py`; local tool path is
  `Tools/ship_background_remover/ship_background_remover.py`.

V2 response: Treat `.agent/workflows/` as stale/unverified. Decide whether to
delete, migrate, or convert to skills after Antigravity path behavior is
confirmed.

### 28. `.agent/workflows/` should be deleted, not repaired.

Verdict: Partially accepted as the default recommendation, but not a verified
fact.

Evidence:

- Staleness is verified.
- Whether Antigravity still uses these files is not verified from this Codex
  session.
- Google getting-started codelab mentions `.agents/workflows`, not local
  `.agent/workflows`.

V2 response: Plan a decision step. Default recommendation is delete or convert
to skills, not repair in place, unless Antigravity confirms the surface is
active.

### 29. `CLAUDE.md` should be capped around 80 lines.

Verdict: Partially accepted as a project target, not an official hard limit.

Evidence:

- Claude Code memory docs advise keeping memory files concise and target under
  200 lines: https://code.claude.com/docs/en/memory
- Local `.agents/CODEX.md` is 38 lines and demonstrates a thin adapter.

V2 response: Set target 80-120 lines and hard cap 200 lines unless justified.

### 30. Claude Code docs canonical URL should be `docs.claude.com`, not `code.claude.com`.

Verdict: Refuted as stated.

Evidence:

- The checked Claude docs are available at `https://code.claude.com/docs/en/...`.
- `https://docs.claude.com/en/docs/claude-code/...` redirects to the Claude
  Code docs host in current browsing.

V2 response: Either URL is acceptable in human-facing docs, but V2 uses the
working `code.claude.com` URLs that resolved during verification.

### 31. The future manifest should be TOML rather than JSON.

Verdict: Accepted as a better implementation detail.

Evidence:

- Python 3.13 includes `tomllib` for reading TOML.
- TOML supports comments, which are useful for compatibility reasons and
  waivers.
- JSON comments are not valid JSON.

V2 response: Use `AgentCoordination/agent_surfaces.toml` for the future
manifest unless a later implementation task finds a stronger reason not to.

### 32. Validator should be stdlib-only and TDD-built.

Verdict: Verified as consistent with repo policy and accepted.

Evidence:

- `AGENTS.md` requires strict TDD for code changes.
- Python 3.13+ is the repo convention.

V2 response: Future validator task must write failing tests first and should
avoid new dependencies.

### 33. Validator should run in CI, pre-commit, and periodic sweeps.

Verdict: Accepted as a maintenance recommendation.

Evidence:

- This is process guidance rather than an externally verifiable fact.
- It aligns with the drift problem the user described.

V2 response: V2 recommends manual runs first, then opt-in pre-commit, PR CI on
agent-surface changes, and scheduled/release sweeps.

### 34. Validator should be integrated directly into the full sharded test suite.

Verdict: Partially accepted.

Evidence:

- Agent docs are important, but the future validator is not implemented yet.
- The sharded runner is the canonical full test command in `AGENTS.md`.

V2 response: Start with a dedicated fast validator and CI trigger. Decide later
whether to include it in the full sharded suite once runtime and flake behavior
are known.

### 35. `.agent/MIGRATION_PROGRESS.md` should be replaced.

Verdict: Verified.

Evidence:

- It says 26 skills were migrated.
- Current local counts are 32 `.claude/skills/` and 32 `.agent/skills/`.
- It does not explain current name mismatches.

V2 response: Replace it with a living manifest after the manifest exists.

### 36. `.opencode/package.json` and `.opencode/node_modules/` are present and may need ignoring.

Verdict: Refuted locally.

Evidence:

- Local `.opencode/` contains only `skills/`.
- `git ls-files .opencode` returns only `.opencode/skills/audit-shrink/SKILL.md`.

V2 response: No action in V2. Revisit only if those artifacts appear.

### 37. `Projects/refactor_loop/WORKER.md` exists and is another instruction surface worth inventorying.

Verdict: Verified.

Evidence:

- `CLAUDE.md` references `Projects/refactor_loop/WORKER.md`.
- The file exists locally.
- `Projects/README.md` documents multiple automated loop worker files.

V2 response: Inventory `Projects/*/WORKER.md` style files in the manifest so
they do not drift silently, but do not treat them as general agent adapters.

### 38. `CLAUDE.md` contains mostly duplicated shared content and only a small Claude-specific portion.

Verdict: Verified directionally.

Evidence:

- `CLAUDE.md` has 353 lines.
- It restates TDD, documentation order, project structure, commands,
  architecture, conventions, and baseline content that belong in `AGENTS.md`
  or `docs/`.
- Claude-specific content includes interactive consultant framing,
  `.agent_reports/`, and subagent report conventions.

V2 response: Trim `CLAUDE.md` to import/reference `AGENTS.md` and keep only
Claude-specific guidance.

### 39. Shared portable skills should conform to Agent Skills spec.

Verdict: Verified and accepted.

Evidence:

- Agent Skills spec defines the portable floor:
  https://agentskills.io/specification
- Codex and Claude Code explicitly build on the Agent Skills concept in their
  skill docs.

V2 response: Validator should enforce the spec for every shared or portable
skill and should warn when tool-specific extensions reduce portability.

### 40. Codex and Antigravity can seamlessly consume all shared unprefixed skills.

Verdict: Refuted as an unsupported generalization.

Evidence:

- Codex only documents repo skill discovery in `.agents/skills`, not
  `.claude/skills`, `.agent/skills`, or a root shared directory:
  https://developers.openai.com/codex/skills
- Antigravity path docs are currently ambiguous across Google codelabs.
- Local `.agent/skills/` includes Claude-specific frontmatter that may or may
  not be valid for Antigravity.

V2 response: Shared skills are allowed only after explicit compatibility is
recorded and validated.

## Net Changes Made In V2

V2 changes the original Codex plan in these ways:

1. Replaces path-prefix drift with a dynamic-root policy.
2. Promotes OpenCode deny-list governance to a first-class requirement.
3. Treats Antigravity pathing as unresolved because official Google codelabs
   conflict.
4. Uses current local skill counts and name differences.
5. Keeps native skill adapter directories instead of moving runtime skills to a
   root `Skills/` directory.
6. Keeps `codex-` prefixes for Codex-specific skills.
7. Recommends TOML for the future manifest.
8. Treats `.agent/workflows/` as stale/unverified and likely deprecated.
9. Adds `Projects/*/WORKER.md` style automation prompts to the future inventory.
10. Sets `CLAUDE.md` as a short adapter with a project target below the official
    Claude memory guidance cap.
