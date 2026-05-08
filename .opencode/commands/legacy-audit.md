---
description: Audit legacy code, aliases, shims, and migration code across all production code
agent: build
---
Load and run the ocode-legacy-audit skill. Detect module aliases, __init__.py re-export shims, deprecation markers, wrapper delegates, name-pair drift, save-migration code (banned by CLAUDE.md), superseded-pattern uses, TYPE_CHECKING-only re-exports, and partial Protocol implementers. Produces a legacy-removal scorecard with prioritized cleanup plan. Pass $ARGUMENTS to the skill if provided.
