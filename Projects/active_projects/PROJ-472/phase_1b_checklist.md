# Phase 1B: Build-queue cluster migration onto facade queries

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-472 1b`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Migrate the ~13-file build-queue UI cluster off domain
`BuildQueueSource` / `collect_build_queues_at_hex` onto the facade queries
`empires.build_queues` / `empires.hex_build_queues`. Enrich `BuildQueueSourceDTO`
ONCE so callers no longer need the domain object; do NOT finish the phase with
domain `BuildQueueSource` and DTOs both live in the cluster. Then remove the
TEMPORARY import-guard allowlist entries for these files so the guard enforces
them.

**Gate:** Phase 1A guards must be landed. **Sequence:** 1B before 1C (so
`strategy_build_queue_manager.py`'s BQS usage is DTO-based before 1C touches its
session read).

---

## Tasks

### Task 1B.1: Enrich BuildQueueSourceDTO (TDD) [Complex]
**File:** `game/strategy/facade/dto/build_queue_dto.py`, `game/strategy/facade/slices/empire_slice.py`
**Tests:** `pytest tests/unit/strategy/facade/ -k build_queue` (add a failing DTO test first)

- [x] Write a FAILING unit test asserting `BuildQueueSourceDTO.from_domain(...)`
      exposes `is_paused` and the owner-derived SCALAR fields named below — confirm
      it fails (fields absent on the current DTO, `build_queue_dto.py:13-22`)
- [x] Add `is_paused: bool` to the frozen DTO and populate it in `from_domain`
      from `source.is_paused`
- [x] Add the **exact** owner-derived SCALAR fields below. Do NOT add a live
      `owner_entity` reference — that re-leaks the mutable domain object the DTO
      exists to hide. `entity_id` / `empire_id` / `planet_id` / `context_type`
      already exist (`build_queue_dto.py:15,19,21-22`). New fields required by the
      verified caller reads (see Task 1B.3 below):
      - `owner_global_hex: HexCoord | None` — the resolved GLOBAL hex of the
        owner. For a **fleet** source this is `owner_entity.location` directly;
        for a **planet** source it is `system.global_location + owner_entity.location`
        where `system = galaxy.get_system_of_planet(owner_entity)` (None if no
        galaxy / no system). This replaces `empire_build_queue_window.get_hex_for_source`
        (`:363-374`) and the `get_sector_text` hex read
        (`empire_build_queue_formatter.py:104-113`).
      - `owner_system_name: str | None` — the resolved system NAME of the owner.
        For a fleet: `galaxy.get_system_at_hex(owner_entity.location).name`; for a
        planet: `galaxy.get_system_of_planet(owner_entity).name` (None if
        unresolved). This replaces `get_system_name`
        (`empire_build_queue_formatter.py:79-92`).
      - These are resolved at projection time in the empire slice (which already
        holds galaxy access via `self._state.session.galaxy`, see
        `empire_slice.py:91-96`), NOT in the frozen DTO — `from_domain` cannot
        reach the galaxy. Pass the resolved scalars (or the galaxy) into
        `from_domain`, OR resolve them in the slice and set them on the DTO. Pick
        one in the failing test and pin it.
- [x] Confirm the DTO stays `frozen=True` and keeps deep-copying
      `construction_queue` (`:34`) so no UI mutation of domain state is possible.
      `owner_global_hex` (HexCoord) and `owner_system_name` (str) are immutable
      value types — safe to hold directly.
- [x] Verify the new test passes; existing facade DTO tests stay green

### Task 1B.2: Migrate per-hex + empire-wide build-queue entry screens [Complex]
**File:** `game/ui/screens/build_queue_screen.py`, `game/ui/screens/empire_build_queue_window.py`
**Tests:** `pytest tests/ --testmon` + `pytest tests/static_guards/test_facade_read_path_imports_guard.py`

- [x] Remove the runtime import `from game.strategy.data.build_queue_source import
      BuildQueueSource, collect_build_queues_at_hex` (`build_queue_screen.py:23`)
- [x] Replace `collect_build_queues_at_hex(...)` calls (`:214-217`, `:333-336`)
      with `facade.empires.hex_build_queues(empire_id, hex_coord)` returning
      `BuildQueueSourceDTO`
- [x] Migrate `empire_build_queue_window.py` `owner_entity` reads to the enriched
      DTO fields. Verified live 2026-05-21:
      - `get_hex_for_source` (`:363-374`) reads `source.owner_entity` then resolves
        fleet `entity.location` / planet `system.global_location + entity.location`
        → replace with the DTO's `owner_global_hex` scalar (resolution moves into
        the slice projection per 1B.1). The method becomes `return source.owner_global_hex`.
      - `_add_item_to_source` (`:413-438`, the `:425-436` cited site) uses
        `owner_entity` only to derive `entity_type` (PLANET vs FLEET) and
        `entity_id` for `AddToConstructionQueueCommand`. Both are already on the
        DTO: `context_type` ("planet"/"fleet") gives the entity type and
        `entity_id` gives the id — use those, do NOT re-fetch the live entity.
        (`:422` is a docstring reference to `source.construction_queue`, no code change.)
- [x] Remove these files' TEMPORARY allowlist entries from the 1A import guard
- [x] Verify the import guard now passes WITHOUT those allowlist entries

### Task 1B.3: Migrate the supporting cluster files [Complex]
**File:** `build_queue_controller.py`, `build_queue_input_router.py`, `build_queue_selector.py`, `build_queue_panel_factory.py`, `build_queue_renderer.py`, `build_queue_viewmodel.py`, `empire_build_queue_data_source.py`, `empire_build_queue_formatter.py`, `empire_build_queue_filter_manager.py`, `empire_build_queue_viewmodel.py`, `strategy_build_queue_manager.py` (BQS usage only)
**Tests:** `pytest tests/ --testmon` + the 1A import guard

- [x] `build_queue_controller.py`: migrate the live-`BuildQueueSource` class
      coupling (`:66-79`,`:117-150`,`:421-522`) to the DTO; the TYPE_CHECKING
      imports (`:18-20`) become unnecessary once the class consumes DTOs — remove them
- [x] `build_queue_input_router.py`: `source.owner_entity` (`:128`,`:164`),
      `source.is_paused` (`:174`), `source.construction_queue` (`:83-84`) → DTO fields
- [x] `empire_build_queue_formatter.py`: migrate the `owner_entity`-derived
      location/system reads (verified live 2026-05-21):
      - `get_system_name` (`:79-92`) → DTO `owner_system_name` (replaces both the
        planet `galaxy.get_system_of_planet(entity).name` and fleet
        `galaxy.get_system_at_hex(entity.location).name` branches; return
        `source.owner_system_name or "-"`).
      - `get_sector_text` (`:95-114`) → DTO `owner_global_hex` (replaces both the
        fleet and planet `entity.location` reads; return
        `str(source.owner_global_hex) if source.owner_global_hex is not None else "-"`).
      - The `galaxy` parameter these helpers take becomes unused once resolution
        moves into the slice — drop it from the signatures and callers.
- [x] Migrate the remaining viewmodels/data-sources/selector/factory/
      renderer to consume `BuildQueueSourceDTO` instead of domain `BuildQueueSource`
- [x] `strategy_build_queue_manager.py`: migrate ONLY its BQS-import usage here;
      its `facade_state.session` read (`:82-84`) is a 1C task — leave that for 1C.
      Specifically the fleet closeout path (verified live 2026-05-21):
      - `_on_build_queue_close` (`:226-235`) iterates `queue_sources`, and for
        `context_type == 'fleet'` reads `source.owner_entity` (`:231`) to get a
        live `Fleet`, then passes it to `_handle_fleet_build_queue_close`. Replace
        the live-entity grab with the DTO `entity_id` (= fleet id) + the facade
        fleet query below; iterate over fleet ids, not live fleets.
      - `_handle_fleet_build_queue_close` (`:253-276`) inspects BUILD-order state
        on the live fleet: `fleet.construction_queue` (`:263`) and
        `fleet.orders` / `order.type == OrderType.BUILD` (`:265-268`). Replace the
        `Fleet` parameter with `fleet_id: int` and read the state from
        `facade.fleets.get(fleet_id)` → `FleetInfo`. The required state is on the
        DTO (verified `fleet_dto.py:67-73`, populated `:221-227`):
        `construction_queue_size > 0` replaces `if fleet.construction_queue:`, and
        `any(o.type == OrderType.BUILD for o in info.orders)` replaces the live
        `fleet.orders` scan (`FleetInfo.orders` is a tuple of `FleetOrderInfo`).
        It still issues `IssueBuildOrderCommand(fleet_id=...)` /
        `RemoveBuildOrderCommand(fleet_id=...)` (already id-based, `:271`,`:275`) —
        no live fleet needed. Do NOT introduce a new live-fleet leak; use the
        existing `facade.fleets.get(...)` (`fleet_slice.py:60-65`).
      - `on_navigate_to_hex_build` (`:278-312`) still receives the live `entity`
        via the `source` callback arg from the empire window's
        `navigate_to_source`; that navigation/asset path is out of the BQS-DTO
        migration's read scope and is NOT part of 1B (it consumes the callback's
        `source`, not the queue-list DTO). Leave it unchanged in 1B; if it needs
        the DTO it is a follow-on.
- [x] Remove each migrated file's TEMPORARY 1A import-guard allowlist entry
- [x] Verify NO file in the cluster still imports domain `BuildQueueSource` /
      `collect_build_queues_at_hex` / `collect_all_build_queues_for_empire`
      (`rg` the cluster); guard passes without their allowlist entries

### Task 1B.4: FleetCapabilityCalculator late-imports — DEFER to import-guard allowlist [Simple]
**File:** `game/ui/screens/fleet_data_source.py`, `game/ui/screens/fleet_report_filters.py`
**Tests:** the 1A import guard

Decision (post-flesh Codex review Blocker 2; verified live 2026-05-21): there are
THREE identical `INTENTIONAL LATE IMPORT` sites of
`FleetCapabilityCalculator.ship_has_spaceyard(ship)`, not one:
- `fleet_data_source.py:241-245` (`_format_spaceyard`)
- `fleet_report_filters.py:163` (`_should_exclude_by_spaceyard`)
- `fleet_report_filters.py:302` (spaceyard sort key)

These are pure per-`ShipInstance` capability checks (static method, no session
state). There is **no existing facade query** for a per-ship spaceyard check, and
adding one is out of the build-queue cluster's scope. Migrating them piecemeal in
a build-queue phase has low boundary value. Therefore:

- [x] Do NOT migrate these in 1B. Keep them as `FleetCapabilityCalculator`
      late-imports.
- [x] Add/keep BOTH files on the 1A import-guard allowlist as
      **allowlisted-with-reason** (exact file + module/member:
      `game.strategy.data.fleet_capability_calculator.FleetCapabilityCalculator`),
      reason: "pure per-ship capability check; no facade query yet; deferred".
- [x] Record the deferral in PROJ-475's plan (remaining live-reader tail) so the
      allowlist entry has a documented owner. Confirm the import guard passes
      WITH these two entries present (not removed).

### Task 1B.5: Phase 1B verification [Medium]
**File:** n/a
**Tests:** `pytest tests/static_guards/ && pytest tests/ --testmon`

- [x] `pytest tests/ --testmon` green for touched files
- [x] Import guard passes with the build-queue CLUSTER allowlist entries REMOVED
      (boundary now enforced for those files). EXCEPTION: `fleet_data_source.py`
      and `fleet_report_filters.py` `FleetCapabilityCalculator` entries STAY
      allowlisted-with-reason per 1B.4 (deferred), NOT removed.
- [x] No domain `BuildQueueSource`/collectors remain in the cluster; no mixed
      domain+DTO representation left in the feature
- [x] Caller read-set fully satisfied by the enriched DTO. Verified against the
      ~13-caller set the review enumerated (2026-05-21):
      `queue_id`, `display_name`, `entity_id` (← `owner_entity.id`),
      `construction_queue`, `can_build_ships`, `can_build_complexes`,
      `context_type`, `build_rate`, `planet_id`, `empire_id` already exist;
      `is_paused`, `owner_global_hex`, `owner_system_name` added in 1B.1. NO
      caller is left needing a live `owner_entity` — the only `owner_entity` reads
      were id/type derivation (→ `entity_id`/`context_type`), location/system
      (→ `owner_global_hex`/`owner_system_name`), and the navigation-callback path
      in `on_navigate_to_hex_build` which is explicitly out of 1B scope (1B.3).
      If implementation finds any caller still unsatisfied, STOP and pin the field
      before exposing a live object.
- [x] Determinism/save-compat unchanged (projection-only; no serialized changes)

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row 1B to `Complete`
- [x] Update plan.md Current State to point to Phase 1C

_Consult §3 (first slice = cluster), §4, and DTO-gap risk; verified 2026-05-21.
Post-flesh Codex review Blocker 2: named the exact owner-derived replacement
fields (`owner_global_hex`, `owner_system_name`) for
`empire_build_queue_formatter.py:79-114` + `empire_build_queue_window.py:365-436`;
pinned the fleet-state read path (`facade.fleets.get(fleet_id)` → `FleetInfo`) for
`strategy_build_queue_manager.py:226-276`; resolved the three
`FleetCapabilityCalculator` late-imports as deferred-to-allowlist (1B.4)._
