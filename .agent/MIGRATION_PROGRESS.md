# Claude to Antigravity Skill Migration Progress

This file tracks the migration of skills from `.claude/skills/` to `.agent/skills/`.

## Overall Status
- **Total Skills**: 26
- **Migrated**: 26
- **In-Progress**: 0
- **Pending**: 0

## Naming Convention

All skills use category prefixes:
- `ticket-` — Unified bug/feature ticket workflow (replaces `debug-` and `feature-`)
- `proj-` — Project lifecycle management
- `analysis-` — Code analysis and review

## Consolidation (2026-03-14)

The 10 `debug-*` and 10 `feature-*` skills were consolidated into 10 unified `ticket-*` skills.
The `debug-triage-qa` agent-only skill was removed (functionality covered by `qa-triage`).
Protocols moved from `Debugging/protocols/` and `Features/protocols/` to `Tickets/protocols/`.

## Skill Detail Tracking

| Skill | Claude Path | Antigravity Path | Status | Notes |
|-------|-------------|------------------|--------|-------|
| ticket-add | `.claude/skills/ticket-add` | `.agent/skills/ticket-add` | Migrated | Replaces debug-add-bug + feature-add |
| ticket-work | `.claude/skills/ticket-work` | `.agent/skills/ticket-work` | Migrated | Replaces debug-fix-bug + feature-implement |
| ticket-close | `.claude/skills/ticket-close` | `.agent/skills/ticket-close` | Migrated | Replaces debug-close-bug + feature-close |
| ticket-batch-close | `.claude/skills/ticket-batch-close` | `.agent/skills/ticket-batch-close` | Migrated | Replaces debug-batch-close + feature-batch-close |
| ticket-update | `.claude/skills/ticket-update` | `.agent/skills/ticket-update` | Migrated | Replaces debug-update-bug + feature-update |
| ticket-reject | `.claude/skills/ticket-reject` | `.agent/skills/ticket-reject` | Migrated | Replaces debug-reject-fix + feature-reject |
| ticket-continue | `.claude/skills/ticket-continue` | `.agent/skills/ticket-continue` | Migrated | Replaces debug-continue + feature-continue |
| ticket-deep-dive | `.claude/skills/ticket-deep-dive` | `.agent/skills/ticket-deep-dive` | Migrated | Replaces debug-deep-dive + feature-deep-dive |
| ticket-next | `.claude/skills/ticket-next` | `.agent/skills/ticket-next` | Migrated | Replaces debug-next + feature-implement-next |
| ticket-answer | `.claude/skills/ticket-answer` | `.agent/skills/ticket-answer` | Migrated | Replaces debug-answer-questions + feature-answer-questions |
| proj-start | `.claude/skills/proj-start` | `.agent/skills/proj-start` | Migrated | |
| proj-continue | `.claude/skills/proj-continue` | `.agent/skills/proj-continue` | Migrated | |
| proj-audit | `.claude/skills/proj-audit` | `.agent/skills/proj-audit` | Migrated | |
| proj-close | `.claude/skills/proj-close` | `.agent/skills/proj-close` | Migrated | |
| proj-revise | `.claude/skills/proj-revise` | `.agent/skills/proj-revise` | Migrated | |
| proj-archive | `.claude/skills/proj-archive` | `.agent/skills/proj-archive` | Migrated | |
| proj-extract-phase | `.claude/skills/proj-extract-phase` | `.agent/skills/proj-extract-phase` | Migrated | |
| proj-add-to-plan | `.claude/skills/proj-add-to-plan` | `.agent/skills/proj-add-to-plan` | Migrated | |
| proj-manage-plan | `.claude/skills/proj-manage-plan` | `.agent/skills/proj-manage-plan` | Migrated | |
| proj-reset-baseline | `.claude/skills/proj-reset-baseline` | `.agent/skills/proj-reset-baseline` | Migrated | |
| proj-review | `.claude/skills/proj-review` | `.agent/skills/proj-review` | Migrated | |
| analysis-complexity | `.claude/skills/analysis-complexity` | `.agent/skills/analysis-complexity` | Migrated | |
| analysis-dead-code | `.claude/skills/analysis-dead-code` | `.agent/skills/analysis-dead-code` | Migrated | |
| analysis-sweep | `.claude/skills/analysis-sweep` | `.agent/skills/analysis-sweep` | Migrated | |

## Session Hand-off
- **Last Updated**: 2026-03-14
- **Last Action**: Consolidated 20 debug-*/feature-* skills into 10 unified ticket-* skills. Updated both .claude and .agent directories.
- **Next Step**: Skills are ready for production use.
