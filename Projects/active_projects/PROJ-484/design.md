# PROJ-484: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source Audit
- **Audit directory:** `Reviews/results/2026-05-20_210635_legacy-audit/`
- **Bundle counts:** Audit verified: 17 (across all sibling projects) | This bundle: 4 verified, 0 uncertain, 0 INFO, 0 deferred
- **Sibling projects:** PROJ-485, PROJ-486, PROJ-487, PROJ-488, PROJ-489, PROJ-490
- **Cluster identity:** dead_reexports — "legacy import-path preservation" lines across entity-header / package-init files
- **Severity breakdown:** 2 CRITICAL (zero call sites), 2 MAJOR (single test caller each), 0 MINOR

### Quick Wins
Two whole-file-line deletions ship in a single PR with no caller migration:
- `game/simulation/entities/ship.py:23` — `CombatConstants` re-export (0 callers)
- `game/ui/services/image/__init__.py:37` — `_null_provider` side-effect import (0 callers; explicit `register_image_provider` at line 42 already covers the registration)

## Initial Analysis
The 2026-05-20 legacy audit reports the codebase is exceptionally clean (0 module aliases, 0 save migrations, 0 TYPE_CHECKING-only re-exports, 0 partial protocol implementers). The remaining "legacy" surface is a small set of dead re-export lines preserved with `# Re-export for backward compatibility` comments — but with verifier-confirmed zero or one call site through the re-export path.

### Architecture
- Each re-export targets a distinct canonical module (`game.core.combat_types`, `game.core.constants`, `game.simulation.physics_constants`). The re-export pattern is the "system being eradicated"; each canonical is the survivor.
- The unused `_null_provider` side-effect import is structurally similar — the canonical registration is the explicit `register_image_provider("null", NullImageProvider)` call.

### Key Patterns to Reuse
- **Direct import from canonical module**: `game/simulation/combat/collision.py:53`, `damage_calculator.py:28`, `projectile_manager.py:148` already use the canonical `from game.core.combat_types import DamageContext` — replicate that for the test caller.
- **Explicit registration**: `image/__init__.py:42` `register_image_provider("null", NullImageProvider)` — the canonical way to register the null provider.

### Dependencies & Risks
1. **Test caller updates** — Two test files must be updated in lockstep with the production deletions, or the test suite will break. Risk is trivial.
2. **`Ship` internal use of `CombatConstants`** — `ship.py` itself uses `CombatConstants.DEFAULT_MAX_TARGETS` (line ~190). That usage routes through `Ship`'s own direct import, not through the re-export line being deleted. Verify before deletion.

### Opportunities Discovered
- `ship.py:21` has a header comment "Re-export for backward compatibility and convenient access" that becomes orphan once both lines 22 and 23 are removed. Remove it in the same PR.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
