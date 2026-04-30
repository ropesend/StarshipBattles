# Claude Code V4 Review

Author: Claude Code (Opus 4.7, 1M context)
Date: 2026-04-28
Reviews: [codex_agent_coordination_plan_v4.md](codex_agent_coordination_plan_v4.md)

## User Discussion Summary

V4 incorporates almost everything raised in the V3 round. Discussed seven remaining issues with the user; user asked for a brief report covering the material ones (#1–#3) plus the smaller ones (#4–#7) noted as deferrable.

## Remaining Issues

### 1. Phase 7 validator is too late to enforce the prefix policy

Between Phase 6 (atomic rename) and Phase 7 (validator), nothing enforces prefixes. A skill added in that window can ship unprefixed and pass. The renamer already understands the prefix scheme; promote a minimal "prefix-only" check out of the rename script and run it as a pre-commit on the rename PR. Full validator in Phase 7 unchanged.

### 2. No phase rewrites AGENTS.md to use the generated baseline

AGENTS.md line 67 still has `15477+ tests baseline. Known flakes…` as prose. After Phase 2 produces `test_baseline.json`, AGENTS.md must be rewritten to reference the JSON rather than carry the count inline. V4 lists AGENTS.md as a renamer target (skill-name rewrites) but no phase replaces volatile facts in AGENTS.md with pointers. Without this step, Phase 7's volatile-fact check will fail against AGENTS.md itself.

### 3. No CI integration step

V4 implements the validator and inventory generator but never wires them into CI. The "automation beats prose" argument depends on PRs catching drift. Add Phase 7b: GitHub Actions workflow runs `validate_agent_surfaces.py` on PRs touching agent surfaces, and verifies the committed `agent_surface_inventory.json` matches a fresh generation.

## Implementation Risks

### 4. Usage counter prototype (Phase 4) precedes rename (Phase 6)

Logged usage data uses old skill names; after Phase 6, those names no longer exist. Either swap so the usage prototype lands after the rename, or extend the renamer to rewrite skill names in `AgentCoordination/generated/skill_usage/by_install/<install_id>.json`. Swapping is simpler.

### 5. `agent_surface_inventory.json` lacks `schema_version`

V4 added `schema_version: 1` to the test baseline schema but not the inventory schema. Same versioning discipline should apply.

### 6. Defensive `anti-*: deny` not added to `opencode.json`

V4 omits the deny rule because OpenCode does not currently discover `.agent/skills/`. If a future OpenCode release expands its discovery list, `anti-*` skills become silently visible. A proactive deny rule is fail-safe and free.

### 7. Project-shared `.claude/settings.json` not covered by sanitizer or validator

V4 only addresses `settings.local.json`. The tracked shared file currently has no absolute paths, but the same volatile-fact rules should apply so an accidental paste-in is caught.

## Required V4 Changes

- Add a prefix-only pre-commit check to Phase 6 to close the Phase 6→7 enforcement gap.
- Add an explicit Phase 2 step that rewrites volatile facts in AGENTS.md (and any other adapter doc) to reference `AgentCoordination/generated/test_baseline.json`.
- Add Phase 7b: CI workflow running validator + inventory freshness check on PRs touching agent surfaces.
- Reorder so Phase 4 (usage counters) runs after Phase 6 (rename), or extend the renamer to rewrite logged skill names.
- Add `schema_version` to `agent_surface_inventory.json`.
- Add `anti-*: deny` to `opencode.json` defensively.
- Extend the settings sanitizer/validator to cover `.claude/settings.json` as well.

## Evidence

- AGENTS.md line 67 contains the literal text `15477+ tests baseline. Known flakes…` — verified.
- V4 §"Generated Test Baseline" includes `schema_version: 1`; V4 §"Generated Skill Inventory" does not.
- V4 §"OpenCode Governance" explicitly states `anti-*` does not need an OpenCode deny rule.
- V4 §"Implementation Order" lists eight phases; none is a CI workflow step.
- V4 Phase 4 (usage counter) precedes Phase 5/6 (rename dry-run / atomic rename).
- OpenCode skill discovery sources: [opencode.ai/docs/skills](https://opencode.ai/docs/skills/) — current list is `.opencode/skills/`, `.claude/skills/`, `.agents/skills/`. Defensive deny is policy, not doc-required.

## Final Recommendation

Adopt V4 with the seven changes above before any tooling work begins. Issues #1–#3 are material and should land in V4 itself. Issues #4–#7 can be folded into the V4 phase notes without restructuring. The eight-phase order is otherwise correct: inventory before rename, generated artifacts before validator, validator before stale-surface deletion.
