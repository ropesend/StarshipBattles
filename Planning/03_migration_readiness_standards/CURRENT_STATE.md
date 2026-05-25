# Stage 3 — Current State

> **Status:** scaffold — not yet filled in. The structure below is a template; future agents should research the codebase and replace each placeholder with concrete findings before this document is treated as authoritative.

> Stage 3 is unusual: it is **continuous** rather than a single milestone. This "current state" doc should be more of a **migration-readiness audit** than a one-time gap analysis. Re-run it periodically.

**As of:** YYYY-MM-DD

## DTO discipline

Where do explicit DTOs already exist at layer boundaries, and where are raw dicts / live objects still crossing?

- Boundaries with proper DTOs: `<list>`
- Boundaries still using raw dicts or live objects: `<list>`

## Stable IDs vs. live object references

Where do save/network/replay candidates already use stable IDs, and where are Python object references still load-bearing?

- Stable IDs already in use for: `<list>`
- Still using object identity (would break across save/load or process boundary): `<list>`

## Hidden global mutable state

List any module-level mutable singletons that game logic depends on.

- `<path / variable>` — used by `<list of callers>`

## UI ↔ game-state coupling

List places where UI objects are referenced from game-core code, or where game-core types leak into UI code in ways that would block migration.

- `<path>` — `<description of coupling>`

## Determinism

Where is randomness injected vs. globally seeded? Where is turn processing already deterministic given a seed?

- Deterministic regions: `<list>`
- Non-deterministic regions (global random, time-of-day-based seeds, etc.): `<list>`

## Serialization readiness

Which DTOs already have round-trip serialization tests? Which planned DTOs would fail one if it were written today?

- DTOs with round-trip coverage: `<list>`
- DTOs that would currently fail round-trip: `<list>`

## Lint / architecture checks

Note any existing lints, import-direction checks, or architecture tests that enforce migration-readiness today.

- `<path or rule>` — `<what it enforces>`

## Top blockers (prioritized)

Once the above is filled in, list the top ~5 single biggest blockers to migration readiness. These are what new Stage 3 enforcement projects should pick from.

1. `<blocker>`
2. `<blocker>`

## How to refresh this document

1. Walk `game/` top-to-bottom, noting boundary types and coupling.
2. Re-run any architecture lints; record results.
3. Check the existing test suite for serialization round-trip coverage.
4. Update sections above and refresh the "As of" date.
