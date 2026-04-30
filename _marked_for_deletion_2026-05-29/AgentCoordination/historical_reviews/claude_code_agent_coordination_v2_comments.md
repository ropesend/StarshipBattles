# Claude Code V2 Review: Codex V2 Plan + Claim Responses

Author: Claude Code (Opus 4.7, 1M context)
Date: 2026-04-28
Reviews: [codex_agent_coordination_plan_v2.md](codex_agent_coordination_plan_v2.md), [codex_agent_coordination_claim_responses.md](codex_agent_coordination_claim_responses.md)

## Clarifying Questions

1. When you adopt the `claude-` / `anti-` / `deep-` / `codex-` prefix scheme, should existing user-facing slash invocations break (e.g. `/proj-start` → `/claude-proj-start`), or do you want a one-time atomic rename plus an `AgentCoordination/RENAMES.md` cheat sheet?
2. For skill usage counters, do you want passive telemetry (counter increments only) or session-aware tracking (last-used timestamp + invoking agent), and is the data allowed to be tracked in git or should it live in an ignored file?
3. Are you OK with deleting `.agent/workflows/` outright now (rather than waiting on Antigravity client confirmation), given your statement that they are stale and Antigravity is low-priority?

## Material Disagreements

### 1. V2's prefix policy contradicts your stated preference

V2 §"Skill Strategy" item 4 and Claim Response §17 both say: *"Keep `codex-` prefix for Codex-only skills. Use generic names only for skills intentionally designed and validated as shared."* Your priority #5 explicitly asks for `claude-`, `anti-`, `deep-`, and `codex-` prefixes on **all** skills. V2 keeps the asymmetric model where only Codex skills are prefixed. This is the largest gap between V2 and your stated direction.

The plan should be rewritten to:
- Prefix every existing skill (rename 32 in `.claude/skills/`, ~33 in `.agent/skills/`, 1 in `.opencode/skills/`).
- Reserve unprefixed names *only* for explicit cross-tool shared skills, recorded in the manifest.

This rename also dramatically **simplifies** OpenCode governance: `opencode.json` permissions collapse from the current 12-pattern deny list to roughly four rules (`deep-*` allow, everything else deny by default, plus per-skill exceptions). V2 should call out that benefit, not bury it.

### 2. V2 forbids load-bearing duplication; your priority #11 endorses it

V2 §"Core Decision": *"They must not restate shared rules, commands, architecture, test baselines, or project policy except as short references back to `AGENTS.md`."* Your priority #11 explicitly endorses some duplication for context-length-induced forgetfulness ("things like TDD, importance of documentation … taking up 1k of tokens to say things … is a worthwhile tradeoff").

The validator as currently scoped (Phase 3 test "`15405` duplicated in `CLAUDE.md` fails", "does not duplicate canonical test baselines or command blocks") will fail any deliberate reinforcement. Two distinct duplication classes need separate rules:

- **Stale duplication** (e.g. `15405`, `python -m unittest discover`) — must fail.
- **Reinforcement duplication** (TDD/docs/clean-sheet rules restated near the top of agent adapters) — must be allowed and tagged with `# reinforcement: <tag>` markers the validator recognizes.

V2 should add a "reinforcement allowlist" concept; otherwise the validator will fight your policy.

### 3. V2 still treats counts as policy text rather than generated artifacts

Your priorities #2 and #4 ask for automated test counts and skill counts. V2 §"OpenCode Visibility Is Load-Bearing" hand-counts skills (32, 8, 1) and the manifest design has no generation step. Codex's own V2 count is already wrong: I see **33** entries under `.agent/skills/` (not 32 — see Evidence below). V2 has been stale for one day.

The plan should make all counts derived:
- Sharded runner writes baseline (e.g. `.test_baseline.json`) on green runs; `AGENTS.md` references the file rather than embedding the integer.
- Validator emits `agent_surfaces_inventory.json` with current skill counts per surface; documentation links to it. No prose count anywhere.

### 4. V2 punts on `.agent/workflows/` and `.agent/MIGRATION_PROGRESS.md` deletion

V2 Phase 1 step 6: *"Decide whether `.agent/workflows/` should be deleted, replaced … or converted into skills."* You've already answered this in priority #7 ("`.agent` workflows are stale"). The plan should commit to **delete** rather than gate on Antigravity-client confirmation. Antigravity is your tooling-and-assets agent (priority #6), so the cost of deleting and re-adding later is trivial; the cost of keeping stale instructions live for any agent that wanders in is real.

Same for `.agent/MIGRATION_PROGRESS.md` — V2 says "replace it with a living manifest after the manifest exists." It can be deleted **now**; it is actively misleading (claims 26 migrated when reality is 32+33).

### 5. V2's `.claude/settings.local.json` policy ignores your solo-developer context

V2 §"Important Correction About Paths": *"`.claude/settings.local.json` should not be tracked at all."* Your priority #3 asked for technical pros/cons given you're the only developer. V2 doesn't engage with the question.

Pros of tracking it (solo developer):
- The growing permission allowlist (currently ~200 entries) acts as a session-bootstrap snapshot — fewer permission prompts after a `git reset`.
- Settings move with the workspace across machines.
- Diffs surface accidental over-permissioning that would otherwise hide in user-only state.

Cons (still apply solo):
- Embeds absolute paths (`c:\\Dev\\Starship Battles\\...`) that go stale per priority #1 (multiple paths in use).
- Mixes user-mutable state with versioned config — `git status` is noisy after every Claude session.
- Becomes a leak risk if you ever onboard a contributor or share the repo publicly.
- Claude Code may rewrite the file format in a future release; tracked merge conflicts are annoying.

Recommendation: **don't track it**, but only because of the embedded paths. If the path entries can be normalized to repo-relative globs (Claude Code's permission syntax permits `**`-style patterns), tracking becomes net-positive for your case. V2 should make this conditional rather than absolute.

## Corrections To Codex Claim Responses

**Claim Response #5** ("path prefix proves staleness") — Codex is right that the prefix isn't itself the bug, but the response misframes Claude Code's earlier point. Claude Code's review flagged the file because it's *tracked while containing a per-machine absolute path*. That's the same conclusion V2 reaches; the responses dismiss the original framing more harshly than warranted. Net: agree on the action, disagree on the characterization.

**Claim Response #20** ("32/32 mirrors") — Local count is **32 / 33**, not 32 / 32. `.agent/skills/` has one more directory than `.claude/skills/`. Combined with the Claude-only and Antigravity-only name lists, the sets diverge by 7 names total, not 7 (4 Antigravity-only would imply +1, not +0). The arithmetic in §22 should be re-checked once and then automated (priority #4) so this never matters again.

**Claim Response #21** ("Claude frontmatter still in `.agent/skills/`") — Codex says "several files." Actual count: **19 of 33** `.agent/skills/*/SKILL.md` files contain `disable-model-invocation` or `argument-hint`. That's 58%, not "several." V2 should treat this as the dominant state and design the mirror generator to strip on every sync, not as an exception.

**Claim Response #30** ("docs.claude.com vs code.claude.com") — Codex's response is technically correct (both work). But `https://docs.claude.com/en/docs/claude-code/skills` is the canonical published URL; `code.claude.com` is the post-redirect host. Either is fine for V2's source list, but if the validator ever URL-checks docs links, it should follow redirects, not require a particular host.

**Claim Response #34** ("integrate validator into sharded suite") — V2 defers this. Reasonable, but combine with priority #2: if the sharded runner is going to write the test baseline file anyway, that's the natural moment to invoke the validator as a fast post-step. One coordinated post-test write is simpler than two separate hooks.

## New Suggestions

1. **Mass rename (priority #5) lands in Phase 1, not later.** Once committed to prefixes, do all renames in one PR — multiple partial renames will be worse than one large one for cross-skill `/skill-name` references in protocol Markdown files (currently many; e.g. `proj-extract-phase` references `proj-start`). Validator should grep for unprefixed names in Markdown bodies after the rename.
2. **Skill usage counter design.** Implement via Claude Code skill-scoped hooks (`hooks:` in frontmatter, on `PostToolUse` for the Skill tool itself, or a `SkillStart` lifecycle event if available). The hook appends to `.skill_usage.jsonl` (gitignored). A monthly `claude-skill-prune` skill summarizes usage and proposes purges. Codex/OpenCode/Antigravity won't write to this file, but cross-tool usage matters less than knowing which skills you've never invoked from any agent.
3. **Reinforcement duplication marker.** Convention: `<!-- reinforcement: tdd -->` HTML-comment markers in adapter files mark sections as deliberately duplicated. Validator extracts these into a stable list and only fails when an unmarked block matches a canonical AGENTS.md block above a similarity threshold (e.g. 80% line overlap).
4. **Per-prefix opencode.json template.** With prefixes, `opencode.json` simplifies to: `deep-*: allow`, `claude-*: deny`, `anti-*: deny`, `codex-*: deny`, plus per-skill overrides for any cross-tool shared skill. V2's current 12-pattern deny list disappears.
5. **Test baseline file location.** `.test_baseline.json` at repo root, written by the sharded runner on green runs. Schema: `{"passed": int, "skipped": int, "duration_seconds": float, "timestamp": iso8601, "git_sha": str}`. `AGENTS.md` references the file path, not the number.
6. **Skill prefix migration script.** A one-shot Python script under `Tools/agent_coordination/rename_skills_with_prefixes.py` that: renames directories, updates `name:` frontmatter, rewrites internal cross-references, and emits a `before → after` map for `AgentCoordination/SKILL_RENAMES.md`.

## Evidence Links And File References

- Skill counts (verified locally): `.claude/skills/` = 32 dirs, `.agent/skills/` = **33** dirs (not 32 as V2 claims), `.agents/skills/` = 8 dirs, `.opencode/skills/` = 1 dir.
- Claude frontmatter leakage in `.agent/skills/`: `grep -l "argument-hint\|disable-model-invocation" .agent/skills/*/SKILL.md | wc -l` = **19 of 33** files.
- `.claude/settings.local.json` tracking: `git ls-files .claude/settings.local.json` returns the file (still tracked at time of review).
- `CLAUDE.md` line count: 353 lines. `AGENTS.md`: 80 lines.
- Cross-skill references: `.claude/skills/proj-extract-phase/`, `.claude/skills/proj-parallel/`, `.claude/skills/proj-start/` all reference `proj-start` by name in their bodies — confirms a rename touches multiple files and must be atomic.
- Agent Skills spec on naming: [agentskills.io/specification](https://agentskills.io/specification) — name regex `^[a-z0-9]+(-[a-z0-9]+)*$`, max 64 chars. Prefixes like `claude-proj-start` (16 chars) are fine.
- Claude Code skill hooks (for usage counter idea): [code.claude.com/docs/en/skills](https://code.claude.com/docs/en/skills) — `hooks:` frontmatter field documented.
- OpenCode discovers `.opencode/skills/`, `.claude/skills/`, `.agents/skills/`: [opencode.ai/docs/skills](https://opencode.ai/docs/skills/) — confirms why prefix renaming simplifies the deny list.
- Codex skill discovery limited to `.agents/skills/`: [developers.openai.com/codex/skills](https://developers.openai.com/codex/skills) — confirms `codex-` prefix remains useful even with universal prefixing.

## Final Recommendation

V2 is structurally sound but is one revision behind your stated priorities. Before any tooling work begins, V2 needs three explicit policy commitments it currently lacks: (a) universal `<agent>-<skill>` prefixing with a one-shot rename, (b) a reinforcement-duplication allowlist so the validator doesn't fight intentional repetition, and (c) automated counts (tests + skills) replacing every prose count in agent docs. Once those are in, the manifest + validator design in V2 is the right foundation. The `.claude/settings.local.json` decision should be made conditional on whether you can normalize away absolute paths; the absolute path is the real bug, not the tracking.
