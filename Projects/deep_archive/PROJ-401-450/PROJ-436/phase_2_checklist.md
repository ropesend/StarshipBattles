# Phase 2: `ShipInstance.bay_inventory` widening to full Container

**Status:** Not Started
**Depends on:** phase_1
**Review Mode:** standard
**Files (planned):** see `phase_state.json` phase_2.planned_files

**Objective:** Extend `BayInventory` (PROJ-431 substrate) from `{pods, vehicles}` to a full `Container` with three slices. Backward-compatible `pods` / `vehicles` accessors become views over `container.items`. Migrate fighter / satellite / mine launch and recovery handlers to source/sink items via `container.remove()` / `container.add()`. Launch / recovery / life support / resource generation / consumption stay separate per-component abilities — Container is storage only.

---

## Tasks

To be authored at phase start. Expected shape per PROJ-431 sub-phase template (1a, 1b, …): one commit per migration sub-batch, AST guard at each, full sharded suite at end.

Sub-phase outline (refine at phase start):
- 2a — extend `BayInventory` to wrap a `Container`; keep `pods` / `vehicles` accessors as views.
- 2b — migrate `LaunchFighters` + `RecoverFighters` order handlers.
- 2c — migrate `LaunchSatellites` + `RecoverSatellites` order handlers.
- 2d — migrate `LayMines` order handler + `MineGroupService`.
- 2e — sweep remaining `bay.pop()` / `bay.append()` direct accesses.
- 2f — AST guard that `BayInventory.bay` / `BayInventory.pods` are derived properties, not raw lists.

---

## Phase Completion Checklist
- [ ] All sub-phases complete
- [ ] PROJ-431 BayInventory tests still green
- [ ] FMS integration tests green
- [ ] Full sharded suite green
- [ ] Update status to Complete; update plan.md + phase_state.json
