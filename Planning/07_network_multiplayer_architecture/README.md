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
- Stage 2.5: developer cheat/test control plane, with clear host/server authority rules for admin/debug commands.
- Stage 3: migration-ready DTO/serialization discipline.
- Stage 4/5 as needed for research and AI turn participation.

## Relationship To Stage 2.5 Developer Cheat And Test Control Plane

Stage 2.5 cheat/admin/debug commands are privileged host/server operations in any future multiplayer mode.

Rules:

- Network clients are untrusted.
- Normal clients must not be able to invoke Stage 2.5 commands as normal gameplay orders.
- Cheat/admin commands require explicit server, host, or admin authority.
- Normal clients should not receive cheat capability lists unless they are host/admin/debug clients.
- Cheat-enabled multiplayer saves or sessions should be clearly flagged.
- PBEM, LAN, and online modes should each define whether cheat/admin commands are disabled, host-only, or otherwise explicitly authorized.
- Stage 2.5 is not a competitive anti-cheat system. It is a development and test control plane. Stage 7 owns network authority and abuse policy.

Potential future multiplayer/admin controls:

```text
HostEnableCheats
HostDisableCheats
AdminLoadScenarioPreset
AdminRevealForSpectator
AdminResolveStaleTurn
AdminForcePlayerReady
AdminReplacePlayerWithAI
```

## First Objectives

1. Choose first multiplayer mode: PBEM-style, LAN, or online server.
2. Define transport-agnostic request/response DTOs.
3. Define game/session identity and player/empire identity.
4. Define order submission lifecycle: draft, submit, lock, resolve.
5. Define reconnect/resync behavior.
6. Define save/resume behavior for multiplayer sessions.
7. Ensure hidden information is never serialized into client packages.
8. Add server-side validation tests using malicious or stale command submissions.
9. Define how Stage 2.5 admin/debug commands are disabled, host-only, or otherwise authorized in the chosen multiplayer mode.

## Initial Non-Goals

- Public matchmaking.
- Ranking/leaderboards.
- Anti-cheat beyond server authority.
- Account management.
- NAT traversal.
- Real-time tactical multiplayer.
- Cloud persistence.
- Implementing the Stage 2.5 cheat/debug command framework inside Stage 7.

## Design Questions

1. What should be the first supported multiplayer mode?
2. Should tactical battles be resolved server-side automatically, manually by host, or separately by involved players?
3. Should turns resolve only when all players submit orders, or after a timer/host override?
4. Should order submissions be editable after submission but before lock?
5. Should clients keep local caches of previous intel packages?
6. Should the network protocol be JSON first for debuggability?
7. Should replays be shared with all players or filtered by visibility?
8. How should desyncs be detected and reported?
9. In PBEM/LAN/online modes, should Stage 2.5 admin commands be disabled entirely, host-only, or allowed only for games explicitly marked as cheat/debug sessions?
10. Should spectator/debug clients be able to request omniscient packages, and if so how is that authority represented?

## Acceptance Criteria

This stage is ready for implementation projects when there is a documented plan for:

- First multiplayer mode.
- Transport DTOs.
- Authority/trust model.
- Player package and order submission flow.
- Save/resume/reconnect behavior.
- Hidden-information protection.
- Server-side validation tests.
- Stage 2.5 admin/debug command authorization rules for the chosen multiplayer mode.

## Implementation Project Guidance

Use the existing `Projects/` system for implementation. Suggested project slices:

1. Add transport-agnostic multiplayer DTOs.
2. Add local fake-server adapter around GameSession.
3. Add PBEM/file package export/import or LAN prototype.
4. Add command submission lock/resolve flow.
5. Add malicious/stale command validation tests.
6. Add minimal multiplayer UI flow.
7. Add save/resume support.
8. Add explicit host/admin authorization checks before exposing any Stage 2.5 command path in multiplayer.
