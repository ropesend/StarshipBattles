# Stage 7 — Current State

> **Status:** scaffold — not yet filled in. The structure below is a template; future agents should research the codebase and replace each placeholder with concrete findings before this document is treated as authoritative.

> Stage 7 is deferred until the local server-style model (Stage 2 + Stage 1) is proven. This document should be light until those stages are real.

**As of:** YYYY-MM-DD

## What already exists in the codebase

Almost certainly nothing network-specific yet. Verify and note anything that does exist.

- `<path>` — `<one-line description>`

Particular things to look for:
- Any save/load code that already serializes per-empire state — this is a useful precursor.
- Any existing PBEM-like file exchange or import/export.
- Any session/lobby-shaped code, even informal.

## Dependency check

Stage 7 is gated by:

- Stage 1 (fog/intel): `<status>`
- Stage 2 (`PlayerTurnPackage`, `OrdersSubmission`, lifecycle): `<status>`
- Stage 2.5 (admin authority rules): `<status>`
- Stage 3 (serialization-ready DTOs): `<status>`

Stage 7 implementation projects should not begin until each of these is at least at "documented with tests" maturity.

## Open questions blocking even the planning

- First multiplayer mode (PBEM vs. LAN vs. online): `<decided?>`
- Trust model granularity (host-only, admin token, full account): `<decided?>`
- Whether tactical battles resolve server-side or per-player: `<decided?>`

## How to refresh this document

1. When Stages 1, 2, and 3 reach implementation maturity, revisit this file.
2. At that point, the focus should shift to: which existing DTOs / lifecycle states are network-ready, and which need adaptation?
3. Update the "As of" date.
