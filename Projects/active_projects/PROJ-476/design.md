# PROJ-476: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source / gating
Deferred tail of **PROJ-472**. GATED on PROJ-472's guards landing and informed by
PROJ-475 (the live-gameplay-UI boundary). Tooling/editor/sandbox screens are
migrated LAST because they likely need broader exemptions than the live strategy
UI. See `Projects/active_projects/PROJ-472/plan.md` and the consult at
`AgentCoordination/Scratchpad/Consult/proj472_preflesh/advice.md` §4 + Open Questions.

## Initial Analysis
The 93-file `game/ui/` strategy-import set (verified 2026-05-21) includes
tooling/sandbox surfaces that are NOT live strategy screens: `battle_setup` (4),
`galaxy_test` (3), `race_setup` (4), and tooling parts of `builder` (3). These
construct/inspect config or drive test flows, so a single live-UI guard would
otherwise need a large allowlist for them (consult Open Question 1). Treating them
as a separate scope keeps the live-UI guard tight while letting tooling screens
take file+reason-scoped exemptions where facade migration adds no boundary value.

### Dependencies & Risks
1. **Over-exemption** — tooling waivers must be file+reason scoped, not blanket
   subpackage waivers, or the guard loses meaning.
2. **Shared widgets** — some tooling screens reuse widgets also used by live UI;
   migrate shared code under the PROJ-475 live-UI rules, not the tooling exemption.

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
