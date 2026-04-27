# PROJ-307 File Manifest

## Files

### EDIT (timestamps backfilled)
| File | Type | Notes |
|------|------|-------|
| `docs/01_ARCHITECTURE.md` | Docs | Add `> **Last verified:** YYYY-MM-DD` blockquote after H1 |
| `docs/02_PATTERNS.md` | Docs | Same |
| `docs/03_CONVENTIONS.md` | Docs | Same — and Phase 2 adds Documentation Freshness section |
| `docs/04_SERVICES.md` | Docs | Same |
| `docs/05_ERROR_HANDLING.md` | Docs | Same |
| `docs/06_UI_STYLE_GUIDE.md` | Docs | Same |
| `docs/guides/adding_abilities.md` | Docs | Same |
| `docs/guides/adding_modifiers.md` | Docs | Same |
| `docs/guides/component_system.md` | Docs | Same |
| `docs/guides/modifier_system.md` | Docs | Same |
| `docs/guides/qs_complex_design.md` | Docs | Same |
| `docs/guides/simulation_testing.md` | Docs | Same |
| `docs/guides/testing_infrastructure.md` | Docs | Same |
| `docs/systems/ability_reference.md` | Docs | Same |
| `docs/systems/ai_system.md` | Docs | Same |
| `docs/systems/combat_simulation.md` | Docs | Same |
| `docs/systems/orders_system.md` | Docs | Same |
| `docs/systems/production_system.md` | Docs | Same |
| `docs/systems/research_system.md` | Docs | Same |
| `docs/systems/resource_system.md` | Docs | Same |
| `docs/systems/strategy_layer.md` | Docs | Same |

### EDIT (convention enforcement)
| File | Type | Notes |
|------|------|-------|
| `CLAUDE.md` | Instructions | Add `Last verified:` rule to Rule 2 (DO + DO NOT lists) |
| `docs/03_CONVENTIONS.md` | Docs | Add §Documentation Freshness section |

### EXPLICITLY EXCLUDED
- `docs/_ignore/**` — user's scratchpad per CLAUDE.md
- `Projects/**/*.md`, `Reviews/**/*.md`, `Tracking/**/*.md` — different lifecycle, not part of `docs/`
- `CLAUDE.md` itself getting a `Last verified:` line — special instruction file, not a doc
- `docs/README.md` — already has the timestamp; verify format consistency only
