# OpenCode / DeepSeek — Refinement Plan Review

Author: OpenCode with DeepSeek V4 Pro
Date: 2026-05-02
Reviews: `AgentCoordination/multi_agent_coordination_refinement_plan_2026-05-02.md` (Codex-authored)
User decisions incorporated: Yes — all 7 clarification questions answered and reflected below.

## Summary Judgment

Approve with one mandatory correction. The plan correctly identifies the 6 problems to fix, the target end state, and the phased implementation approach. Phases 1–6 are directionally correct. Phase 7 needs rewriting per the user's rollback decision. Phase 8 has a terminology mismatch that should be flagged.

The recommended initial PR scope (atomic logging + cross-agent reference validator + prefix drift fix) is the right sequencing — add guard rails before content deletions.

## Corrections Required

### C1. Phase 7: Replace `git reset --hard HEAD~1` with `git revert` (user decision)

**The plan's current approach is incorrect for this repo.** The user selected "always `git revert`" over the 7-condition guarded `git reset`. This simplifies Phase 7 substantially:

- The cleanup preconditions (clean worktree, record pre-merge SHA, confirm HEAD, confirm not pushed) become unnecessary — `git revert` is safe regardless of worktree state or push status.
- The 6 files needing update are confirmed real (verified via grep):

| File | Lines |
|------|-------|
| `Tracking/protocols/02c_parallel_debug.md` | 173, 393 |
| `Tracking/protocols/02d_parallel_deep_dive.md` | 376, 820 |
| `Projects/protocols/03b_parallel_projects.md` | 143 |
| `.claude/skills/claude-debug-parallel/SKILL.md` | 118 |
| `.claude/skills/claude-deep-dive-parallel/SKILL.md` | 152 |
| `.claude/skills/claude-proj-parallel/SKILL.md` | 94 |

**Recommended rewrite:** Replace every `git reset --hard HEAD~1` with `git revert HEAD --no-edit` and remove the associated cleanup instructions (they become moot). A follow-up `git revert <revert-commit>` can restore the merge if desired — simpler mental model, no history destruction.

**Sequencing suggestion:** Since this is now a straightforward search-and-replace, consider folding it into the initial PR scope rather than deferring to a later phase.

## Confirmed Findings

### F1. Phase 2: `log_skill_usage.py` is NOT atomic — confirmed

The script (116 lines) writes the per-install counter file at `AgentCoordination/generated/skill_usage/by_install/<id>.json` but never calls `summarize_skill_usage.py`. The summarizer must be run separately. The plan's Phase 2 fix is confirmed necessary.

`summarize_skill_usage.py` exists but is a separate script. The fix should integrate its logic into `log_skill_usage.py` so one invocation updates both the per-install file and `summary.json`. The plan's proposed test coverage is adequate.

### F2. Phase 3: CLAUDE.md stale facts — confirmed

CLAUDE.md is 377 lines. The plan targets ~200 lines. Three specific stale facts verified:

- **Line 126:** `"27 design patterns"` — volatile count that drifts as patterns are added/deprecated.
- **Line 296:** `"9 services"` — AGENTS.md says 10 services.
- **Lines 289-293:** Layer architecture summary lists Core → Simulation → Strategy → UI → AI but misses Services, Assets, Engine, and Research layers that AGENTS.md documents.

**Recommendation:** Remove the entire "Architecture Principles" section (lines 283-302) since AGENTS.md owns this. Remove the pattern count claim. Remove the service count — reference AGENTS.md instead. This alone recovers ~40 lines.

### F3. Phase 4: Prefix drift — confirmed with one missed file

20 matches of `/anti-*` across 11 `.claude/skills/` files confirmed. The plan's audit list is accurate but missing one file:

> `claude-analysis-sweep/SKILL.md:101` — contains `/anti-analysis-sweep`

This is a Claude skill referencing an Antigravity-prefixed command. Add it to the Phase 4 fix list.

All other matches are in `claude-ticket-*`, `claude-qa-*`, `claude-proj-*` skills, matching the plan's description.

### F4. Phase 5: Antigravity retire list — user approved

32 `.agent/skills/anti-*` directories exist. The retire list removes 21 of them (anti-proj-*, anti-ticket-*, anti-qa-*, anti-debug-*, anti-deep-dive-*, anti-fix-crash, anti-triage-to-proj). User agreed with the full retire list. This leaves `anti-validate-designs`, `anti-loc`, `anti-analysis-sweep`, `anti-analysis-dead-code`, and `anti-analysis-complexity` as the candidate keep list. Confirm these asset/tooling skills are the ones the user wants retained before deletion.

### F5. Phase 6: Local settings handling — resolved

User chose "skip by default in validator." No separate local-only audit mode needed. The plan's Phase 6 implementation steps are correct as written.

### F6. `agent_surface_policy.json` approach — confirmed

User chose external JSON policy file. The plan's proposal is correct. Add a `schema_version` field in the initial version to match the existing convention used by `test_baseline.json` and `agent_surface_inventory.json`.

## Suggestions and Refinements

### S1. CLAUDE.md thinning — suggested keep/cut breakdown

Given the user's directive to keep hard rules duplicated for context retention (user_response #11: 1K tokens to reinforce critical items is worthwhile), here's a proposed keep/cut for the 377→200 line reduction:

**Keep (must stay in CLAUDE.md):**
- Three Non-Negotiable Rules (lines 9-97) — user explicitly wants these reinforced
- Documentation First (lines 115-137) — includes `docs/_ignore/` ignore rule
- Project Overview tech stack and spatial terminology (lines 141-165) — these are Claude-specific navigation facts
- TDD Workflow and test commands (lines 216-241) — Claude needs to know test commands
- Key Conventions: return-type annotations, file size ceiling, specific exceptions, save-file policy (lines 248-279)
- Git Workflow (lines 328-334) — short
- Skill Usage Logging (lines 338-353) — Claude-specific hook behavior
- Subagent Report Output (lines 357-377) — Claude-specific

**Cut (move to AGENTS.md reference):**
- Architecture Principles (lines 283-302) — duplicate of AGENTS.md, contains stale counts
- Development Workflows → project structure (lines 200-214) — AGENTS.md owns this
- Common Tasks → adding abilities (lines 306-315) — better in docs/guides/
- Testing Configuration (lines 319-324) — move worker counts to AGENTS.md or drop
- Project Structure tree (lines 171-196) — AGENTS.md owns this

This cut brings CLAUDE.md to approximately 240 lines. Further trimming in the "Key Conventions" and "Project Overview" sections can reach ~200.

### S2. Phase 4 scope addition

Add `.claude/skills/claude-analysis-sweep/SKILL.md:101` to the prefix drift fix list (see F3 above).

### S3. Phase 8: OpenCode audit skill terminology — needs adjustment

The `ocode-audit-shrink` skill (533 lines) uses terminology that is partly correct and partly wrong for OpenCode:

| Term in skill | OpenCode status | Recommendation |
|---------------|-----------------|----------------|
| `Task tool` with `subagent_type` | **Valid** — OpenCode's Task tool accepts `subagent_type` | Keep as-is |
| `Write tool` (used ~20 times across the skill) | **NOT valid** — OpenCode has no tool named "Write" | Replace with neutral phrasing: "You MUST save your report to:" (the agent knows its own write mechanisms) |

The skill's Phase 2 agent prompt templates all specify `You MUST use the Write tool to save your report to:`. For OpenCode agents, these should read: `You MUST save your report to:` — the agent's tool surface handles the mechanism.

This is a lower-priority fix than prefix drift and rollback, as the plan notes, but the terminology mismatch could confuse OpenCode agents executing the skill. **Recommendation:** fix the terminology in the initial PR rather than deferring — it's a mechanical find-and-replace.

### S4. `agent_surface_policy.json` structure

Proposed initial structure matching existing conventions:

```json
{
  "schema_version": 1,
  "generated_at": "<utc-iso>",
  "skill_prefixes": {
    "claude": "claude-",
    "codex": "codex-",
    "ocode": "ocode-",
    "anti": "anti-"
  },
  "antigravity_allowed_scope": {
    "categories": ["tooling", "assets", "design-validation"],
    "allowed_skills": ["anti-validate-designs"],
    "retired_skills": ["anti-proj-*", "anti-ticket-*", "anti-qa-*", "anti-debug-*", "anti-deep-dive-*", "anti-fix-crash", "anti-triage-to-proj"]
  },
  "cross_agent_references": {
    "policy": "deny",
    "allowed": []
  },
  "claude_settings": {
    "tracked_files": [".claude/settings.json"],
    "ignored_files": [".claude/settings.local.json"],
    "local_audit_mode": false
  }
}
```

### S5. Phase sequencing adjustment

Current recommended initial PR (Phase 1 tests + Phase 2 atomic logging + Phase 4 prefix fix). With rollback now simplified, suggest:

1. **Initial PR:** Phase 2 (atomic logging) + Phase 4 (prefix drift fixes) + Phase 7 (revert rollback protocols). These are all mechanical changes.
2. **Second PR:** Phase 1 (validator guard rail tests + policy file).
3. **Third PR:** Phase 3 (CLAUDE.md thinning).
4. **Fourth PR:** Phase 5 (Antigravity retirement) + Phase 6 (stop tracking local settings).

This groups the mechanical fixes first, policy infrastructure second, content changes third, and deletions last — safest ordering.

## Risk Assessment

| Phase | Risk | Mitigation |
|-------|------|------------|
| 5 (Antigravity retirement) | **Highest** — deletes 21 skill directories. If a deleted skill is still referenced, agents break silently. | Must run full validator + inventory regeneration after deletion. Cross-reference grep before deleting each skill. |
| 3 (CLAUDE.md thinning) | **Medium** — removing stale architecture text could accidentally remove a Claude-specific instruction that looks stale but is intentional. | Diff review with user before landing. Validate reinforcement markers still cover all 6 tags. |
| 4 (Prefix drift fix) | **Low** — changing `/anti-*` to `/claude-*` in Claude skills is mechanical. The plan's exception for "anti" in ordinary prose (anti-pattern, etc.) is correct. | The plan's Phase 4 exception must be enforced in the fix tooling. |
| 2 (Atomic logging) | **Low** — the two scripts are well-contained, tests are scoped. | Confirm `summarize_skill_usage.py` is fully subsumed before deleting it. |

## Open Questions — Now Resolved

The plan's 5 open questions are all resolved by user decisions:

| # | Question | Answer |
|---|----------|--------|
| 1 | CLAUDE.md import vs. duplication | **Duplicate hard rules + pointer** to AGENTS.md |
| 2 | Which Antigravity skills remain | **Agreed with retire list** (anti-proj-*, anti-ticket-*, anti-qa-*, anti-debug-*, anti-deep-dive-*, anti-fix-crash, anti-triage-to-proj) |
| 3 | agent_surface_policy.json vs. embedded policy | **External JSON** (`AgentCoordination/agent_surface_policy.json`) |
| 4 | Validator handling of settings.local.json | **Skip by default** — no separate audit mode |
| 5 | Rollback: revert vs. reset | **Always `git revert`** |

## Validation Commands Confirmed

The plan's validation commands are correct. Add after policy file creation:

```powershell
python Tools/agent_coordination/validate_agent_surfaces.py   # verify policy JSON loads
```

## Final Recommendation

Land with the Phase 7 correction. The plan is otherwise sound. The suggested sequencing adjustment (S5 above) groups changes into fewer PRs with safer ordering. Proceed.
