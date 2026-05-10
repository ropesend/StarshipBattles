# PROJ-240: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-05 | Project initialized | Starting point for Ship God Class Decomposition |
| 2026-04-05 | Facade pattern: Ship stays as public API, delegates to managers | Consistent with PROJ-86/87/88/89 pattern per docs/02_PATTERNS.md section 5. Zero call-site changes required. |
| 2026-04-05 | Layer management (_initialize_layers, change_class) stays on Ship | Identity-level operations tied to Ship construction. Moving them would create circular references with ShipComponentManager since the manager needs ship.layers. |
| 2026-04-05 | AI state (current_target, secondary_targets, ai_strategy) stays on Ship | Simple properties with no logic to extract. Moving would break AI call sites (controllable.py, controller.py, target_evaluator.py) for zero architectural benefit. |
| 2026-04-05 | Resource state stays on Ship | ResourceRegistry is already a separate object; Ship just holds the reference. No logic to extract. |
| 2026-04-05 | Fix mutable cache bug in Phase 1 extraction | The extraction naturally creates the opportunity to fix get_all_components() returning internal cache. Phase 3 adds regression tests to prove the fix. |
| 2026-04-05 | just_fired_projectiles and comp_trigger_pulled exposed as Ship properties with getter/setter | battle_engine.py (lines 442-444) assigns `s.just_fired_projectiles = []` directly. ai/controllable.py (line 394) writes `self._ship.comp_trigger_pulled = value`. Property delegation preserves existing access pattern with zero call-site changes. |
| 2026-04-05 | get_weapon_components_cached loses current_tick parameter | Only used internally (0 external callers found). Dirty-flag invalidation is simpler, more reliable, and consistent with _components_cache pattern. |
| 2026-04-05 | recalculate_stats stays on Ship (not extracted to either manager) | Called from both component lifecycle (add_component) and combat (update). It already delegates to ShipStatsCalculator. Both managers call self._ship.recalculate_stats(). |
| 2026-04-05 | 5-phase plan: Extract Components -> Extract Combat -> Fix Bugs -> Slim Init -> Docs | Components first because combat manager depends on component access methods. Bug fixes after extraction since Phase 1 naturally fixes the cache bug. Docs last per convention. |
| 2026-04-05 | Performance checkpoint after Phase 2 | Ship will have 9 delegates after this project (7 existing + ShipComponentManager + ShipCombatManager). Run simulation tests after Phase 2 to verify no measurable slowdown from added delegation layers. |
| 2026-04-05 | Add ship.set_event_bus() facade method | battle_engine.py currently reaches through `ship.combat_engine._event_bus` to wire the event bus (line 287). After extraction this becomes a 3-level delegation chain. Add a `set_event_bus(bus)` method on Ship facade to avoid deep reaching. |
| 2026-04-05 | Execute after PROJ-241 and PROJ-243 | PROJ-243 adds fleet_attack_bonus/fleet_defense_bonus to Ship.__init__ — Phase 4 (Slim Down Init) needs to incorporate those. PROJ-241 stabilizes Component internal API before ShipComponentManager wraps it. |
