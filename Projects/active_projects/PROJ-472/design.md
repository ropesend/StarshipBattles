# PROJ-472: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source
- **Origin:** Deferred scope extracted from PROJ-470 (pattern-conformance cleanup) under Protocol 06 / Protocol 07 after a dual independent+Codex review on 2026-05-20.
- **Audit directory:** `Reviews/results/2026-05-20_075227_pattern-audit/` (FAC-001/FAC-002/FAC-003).

## Initial Analysis

### The read-path gap (verified against live code, 2026-05-20)
`StrategySessionFacade` is a **write-path-only half-facade**:
- **Write path is guarded:** strategy commands route through `facade.handle_command()`, enforced by the AST/import static guard `tests/static_guards/test_facade_bypass_guard.py`.
- **Read path is unguarded:** UI code reads strategy domain objects directly. A repo search on 2026-05-20 found **93 files under `game/ui/`** importing `game.strategy` (`grep -rln "import game.strategy\|from game.strategy" game/ui/`). These pull data/engine types (`BuildQueueSource`, `FleetCapabilityCalculator`, `CarriedVehicle`, deployed-group dataclasses, `ContainableKind`, etc.) and read through the `StrategyScreen.session` property.

Without a read-path static guard, every new UI screen continues to reach past the facade and the boundary erodes silently.

### Why this is a migration, not a cleanup
- It is a **multi-PR architecture migration** with prior deferral history (PROJ-382 / U1–U3 work stream).
- A single-pass migration of 93 files would dominate (and balloon) any conformance pass. The correct shape is: **policy decision → read-path static guard → first migration slice → incremental migration under the guard**, exactly mirroring how the write-path guard was rolled out.
- The independent reviewer flagged that folding this into PROJ-470 conflated a localized conformance pass with a structural refactor; hence the extraction here.

### Densest sites (first-slice candidates)
- `game/ui/screens/build_queue_screen.py:23` — runtime import of `BuildQueueSource` / `collect_build_queues_at_hex`.
- `game/ui/panels/build_queue_controller.py:18-20` — `BuildContext` / `BuildQueueSource` under `TYPE_CHECKING` (type-only today; reconcile with policy).
- `game/ui/screens/fleet_data_source.py:242` — `FleetCapabilityCalculator` late-import.
- `game/ui/screens/strategy_screen.py:242-257` — public `session` property exposing `_session`; 4 consumers read domain objects directly (`strategy_detail_formatter.py`, `strategy_windows/list_windows.py`, `hex_outlines.py`).

## Key Patterns to Reuse
- **Pattern #5 (Facade / Delegate)** — `docs/02_PATTERNS.md:148`; the read-path policy extends this entry.
- **Write-path static guard** — `tests/static_guards/test_facade_bypass_guard.py`; the read-path guard mirrors its AST/import-scan structure and allowlist mechanism.
- **Facade slices/DTOs** — `game/strategy/facade/slices/`, `game/strategy/facade/dto/`; new read DTOs (if option (a) is chosen) live here.

## Dependencies & Risks
1. **Policy choice (a) read DTOs vs (b) documented UI-safe read surface** — option (a) adds DTO surface and conversion cost but gives a hard boundary; option (b) is lighter but relies on convention + guard allowlist. Decide in Phase 1 Task 1; record in Pattern #5.
2. **Allowlist correctness** — the guard must allowlist genuinely-UI-safe read types or it will block legitimate reads; too permissive and it fails to catch new bypasses. Mirror the write-path guard's allowlist discipline.
3. **Determinism/save-compat** — read-path migration must not alter serialized payloads. Any DTO conversion is read-only projection; no save format changes.

## Opportunities Discovered
- Once the read-path guard exists, the remaining ~85 sites can be migrated in mechanical batches per UI subpackage (panels, screens, widgets) under the guard, each batch a small PR.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
