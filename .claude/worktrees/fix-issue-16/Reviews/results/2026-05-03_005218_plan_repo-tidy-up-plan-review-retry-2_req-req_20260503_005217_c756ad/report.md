# Plan Review: Repo Tidy-Up (retry 2)

**Request ID:** req_20260503_005217_c756ad
**Review Type:** plan
**Scope:** `.agent_reports/plan_review/perform-a-review-of-wild-lampson.md`
**Reviewed:** 2026-05-03

---

## Q1: Does the revised Tier 4 cutoff (2026-03-31) bisect any active project's review trail?

**Finding: MAJ — `reviews_index.md` links break silently.**

No active project (PROJ-300 through PROJ-318) references any pre-April review result folder. Grep across `Projects/active_projects/` returned zero hits for `Reviews/results/2026-0[123]`. However, `reviews_index.md` itself contains ~55 relative links pointing at `results/<date>_<type>_<description>/`. The plan moves those folders into `results/_archive_2026_Q1/` but states "reviews_index.md rows stay untouched." Every link to a pre-April folder will break — the index becomes a mass of 404-equivalents. This is a documentation break, not a code break, but it affects the primary navigational artifact for the Reviews system.

**Suggested fix:** Either (a) run a find-replace across `reviews_index.md` to prefix `_archive_2026_Q1/` on all pre-April links as part of Tier 4, or (b) keep the 4 "In Progress" and "Led to Project" March reviews live and adjust the cutoff to 2026-02-28, which would reduce the archive count but avoid archiving semantically active reviews.

Additionally, the 2026-03-13 consistency reviews are marked "In Progress" and the 2026-03-24 duplication-consolidation review is "Led to Project" (→ PROJ-224 through PROJ-228). Archiving "In Progress" reviews is semantically wrong regardless of link breakage. Consider resolving their status before archiving, or exclude live-status entries.

---

## Q2: Did the plan miss any obvious junk at the repo root or in `Tools/`/`scripts/`?

**No findings.**

Root scan: 24 files, all either covered by the plan (Tier 1/2 candidates) or legitimate (`launcher.py`, `conftest.py`, `qa_launcher.py`, `pyproject.toml`, `pytest.ini`, `.gitignore`, `AGENTS.md`, `CLAUDE.md`, etc.). `Tools/` is well-organized with 33 subdirectories matching tool names. `scripts/` contains only `planet_qc/` (noted in plan as excluded). No stale `*_old.py`, `_backup/`, or `tmp_*` artifacts found.

---

## Q3: Should anything in `AgentCoordination/` outside of `_archive/` also be retired?

**Finding: MIN — stale one-off planning documents exist but none are obvious junk.**

`AgentCoordination/` top-level contains several `.md` files that appear to be one-off plans or review responses (`codex_agent_coordination_plan_final.md`, `support_systems_cleanup_plan.md`, `support_systems_critical_review.md`, `user_response.md`). They lack dates in filenames and may be stale. However, none are obviously junk — they could still be reference material for the multi-agent coordination system. A deeper audit would be required to determine staleness, which exceeds the "30-second scan" instruction. Not recommended for this tidy-up pass.

---

## Q4: One overall risk that the plan's author may have missed.

**Finding: MIN — `.agent_reports/` directory is not accounted for in cleanup scope.**

The plan file itself was copied into `.agent_reports/plan_review/` to enable this review. This is a new, non-standard directory at the repo root created as a workaround for the OpenCode worker's path restriction. After this review completes, the plan file becomes residual junk — the same category as Tier 1 candidates. The plan does not mention it because it was created to deliver the plan. Recommend adding a note to Tier 4 or a post-review step: delete `.agent_reports/plan_review/perform-a-review-of-wild-lampson.md` (and the directory if empty) once the tidy-up is executed.

---

## Verdict

**APPROVE WITH CHANGES** — fix `reviews_index.md` links during Tier 4 archive move, and exclude In-Progress/Led-to-Project March reviews from the archive cutoff (or resolve their status first).
