# PROJ-65: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-06 | Project initialized | Starting point for Game Class Scene Protocol Refactor |
| 2026-02-06 | Standardize all scenes to IScene (no adapters) | Cleaner than adapters; avoids indirection layer. All scenes modified to match protocol directly. |
| 2026-02-06 | Extract menu to MenuScene | Eliminates MENU special-casing in Game; `active_scene` is always valid. |
| 2026-02-06 | Decouple battle coordinator in this project | Required for clean scene dispatch; `_battle_accumulator` belongs in BattleScreen, not Game. |
| 2026-02-06 | WIDTH/HEIGHT as Game instance attrs | Simple fix; globals are testability hazard. Pass via constructor + handle_resize. |
| 2026-02-06 | Keep exit_dialog as overlay, not a scene | It overlays any scene, doesn't replace current one. Different lifecycle. |
| 2026-02-06 | Use callback-based scene transitions | Scenes call `scene_callback("action", **kwargs)` instead of setting flags. Game registers handler. Explicit, testable, no polling. |
| 2026-02-06 | IScene has 4 methods: handle_event, update, draw, handle_resize | Minimal common denominator. draw is universal; handle_event standardizes inconsistent patterns; update(dt) for animation; handle_resize for window changes. |
| 2026-02-06 | TestLabScreen coupling handled via scene_callback | Replace `self.game.battle_scene` access with callbacks. Game sets up battles when TestLab requests them. PROJ-57 handles internal decomposition. |
| 2026-02-06 | Keep FormationEditorScreen in Tools/ | Moving it is out of scope. Just verify it matches IScene. |
