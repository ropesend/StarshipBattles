# Phase 10: Doc refresh

**Status:** Complete
**Depends on:** phase_9
**Review Mode:** lightweight

**Objective:** Update documentation to reflect the unified Container
substrate. Touch only what this project changed; broader doc drift
from PROJ-422..435 stays out of scope (logged for a separate hygiene
pass if needed).

---

## What landed

Six docs updated (no production / test code changes):

- **`docs/systems/resource_system.md`** — rewrote the
  `ProductionEngine._check_affordability` description around the
  `IProductionResourceSource` Protocol (Phase 8); replaced the
  `TransferValidator.VALID_CARGO_TYPES` warning paragraph with the
  Phase 7 registry-driven contract; drop-pod section now describes
  the typed `DropPod` dataclass shape and notes Phase 9's deletion
  of the `_CarriedItemsProxy` shim; "Add a transferable resource"
  recipe simplified (no validator update needed for new resources).
  `Last verified` stamp refreshed.
- **`docs/systems/production_system.md`** — `Resource Sources`
  section rewritten around the unified Protocol (Phase 8 cutover);
  `BuildQueueSource(context_type: ...)` annotated as "UI entity
  routing only" to distinguish from the deleted engine-side dispatch;
  staging-yard line updated to describe typed `DropPod`; "Adding a
  new build context" recipe updated to require
  `IProductionResourceSource` implementation on the new entity.
- **`docs/systems/strategy_layer.md`** — minefield-resolver
  indirection note updated to point at `ship.bay_inventory.bay`
  with explicit deletion-history mention of the `carried_items` shim.
- **`docs/systems/satellites.md`** — lifecycle map ASCII art
  updated to point at `ShipInstance.bay_inventory.bay[*]` (the typed
  slot) with a parenthetical noting Phase 9's deletion.
- **`docs/02_PATTERNS.md`** — updated Pattern #38 (CarriedVehicle
  Substrate) to describe the four-slot `BayInventory`; updated
  Pattern #41 (Polymorphic Order Issuer) to point at the typed
  `bay_inventory.bay` slot; **added Pattern #43 (Unified Container
  Substrate)** — ~60 lines covering `Container` + `ContainerPolicy` +
  `ContainableKind` + `BayInventory.four_slot` +
  `IProductionResourceSource`, with usage guidance + a boundary note
  about launch/recovery/life-support/production staying separate
  abilities. Pattern #43 has its own per-pattern `Last verified` line.
- **`docs/01_ARCHITECTURE.md`** — extended the `game/strategy/data/`
  listing's bold note to include the Container substrate sentence
  (Container + ContainerPolicy + BayInventory four-slot +
  `Empire.resource_pool` pure-aggregation +
  `IProductionResourceSource` Protocol seam).

## What was NOT done (intentional)

- Did not edit `docs/03_CONVENTIONS.md` / `04_SERVICES.md` /
  `05_ERROR_HANDLING.md` / `06_UI_STYLE_GUIDE.md` — quick greps
  returned no PROJ-436-symbol hits in those files.
- Did not delete the deletion-history mentions (`"_CarriedItemsProxy
  deleted in Phase 9"`, `"VALID_CARGO_TYPES deletion (Phase 7)"`,
  etc.) — those are intentional history markers per the doc
  convention.
- Did not touch any test or production code; this phase is doc-only.
- Did not refresh `Last verified` blockquotes on docs Phase 10 did
  not touch.

## Phase Completion Checklist

- [x] All touched docs reflect the unified Container substrate
- [x] Doc-sync grep checks pass: `rg "VALID_CARGO_TYPES" docs/` returns only deletion-history mentions; `rg "_CarriedItemsProxy" docs/` same; `rg "getattr.*context_type|colony_or_fleet.*context_type" docs/` zero; `rg "\.carried_items\b" docs/` only deletion-history mentions and Last verified blockquotes
- [x] `> **Last verified:**` blockquote stamps refreshed on the 6 touched docs (Pattern #43 also carries its own per-pattern stamp)
- [x] Sharded suite still green (23209/23211 — doc-only changes are no-op for tests)
- [x] Codex pre-final-check consult complete — see `AgentCoordination/Scratchpad/Consult/20260518T143802Z_proj436-phase10-doc-refresh/`
- [x] Update status to Complete; update plan.md + phase_state.json
