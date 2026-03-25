# PROJ-228 Phase 6: Serialization Protocol & Evaluation

## DUP-PAT-002: Serializable Protocol
- [ ] Audit `Serializable` definitions across:
  - `game/simulation/interfaces/entity_protocols.py`
  - `game/simulation/interfaces/__init__.py`
  - `game/simulation/battle_state.py`
- [ ] Consolidate to a single protocol definition
- [ ] Update all implementors to reference the canonical definition
- [ ] Verify serialization tests pass

## DUP-SS-06: Remaining UI Structural Evaluation
- [ ] Review all UI files for any remaining structural duplication
- [ ] Document findings — fix or log as future work
- [ ] Update decision log with rationale for any deferred items

## Documentation Updates
- [ ] Update `docs/02_PATTERNS.md` with new UI patterns (ScrollState, BaseScene, etc.)
- [ ] Update `docs/03_CONVENTIONS.md` if new naming/organization conventions established
- [ ] Update any UI-specific docs affected by consolidation
- [ ] Verify docs-code consistency

## Completion
- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] All Phase 6 items verified
- [ ] Project complete — archive PROJ-228
