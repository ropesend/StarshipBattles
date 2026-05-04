from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SKILL_ROOT = REPO_ROOT / ".agents" / "skills"
SPEC_REF = "AgentCoordination/protocols/interagent_discussion.md"


def _skill_text(skill_name: str) -> str:
    return (SKILL_ROOT / skill_name / "SKILL.md").read_text(encoding="utf-8")


def test_codex_discussion_skills_reference_v26_contract() -> None:
    for skill_name in (
        "codex-discuss-start",
        "codex-discuss-respond",
        "codex-discuss-continue",
    ):
        text = _skill_text(skill_name)

        assert SPEC_REF in text
        assert "v2.3_spec_r001.md" not in text
        assert "(claude|codex|opencode)" in text
        assert "participants" in text
        assert "turn_order" in text
        assert "opencode" in text
        assert "implementation_owners" in text
        assert "continuation_starter" in text
        assert "5 * n" in text
        assert "10 * n" in text
        assert "protocol_version: 2.6" in text
        assert "same-directory" in text
        assert "complete: true" in text
        assert "mandatory observer" in text.lower()


def test_codex_discussion_skill_modes_cover_v26_control_flow() -> None:
    start = _skill_text("codex-discuss-start")
    respond = _skill_text("codex-discuss-respond")
    continue_skill = _skill_text("codex-discuss-continue")

    assert (
        "Argument surface: `[--folder <parent>] [--slug <slug>] "
        "[--with <agents>] [context...]`"
    ) in start
    assert "## Turn topology" in start
    assert "Turn order: codex ->" in start

    assert "Parent-Folder Discovery" in respond
    assert "P[i_in mod n] == codex" in respond
    assert "latest non-temp message" in respond
    assert "outcome.md` exists" in respond

    assert "continuation_starter == codex" in continue_skill
    assert "outcome_arc<NN>.md" in continue_skill
    assert "arc-N to arc-(N+1)" in continue_skill
