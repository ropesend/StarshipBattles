"""Build SHA-pinned cumulative review payloads for the OpenCode daemon.

A v1 03c payload extends the baseline review payload with two new blocks:

    {
      "type": "code",
      "title": "...",
      "scope": "...",
      "instructions": "...",
      "checkout": {
        "mode": "detached_worktree",
        "ref": "<project_branch>",
        "sha": "<project_tip_sha>",
        "worktree_path": "AgentCoordination/opencodereview/local/worktrees/<request_id>"
      },
      "coverage": {
        "project_id": "PROJ-XX",
        "review_sequence": <n>,
        "project_tip_sha": "<sha>",
        "coverage_set": ["phase_1", ...],
        "focus_phase": "phase_n",
        "review_mode": "standard"
      },
      "requester": "claude-code"
    }
"""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from . import dag as dag_mod


def build_payload(
    state: dict[str, Any],
    *,
    focus_phase: str,
    project_tip_sha: str,
    files_newly_changed: list[str],
    files_in_earlier_phases: list[str],
    worktree_path_for_review: str,
    extra_instructions: str | None = None,
) -> dict[str, Any]:
    """Render a complete review payload for `focus_phase` at `project_tip_sha`."""
    if focus_phase not in state["phases"]:
        raise KeyError(f"unknown focus_phase: {focus_phase!r}")

    coverage = dag_mod.coverage_set(state, focus_phase=focus_phase)
    project_id = state["project_id"]
    project_branch = state["project_branch"]
    review_mode = state["phases"][focus_phase]["review_mode"]
    sequence = len(state["reviews"]) + 1

    title = (
        f"{project_id} cumulative review "
        f"(focus: {focus_phase}, coverage: {len(coverage)} phases)"
    )

    scope_lines = [
        f"## Scope\n",
        f"**Cumulative review through {focus_phase}.**",
        f"Project branch: `{project_branch}` at SHA `{project_tip_sha}`.",
        "",
    ]
    if files_newly_changed:
        scope_lines.append(f"Files newly changed in {focus_phase} (focus area):")
        for f in files_newly_changed:
            scope_lines.append(f"- `{f}`")
        scope_lines.append("")
    if files_in_earlier_phases:
        scope_lines.append("Files changed in earlier phases (context, already partially reviewed):")
        for f in files_in_earlier_phases:
            scope_lines.append(f"- `{f}`")
        scope_lines.append("")
    scope = "\n".join(scope_lines)

    instructions = _render_instructions(state, focus_phase, review_mode, extra_instructions)

    return {
        "type": "code",
        "title": title,
        "scope": scope,
        "instructions": instructions,
        "checkout": {
            "mode": "detached_worktree",
            "ref": project_branch,
            "sha": project_tip_sha,
            "worktree_path": worktree_path_for_review,
        },
        "coverage": {
            "project_id": project_id,
            "review_sequence": sequence,
            "project_tip_sha": project_tip_sha,
            "coverage_set": coverage,
            "focus_phase": focus_phase,
            "review_mode": review_mode,
        },
        "requester": "claude-code",
    }


def _render_instructions(
    state: dict[str, Any],
    focus_phase: str,
    review_mode: str,
    extra: str | None,
) -> str:
    lines = ["## Instructions", ""]
    if review_mode == "lightweight":
        lines += [
            "**Review mode: lightweight.** Phase scope is small (≤ 1 production",
            "file or trivial change). Focus on:",
            "- correctness of the change itself,",
            "- regression risk vs earlier phases,",
            "- nothing else.",
            "Do not produce stylistic / refactoring findings unless they directly",
            "affect correctness.",
            "",
        ]
    else:
        lines += [
            "Focus your scrutiny on the 'newly changed in focus phase' file list.",
            "Re-check earlier phases only for: (a) integration issues with the",
            "focus phase's changes, (b) regressions, (c) findings from prior",
            "reviews that may have been reintroduced.",
            "",
        ]

    # Ledger-aware skip list.
    skip_findings = _findings_to_skip(state)
    if skip_findings:
        lines.append("**Findings already triaged in this project — DO NOT re-raise:**")
        for f in skip_findings:
            lines.append(
                f"- `{f['id']}` ({f['status']}): {f['summary']} — rationale: {f['rationale'] or '—'}"
            )
        lines.append("")

    # Resurfacing rule for deferred-until-phase findings.
    resurface = _findings_to_resurface(state, focus_phase)
    if resurface:
        lines.append("**Findings deferred to this phase — please verify whether they are now resolved:**")
        for f in resurface:
            lines.append(f"- `{f['id']}`: {f['summary']} (deferred to {f['target']})")
        lines.append("")

    if extra:
        lines.append(extra.rstrip())
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def _findings_to_skip(state: dict[str, Any]) -> list[dict[str, Any]]:
    skip_statuses = {"acknowledged-deferred", "wontfix_with_rationale"}
    out = []
    for fid, f in state["findings"].items():
        if f["status"] in skip_statuses:
            out.append(
                {
                    "id": fid,
                    "status": f["status"],
                    "summary": f["summary"],
                    "rationale": f.get("rationale"),
                }
            )
    return out


def _findings_to_resurface(state: dict[str, Any], focus_phase: str) -> list[dict[str, Any]]:
    """Findings with status=deferred_until_phase whose target is reached."""
    # Compute coverage set of phases at-or-before the focus phase (committed or beyond).
    covered = set(dag_mod.coverage_set(state, focus_phase=focus_phase))
    out = []
    for fid, f in state["findings"].items():
        if f["status"] != "deferred_until_phase":
            continue
        target = f.get("deferred_until_phase")
        if target and target in covered:
            out.append({"id": fid, "summary": f["summary"], "target": target})
    return out


# ---------------------------------------------------------------------------
# Diff helpers
# ---------------------------------------------------------------------------


def compute_files_changed_between(
    repo: Path,
    *,
    focus_base_sha: str,
    focus_head_sha: str,
    project_root_sha: str,
) -> tuple[list[str], list[str]]:
    """Split files into (newly changed in focus phase, changed in earlier phases).

    'Newly changed' = files touched between focus_base_sha and focus_head_sha.
    'Earlier phases' = files touched between project_root_sha and focus_base_sha.
    """
    new = _diff_names(repo, focus_base_sha, focus_head_sha)
    earlier = _diff_names(repo, project_root_sha, focus_base_sha)
    earlier_only = sorted(set(earlier) - set(new))
    return sorted(new), earlier_only


def _diff_names(repo: Path, a: str, b: str) -> list[str]:
    if a == b:
        return []
    res = subprocess.run(
        ["git", "diff", "--name-only", f"{a}..{b}"],
        cwd=str(repo),
        check=True,
        capture_output=True,
        text=True,
        shell=False,
    )
    return [line for line in res.stdout.splitlines() if line.strip()]
