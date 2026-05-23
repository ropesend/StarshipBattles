# PROJ-493 Design

## Background

PROJ-479 Phase 3 Task 3.14 deferred the SuperweaponValidator test cluster (10+ tests across 16 patch sites) with the rationale "requires DI introduction in production". Per Codex planning consult (`AgentCoordination/Scratchpad/Consult/20260523T125621Z_plan-PROJ-479-followthrough/response.md`, Finding 1 + Risks), this is **the only confirmed production seam gap** from PROJ-479's deferred CAT-6 set.

Evidence:
- `SuperweaponOrderProcessor.__init__` accepts `event_bus`, `empire_mutator`, `nav_service` but no validator dep (`game/strategy/engine/superweapon_order_processor.py:62-79`).
- `_get_empire_mutator` and `_get_nav_service` use the canonical lazy-default pattern (`game/strategy/engine/superweapon_order_processor.py:81-94`).
- The processor calls `SuperweaponValidator.find_ship_with_ability(...)` statically at `:275-282`.
- 16 tests patch this static path (`tests/unit/strategy/engine/test_superweapon_order_processor.py:131,166,201,622,669,708,749,786,854,910,1009,1049,1098,1132,1181,1239`).

## Approach

Two phases. Phase 1 is a TDD-driven production change following the existing lazy-default pattern. Phase 2 is mechanical test migration.

### Phase 1 — Production DI seam introduction
Mirror the existing `empire_mutator` / `nav_service` pattern:

```python
def __init__(
    self,
    event_bus: Optional[Any] = None,
    empire_mutator: Optional[Any] = None,
    nav_service: Optional[Any] = None,
    validator: Optional[Any] = None,  # NEW
) -> None:
    self._event_bus = event_bus
    self._empire_mutator = empire_mutator
    self._nav_service = nav_service
    self._validator = validator  # NEW

def _get_validator(self) -> "SuperweaponValidator":  # NEW
    if self._validator is None:
        from game.strategy.validation.superweapon_validator import SuperweaponValidator
        self._validator = SuperweaponValidator()
    return self._validator
```

Update the static call sites at `:275-282` to route through `self._get_validator()`:

```python
# Before:
ship = SuperweaponValidator.find_ship_with_ability(...)
# After:
ship = self._get_validator().find_ship_with_ability(...)
```

If `find_ship_with_ability` is currently a `@staticmethod`, that's fine — calling it via instance works without changing the signature. If a future task needs to make it an instance method, do it then.

**TDD step (Phase 1 Task 1.1):** write a test that constructs `SuperweaponOrderProcessor(validator=StubValidator())` and asserts the stub's `find_ship_with_ability` is consulted. Confirm test fails before Phase 1 production change; passes after.

### Phase 2 — Test migration
For each of the 16 patch sites:

```python
# Before:
with patch('game.strategy.engine.superweapon_validator.SuperweaponValidator.find_ship_with_ability') as mock:
    mock.return_value = stub_ship
    processor = SuperweaponOrderProcessor(event_bus=...)
    processor.process_xxx(...)

# After:
class StubValidator:
    def find_ship_with_ability(self, *args, **kwargs):
        return stub_ship
processor = SuperweaponOrderProcessor(event_bus=..., validator=StubValidator())
processor.process_xxx(...)
```

Extract `StubValidator` to a module-level fixture or class helper to avoid 16 copies.

## Why only this one seam

Per Codex consult Risks section: "PROJ-493 will sprawl if it is seeded with speculative 'others'. On current evidence, only 3.14 is a confirmed missing production seam; 3.32 is definitively not one." Other PROJ-479 deferred items previously labeled "needs DI introduction" either:
- Already have the seam (Task 3.32 — `ActionExecutionEngine.action_time_resolver`, addressed in PROJ-491 Phase 3), OR
- Are actually test-side patterns dressed up as DI claims (Tasks 3.1, 3.2, 3.4, etc. — addressed in PROJ-491 Phase 1), OR
- Are unverified seam-gap claims that need investigation first (Task 3.20 second bullet — PROJ-491 Phase 4 will route).

If PROJ-491 Phase 4 investigation finds a real seam gap, the task gets added to PROJ-493 with a new phase. Until then, this project stays narrow.

## Risks

- **Risk:** The lazy-default `_get_validator()` pattern creates a hidden `SuperweaponValidator()` instance in production if no validator is injected. If `SuperweaponValidator.__init__` has side effects (registers handlers, opens files), production behavior could change.
  **Mitigation:** Phase 1 Task 1.0 reads `SuperweaponValidator.__init__` and confirms it has no side effects. If it does, change Phase 1 Task 1.1 to use module-level singleton instead.

- **Risk:** Test migration may surface latent dependencies on the static call's import-time behavior (rare but possible if validator caches something at import).
  **Mitigation:** Run the full superweapon test file after each batch of ~4 migrations.

- **Risk:** `find_ship_with_ability` may be defined on multiple classes (e.g. base + subclass). Routing through `self._get_validator()` could resolve to a different class than the static call.
  **Mitigation:** Phase 1 Task 1.0 confirms the class hierarchy and overrides.

## Source evidence

- Codex consult response: `AgentCoordination/Scratchpad/Consult/20260523T125621Z_plan-PROJ-479-followthrough/response.md` (Finding 1, Risks)
- PROJ-479 Phase 3 Task 3.14: `Projects/active_projects/PROJ-479/phase_3_checklist.md:107-111`
- Production class: `game/strategy/engine/superweapon_order_processor.py:62-94, 275-282`
- DI pattern reference: `docs/02_PATTERNS.md:22,88,106,678`, `docs/01_ARCHITECTURE.md:58,175,437-438`
