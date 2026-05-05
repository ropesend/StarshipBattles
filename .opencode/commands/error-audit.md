---
description: Audit error handling & robustness across all production code
agent: build
---
Load and run the ocode-error-audit skill. Scan all production code for exception hygiene: broad except without Intentional comment, bare except, JSON bypass of json_utils, generic raise Exception, print-debug leakage, resource cleanup, and LLM context security. Produces a prioritized error hygiene scorecard. Pass $ARGUMENTS to the skill if provided.
