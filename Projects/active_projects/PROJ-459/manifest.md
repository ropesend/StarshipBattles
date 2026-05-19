# PROJ-459 File Manifest

Generated 2026-05-19 during charter creation. Sourced from Codex r4 redesign Job 11 plus the archived `Projects/archived_projects/PROJ-444/findings/bucket_a_data_facade_scan.md` (F-A-007, F-A-008, F-A-009).

## Files by phase

### Phase 0 — Re-measurement (no production touches)

| File | Type | Notes |
|------|------|-------|
| `Projects/active_projects/PROJ-459/findings/phase_0_remeasurement.md` | Findings (new) | Snapshot LOC table for fleet.py / planet_gen.py / ship_instance.py at PROJ-449 + PROJ-451 merge HEAD. Confirms PROJ-449/451 status. Verifies extraction-target locations. Phase 3 verdict pending or final. |
| `game/strategy/data/fleet.py` | Production (read-only) | Re-measure LOC; verify `Fleet.to_dict` / `Fleet.from_dict` / `resolve_order_references` still at expected locations. |
| `game/strategy/data/planet_gen.py` | Production (read-only) | Re-measure LOC; identify clean split axis or absence thereof. |
| `game/strategy/data/ship_instance.py` | Production (read-only) | Re-measure LOC post-PROJ-449. Most important re-measurement of the project (gates Phase 3). |

### Phase 1 — F-A-008 fleet.py extraction (Production)

| File | Type | Notes |
|------|------|-------|
| `game/strategy/data/fleet.py` | Production | Replace `Fleet.to_dict` (currently fleet.py:520) body with 1-line call to `fleet_to_dict(self)`. Replace `Fleet.from_dict` (currently fleet.py:558) with the split-call shape: `Fleet(**fleet_from_dict_kwargs(data, registries))`, then ship hydration via `_deserialize_fleet_ships`, then post-construction reattach (task_forces, fleet_policy, orders, resolve_order_references). `Fleet.__init__` accepts only identity/config kwargs (fleet.py:44-68), so `fleet_from_dict_kwargs` returns ONLY those — `ships` are hydrated outside. Adjust `resolve_order_references` per planet_serde precedent. |
| `game/strategy/data/fleet_serde.py` | Production (new) | New module modeled on `planet_serde.py`. `fleet_to_dict(fleet) -> dict`, `fleet_from_dict_kwargs(data, registries) -> dict` (constructor kwargs ONLY), plus `_deserialize_fleet_ships(ship_data_list, registries) -> List[ShipInstance]` and `_deserialize_fleet_orders(orders_data, fleet_id) -> List[Order]`. The `registries` parameter threads through for ship deserialization (`ShipInstance.from_dict(ship_data, registries=registries)`). |
| `tests/integration/save_load/test_fleet_serde_roundtrip.py` | Test (new) | Characterization-first: a comprehensive fleet -> dict -> fleet round-trip test created BEFORE the refactor; passes against current code (captures current dict shape verbatim). Asserts byte-identical save output before and after extraction. This file does NOT exist at HEAD; Phase 1 creates it. |
| `tests/unit/strategy/fleet/test_serialization.py` | Test (existing) | Verify still green post-extraction (existing fleet-serialization unit coverage). |
| `tests/integration/save_load/test_roundtrip_fleet.py` | Test (existing) | Verify still green post-extraction (existing integration round-trip coverage). |
| `tests/integration/save_load/` (all) | Test (existing) | Targeted regression gate per the plan. |
| `Projects/active_projects/PROJ-459/decisions.md` | Docs | Phase 1 records the serde-shape decision per Task 1.3 (`fleet_from_dict_kwargs` returns only `__init__` kwargs; ship/order hydration lives outside the helper). |

### Phase 2 — F-A-009 planet_gen.py split or deferral

| File | Type | Notes |
|------|------|-------|
| `game/strategy/data/planet_gen.py` | Production | Either: extract methods to sibling module(s) AND drop file below 500 LOC, OR: leave untouched and document deferral. Decision made after reading the file end-to-end. |
| `game/strategy/data/planet_gen_*.py` | Production (new, conditional) | One or more sibling modules created if a clean split axis emerges. Candidate names per F-A-009: `planet_gen_surface.py`, `planet_gen_orbits.py`, `planet_gen_atmosphere.py`. Exact naming chosen at extraction time. |
| `tests/unit/strategy/data/test_planet_gen.py` | Test (existing) | Verify still green post-split (deterministic-given-seed). |
| `tests/unit/strategy/generation/` (all) | Test (existing) | Verify still green; this is the systemic regression gate for procedural generation. |
| `Projects/active_projects/PROJ-459/decisions.md` | Docs | If deferring: document the structural reason and concrete next-touch criterion. |
| `Projects/active_projects/PROJ-459/findings/PROJ-459_findings.md` | Findings | Update F-A-009 status to "closed via split" or "deferred with rationale". |

### Phase 3 — F-A-007 ship_instance.py measurement decision (no code)

| File | Type | Notes |
|------|------|-------|
| `game/strategy/data/ship_instance.py` | Production (read-only) | Re-measure LOC. Inspect what survived after PROJ-449 retirements. |
| `Projects/active_projects/PROJ-459/decisions.md` | Docs | Verdict recorded: closed (under 500) OR spun out (over 500). |
| `Projects/active_projects/PROJ-459/findings/PROJ-459_findings.md` | Findings | Update F-A-007 status with final disposition. |
| `Projects/active_projects/PROJ-461/` | Project (new, conditional) | If LOC still ≥ 500: full project skeleton scaffolded via `python Projects/scripts/create_project.py "ShipInstance LOC reduction"` (likely PROJ-461; ID auto-assigned). |

### Docs touched (likely)

| File | Type | Notes |
|------|------|-------|
| `docs/02_PATTERNS.md` | Docs | Phase 1: 1-line update referencing `fleet_serde.py` as the second instance of the planet_serde pattern (alongside planet_serde itself). |
| `docs/01_ARCHITECTURE.md` | Docs | Phase 1: update strategy/data/ listing if it enumerates `fleet_serde.py` style modules. Verify against current listing before editing. |

## Notes
- All phases run on `main` per user's standing no-worktrees preference.
- Phase 0 is mandatory. Without re-measurement, scope is unverified.
- Phase 1 has the most save-format risk; byte-identical save output is the gate.
- Phase 2 may end as a "no split" deferral — that's an acceptable outcome per Codex r4 ("If no clean axis emerges from the read, document the structural reason... and defer the split — don't force a bad cut").
- Phase 3 is explicitly NOT a code change. Per Codex r4: "F-A-007 should not be smuggled in as a side quest."
