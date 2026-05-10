# PROJ-391 File Manifest

## Files

| File | Type | Action | Notes |
|------|------|--------|-------|
| `game/strategy/services/planet_economy_projector.py` | Production | Edit | LEG-04-007 + cross-system Pair 2 secondary — replace `_get_harvester_info` call + manual layer iteration with canonical helpers |
| `game/strategy/engine/harvesting_engine.py` | Production | (Reference only) | Canonical `get_harvester_info` lives here |
| `game/ui/screens/battle_setup/spec_compiler.py` | Production | Edit | LEG-01-011 / LEG-04-008 — replace `_iter_components` call + delete local function |
| `game/core/patterns/layer_iterator.py` | Production | (Reference only) | Canonical `iter_components` lives here |
| `game/simulation/combat/formation.py` | Production | Edit | LEG-01-017 — add `FormationSpec.to_dict/from_dict` per Pattern 17 |
| `game/strategy/data/task_force.py` | Production | Edit | LEG-01-017 — delete duplicate `_formation_to_dict/_formation_from_dict` (lines 125-142); migrate callers |
| `game/simulation/replay/replay_serialization.py` | Production | Edit | LEG-01-017 — delete duplicate helpers (lines 191-213); migrate callers |
