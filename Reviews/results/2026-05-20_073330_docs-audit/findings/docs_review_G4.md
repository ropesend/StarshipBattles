# Documentation Review: Root Agent Docs (G4)

## Summary
- Group: Root Agent Docs (G4)
- Docs in Scope: 3
- Docs Actually Read: 3
- Total Findings: 8
- Critical: 1 | Major: 3 | Minor: 4

## Dead Reference Findings

### F1 [MINOR] Placeholder test path in command examples — AGENTS.md
- **Doc:** `AGENTS.md:24`
- **Reference:** `tests/path/to/test.py`
- **Status:** Dead — does not exist on filesystem
- **Context:** Example command: `pytest tests/path/to/test.py -k test_name`
- **Severity rationale:** This is an intentional placeholder showing command syntax, not a broken file reference. All agents understand this pattern. No corrective action needed, but it flags as dead in the scan.

### F2 [MINOR] Placeholder test path in command examples — CLAUDE.md
- **Doc:** `CLAUDE.md:60`
- **Reference:** `tests/path/to/test.py`
- **Status:** Dead — does not exist on filesystem
- **Context:** Same example command as F1, restated as part of the TDD reinforcement section.
- **Severity rationale:** Same as F1 — intentional placeholder.

## Stale PROJ Reference Findings

No stale PROJ references found for any file in this group. The `stale_proj_refs.json` contains zero entries matching `doc` = `AGENTS.md`, `CLAUDE.md`, or `.agents/CODEX.md`.

## Content Accuracy Findings

### F3 [CRITICAL] Contradictory Python version between AGENTS.md and CLAUDE.md
- **AGENTS.md:52** states: `Python 3.14` (absolute, no qualifier)
- **CLAUDE.md:94** states: `Python baseline: 3.13+`
- **docs/03_CONVENTIONS.md:489** (canonical conventions): `Project baseline is Python 3.13+ (\`pyproject.toml\` declares \`requires-python = ">=3.13"\`)`
- **Live Python:** 3.14.4 (confirmed)
- **Analysis:** CLAUDE.md defers to AGENTS.md as the canonical agent reference (CLAUDE.md:3: "Read `AGENTS.md` first; it owns the non-negotiable rules"). Yet AGENTS.md says "Python 3.14" while CLAUDE.md and the canonical docs/03_CONVENTIONS.md agree on "3.13+". AGENTS.md is out of sync with the project's declared minimum.
- **Impact:** A new agent reading only AGENTS.md might assume Python 3.14 is required rather than 3.13+. In practice, 3.14 ≥ 3.13+, so no code breaks.
- **Recommendation:** Align AGENTS.md to match docs/03_CONVENTIONS.md: change to `Python 3.13+` or `Python 3.14 (baseline: 3.13+)`.

### F4 [MAJOR] `docs/_ignore/` referenced but does not exist on filesystem
- **AGENTS.md:11:** `Never read \`docs/_ignore/\`. It is not documentation.`
- **CLAUDE.md:78-79:** `Never read, summarize, reference, or act on \`docs/_ignore/\`. It is the user's scratch space, not project documentation.`
- **CODEX.md:** Does not reference `_ignore/`.
- **Filesystem check:** `docs/_ignore/` does NOT exist.
- **Other references:** `docs/README.md:15,216`, `docs/03_CONVENTIONS.md:240`, `docs/guides/testing_infrastructure.md:5`, `docs/guides/qs_complex_design.md:5,336` all reference `_ignore/`.
- **Analysis:** The `_ignore/` directory is documented as personal-notes scratch space but has been removed or never created in this checkout. The prohibition against reading it may be misleading to agents who cannot find it. If this is a user-managed directory, the docs should clarify that it may not exist in all checkouts.
- **Recommendation:** Either create `docs/_ignore/` with a `.gitkeep` so the warning has visible purpose, or soften the language to `Never read \`docs/_ignore/\` if it exists` in all referencing files.

### F5 [MAJOR] Broad-except comment placement differs between AGENTS.md and CLAUDE.md
- **AGENTS.md:54:** `Broad catches (\`except Exception\`) must carry \`# Intentional broad catch: <reason>\` on the same line.`
- **CLAUDE.md:111-112:** `Broad \`except Exception\` catches require an intentional-reason comment on the same line or immediately above.`
- **docs/03_CONVENTIONS.md:427:** `Any \`except Exception\` must carry \`# Intentional broad catch: <reason>\` on the same line.`
- **Analysis:** CLAUDE.md adds "or immediately above" which is not in AGENTS.md or the authoritative conventions doc. This could lead to inconsistent comment placement across the codebase if agents follow CLAUDE.md.
- **Recommendation:** Remove "or immediately above" from CLAUDE.md to match the canonical rule.

## Code Example Issues

### F6 [MINOR] Missing "Last verified" line in all three files
- **AGENTS.md:** No `Last verified` timestamp below H1
- **CLAUDE.md:** No `Last verified` timestamp below H1
- **.agents/CODEX.md:** No `Last verified` timestamp below H1
- **Context:** `docs/03_CONVENTIONS.md:503-506` requires all files under `docs/` to carry a `Last verified` timestamp. While agent adapter files are not strictly under `docs/`, the same freshness-tracking convention benefits maintainers.
- **Doc staleness scan:** All three files show `last_verified: null` in the staleness report.
- **Recommendation:** Add `> **Last verified:** 2026-05-20` lines below each H1 for tracking.

### F7 [MINOR] Command verification — all referenced tools exist
- `Tools/test_sharded/test_sharded.py` — EXISTS
- `Tools/audit_shrink/audit_shrink.py` — EXISTS
- `combat_lab/` (for `python -m combat_lab.run_tests`) — EXISTS
- `Tools/agent_coordination/log_skill_usage.py` — EXISTS
- `Tools/agent_coordination/claude_skill_usage_hook.py` — EXISTS
- `Tools/agent_coordination/log_discovered_issue.py` — EXISTS
- `Tools/agent_coordination/triage_discovered_issues.py` — EXISTS
- `Tools/agent_coordination/sync_github_labels.py` — EXISTS
- `.claude/settings.json` — EXISTS
- `.claude/skills/` — EXISTS
- `.agents/skills/` — EXISTS
- `.codex/config.toml` — EXISTS
- `.opencode/skills/ocode-audit-shrink/SKILL.md` — EXISTS
- `AgentCoordination/protocols/ticket_workflow.md` — EXISTS
- `AgentCoordination/protocols/ticket_deep_dive.md` — EXISTS
- `AgentCoordination/SCRATCHPAD.md` — EXISTS
- `AgentCoordination/discovered_issues/README.md` — EXISTS
- `AgentCoordination/discovered_issues/log.jsonl` — EXISTS
- `AgentCoordination/generated/test_baseline.json` — EXISTS
- `AgentCoordination/generated/test_baseline/by_install/` — EXISTS
- `AgentCoordination/Scratchpad/` — EXISTS
- `AgentCoordination/legacy_tickets/` — EXISTS
- `Projects/active_projects/` — EXISTS
- `Projects/archived_projects/` — EXISTS
- `Projects/deep_archive/` — EXISTS
- `Reviews/protocols/` — EXISTS
- `Reviews/results/` — EXISTS
- `tracking-assets/projects/` — EXISTS
- `requirements-dev.txt` — EXISTS
- `requirements.txt` — EXISTS
- `conftest.py` — EXISTS
- `game/context.py` — EXISTS
- `.test_durations.json` — EXISTS
- No referenced command paths are broken.

### F8 [MAJOR] CLAUDE.md references directory marked for deletion
- **CLAUDE.md:5:** `For automated CLI loop execution, see retired loop systems at \`_marked_for_deletion_2026-05-29/Projects/\`.`
- **Status:** Directory `_marked_for_deletion_2026-05-29/` EXISTS on filesystem.
- **Deletion date:** 2026-05-29 (9 days from 2026-05-20).
- **Analysis:** This reference will become dead after 2026-05-29 when the directory is presumably deleted. The note describes "retired loop systems" — directing readers to a soon-to-be-deleted location is questionable.
- **Recommendation:** Remove this reference when the directory is deleted, or restructure to avoid directing agents to deprecated locations.

## Missing Documentation

The `undocumented_modules.json` scan covers production code modules not referenced in any doc. This is not directly applicable to the G4 agent docs, which are instruction files rather than code documentation. No modules are documented by these files (by design — they reference `docs/` for architecture).

## Cross-File Consistency Comparison

| Convention | AGENTS.md | CLAUDE.md | .agents/CODEX.md | docs/03_CONVENTIONS.md |
|---|---|---|---|---|
| Python version | 3.14 | 3.13+ | (not stated) | 3.13+ |
| LOC ceiling | "production files" | "under game/" | (not stated) | (varies by file) |
| Broad-except comment | "on the same line" | "on the same line or immediately above" | (not stated) | "on the same line" |
| TDD required | Yes | Yes | Yes (via AGENTS.md) | Yes |
| Read docs first | Yes | Yes (explicitly reinforces) | Yes (startup checklist) | N/A (it IS the doc) |
| Root cause fixes only | Yes | Yes (explicitly reinforces) | (via AGENTS.md) | Yes |
| No revert unrelated | Yes | Yes (explicitly reinforces) | Yes (startup checklist) | (via AGENTS.md) |
| Spatial terminology | Explicit definitions | Summarized | (not stated) | Present |
| Min resolution 2560x1600 | Yes | Yes | (not stated) | Yes |
| Skill-usage logging | Shared policy | Claude auto-log | Manual codex logging | N/A |
| Scratchpad policy | `AgentCoordination/Scratchpad/` | Same + `.agent_reports/` exception | (not stated) | N/A |

### Key Discrepancies
1. **Python version** (F3 above) — AGENTS.md out of sync with canonical conventions doc.
2. **Broad-except placement** (F5 above) — CLAUDE.md relaxes the rule.
3. **LOC ceiling scope** — AGENTS.md says "production files" while CLAUDE.md narrows to "under game/". The intent is likely the same (all production code lives under `game/`), but precision differs.

## Doc File Coverage Verification

| Doc File | Status | Findings |
|----------|--------|----------|
| `AGENTS.md` | Reviewed | F1 (dead ref), F3 (Python version), F5 (broad-except), F6 (no Last verified), F7 (all tools OK) |
| `CLAUDE.md` | Reviewed | F2 (dead ref), F3 (Python version), F4 (_ignore/ ref), F5 (broad-except), F6 (no Last verified), F8 (marked-for-deletion ref) |
| `.agents/CODEX.md` | Reviewed | F6 (no Last verified); no dead refs, no PROJ refs, no content issues found |
