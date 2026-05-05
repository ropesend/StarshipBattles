---
description: Audit state management & mutability across all production code
agent: build
---
Load and run the ocode-state-audit skill. Scan all production code for module-level mutable state, singleton divergence risk (ctx.xxx vs get_default_xxx()), global keyword abuse, class-level mutable defaults, and random.seed() bypass. Produces a PROJ-258 transition progress report and singleton divergence risk map. Pass $ARGUMENTS to the skill if provided.
