# PROJ-489 Audit Verification

**Audit:** Codex consult 2026-05-23, leaf `AgentCoordination/Scratchpad/Consult/20260523T120008Z_audit-PROJ-489/`
**Verifier:** Claude orchestrator (Batch 1)

| id | finding | verdict | evidence | action |
|----|---------|---------|----------|--------|
| F1 | Delegation correct in all 3 sites (modifier_manager, component_service, modifier_logic) | REJECTED (audit-self-confirmation) | Codex verified instance-field caches, no double-instantiation, registry providers stable | None |
| F2 | Facade boundary clean — `calculate_snap_value` is the only retained non-delegated facade method, used only by builder/modifier_row.py | REJECTED (audit-self-confirmation) | Codex verified | None |
| F3 | Two spot-checked re-shot snapshots semantically correct | REJECTED (audit-self-confirmation) | Codex verified vs `data/components.json` and `data/modifiers.json` | None |
| F4 | Re-shot snapshots picked up 4 extra keys (`launch_rate_mult`, `recovery_rate_mult`, `bay_capacity_mult`, `shield_bonus_add`) not in unchanged 0-baseline siblings; harness ignores extra keys | INFORMATIONAL | `conftest.py:147-173` compare_snapshots iterates only expected JSON keys | No action — harness masks; pre-existing schema-drift behavior unrelated to PROJ-489 |
| F5a | `allow_abilities` blast radius: 105-168 theoretical mismatches per restricted modifier under canonical rules, but `data/designs/*.json` scan found 0 shipped designs using invalid pairs | INFORMATIONAL | Codex static scan | Note in handoff; production safe |
| F5b | `efficient_engines` modifier uses ability names (`Engine`, `Generator`, `Weapon`, `Thruster`) that don't match any component's ability keys (which use `CombatPropulsion`, `ResourceGeneration`, `ManeuveringThruster`, etc.). Under canonical ModifierService semantics, allowed on nothing. Pre-existing data bug. | VERIFIED + OUT-OF-SCOPE | `data/modifiers.json:448-464` vs `data/components.json` ability key namespace | Log as DI |
| F6 | Test rewrite (`test_modifier_logic_service.py`) is largely transitive through underlying ModifierService rather than facade-isolated. Acceptable for one-line pass-through but delegation wiring not asserted with spies | INFORMATIONAL | Codex verified `_make_service()` always constructs real ModifierService | No action — facade is genuinely a pass-through; mock-based delegation tests would be cosmetic |
| F7 | Doc drift: 3 docs still describe pre-consolidation behavior. `docs/04_SERVICES.md:269-273` says ModifierLogicService owns builder logic and requires IRegistryProvider (false). `docs/guides/modifier_system.md:98,285` and `docs/guides/adding_modifiers.md:128,162` say ModifierManager.add_modifier enforces only type restrictions (false — now also enforces allow_abilities per PROJ-489 fix) | VERIFIED + IN-SCOPE | Codex citations + CLAUDE.md "Documentation First" / "keep code and docs consistent" | Phase 2: rewrite the 5 doc references |
