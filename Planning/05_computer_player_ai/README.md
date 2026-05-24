# Stage 5: Computer Player AI

## Purpose

Create computer-controlled empires that can play the strategy game through the same information and command surfaces as human players.

The AI should not be a privileged script that mutates raw game state. It should receive an empire-specific player package, make decisions based on that knowledge, and submit orders through the same command/batch system used by humans.

## Core Principle

Fair AI should know only what its empire knows. Debug or cheating AI modes may exist later, but the default AI should consume the same intel-limited view as a human empire.

## AI Layers

| Layer | Responsibility |
|---|---|
| Tactical AI | Movement, targeting, formations, retreat behavior inside battles. |
| Operational AI | Fleet movement, scouting, defense, invasion, interception, logistics. |
| Strategic AI | Research, colonization, ship design, production, expansion, economy. |
| Personality/policy AI | Aggressive, defensive, expansionist, isolationist, tech-focused, etc. |
| Diplomacy AI | Future stage: treaties, threats, trade, surrender, alliances. |

This stage is primarily about strategic and operational AI. Tactical AI improvements overlap with Stage 6.

## Dependencies

This stage should follow or at least depend on stable planning from:

- Stage 1: information boundary and fog of war.
- Stage 2: command batches and player turn packages.
- Stage 4: research integration.

AI can start with partial systems, but it should not be built around hidden raw-state access that will later need to be removed.

## First Objectives

1. Define the AI input package shape.
2. Define the AI output as command batches, not direct mutations.
3. Create a simple strategic AI loop: scout, colonize, build, research, defend.
4. Add difficulty/policy knobs without changing core rules.
5. Make AI decisions explainable through logs or debug reports.
6. Add deterministic test hooks for AI planning.
7. Ensure AI can function with incomplete/fogged information.
8. Keep tactical AI separate from empire-level strategy AI.

## Initial Non-Goals

- Perfect AI.
- Diplomacy.
- LLM-driven personality logic.
- Cheating/omniscient default AI.
- Real-time adaptive learning.
- Full ship-design optimization.

## Design Questions

1. Should AI be deterministic for a given seed and player package?
2. Should AI difficulty change rule access, bonuses, planning depth, or all three?
3. Should AI use scripted priorities, utility scoring, behavior trees, GOAP-style planning, or a hybrid?
4. How much ship design freedom should AI have in the first version?
5. Should each empire have an AI personality profile from game start?
6. Should AI orders be generated before or after human players submit their orders?
7. Should debug AI be allowed to inspect authoritative state for testing only?
8. Should AI maintain its own memory, or rely entirely on `EmpireIntelState`?

## Acceptance Criteria

This stage is ready for implementation projects when there is a documented plan for:

- AI input package.
- AI command-batch output.
- AI use of fog-limited information.
- Strategy/operational/tactical separation.
- Difficulty and personality knobs.
- Logging/debugging of AI decisions.

## Implementation Project Guidance

Use the existing `Projects/` system for implementation. Suggested project slices:

1. Define AI player package adapter.
2. Add simple command-producing AI controller.
3. Implement scout/colonize/build/research priorities.
4. Add AI order validation tests.
5. Add debug decision reports.
6. Add personality/difficulty profiles.
7. Add tactical/operational integration hooks.
