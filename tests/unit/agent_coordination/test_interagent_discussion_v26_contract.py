from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SPEC_PATH = REPO_ROOT / "AgentCoordination" / "protocols" / "interagent_discussion.md"

SKILL_PATHS = (
    REPO_ROOT / ".agents" / "skills" / "codex-discuss-start" / "SKILL.md",
    REPO_ROOT / ".agents" / "skills" / "codex-discuss-respond" / "SKILL.md",
    REPO_ROOT / ".agents" / "skills" / "codex-discuss-continue" / "SKILL.md",
    REPO_ROOT / ".claude" / "skills" / "claude-discuss-start" / "SKILL.md",
    REPO_ROOT / ".claude" / "skills" / "claude-discuss-respond" / "SKILL.md",
    REPO_ROOT / ".claude" / "skills" / "claude-discuss-continue" / "SKILL.md",
    REPO_ROOT / ".opencode" / "skills" / "ocode-discuss-start" / "SKILL.md",
    REPO_ROOT / ".opencode" / "skills" / "ocode-discuss-respond" / "SKILL.md",
    REPO_ROOT / ".opencode" / "skills" / "ocode-discuss-continue" / "SKILL.md",
)

REPLY_CAPABLE_SKILLS = tuple(
    path for path in SKILL_PATHS if "respond" in path.parts[-2] or "continue" in path.parts[-2]
)

OPENCODE_SKILLS = tuple(path for path in SKILL_PATHS if ".opencode" in path.parts)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_shared_spec_documents_v26_atomicity_receipts_and_liveness() -> None:
    text = _read(SPEC_PATH)

    assert "protocol_version: 2.6" in text
    assert "same-directory `.tmp_*`" in text
    assert "message files" in text
    assert "plan revisions" in text
    assert "outcome files" in text
    assert "ack sidecar files" in text
    assert "Direct writes to final protocol filenames are invalid" in text
    assert "complete: true" in text
    assert "warn" in text.lower()
    assert "proceed" in text.lower()
    assert "ack_arc<NN>_<MMM>_<from>_to_<to>_<acker>.md" in text
    assert "Observer acks are mandatory" in text
    assert "all participants other than the message author" in text
    assert "state: polling | reading | drafting | idle" in text
    assert "last_seen_message" in text


def test_all_discussion_skills_reference_v26_contract() -> None:
    for skill_path in SKILL_PATHS:
        text = _read(skill_path)

        assert "v2.6" in text, skill_path
        assert "AgentCoordination/protocols/interagent_discussion.md" in text, skill_path
        assert "same-directory" in text, skill_path
        assert ".tmp_*" in text, skill_path
        assert "complete: true" in text, skill_path
        assert "ack_arc<NN>_<MMM>_<from>_to_<to>_<acker>.md" in text, skill_path


def test_reply_capable_skills_document_mandatory_observer_acks() -> None:
    for skill_path in REPLY_CAPABLE_SKILLS:
        text = _read(skill_path)
        lowered = text.lower()

        assert "mandatory observer" in lowered, skill_path
        assert "before drafting" in lowered, skill_path
        assert "message_index" in text, skill_path
        assert "cap" in lowered, skill_path
        assert "consensus" in lowered, skill_path
        assert "state: polling | reading | drafting | idle" in text, skill_path


def test_opencode_discussion_skills_remove_direct_write_allowances() -> None:
    forbidden_fragments = (
        "write tool directly",
        "atomic enough",
        "single-writer-per-index",
        "(or `write` tool)",
        "or use the `write` tool",
        "or `write` tool",
        "/dev/urandom",
    )

    for skill_path in OPENCODE_SKILLS:
        text = _read(skill_path)
        lowered = text.lower()

        for fragment in forbidden_fragments:
            assert fragment.lower() not in lowered, (skill_path, fragment)
        assert "guid" in lowered or "mktemp" in lowered, skill_path
