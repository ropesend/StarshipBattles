# PROJ-461 Consolidated Findings

> Spinout from PROJ-459 Phase 3 (2026-05-19).
>
> Source: `Projects/archived_projects/PROJ-444/findings/bucket_a_data_facade_scan.md` (F-A-007 original entry, carried verbatim).

---

## F-A-007 — `ship_instance.py` over the 500-LOC ceiling

- **Severity**: medium
- **Category**: structure / LOC
- **File**: `game/strategy/data/ship_instance.py` (789 LOC post-PROJ-449 + PROJ-454; was 839 LOC pre-PROJ-449)
- **What survived PROJ-449**: read-only `@property` views for `consumable_levels` / `cargo_contents` (deliberate; the substrate-widening seam was closing the setter halves only). The 5 TD-06 "high-value shim" entry points remain: serializer family (`to_dict`/`from_dict`/`to_json`/`from_json`/`clone`), bridge family (`to_ship`/`update_from_ship`), resource-manager facades (`consume_resource`/`get_resource_capacity`/`get_current_resource`/`get_all_resource_costs_per_*`/`get_warp_resource_costs`/`resupply`), and write-service facades (`set_component_enabled`/`repair`). Each shim is 5-10 LOC × ~10 shims = ~80-100 LOC just in shim bodies; the class docstring catalog adds another ~25 LOC.
- **Why it's a problem**: the 500-LOC ceiling (per `docs/03_CONVENTIONS.md`) is the project's working invariant; one file +289 over is a chronic exception that should be retired.
- **Suggested action**: enumerate the 5 high-value shim clusters, count callers per cluster, plan a migration sweep that moves callers to the underlying manager APIs (`ship._cargo_mgr.*`, `ship._resource_mgr.*`, `ShipInstanceBridge.*`, `ShipInstanceSerializer.*`). Each shim retirement requires its own caller audit + mechanical caller sweep. Total caller count was estimated at ~910 in PROJ-425 Phase 5d/5e analysis.
- **Effort**: large (multi-phase per-shim sweep). Per Codex r4: "if it still sits at 750+ LOC after PROJ-449, spin it as its own next-touch project."
- **Status as of 2026-05-19**: **Open. Project spun out from PROJ-459 Phase 3 verdict.** PROJ-459 carries only the measurement-decision narrative; PROJ-461 owns the actual reduction work.
- **Cross-references**:
  - PROJ-449 wrapper retirement (LANDED at SHA `ebb5c0e7f`).
  - PROJ-454 component_inspector retirement (LANDED at SHA `ab2da0669`).
  - PROJ-425 Phase 5d/5e — original TD-06 catalog and 910-caller estimate.
  - Class docstring at `ship_instance.py:106-125` — the catalog of retained shims is the canonical inventory.

---
