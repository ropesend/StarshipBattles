"""BattleConfig tests — slimmed in PROJ-269 Phase 6.

The previous test suite covered `BattleMode` enum behavior, which was
removed in Phase 6. The remaining BattleConfig surface is just a
plain operational-options dataclass; its dataclass behavior is covered
indirectly by `tests/unit/simulation/battle_controller/` fixtures.

This empty module is retained so older test-discovery references
resolve to a valid path.
"""
