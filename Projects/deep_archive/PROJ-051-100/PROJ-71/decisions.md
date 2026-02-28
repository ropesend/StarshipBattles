# PROJ-71: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-07 | Project initialized | Starting point for Strategy Layer Hotkey System |
| 2026-02-07 | Scope: Strategy layer + all sub-screens reachable from it | User specified: includes Build Queue, Fleet Orders, Transfer Dialog, Planet List, Fleet Report. Does NOT include Design Workshop (future PROJ) or Battle screen |
| 2026-02-07 | Hotkey hints shown as tooltips only, not in button text | User preference - cleaner UI, no button text changes |
| 2026-02-07 | Full-screen IScene for keybindings editor (not dialog overlay) | User preference - more room for the editor UI |
| 2026-02-07 | Default bindings in data/, user overrides in output/settings/ | Follows existing pattern: data/ = read-only game data, output/ = user-generated files |
| 2026-02-07 | PROJ-72 will wire the "Controls" button access point | User confirmed PROJ-72 exists and will be done after this project. This project builds the system and scene only |
| 2026-02-07 | InputAction uses string-valued enum with dot-notation | Enables context-based filtering (e.g., "fleet.move" matches context "fleet") and human-readable JSON keys |
| 2026-02-07 | KeyBinding stores pygame key names as strings, not ints | Allows JSON to be human-readable ("K_m" vs 109) and decouples from pygame at the data layer |
| 2026-02-07 | O(1) resolution via pre-built (key_int, modifiers) -> action dict | Performance: resolve() is called on every KEYDOWN event, must be fast |
| 2026-02-07 | User overrides file stores only diffs from defaults | Smaller file, easier to understand, survives default keybinding additions in updates |
| 2026-02-07 | Modifier normalization: LSHIFT/RSHIFT both map to "shift" | Users expect Shift to work regardless of which physical key is pressed |
| 2026-02-07 | Conflict detection scoped to overlapping contexts | Two bindings only conflict if their contexts overlap or either is "global". Different screens can share the same key |
