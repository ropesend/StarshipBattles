# PROJ-468 File Manifest

> Generated during project creation. Used by parallel-project conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| `docs/04_SERVICES.md` | Doc | DONE: removed component_inspector shim claim + dir-map entry (CRITICAL); fixed in-family effect_ability_metadata refs (lines 63/538/605/615) → ability_metadata.py; stamp bumped |
| `docs/systems/ability_reference.md` | Doc | DONE: component_inspector → component_abilities/layers; effect_ability_metadata → ability_metadata (CRITICAL); planetary.py table rows mapped to exact planetary/ package files + section sources; dead test_effect_ability_metadata.py → test_ability_metadata_* |
| `docs/systems/strategy_layer.md` | Doc | DONE: removed "remains importable" effect_ability_metadata claim (CRITICAL); data/spectrum.py → game/strategy/data/spectrum.py; added Superweapon Order Processing section (superweapon_order_processor.py); Phase 3 (Codex-audit): fixed residual EFFECT_ABILITY_METADATA shim claim (706), planetary.py (746), SYSTEM_EFFECT_ABILITIES (752) |
| `docs/guides/adding_abilities.md` | Doc | DONE: component_inspector → component_abilities/layers; effect_ability_metadata → ability_metadata + EffectFacet (CRITICAL); dead test paths → test_ability_metadata_effects.py; Phase 3 (Codex-audit): residual planetary.py (511) → planetary/ package, EFFECT_ABILITY_METADATA (582) → AbilityMetadata/EffectFacet |
| `docs/guides/component_system.md` | Doc | DONE: component_inspector → component_abilities/layers incl. false re-export claim + dead example import (CRITICAL); dead test path → test_component_abilities/layers.py |
| `docs/guides/qs_complex_design.md` | Doc | DONE: component_inspector → component_abilities/layers (CRITICAL); planetary.py → planetary/ package; dead test path → test_component_abilities/layers.py |
| `docs/systems/fighters.md` | Doc | DONE: removed dead planet_context_menu.py link (split files already present) |
| `docs/systems/minefields.md` | Doc | DONE: removed dead planet_context_menu.py link + File-table row (split rows already present) |
| `docs/systems/research_system.md` | Doc | DROPPED — not touched. Re-verification: line 24 already a correct historical-corrective warning, not self-contradictory. Finding no longer holds (see decisions.md). |
| `docs/guides/testing_infrastructure.md` | Doc | DONE: test_damage.py → tests/unit/simulation/combat/test_damage_calculator.py |
| `docs/guides/pre_commit_hooks.md` | Doc | DONE: added Last verified blockquote |
| `docs/01_ARCHITECTURE.md` | Doc | DONE: added New-Game Initialization (GameInitializer) subsection documenting game_initializer.py; prepended PROJ-468 note to PROJ-467's Last-verified stamp (preserved 467's edits) |

> **Sibling-overlap note:** `docs/01_ARCHITECTURE.md` also appears in PROJ-467 (path-drift fixes). PROJ-468 only *added* a New-Game Initialization subsection and prepended a note to the existing 2026-05-20 PROJ-467 stamp; 467's path-drift edits were re-read and preserved (not reverted).
>
> **Re-verification note (post-PROJ-467):** all surviving findings re-grepped against live repo before editing. Dropped: Task 2.5 (research_system.md). No 467 edit was reapplied or reverted.
