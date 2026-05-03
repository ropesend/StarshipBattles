"""Phase / global manifest rendering from phase_state.json + git history.

The global `manifest.md` for a 03c project is regenerated from the SHAs
stored in `phase_state.json`. There is no per-phase manifest.md fragment —
the source of truth is the JSON state, the markdown is a generated view.
"""
from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path
from typing import Any


def phase_files_changed(repo: Path, base_sha: str, head_sha: str) -> list[str]:
    """List files changed between two SHAs. Empty if base_sha == head_sha."""
    if base_sha == head_sha:
        return []
    res = subprocess.run(
        ["git", "diff", "--name-only", f"{base_sha}..{head_sha}"],
        cwd=str(repo),
        check=True,
        capture_output=True,
        text=True,
        shell=False,
    )
    return [line for line in res.stdout.splitlines() if line.strip()]


def render_manifest(state: dict[str, Any], *, repo_root: Path | None) -> str:
    """Render `manifest.md` content for a 03c project.

    For each phase that has both `phase_base_sha` and `phase_head_sha` set,
    list the files changed between those SHAs (which may differ from
    `planned_files` in state).

    `repo_root` may be None when no committed phases exist yet (no git diff
    needed).
    """
    project_id = state["project_id"]
    lines: list[str] = []
    lines.append(f"# {project_id} — File Manifest")
    lines.append("")
    lines.append(
        "Generated from `phase_state.json` and git history. "
        "Do not edit by hand; re-run `manifests.py` (or `phase_complete.py`) "
        "to regenerate."
    )
    lines.append("")
    lines.append("## Files by phase")
    lines.append("")

    # Order phases by topological-ish status: committed/verified first, then planning order.
    ordered = sorted(state["phases"].items(), key=lambda kv: kv[0])

    any_rendered = False
    for phase_id, phase in ordered:
        base = phase.get("phase_base_sha")
        head = phase.get("phase_head_sha")
        if not (base and head and repo_root):
            # Phase has no commit yet — surface its planned_files so
            # readers see the intent before work lands.
            if phase.get("planned_files"):
                any_rendered = True
                lines.append(f"### `{phase_id}` (status: {phase['status']}) — planned only")
                lines.append("")
                for f in phase["planned_files"]:
                    lines.append(f"- `{f}`")
                lines.append("")
            continue
        files = phase_files_changed(repo_root, base, head)
        if not files:
            continue
        any_rendered = True
        lines.append(
            f"### `{phase_id}` (status: {phase['status']}, base `{base[:8]}` → head `{head[:8]}`)"
        )
        lines.append("")
        for f in files:
            lines.append(f"- `{f}`")
        lines.append("")

    if not any_rendered:
        lines.append("_No phases with committed work yet._")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def write_manifest(
    state: dict[str, Any],
    *,
    repo_root: Path | None,
    output_path: Path,
) -> None:
    """Atomically write the rendered manifest to `output_path`."""
    text = render_manifest(state, repo_root=repo_root)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = output_path.with_name(f".tmp_{os.getpid()}_{time.time_ns()}_{output_path.name}")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, output_path)
