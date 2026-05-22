# PROJ-472 File Manifest

> Generated during planning. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.
> Files are grouped per phase so phases can be sequenced/parallel-checked.

## Phase 1A — Policy + two guards

| File | Type | Notes |
|------|------|-------|
| `docs/02_PATTERNS.md` | Doc | Pattern #5: record the read-path policy (option b: UI-safe surface + guard + allowlist + convention); name the UI-safe config/value/enum types and the transitional pass-throughs |
| `tests/static_guards/test_facade_read_path_imports_guard.py` | Test (new) | Runtime-import guard; ignores `TYPE_CHECKING`; exact allowlist; positive controls |
| `tests/static_guards/test_facade_read_path_session_guard.py` | Test (new) | Session-read guard: `.session.<attr>` / `._session.<attr>` / `.facade_state.session.<attr>`; file+path+reason allowlist; positive controls |
| `tests/static_guards/test_facade_bypass_guard.py` | Test (read-only) | Existing write-path guard; structural template — DO NOT edit |

**Conflicts:** Pattern #5 doc edit must not collide with PROJ-470 (closed) or any
concurrent docs change — check `git status --short` first. Guards are net-new files.

## Phase 1B — Build-queue cluster migration

| File | Type | Notes |
|------|------|-------|
| `game/strategy/facade/dto/build_queue_dto.py` | Production | One-time enrichment: add `is_paused: bool` + `owner_global_hex: HexCoord \| None` + `owner_system_name: str \| None` (resolved scalars); do NOT expose live `owner_entity` |
| `game/strategy/facade/slices/empire_slice.py` | Production | Resolve `owner_global_hex` / `owner_system_name` via galaxy (`self._state.session.galaxy`) at projection time in the collectors (`:68-97`); pass resolved scalars into `BuildQueueSourceDTO.from_domain` (DTO has no galaxy access) |
| `game/ui/screens/build_queue_screen.py` | Production | Replace runtime `BuildQueueSource`/`collect_build_queues_at_hex` import (`:23`) + calls (`:214-217`,`:333-336`) with `facade.empires.hex_build_queues(...)` |
| `game/ui/panels/build_queue_controller.py` | Production | Reconcile TYPE_CHECKING imports (`:18-20`); migrate live-BQS coupling (`:66-79`,`:117-150`,`:421-522`) to DTO |
| `game/ui/screens/build_queue_input_router.py` | Production | `owner_entity`/`is_paused`/`construction_queue` consumers (`:83-84`,`:128`,`:164`,`:174`) → DTO fields |
| `game/ui/screens/build_queue_selector.py` | Production | type/behavior consumer |
| `game/ui/screens/build_queue_panel_factory.py` | Production | cluster consumer |
| `game/ui/screens/build_queue_renderer.py` | Production | cluster consumer |
| `game/ui/screens/build_queue_viewmodel.py` | Production | type/behavior consumer |
| `game/ui/screens/empire_build_queue_data_source.py` | Production | cluster consumer |
| `game/ui/screens/empire_build_queue_formatter.py` | Production | cluster consumer |
| `game/ui/screens/empire_build_queue_filter_manager.py` | Production | cluster consumer |
| `game/ui/screens/empire_build_queue_window.py` | Production | `owner_entity`/`construction_queue` (`:365`,`:422`,`:425`) → DTO fields |
| `game/ui/screens/empire_build_queue_viewmodel.py` | Production | cluster consumer |
| `game/ui/screens/fleet_data_source.py` | Allowlist-only | `FleetCapabilityCalculator` late-import (`:241-245`) — DEFERRED, stays import-guard allowlisted-with-reason (no facade query exists; 1B.4) |
| `game/ui/screens/fleet_report_filters.py` | Allowlist-only | Two more identical `FleetCapabilityCalculator` late-imports (`:163`, `:302`) — DEFERRED, stays import-guard allowlisted-with-reason (1B.4) |

**Conflicts:** `empire_slice.py` and `build_queue_dto.py` are facade-internal —
1B owns them; no other phase touches them. The 13 UI files are 1B-exclusive.
`fleet_data_source.py` / `fleet_report_filters.py` are NOT migrated — their three
`FleetCapabilityCalculator` late-imports stay allowlisted-with-reason (deferred;
recorded in PROJ-475). The Phase 1A import guard (advisory-then-enforcing) gates
this batch.

## Phase 1C — StrategyScreen.session read-consumer cleanup

| File | Type | Notes |
|------|------|-------|
| `game/ui/screens/strategy_screen.py` | Production | Add facade-fed scene accessors (registries / active_empire / turn / empires) so consumers stop reading `.session.<x>`; pass-through properties (`:160-189`) stay as documented transitional surfaces |
| `game/ui/screens/strategy_detail_formatter.py` | Production | `.session.registries` (`:112`,`:278`) + `.session.turn_engine` (`:395-396`) → facade accessors |
| `game/ui/screens/strategy_windows/list_windows.py` | Production | `.session.empires` (`:69`) + `.session.registries` (`:70`) → facade accessors |
| `game/ui/screens/strategy_render/hex_outlines.py` | Production | `r.scene.session.active_empire` (`:30`) → scene/facade accessor; KEEP turn-keyed cache; no per-frame DTO alloc |
| `game/ui/screens/strategy_build_queue_manager.py` | Production | `facade_state.session.services...` bypass (`:82-84`) → facade accessor |
| `game/ui/screens/strategy_render/fleets.py` | Production | `r.scene.session.get_fleet_path_projection(fleet, ...)` (`:85`) → `facade.fleets.path_projection(fleet.id, max_turns=50)` (render-hot, one-for-one List[dict] swap; 1C.6) |

**Conflicts:** `strategy_screen.py` is the composition root touched only in 1C
(adds accessors). `strategy_build_queue_manager.py` overlaps the build-queue
*feature* but its leak is a session-read (1C), not a BQS import (1B) — sequence
1B before 1C so the file's BQS usage is already DTO-based when 1C touches the
session read. `strategy_detail_formatter.py` appeared in the BQS grep but its
strategy coupling is session reads, handled here, not in 1B.

**Deferred-to-PROJ-475 session readers (allowlisted-with-reason, NOT migrated in
1C — see 1C.7):** `strategy_event_router.py:223/368` (`scene.session.get_empire`),
`strategy_screen_selection.py:93` + `strategy_screen_order_editing.py:42`
(`session.active_empire` gates), `empire_panel_ctrl.py:62`
(`session.registries` DI). Mutator WRITE seams that also stay allowlisted:
`strategy_game_state_manager.py:164`, `strategy_screen_order_editing.py:66/92`.

## Out-of-scope (deferred — NOT in PROJ-472's manifest)
The remaining ~75 `game/ui/` files: PROJ-474 (value/config allowlist),
PROJ-475 (remaining live screen/render readers + pass-through deprecation +
the explicitly-deferred 1C session readers + the `FleetCapabilityCalculator`
late-import allowlist tail), PROJ-476 (battle_setup / galaxy_test / race_setup /
builder tooling). NOTE: `strategy_render/fleets.py`'s path-projection read is
migrated IN 1C (1C.6) — only its OTHER readers (if any) remain PROJ-475's.
