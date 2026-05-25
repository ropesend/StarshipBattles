# Stage 2: Server-Style Turn Packages And Commands

## Purpose

Make the local game architecture behave as if there is already an authoritative server, even before real networking exists.

The authoritative session should own the full game state. A player, whether human or AI, should receive a filtered turn package containing only the information their empire should know. The player then submits orders/commands, and the authoritative session validates and executes them.

> **Companion document:** detailed DTO field-list drafts, the first-vertical-slice command choice, and concrete test wording live in [`STAGE_2_REVIEW_AND_EXPANSION_NOTES.md`](STAGE_2_REVIEW_AND_EXPANSION_NOTES.md). Read it before creating Stage 2 implementation projects. This README owns the **planning-level rules**; the expansion notes own the **implementation-prep detail** that will be revised as projects begin.

## Core Principle

Do not let the player-facing client or UI operate on raw authoritative game state. Even in local hot-seat mode, the interface should move toward this shape:

```text
Authoritative GameSession
  -> build PlayerTurnPackage(empire_id)
  -> player submits OrdersSubmission / CommandBatch
  -> server/session validates commands
  -> all empires' commands execute through the turn engine
  -> produce new PlayerTurnPackage
```

This is the bridge between the current single-process game and future multiplayer.

## Boundary Rules

These are hard rules, not open questions. They scope what Stage 2 implementation projects are allowed to do and what they must refuse.

- The player/UI code must not mutate authoritative state directly. The authoritative session is the only path to mutation.
- `PlayerTurnPackage` is **immutable** from the client/UI perspective. The UI may derive view models from it, but it must not mutate it in place.
- All player packages and command submissions are **serializable DTOs using stable IDs only**. No live Python object references, manager references, fleet/planet/ship object references, or UI references may cross the player/session boundary.
- The UI may create command **drafts**. Only the `GameSession` validates and applies commands.
- AI must eventually consume the same `PlayerTurnPackage` type and emit the same `OrdersSubmission` shape as a human player. Any temporary AI access to authoritative state is transitional and must be marked as such.
- Local hot-seat is the **first client** of the server-style architecture, not a bypass.
- Hidden authoritative state must never be shipped to the UI in normal package mode. Debug omniscience (Stage 2.5) is a server-side package-building mode, not a UI-side raw-state read.
- Cheat/admin commands (Stage 2.5) live on a separate command surface from normal player orders. Normal orders must not be able to invoke cheat behavior by accident.

## Command Lifecycle

```text
Drafting    UI creates/edits commands locally against the current PlayerTurnPackage.
Submitted   Player sends OrdersSubmission for empire + turn.
Validated   Session validates each command, returns accepted/rejected per command.
Locked      Empire is marked ready. No further changes unless explicitly unlocked.
Resolving   Turn engine executes all locked empire command batches.
Resolved    TurnResolutionReport is produced, then a new PlayerTurnPackage is built.
```

Default policy: command drafts may be freely edited before submission, a submission may be replaced until the empire is locked, and once locked an explicit unlock action is required before replacement. This supports local hot-seat now and multiplayer later without a second lifecycle.

## Failure Semantics

- **Default:** reject invalid commands **individually**. Accept the rest of the submission.
- **Whole-submission rejection** is reserved for envelope errors (bad `game_id`, `empire_id`, `turn_number`, malformed schema, stale `package_id`).
- A command that depends on a prior rejected command in the same batch should be rejected with a `dependency_failed` reason.
- Validation results are structured per command (`accepted` | `rejected` | `warning` | `normalized`) so UIs, AI, PBEM, and debugging can all reason about partial success.

## Validation Layers

Command validation should live in defined layers rather than scattered across UI, strategy services, and turn-engine internals. The intended layers are:

| Layer | Question |
|---|---|
| Schema | Is this a known command type with valid fields? |
| Identity | Do referenced game/empire/package/object IDs exist? |
| Authority | Does this empire own or control the referenced object? |
| Visibility / intel | Is the target visible, remembered, or completely unknown (per Stage 1)? |
| Rules | Is the command legal under current game rules? |
| Resource | Does the empire have required resources, movement, command points, etc.? |
| Temporal | Is the command for the current turn and based on a fresh package? |
| Conflict | Does the command conflict with another command in the same batch? |

The `CommandValidationContext` is server-side only and must not be exposed to the UI.

## Proposed Concepts

| Concept | Responsibility |
|---|---|
| `PlayerTurnPackage` | Complete player-visible state for one empire at one turn. |
| `OrdersSubmission` | Commands submitted by one empire for a specific turn. |
| `CommandBatch` | Ordered list of validated or pending commands. |
| `CommandValidationContext` | Server-side authority, visibility, and rules context for command validation. |
| `TurnResolutionReport` | Results of executing all submitted orders for all players. |
| `PlayerEventPackage` | Filtered events visible to one empire. |

## Relationship To Stage 2.5 Developer Cheat And Test Control Plane

Stage 2.5 builds on the Stage 2 command/package boundary but adds a separate privileged command surface for developer cheats, debug controls, and scenario setup.

Stage 2 should leave room for a distinct admin/debug envelope such as:

```text
OrdersSubmission        # normal gameplay orders
AdminCommandSubmission  # privileged cheat/debug/admin commands
```

or an equivalent scoped envelope:

```text
CommandEnvelope
  command_scope = gameplay | admin_debug
```

Hard boundary rules:

- Normal gameplay commands and Stage 2.5 cheat/admin commands must be visibly distinct.
- Normal player orders must not be able to invoke cheat behavior by accident.
- Cheat/admin command validation belongs to the authoritative session, not the UI.
- Both normal commands and cheat/admin commands should use stable IDs, not live object references.
- Stage 2.5 commands may use the same transport/facade concepts, but they should have separate capability checks, validation results, audit events, and save-flag behavior.
- A future developer console should parse text into typed admin command DTOs rather than directly mutating game state.

## First Objectives

1. Define the DTO shape for player-visible turn packages.
2. Define the DTO shape for player order submissions.
3. Ensure commands can be validated without trusting the UI.
4. Separate command creation from command authorization.
5. Ensure command processing can eventually accept all empires' orders before resolving the turn.
6. Keep local hot-seat support working while moving toward server-style boundaries.
7. Make AI consume the same kind of player turn package humans receive.
8. Preserve an explicit future seam for Stage 2.5 `AdminCommandSubmission` / cheat-debug command handling.

## Relationship To Stage 1

Stage 1 owns the visibility/intel rules. Stage 2 packages that knowledge into a server-authoritative turn flow and uses it to validate commands.

- Stage 1 determines whether an object is unknown, remembered, contact-level, identified, or detailed.
- Stage 2 decides whether a command is legal given that intel level (e.g., move toward a remembered hex may be allowed; inspect hidden fleet composition is not; speculative orders against ghost contacts are a design decision flagged in Open Decisions).

Stage 2 must not expose hidden authoritative state. It should consume the `IntelSnapshot` and owned-asset DTOs produced by Stage 1.

Stage 2.5 debug visibility controls such as omniscient view must also respect this layering: they should request a debug package mode from the authoritative session rather than letting UI code access raw hidden state directly.

## Relationship To Stage 3 (Migration-Readiness)

Stage 2 DTOs are **migration-boundary candidates**. They should be designed as if they may later cross a Python ↔ Rust/C++ boundary or a network boundary. Stage 2 implementation must follow Stage 3 rules: explicit DTOs at layer boundaries, stable IDs over object references, serialization-first design, deterministic turn processing where practical, no hidden global mutable state, constructor injection or explicit provider seams, and narrow public APIs.

## Relationship To Stage 4 (Research Integration)

Stage 4 depends on Stage 2's command/package architecture. Research allocation is a natural early candidate command because it is empire-owned, turn-based, serializable, and easy to validate compared with movement or combat. The Stage 2 package should reserve a `research_state` section (known fields, available projects, current allocations, accumulated RP, completed techs, visible unlocks) before Stage 4 implementation begins so research projects don't invent a parallel data surface.

## Relationship To Stage 7 (Network Multiplayer)

Stage 2 is the local fake-server architecture. Stage 7 should not need a different package/command lifecycle; it should add transport around the Stage 2 boundary. To make that possible, Stage 2 must keep DTOs transport-agnostic, define stale-submission handling, never leak hidden information, and treat clients as untrusted-equivalent even in local mode.

## Initial Non-Goals

- Actual sockets/network transport.
- Authentication.
- Cloud hosting.
- Anti-cheat hardening beyond not sending hidden state.
- Simultaneous remote UI clients.
- Persistent lobby/matchmaking systems.
- Stage 2.5 cheat/debug command implementation.

## Open Decisions

Items now settled as hard rules above (and so removed from this list): stable IDs only, immutable packages, individual command rejection by default, hot-seat uses the same package/command path, AI must consume the same package type.

Still open:

1. How should stale intel affect commands against targets that may no longer be present (silent normalization, warning, or reject)?
2. Should the server allow speculative commands against remembered/ghost contacts?
3. Should AI orders be generated before or after human submissions are locked?
4. Should the Stage 2 command facade define `AdminCommandSubmission` from the start, or should Stage 2.5 add it as a parallel facade once normal commands are stable?
5. Should `PlayerTurnPackage` include the empire's already-submitted pending orders so the UI can reload/review/edit them?
6. Should Stage 2 start with JSON-serializable DTOs from day one, or Python dataclasses first with serialization added shortly after?
7. For local play, should Stage 2 support one active empire at a time, or all empires staging orders before any turn resolves?
8. What should the first vertical-slice command be? (See expansion notes for the `RenameFleetCommand` vs. `SetResearchAllocationCommand` analysis.)

## Acceptance Criteria

This stage is ready for implementation projects when the following are documented:

- `PlayerTurnPackage` draft schema (see expansion notes).
- `OrdersSubmission` draft schema (see expansion notes).
- Command identity and stable-ID rules (covered above in Boundary Rules).
- Command lifecycle (covered above).
- Submission editing/locking policy (covered above).
- Validation layers (covered above).
- Per-command vs. whole-submission failure semantics (covered above).
- Relationship between intel snapshots and command legality (covered in Relationship to Stage 1).
- Relationship to Stage 3 migration-readiness rules (covered above).
- Local hot-seat compatibility path.
- Future network transport seam.
- Documented seam for Stage 2.5 privileged admin/debug command submissions.
- At least one safe vertical-slice command chosen.
- Test strategy documented (see expansion notes).
- Remaining open decisions explicitly listed above.

## Implementation Project Guidance

Use the existing `Projects/` system for implementation. Suggested slices:

1. Define command batch and player package DTOs.
2. Add server-style command validation context.
3. Add local package builder for the current active empire.
4. Convert one UI flow to consume a package instead of raw state.
5. Add multi-empire order staging without networking.
6. Add integration tests for two players submitting orders before resolution.
7. When this facade exists, Stage 2.5 can add the first admin/cheat command skeleton without creating UI-side mutation shortcuts.
