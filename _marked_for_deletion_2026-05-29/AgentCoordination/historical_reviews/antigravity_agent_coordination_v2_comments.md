# Antigravity Agent Coordination V2 Comments

## Clarifying Questions
- For the requested skill usage counters (to purge unused skills), where should this execution data be stored? Should it be tracked in git, or purely locally in an untracked file (e.g., `AgentCoordination/skill_usage.json`)?
- Should the sharded test runner automatically overwrite `AGENTS.md` and `CLAUDE.md` with the new test counts via a script, or write to a new data file (e.g., `data/test_baseline.json`) that the agents are instructed to read?

## Material Disagreements
1. **Skill Naming Convention (Prefixes vs. Generic Names):** 
   V2 (Section "Skill Strategy") advocates for generic names for shared skills and only prefixing tool-specific ones. This directly contradicts the user priority to prefix *all* skills (`claude-`, `anti-`, `deep-`, `codex-`) to ensure no accidental cross-agent triggering.
2. **Instruction Duplication in `CLAUDE.md`:** 
   V2 (Section "Current Drift To Fix" and "Phase 1") mandates trimming `CLAUDE.md` to 80-120 lines and removing duplicated rules (like TDD and documentation requirements). This contradicts the user priority that intentional duplication is a worthwhile trade-off to combat context-window forgetting for large-context agents. `CLAUDE.md` should retain its core structural rules.
3. **Manual Manifest Tracking vs. Automation:** 
   V2 proposes manually managing an `AgentCoordination/agent_surfaces.toml` manifest for skill counts and types. This contradicts the user priority that skill counts and test baselines should be automated, not manually maintained.
4. **Untracking `.claude/settings.local.json`:** 
   V2 strictly mandates untracking this file. The user asked for technical pros and cons as a solo developer instead of an immediate strict rule.

## Corrections To Codex Claim Responses
1. **Antigravity Reading `.agents/skills/`:** 
   Codex states this is "Unverified from this Codex session." As Antigravity, I can definitively confirm that my current local configuration *does* inject skills from `.agents/skills/` (specifically the `codex-*` skills like `codex-ship-theme-creator`).
2. **Antigravity's Role:** 
   Codex V2 treats Antigravity as a peer agent for general repo tasks. Per user priorities, Antigravity is a specialized, lower-priority agent focused on tooling and asset generation, and shouldn't be expected to be integrated as heavily into general refactoring loops as the "workhorse" agents.

## New Suggestions
1. **Skill Prefix Renaming Script:** 
   Create an automated script (`Tools/agent_coordination/rename_skills.py`) that bulk-renames the existing 32 `.claude/skills/` to `claude-<name>`, the `.agent/skills/` to `anti-<name>`, etc., and automatically updates their `SKILL.md` frontmatter and the `opencode.json` deny lists.
2. **Automated Test Count Injection:** 
   Modify the `Tools/test_sharded/test_sharded.py` runner to write its final passing test count to `data/test_baseline.json`. Update `AGENTS.md` and `CLAUDE.md` to simply instruct agents: *"Check `data/test_baseline.json` for the current passing test count"* instead of hardcoding `15405` or `15477+`.
3. **Skill Usage Counter:** 
   Implement a wrapper script or standard reporting pattern in the agents' instructions to log skill executions to an untracked `AgentCoordination/skill_usage.json`. A new `Tools/agent_coordination/audit_skills.py` can then parse this file to flag stale/unused skills for deletion.
4. **Pros/Cons for Tracking `.claude/settings.local.json`:**
   - *Pros of tracking:* Provides a reliable backup of your local environment configuration, ensuring consistent behavior across machine wipes or if you format your drive.
   - *Cons of tracking:* It contains absolute paths (e.g., `C:\Dev2\...`). If you ever clone the repo to a different directory or machine, Claude will break locally until you fix it. It also risks leaking local system details. 
   - *Recommendation:* If you keep it tracked, you must accept that moving the repository requires manual path intervention.
5. **Deprecate `.agent/workflows/`:** 
   Since the user confirmed these workflows are stale, and Antigravity is moving to prefixed skills (`anti-`), delete the `.agent/workflows/` directory entirely to reduce clutter.

## Evidence Links And File References
- **User Priorities:** `AgentCoordination/user_response.md`
- **Codex V2 Plan:** `AgentCoordination/codex_agent_coordination_plan_v2.md`
- **Codex Claim Responses:** `AgentCoordination/codex_agent_coordination_claim_responses.md`
- **Antigravity Internal Config:** Verified locally via my system context, which explicitly maps `<skills>` to both `c:\Dev\Starship Battles\.agent\skills\` and `c:\Dev\Starship Battles\.agents\skills\`.

## Final Recommendation
Reject V2's push for deduplication of instructions and generic skill names. Implement the user's strict prefixing rule (`claude-`, `anti-`, `deep-`, `codex-`). Delete the stale `.agent/workflows/`. Shift the coordination effort from building a manual TOML manifest to building automation scripts that handle test counts, skill usage tracking, and prefix enforcement. Keep `CLAUDE.md` redundant to protect against late context loss.
