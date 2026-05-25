# Stage 2.5 Integration Notes

This document explains how the Developer Cheat And Test Control Plane should interact with the other planning stages.

The main Stage 2.5 plan defines the command/control architecture. This document is for future agents deciding where to add new cheat/debug controls as later gameplay systems are implemented.

## Integration Principle

Stage 2.5 should define the control plane. Later stages should add their own narrow controls through that plane.

Do not build a separate debug bypass for each subsystem.

Preferred pattern:

```text
New gameplay system
  -> defines normal DTOs / commands / packages
  -> defines any needed Stage 2.5 cheat/admin command DTOs
  -> registers commands with CheatCommandRegistry
  -> adds validation, audit events, and tests
```

## Stage 1 — Information Boundary And Fog Of War

Stage 1 must preserve hidden-information correctness for normal play while exposing explicit debug package modes for Stage 2.5.

Stage 2.5 needs Stage 1 seams for:

- global omniscient package mode,
- per-empire omniscient package mode,
- reveal system to empire,
- reveal galaxy to empire,
- reveal object/contact to empire,
- reset or edit empire intel,
- create or remove ghost contacts for testing.

Rules:

- Debug visibility controls must be reversible.
- Normal player packages must remain hidden-information safe.
- The UI should never receive hidden authoritative truth in normal mode.

## Stage 2 — Server-Style Turn Packages And Commands

Stage 2 provides the command/package boundary that Stage 2.5 uses.

Stage 2.5 should add a privileged command surface such as:

```text
AdminCommandSubmission
CheatValidationResult
CheatAuditEvent
CheatModeState
```

Rules:

- Keep normal `OrdersSubmission` distinct from `AdminCommandSubmission`.
- Validate admin commands server-side.
- Use stable IDs only.
- Return structured results.
- Do not allow cheat commands to become legal player orders by accident.

## Stage 3 — Migration-Readiness Standards

Stage 2.5 commands are future server-core boundary objects.

Rules:

- Use explicit DTOs.
- Keep scenario presets schema-validated.
- Add serialization round-trip tests.
- Avoid Python-only object references or dynamic tricks.
- Do not implement the developer console as arbitrary Python `eval`.

## Stage 4 — Research Integration

When research is integrated, add debug controls through Stage 2.5 rather than custom UI mutations.

Likely commands:

```text
AddResearchPoints
SetResearchPoints
UnlockTech
SetTechLevel
CompleteCurrentResearchProject
RevealResearchNode
ResetEmpireResearch
SetResearchAllocationDebug
```

Useful scenario presets:

```text
early_research_acceleration
late_game_component_unlock_test
sensor_tech_visibility_test
weapon_family_level_comparison
```

Acceptance expectation for Stage 4 implementation projects:

- At least a small set of research debug commands should be planned or stubbed once research state becomes authoritative and per-empire.

## Stage 5 — Computer Player AI

AI debug controls should use the Stage 2.5 control plane where practical.

Likely commands / flags:

```text
FreezeAI
UnfreezeAI
ForceAIPlanRecompute
SetAIPersonality
SetAIDifficultyDebug
GiveAIOmniscienceForTesting
ShowAIReasoningReport
ForceAICommandSubmission
DisableEmpireAI
EnableEmpireAI
```

Important distinction:

- Default fair AI should consume fog-limited packages.
- Debug or cheating AI modes may exist for testing, but they should be explicit, logged, and separate from normal AI difficulty/bonus design.

## Stage 6 — Tactical Combat Persistence And Formations

Tactical combat and formation work will need strong debug controls because repeated combat, formations, retreat behavior, and battle continuation are hard to test manually.

Likely commands / flags:

```text
AutoResolveBattleAsVictory
AutoResolveBattleAsDefeat
SpawnBattleAtSector
DamageShip
DestroyShip
RepairShip
ForceRetreat
SetFormation
FreezeBattleTick
ResumeBattleTick
ReplayBattleSeed
PersistTacticalSectorStateDebug
ClearTacticalSectorState
```

Useful scenario presets:

```text
same_sector_repeated_battle
formation_screening_test
retreat_vector_test
carrier_fighter_persistence_test
stationary_defense_test
```

## Stage 7 — Network Multiplayer Architecture

Stage 7 must treat Stage 2.5 commands as privileged host/server/admin operations, not normal client operations.

Rules:

- Network clients are untrusted.
- Cheat/admin commands require explicit server/host authority.
- Normal clients should not receive cheat capability lists unless they are host/admin/debug clients.
- Cheat-enabled multiplayer saves/sessions should be clearly flagged.
- PBEM/LAN/online modes should define whether cheat/admin commands are allowed, disabled, or host-only.

Potential future command categories:

```text
HostEnableCheats
HostDisableCheats
AdminLoadScenarioPreset
AdminRevealForSpectator
AdminResolveStaleTurn
AdminForcePlayerReady
AdminKickOrReplacePlayerWithAI
```

Do not design competitive anti-cheat in Stage 2.5. Stage 2.5 is for development and test control. Stage 7 owns real network authority policy.

## Stage 8 — Language Migration Plan

If the authoritative core later moves to Rust or C++, Stage 2.5 should remain usable through the same command boundary.

Rules:

- Admin command DTOs should be serialization-ready.
- Scenario preset commands should map cleanly to typed structs/enums.
- Cheat handlers should live on the authoritative side of the boundary.
- Python UI/console/preset loader should remain a client/front end.

## Cross-Stage Acceptance Rule

When a later stage creates a new major authoritative subsystem, future agents should ask:

```text
What narrow Stage 2.5 cheat/debug commands are needed to test this subsystem quickly?
```

The answer does not need to be a large implementation in that stage, but the stage should avoid creating hidden UI-side shortcuts that bypass the Stage 2.5 control plane.
