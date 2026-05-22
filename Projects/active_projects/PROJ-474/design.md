# PROJ-474: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source / gating
Deferred tail of **PROJ-472** (close the StrategySessionFacade read-path gap).
GATED on PROJ-472's runtime-import read guard
(`tests/static_guards/test_facade_read_path_imports_guard.py`) landing — this
project consolidates that guard's UI-safe allowlist. See
`Projects/active_projects/PROJ-472/plan.md` and the consult at
`AgentCoordination/Scratchpad/Consult/proj472_preflesh/advice.md` §1, §4.

## Initial Analysis
This is the value/config slice of the option-(b) policy. The codebase has many
`game/ui/` imports of strategy types that are NOT live-session reads but
immutable config/value/enum/protocol surfaces (verified live 2026-05-21 by the
PROJ-472 planning pass):
- New-game setup builds a `GameConfig` before any `GameSession` exists
  (`new_game_setup_controller.py:39-44`).
- Race setup edits a standalone `RaceConfig` + factor definitions
  (`race_environment_panel.py:25-35`, `preference_row.py:37-40`).
- Transfer UI uses `ContainableKind` tags over facade-provided snapshots
  (`transfer_view_model.py:243-255`).
- Planet-ability UI uses `ActivationPhase` as a status enum
  (`planet_abilities_controller.py:30-34`).

The work is mostly documentation + allowlist cleanup: bless these types
explicitly in Pattern #5 + the guard allowlist with reason comments, after
verifying each use site is genuinely value-shaped (not a live traversal hiding
behind a value name).

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
