"""Tests for Projects/scripts/phase_workflow/reviews.py."""
import sys
from pathlib import Path

import pytest

PROJECTS_SCRIPTS = Path(__file__).parent.parent.parent.parent / "Projects" / "scripts"
sys.path.insert(0, str(PROJECTS_SCRIPTS))

from phase_workflow import state as state_mod
from phase_workflow import reviews as reviews_mod


def _basic_state(focus="phase_1"):
    s = state_mod.initial_state("PROJ-TEST-001")
    state_mod.add_phase(s, "phase_1", depends_on=[], planned_files=["game/foo.py"])
    state_mod.add_phase(s, "phase_2", depends_on=["phase_1"], planned_files=["game/bar.py"])
    state_mod.set_phase_status(s, "phase_1", "verified")
    state_mod.set_phase_status(s, "phase_2", "committed")
    state_mod.set_phase_branch(s, "phase_2", phase_branch="proj/PROJ-TEST-001/phase_2", phase_base_sha="abc")
    state_mod.set_phase_head_sha(s, "phase_2", "def")
    return s


def test_payload_top_level_fields():
    s = _basic_state()
    payload = reviews_mod.build_payload(
        s,
        focus_phase="phase_2",
        project_tip_sha="def",
        files_newly_changed=["game/bar.py"],
        files_in_earlier_phases=["game/foo.py"],
        worktree_path_for_review="AgentCoordination/opencodereview/local/worktrees/req_X",
    )
    assert payload["type"] == "code"
    assert payload["requester"] == "claude-code"
    assert "title" in payload and "PROJ-TEST-001" in payload["title"]
    assert "phase_2" in payload["title"]


def test_payload_includes_checkout_block_with_sha_pin():
    s = _basic_state()
    payload = reviews_mod.build_payload(
        s,
        focus_phase="phase_2",
        project_tip_sha="def0123",
        files_newly_changed=["game/bar.py"],
        files_in_earlier_phases=[],
        worktree_path_for_review="AgentCoordination/opencodereview/local/worktrees/req_X",
    )
    co = payload["checkout"]
    assert co["mode"] == "detached_worktree"
    assert co["ref"] == "proj/PROJ-TEST-001/main"
    assert co["sha"] == "def0123"
    assert co["worktree_path"] == "AgentCoordination/opencodereview/local/worktrees/req_X"


def test_payload_includes_coverage_block():
    s = _basic_state()
    payload = reviews_mod.build_payload(
        s,
        focus_phase="phase_2",
        project_tip_sha="def",
        files_newly_changed=["game/bar.py"],
        files_in_earlier_phases=["game/foo.py"],
        worktree_path_for_review="wt_path",
    )
    cov = payload["coverage"]
    assert cov["project_id"] == "PROJ-TEST-001"
    assert cov["focus_phase"] == "phase_2"
    assert cov["project_tip_sha"] == "def"
    assert set(cov["coverage_set"]) == {"phase_1", "phase_2"}
    assert isinstance(cov["review_sequence"], int)
    assert cov["review_sequence"] >= 1


def test_payload_scope_separates_new_and_context():
    s = _basic_state()
    payload = reviews_mod.build_payload(
        s,
        focus_phase="phase_2",
        project_tip_sha="def",
        files_newly_changed=["game/bar.py", "tests/unit/test_bar.py"],
        files_in_earlier_phases=["game/foo.py"],
        worktree_path_for_review="wt_path",
    )
    scope = payload["scope"]
    assert "phase_2" in scope or "Phase 2" in scope or "newly" in scope.lower()
    assert "game/bar.py" in scope
    assert "game/foo.py" in scope


def test_payload_instructions_reference_findings_ledger():
    s = _basic_state()
    state_mod.record_review(
        s, "req_old", "old_sha", ["phase_1"], "phase_1", "standard", "2026-05-03T14:00:00Z"
    )
    state_mod.add_finding(s, "FND-001", "fp1", "req_old", "phase_1", "MIN", "old finding")
    state_mod.set_finding_status(
        s, "FND-001", "wontfix_with_rationale", rationale="Out of scope per decisions.md L42"
    )
    payload = reviews_mod.build_payload(
        s,
        focus_phase="phase_2",
        project_tip_sha="def",
        files_newly_changed=["game/bar.py"],
        files_in_earlier_phases=["game/foo.py"],
        worktree_path_for_review="wt_path",
    )
    instructions = payload["instructions"]
    assert "FND-001" in instructions or "findings_ledger" in instructions.lower()
    assert "wontfix" in instructions.lower() or "acknowledged" in instructions.lower() or "skip" in instructions.lower()


def test_payload_lightweight_review_mode_reflected():
    s = _basic_state()
    s["phases"]["phase_2"]["review_mode"] = "lightweight"
    payload = reviews_mod.build_payload(
        s,
        focus_phase="phase_2",
        project_tip_sha="def",
        files_newly_changed=["game/bar.py"],
        files_in_earlier_phases=[],
        worktree_path_for_review="wt_path",
    )
    assert payload["coverage"]["review_mode"] == "lightweight"
    # Lightweight mode should hint at lighter-touch review in the instructions.
    assert "lightweight" in payload["instructions"].lower()


def test_payload_unknown_focus_phase_raises():
    s = _basic_state()
    with pytest.raises(KeyError):
        reviews_mod.build_payload(
            s,
            focus_phase="phase_99",
            project_tip_sha="def",
            files_newly_changed=[],
            files_in_earlier_phases=[],
            worktree_path_for_review="wt_path",
        )


def test_payload_empty_newly_changed_is_legal_for_remediation():
    """Remediation reviews may have no new files (just verifying earlier work)."""
    s = _basic_state()
    payload = reviews_mod.build_payload(
        s,
        focus_phase="phase_2",
        project_tip_sha="def",
        files_newly_changed=[],
        files_in_earlier_phases=["game/foo.py", "game/bar.py"],
        worktree_path_for_review="wt_path",
    )
    assert "game/foo.py" in payload["scope"]


def test_compute_files_changed_between_split_into_new_and_context(tmp_path):
    """Helper that, given a phase head SHA and the project tip SHA, splits
    files into 'newly changed in focus phase' vs 'changed in earlier phases'."""
    # This needs a real git repo to exercise; use the same fixture style as git_ops tests.
    import subprocess

    def run(args, cwd):
        subprocess.run(args, cwd=str(cwd), check=True, capture_output=True, text=True)

    repo = tmp_path / "repo"
    repo.mkdir()
    run(["git", "init", "-b", "main"], repo)
    run(["git", "config", "user.email", "t@t"], repo)
    run(["git", "config", "user.name", "T"], repo)
    (repo / "README.md").write_text("init", encoding="utf-8")
    run(["git", "add", "."], repo)
    run(["git", "commit", "-m", "init"], repo)
    base_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=str(repo), capture_output=True, text=True
    ).stdout.strip()

    # Phase 1 commits
    (repo / "phase1.py").write_text("p1", encoding="utf-8")
    run(["git", "add", "."], repo)
    run(["git", "commit", "-m", "phase 1"], repo)
    phase1_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=str(repo), capture_output=True, text=True
    ).stdout.strip()

    # Phase 2 commits
    (repo / "phase2.py").write_text("p2", encoding="utf-8")
    (repo / "phase2_test.py").write_text("p2t", encoding="utf-8")
    run(["git", "add", "."], repo)
    run(["git", "commit", "-m", "phase 2"], repo)
    phase2_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=str(repo), capture_output=True, text=True
    ).stdout.strip()

    new, context = reviews_mod.compute_files_changed_between(
        repo, focus_base_sha=phase1_sha, focus_head_sha=phase2_sha, project_root_sha=base_sha
    )
    assert set(new) == {"phase2.py", "phase2_test.py"}
    assert set(context) == {"phase1.py"}
