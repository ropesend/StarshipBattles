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

## Phase 1 — Split (2026-05-17)

- Created `game/strategy/services/component_abilities.py` — Surface A + `has_warp_capability`. LOC: **403** (under 500, well under the 537 starting point).
- Created `game/strategy/services/component_layers.py` — Surface B + `lookup_design_max_hp`. LOC: **168** (under 500).
- Rewrote `game/strategy/services/component_inspector.py` as a thin re-export shim. LOC: **67**.
- Surface preserved: snapshot test (`tests/unit/strategy/services/test_component_inspector_surface.py`) green; `__all__` identical to the pre-split set.
- Focused suite after split (`test_component_inspector_surface.py + test_component_inspector_layers.py + tests/unit/strategy/test_component_inspector.py + tests/unit/strategy/ship_instance/`): **172 passed**.
- No function signatures changed; bodies are verbatim moves.
- No caller files needed updating because Option A (re-export shim) was chosen.

## Phase 2 — Verification + docs (2026-05-17)

- Full sharded suite: **21144 / 21144 passed** (wall time 144.9s, 12 shards).
- Doc updates:
  - `docs/04_SERVICES.md` — service listing and inspection section now describe the `component_abilities` + `component_layers` split, with the legacy shim called out.
  - `docs/guides/component_system.md` — usage section points at the new module pair.
- PROJ-425 back-link added in `Projects/active_projects/PROJ-425/findings_ledger.md` Phase 2 entry closing the deferred-split note.
- Final LOC: `component_abilities.py` = 403, `component_layers.py` = 168, `component_inspector.py` (shim) = 67. All materially under the 500-LOC convention.
