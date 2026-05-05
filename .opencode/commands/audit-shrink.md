---
description: Run a comprehensive code shrinkage audit (vulture, radon, clone detector, agents)
agent: build
---
Load and run the ocode-audit-shrink skill. Execute all phases: Phase 1 deterministic tools, Phase 2 agents (cross-shard duplication, in-shard deep review, dead code validation), and compile the final report with shrinkage estimates. Pass $ARGUMENTS to the skill if provided.
