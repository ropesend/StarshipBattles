# Stage 8 — Current State

> **Status:** scaffold — not yet filled in. The structure below is a template; future agents should research the codebase and replace each placeholder with concrete findings before this document is treated as authoritative.

> Stage 8 is deferred until the relevant interfaces stabilize. This document should be light until then.

**As of:** YYYY-MM-DD

## Profile data

Stage 8 is profiling-driven. Without measurements, there is nothing to migrate. Note any profiling work already done:

- `<path or report>` — `<what it measured, on what hardware, at what game scale>`

## Candidate migration areas (from the plan)

For each area, note current hot-path evidence (or lack of it) and stability of the surrounding interfaces.

| Area | Current performance evidence | Interface stability | Migration-ready? |
|---|---|---|---|
| Tactical combat simulation | | | |
| Turn processing | | | |
| Visibility / fog resolver | | | |
| Pathfinding | | | |
| AI planning / search | | | |
| Server authority core | | | |
| Serialization / validation core | | | |

## Dependency check

Stage 8 is gated by Stages 1, 2, 3, and the subsystem-specific stage (4/5/6).

- Stage 3 boundary discipline: `<status>`
- Subsystem-specific DTO/schema freeze: `<status>`
- Parity-test coverage for candidate subsystem: `<status>`

## How to refresh this document

1. Wait until at least one subsystem has both stable DTOs and measurable performance pressure.
2. At that point, capture before/after benchmarks and parity-test inventory here.
3. Update the "As of" date.
