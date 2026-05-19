# PROJ-457 — Pending doc consolidation

Cross-group doc edits staged here per
`Projects/active_projects/PROJ-457/plan.md` "Doc consolidation rule
(cross-group)". PROJ-457 / PROJ-459 / PROJ-460 each stage their intended
`docs/01_ARCHITECTURE.md` and `docs/02_PATTERNS.md` edits as a single
block here; the last of the three to finish applies all three pending
blocks as one consolidated commit.

---

## docs/01_ARCHITECTURE.md

**No edits.** PROJ-457's Phase 1-3 extractions are internal UI refactors
that introduce sub-modules of existing screens (`build_queue_input_router.py`,
`planet_list_helpers.py`, `planet_list_event_router.py`,
`test_lab/screen_actions.py`). The architecture doc's `game/ui/screens/`
section lists package-level concepts and sibling sub-packages
(`builder/`, `battle_setup/`, `test_lab/`, etc.), not individual helper
modules. No public-surface changes warrant an architecture-doc update.

Phase 4 (the `exceptions.py` split that WOULD have required an
architecture-doc edit) was DROPPED per the user decision recorded in
`Projects/active_projects/PROJ-457/decisions.md` (2026-05-19, "Phase 4
DROPPED").

## docs/02_PATTERNS.md

**No edits.** Phases 1-3 reuse the existing "thin facade + delegate
class holding screen ref" pattern that Pattern #32 (Compositional
Construction) already describes. The PROJ-457 extractions are concrete
instances of that pattern, not new patterns warranting their own §
entries.

---

## Summary

PROJ-457 produces zero doc edits. Whichever of PROJ-457 / PROJ-459 /
PROJ-460 finishes LAST per the §9.2 "am I last?" check should apply
the PROJ-459 + PROJ-460 pending blocks (if any) and delete all three
`PROJ-*_pending.md` files including this one.
