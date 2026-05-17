# PROJ-433 — Findings Ledger

_(Generated from phase_state.json. Do not edit by hand.)_

## Phase 0 — Characterization (2026-05-17)

- Source `game/strategy/services/component_inspector.py` LOC: **537** (matches scaffold expectation).
- `__all__` snapshot test added at `tests/unit/strategy/services/test_component_inspector_surface.py` covering the 16-name public surface and a callability assertion. Green against current HEAD.
- Focused suite baseline (current branch tip):
  `pytest tests/unit/strategy/services/test_component_inspector_surface.py tests/unit/strategy/services/test_component_inspector_layers.py tests/unit/strategy/test_component_inspector.py` -> **44 passed**.
- Import-site grep (`from game.strategy.services.component_inspector ... import ...`): **~50 import statements across ~33 files** (production + tests). The majority are inline imports inside engine / UI / validator methods. Surface A names dominate (`extract_abilities_from_component`, `get_component_abilities`, `iter_facility_ability_entries`, `has_warp_capability`, `ship_has_ability`, `count_ability`, `list_ship_abilities`, `get_ability_list`). Surface B names are imported only by `game/strategy/data/ship_instance.py` (the three layer-view delegates).
- **Option A (re-export shim) locked.** With ~50 import sites scattered across engines, UI, validators, and tests — many of them inside hot paths and lazy inline imports — the re-export shim is dramatically cheaper than a parallel caller migration. Shim debt is ~25 LOC and well-isolated.
- Surface placement decision: `lookup_design_max_hp` ships in `component_layers.py` because its only consumer is `iter_components_by_layer` (no non-layer importer found in the grep). Keeping it with its caller avoids cross-module coupling between the two new modules.
