"""S-001: Validate repository directory structure and placeholder frontmatter."""
import os
import glob
import yaml
import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

REQUIRED_DIRS = [
    "architecture/current",
    "architecture/future",
    "architecture/decisions",
    "repo-standards",
    "agent-guidelines",
    "agent-integration/templates",
]

CONTENT_DIRS = [
    "architecture/current",
    "architecture/future",
    "architecture/decisions",
    "repo-standards",
    "agent-guidelines",
]


def parse_frontmatter(filepath):
    with open(filepath) as f:
        content = f.read()
    if not content.startswith("---"):
        return None
    parts = content.split("---", 2)
    if len(parts) < 3:
        return None
    return yaml.safe_load(parts[1])


@pytest.mark.parametrize("directory", REQUIRED_DIRS)
def test_required_directories_exist(directory):
    path = os.path.join(REPO_ROOT, directory)
    assert os.path.isdir(path), f"Missing required directory: {directory}"


@pytest.mark.parametrize("directory", CONTENT_DIRS)
def test_directory_has_at_least_one_md_file(directory):
    path = os.path.join(REPO_ROOT, directory)
    md_files = glob.glob(os.path.join(path, "*.md"))
    assert len(md_files) >= 1, f"Directory has no .md files: {directory}"


def test_all_content_md_files_have_valid_frontmatter():
    for directory in CONTENT_DIRS:
        path = os.path.join(REPO_ROOT, directory)
        md_files = glob.glob(os.path.join(path, "*.md"))
        for filepath in md_files:
            rel = os.path.relpath(filepath, REPO_ROOT)
            fm = parse_frontmatter(filepath)
            assert fm is not None, f"{rel}: missing or unparseable frontmatter"
            assert "status" in fm, f"{rel}: frontmatter missing field: status"
            assert "last_updated" in fm, f"{rel}: frontmatter missing field: last_updated"
