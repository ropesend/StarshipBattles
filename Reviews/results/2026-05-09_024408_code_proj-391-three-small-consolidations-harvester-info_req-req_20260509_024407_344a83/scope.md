# Review Scope: PROJ-391 — Three small consolidations

**Type:** code (delegated by Claude Code)
**Request ID:** req_20260509_024407_344a83
**Scope:** 4 commits on `feat/03c-phase-aware-execution`:
- `game/strategy/services/planet_economy_projector.py`
- `game/ui/screens/battle_setup/spec_compiler.py`
- `game/simulation/combat/formation.py`
- `game/strategy/data/task_force.py`
- `game/simulation/replay/replay_serialization.py`
- `tests/unit/ui/panels/test_planet_report_panel.py`
- `tests/unit/ui/screens/test_strategy_detail_formatter.py`
- `tests/unit/ui/screens/battle_setup/test_spec_compiler.py`
- `tests/unit/simulation/combat/test_ability_stat_registry.py`
- `tests/unit/simulation/replay/test_serialization.py`

**Instructions:** Verify semantic equivalence of three consolidations: `_get_harvester_info` → `get_harvester_info`, `_iter_components` → `iter_components`, and `_formation_to_dict/from_dict` → `FormationSpec` (Pattern 17). Check deleted helpers have no hidden callers, verify byte-identical serialization, confirm Pattern 17 conformance, and validate replay deserialization isn't broken.

**Context:** Tenth of 11 sequential PROJ runs. Stage 3 third project. Pre-existing test baselines: 19733 passed / 3 failures + 2 errors.
