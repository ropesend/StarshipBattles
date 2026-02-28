# Claude to Antigravity Skill Migration Progress

This file tracks the migration of skills from `.claude/skills/` to `.agent/skills/`.

## Overall Status
- **Total Skills**: 35
- **Migrated**: 35
- **In-Progress**: 0
- **Pending**: 0

## Naming Convention

All skills use category prefixes:
- `debug-` — Bug tracking and debugging workflow
- `proj-` — Project lifecycle management
- `feature-` — Feature lifecycle management
- `analysis-` — Code analysis and review

## Skill Detail Tracking

| Skill | Claude Path | Antigravity Path | Status | Notes |
|-------|-------------|------------------|--------|-------|
| debug-add-bug | `.claude/skills/debug-add-bug` | `.agent/skills/debug-add-bug` | Migrated | |
| debug-answer-questions | `.claude/skills/debug-answer-questions` | `.agent/skills/debug-answer-questions` | Migrated | |
| debug-batch-close | `.claude/skills/debug-batch-close` | `.agent/skills/debug-batch-close` | Migrated | |
| debug-close-bug | `.claude/skills/debug-close-bug` | `.agent/skills/debug-close-bug` | Migrated | |
| debug-continue | `.claude/skills/debug-continue` | `.agent/skills/debug-continue` | Migrated | |
| debug-deep-dive | `.claude/skills/debug-deep-dive` | `.agent/skills/debug-deep-dive` | Migrated | Adapted swarm to deep dive |
| debug-fix-bug | `.claude/skills/debug-fix-bug` | `.agent/skills/debug-fix-bug` | Migrated | |
| debug-next | `.claude/skills/debug-next` | `.agent/skills/debug-next` | Migrated | |
| debug-reject-fix | `.claude/skills/debug-reject-fix` | `.agent/skills/debug-reject-fix` | Migrated | |
| debug-triage-qa | — | `.agent/skills/debug-triage-qa` | Migrated | Agent-only skill |
| debug-update-bug | `.claude/skills/debug-update-bug` | `.agent/skills/debug-update-bug` | Migrated | |
| proj-start | `.claude/skills/proj-start` | `.agent/skills/proj-start` | Migrated | Adapted swarm to deep dive |
| proj-continue | `.claude/skills/proj-continue` | `.agent/skills/proj-continue` | Migrated | |
| proj-audit | `.claude/skills/proj-audit` | `.agent/skills/proj-audit` | Migrated | |
| proj-close | `.claude/skills/proj-close` | `.agent/skills/proj-close` | Migrated | |
| proj-revise | `.claude/skills/proj-revise` | `.agent/skills/proj-revise` | Migrated | |
| proj-archive | `.claude/skills/proj-archive` | `.agent/skills/proj-archive` | Migrated | |
| proj-extract-phase | `.claude/skills/proj-extract-phase` | `.agent/skills/proj-extract-phase` | Migrated | |
| proj-add-to-plan | `.claude/skills/proj-add-to-plan` | `.agent/skills/proj-add-to-plan` | Migrated | |
| proj-manage-plan | `.claude/skills/proj-manage-plan` | `.agent/skills/proj-manage-plan` | Migrated | |
| proj-reset-baseline | `.claude/skills/proj-reset-baseline` | `.agent/skills/proj-reset-baseline` | Migrated | |
| proj-review | `.claude/skills/proj-review` | `.agent/skills/proj-review` | Migrated | Newly migrated |
| feature-add | `.claude/skills/feature-add` | `.agent/skills/feature-add` | Migrated | Newly migrated |
| feature-implement | `.claude/skills/feature-implement` | `.agent/skills/feature-implement` | Migrated | Newly migrated |
| feature-implement-next | `.claude/skills/feature-implement-next` | `.agent/skills/feature-implement-next` | Migrated | Newly migrated |
| feature-continue | `.claude/skills/feature-continue` | `.agent/skills/feature-continue` | Migrated | Newly migrated |
| feature-update | `.claude/skills/feature-update` | `.agent/skills/feature-update` | Migrated | Newly migrated |
| feature-close | `.claude/skills/feature-close` | `.agent/skills/feature-close` | Migrated | Newly migrated |
| feature-batch-close | `.claude/skills/feature-batch-close` | `.agent/skills/feature-batch-close` | Migrated | Newly migrated |
| feature-deep-dive | `.claude/skills/feature-deep-dive` | `.agent/skills/feature-deep-dive` | Migrated | Newly migrated |
| feature-answer-questions | `.claude/skills/feature-answer-questions` | `.agent/skills/feature-answer-questions` | Migrated | Newly migrated |
| feature-reject | `.claude/skills/feature-reject` | `.agent/skills/feature-reject` | Migrated | Newly migrated |
| analysis-complexity | `.claude/skills/analysis-complexity` | `.agent/skills/analysis-complexity` | Migrated | |
| analysis-dead-code | `.claude/skills/analysis-dead-code` | `.agent/skills/analysis-dead-code` | Migrated | |
| analysis-sweep | `.claude/skills/analysis-sweep` | `.agent/skills/analysis-sweep` | Migrated | Adapted 25-agent swarm |

## Session Hand-off
- **Last Updated**: 2026-02-28
- **Last Action**: Renamed all skills with category prefixes and migrated 11 remaining skills from .claude to .agent.
- **Next Step**: Skills are ready for production use.
