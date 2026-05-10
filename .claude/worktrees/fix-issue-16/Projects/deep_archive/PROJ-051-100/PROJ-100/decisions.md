# PROJ-100: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-10 | Project initialized | Starting point for Cargo Transfer Orders Overhaul |
| 2026-02-10 | T key enters TRANSFER input mode (click-to-select hex) | User wants T to require hex selection before dialog opens, matching M/J/C pattern |
| 2026-02-10 | D/L commands queue TRANSFER orders (not instant) | Consistent with existing transfer system; all cargo operations are end-of-turn orders |
| 2026-02-10 | D/L commands require clicking a hex first | Consistent with new T flow; user confirmed this approach |
| 2026-02-10 | D/L use simple list dialog with All button | User preference for simpler UI vs. full Transfer dialog slider approach |
| 2026-02-10 | Screen/menu openers use Shift+Key, fleet commands use plain keys | User wants consistent keybinding convention. Frees D for fleet.drop_cargo |
| 2026-02-10 | O (Fleet Orders) and F (Fleet Report) stay as plain keys | User decided these are fleet-context commands, not screen openers |
| 2026-02-10 | Keybinding changes: P→Shift+P, E→Shift+E, R→Shift+R, D→Shift+D, B→Shift+B | Screen openers (Planets, Empire, Research, Design, Build Yards) all get Shift modifier |
| 2026-02-10 | D key for Drop Cargo (no modifier), L key for Load Cargo (no modifier) | Both are fleet commands, no conflicts after keybinding standardization |
| 2026-02-10 | Reuse IssueTransferCommand for D/L | No new command types needed; D creates 'unload' direction, L creates 'load' direction |
| 2026-02-10 | CargoQuickDialog is a new file (not modifying TransferDialog) | Different UX requirements — simpler list vs. full source/target/item/slider dialog |
| 2026-02-10 | Transfer dialog size: 600x500 → 750x600 | User reported current size clips UI elements |
| 2026-02-10 | No backend changes (commands, handlers, validators, processor) | Existing backend fully supports the new UI flows |
