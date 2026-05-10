# Marked For Deletion — 2026-05-29

This directory is a staging area for files and directories scheduled for permanent deletion on **2026-05-29** (one calendar month after the cleanup pass that moved them here).

**Why this exists.** Rather than deleting outright, the cleanup work migrates dead-but-recoverable artifacts here. If anyone needs one of these files, they can run `git mv` to restore it before 2026-05-29. After that date, this entire directory should be removed in one commit.

**Why one month.** Every file here came from one of three categories:

1. **Confirmed-stale automation** — the three CLI loop systems (`refactor_loop`, `complexity_loop`, `continuous_loop`) had their last activity between 2026-02-13 and 2026-03-01. None had run successfully in 60+ days at the time of staging. A 30-day cooling-off window adds margin without indefinite carry.
2. **Confirmed-dead docs/scripts** — legacy prompts the README explicitly called legacy, completed one-shot migrations, asset browsers with no processing logic, an analysis doc that was never converted to a project.
3. **Pruned Antigravity skill copies** — the 33 `.agent/skills/anti-*` directories were reduced to the ~6 Antigravity actually uses (per the user's stated priority of using Antigravity for tooling and asset generation). The other ~27 are recoverable here in case the prune was wrong.

The historical critical review that motivated this cleanup is at `AgentCoordination/support_systems_critical_review.md`. The cleanup plan is at `AgentCoordination/support_systems_cleanup_plan.md`.

## Contents

Subdirectories below mirror the original repo path so a restoration is a single `git mv` per file.

```
_marked_for_deletion_2026-05-29/
  README.md                                    (this file)
  Tracking/
    prompts/                                   (9 legacy prompt files; superseded by /claude-ticket-* skills)
  Projects/
    Triage/
      fleet_system_review.md                   (analysis doc from 2026-03-22, never converted to PROJ)
    refactor_loop/                             (CLI loop, intentionally complete 2026-03-01)
    complexity_loop/                           (CLI loop, hit 8h timeout 2026-02-27, never resumed)
    continuous_loop/                           (CLI loop, stuck mid-cycle 6 since 2026-02-13)
  Tools/
    migrate_ai_strategy.py                     (completed schema migration; one-shot)
    background_eraser/                         (asset browser with no processing logic)
  AgentCoordination/
    historical_reviews/                        (18 review-round artifacts, V1-V4 plans, baseline/implementation/system reviews)
  Reviews/
    Prompts/
      Sweep - *.txt                            (8 prompts; no protocol existed; index entries removed in same commit)
  .agent/
    skills/                                    (~27 anti-* skills not retained in the pruned set)
```

Each subsystem's subdirectory may contain a short `WHY.md` adding context for why that particular item was retired.

## Restoration recipe

If you discover a file here is needed:

```bash
# Restore a single file
git mv _marked_for_deletion_2026-05-29/<original-path> <original-path>

# Restore an entire subsystem (example: refactor_loop)
git mv _marked_for_deletion_2026-05-29/Projects/refactor_loop Projects/refactor_loop
```

Commit the restore with a brief justification. Update this README to remove the restored path from the inventory.

## Final deletion (2026-05-29 or later)

When the date arrives and nothing here has been restored:

```bash
git rm -r _marked_for_deletion_2026-05-29/
git commit -m "chore: delete 2026-05-29 staging directory; 30-day window elapsed with no restorations"
```

After deletion, every file is still recoverable from git history at the cleanup branch's merge commit.
