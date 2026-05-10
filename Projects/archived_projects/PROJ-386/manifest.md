# PROJ-386 File Manifest

## Files

| File | Type | Action | Notes |
|------|------|--------|-------|
| `game/ui/screens/battle_setup/controller.py` | Production | Edit | LEG-03-008 — delete `_complex_toggles` migration at lines 548-568 [banned by CLAUDE.md Rule 3] |
| `game/strategy/data/component_activation_state.py` | Production | Edit | LEG-03-017 — delete `{'active': bool}` legacy-format branch at lines 144-149 [banned by CLAUDE.md Rule 3] |
| `game/strategy/data/ship_instance_serializer.py` | Production | Edit | LEG-03-018 — delete silent-ignore (lines 100-102) + graceful-degrade (lines 127-138) [banned by CLAUDE.md Rule 3] |
| `game/ui/screens/battle_setup_state.py` | Production | Edit | LEG-04-005 — delete legacy `side_0`/`side_1` emit + read at lines 257-300 [banned by CLAUDE.md Rule 3] |
