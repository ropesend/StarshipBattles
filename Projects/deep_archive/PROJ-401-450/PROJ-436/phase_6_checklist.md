# Phase 6: Protocol churn + build-queue/UI `context_type` cleanup

**Status:** Complete
**Depends on:** phase_5
**Review Mode:** standard
**Files (planned):** see `phase_state.json` phase_6.planned_files

**Objective:** Audit the post-Phase-5 protocol surface (`IEmpire`,
`IStockpileHolder`, `IStagingYardHolder`, `IShipInstance`,
`IFacility`) and the `build_queue_controller.py:483-513`
`context_type` reads. Refresh docstrings to match the contracts
actually shipped in Phases 3-5. Pin the surviving contract with an
AST guard so accidental future drift (especially around `IEmpire`
mutator-style methods that were deleted from the concrete class in
Phase 5) gets caught.

---

## Audit conclusion (Phase 6a)

Full audit found NO protocol methods need deletion:

| Protocol member | Disposition |
|---|---|
| `IEmpire.resource_pool` | Stable; satisfied by post-Phase-5 colony-aggregation property. Docstring refresh only. |
| `IEmpire.max_storage` | Stable; set by `EmpireWriteService` via `HarvestingEngine`, read by UI. Docstring refresh only. |
| `IShipInstance.cargo_contents` | Stable; Phase 3f kept the public name as `@property`. Docstring refresh notes manager-API canonical write path. |
| `IFacility.consumable_levels` | Stable; Phase 0 D1 kept `PlanetaryFacility.consumable_levels` as internal state. No change. |
| `IStockpileHolder` (4 methods) | Stable; post-Phase-4 Planet `@property`-over-private-field implementation transparently satisfies the protocol. Class docstring refresh only. |
| `IStagingYardHolder` (4 methods) | Same as `IStockpileHolder`. |

Production callers of the deleted `Empire.add_resources` /
`Empire.consume_resources` / `Empire._fleet_resource_pool`:
**zero**. These were never on the protocol surface — they were
concrete-class methods/fields. The Phase 5 deletion guard at
`tests/static_guards/test_no_legacy_storage_fields.py` already pins
the concrete-class absence. The Phase 6 guard pins the
protocol-surface contract — both positive (surviving members stay)
and negative (mutator-style methods never appear on `IEmpire`).

`build_queue_controller.py:483-513` `context_type` reads are UI
entity-routing (planet vs fleet `entity_id` extraction), NOT
storage-typed. `ProductionEngine.context_type` branches at
`production_engine.py:561,629` ARE storage-typed; those are Phase 8.

See `decisions.md` 2026-05-18 rows for full audit detail.

---

## Sub-phases

### 6a — Audit (decisions only, no code)

- [x] Audit `IEmpire` / `IStockpileHolder` / `IStagingYardHolder` /
  `IShipInstance` / `IFacility` against production callers and
  implementers.
- [x] Audit `build_queue_controller.py:483-513` to classify as
  UI-routing vs storage-typed.
- [x] Document audit conclusion in `decisions.md`.

### 6b — Docstring refresh + AST guard

- [x] Refresh docstrings on `IEmpire.resource_pool`, `IEmpire.max_storage`,
  `IShipInstance.cargo_contents`, `IStockpileHolder` class,
  `IStagingYardHolder` class.
- [x] Author `tests/static_guards/test_no_legacy_protocol_names.py`
  with positive ratchets (surviving methods stay) AND negative
  ratchets (no mutator-style methods on `IEmpire`).
- [x] Sharded suite green.

### 6c — Build-queue UI classification

- [x] Document why `build_queue_controller.py:483-513` `context_type`
  reads stay as-is. The branching is UI entity-routing, not storage-
  typed; Phase 8 (`ProductionEngine.context_type` deletion) does not
  affect the UI controller's planet/fleet dispatch.

### 6d — Codex consult + remediation

- [x] Run `claude-consult` against Codex, mode `pre-final-check`,
  `--allow-tests`. See `decisions.md` 2026-05-18 Codex consult row.
- [x] Verify findings against current code (do not trust without
  verification per the standing workflow rule).
- [x] Remediate verified findings; document non-remediated findings.

---

## Phase Completion Checklist
- [x] All sub-phases complete
- [x] `tests/static_guards/test_no_legacy_protocol_names.py` green
- [x] Existing protocol-isinstance tests still green
  (`test_galaxy_protocols.py`, `test_protocols.py`)
- [x] Full sharded suite green
- [x] Update status to Complete; update plan.md + phase_state.json
