"""Tests for Projects/scripts/phase_workflow/state.py."""
import json
import multiprocessing
import sys
from pathlib import Path

import pytest

PROJECTS_SCRIPTS = Path(__file__).parent.parent.parent.parent / "Projects" / "scripts"
sys.path.insert(0, str(PROJECTS_SCRIPTS))

from phase_workflow import state as state_mod


@pytest.fixture
def state_path(tmp_path):
    return tmp_path / "phase_state.json"


def test_initial_state_has_required_top_level_keys():
    s = state_mod.initial_state("PROJ-TEST-001")
    assert s["schema_version"] == 1
    assert s["project_id"] == "PROJ-TEST-001"
    assert s["execution_protocol"] == "03c-phase-aware-execution"
    assert s["project_branch"] == "proj/PROJ-TEST-001/main"
    assert s["buffer_depth"] == 0
    assert s["buffer_depth_override_reason"] is None
    assert s["phases"] == {}
    assert s["reviews"] == {}
    assert s["findings"] == {}
    assert s["audit"]["final_audit_status"] == "not_run"


def test_save_then_load_roundtrip(state_path):
    s = state_mod.initial_state("PROJ-TEST-001")
    state_mod.save_state(state_path, s)
    loaded = state_mod.load_state(state_path)
    assert loaded == s


def test_load_missing_file_raises(state_path):
    with pytest.raises(FileNotFoundError):
        state_mod.load_state(state_path)


def test_load_or_init_returns_initial_when_missing(state_path):
    s = state_mod.load_or_init(state_path, "PROJ-TEST-001")
    assert s["project_id"] == "PROJ-TEST-001"
    assert s["phases"] == {}


def test_load_or_init_returns_existing(state_path):
    s = state_mod.initial_state("PROJ-TEST-001")
    state_mod.add_phase(s, "phase_1", depends_on=[])
    state_mod.save_state(state_path, s)
    loaded = state_mod.load_or_init(state_path, "PROJ-TEST-001")
    assert "phase_1" in loaded["phases"]


def test_save_is_atomic_no_partial_file(state_path):
    s = state_mod.initial_state("PROJ-TEST-001")
    state_mod.save_state(state_path, s)
    assert state_path.exists()
    siblings = list(state_path.parent.iterdir())
    tmp_files = [p for p in siblings if p.name.startswith(".tmp_")]
    assert tmp_files == [], f"temp files left behind: {tmp_files}"


def test_add_phase_creates_default_phase_record():
    s = state_mod.initial_state("PROJ-TEST-001")
    state_mod.add_phase(s, "phase_1", depends_on=[], planned_files=["a.py"])
    p = s["phases"]["phase_1"]
    assert p["depends_on"] == []
    assert p["planned_files"] == ["a.py"]
    assert p["review_mode"] == "standard"
    assert p["status"] == "not_started"
    assert p["phase_branch"] is None
    assert p["phase_base_sha"] is None
    assert p["phase_head_sha"] is None
    assert p["review_dispatch_failed"] is False
    assert p["scrap_history"] == []


def test_add_phase_lightweight_review_mode():
    s = state_mod.initial_state("PROJ-TEST-001")
    state_mod.add_phase(s, "phase_1", depends_on=[], planned_files=[], review_mode="lightweight")
    assert s["phases"]["phase_1"]["review_mode"] == "lightweight"


def test_add_phase_rejects_invalid_review_mode():
    s = state_mod.initial_state("PROJ-TEST-001")
    with pytest.raises(ValueError, match="review_mode"):
        state_mod.add_phase(s, "phase_1", depends_on=[], planned_files=[], review_mode="skip")


def test_set_phase_status_valid_transitions():
    s = state_mod.initial_state("PROJ-TEST-001")
    state_mod.add_phase(s, "phase_1", depends_on=[])
    for status in ["in_progress", "committed", "under_review", "verified"]:
        state_mod.set_phase_status(s, "phase_1", status)
        assert s["phases"]["phase_1"]["status"] == status


def test_set_phase_status_rejects_unknown():
    s = state_mod.initial_state("PROJ-TEST-001")
    state_mod.add_phase(s, "phase_1", depends_on=[])
    with pytest.raises(ValueError, match="status"):
        state_mod.set_phase_status(s, "phase_1", "bogus")


def test_record_review_creates_review_entry():
    s = state_mod.initial_state("PROJ-TEST-001")
    state_mod.add_phase(s, "phase_1", depends_on=[])
    state_mod.record_review(
        s,
        review_id="req_test_001",
        project_tip_sha="abc123",
        coverage_set=["phase_1"],
        focus_phase="phase_1",
        review_mode="standard",
        dispatched_at_utc="2026-05-03T14:16:01Z",
    )
    r = s["reviews"]["req_test_001"]
    assert r["review_sequence"] == 1
    assert r["project_tip_sha"] == "abc123"
    assert r["coverage_set"] == ["phase_1"]
    assert r["result_status"] == "pending"
    assert r["supersedes"] == []
    assert r["superseded_by"] is None


def test_review_sequence_monotonically_increases():
    s = state_mod.initial_state("PROJ-TEST-001")
    state_mod.add_phase(s, "phase_1", depends_on=[])
    state_mod.add_phase(s, "phase_2", depends_on=["phase_1"])
    state_mod.record_review(
        s, "req_a", "sha_a", ["phase_1"], "phase_1", "standard", "2026-05-03T14:16:01Z"
    )
    state_mod.record_review(
        s, "req_b", "sha_b", ["phase_1", "phase_2"], "phase_2", "standard", "2026-05-03T14:20:00Z"
    )
    assert s["reviews"]["req_a"]["review_sequence"] == 1
    assert s["reviews"]["req_b"]["review_sequence"] == 2


def test_mark_review_completed_clean_verifies_phases_in_coverage():
    s = state_mod.initial_state("PROJ-TEST-001")
    state_mod.add_phase(s, "phase_1", depends_on=[])
    state_mod.add_phase(s, "phase_2", depends_on=["phase_1"])
    state_mod.set_phase_status(s, "phase_1", "committed")
    state_mod.set_phase_status(s, "phase_2", "committed")
    state_mod.record_review(
        s, "req_a", "sha_a", ["phase_1", "phase_2"], "phase_2", "standard", "2026-05-03T14:16:01Z"
    )
    state_mod.mark_review_result(s, "req_a", "completed_clean", result_path="Reviews/results/foo")
    assert s["reviews"]["req_a"]["result_status"] == "completed_clean"
    assert s["phases"]["phase_1"]["status"] == "verified"
    assert s["phases"]["phase_2"]["status"] == "verified"
    assert s["phases"]["phase_1"]["verifying_review_id"] == "req_a"
    assert s["phases"]["phase_2"]["verifying_review_id"] == "req_a"


def test_clean_review_supersedes_earlier_subset_reviews():
    s = state_mod.initial_state("PROJ-TEST-001")
    state_mod.add_phase(s, "phase_1", depends_on=[])
    state_mod.add_phase(s, "phase_2", depends_on=["phase_1"])
    state_mod.record_review(
        s, "req_a", "sha_a", ["phase_1"], "phase_1", "standard", "2026-05-03T14:16:01Z"
    )
    state_mod.mark_review_result(s, "req_a", "completed_clean")
    state_mod.record_review(
        s, "req_b", "sha_b", ["phase_1", "phase_2"], "phase_2", "standard", "2026-05-03T14:20:00Z"
    )
    state_mod.mark_review_result(s, "req_b", "completed_clean")
    # req_a's coverage_set is a strict subset of req_b's; req_a is superseded.
    assert s["reviews"]["req_a"]["superseded_by"] == "req_b"
    assert "req_a" in s["reviews"]["req_b"]["supersedes"]


def test_add_finding_default_status_open():
    s = state_mod.initial_state("PROJ-TEST-001")
    state_mod.add_phase(s, "phase_1", depends_on=[])
    state_mod.record_review(
        s, "req_a", "sha_a", ["phase_1"], "phase_1", "standard", "2026-05-03T14:16:01Z"
    )
    state_mod.add_finding(
        s,
        finding_id="FND-001",
        fingerprint="sha256:abc",
        source_review_id="req_a",
        source_phase="phase_1",
        severity="MAJ",
        summary="test finding",
    )
    f = s["findings"]["FND-001"]
    assert f["status"] == "open"
    assert f["fingerprint"] == "sha256:abc"
    assert f["source_review_id"] == "req_a"
    assert f["verifying_review_id"] is None
    assert f["deferred_until_phase"] is None


def test_set_finding_status_to_verified_requires_verifying_review():
    s = state_mod.initial_state("PROJ-TEST-001")
    state_mod.add_phase(s, "phase_1", depends_on=[])
    state_mod.record_review(
        s, "req_a", "sha_a", ["phase_1"], "phase_1", "standard", "2026-05-03T14:16:01Z"
    )
    state_mod.add_finding(
        s, "FND-001", "sha256:x", "req_a", "phase_1", "MAJ", "x"
    )
    with pytest.raises(ValueError, match="verifying_review_id"):
        state_mod.set_finding_status(s, "FND-001", "verified")
    state_mod.set_finding_status(s, "FND-001", "verified", verifying_review_id="req_b")
    assert s["findings"]["FND-001"]["status"] == "verified"
    assert s["findings"]["FND-001"]["verifying_review_id"] == "req_b"


def test_set_finding_status_deferred_requires_target_phase():
    s = state_mod.initial_state("PROJ-TEST-001")
    state_mod.add_phase(s, "phase_1", depends_on=[])
    state_mod.record_review(
        s, "req_a", "sha_a", ["phase_1"], "phase_1", "standard", "2026-05-03T14:16:01Z"
    )
    state_mod.add_finding(s, "FND-001", "sha256:x", "req_a", "phase_1", "MAJ", "x")
    with pytest.raises(ValueError, match="deferred_until_phase"):
        state_mod.set_finding_status(s, "FND-001", "deferred_until_phase")
    state_mod.set_finding_status(
        s, "FND-001", "deferred_until_phase", deferred_until_phase="phase_3"
    )
    assert s["findings"]["FND-001"]["deferred_until_phase"] == "phase_3"


def test_set_finding_status_wontfix_requires_rationale():
    s = state_mod.initial_state("PROJ-TEST-001")
    state_mod.add_phase(s, "phase_1", depends_on=[])
    state_mod.record_review(
        s, "req_a", "sha_a", ["phase_1"], "phase_1", "standard", "2026-05-03T14:16:01Z"
    )
    state_mod.add_finding(s, "FND-001", "sha256:x", "req_a", "phase_1", "MAJ", "x")
    with pytest.raises(ValueError, match="rationale"):
        state_mod.set_finding_status(s, "FND-001", "wontfix_with_rationale")
    state_mod.set_finding_status(
        s, "FND-001", "wontfix_with_rationale", rationale="out of scope"
    )
    assert s["findings"]["FND-001"]["rationale"] == "out of scope"


def test_set_buffer_depth_to_one_requires_reason():
    s = state_mod.initial_state("PROJ-TEST-001")
    with pytest.raises(ValueError, match="buffer_depth_override_reason"):
        state_mod.set_buffer_depth(s, 1)
    state_mod.set_buffer_depth(s, 1, reason="trusted code path with frequent rebases")
    assert s["buffer_depth"] == 1
    assert s["buffer_depth_override_reason"] == "trusted code path with frequent rebases"


def test_set_buffer_depth_invalid():
    s = state_mod.initial_state("PROJ-TEST-001")
    with pytest.raises(ValueError):
        state_mod.set_buffer_depth(s, 2)
    with pytest.raises(ValueError):
        state_mod.set_buffer_depth(s, -1)


def test_validate_state_rejects_wrong_schema_version():
    s = state_mod.initial_state("PROJ-TEST-001")
    s["schema_version"] = 999
    with pytest.raises(ValueError, match="schema_version"):
        state_mod.validate(s)


def test_load_invalid_json_raises(state_path):
    state_path.write_text("{not valid json}", encoding="utf-8")
    with pytest.raises(json.JSONDecodeError):
        state_mod.load_state(state_path)


def _writer(state_path_str, project_id, key_prefix, count):
    """Helper for concurrent-write test (must be top-level for pickling)."""
    sys.path.insert(0, str(Path(state_path_str).parent.parent.parent.parent / "Projects" / "scripts"))
    from phase_workflow import state as state_mod_inner
    state_path = Path(state_path_str)
    for i in range(count):
        with state_mod_inner.locked(state_path):
            s = state_mod_inner.load_or_init(state_path, project_id)
            state_mod_inner.add_phase(s, f"{key_prefix}_{i}", depends_on=[])
            state_mod_inner.save_state(state_path, s)


def test_concurrent_writes_do_not_lose_phases(state_path):
    """Two processes each adding 5 phases under the lock should yield 10 distinct phases."""
    procs = [
        multiprocessing.Process(target=_writer, args=(str(state_path), "PROJ-TEST-001", "a", 5)),
        multiprocessing.Process(target=_writer, args=(str(state_path), "PROJ-TEST-001", "b", 5)),
    ]
    for p in procs:
        p.start()
    for p in procs:
        p.join(timeout=30)
        assert p.exitcode == 0, f"writer crashed: {p.exitcode}"
    final = state_mod.load_state(state_path)
    assert len(final["phases"]) == 10
    assert set(final["phases"]) == {f"a_{i}" for i in range(5)} | {f"b_{i}" for i in range(5)}


def test_record_scrap_appends_history():
    s = state_mod.initial_state("PROJ-TEST-001")
    state_mod.add_phase(s, "phase_1", depends_on=[])
    state_mod.set_phase_status(s, "phase_1", "verified")
    state_mod.record_scrap(s, "phase_1", reason="parent remediation invalidated work")
    assert s["phases"]["phase_1"]["status"] == "not_started"
    assert s["phases"]["phase_1"]["phase_branch"] is None
    assert s["phases"]["phase_1"]["phase_head_sha"] is None
    assert s["phases"]["phase_1"]["verifying_review_id"] is None
    assert s["phases"]["phase_1"]["review_request_id"] is None
    assert len(s["phases"]["phase_1"]["scrap_history"]) == 1
    assert s["phases"]["phase_1"]["scrap_history"][0]["reason"] == "parent remediation invalidated work"
