# PROJ-232: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

Code review of the strategy layer's command dispatch system revealed five problems:

1. **Broken dataclass pattern:** All 25+ command classes in `commands.py` use `@dataclass` but override `__init__` manually, defeating dataclass's purpose (auto-generated `__init__`, `__eq__`, `__repr__`).
2. **No type safety:** All 27 handler `execute()` methods use `cmd: Any`, losing IDE autocomplete and type checking.
3. **Magic strings:** `"load"`/`"unload"` and `"planet"`/`"fleet"` used as bare strings instead of enums.
4. **Leftover debug logging:** 9 `DIAG` log statements in `TransferCommandHandler`.
5. **Fleet resolution boilerplate:** 3-line pattern repeats 25 times (excluded from scope — see decisions.md).

## Swarm Findings Summary

### Architecture
- `ICommandHandler` Protocol at `command_handlers.py:100-114` uses `@runtime_checkable` with `command: Any`
- `CommandHandlerRegistry.dispatch()` at line 286 routes via `command.name` property (`__class__.__name__`)
- `GameSession.handle_command()` at line 203 delegates to registry
- All 27 handlers extend `BaseCommandHandler` (mixin with static resolution helpers)
- Superweapon handlers in separate file follow identical pattern

### Key Patterns to Reuse
- **`field(init=False)` + `__post_init__`:** `game/core/validation.py:91` — exact precedent for excluding fields from `__init__`
- **`TYPE_CHECKING` imports:** Already used at `command_handlers.py:26` for `GameSession` forward ref
- **`str, Enum`:** Standard Python pattern for backwards-compatible string enums

### Dependencies & Risks

1. **Dataclass inheritance ordering** — Base `Command` class has `type: CommandType` without a default. If removed naively, `type` becomes the first positional arg in all subclass `__init__` signatures, breaking all 24 call sites. **Mitigation:** `field(init=False)` removes `type` from `__init__` entirely.

2. **Positional call sites (12 total)** — UI files use positional args: `IssueColonizeCommand(fleet.id, planet.id)`. These work with `field(init=False)` because `type` is no longer in `__init__`. **Verified safe.**

3. **Protocol runtime checking** — `@runtime_checkable` Protocol doesn't enforce parameter type exactness. Narrowing `command: Any` → `command: Command` in concrete handlers is standard practice. **No runtime impact.**

4. **`str, Enum` serialization** — Transfer params stored in `FleetOrder.target` dicts serialize `TransferDirection.LOAD` as `"load"` (str value). **Safe — backwards compatible.**

### Call Site Inventory

**Positional (12 sites — safe with field(init=False)):**
- `strategy_colonization.py:157,258`
- `strategy_fleet_ops.py:119,145,208`
- `strategy_superweapons.py:102,146,208,248,292,331`
- `strategy_click_dispatcher.py:244`

**Keyword (12 sites — always safe):**
- `strategy_window_manager.py:399,407,413,445`
- `build_queue_screen.py:253,292`
- `empire_build_queue_window.py:364`
- `cargo_transfer_service.py:236`
- `transfer_dialog.py:428`
- `strategy_build_queue_manager.py:167,171`
- `game_session.py:43`

### Test Impact (27 files, ~8600 lines)
- Primary unit tests: `test_commands.py`, `test_command_handlers.py`, `test_superweapon_command_handlers.py`
- Integration tests: `test_command_handlers.py`, `test_commands.py`, `test_commands_colonization.py`
- All tests should pass without modification — only `__init__` generation mechanism changes

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
