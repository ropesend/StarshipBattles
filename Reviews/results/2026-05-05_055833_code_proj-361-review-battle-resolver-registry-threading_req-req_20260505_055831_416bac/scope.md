# Review Scope: PROJ-361 Battle Resolver Registry Threading
**Type:** code (delegated by Claude Code)
**Request ID:** req_20260505_055831_416bac
**Scope:**
- `game/strategy/adapters/simulation_adapter.py` (around line 258)
- `tests/unit/strategy/adapters/test_simulation_adapter_registry_threading.py` (new)
- `Projects/active_projects/PROJ-361/plan.md`
**Instructions:**
- Verify the registry-injection threading is correct and the PROJ-306 fallback is preserved
- Confirm injected `GameRegistries` correctly implements `IRegistryProvider`
- Audit other call sites in `simulation_adapter.py` for similar drop-the-injection bugs
- Check for layer violations
**Context:** Just-completed project authored at commit `3d9519090`. PROJ-361 functional code IS in HEAD.
