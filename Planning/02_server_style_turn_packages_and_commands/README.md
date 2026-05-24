# Stage 2: Server-Style Turn Packages And Commands

## Purpose

Make the local game architecture behave as if there is already an authoritative server, even before real networking exists.

The authoritative session should own the full game state. A player, whether human or AI, should receive a filtered turn package containing only the information their empire should know. The player then submits orders/commands, and the authoritative session validates and executes them.

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

## Proposed Concepts

| Concept | Responsibility |
|---|---|
| `PlayerTurnPackage` | Complete player-visible state for one empire at one turn. |
| `OrdersSubmission` | Commands submitted by one empire for a specific turn. |
| `CommandBatch` | Ordered list of validated or pending commands. |
| `CommandValidationContext` | Server-side authority, visibility, and rules context for command validation. |
| `TurnResolutionReport` | Results of executing all submitted orders for all players. |
| `PlayerEventPackage` | Filtered events visible to one empire. |

## First Objectives

1. Define the DTO shape for player-visible turn packages.
2. Define the DTO shape for player order submissions.
3. Ensure commands can be validated without trusting the UI.
4. Separate command creation from command authorization.
5. Ensure command processing can eventually accept all empires' orders before resolving the turn.
6. Keep local hot-seat support working while moving toward server-style boundaries.
7. Make AI consume the same kind of player turn package humans receive.

## Relationship To Stage 1

Stage 1 defines what an empire can know. Stage 2 packages that knowledge into a server-authoritative turn flow.

Stage 2 should not expose hidden authoritative state. It should consume the `IntelSnapshot` and owned-asset DTOs produced by Stage 1.

## Initial Non-Goals

- Actual sockets/network transport.
- Authentication.
- Cloud hosting.
- Anti-cheat hardening beyond not sending hidden state.
- Simultaneous remote UI clients.
- Persistent lobby/matchmaking systems.

## Design Questions

1. Should command batches be submitted once per turn or editable until all players are ready?
2. Should local hot-seat use the exact same `PlayerTurnPackage` path as future multiplayer clients?
3. Should invalid commands fail the whole batch or be rejected individually?
4. Should commands reference only stable IDs, never live object references?
5. How should stale intel affect commands against targets that may no longer be present?
6. Should the server allow speculative commands against remembered/ghost contacts?
7. Should AI orders be generated before or after human submissions are locked?

## Acceptance Criteria

This stage is ready for implementation projects when the following are documented:

- Player turn package shape.
- Orders submission shape.
- Server-side command validation approach.
- Relationship between intel snapshots and command legality.
- Local hot-seat compatibility path.
- Future network transport seam.

## Implementation Project Guidance

Use the existing `Projects/` system for implementation. Suggested slices:

1. Define command batch and player package DTOs.
2. Add server-style command validation context.
3. Add local package builder for the current active empire.
4. Convert one UI flow to consume a package instead of raw state.
5. Add multi-empire order staging without networking.
6. Add integration tests for two players submitting orders before resolution.
