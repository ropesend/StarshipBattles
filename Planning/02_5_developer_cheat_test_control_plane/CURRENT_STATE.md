# Stage 2.5 — Current State

> **Status:** scaffold — not yet filled in. The structure below is a template; future agents should research the codebase and replace each placeholder with concrete findings before this document is treated as authoritative.

> Goal of this document: ground the Stage 2.5 plan in the actual codebase so implementation projects start from reality, not abstraction.

**As of:** YYYY-MM-DD

## What already exists in the codebase

List existing cheat, debug, scenario, or test-control code. Use file paths.

- `<path>` — `<one-line description>`

Particular things to look for:
- Any "debug menu", debug panel, or developer-only UI.
- Test setup helpers that mutate game state directly (these are the closest analog to typed cheat commands and may inform DTO design).
- Save-game metadata fields, especially anything that already flags "this save used X".
- Scenario / preset / fixture loaders for tests.
- Any keyboard-shortcut handlers that bypass normal play (instant build, reveal map, etc.).

## What partially overlaps but doesn't match the planned shape

- `<path>` — overlaps with `<planned concept>`, differs because `<X>`

## What is missing entirely

- `<planned concept>` — no current code

## Hard blockers to the planned design

- `<thing in current code>` — contradicts `<planned rule>`, needs `<resolution>` first

Specifically check for:
- UI panels that mutate `game_state.X` directly (these are the pattern Stage 2.5 forbids long-term).
- Test code that depends on direct mutation (this is acceptable transitional state but should be inventoried).
- Any existing `eval`-style debug console.

## Naming map

| Planning term | Current code name (if any) | Notes |
|---|---|---|
| `AdminCommandSubmission` | | |
| `CheatCommand` / `DebugCommand` | | |
| `CheatCommandRegistry` | | |
| `CheatValidationContext` | | |
| `CheatModeState` | | |
| `DebugScenarioPreset` | | |
| `CheatAuditEvent` | | |
| `DeveloperConsole` | | |

## Dependency check

Stage 2.5 implementation depends on the Stage 2 `GameSession` command facade existing first. Note here whether that prerequisite is met yet:

- Stage 2 `GameSession` facade status: `<not started | in progress | complete>`
- Earliest reasonable Stage 2.5 skeleton start: `<date or milestone>`

## How to refresh this document

1. Grep for "cheat", "debug", "dev", "scenario", "preset", "test fixture" in the codebase.
2. List every place game state is mutated outside the normal turn/order flow.
3. Note any existing save metadata related to debug or test mode.
4. Update sections above and refresh the "As of" date.
