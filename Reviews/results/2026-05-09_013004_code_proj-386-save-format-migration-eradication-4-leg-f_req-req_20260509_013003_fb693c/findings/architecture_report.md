# Architecture Conformance Findings

## CLAUDE.md Rule 3 — Save-file migration ban

### ARCH-001: Rule 3 adherence — PASS (verified)
All 4 deleted legacy code paths confirmed eradicated:

| Finding ID | File | Legacy Path | Verification |
|---|---|---|---|
| LEG-03-008 | `controller.py:548-568` | `_complex_toggles` top-level migration | Deleted. `_load_from_path` now calls `BattleSetupState.from_dict()` directly — no migration block. |
| LEG-03-017 | `component_activation_state.py:144-149` | `{'active': bool}` branch in `from_dict` | Deleted. `from_dict` now uses `data['phase']` directly — raises `KeyError` on old format. |
| LEG-03-018 | `ship_instance_serializer.py` | silent-ignore `component_damage` + graceful-degrade missing `components` | Deleted. `from_dict` uses `data['components']` directly — raises `KeyError` on missing key. |
| LEG-04-005 | `battle_setup_state.py:257-300` | `side_0`/`side_1` emit + read | Deleted. `to_dict` emits only `{"sides": [...]}`; `from_dict` requires `data["sides"]`. |

Zero `data.get('active'...)` references in production code.
Zero `if 'version' in data` gates.
Zero `# DEPRECATED, will remove later` comments.
Zero `data.get('components', {})` patterns in serialization paths (the remaining 5 matches in `game/` are unrelated: `battle_state.py`, `data_extractor.py`, `layer_iterator.py`).

### ARCH-002: `side_0`/`side_1` property shims — NOT a violation
`battle_setup_state.py:168-182` retains `side_0`/`side_1` as in-memory `@property` accessors to `sides[0]`/`sides[1]`. These are NOT save-format keys — they are in-memory backward-compat shims for callers. The save format only uses `{"sides": [...]}`. Per the agent's note, this is in-scope as in-memory properties.

### ARCH-003: Cross-impact with PROJ-388 (ModifierLogic) — NONE
Grepped `ModifierLogic` across `game/strategy/data/` and `game/simulation/` — zero production references. PROJ-386's serialization changes have no interaction with the now-deleted `ModifierLogic` consumers.

### ARCH-004: `ship_instance_serializer.py` layer placement — PASS
`ShipInstanceSerializer` sits in `game/strategy/data/` (Strategy layer). Its imports: `game.core.validation_helpers`, `game.core.component_state` — both Core layer. No layer violation.
