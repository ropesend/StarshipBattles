# PROJ-232: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-03-28 | Project initialized | Starting point for Command Layer Cleanup |
| 2026-03-28 | Exclude fleet resolution boilerplate from scope | 3-line pattern repeats 25x but abstraction (decorator/exception) deviates from codebase conventions (Protocol+mixin). Cost exceeds benefit. Can revisit if handler count grows. |
| 2026-03-28 | Use `field(init=False)` on base `Command.type` | Removes `type` from generated `__init__`, preserving all 24 call sites (12 positional + 12 keyword). Precedented by `ValidationResult` in `game/core/validation.py:91`. |
| 2026-03-28 | Use `str, Enum` for TransferDirection and BuildEntityType | Backwards compatible — `BuildEntityType.PLANET == "planet"` is True. No changes needed at existing string comparison sites. Serialization produces raw string values. |
| 2026-03-28 | Keep `IssueTransferCommand.cargo_type` as `str` | Only one value ("passengers") currently used — not worth an enum yet. |
| 2026-03-28 | Change Protocol `command: Any` to `command: 'Command'` | More informative than `Any` while still accepting all subclasses. `@runtime_checkable` doesn't enforce parameter type exactness. Concrete handlers can narrow further. |
| 2026-03-28 | Convert DIAG logs to debug, not remove all | Some diagnostic info (cargo capacity, validation result) is useful for future debugging at debug level. Only remove the truly redundant error-path duplicates. |
