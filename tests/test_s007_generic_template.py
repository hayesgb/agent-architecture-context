"""S-007: Validate generic-http-template.md contains required curl examples."""
import os
import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_PATH = os.path.join(
    REPO_ROOT, "agent-integration", "templates", "generic-http-template.md"
)


@pytest.fixture(scope="module")
def template_content():
    assert os.path.isfile(TEMPLATE_PATH), \
        "agent-integration/templates/generic-http-template.md does not exist"
    with open(TEMPLATE_PATH) as f:
        return f.read()


def test_template_includes_raw_json_accept_header(template_content):
    assert "application/vnd.github.raw+json" in template_content, \
        "Template missing Accept: application/vnd.github.raw+json header"


def test_template_includes_authorization_bearer(template_content):
    assert "Authorization: Bearer" in template_content, \
        "Template missing Authorization: Bearer header"


def test_template_includes_manifest_endpoint(template_content):
    assert "api.github.com/repos" in template_content, \
        "Template missing GitHub Contents API endpoint (api.github.com/repos)"


def test_template_includes_manifest_path(template_content):
    assert "manifest.yaml" in template_content, \
        "Template missing reference to manifest.yaml endpoint"


def test_template_includes_file_endpoint_with_path_param(template_content):
    assert "{path}" in template_content or "<path>" in template_content, \
        "Template missing parameterized file endpoint ({path} or <path>)"


def test_template_uses_os_native_credential_store_macos(template_content):
    assert "security find-generic-password" in template_content, \
        "Template missing macOS Keychain token retrieval (security find-generic-password)"


def test_template_uses_os_native_credential_store_linux(template_content):
    assert "secret-tool lookup" in template_content, \
        "Template missing Linux credential store token retrieval (secret-tool lookup)"


def test_template_uses_os_native_credential_store_windows(template_content):
    assert "cmdkey" in template_content or "keyring" in template_content, \
        "Template missing Windows credential store token retrieval (cmdkey or keyring)"
