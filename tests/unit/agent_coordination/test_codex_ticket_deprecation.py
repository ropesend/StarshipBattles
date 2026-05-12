from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
CODEX_DOC = REPO_ROOT / ".agents" / "CODEX.md"
CODEX_SKILLS = REPO_ROOT / ".agents" / "skills"
QA_OBSERVER_SKILL = CODEX_SKILLS / "codex-starship-qa-observer" / "SKILL.md"
TICKET_SKILL = CODEX_SKILLS / "codex-starship-ticket-system"


def test_codex_legacy_ticket_skill_is_retired() -> None:
    assert not TICKET_SKILL.exists()


def test_codex_adapter_points_ticket_work_to_github_issues() -> None:
    text = CODEX_DOC.read_text(encoding="utf-8")

    assert "codex-starship-ticket-system" not in text
    assert "Tracking/" not in text
    assert "GitHub Issues" in text
    assert "AgentCoordination/protocols/ticket_workflow.md" in text


def test_codex_qa_observer_deduplicates_against_github_issues() -> None:
    text = QA_OBSERVER_SKILL.read_text(encoding="utf-8")

    assert "Tracking/" not in text
    assert "AgentCoordination/protocols/ticket_workflow.md" in text
    assert 'gh issue list --state open --label "type:bug"' in text
    assert 'gh issue list --state open --label "type:feature"' in text
