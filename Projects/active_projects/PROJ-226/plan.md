# PROJ-226: Strategy Layer Consolidation

**Dedup Campaign: 3/5**

## Overview

Consolidate duplicated logic across the strategy layer — engine, data, services, and validation modules. This project addresses findings from the full-codebase duplication review, targeting strategy-specific duplications that create maintenance burden and inconsistency risks.

**Source:** `Reviews/results/2026-03-24_200858_general_duplication-consolidation-full-codebase/`

**Depends on:** PROJ-224 (already merged)

## Current State

**Not started.**

## Phases

### Phase 1: Bug Fix & Critical Dedup
Priority fixes that address correctness issues or violate architectural boundaries.

- **DUP-SE-001** — Superweapon mission move bug: fix incorrect movement logic in superweapon command handlers
- **DUP-SE-002** — Combat event logging: deduplicate combat event logging across engine modules
- **DUP-SE-008** — Private API access: all `session.turn_engine._registries` references must use public API (12 call sites across 2 files)
- **DUP-SE-009** — Backward compat alias: remove `process_end_turn_orders` alias, update all call sites

### Phase 2: Strategy Data Consolidation
Deduplicate logic in strategy data modules.

- **DUP-SD-01** — Companion star generation: consolidate duplicated companion/secondary star generation logic in `planet_gen.py`
- **DUP-SD-02** — Planet registration: consolidate planet registration logic across `galaxy_entity_registry.py`, `galaxy_spatial_index.py`, `galaxy_system_generator.py`, `galaxy.py`
- **DUP-SD-06** — Dead `_generate_mass`: remove dead `_generate_mass` method from `stars.py` and/or `planet_gen.py`
- **DUP-SD-09** — `occupied_hexes`: consolidate duplicated `occupied_hexes` logic across 7 strategy data files
- **DUP-SD-10** — `_facility_is_shipyard`: consolidate shipyard facility check logic across `build_queue_source.py`, `production_engine.py`, `empire_economy_calculator.py`

### Phase 3: Engine & Service Consolidation
Deduplicate logic in strategy engine and services.

- **DUP-SE-003/004** — Spawn logic: consolidate fleet/ship spawn logic in `production_engine.py` and `conflict_resolution_engine.py`
- **DUP-SE-006** — JOIN_FLEET: consolidate `JOIN_FLEET` handling across `fleet_order_processor.py`, `command_handlers.py`, `turn_engine.py`, `game_session.py`
- **DUP-SE-007** — Registries init: consolidate registry initialization across 7 engine files
- **DUP-SS-01** — Population extraction: extract duplicated population logic from `cargo_transfer_service.py`
- **DUP-SS-02** — Superweapon validation: consolidate duplicated validation in `superweapon_validator.py` and `superweapon_command_handlers.py`

### Phase 4: Documentation & Evaluation
Evaluate remaining findings, update docs.

- **DUP-SD-07** — Evaluate and document any remaining strategy data duplication
- **DUP-SYS-001** — Evaluate system-level duplication patterns
- **DUP-SE-005** — Evaluate remaining engine duplication, document decisions

## Success Criteria

- All `session.turn_engine._registries` replaced with public API access
- `process_end_turn_orders` alias removed
- Dead `_generate_mass` removed
- Duplicated spawn, registration, and validation logic consolidated
- All tests pass (7353+ baseline)
- No new test warnings introduced
