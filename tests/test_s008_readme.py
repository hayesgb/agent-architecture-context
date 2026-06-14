"""S-008: Validate agent-integration/README.md contains required sections."""
import os
import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
README_PATH = os.path.join(REPO_ROOT, "agent-integration", "README.md")


@pytest.fixture(scope="module")
def readme_content():
    assert os.path.isfile(README_PATH), \
        "agent-integration/README.md does not exist"
    with open(README_PATH) as f:
        return f.read()


def test_readme_references_generic_template(readme_content):
    assert "agent-integration/templates/generic-http-template.md" in readme_content, \
        "README does not reference agent-integration/templates/generic-http-template.md"


def test_readme_covers_pat_generation(readme_content):
    assert "fine-grained" in readme_content, \
        "README missing PAT generation section (expected 'fine-grained')"


def test_readme_covers_macos_credential_store(readme_content):
    assert "macOS" in readme_content or "Keychain" in readme_content, \
        "README missing macOS credential store instructions"


def test_readme_covers_linux_credential_store(readme_content):
    assert "Linux" in readme_content or "secret-tool" in readme_content, \
        "README missing Linux credential store instructions"


def test_readme_covers_windows_credential_store(readme_content):
    assert "Windows" in readme_content or "cmdkey" in readme_content, \
        "README missing Windows credential store instructions"


def test_readme_covers_setup_verification(readme_content):
    assert "manifest.yaml" in readme_content, \
        "README missing setup verification section (expected 'manifest.yaml')"


def test_readme_covers_template_selection(readme_content):
    assert "template" in readme_content.lower(), \
        "README missing template selection guidance"
