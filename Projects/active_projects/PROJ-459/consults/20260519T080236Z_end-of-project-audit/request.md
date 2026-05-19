---
protocol: consult/v1
from: claude
to: codex
mode: planning
allow_tests: false
created_at_utc: 2026-05-19T08:02:36Z
repo_root: <runtime-discovered>
consult_leaf: <runtime-discovered>
complete: true
---

# PROJ-459 — End-of-Project Audit Consult

## Context

PROJ-459 ("Strategy data LOC extractions") closed all 4 phases on `group-a`. Scope was three findings: F-A-007 (ship_instance.py LOC), F-A-008 (fleet.py serde extraction), F-A-009 (planet_gen.py split).

What this project did:

- **Phase 0**: re-measurement after PROJ-449 + PROJ-451 + PROJ-454 landed. LOC table written to `findings/phase_0_remeasurement.md`. fleet.py 686→693 (+7 from PROJ-451 Task 2.0), planet_gen.py 610→610, ship_instance.py 839→789.
- **Phase 1 (F-A-008)**: extracted `Fleet.to_dict` / `Fleet.from_dict` and helpers to new `game/strategy/data/fleet_serde.py` (168 LOC) modeled on `planet_serde.py`. fleet.py 693→632 LOC (−61). Smaller drop than the planned ~140 because the post-construction hydration (task_forces / fleet_policy / path / construction_queue) had to stay on Fleet — `Fleet.__init__` only accepts identity/config kwargs. New characterization test at `tests/integration/save_load/test_fleet_serde_roundtrip.py` locks byte-identical save shape. `Fleet.resolve_order_references` stayed on Fleet (mirrors planet_serde precedent). F-A-008 closed.
- **Phase 2 (F-A-009)**: extracted `_generate_surface_flags`, `_determine_type`, `_generate_resources` from `PlanetGenerator` into a new sibling module `game/strategy/data/planet_gen_surface.py` (236 LOC). All three were `self`-method declarations only — their bodies don't reference `self`. The move is a pure mechanical change. The `_get_planetary_ids` cached helper moved with `_generate_resources` (its only caller). planet_gen.py 610→427 LOC (−183, under the 500 ceiling). 27 test call-site migrations across `test_planet_gen.py` + `test_planet_classification_logic.py`. One downstream fix in `tests/integration/strategy/test_planet_physics.py` re-pointed leaky re-exports (MASS_EARTH/MASS_JUPITER/generate_atmosphere) to canonical sources. F-A-009 closed via split.
- **Phase 3 (F-A-007)**: SPINOUT verdict. ship_instance.py at 789 LOC (+289 over the 500 ceiling). Per Codex r4 directive, F-A-007 spun out as new project PROJ-461 at `Projects/active_projects/PROJ-461/` with findings carried verbatim. PROJ-459 retains only the measurement-decision narrative.

Cross-group state observed:
- PROJ-449 merged at `ebb5c0e7f`
- PROJ-451 merged at `893482c04`
- PROJ-454 merged at `ab2da0669`
- PROJ-456 merged at `244c1fa16`

Doc consolidation rule (per protocol §9): docs/01_ARCHITECTURE.md + docs/systems/strategy_layer.md edits for fleet_serde mention are staged at `Projects/active_projects/_doc_consolidation/PROJ-459_pending.md`. Phase 2 (planet_gen_surface) did not generate new doc edits — pattern docs already describe extraction generically. The last finisher of PROJ-457/459/460 applies all three staged edits.

Final sharded baseline: **23397 tests / 23397 passed / 0 failed / 0 errors**.

## Commit range on `origin/group-a` (since PROJ-451 merge)

```
b5af0340f PROJ-459 Phase 0: re-measurement after PROJ-449 + PROJ-451 merged
4ffe065b1 PROJ-459 Phase 1: extract Fleet.to_dict/from_dict to fleet_serde.py (closes F-A-008)
781e8e451 PROJ-459 Phase 2: split planet_gen.py into planet_gen_surface.py (closes F-A-009)
1b85114ee PROJ-459 Phase 3: ship_instance.py at 789 LOC — F-A-007 spun out as PROJ-461
```

## What I want you to do

Audit end-to-end. Four things I want a second opinion on:

### 1. Verify each finding's closure status against current HEAD

- **F-A-008**: confirm `fleet_serde.py` exists with `fleet_to_dict` + `fleet_from_dict_kwargs` + `_deserialize_fleet_ships` + `_deserialize_fleet_orders`. Confirm `Fleet.to_dict` and `Fleet.from_dict` are 1-line facades. Confirm the byte-identical save test exists and passes.
- **F-A-009**: confirm `planet_gen_surface.py` exists with the three module-level functions. Confirm `PlanetGenerator._determine_type` etc. are GONE from `planet_gen.py`. Confirm `planet_gen.py` is now under 500 LOC.
- **F-A-007**: confirm PROJ-461 exists at `Projects/active_projects/PROJ-461/` with a populated plan.md + findings file carrying F-A-007 verbatim. Confirm PROJ-459's findings + decisions document the spinout.

### 2. Sanity-check the Phase 1 split design

`fleet_from_dict_kwargs` returns ONLY `Fleet.__init__` kwargs; per-ship hydration runs in `Fleet.from_dict` AFTER `Fleet(**kwargs)` returns. Is that the right shape, or would moving ship/order hydration into a single `fleet_from_dict(data, registries) -> Fleet` helper (constructing the Fleet inside the helper) be cleaner? The current shape mirrors `planet_serde.planet_from_dict_kwargs` precedent, which has the same split.

`resolve_order_references` stayed on Fleet. Justified by planet_serde precedent (Planet has no equivalent — its orders don't carry cross-entity refs). Reasonable, or should it move?

### 3. Sanity-check Phase 2 — seed determinism

The three moved functions use the global `random` module (same as before). The move is byte-identical mechanically but is the seed-determinism contract preserved? Specifically: if a test seeds `random.seed(N)` and runs the old `_determine_type` and the new `determine_planet_type` with the same inputs, do they produce identical outputs in identical order? My understanding: yes (same `random.random()` calls in the same order), but verify by inspection.

### 4. Look for residue / missed sites

- Did the test sweep miss any callers of `_determine_type` / `_generate_resources` / `_generate_surface_flags`?
- Did the fleet_serde extraction miss any callers of `Fleet.to_dict` / `Fleet.from_dict`?
- Is there any caller of `Fleet.from_dict` that expects the old signature (just `data` arg, no `registries`)? — the new shape requires `registries` per `fleet_serde.fleet_from_dict_kwargs(data, registries)`.
- Look at `Projects/active_projects/PROJ-461/plan.md` — is it minimally complete enough to be the canonical follow-up project, or are there obvious gaps (e.g., no caller-count audit) that should be filled before PROJ-459 closes?

## Output schema

Standard consult/v1 response.md:
- `## Findings` — per concern with `file:line` citations.
- `## Risks` — anything that might bite later.
- `## Open questions` — anything you couldn't determine read-only.
- Set `exit_status: ok` if no blockers; `exit_status: needs-fixes` for verified blockers.

## Constraints

(Inline-include the canonical Constraints block from `AgentCoordination/protocols/consult_prompt_block.md`.)

- Strict TDD: identify failing tests first; don't propose code that bypasses this.
- Documentation first: reference `docs/` as source of truth; never read or cite `docs/_ignore/`.
- No backward-compat shims, monkey patches, fallback systems, or save-file migrations.
- Respect layer boundaries (per `docs/01_ARCHITECTURE.md`, `docs/02_PATTERNS.md`).
- Do NOT revert unrelated user changes; work around existing dirty state.
- Evidence standard: cite `file:line`, command output, or transcript. Label unverified claims `[unverified]`.
- Final ownership: the initiator owns synthesis. You advise; you do NOT implement.
- Follow-up rule: the initiator may ask follow-ups. You stop when advice converges or repeats.
- Permission contract: read repo, run tests only when `allow_tests: true` AND the mode is `pre-final-check` or `deep-dive`, write only inside the directory named by `consult_leaf` in the request frontmatter. Do NOT edit production code, docs, tickets, projects, configs, commits, branches, or PRs.

This consult has `allow_tests: false` and `mode: planning` — read-only inspection only.
