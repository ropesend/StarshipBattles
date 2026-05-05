---
description: Audit type safety & annotation quality with mypy strict-mode + AST scan
agent: build
---
Load and run the ocode-type-audit skill. Run mypy strict-mode + AST annotation scanner. Audits -> Any density by layer, missing return types, # type: ignore justifications, cast() proliferation, and TYPE_CHECKING block hygiene. Produces a type safety scorecard and mypy strict-mode readiness assessment. Pass $ARGUMENTS to the skill if provided.
