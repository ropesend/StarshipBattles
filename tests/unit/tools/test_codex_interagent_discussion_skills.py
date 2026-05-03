from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SKILL_ROOT = ROOT / ".agents" / "skills"


def _read_skill(name: str) -> str:
    return (SKILL_ROOT / name / "SKILL.md").read_text(encoding="utf-8")


def test_codex_discussion_skills_exist_with_matching_frontmatter() -> None:
    expected = {
        "codex-discuss-start": "Start an inter-agent discussion with Claude Code",
        "codex-discuss-respond": "Respond in an inter-agent discussion with Claude Code",
    }

    for skill_name, description_fragment in expected.items():
        text = _read_skill(skill_name)

        assert text.startswith("---\n")
        assert f"name: {skill_name}\n" in text
        assert description_fragment in text


def test_codex_discussion_skills_document_shared_protocol() -> None:
    for skill_name in ("codex-discuss-start", "codex-discuss-respond"):
        text = _read_skill(skill_name)

        assert "interagent-discussion/v1" in text
        assert "001_codex_to_claude.md" in text
        assert "001_claude_to_codex.md" in text
        assert "010_" in text
        assert "message_index" in text
        assert "agent_turn" in text
        assert "status: continue" in text
        assert "continue | consensus | needs-user" in text
        assert "outcome.md" in text
        assert "temporary file" in text
        assert "heartbeat_codex.txt" in text
        assert "heartbeat_claude.txt" in text


def test_codex_discussion_skills_document_v2_refinements() -> None:
    for skill_name in ("codex-discuss-start", "codex-discuss-respond"):
        text = _read_skill(skill_name)

        assert "frontmatter on line 1" in text
        assert "User-supplied context" in text
        assert "topic.md" in text
        assert "plans/" in text
        assert "revision:" in text
        assert ".tmp_*" in text
        assert "extension_requested_cap: 20" in text
        assert "extension_accepted: true" in text
        assert "message_cap: 20" in text
        assert "Handover proposal" in text
        assert "user_facing_agent" in text


def test_codex_discussion_message_examples_put_frontmatter_first() -> None:
    for skill_name in ("codex-discuss-start", "codex-discuss-respond"):
        text = _read_skill(skill_name)

        assert "visible prefix" not in text
        assert "Codex message 001\n\n---" not in text
        assert "Codex message 002\n\n---" not in text
