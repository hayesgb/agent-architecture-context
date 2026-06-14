"""S-004: All markdown files under architecture/, repo-standards/, agent-guidelines/ have required frontmatter."""
import os
import glob
import yaml
import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CONTENT_DIRS = ["architecture", "repo-standards", "agent-guidelines"]
REQUIRED_FIELDS = ["status", "last_updated"]


def _parse_frontmatter(filepath):
    with open(filepath) as f:
        content = f.read()
    if not content.startswith("---"):
        return None
    parts = content.split("---", 2)
    if len(parts) < 3:
        return None
    return yaml.safe_load(parts[1])


def _all_content_md_files():
    files = []
    for d in CONTENT_DIRS:
        pattern = os.path.join(REPO_ROOT, d, "**", "*.md")
        files.extend(glob.glob(pattern, recursive=True))
    return [os.path.relpath(f, REPO_ROOT) for f in files]


@pytest.mark.parametrize("rel_path", _all_content_md_files())
def test_content_file_has_frontmatter(rel_path):
    filepath = os.path.join(REPO_ROOT, rel_path)
    fm = _parse_frontmatter(filepath)
    assert fm is not None, f"{rel_path}: missing or unparseable YAML frontmatter"


@pytest.mark.parametrize("rel_path", _all_content_md_files())
@pytest.mark.parametrize("field", REQUIRED_FIELDS)
def test_content_file_frontmatter_has_required_field(rel_path, field):
    filepath = os.path.join(REPO_ROOT, rel_path)
    fm = _parse_frontmatter(filepath)
    if fm is None:
        pytest.skip(f"{rel_path}: no frontmatter (caught by test_content_file_has_frontmatter)")
    assert field in fm, f"{rel_path}: frontmatter missing field: {field}"
