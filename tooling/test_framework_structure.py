"""Validates the framework's own structure.

These are the tests that actually check Cato rather than checking Python. A
broken agent frontmatter, a reference to a file that was renamed, or a number
restated in two places are the failures that silently degrade the system — the
agents keep running, they just follow stale instructions.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLAUDE = ROOT / ".claude"
AGENTS = CLAUDE / "agents"

REQUIRED_FRONTMATTER = ("name", "description", "tools", "model")

ROSTER = {
    "strategist",
    "researcher",
    "architect",
    "designer",
    "implementer",
    "qa",
    "reviewer",
    "docs",
}


def _frontmatter(path: Path) -> dict[str, str]:
    """Parse the YAML-ish frontmatter block at the top of an agent file."""
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    assert match, f"{path.name} has no frontmatter block"

    fields = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            fields[key.strip()] = value.strip()
    return fields


def test_every_roster_agent_has_a_file():
    present = {p.stem for p in AGENTS.glob("*.md")}
    assert present == ROSTER, f"Roster mismatch: {present ^ ROSTER}"


def test_agent_frontmatter_is_complete():
    for path in AGENTS.glob("*.md"):
        fields = _frontmatter(path)
        for key in REQUIRED_FRONTMATTER:
            assert key in fields, f"{path.name} is missing '{key}' in frontmatter"
        assert fields["name"] == path.stem, (
            f"{path.name} declares name '{fields['name']}' — must match the filename"
        )


def test_agent_descriptions_say_when_to_use():
    """Claude Code routes on the description, so it has to be actionable."""
    for path in AGENTS.glob("*.md"):
        description = _frontmatter(path)["description"]
        assert len(description) > 40, f"{path.name} description is too thin to route on"


def test_internal_references_resolve():
    """Catches links to files that were renamed or moved."""
    referenced = re.compile(r"`([\w./-]+\.md)`")
    known_external = {"CLAUDE.md", "AGENTS.md", "README.md"}

    for path in list(CLAUDE.rglob("*.md")) + [ROOT / "CLAUDE.md", ROOT / "AGENTS.md"]:
        for name in referenced.findall(path.read_text(encoding="utf-8")):
            candidates = [
                ROOT / name,
                CLAUDE / name,
                path.parent / name,
            ]
            if name in known_external or any(c.exists() for c in candidates):
                continue
            # Files a project creates as it goes, absent in the blank template.
            generated = (
                "specs/", "memory/adr/", "0001", "0000", "CHANGELOG.md",
                "memory/run-NN-notes.md", "memory/runs.md",  # written by /close-run
            )
            if any(part in name for part in generated):
                continue
            raise AssertionError(f"{path.name} references missing file: {name}")


def test_tuneable_numbers_live_only_in_config():
    """config.md is the single source of truth for anything adjustable.

    If a threshold gets restated elsewhere, calibration updates one copy and the
    others quietly disagree.
    """
    config = CLAUDE / "config.md"
    assert config.exists()

    # Files allowed to mention numbers: config itself, and prose that explains
    # the calibration process without asserting values.
    exempt = {"config.md", "calibrate.md"}

    offenders = []
    for path in CLAUDE.rglob("*.md"):
        if path.name in exempt:
            continue
        text = path.read_text(encoding="utf-8")
        for pattern in (r"\b70%", r"\b2/5/8\b", r"max(?:imum)? 5 iterations"):
            if re.search(pattern, text, re.IGNORECASE):
                offenders.append(f"{path.name} restates a config value ({pattern})")
    assert not offenders, "; ".join(offenders)


def test_minimalism_ladder_is_not_duplicated():
    """The ladder lives in one file; everything else points at it.

    AGENTS.md is the one accepted exception: hosts reading it have no access to
    .claude/, so it carries a standalone copy. Anything beyond those two — the
    README, the docs, another agent — is drift waiting to happen.
    """
    ladder_marker = "Does this need to exist?"
    searched = (
        list(CLAUDE.rglob("*.md"))
        + list((ROOT / "docs").glob("*.md"))
        + [ROOT / "AGENTS.md", ROOT / "README.md"]
    )
    holders = [
        p.name for p in searched if ladder_marker in p.read_text(encoding="utf-8")
    ]
    assert set(holders) <= {"minimalism-ladder.md", "AGENTS.md"}, (
        f"Ladder duplicated in: {holders}"
    )


def test_agents_that_own_files_have_write_tools():
    """Frontmatter tools must match write responsibilities (audit failure mode)."""
    must_write = {
        "architect": "Write",
        "strategist": "Write",
        "designer": "Write",
        "implementer": "Write",
        "docs": "Write",
    }
    for name, tool in must_write.items():
        fields = _frontmatter(AGENTS / f"{name}.md")
        tools = fields.get("tools", "")
        assert tool in tools, f"{name}.md must include {tool} in tools (got {tools!r})"

    reviewer_tools = _frontmatter(AGENTS / "reviewer.md")["tools"]
    assert "Bash" in reviewer_tools, "reviewer needs Bash for git diff"


def test_docs_exist_and_are_linked():
    """Documentation that nothing points at doesn't get read."""
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for doc in (
        "docs/CONCEPTS.md",
        "docs/FIRST-PROJECT.md",
        "docs/VALIDATION.md",
        "docs/EVALS.md",
        "docs/POSITIONING.md",
    ):
        assert (ROOT / doc).exists(), f"Missing {doc}"
        assert doc in readme, f"README doesn't link {doc}"


def test_hard_rules_contain_no_tuneable_numbers():
    """rules-hard.md is constraints only — if it has knobs, the split failed."""
    text = (CLAUDE / "rules-hard.md").read_text(encoding="utf-8")
    assert not re.search(r"\b\d+%", text), "rules-hard.md contains a percentage threshold"


def test_claude_md_imports_the_split_rule_files():
    text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    for expected in ("rules-hard.md", "config.md", "process.md"):
        assert expected in text, f"CLAUDE.md doesn't import {expected}"
