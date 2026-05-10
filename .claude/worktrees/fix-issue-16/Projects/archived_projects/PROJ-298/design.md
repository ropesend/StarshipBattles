# PROJ-298: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

This project finishes the FleetOrder/PlanetOrder → Order migration introduced by PROJ-238 (archived). PROJ-238 unified fleet and planet order types into a single `Order` class but left backward-compat aliases in place "for the migration period." That period is over — the aliases are now technical debt that violates the System Migration Policy.

### Verified Inventory (as of 2026-04-26)

**Alias declarations (5 sites):**
- `game/strategy/data/order_types.py:170` → `FleetOrder = Order`
- `game/strategy/data/order_types.py:171` → `PlanetOrder = Order`
- `game/strategy/engine/commands.py:100` → `ClearFleetOrdersCommand = ClearOrdersCommand`
- `game/strategy/engine/commands.py:289` → `DeleteFleetOrderCommand = DeleteOrderCommand`
- `game/strategy/engine/commands.py:305` → `ReorderFleetOrderCommand = ReorderOrderCommand`

**Re-export shim module (1 file):**
- `game/ui/screens/fleet_orders_window.py` (8 lines) — wildcard re-export of `orders_window.py` plus `FleetOrdersWindow = OrdersWindow` alias

**Old-name usage scope (initial grep, includes archives):**
- `FleetOrder`/`FleetOrders*` — 109 files
- `PlanetOrder` — 14 files in production + tests (not counting archives/Tracking)
- After filtering out `Projects/deep_archive/`, `Reviews/results/`, `Tracking/`, `coverage.json`, the production+test count drops dramatically — exact figure is Phase 1's job

### Verification Note (vs. Code Review Report)

The 2026-04-26 code review listed only `FleetOrder` and three command aliases (4 symbols). It missed:
- `PlanetOrder = Order` alias (line 171 of `order_types.py`)
- `FleetOrdersWindow = OrdersWindow` alias (`fleet_orders_window.py:8`)
- The whole `fleet_orders_window.py` re-export shim module
- Documentation references to old names (e.g., `docs/03_CONVENTIONS.md`)

The original report's "726 usages" figure may have included `Tracking/`, `Reviews/results/`, and `Projects/deep_archive/` — Phase 1 will produce the accurate production+test-only count.

## Architecture

### Pattern: System Migration Policy
Per CLAUDE.md "When a new system replaces an old one, ERADICATE the old system completely." The alias-and-shim approach was an acceptable transitional state during PROJ-238; leaving them after the migration completed violates the policy. The clean-sheet question is: "If we were building this from scratch, would we have aliases?" No — we'd have one canonical name. So we delete.

### Why Aliases Were Created (PROJ-238 context)
The original migration unified `FleetOrder` (orders attached to fleets) and `PlanetOrder` (orders attached to planets/colonies) into a single `Order` class with an `entity_type` discriminator. The fleet-vs-planet distinction is now data, not type. The aliases let the migration land in stages — but staged migration only justifies temporary aliases.

### Why Both `FleetOrder` AND `PlanetOrder` Alias the Same `Order`
Originally these were two separate classes; PROJ-238 collapsed them. The aliases preserve both old import paths during the transition. After cleanup, callers should use `Order` directly and disambiguate via `order.entity_type` when needed.

### Risk: `fleet_id` Field Name (OUT OF SCOPE)
`commands.py:95` carries `fleet_id: int  # Kept for backward compat; use entity_id for new code`. This is a **field-level** backward-compat marker that touches serialized command data, save files, and command-handler logic. Renaming it is meaningfully riskier than the symbol-level renames in this project (could break save files; could change wire format for any saved commands). **Out of scope.** Track as a follow-up project if desired.

## Key Patterns to Reuse

- **Migration cadence (lessons from PROJ-238):** big renames go smoothly when split into "rename in production → rename in tests → delete aliases." This project follows the same cadence (Phases 2 → 3 → 4).
- **Bulk find-and-replace:** Python's symbol-level renames are safe with whole-word replacements (e.g., `\bFleetOrder\b` regex). Care: don't substring-match into longer names. `FleetOrders*` should remain (per `OrdersWindow.fleet_orders_logic`-style names that are about a fleet's *orders*, not the FleetOrder class).
- **Shim deletion = caller migration first:** verify zero internal importers of the shim module before deletion (the shim's purpose was to support callers that hadn't migrated yet).

## Dependencies & Risks

1. **Risk: substring matches in find-and-replace.**
   `FleetOrder` is a substring of variable names like `fleet_orders` (instance variables, function names). A naive `sed s/FleetOrder/Order/g` would corrupt those.
   **Mitigation:** use word-boundary regex (`\bFleetOrder\b`) or symbol-aware tools (libcst, ast). Test with a small file first.

2. **Risk: PROJ-238's "fleet_orders" naming conventions are pervasive in non-symbol contexts.**
   Variable names, file names (`test_fleet_orders_logic.py`, `test_fleet_orders_refresh.py`), method names (`get_fleet_orders()`) all use `fleet_orders` — these are NOT being renamed (they refer to "the orders for a fleet" — a sensible domain term, just not the same concept as the deprecated `FleetOrder` class).
   **Mitigation:** explicitly scope the rename to **class-level/symbol-level only.** Variable, function, and file names with `fleet_orders` stay.

3. **Risk: external/save data referring to old class names.**
   If save files serialize class names, old saves may not load after the rename. Per CLAUDE.md "Save files are disposable. Old saves are not migrated — they are discarded."
   **Mitigation:** none required by policy; document this in the project's verification notes.

4. **Risk: `docs/03_CONVENTIONS.md` references old names.**
   Old names in convention docs propagate stale guidance.
   **Mitigation:** Phase 5 includes a doc sweep; replace examples with current canonical names.

5. **Risk: 109-file grep includes a lot of archives.**
   Renaming archived project plans or historical reviews would distort historical record.
   **Mitigation:** scope explicitly excludes `Projects/deep_archive/`, `Reviews/results/`, `Tracking/`, `coverage.json`. Phase 1 produces a filtered manifest.

## Opportunities Discovered

- The `fleet_orders_window.py` shim deletion is a clean exemplar — single-purpose backward-compat module with no internal users; perfect Migration Policy demonstration.
- Renaming validator filenames like `planet_order_validator.py` → `order_validator.py` may be worth doing in a follow-up (since `PlanetOrder` no longer exists). Out of scope here, but worth a project-end note.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
