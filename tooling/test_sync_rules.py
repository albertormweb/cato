"""Guards against the portable ruleset copies drifting out of sync.

Several hosts read rules from their own path, so the same text lives in several
files. Without this test, a change to AGENTS.md silently leaves the others stale.
"""

from sync_rules import COPIES, SOURCE, stale


def test_source_ruleset_exists():
    assert SOURCE.exists(), "AGENTS.md is the source of truth for portable rules"


def test_all_copies_match_source():
    drifted = stale()
    assert not drifted, (
        "Stale ruleset copies: "
        + ", ".join(str(p.name) for _, p in drifted)
        + ". Run: python tooling/sync_rules.py --fix"
    )


def test_every_declared_copy_is_present():
    for host, path in COPIES.items():
        assert path.exists(), f"Missing ruleset copy for {host}: {path}"
