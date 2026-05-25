# Stage 2 Review And Expansion Notes

This document captures a code-review-style critique and expansion plan for `Planning/02_server_style_turn_packages_and_commands/README.md`.

It is intended for a future agent or human planner to use when fleshing out Stage 2 before implementation projects are created.

## Context

Stage 2 is about making the local game architecture behave as if there is already an authoritative server, even before real networking exists.

The authoritative session should own the full game state. A player, whether human or AI, should receive a filtered turn package containing only the information their empire should know. The player then submits orders/commands, and the authoritative session validates and executes them.

Relevant adjacent planning dependencies:

- Stage 1 defines the player information boundary, fog of war, per-empire intel, visibility, and ghost-contact concepts.
- Stage 2 packages that information into player-facing turn packages and command submissions.
- Stage 3 establishes migration-readiness standards such as DTO boundaries, stable IDs, deterministic services, and serialization-first thinking.
- Stage 4 depends on Stage 2 for research allocation commands and player-visible research package data.
- Stage 7 depends on Stage 2 for real multiplayer transport, command locking, server validation, stale submission handling, and hidden-information protection.

## High-Level Review

The current Stage 2 document is directionally correct, but it is still too thin to safely drive implementation.

It identifies the right concepts:

- `PlayerTurnPackage`
- `OrdersSubmission`
- `CommandBatch`
- `CommandValidationContext`
- `TurnResolutionReport`
- `PlayerEventPackage`

However, the document currently names the nouns without defining enough contracts, lifecycle rules, validation layers, DTO boundaries, or tests.

Before implementation begins, Stage 2 should become a contract document, not just a concept list.

## What Is Already Good

Stage 2 has the correct architectural goal:

```text
Authoritative GameSession
  -> build PlayerTurnPackage(empire_id)
  -> player submits OrdersSubmission / CommandBatch
  -> server/session validates commands
  -> all empires' commands execute through the turn engine
  -> produce new PlayerTurnPackage
```

This is the right bridge between the current single-process game and future multiplayer.

The document also correctly ties itself to Stage 1. Stage 1 defines what an empire can know; Stage 2 should package that knowledge without exposing hidden authoritative state.

The document also aligns well with Stage 3's migration-readiness goals:

- explicit DTOs at layer boundaries,
- stable IDs over object references,
- deterministic turn processing where practical,
- no UI objects in strategy/simulation state,
- no hidden global mutable game state,
- serialization-first thinking.

## Main Weakness: Concepts Are Not Yet Contracts

The current document lists useful concepts, but it does not yet say:

- what fields each DTO contains,
- what must be stable and serializable,
- what may be omitted,
- what owns identity,
- what invariants must be preserved,
- what the server/session must reject,
- what the UI/client is forbidden from doing.

A future agent should turn each major Stage 2 concept into a concrete draft contract.

## Suggested `PlayerTurnPackage` Draft Shape

A first draft does not need to be final, but it should be explicit enough to guide implementation and tests.

Possible package envelope:

```text
PlayerTurnPackage
  game_id
  turn_number
  empire_id
  package_id
  rules_version
  schema_version
  generated_at_or_sequence
  visible_galaxy_snapshot
  owned_assets
  known_contacts
  available_commands
  research_state
  economy_summary
  diplomacy_summary
  event_package
  pending_orders_snapshot
```

Important notes:

- The package is player-visible only.
- It must not include hidden authoritative state.
- It should be immutable from the UI/client perspective.
- It should use stable IDs, not live Python object references.
- It should be serialization-ready from the start, even if serialization is added after dataclasses exist.

## Suggested `OrdersSubmission` Draft Shape

Possible submission envelope:

```text
OrdersSubmission
  game_id
  turn_number
  empire_id
  package_id_seen_by_client
  submission_id
  submitted_at_or_sequence
  client_generated_sequence
  commands[]
```

Important notes:

- The submission references the package or turn state the player saw.
- The server/session decides whether that package reference is still valid.
- Commands should be serializable DTOs.
- Commands should reference stable IDs only.
- The UI/client may draft commands, but authorization belongs to the authoritative session.

## Suggested `CommandBatch` Draft Shape

A `CommandBatch` should distinguish raw submitted commands from validation results.

Possible structure:

```text
CommandBatch
  game_id
  turn_number
  empire_id
  submission_id
  validation_status
  commands[]
  accepted_commands[]
  rejected_commands[]
  warnings[]
```

A future agent should decide whether `CommandBatch` is:

1. the raw submitted command container,
2. the validated executable container,
3. or two separate types.

Recommendation: use separate types if the implementation starts to blur submitted commands with executable commands.

## Suggested `CommandValidationResult` Shape

Stage 2 should define validation result semantics before implementation.

Possible shape:

```text
CommandValidationResult
  command_id
  command_type
  status
  error_code
  message
  blocking
  dependency_failed
  normalized_command
```

Suggested statuses:

```text
accepted
rejected
warning
normalized
```

Suggested error categories:

```text
schema_invalid
wrong_turn
wrong_empire
unknown_command_type
unknown_object_id
not_owner
not_visible
stale_intel
insufficient_resources
illegal_state
conflicts_with_command
command_dependency_failed
server_error
```

## Boundary Rules To Add To Stage 2

The Stage 2 README should add a hard boundary-rules section.

Suggested wording:

```text
## Boundary Rules

- Player/UI code must not mutate authoritative state directly.
- Player-facing DTOs are immutable snapshots.
- Commands use stable IDs only.
- All package/submission DTOs must be serialization-ready.
- UI may create command drafts, but only GameSession validates and applies commands.
- AI should eventually consume the same player package and emit the same order submission shape as a human player.
- Any temporary bypasses must be explicitly marked as transitional.
```

## Stable IDs Should Be A Hard Rule

The current Stage 2 document asks whether commands should reference only stable IDs and never live object references.

Recommended answer: yes.

This should be promoted from an open question to a design rule.

Suggested wording:

```text
All player packages and command submissions must be serializable DTOs using stable IDs only.
No UI object references, Python object references, manager references, live fleet objects, live planet objects, or direct authoritative model references may cross the player/session boundary.
```

This is required for:

- multiplayer,
- save/load,
- replay/debugging,
- AI parity,
- future Rust/C++ migration,
- automated validation tests.

## Player Package Should Be Read-Only

The current Stage 2 doc says the UI should not operate on raw authoritative game state.

That should become a concrete rule:

```text
PlayerTurnPackage is immutable from the client/UI perspective.
The UI may derive temporary view models from it.
The UI may create command drafts.
The UI may not mutate authoritative strategy objects directly.
```

Without this rule, the project risks creating DTOs on paper while the UI continues to mutate live game state through side channels.

## Command Lifecycle Needs To Be Defined

The current Stage 2 document asks whether command batches are submitted once per turn or editable until all players are ready.

This question is important enough to become a required lifecycle section.

Recommended initial lifecycle:

```text
Drafting
  UI creates/edits commands locally against the current PlayerTurnPackage.

Submitted
  Player sends OrdersSubmission for empire + turn.

Validated
  Server/session validates each command and returns accepted/rejected status.

Locked
  Empire is marked ready. No further changes unless explicitly unlocked.

Resolving
  Turn engine executes all locked empire command batches.

Resolved
  TurnResolutionReport is generated, then new PlayerTurnPackage is built.
```

This supports local hot-seat now and future multiplayer later.

## Submission Editing Recommendation

Recommended default:

- Allow command drafts to be freely edited before submission.
- Treat submission as a candidate validation event.
- Allow replacing a submission until the empire is explicitly locked or the turn begins resolving.
- Once locked, require an explicit unlock action before replacing orders.

This gives local play flexibility without losing the future lock/resolve model required by multiplayer.

## Failure Semantics Recommendation

The current Stage 2 document asks whether invalid commands fail the whole batch or are rejected individually.

Recommended answer:

```text
Default: reject invalid commands individually.
Reject the whole submission only if the envelope is invalid.
```

Examples:

```text
Bad game_id / empire_id / turn_number / malformed schema
  -> reject whole submission.

One invalid fleet command among ten valid commands
  -> reject that command, accept the rest unless there is a declared dependency chain.

Command depends on a prior rejected command
  -> reject dependent command with dependency_failed.
```

This is friendlier for UI, AI, PBEM, debugging, and future network play.

## Validation Layers To Add

Stage 2 currently says commands should be validated without trusting the UI and command creation should be separated from command authorization.

That needs more detail.

Suggested validation layers:

```text
Schema validation
  Is this a known command type with valid fields?

Identity validation
  Does the referenced game, empire, package, and object ID exist?

Authority validation
  Does this empire own or control the referenced object?

Visibility/intel validation
  Is the target currently visible, remembered, or completely unknown?

Rules validation
  Is the command legal under game rules?

Resource validation
  Does the empire have the required resources, movement, command points, build capacity, etc.?

Temporal validation
  Is this command for the current turn and based on a package that is not stale?

Conflict validation
  Does this command conflict with another command in the same batch?
```

The goal is to prevent validation logic from being scattered through UI, strategy services, and turn-engine internals.

## `CommandValidationContext` Expansion

The current Stage 2 concept list includes `CommandValidationContext`, but the document does not yet define what it contains.

Suggested context fields:

```text
CommandValidationContext
  authoritative_session
  game_id
  turn_number
  empire_id
  package_id
  empire_authority_view
  intel_snapshot_or_resolver
  ruleset
  resource_view
  object_id_resolver
  current_submission
  already_accepted_commands
```

Important design rule:

- The context is server-side only.
- It may access authoritative state.
- It should not be sent to the UI/client.
- It should expose narrow validation helpers instead of dumping the full game state into command validators.

## Relationship To Stage 1

Stage 2 should explicitly consume Stage 1's intel output.

Suggested wording:

```text
Stage 2 does not decide what an empire knows. Stage 1 owns visibility and intel rules.
Stage 2 consumes Stage 1's player-visible intel snapshots and uses them to build packages and validate commands.
```

Key dependency:

- Stage 1 determines whether an object is unknown, remembered, contact-level, identified, or detailed.
- Stage 2 decides whether a command is legal given that intel level.

Example:

```text
A player may be allowed to move toward a remembered location.
A player may not be allowed to inspect hidden fleet composition.
A player may be allowed to attack a currently visible hostile fleet.
A player may or may not be allowed to issue speculative orders against a ghost contact, depending on design decision.
```

## Relationship To Stage 3

Stage 2 should explicitly adopt Stage 3 rules:

- DTOs at layer boundaries.
- Stable IDs instead of object references.
- Serialization-first design.
- Deterministic turn processing where practical.
- No hidden global mutable game state.
- Constructor injection or explicit provider seams.
- Narrow public APIs.

Suggested wording:

```text
Stage 2 DTOs are migration-boundary candidates. They should be designed as if they may later cross a Python/Rust/C++ boundary or network boundary.
```

## Relationship To Stage 4

Stage 4 depends on command/package architecture for research integration.

Stage 2 should explicitly say that research allocation is a candidate early command because it is:

- empire-owned,
- turn-based,
- serializable,
- easy to validate compared with movement/combat,
- needed by Stage 4.

Possible command:

```text
SetResearchAllocationCommand
  empire_id
  allocation_id_or_field_id
  allocation_weight_or_points
```

Possible package section:

```text
research_state
  known_fields
  available_projects
  current_allocations
  accumulated_research_points
  completed_techs
  visible_unlocks
```

## Relationship To Stage 7

Stage 7 depends on Stage 2 for the multiplayer trust model.

Stage 2 should avoid implementing sockets or networking, but it should define transport-agnostic DTOs and lifecycle states that can later support:

- PBEM/file exchange,
- LAN host/client,
- online authoritative server,
- reconnect/resync,
- stale command rejection,
- hidden-information protection,
- malicious command validation tests.

Suggested wording:

```text
Stage 2 is the local fake-server architecture. Stage 7 should not need to invent a different package/command lifecycle; it should add transport around the Stage 2 boundary.
```

## Recommended First Vertical Slice

The Stage 2 README currently suggests broad slices such as defining DTOs, adding validation context, adding a package builder, converting one UI flow, and adding multi-empire staging.

That is good, but the first slice should be more specific.

Recommended first implementation project:

```text
Stage 2 Slice A: Package/Command Skeleton With One Safe Command

Command candidate:
  SetResearchAllocationCommand or RenameFleetCommand

Deliverables:
  PlayerTurnPackage envelope
  OrdersSubmission envelope
  Command DTO base shape
  CommandValidationResult
  GameSession package builder facade
  GameSession submit_orders facade
  Per-command validation result list
  Serialization round-trip tests
  Two-empire package isolation test
```

## Recommended First Command Choice

Two good candidates:

### Option A: `RenameFleetCommand`

Pros:

- Very low gameplay risk.
- Easy to validate ownership.
- Easy to see result in UI.
- Avoids research dependencies.
- Avoids pathfinding, combat, construction, resource costs, and timing complexity.

Cons:

- Less strategically meaningful.
- Does not exercise turn-resolution complexity.

### Option B: `SetResearchAllocationCommand`

Pros:

- Directly supports Stage 4.
- Turn-based and empire-owned.
- Naturally package/command oriented.
- Good early test of package state, command submission, validation, and next-turn reflection.

Cons:

- Depends on research model decisions.
- May be premature if research integration is not ready.

Recommendation:

- Use `RenameFleetCommand` if the goal is to prove the architecture with minimum risk.
- Use `SetResearchAllocationCommand` if Stage 4 is expected to begin soon and the research foundation is stable enough.

Avoid using fleet movement, construction, combat, colonization, or diplomacy as the first command. Those involve too many rules and will obscure whether the package/command boundary works.

## AI Integration Recommendation

The current Stage 2 document says AI should consume the same kind of player turn package humans receive.

That is the right long-term direction.

Suggested rule:

```text
AI should eventually consume PlayerTurnPackage and emit OrdersSubmission.
Any temporary AI access to authoritative state must be explicitly marked as transitional and should not be copied into new systems.
```

Potential staged approach:

1. Human UI uses package/command path for one safe command.
2. AI adapter is added for the same package/command path.
3. AI remains allowed to use authoritative state only in clearly marked legacy code.
4. New AI features must use the package/command path unless a project explicitly approves an exception.

## Hot-Seat Recommendation

Local hot-seat should use the same package/command path as future multiplayer.

Suggested wording:

```text
Local hot-seat is the first client of the server-style architecture. It should not be a special bypass.
```

This means:

- active empire receives a package,
- UI displays that package,
- UI submits commands,
- session validates commands,
- empire locks orders,
- next empire receives its own package,
- turn resolves after all required empires are locked or controlled by AI.

## Open Questions For Ross

A future agent should ask or resolve these before finalizing Stage 2 implementation projects:

1. For local play, should Stage 2 support one active empire at a time, or all empires staging orders before any turn resolves?
2. Should local hot-seat be treated as a first-class target or just a stepping stone toward AI/multiplayer?
3. Should submitted orders be editable until all players are ready, or should submit mean locked?
4. Should invalid commands be rejected individually by default, with whole-submission rejection only for bad envelopes?
5. Should Stage 2 define a `GameSession` facade now, even if it initially wraps the existing strategy/turn engine?
6. Should `PlayerTurnPackage` include pending orders already submitted by that empire so the UI can reload/review/edit orders?
7. Should AI be forced onto the package/command path immediately, or can it use authoritative state temporarily while the human UI is migrated first?
8. Should speculative commands against remembered/ghost contacts be allowed?
9. Should Stage 2 start with JSON-serializable DTOs from day one, or Python dataclasses first with serialization added shortly after?
10. What should the first vertical-slice command be: research allocation, rename fleet, fleet stance, build queue change, or fleet movement?

## Suggested README Additions

A future agent should add or merge the following sections into `Planning/02_server_style_turn_packages_and_commands/README.md`:

```text
## Boundary Rules
## PlayerTurnPackage Draft Shape
## OrdersSubmission Draft Shape
## CommandBatch And Validation Result Shape
## Command Lifecycle
## Submission Editing And Locking
## Validation Layers
## Failure Semantics
## Relationship To Stage 1 Intel
## Relationship To Stage 3 Migration-Readiness Standards
## Relationship To Stage 4 Research Integration
## Relationship To Stage 7 Multiplayer Architecture
## First Vertical Slice
## Test Strategy
## Open Decisions
```

## Suggested Test Strategy

Stage 2 should not be considered ready for implementation without concrete tests.

Recommended tests:

```text
Two empires receive different packages from the same authoritative state.
A package contains no hidden enemy object details.
A command using a live object reference is impossible or rejected.
A command from the wrong empire is rejected.
A stale-turn submission is rejected.
A valid command from a package is accepted.
One invalid command does not necessarily poison the whole batch.
AI can consume the same package type as human UI.
Round-trip serialization preserves command/package identity fields.
A local hot-seat flow can package, submit, lock, switch empire, submit, and resolve.
```

## Suggested Acceptance Criteria Expansion

Current Stage 2 acceptance criteria are good but should be expanded.

Suggested acceptance criteria before creating implementation projects:

- `PlayerTurnPackage` draft schema exists.
- `OrdersSubmission` draft schema exists.
- Command identity and stable-ID rules are documented.
- Command lifecycle is documented.
- Submission editing/locking policy is documented.
- Validation layers are documented.
- Per-command vs whole-submission failure semantics are documented.
- Relationship to Stage 1 intel snapshots is documented.
- Relationship to Stage 3 migration-readiness rules is documented.
- At least one safe vertical-slice command is chosen.
- Test strategy is documented.
- Open decisions are listed clearly.

## Suggested Implementation Project Slices

Use the existing `Projects/` system for implementation after this planning document is expanded.

Recommended project sequence:

```text
Project 1: Define Stage 2 DTO contracts
  - PlayerTurnPackage envelope
  - OrdersSubmission envelope
  - Command DTO base/protocol
  - CommandValidationResult
  - Serialization round-trip tests

Project 2: Add local GameSession package/command facade
  - build_player_turn_package(empire_id)
  - submit_orders(submission)
  - validate_orders(submission)
  - no UI conversion yet

Project 3: Implement one safe command vertical slice
  - RenameFleetCommand or SetResearchAllocationCommand
  - validation
  - application
  - package reflection after command

Project 4: Add local hot-seat order staging
  - draft/submit/lock lifecycle
  - two-empires-submit-before-resolution test

Project 5: Convert one UI flow to package/command boundary
  - UI reads package-derived view model
  - UI emits command DTO
  - UI stops mutating authoritative state for that flow

Project 6: Add AI package/command adapter
  - AI consumes package for one command path
  - AI emits OrdersSubmission
```

## Risks To Watch

### Risk: DTOs become wrappers around live objects

Mitigation:

- stable IDs only,
- serialization tests,
- no live object references in packages/commands.

### Risk: UI keeps mutating authoritative state

Mitigation:

- convert one UI flow at a time,
- add tests or architecture checks for direct mutation where practical,
- mark temporary bypasses clearly.

### Risk: command validation scatters across systems

Mitigation:

- define validation layers,
- centralize validation entry points,
- use command-specific validators behind a shared interface.

### Risk: Stage 2 overreaches into networking

Mitigation:

- keep Stage 2 transport-agnostic,
- do not implement sockets/auth/lobbies,
- define DTOs and lifecycle only.

### Risk: Stage 2 blocks Stage 1

Mitigation:

- allow package skeletons to start with current visible data,
- mark hidden-information enforcement as dependent on Stage 1,
- add stronger tests once Stage 1 intel snapshots exist.

## Summary Recommendation

Flesh Stage 2 into a contract-first planning document before implementation.

The most important decisions to lock down are:

1. stable IDs only,
2. immutable player packages,
3. explicit package/submission envelopes,
4. draft/submit/validate/lock/resolve lifecycle,
5. per-command validation results,
6. individual command rejection by default,
7. one safe vertical-slice command,
8. tests proving hidden state does not cross the boundary.

Once those are documented, implementation should proceed through a small safe command rather than starting with movement, construction, combat, or networking.
