# Review Scope: PROJ-363 Review: Declarative Command/Order Spec Registry
**Type:** code (delegated by Claude Code)
**Request ID:** req_20260505_061729_d2a4f7
**Scope:**
- `game/strategy/engine/commands/specs.py` (new)
- `game/strategy/engine/commands/__init__.py` (was `commands.py`)
- `game/strategy/engine/handlers/registry_factory.py` (slim down)
- `game/strategy/data/order_types.py` (frozensets)
- `game/strategy/services/action_time_resolver.py` (`ORDER_TO_ABILITY_MAP`)
- `game/strategy/facade/slices/command_dispatch_slice.py` (`__getattr__`)
- `tests/unit/strategy/engine/test_command_specs_contract.py` (new) and any other new tests

**Instructions:**
- Verify all 35 `COMMAND_SPECS` entries are correct; cross-check against the actual command class set
- Confirm `__getattr__` returns proper closures and does not break facade introspection (e.g., `hasattr`, `dir()`)
- Check the `OrderType` frozenset import-cycle workaround — is the test really sufficient?
- Audit for layer violations
- Confirm facade dispatch surface is bit-identical (every existing dispatch_X method still callable)
- Look for `Set{Gravity,Water,RadiationShield,BuildQueuePaused}` commands and confirm their `facade_helper_name=None` is correct (no UI dispatcher today)

**Context:** Just-completed project commit `579a097ec`. 35 commands captured (not 31 as in plan). Sharded 17586 passed. Phase 4 `__getattr__` collapse done.

**Review Mode:** normal (code review with documentation cross-references)

**Limitations:** Single-agent review; no swarm agents launched. Findings based on direct file analysis against docs/ conventions and architecture rules.
