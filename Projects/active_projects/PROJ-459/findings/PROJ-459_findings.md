# PROJ-459 Findings — Strategy data LOC extractions

Consolidated findings carried verbatim from `Projects/archived_projects/PROJ-444/findings/bucket_a_data_facade_scan.md` (the original 2026-05-18 bucket-A scan), with current status as of 2026-05-19 (after Codex r4 redesign closed PROJ-444..447 and respun the work into 12 job-oriented projects per `AgentCoordination/Scratchpad/Consult/20260519T004841Z_stages-1-2-audit-and-redesign/response.md`).

This project carries three findings:
- **F-A-008** — `fleet.py` 677 LOC (now 686 as of re-measurement 2026-05-19); extract `Fleet.to_dict` / `Fleet.from_dict` to `fleet_serde.py`. **Closes here in Phase 1.**
- **F-A-009** — `planet_gen.py` 610 LOC; split by sub-concern or document deferral. **Closes here in Phase 2 (either via split or via documented deferral with concrete next-touch criterion).**
- **F-A-007** — `ship_instance.py` 839 LOC; **explicit follow-up decision only — not closed in this project.** Per Codex r4: "if it still sits at 839 LOC after job 1 [PROJ-449], spin it as its own next-touch project." Phase 3 of this project is measurement-and-decision; the actual extraction work, if needed, is a fresh project.

---

## F-A-007 — `ShipInstance` is 839 LOC, well over the 500-LOC production ceiling

- **Severity (original)**: medium
- **Category**: polish
- **File**: `game/strategy/data/ship_instance.py:1` (file is 839 LOC)
- **Symbol**: module-level
- **Source refactor**: PROJ-425 + PROJ-431 + PROJ-436 (multiple extraction passes)
- **What survived**: The class docstring at lines 47-125 explicitly acknowledges and rationalizes the size: "intentionally large because of D2 default (a) — keep inline ``design_data``". 910-caller entry-point sweep declared OUT of PROJ-438 scope; PROJ-443 Phase 5b found 18-file test footprint and kept the kwarg wrapper. Five high-value shim entry points (`create`, `to_dict`, `clone`, `to_ship`, `update_from_ship`) explicitly retained per TD-06 Weak-LLM Guardrail #1 (PROJ-436 decisions.md row 122). Net: ceiling violation IS the documented residue.
- **Why it's a problem**: Single largest data-layer file by 200+ LOC. The retained shims occupy roughly ship_instance.py:419-783 (~360 LOC of forwarding methods). Each shim has 4-10 callers; the 910-caller migration is the blocker. CLAUDE.md says "Production files under `game/` should stay under 500 LOC. Split by responsibility when a touched file approaches that ceiling." The file is 67% over.
- **Suggested action (original)**: NOT a quick sweep. Bundle into a future "ShipInstance shim retirement" project — likely 2-3 phases of mechanical caller migration per shim cluster (serializer, bridge, resource manager). The class docstring already documents the explicit removal conditions; act on them when bandwidth allows.
- **Effort (original)**: large

### Status as of 2026-05-19 (Phase 3 verdict)
- **Disposition: SPUN OUT as PROJ-461.** Post-PROJ-449 + post-PROJ-454 LOC = **789** (+289 over the 500 ceiling). The retained TD-06 high-value shim cluster + class-docstring catalog account for the residual overage. The 910-caller migration sweep (PROJ-425 Phase 5d/5e estimate) is the actual cost and is out of PROJ-459's scope per Codex r4 directive.
- PROJ-461 created at `Projects/active_projects/PROJ-461/`. F-A-007 transferred verbatim to `PROJ-461/findings/PROJ-461_findings.md` with updated status. PROJ-459 retains only the measurement-decision narrative here.
- See PROJ-459 decisions.md row 2026-05-19 (Phase 3 verdict) for the disposition entry.

---

## F-A-008 — `Fleet.py` is 677 LOC, over the 500-LOC ceiling

- **Severity (original)**: low
- **Category**: polish
- **File**: `game/strategy/data/fleet.py:1` (file was 677 LOC; re-measured 686 LOC on 2026-05-19)
- **Symbol**: module-level
- **Source refactor**: PROJ-87, PROJ-210, PROJ-222, PROJ-238, PROJ-269, PROJ-382, PROJ-431, PROJ-436 (progressive extraction passes)
- **What survived**: Five delegate classes already extracted (`FleetBattleAdapter`, `FleetCapabilityCalculator`, `FleetConsumableAggregator`, `FleetPursuerTracker`, `FleetHierarchy`). What remains is mostly: order-queue management (~120 LOC), to_dict/from_dict (~140 LOC), and merge_with logic (~50 LOC). The serialization helpers are a natural extraction target into `fleet_serde.py` per PROJ-372's planet_serde precedent.
- **Why it's a problem**: Modest ceiling violation (35% over). Less acute than ship_instance.py but a natural candidate when next touched.
- **Suggested action (original)**: Extract `Fleet.to_dict` + `Fleet.from_dict` (+ `resolve_order_references` already delegating to OrderSerializer) into a sibling `fleet_serde.py` modeled on `planet_serde.py`. Would drop fleet.py by ~140 LOC to ~537 LOC.
- **Effort (original)**: small

### Status as of 2026-05-19
- **Disposition in this project: CLOSED via Phase 1 extraction.**
- Re-measurement confirms fleet.py is now 686 LOC (up slightly from the original 677 — small drift). `Fleet.to_dict` is at fleet.py:520; `Fleet.from_dict` is at fleet.py:558; `resolve_order_references` is at fleet.py:657. All three are at the locations the original finding identified.
- Phase 1 mirrors the planet_serde extraction exactly. Save-format byte-identity is the regression gate; targeted save-load tests are the TDD entry point.
- Note: Fleet's from_dict requires the `registries` parameter (unlike Planet's), because ship deserialization needs it. The fleet_serde split must thread the registry through. Verified by Read of fleet.py:558-655 on 2026-05-19.

### Closure record — 2026-05-19 Phase 1 execution
- `game/strategy/data/fleet_serde.py` created (168 LOC). Public surface: `fleet_to_dict`, `fleet_from_dict_kwargs`, `_deserialize_fleet_ships`, `_deserialize_fleet_orders`. Mirrors `planet_serde.py` (219 LOC).
- `Fleet.to_dict` reduced to a 1-line facade calling `fleet_to_dict(self)`. `Fleet.from_dict` is a **thin facade** that calls `Fleet(**fleet_from_dict_kwargs(data, registries))` then performs the unavoidable post-construction hydration of `ships` / `task_forces` / `fleet_policy` / `path` / `construction_queue` / `orders` (none of which `Fleet.__init__` accepts as kwargs — see decisions.md row 2026-05-19 "fleet_from_dict_kwargs returns only Fleet.__init__ kwargs"). `Fleet.resolve_order_references` stays a method on `Fleet` (already a thin delegate to `OrderSerializer`; moving it adds no value — see decisions.md row 2026-05-19).
- fleet.py LOC: 693 → 632 (−61). Still above 500-LOC ceiling; the next mechanical extraction target (order-queue management, ~120 LOC) is the natural next-touch.
- Save-format byte-identical, confirmed by new characterization test at `tests/integration/save_load/test_fleet_serde_roundtrip.py` (3 tests).
- Targeted regression: 35 tests pass (`test_fleet_serde_roundtrip.py` + `test_roundtrip_fleet.py` + `test_serialization.py`). Broader `tests/integration/save_load/` + `tests/unit/strategy/fleet/`: 388 pass.
- Full sharded suite: 23397/23397 passed, 0 failures.
- F-A-008 marked **closed**.

---

## F-A-009 — `planet_gen.py` is 610 LOC, over the ceiling

- **Severity (original)**: low
- **Category**: polish
- **File**: `game/strategy/data/planet_gen.py:1` (file is 610 LOC — re-measured 2026-05-19 same)
- **Symbol**: module-level
- **Source refactor**: PROJ-372 (planet split)
- **What survived**: Procedural planet generation logic. Likely splittable along atmosphere-gen / surface-conditions-gen / orbital-arrangement axes. (Not deep-read in the original scan — flagged the LOC ceiling violation only.)
- **Why it's a problem**: Modest ceiling violation (22% over). Out-of-scope for any other current finding.
- **Suggested action (original)**: When next touched, split by sub-concern (atmosphere / surface / orbits).
- **Effort (original)**: medium

### Status as of 2026-05-19
- **Disposition in this project: Phase 2 closes this finding (via split OR via documented deferral with concrete next-touch criterion).**
- Cursory inspection of `planet_gen.py` reveals one class `PlanetGenerator` with ~13 private methods. Candidate split axes visible from the method list:
  - **Orbital arrangement**: `_generate_orbital_slots`, `_collect_star_exclusion_zones`, `_generate_mass_constrained` (~150 LOC)
  - **Moon generation**: `_generate_moons`, `_calculate_moon_chance`, `_generate_moon_mass` (~80 LOC)
  - **Body construction**: `_create_planet_objects`, `_create_single_planet` (~100 LOC)
  - **Surface / type / resource**: `_generate_surface_flags`, `_determine_type`, `_generate_resources` (~150 LOC)
- One of these — most likely moon-gen or surface/type/resource — should extract cleanly. Decision made in-phase after end-to-end read.
- Per Codex r4: if no clean axis emerges, document the structural reason and defer. A 610 LOC file is not so far over that a forced bad cut beats deferral.

---

## Open follow-up criteria (for future projects to triage)

- **F-A-007 spinout candidate (PROJ-461 or later)**: If Phase 3 spins this out, the new project should: (a) enumerate the TD-06 shims that survive PROJ-449; (b) propose a caller migration sequence (serializer / bridge / resource manager clusters); (c) re-confirm the 910-caller estimate against current code; (d) carry a measurable LOC target.
- **F-A-009 next-touch criterion (if deferred)**: Should be a concrete observable like "split when atmosphere-gen passes 200 LOC" or "split when a non-orbital generator emerges". Set in `decisions.md` at the time of deferral; don't leave as "split eventually".
