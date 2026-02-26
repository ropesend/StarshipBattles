# PROJ-193: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-24 | Project initialized | Starting point for UI Data Binding Duck Typing Elimination |
| 2026-02-24 | Extend existing Protocols (IPlanet, IFleet) rather than keeping them minimal | User wants maximum maintainability/extensibility for eventual C++/C#/Rust porting. Protocols map to abstract base classes/interfaces/traits. Accepting mock breakage as one-time cost. |
| 2026-02-24 | Create new Protocols: IEmpire, ICombatShip, IShipInstance, IFacility | These don't exist yet, no breakage risk. Provides typed interfaces for all major domain objects accessed by UI. |
| 2026-02-24 | Fix all 31+ mock test files that break from Protocol extension | User explicitly said "I am willing to break test files if it means we have a better architecture in the long run." Follow PROJ-159 pattern (real objects over MagicMock). |
| 2026-02-24 | RaceConfig as concrete type (exception to Protocol rule) | Simple @dataclass with no polymorphic use. Only ever one implementation. Direct type hint is simpler and more maintainable. |
| 2026-02-24 | Leave ~69 instances as-is (self-init guards, pygame checks, dynamic dispatch) | These are legitimate patterns: self-init order guards, 3rd party framework checks, intentional dynamic dispatch. Changing them would reduce clarity. |
| 2026-02-24 | Keep getattr for dynamically-injected attributes | `crew_onboard`, `crew_required`, `shots_fired`, `shots_hit` are set at runtime by `ShipStatsCalculator.recalculate()` (ship_stats.py:386), NOT in `Ship.__init__`. Must use `getattr(ship, 'attr', default)`. |
| 2026-02-24 | Use 8 granular phases | User chose granular phases for easier automated execution and validation. Each phase is independently testable. |
| 2026-02-24 | Use TYPE_CHECKING imports for all new type annotations | Zero runtime cost. Standard codebase pattern. Avoids circular import risk. |
| 2026-02-24 | Document stats_config.py dynamic dispatch with docstring only | `StatDefinition.get_value()` uses `getattr(ship, self.attr_key, 0)` by design — this IS the interface. Adding type hints would break the pattern. |
