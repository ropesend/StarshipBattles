# OpenCode (DeepSeek V4 Pro) V3 Review

Author: OpenCode with DeepSeek V4 Pro
Date: 2026-04-30
Reviews: [codex_agent_coordination_plan_v3.md](codex_agent_coordination_plan_v3.md), [user_response.md](user_response.md)

## User Discussion Summary

Prefix confirmed as `ocode-` (shorter than `opencode-`, tool-tied not model-tied). User agreed command template text in `opencode.json` must also be updated during prefix rename. User wants generated baseline and inventory files tracked. User asked to flag uncertainty around HTML comment marker handling in OpenCode's context handler.

## Material Disagreements

None.

## Implementation Risks

### 1. `opencode.json` command template text missed in migration spec

V3 §4 step 6 says "Update `opencode.json` skill permissions and command names." The command *key* changes (`"audit-shrink"` → `"ocode-audit-shrink"`), but the template *body* also embeds the old name:

```json
"template": "Load the audit-shrink skill and run a comprehensive..."
```

The rename script must regex-replace old skill names in template bodies, not just rename keys. Add a step 6a: "Replace old skill-name strings in `opencode.json` command template text bodies."

### 2. Deny-list transition is race-condition sensitive

V3 §5 proposes simplifyng to `ocode-*: allow`, `claude-*: deny`, `codex-*: deny`. During migration, the script renames directories *and* updates `opencode.json` deny patterns within the same commit. If the deny pattern update lags behind the directory rename by even one file-save, newly renamed `claude-proj-*` skills briefly fall through the old `proj-*` deny pattern (which no longer matches) and become visible to OpenCode. The rename script should update `opencode.json` first, then rename directories.

### 3. `.agent/skills/` count increased from 32 to 33 between V2 and V3

V3 correctly notes this. The inventory script eliminates this risk entirely. The 33rd skill is one already in the Antigravity-only set (the set was always 4 Antigravity-only + 29 shared = 33). V2's count of 32 was stale, not a newly created skill. No action needed beyond confirming the inventory script is Phase 1.

### 4. Reinforcement markers: OpenCode context behavior is unknown

V3 proposes `<!-- agent-coordination:reinforcement tdd -->`. The validator reads these; OpenCode agents don't need to. But if OpenCode's context handler strips HTML comments before injecting Markdown into the LLM context, the markers are invisible to agents (fine) but also invisible to any future tool that might want agents to self-police reinforcement scope. Low risk for the validator, but worth a quick smoke test in Phase 5: write a skill with a marker, load it via OpenCode's skill tool, and confirm the marker text is preserved in what the agent receives.

## New Suggestions

### 1. V3 Question #1 (`deep-` vs `opencode-`) should be replaced with `ocode-`

V3's Question #1 only compares `deep-` and `opencode-`. Replace with `ocode-` as the settled answer. `ocode-` is shorter than `opencode-`, tool-tied (unlike model-tied `deep-`), and won't collide with other conventions if the model backend changes.

### 2. Update AGENTS.md tooling note after rename

`AGENTS.md` line 34 references `.opencode/skills/audit-shrink/SKILL.md`. This reference must update to `ocode-audit-shrink`. The rename map in V3 §4 should include AGENTS.md as a target file.

### 3. Add the reinforcement marker syntax to the Agent Skills spec compatibility check

If the marker is `<!-- agent-coordination:reinforcement ... -->`, the validator should ensure it appears only in adapter files (CLAUDE.md, `.agents/CODEX.md`), not in `SKILL.md` bodies where it could be misinterpreted as a skill instruction. Reinforcer markers are an adapter concern, not a skill concern.

### 4. Track both generated files

The test baseline (`AgentCoordination/generated/test_baseline.json`) and skill inventory (`AgentCoordination/generated/agent_surface_inventory.json`) should both be tracked. The baseline feeds validator freshness checks. The inventory provides a stable snapshot for the rename map. Commit them only after intentional full runs.

### 5. `.agent/skills/` has 33 directories, not 32

V3 correctly states 33. V2 said 32. This is now settled, but any intermediate docs referencing 32 should not be relied on.

## Evidence

- **OpenCode skills discovery**: https://opencode.ai/docs/skills/ — `.opencode/skills/`, `.claude/skills/`, `.agents/skills/` are all project surfaces; `.agent/skills/` is not
- **OpenCode permissions**: https://opencode.ai/docs/permissions/ — pattern-based allow/deny/ask
- **Agent Skills spec**: https://agentskills.io/specification — name regex `^[a-z0-9]+(-[a-z0-9]+)*$`, max 64 chars, min 1 char, description 1–1024 chars
- **Claude Code settings**: https://code.claude.com/docs/en/settings — documents `settings.local.json` as per-user, not checked in
- **Local verification**: `.claude/skills/` 32 dirs, `.agent/skills/` 33 dirs, `.agents/skills/` 8 dirs, `.opencode/skills/` 1 dir; `opencode.json` deny list covers all visible non-OpenCode skills; `.agent/workflows/` is stale; `.agent/MIGRATION_PROGRESS.md` is stale
- **V3 local state claim**: verified — `.agent/skills/` has 33, not 32 as V2 claimed; `.claude/skills/` has 32; 19 of 33 `.agent/skills/` files still contain Claude-specific frontmatter

## Final Recommendation

Adopt V3 with three adjustments:

1. Settle the prefix as `ocode-` (not `deep-` or `opencode-`), updating V3 §3 and Question #1.
2. Expand rename script step 6 to include `opencode.json` command template text bodies.
3. Update the deny-list transition ordering: write new deny patterns before renaming directories.

Beyond those, V3 is ready to proceed. The inventory-then-rename-then-validate sequence is correct. Generated file tracking, settings.local.json policy, reinforcement marker design, Antigravity deferral, and usage tracking scope all align with the user's stated priorities.
