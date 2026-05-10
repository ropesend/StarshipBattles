"""Tests for Projects/scripts/phase_workflow/manifests.py."""
import subprocess
import sys
from pathlib import Path

import pytest

PROJECTS_SCRIPTS = Path(__file__).parent.parent.parent.parent / "Projects" / "scripts"
sys.path.insert(0, str(PROJECTS_SCRIPTS))

from phase_workflow import state as state_mod
from phase_workflow import manifests as manifests_mod


def _run(args, cwd):
    return subprocess.run(args, cwd=str(cwd), check=True, capture_output=True, text=True)


def _commit(repo, name, content="x"):
    target = repo / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    _run(["git", "add", name], repo)
    _run(["git", "commit", "-m", f"add {name}"], repo)


@pytest.fixture
def repo(tmp_path):
    r = tmp_path / "repo"
    r.mkdir()
    _run(["git", "init", "-b", "main"], r)
    _run(["git", "config", "user.email", "t@t"], r)
    _run(["git", "config", "user.name", "T"], r)
    _commit(r, "README.md", "initial")
    return r


def _sha(repo, ref="HEAD"):
    return subprocess.run(
        ["git", "rev-parse", ref], cwd=str(repo), capture_output=True, text=True
    ).stdout.strip()


def test_phase_files_changed_returns_diff(repo):
    base = _sha(repo)
    _commit(repo, "feature.py")
    _commit(repo, "tests/test_feature.py")
    head = _sha(repo)
    files = manifests_mod.phase_files_changed(repo, base, head)
    assert "feature.py" in files
    assert "tests/test_feature.py" in files


def test_phase_files_changed_empty_when_no_diff(repo):
    base = _sha(repo)
    files = manifests_mod.phase_files_changed(repo, base, base)
    assert files == []


def test_render_manifest_empty_state():
    s = state_mod.initial_state("PROJ-TEST-001")
    text = manifests_mod.render_manifest(s, repo_root=None)
    # Empty: still has a header, no rows.
    assert "PROJ-TEST-001" in text
    assert "## Files by phase" in text or "## Manifest" in text


def test_render_manifest_skips_uncommitted_phases():
    s = state_mod.initial_state("PROJ-TEST-001")
    state_mod.add_phase(s, "phase_1", depends_on=[])
    # phase_1 has no SHAs yet.
    text = manifests_mod.render_manifest(s, repo_root=None)
    assert "phase_1" not in text or "(not yet committed)" in text


def test_render_manifest_includes_committed_phase(repo):
    base = _sha(repo)
    _commit(repo, "alpha.py")
    head = _sha(repo)

    s = state_mod.initial_state("PROJ-TEST-001")
    state_mod.add_phase(s, "phase_1", depends_on=[])
    state_mod.set_phase_branch(s, "phase_1", phase_branch="proj/PROJ-TEST-001/phase_1", phase_base_sha=base)
    state_mod.set_phase_head_sha(s, "phase_1", head)
    state_mod.set_phase_status(s, "phase_1", "committed")

    text = manifests_mod.render_manifest(s, repo_root=repo)
    assert "phase_1" in text
    assert "alpha.py" in text


def test_render_manifest_groups_multiple_phases(repo):
    base = _sha(repo)
    _commit(repo, "a.py")
    a_sha = _sha(repo)
    _commit(repo, "b.py")
    b_sha = _sha(repo)

    s = state_mod.initial_state("PROJ-TEST-001")
    state_mod.add_phase(s, "phase_1", depends_on=[])
    state_mod.set_phase_branch(s, "phase_1", phase_branch="proj/PROJ-TEST-001/phase_1", phase_base_sha=base)
    state_mod.set_phase_head_sha(s, "phase_1", a_sha)
    state_mod.set_phase_status(s, "phase_1", "verified")

    state_mod.add_phase(s, "phase_2", depends_on=["phase_1"])
    state_mod.set_phase_branch(s, "phase_2", phase_branch="proj/PROJ-TEST-001/phase_2", phase_base_sha=a_sha)
    state_mod.set_phase_head_sha(s, "phase_2", b_sha)
    state_mod.set_phase_status(s, "phase_2", "committed")

    text = manifests_mod.render_manifest(s, repo_root=repo)
    assert "phase_1" in text
    assert "a.py" in text
    assert "phase_2" in text
    assert "b.py" in text
    # Phases listed in order.
    assert text.index("phase_1") < text.index("phase_2")


def test_write_manifest_atomic(tmp_path, repo):
    out = tmp_path / "manifest.md"
    s = state_mod.initial_state("PROJ-TEST-001")
    manifests_mod.write_manifest(s, repo_root=repo, output_path=out)
    assert out.exists()
    siblings = list(out.parent.iterdir())
    tmps = [p for p in siblings if p.name.startswith(".tmp_")]
    assert tmps == []


def test_write_manifest_overwrites(tmp_path, repo):
    out = tmp_path / "manifest.md"
    out.write_text("OLD CONTENT", encoding="utf-8")
    s = state_mod.initial_state("PROJ-TEST-001")
    manifests_mod.write_manifest(s, repo_root=repo, output_path=out)
    text = out.read_text(encoding="utf-8")
    assert "OLD CONTENT" not in text
    assert "PROJ-TEST-001" in text
