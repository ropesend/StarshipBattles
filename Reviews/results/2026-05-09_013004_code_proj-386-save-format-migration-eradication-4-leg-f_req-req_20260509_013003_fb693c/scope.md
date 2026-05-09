# Review Scope: PROJ-386 — Save-format migration eradication

**Type:** code (delegated by Claude Code)
**Request ID:** req_20260509_013003_fb693c
**Review Mode:** standard

## Scope

4 production files in commit `00e4abac6` (on top of merge `b00012fcb`):

- `game/strategy/data/component_activation_state.py` — LEG-03-017: deleted `{'active': bool}` legacy-format branch in `from_dict`
- `game/strategy/data/ship_instance_serializer.py` — LEG-03-018: deleted silent-ignore for legacy `component_damage` + graceful-degrade for missing `components`
- `game/ui/screens/battle_setup/controller.py` — LEG-03-008: deleted `_complex_toggles` legacy migration in `_load_from_path`
- `game/ui/screens/battle_setup_state.py` — LEG-04-005: deleted `side_0`/`side_1` legacy emit + read

Plus 5 deleted test classes/methods and 14 rewritten test fixtures across 11 test files.

## Instructions

1. Grep verification of complete deletion of legacy symbols/branches
2. `to_dict` round-trip symmetry verification
3. Test deletions: were they really only-legacy tests?
4. Test rewrites: semantic-preserving?
5. CLAUDE.md Rule 3 strict adherence
6. Cross-impact with PROJ-388 (ModifierLogic deletion)
7. `to_dict` always-emit change scrutiny

## Context

Stage 2 second project in 11 sequential PROJ runs. Sits on top of merge `b00012fcb`. PROJ-386 enforces CLAUDE.md Rule 3: no save-file migration, no fallback, no version-gate.

## Limitations

Review performed via git diff comparison (parent `b00012fcb` vs HEAD `00e4abac6`), text search, and manual code inspection. Tests not executed. Review directory created manually (daemon invocation path).
