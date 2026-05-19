---
protocol: consult/v1
from: claude
to: codex
mode: planning
allow_tests: false
created_at_utc: 2026-05-19T09:24:28Z
repo_root: <runtime-discovered>
consult_leaf: <runtime-discovered>
complete: true
---

# PROJ-450 — End-of-Project Audit Consult

## Context

PROJ-450 ("Typed staging-yard substrate completion") closed all 5 phases on `group-a`. This is the substrate-typing project that the cancelled PROJ-444..447 Joint A phase tried (and could not complete) in May 2026.

What this project did:

- **Phase 0**: re-verified PROJ-449 Phase 3 precondition + cross-group sync gate (PROJ-454 + PROJ-456 from Group B both Complete on origin/main). Re-checked the 3 blockers from the Stage 3 preflight at HEAD. Findings at `findings/phase_0_audit.md`.
- **Phase 1** (Path A engine API cleanup): widened `Planet.add_to_staging_yard()` to accept `Dict | CarriedVehicle | DropPod`; added `pop_staging_yard_typed()`. Moved 3 private helpers (`_is_carried_vehicle_dict`, `_pod_from_dict`, `_staging_yard_carried_vehicle`) from `transfer_branches.py:41-87` to `planet.py`. Dropped engine flatten/inflate at `transfer_branches.py:412, 454-460` and `issuer_adapter.py:363`. 9 new tests.
- **Phase 2** (substrate widening): `_staging_yard: List[CarriedVehicle | DropPod]`. `planet_serde._normalize_to_typed()` promotes dicts on load; `planet_to_dict` emits per-entry `.to_dict()` on save. Added `__post_init__` normaliser for kwarg construction. Temporary dict-projection bridge property installed. `IStagingYardHolder` annotations tightened. `production_spawner` constructs typed instances directly. Save fixture `galaxy_proj372_populated.json` regenerated. 3 new tests + 5 test-file migrations. LOC ceilings raised: planet.py 485→525, galaxy_protocols.py 210→230.
- **Phase 3** (UI/DTO/validator/bridge replacement): replaced the Phase-2 dict-projection bridge with a permanent typed read-only property `Planet.staging_yard -> tuple[CarriedVehicle | DropPod, ...]` (Option A; no setter). Migrated UI reader at `strategy_detail_fmt.py:285-297` to typed access with dict-mock backward-compat. Migrated `planet_slice` and `planet_dto` to typed attribute access. Simplified `transfer_validator._validate_vehicle_load` (only `isinstance(item, CarriedVehicle)` branch survives). Tightened `IPlanetMutator.add_staging_item` / `pop_staging_item` annotations to the typed union. 2 new UI tests + 4 test migrations. Two `# Intentional:` markers converted to `# Intentional broad catch: <reason>` per docs/03_CONVENTIONS.md.
- **Phase 4** (integration test migration): 6 mutation sites across `test_fms_planet_lay_mines.py` (3) and `test_fms_planet_launch.py` (3) migrated. Renamed `_mine_dict`/`_fighter_dict`/`_satellite_dict` to `_mine_typed`/`_fighter_typed`/`_satellite_typed` returning `CarriedVehicle`. `_StubPlanet.add_to_staging_yard` migrated to isinstance-aware mass access. `test_fms_planet_recovery.py` already typed-aware from Phase 1; `test_fms_a_e2e.py` `.clear()` already migrated in Phase 2.0.
- **Phase 5** (static guard): added `test_planet_staging_yard_substrate_is_typed_not_dict` to `tests/static_guards/test_no_legacy_storage_fields.py`. Exercises both typed-input AND dict-input paths through the public API and asserts every entry in `planet._staging_yard` is `isinstance` of `CarriedVehicle | DropPod`.

Final sharded baseline: **23412 tests / 23412 passed / 0 failed / 0 errors**.

Cross-group state (merged to main):
- PROJ-449 at `ebb5c0e7f` (Group A)
- PROJ-451 at `893482c04` (Group A)
- PROJ-454 at `ab2da0669` (Group B)
- PROJ-456 at `244c1fa16` (Group B)
- PROJ-459 at `2574d5000` (Group A)

PROJ-450 is the LAST project in Group A's serial sequence.

## Commit range on `origin/group-a` (since PROJ-459 merge)

```
b7c368afd PROJ-450 Phase 0: audit complete — sync gate cleared, blockers confirmed
62588d687 PROJ-450 Phase 1: Path A engine API cleanup — typed accept + typed pop
fd3251ec3 PROJ-450 Phase 2: widen Planet._staging_yard to List[CarriedVehicle | DropPod]
a83a299fc PROJ-450 Phase 3: migrate UI reader to typed; replace bridge with read-only property
ae98db76b PROJ-450 Phase 4: migrate 6 integration-test staging-yard mutations to typed inputs
94e579358 PROJ-450 Phase 5: type-pin guard for typed staging-yard substrate (closes F-B-013)
```

## What I want you to do

Audit end-to-end. Five things I want a second opinion on:

### 1. Verify each finding's closure status against current HEAD

- **F-B-013 (substrate type widening)**: confirm `Planet._staging_yard` is typed `List[CarriedVehicle | DropPod]`. Confirm `planet_serde._normalize_to_typed` promotes dicts on load. Confirm `planet_to_dict` emits dicts via per-entry `.to_dict()`. Confirm the 3 helpers moved from `transfer_branches.py` are now in `planet.py`.
- **DI-2026-05-18-001 substrate half**: confirm `transfer_branches.py:412, 454-460` flatten/inflate is gone. Confirm `issuer_adapter.py:363` flatten is gone.
- **3 blockers from Stage 3 preflight**:
  - BLOCKER #1 (UI reader): `strategy_detail_fmt.py:285-297` now reads typed entries with dict-mock fallback. The `isinstance(staging_yard, list)` silent-skip bug is gone.
  - BLOCKER #2 (integration tests): `test_fms_planet_lay_mines.py` + `test_fms_planet_launch.py` mutate via `planet.add_to_staging_yard(typed_helper())`.
  - BLOCKER #3 (validator + write-service): probes simplified; `IPlanetMutator` annotations tightened.

### 2. Verify the read-only property contract holds

`Planet.staging_yard` is a permanent typed read-only `@property` returning `tuple[CarriedVehicle | DropPod, ...]`. No setter. Confirm there's no `@staging_yard.setter` definition anywhere. Confirm `planet.staging_yard = X` raises `AttributeError` at runtime.

### 3. Save-format compatibility

Save format on disk is dict-shaped. Confirm `planet_to_dict` emits dicts via per-entry `.to_dict()` on save. Confirm `_normalize_to_typed` on load handles BOTH the old shape (DropPod with flat `name`/`vehicle_type`/`owner_id` at top level) and the new shape (DropPod with nested `payload`). The save fixture `galaxy_proj372_populated.json` was regenerated to the new shape — sanity-check that loading an old-shape save still produces a typed substrate.

### 4. Look for residue / missed sites

- Any remaining `.to_dict()` call against a CarriedVehicle/DropPod at engine layer boundaries that should now be direct typed pass-through?
- Any place that still constructs a dict-literal staging-yard entry instead of a typed instance?
- Any place that does `isinstance(item, dict)` against staging-yard entries and was missed?
- Any `_StubPlanet` in tests that still uses dict-style attribute access on items it stores?
- `issuer_adapter.py:335` (subagent flagged it but didn't migrate it — verify if that direct `_staging_yard = remaining` assignment is still appropriate post-Phase-3 or if it needs migration to a typed-write path).

### 5. LOC ceilings

`planet.py` ceiling was raised 485→525 in Phase 2. After the Phase-3 bridge replacement (~20 LOC removed), the ceiling could probably drop back to 510 or so. Was the ceiling reset, or is there headroom that should be reclaimed?

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
