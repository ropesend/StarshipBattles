# PROJ-468: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source Audit

- **Audit directory:** `Reviews/results/2026-05-20_073330_docs-audit/`
- **Bundle counts:** Audit verified (this run): 40 | This bundle: 18 verified, 0 uncertain (resolved), 0 deferred | Project siblings: PROJ-467 (foundation), PROJ-469 (cross-doc consistency)
- **Doc-cluster coverage:** systems docs (`docs/systems/ability_reference.md`, `strategy_layer.md`, `fighters.md`, `minefields.md`, `research_system.md`), guide docs (`docs/guides/adding_abilities.md`, `component_system.md`, `qs_complex_design.md`, `testing_infrastructure.md`, `pre_commit_hooks.md`), the coordinated `docs/04_SERVICES.md` content error, and 2 missing-docs additions.
- **Severity breakdown:** 7 CRITICAL / 11 MAJOR.

### Mislead Risk Notes
This bundle holds the largest concentration of CRITICAL content-accuracy errors in the audit. Six docs (`04_SERVICES.md`, `ability_reference.md`, `strategy_layer.md`, `adding_abilities.md`, `component_system.md`, `qs_complex_design.md`) instruct developers to import from `game/strategy/services/component_inspector.py` and/or `game/strategy/services/effect_ability_metadata.py`. Both files were fully deleted (component_inspector split into `component_abilities.py` + `component_layers.py` by PROJ-433, shim removed by PROJ-454; effect_ability_metadata renamed to `ability_metadata.py` by PROJ-429/454). `strategy_layer.md:692` and `04_SERVICES.md:480` go further and assert a re-export shim "remains importable" / "is preserved" — a developer copying those example imports gets an immediate `ImportError`. Filesystem verification confirms both old paths absent and both replacements present.

## Initial Analysis
[Findings from Phase A code review - what was discovered about the codebase]

## Swarm Findings Summary
Combined analysis from individual agent reports in `findings/`.

### Architecture
[Key architecture points relevant to implementation]

### Key Patterns to Reuse
- **[Pattern Name]**: `file:lines` - description

### Dependencies & Risks
1. **[Risk/Dependency]** - mitigation approach

### Opportunities Discovered
- [Opportunity 1]

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
