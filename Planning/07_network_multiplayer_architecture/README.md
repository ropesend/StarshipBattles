# Stage 7: Network Multiplayer Architecture

## Purpose

Add real multiplayer architecture after the local server-authoritative model has been proven.

This stage should build on player turn packages, command batches, and fog-limited information. It should not send raw authoritative game state to clients.

## Core Principle

Clients are untrusted. The authoritative server/session validates all commands and sends each player only the information their empire is allowed to know.

## Possible Multiplayer Modes

| Mode | Description | Complexity |
|---|---|---|
| Local hot-seat | Current/local players on one machine, but using player packages. | Low |
| PBEM-style async | Server/file exchange of turn packages and order submissions. | Low/medium |
| LAN host/client | One authoritative host, multiple local clients. | Medium |
| Online dedicated server | Remote authoritative server, persistent games. | High |
| Cloud/lobby matchmaking | Accounts, lobbies, hosted games, reconnects. | Very high |

Recommended first real multiplayer target: PBEM-style or LAN host/client, not full cloud matchmaking.

## Dependencies

This stage should wait until these foundations exist:

- Stage 1: fog/intel information boundary.
- Stage 2: player turn packages and order submissions.
- Stage 3: migration-ready DTO/serialization discipline.
- Stage 4/5 as needed for research and AI turn participation.

## First Objectives

1. Choose first multiplayer mode: PBEM-style, LAN, or online server.
2. Define transport-agnostic request/response DTOs.
3. Define game/session identity and player/empire identity.
4. Define order submission lifecycle: draft, submit, lock, resolve.
5. Define reconnect/resync behavior.
6. Define save/resume behavior for multiplayer sessions.
7. Ensure hidden information is never serialized into client packages.
8. Add server-side validation tests using malicious or stale command submissions.

## Initial Non-Goals

- Public matchmaking.
- Ranking/leaderboards.
- Anti-cheat beyond server authority.
- Account management.
- NAT traversal.
- Real-time tactical multiplayer.
- Cloud persistence.

## Design Questions

1. What should be the first supported multiplayer mode?
2. Should tactical battles be resolved server-side automatically, manually by host, or separately by involved players?
3. Should turns resolve only when all players submit orders, or after a timer/host override?
4. Should order submissions be editable after submission but before lock?
5. Should clients keep local caches of previous intel packages?
6. Should the network protocol be JSON first for debuggability?
7. Should replays be shared with all players or filtered by visibility?
8. How should desyncs be detected and reported?

## Acceptance Criteria

This stage is ready for implementation projects when there is a documented plan for:

- First multiplayer mode.
- Transport DTOs.
- Authority/trust model.
- Player package and order submission flow.
- Save/resume/reconnect behavior.
- Hidden-information protection.
- Server-side validation tests.

## Implementation Project Guidance

Use the existing `Projects/` system for implementation. Suggested project slices:

1. Add transport-agnostic multiplayer DTOs.
2. Add local fake-server adapter around GameSession.
3. Add PBEM/file package export/import or LAN prototype.
4. Add command submission lock/resolve flow.
5. Add malicious/stale command validation tests.
6. Add minimal multiplayer UI flow.
7. Add save/resume support.
