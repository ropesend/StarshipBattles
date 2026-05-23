"""Contract test for StrategyRenderer public API surface (PROJ-309 sub-phase 3.2).

The structural existence tests (isclass / constant isinstance / signature checks /
hasattr+signature / property loop) were deleted by PROJ-478 Phase 1 — they all
passed trivially on any import success. Behavioural coverage of StrategyRenderer
lives in the sibling renderer/animation/draw tests under
tests/unit/ui/screens/.
"""
from __future__ import annotations
