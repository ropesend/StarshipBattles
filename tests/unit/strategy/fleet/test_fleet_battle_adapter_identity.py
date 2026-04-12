"""Ship identity matching tests — superseded by post_battle_hook tests.

PROJ-269 Phase 6 Task 6.6 deleted `FleetBattleAdapter.update_from_battle_results`.
The instance_id-based survivor matching logic moved to
`game.strategy.combat.post_battle_hook.apply_outcome_to_fleets`, which
has its own dedicated test coverage at
`tests/unit/strategy/combat/test_post_battle_hook.py`.

This file is retained (empty) so that references in older changelogs /
grep output still resolve to a valid module path.
"""
