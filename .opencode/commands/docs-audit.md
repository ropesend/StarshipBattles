---
description: Audit documentation freshness, find dead references, stale PROJ mentions, undocumented modules
agent: build
---
Load and run the ocode-docs-audit skill. Cross-reference all docs/ references against live code, PROJ statuses against projects_index.md, and timestamps against staleness thresholds. Produces a doc health scorecard with prioritized update plan. Pass $ARGUMENTS to the skill if provided.
