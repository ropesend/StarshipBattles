# OpenCode (DeepSeek V4 Pro) Review: Codex Agent Coordination Plan V2

Author: OpenCode with DeepSeek V4 Pro
Date: 2026-04-29
Reviews: [codex_agent_coordination_plan_v2.md](codex_agent_coordination_plan_v2.md), [codex_agent_coordination_claim_responses.md](codex_agent_coordination_claim_responses.md), [user_response.md](user_response.md)

## Clarifying Questions

None. User priorities are clear from `user_response.md`.

## Material Disagreements

### 1. Skill naming: V2 preserves unprefixed names; user requires prefixes

V2 says "Keep `codex-` for Codex-only skills" and preserves unprefixed names for Claude/Antigravity/OpenCode skills. The user explicitly states:

> *"I would like for All SKILLS to be given a prefix specific to the agent/system they are designed for: claude-, anti-, deep-, codex-"*

This is the single largest gap. None of the 32 `.claude/skills/` names carry a `claude-` prefix. None of the 32 `.agent/skills/` names carry an `anti-` prefix. The sole `.opencode/skills/audit-shrink` lacks a `deep-` prefix. Only `.agents/skills/` (8 skills) already has `codex-` prefixes.

V2's claim response #22 says "Keep `codex-` for Codex-specific skills. Use generic names only for skills intentionally designed and validated as shared." This directly contradicts the user's stated preference.

This also invalidates parts of the V2 drift list. If skills are renamed (e.g., `proj-start` → `claude-proj-start`), every reference in `opencode.json`, `.agents/CODEX.md`, and skill bodies must update. The deny patterns in `opencode.json` change from `proj-*` to `claude-proj-*`, etc.

### 2. `.claude/settings.local.json`: V2 asserts untracked; user wants technical discussion

V2 says it "Must be untracked and ignored." The user says:

> *"is there a good reason not to track this... There is only one user (me) and no one else develops this program"*

The V2 plan assumes a team setting without addressing the single-developer case. Technical trade-offs for tracking:

- **Pro tracking**: Single dev means no path conflicts; Claude Code settings docs distinguish project/local but don't forbid tracking local if it contains only project-relevant permissions; allows reproducible Claude environment.
- **Con tracking**: Absolute machine paths will break on any machine move, drive letter change, or second dev; the file is machine-local by definition (per Claude Code docs); `git clone` on another machine would start with broken settings; permissions like `Bash(pytest:*)` and `Bash(pip install:*)` are reasonable to track, but the many `c:\Dev\Starship Battles` absolute paths are not.

**Recommendation**: Split into two approaches. Track a `.claude/settings.project.json` with repo-shared permissions and hooks (already `settings.json` serves this). Keep `settings.local.json` untracked but document its purpose and syntax in `AgentCoordination/README.md`. The validator should flag tracked local settings files regardless.

### 3. Automated counts are absent from V2

User wants test baseline and skill counts automated:

> *"maintaining an exact count of the total number of tests seems like something that should be automated"*
> *"counts of skills should be an automatable thing as well"*

V2 still lists manual counts (`15477+`, "32 skill directories"). V2 adds no mechanism for automation. The sharded test runner can write counts to a file. A simple script can count skill directories. Neither is proposed.

This matters because V2's validator checks for `15405` as a stale string but the `15477+` in AGENTS.md will itself go stale. A validator checking for manual baselines is checking a symptom rather than the root cause (manual maintenance).

### 4. Skill usage counters not addressed

User is interested in tracking skill usage (e.g., Claude's built-in skill metrics):

> *"to have some sort of counter associated with each skill so it tracks how often the skill is used. Unused skills could be purged and removed."*

V2 has no mechanism for this. This ties directly to the cleanup problem — without usage data, deciding which skills to delete is guesswork. Claude Code offers `scheduled_tasks.lock` (present locally) and may have usage tracking; OpenCode does not. This should be an explicit open question or Phase 2 research item.

### 5. V2 treats all duplication as drift; user says some is intentional

User on 1M-token context windows:

> *"you get a little forgetful when you are getting into the upper half of your context window. For that reason some things are deliberately in multiple places... taking up 1k of tokens to say things an extra time or two... is a worthwhile tradeoff."*

V2's drift list item #1 flags `CLAUDE.md` duplicating shared policy as drift to fix. V2's validator says duplicated test baselines and command blocks should fail.

This creates tension: removing ALL duplication from adapters eliminates the redundancy the user values for context-window reliability. The validator should distinguish between "stale duplication" (wrong test baseline `15405`) and "intentional reinforcement" (restating TDD requirements in an adapter that may be read by a context-saturated agent).

## Corrections To Codex Claim Responses

### Claim response #9: "Only audit-shrink is intentionally OpenCode-native today"

Correct locally but needs updating. If the user's prefix requirement is applied, this becomes `deep-audit-shrink`. The deny list and all references must update.

### Claim response #21: ".agent/skills/ has stripped Claude-specific frontmatter"

Verdict of "refuted locally" is correct (19 of 32 Antigravity skills still contain `disable-model-invocation` or `argument-hint` per verified local state). This is not corrected — it's confirmed.

### Claim response #22: "Antigravity uses .agent/skills/ singular"

V2 says "Treat Antigravity pathing as an explicit open question." This is reasonable given conflicting Google codelabs. However, since Antigravity is lower-priority per user ("the least reliable with large code bases — it mostly is used for tools and asset generation"), spending V2 effort on resolving this ambiguity may not be the highest-value task. Recommend deferring Antigravity path resolution until after the workhorse agents are aligned.

### Claim response #36: ".opencode/package.json and .opencode/node_modules/"

Verdict of "refuted locally" is correct. The earlier claim in Claude Code's V1 review was based on truncated directory listing displaying `node_modules/` entries. Local `.opencode/` contains only `skills/audit-shrink/SKILL.md`. No action needed.

## New Suggestions

### 1. Add a prefix renaming phase as highest priority

The user's prefix requirement (`claude-`, `anti-`, `deep-`, `codex-`) should be Phase 1, before any other cleanup. It affects every surface. Sequence:

1. Rename all 32 `.claude/skills/X` → `.claude/skills/claude-X`
2. Rename all 32 `.agent/skills/X` → `.agent/skills/anti-X`
3. Rename `.opencode/skills/audit-shrink` → `.opencode/skills/deep-audit-shrink`
4. Update all `SKILL.md` `name:` frontmatter fields
5. Update `opencode.json` deny patterns: `proj-*` → `claude-proj-*`, `ticket-*` → `claude-ticket-*`, `codex-*` stays, `analysis-*` → `claude-analysis-*`, `debug-*` → `claude-debug-*`, `deep-dive-*` → `claude-deep-dive-*`, `qa-*` → `claude-qa-*`, individual denies → `claude-fix-crash`, `claude-loc`, etc.
6. Update `.agents/CODEX.md` skill routing references
7. Update `CLAUDE.md` if it references specific skill names
8. Update `.codex/config.toml` if it references skill names
9. Update `opencode.json` command template: `"audit-shrink"` → `"deep-audit-shrink"`
10. Update `AGENTS.md` tooling notes reference to `audit-shrink` → `deep-audit-shrink`

### 2. Automate test baseline instead of validating it

Rather than having the validator check for specific stale strings (which will always drift), have the sharded test runner write `{total} passed, {skipped} skipped` to a file (e.g., `Reviews/latest_test_baseline.txt`), and have the validator compare `AGENTS.md`'s claimed baseline against the automated count. This fixes the root cause.

### 3. Add a skill inventory script as a pre-validator step

Before the manifest exists, a simple script:

```powershell
# Tools/agent_coordination/list_skills.ps1
# Outputs: directory / name / description / lines / has_claude_frontmatter
```

This feeds the validator and the manifest. The manifest can be partially generated from live state, with manual annotations for compatibility decisions.

### 4. Add intentional-duplication waivers to manifest schema

The manifest schema should include a field for intentional duplication:

```toml
[adapter_records.CLAUDE_md]
intentional_duplications = [
  "TDD rule restatement (context-window reinforcement per user_response.md §11)",
  "Documentation reading order (critical for agents unfamiliar with repo)"
]
```

Items marked as intentional redundancy should not fail the validator. Only items NOT in this list should fail if duplicated.

### 5. Add skill usage tracking as a Phase 2 research item

Claude Code's `.claude/scheduled_tasks.lock` may have invocation data. Other agents may not support it natively but could be wrapped. Add an explicit research item:

> "Determine which agents support skill invocation tracking (Claude Code: possibly; OpenCode: no; Codex: unknown; Antigravity: unknown). If unsupported, evaluate a wrapper approach."

### 6. OpenCode-specific: add deep- prefix to the audit-shrink command

`opencode.json` `command.audit-shrink` should become `command.deep-audit-shrink` once the skill is renamed. The template text inside it should reference the renamed skill.

### 7. OpenCode-specific: prevent accidental skill name collision after prefix rename

After adding `claude-` prefix, Claude skill `claude-proj-start` could still collide with a future `deep-proj-start` or `codex-proj-start` if anyone adds a shared skill. The validator should flag same-base-name skills across surfaces even with different prefixes, to prevent ambiguous behavior.

### 8. Document the `.claude/settings.local.json` format in AgentCoordination/README.md

Since the user is considering tracking it, document:
- What goes in `settings.json` (project-shared: hooks, effort level, broad permission allowlists)
- What goes in `settings.local.json` (machine-specific: absolute paths, local tool paths, personal preferences)
- How to migrate absolute paths to relative paths where possible
- That tracking it requires accepting breakage on any workspace move

## Evidence Links And File References

- **OpenCode skills discovery (three surfaces)**: https://opencode.ai/docs/skills/ — confirms `.opencode/skills/`, `.claude/skills/`, and `.agents/skills/` are all discovered
- **OpenCode rules (AGENTS.md canonical)**: https://opencode.ai/docs/rules/ — confirms `AGENTS.md` is canonical, `CLAUDE.md` is fallback only
- **OpenCode permissions (pattern matching)**: https://opencode.ai/docs/permissions/
- **Agent Skills spec (name/description constraints)**: https://agentskills.io/specification
- **Claude Code skills (extensions)**: https://code.claude.com/docs/en/skills
- **Claude Code settings (project vs local)**: https://code.claude.com/docs/en/settings
- **Codex skills (.agents/skills/ only)**: https://developers.openai.com/codex/skills
- **Codex AGENTS.md**: https://developers.openai.com/codex/guides/agents-md
- **Local verification — Claude skills (32)**: `.claude/skills/` — none prefixed `claude-`
- **Local verification — Antigravity skills (32)**: `.agent/skills/` — none prefixed `anti-`; 19 of 32 contain Claude-specific frontmatter
- **Local verification — Codex skills (8)**: `.agents/skills/` — all prefixed `codex-`
- **Local verification — OpenCode skills (1)**: `.opencode/skills/audit-shrink` — no `deep-` prefix
- **Local verification — `opencode.json` deny list**: covers all visible skill names via wildcard patterns
- **Local verification — `.agent/workflows/`**: 4 files, all stale (wrong test command, removed docs, wrong paths)

## Final Recommendation

**The V2 plan is directionally correct but misses the user's most important requirement: all skills must carry agent/system prefixes.** This must be resolved before any other V2 implementation begins. The prefix rename will cascade through every adapter surface, every deny pattern, and every skill reference. Delaying it means re-doing the validator and manifest work.

Priority order I recommend: (1) prefix all skills, (2) trim CLAUDE.md into adapter form with intentional-duplication waivers, (3) build automated test/skill counters, (4) implement manifest and validator, (5) add usage tracking research. Defer Antigravity path resolution until after workhorse agents are aligned.
