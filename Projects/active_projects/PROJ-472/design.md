# PROJ-472: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source
- **Origin:** Deferred scope extracted from PROJ-470 (pattern-conformance cleanup)
  under Protocol 06 / Protocol 07 after a dual independent+Codex review on 2026-05-20.
- **Audit directory:** `Reviews/results/2026-05-20_075227_pattern-audit/` (FAC-001/FAC-002/FAC-003).
- **Pre-flesh consult (authoritative input, citations re-verified against live
  code 2026-05-21):** `AgentCoordination/Scratchpad/Consult/proj472_preflesh/advice.md`.

## The read-path gap (the half-facade)

`StrategySessionFacade` is a **write-path-only half-facade**:

- **Write path is guarded.** Strategy commands route through
  `facade.handle_command()` or the grouped `facade.commands.<verb>()` namespace,
  enforced by the AST/import static guard
  `tests/static_guards/test_facade_bypass_guard.py`.
- **Read path is unguarded.** UI code reads strategy domain objects directly.
  A live search on 2026-05-21 found **93 files under `game/ui/`** importing
  `game.strategy` (`rg -l "import game\.strategy|from game\.strategy" game/ui -g '*.py'`).
  They pull data/engine types (`BuildQueueSource`, `collect_build_queues_at_hex`,
  `FleetCapabilityCalculator`, deployed-group dataclasses, `ContainableKind`, …)
  and read through `StrategyScreen.session` / `facade_state.session`.

Without a read-path static guard, every new UI screen continues to reach past
the facade and the boundary erodes silently.

The facade is *already* a real read boundary for several session-shaped queries:
it exposes grouped read namespaces, not just commands
(`strategy_session_facade.py:132-198`). Those namespaces already cover empire
build-queue queries, session registries, turn number, colony demographic views,
and colonization validation (`grouped_namespaces.py:232-264`, `:302-337`,
`:344-393`). The build-queue path already proves the facade can project useful
read DTOs: `EmpireSlice.get_empire_build_queues()` / `get_hex_build_queues()`
collect domain `BuildQueueSource` objects and convert to `BuildQueueSourceDTO`
(`empire_slice.py:68-97`), and the DTO deep-copies queue items to prevent UI
mutation (`build_queue_dto.py:24-41`).

## Why option (b), not a blanket DTO layer

Orchestrator decision (confirmed with user): **policy = option (b)** — a
documented UI-safe read surface enforced by static guard + exact allowlist +
convention; NOT a blanket "all UI reads become facade DTOs" layer.

A blanket DTO layer does not fit the codebase cleanly because many of the 93
imports are **not live-session reads**:

- Race setup/editor UI edits a standalone `RaceConfig` + registry-driven factor
  definitions before any session exists (`game/ui/panels/race_environment_panel.py:25-35`,
  `game/ui/widgets/preference_row.py:37-40`).
- New-game setup constructs a `GameConfig` before any `GameSession` exists
  (`game/ui/screens/new_game_setup_controller.py:39-44`).
- Transfer UI only needs `ContainableKind` tags while reading facade-provided
  container snapshots (`game/ui/screens/transfer_view_model.py:243-255`).
- Planet-ability UI uses `ActivationPhase` only as a status enum over
  already-resolved facility state (`game/ui/screens/planet_abilities_controller.py:30-34`).

There is no "cannot ever be projected" case, but several reads are **poor Phase 1
DTO targets** because they are render-hot, identity-sensitive, or pre-session
configuration surfaces. Hence option (b).

**Practical policy shape (to record in Pattern #5):**
- Use the facade for **session-owned, mutation-adjacent, or cross-screen-cached**
  reads.
- Allow a documented UI-safe surface for **immutable-ish config/value/enums/
  protocols** (`GameConfig`, `RaceConfig`, `EnvironmentalPreference`,
  `HabitabilityFactor`, `ContainableKind`, `ActivationPhase`) and a short,
  explicitly-blessed list of pure query helpers.
- Do **not** allowlist live session/domain traversal helpers just because they
  are "read-only". `BuildQueueSource` and `collect_build_queues_at_hex` are the
  counterexample: they return mutable owner references and live queue lists
  (`game/strategy/data/build_queue_source.py`).

## The two-guard design (mirror the write-path guard structurally)

Mirror `tests/static_guards/test_facade_bypass_guard.py`: AST walk over every
`game/ui/**/*.py`, helper functions, explicit allowlists, and positive-control
tests (`:53-60`, `:69-103`, `:105-155`, `:208-238`). Split into **two** guards:

### Guard 1 — `test_facade_read_path_imports_guard.py`
Runtime-import guard.
- Parse `Import` / `ImportFrom`.
- **Ignore imports under `if TYPE_CHECKING:`** — this avoids false positives like
  `build_queue_controller.py:18-20`, where the strategy imports are type-only.
- Fail only on **runtime** imports from `game.strategy.*` that are not on an
  **exact module/member allowlist** (not broad subpackage wildcards — the
  codebase is too mixed for `game.strategy.data.*` to be safe).
- Always allow `game.strategy.facade.*` and `game.strategy.engine.commands`
  (the intended write path).
- **Counts as a bypass:** runtime import of live domain/session surfaces or live
  query helpers, e.g. `build_queue_source.BuildQueueSource`,
  `build_queue_source.collect_build_queues_at_hex`,
  `fleet_capability_calculator.FleetCapabilityCalculator`, any direct import of
  `GameSession`, mutators, or `turn_engine`-shaped helpers.
- **Counts as UI-safe:** the pre-session config/value/enum surfaces above.
- Positive controls so a future matcher regression cannot silently narrow the guard.

### Guard 2 — `test_facade_read_path_session_guard.py`
Session-read guard.
- AST-match `<expr>.session.<attr>`, `<expr>._session.<attr>`, AND
  `<expr>.facade_state.session.<attr>` reads. The third form is mandatory —
  otherwise the guard misses already-live bypasses like
  `strategy_build_queue_manager.py:82-83` even if `.scene.session` consumers are
  migrated.
- Allowlist by **file + attribute-path + reason**, not just attribute name.
  Documented transitional exceptions:
  - `strategy_screen.py` composition-root property implementations
    (`:160-189` pass-throughs, `:242-276` the `session` property/setter).
  - `strategy_game_state_manager.py` writing `session.active_empire` (write seam).
  - Any temporary mutator seam intentionally left for a follow-on migration.
- Positive controls + `TYPE_CHECKING` exemption + comment/docstring exemption
  (AST handles the latter for free).

**Guard strictness = pragmatic** (orchestrator decision). The guard covers all
of `game/ui/`, but the pre-session config/value/enum types AND the StrategyScreen
pass-through properties are **allowlisted-with-reason as documented TRANSITIONAL
read surfaces**. The plan honestly states the read path is not fully closed in
Phase 1; deprecating the pass-throughs is PROJ-475.

## The build-queue DTO gap (drives Phase 1B shape)

`BuildQueueSourceDTO` currently carries `queue_id, display_name, entity_id,
construction_queue, can_build_ships, can_build_complexes, context_type,
build_rate, planet_id, empire_id` (`build_queue_dto.py:6-42`). It does **NOT**
carry `owner_entity` or `is_paused`, but callers need both:

- `build_queue_input_router.py:128`, `:164` read `source.owner_entity`.
- `build_queue_input_router.py:174` reads `source.is_paused`.
- `empire_build_queue_window.py:365`, `:425` read `source.owner_entity`.

**Decision (orchestrator):** enrich `BuildQueueSourceDTO` **once** with the
caller-needed projected fields (`is_paused`, plus the `owner_entity`-derived
identity/flags the callers actually consume — `entity_id`/`empire_id` already
exist; add `is_paused` and any missing owner-derived display fields) rather than
leaving domain `BuildQueueSource` and DTOs mixed in the same feature. Do **not**
expose the live `owner_entity` reference on the DTO (that would re-leak the
mutable domain object the DTO exists to hide); project the specific scalar
fields the callers use. If a caller genuinely needs behavior that cannot be a
scalar projection, add one small facade-fed UI adapter — but do not finish 1B
with both representations live in the cluster.

## Render-hot-path caution

Some reads sit on render/cache hot paths and must not gain heavy per-frame
projections just to satisfy purity:
- `HexOutlineLayer.build_data` iterates `r.galaxy.state.*`, `r.empires`, active
  empire on each turn-cache rebuild (`hex_outlines.py:24-80`). Phase 1C migrates
  only the `r.scene.session.active_empire` read to a facade/scene accessor; it
  must keep the existing turn-keyed cache and must NOT introduce per-frame DTO
  allocation.
- `draw_fleet_path` pulls path projections while rendering (`strategy_render/fleets.py`).
- The `FacadeSessionState` cache holder is a **kept-by-design performance
  boundary**, pinned by
  `tests/unit/strategy/engine/test_game_session_projection_boundary.py`
  (`_facade_state.py:48-60`). Do not remove/inline it.

## Determinism / save-compat
Migration is **projection-only**. No serialized payload, no domain-persistence,
no save-format changes. The existing DTO pattern is safe precisely because it
copies read data without changing owner objects (`build_queue_dto.py:24-41`).
Old saves are disposable per project rules, but nothing here should require that.

## Citation corrections (consult verified against live code, 2026-05-21)
- **93-file count:** still live (confirmed by `rg`).
- **`build_queue_controller.py:18-20`:** TYPE_CHECKING-**only**; stale if treated
  as a runtime bypass. The real coupling is the class's dependence on live
  `BuildQueueSource` objects (`:66-79`, `:117-150`, `:421-522`). The runtime-import
  guard MUST exempt `TYPE_CHECKING` so this is not churned pointlessly.
- **`hex_outlines.py` path:** the live file is
  `game/ui/screens/strategy_render/hex_outlines.py` (NOT `game/ui/screens/`),
  active-empire read at `:30`, turn read at `:76-79`.
- **FAC-003 consumer list was incomplete:** add
  `strategy_detail_formatter.py:278` (extra `.session.registries` read),
  `list_windows.py:70` (`.session.registries` alongside `:69` `.session.empires`),
  and the `facade_state.session` bypass at `strategy_build_queue_manager.py:82-83`.
- **DTO gaps confirmed:** `BuildQueueSourceDTO` lacks `owner_entity` and
  `is_paused` that callers use (see DTO-gap section).
- **Incomplete leak model:** `StrategyScreen` still exposes raw session
  pass-through properties (`strategy_screen.py:160-189`) and `FacadeSessionState`
  publicly holds `session` (`_facade_state.py:63-86`) — both remain after Phase 1
  (documented transitional surfaces; deprecation is PROJ-475).

## First slice = the build-queue read surface as a feature CLUSTER
Not just `build_queue_screen.py`. `BuildQueueSource` / collectors are referenced
across ~13 UI files (verified: `build_queue_controller`, `build_queue_selector`,
`build_queue_panel_factory`, `build_queue_screen`, `build_queue_renderer`,
`build_queue_input_router`, `build_queue_viewmodel`, `empire_build_queue_data_source`,
`empire_build_queue_formatter`, `empire_build_queue_filter_manager`,
`empire_build_queue_window`, `empire_build_queue_viewmodel`,
`strategy_build_queue_manager`). The facade already has the queries
(`empires.build_queues` / `hex_build_queues`) — the missing piece is DTO richness,
which is exactly why this is the right first cluster.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
