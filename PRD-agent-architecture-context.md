---
id: PRD-0001
type: prd
title: "Agent Architecture Context Repository"
status: draft
owner: hayesgb
created_at: 2026-06-13
updated_at: 2026-06-13
related_stories: []
tags: [architecture, agent-guidelines, data-engineering, dataform, looker]
---

## Problem Statement

A data engineering team builds pipelines (Dataform, BigQuery, Looker Core)
using a mix of AI coding agents (Gemini, Claude, Copilot, and others). There is currently
no single, authoritative, machine- and human-readable source for system architecture
(current and future state), repository/code structure standards, and best-practice
guidelines that those agents should follow. As a result, agents may generate code that
diverges from architectural intent or team conventions, and humans lack a single place
to see "what does the platform actually look like today, and where is it heading."

This project creates a version-controlled repository — `agent-architecture-context` — that serves as
the single source of truth for architecture, repo standards, and agent guidelines, along
with a lightweight, platform-agnostic mechanism for any AI agent (regardless of vendor)
to discover and fetch the subset of that content relevant to its current task.

## Goals

**Primary goals:**
- Establish a repository structure that cleanly separates current-state architecture,
  future-state/planned architecture, repo standards, and agent guidelines.
- Provide a `manifest.yaml` at the repo root that indexes all guideline files, tags each
  with `applies_to` task types, and exposes a `version` / `last_updated` field.
- Provide a `skill-spec.yaml` defining a platform-agnostic contract (auth method,
  endpoints, expected output format) for how an agent retrieves manifest and content
  files via the GitHub Contents API using a per-user fine-grained Personal Access Token (PAT).
- Provide at least one working reference template (generic HTTP/curl-based) under
  `/agent-integration/templates` that a team member can adapt to their agent platform
  (Gemini extension, MCP server, etc.), plus a README walking through PAT generation
  and template selection.
- Provide automated tests that validate: the manifest is well-formed YAML, every file
  path referenced in the manifest exists in the repo, every markdown file has valid
  frontmatter (where applicable), and the skill-spec.yaml conforms to its schema.

**Secondary / stretch goals:**
- Provide a second platform-specific template (e.g., a minimal MCP server in Python)
  in addition to the generic HTTP template.

## Out of Scope

- Building a hosted API service (beyond the existing GitHub Contents API) — this is
  explicitly deferred; the GitHub API itself is the retrieval mechanism for this phase.
- Building or configuring actual Gemini extensions, Claude MCP servers, or Copilot
  integrations end-to-end — only reference templates/skeletons are produced.
- Authoring the actual content of the architecture diagrams, repo standards, or
  agent guidelines documents (these will be placeholder/stub files with the correct
  structure and frontmatter, to be filled in by the team afterward).
- Token issuance, rotation, or secrets management infrastructure — the README documents
  the process but does not automate it.
- CI/CD pipeline setup for auto-publishing or syncing content elsewhere.

## Requirements

### Tech Stack & Best Practices

| Dimension | Decision |
|---|---|
| Language & Runtime | Python 3.12 (for validation scripts and tests) |
| Frameworks & Libraries | PyYAML (YAML parsing/validation), pytest, jsonschema (for skill-spec/manifest schema validation) |
| Test Framework | pytest |
| Deployment / Environment | Standalone GitHub repository; no deployment target — content is consumed via the GitHub Contents API by external agents |

### Functional Capabilities

- **CAP-001**: Repository scaffold with the following top-level directories:
  `/architecture/current`, `/architecture/future`, `/architecture/decisions`,
  `/repo-standards`, `/agent-guidelines`, `/agent-integration`. Each directory contains
  at least one placeholder markdown file with valid frontmatter (`status`, `last_updated`,
  `owner` fields at minimum) so the structure is non-empty and testable.
- **CAP-002**: `manifest.yaml` at repo root with `version`, `last_updated`, and a
  `categories` section enumerating every guideline file with a relative `path` and an
  `applies_to` list (values: `all`, `pipeline-development`, `code-review`,
  `architecture-review`, or others as needed). Malformed entries (missing `path` or
  `applies_to`) must be rejected by validation.
- **CAP-003**: `skill-spec.yaml` under `/agent-integration` defining: `name`,
  `description`, `auth` (type: `github-pat`, scope, header format), `endpoints`
  (`manifest` and `file`, both GitHub Contents API paths), and `output_format`.
- **CAP-004**: `/agent-integration/templates/generic-http-template.md` — a
  copy/paste-ready set of instructions (including example `curl` commands using the
  GitHub Contents API with a Bearer token and the `application/vnd.github.raw+json`
  Accept header) for fetching the manifest and any listed file. The token must be
  retrieved from the OS-native credential store at runtime (e.g.,
  `security find-generic-password ... -w` on macOS, `secret-tool lookup` on Linux,
  `keyring`/`cmdkey` on Windows) rather than hardcoded or read from a plaintext file.
- **CAP-005**: `/agent-integration/README.md` documenting: (1) how to generate a
  fine-grained GitHub PAT scoped read-only to this repo, (2) how to store the token
  securely using the OS-native credential store — macOS Keychain via the `security`
  command (or the `keyring` Python library), Linux `secret-tool`/libsecret, or Windows
  Credential Manager via `cmdkey`/`keyring` — rather than plaintext config or `.env`
  files, (3) how to pick and adapt a template from `/templates`, including how the
  template retrieves the token from the OS credential store at runtime, (4) how to
  verify setup by fetching `manifest.yaml`.
- **CAP-006**: Validation test suite (pytest) covering:
  - `manifest.yaml` parses as valid YAML and matches an expected schema (required
    top-level keys: `version`, `last_updated`, `categories`).
  - Every `path` referenced under `categories.*.files` corresponds to a file that
    exists in the repo.
  - Every `applies_to` value is from an allowed/known set defined in the test (or in
    a `task_types` section if present).
  - `skill-spec.yaml` parses as valid YAML and contains the required keys: `name`,
    `description`, `auth`, `endpoints`, `output_format`.
  - Every markdown file under `/architecture`, `/repo-standards`, and
    `/agent-guidelines` has YAML frontmatter containing at least `status` and
    `last_updated` fields.
- **Constraints**:
  - All content files are Markdown or YAML — no platform-specific syntax (e.g., no
    Gemini- or Claude-specific markup) in `/architecture`, `/repo-standards`, or
    `/agent-guidelines`.
  - The manifest and skill-spec must remain valid (pass CAP-006 tests) after any future
    content addition — tests are the guardrail for repo integrity going forward.
  - Input/error handling: if `manifest.yaml` references a missing file, or
    `skill-spec.yaml` is missing required keys, the test suite must fail with a clear
    error message identifying the offending path/key (not a generic stack trace).
  - Output: test suite runs via `pytest` from the repo root with no additional
    configuration beyond a `requirements.txt` (or `pyproject.toml`) listing PyYAML,
    pytest, and jsonschema.

### Workflow Sequences

- **WF-001 — Agent retrieves task-relevant guidelines**
  1. Agent (via its platform-specific skill, built from CAP-004 template) fetches
     `manifest.yaml` using the GitHub Contents API and a PAT (per `skill-spec.yaml`,
     CAP-003).
  2. Agent filters `categories.*.files` by `applies_to` matching its current task type.
  3. Agent fetches each filtered file's content via the same API/auth pattern.
  4. Agent uses the retrieved content as context before generating code/output.
  - Error condition: if the manifest fetch returns a 401/403, the agent (per
    CAP-005 README) should surface a message indicating the PAT is missing, expired,
    or insufficiently scoped.

- **WF-002 — Team member sets up their own agent integration**
  1. Team member generates a personal fine-grained PAT (read-only, scoped to this repo),
     per `/agent-integration/README.md`.
  2. Team member selects the template under `/agent-integration/templates` matching
     their platform (or the generic HTTP template if none matches).
  3. Team member stores their token per their platform's credential mechanism and wires
     it into the template.
  4. Team member verifies setup by fetching `manifest.yaml` and confirming a 200 response.
  - Depends on: WF-001's `skill-spec.yaml` contract (CAP-003) being stable.

- **WF-003 — Maintainer updates architecture or guidelines**
  1. Maintainer edits or adds a file under `/architecture`, `/repo-standards`, or
     `/agent-guidelines`, including required frontmatter fields.
  2. Maintainer adds/updates the corresponding entry in `manifest.yaml`, including
     `applies_to` tags, and bumps `version` / `last_updated`.
  3. CI (or local `pytest` run) validates the manifest and frontmatter per CAP-006
     before merge.
  - Error condition: if a new file is added without a corresponding manifest entry,
    or vice versa, CAP-006 tests should fail.

### GitHub Repository

| Field | Value |
|---|---|
| Repository URL | github.com/hayesgb/agent-architecture-context (to be created) |
| Visibility | Private |

> Branch naming, commit message format, and PR conventions are defined by the implementation agent.

## Story Scaffold

> Stories generated by the `story-decomposer` skill on 2026-06-13.
> Ordered for sequential implementation. Stories with empty `depends_on` are valid parallel starting points.
> Do not reorder without updating dependencies.

```yaml
stories:

  - story_id: "S-001"
    title: "Scaffold repository directory structure"
    description: >
      Create the top-level directory structure (/architecture/current,
      /architecture/future, /architecture/decisions, /repo-standards,
      /agent-guidelines, /agent-integration/templates) with placeholder
      markdown files containing valid YAML frontmatter.
    depends_on: []
    acceptance_criteria:
      - "Repository contains directories: architecture/current, architecture/future, architecture/decisions, repo-standards, agent-guidelines, agent-integration/templates"
      - "Each of architecture/current, architecture/future, architecture/decisions, repo-standards, and agent-guidelines contains at least one .md file"
      - "Each placeholder .md file under architecture, repo-standards, and agent-guidelines has parseable YAML frontmatter"
      - "Each placeholder .md file's frontmatter includes a 'status' field and a 'last_updated' field"
    test_criteria:
      - "os.path.isdir('architecture/current') is True"
      - "os.path.isdir('architecture/future') is True"
      - "os.path.isdir('architecture/decisions') is True"
      - "os.path.isdir('repo-standards') is True"
      - "os.path.isdir('agent-guidelines') is True"
      - "os.path.isdir('agent-integration/templates') is True"
      - "Each directory under architecture, repo-standards, agent-guidelines has >= 1 .md file"
      - "yaml.safe_load of frontmatter block from each .md returns dict with 'status' and 'last_updated' keys"
    test_files:
      - "tests/test_s001_scaffold.py"
    notes: "Frontmatter delimited by '---' lines at top of file. Use PyYAML to parse."
    passes: false

  - story_id: "S-002"
    title: "Create and validate manifest.yaml schema"
    description: >
      Create manifest.yaml at the repo root with version, last_updated, and a
      categories section listing files with path and applies_to fields, and
      write tests validating its schema.
    depends_on: ["S-001"]
    acceptance_criteria:
      - "manifest.yaml exists at repo root and parses as valid YAML"
      - "manifest.yaml contains top-level keys: version, last_updated, categories"
      - "Each entry under categories.*.files contains a 'path' field and an 'applies_to' field"
      - "Validation raises a clear error identifying the entry when 'path' or 'applies_to' is missing"
      - "Validation raises a clear error when an 'applies_to' value is not one of: all, pipeline-development, code-review, architecture-review"
    test_criteria:
      - "yaml.safe_load('manifest.yaml') succeeds without exception"
      - "manifest keys include 'version', 'last_updated', 'categories'"
      - "For each category and each file entry: 'path' key present, else AssertionError names the entry"
      - "For each category and each file entry: 'applies_to' key present, else AssertionError names the entry"
      - "Each applies_to value in ALLOWED_TASK_TYPES = {'all','pipeline-development','code-review','architecture-review'}"
    test_files:
      - "tests/test_s002_manifest_schema.py"
    notes: "ALLOWED_TASK_TYPES defined as a constant in the test file."
    passes: false

  - story_id: "S-003"
    title: "Validate manifest file references resolve to real files"
    description: >
      Write a test that confirms every path referenced in manifest.yaml
      corresponds to a file that exists in the repository.
    depends_on: ["S-001", "S-002"]
    acceptance_criteria:
      - "Test passes when every path in manifest.yaml categories.*.files exists on disk"
      - "Test fails and names the specific missing path when a referenced file does not exist"
    test_criteria:
      - "For each file entry path in manifest: os.path.isfile(path) is True, else AssertionError('Missing file: <path>')"
    test_files:
      - "tests/test_s003_manifest_file_refs.py"
    notes: "Paths in manifest are relative to repo root."
    passes: false

  - story_id: "S-004"
    title: "Validate frontmatter across content files"
    description: >
      Write a test that confirms every markdown file under /architecture,
      /repo-standards, and /agent-guidelines has frontmatter containing
      'status' and 'last_updated' fields.
    depends_on: ["S-001"]
    acceptance_criteria:
      - "Test passes for all placeholder markdown files created in S-001"
      - "Test fails and names the specific file and missing field when a file under architecture, repo-standards, or agent-guidelines lacks 'status' or 'last_updated' in its frontmatter"
    test_criteria:
      - "glob all .md files under architecture/, repo-standards/, agent-guidelines/"
      - "For each file: parse frontmatter between first pair of '---' delimiters"
      - "Assert 'status' in frontmatter, else AssertionError('<file>: missing field: status')"
      - "Assert 'last_updated' in frontmatter, else AssertionError('<file>: missing field: last_updated')"
    test_files:
      - "tests/test_s004_frontmatter.py"
    notes: "Reuse frontmatter parsing logic; consider a conftest helper."
    passes: false

  - story_id: "S-005"
    title: "Create skill-spec.yaml"
    description: >
      Create agent-integration/skill-spec.yaml defining the platform-agnostic
      contract for fetching manifest and content files via the GitHub Contents
      API using a per-user fine-grained PAT.
    depends_on: ["S-001"]
    acceptance_criteria:
      - "agent-integration/skill-spec.yaml exists and parses as valid YAML"
      - "skill-spec.yaml contains top-level keys: name, description, auth, endpoints, output_format"
      - "auth section specifies type: github-pat, a scope description, and a header format string"
      - "endpoints section defines both 'manifest' and 'file' entries as GitHub Contents API paths"
    test_criteria:
      - "os.path.isfile('agent-integration/skill-spec.yaml') is True"
      - "yaml.safe_load succeeds"
      - "All of name, description, auth, endpoints, output_format present as top-level keys"
      - "spec['auth']['type'] == 'github-pat'"
      - "'manifest' in spec['endpoints'] and 'file' in spec['endpoints']"
    test_files:
      - "tests/test_s005_s006_skill_spec.py"
    notes: "GitHub Contents API base: https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    passes: false

  - story_id: "S-006"
    title: "Validate skill-spec.yaml schema"
    description: >
      Write a test that confirms skill-spec.yaml contains all required keys
      and that the auth and endpoints sections are well-formed.
    depends_on: ["S-005"]
    acceptance_criteria:
      - "Test passes when skill-spec.yaml contains name, description, auth, endpoints, and output_format"
      - "Test fails and names the specific missing key when name, description, auth, endpoints, or output_format is absent"
      - "Test fails when endpoints is missing either 'manifest' or 'file'"
    test_criteria:
      - "For each required key in ['name','description','auth','endpoints','output_format']: assert key in spec, else AssertionError('skill-spec.yaml missing key: <key>')"
      - "For each required endpoint in ['manifest','file']: assert key in spec['endpoints'], else AssertionError('skill-spec.yaml endpoints missing: <key>')"
    test_files:
      - "tests/test_s005_s006_skill_spec.py"
    notes: "S-005 and S-006 share a test file; S-005 creates the file, S-006 adds schema tests."
    passes: false

  - story_id: "S-007"
    title: "Create generic HTTP template"
    description: >
      Create agent-integration/templates/generic-http-template.md containing
      working curl examples for fetching the manifest and a content file via
      the GitHub Contents API, using a Bearer token retrieved from the OS-native
      credential store at runtime, and the application/vnd.github.raw+json
      Accept header, consistent with skill-spec.yaml's endpoints.
    depends_on: ["S-005"]
    acceptance_criteria:
      - "agent-integration/templates/generic-http-template.md exists"
      - "Template includes a curl example for the 'manifest' endpoint matching skill-spec.yaml's endpoints.manifest pattern"
      - "Template includes a curl example for the 'file' endpoint matching skill-spec.yaml's endpoints.file pattern"
      - "Template includes the Authorization: Bearer header and the application/vnd.github.raw+json Accept header in both examples"
      - "Template demonstrates retrieving the token from an OS-native credential store (macOS Keychain via security, Linux secret-tool, or Windows Credential Manager via cmdkey/keyring) rather than a hardcoded value or plaintext file"
    test_criteria:
      - "os.path.isfile('agent-integration/templates/generic-http-template.md') is True"
      - "File content contains 'application/vnd.github.raw+json'"
      - "File content contains 'Authorization: Bearer'"
      - "File content contains 'security find-generic-password' OR 'secret-tool lookup' OR 'cmdkey'"
      - "File content contains the manifest endpoint URL pattern from skill-spec.yaml"
    test_files:
      - "tests/test_s007_generic_template.py"
    notes: "Token retrieval must use OS credential store, not env vars or plaintext files."
    passes: false

  - story_id: "S-008"
    title: "Write agent-integration README"
    description: >
      Create agent-integration/README.md documenting PAT generation, secure
      token storage in the OS-native credential store across macOS, Linux, and
      Windows, how to select and adapt a template, and how to verify setup by
      fetching manifest.yaml.
    depends_on: ["S-007"]
    acceptance_criteria:
      - "agent-integration/README.md exists"
      - "README references agent-integration/templates/generic-http-template.md by path"
      - "README contains sections covering: PAT generation, OS-native credential store storage (macOS, Linux, and Windows), template selection, and setup verification"
    test_criteria:
      - "os.path.isfile('agent-integration/README.md') is True"
      - "File content contains 'agent-integration/templates/generic-http-template.md'"
      - "File content contains 'macOS' or 'Keychain'"
      - "File content contains 'Linux' or 'secret-tool'"
      - "File content contains 'Windows' or 'cmdkey'"
      - "File content contains 'fine-grained' (PAT generation section)"
      - "File content contains 'manifest.yaml' (setup verification section)"
    test_files:
      - "tests/test_s008_readme.py"
    notes: "README is documentation only; no code to implement."
    passes: false
```

## Open Questions

- ~~Should `manifest.yaml` include a `task_types` section in this initial version...~~
  **Resolved**: v1 uses per-file `applies_to` tags only. `task_types` filtering is
  deferred as a future enhancement (not part of this PRD's scope).
- ~~What specific `applies_to` / task-type values does the team want...~~
  **Resolved**: `all`, `pipeline-development`, `code-review`, `architecture-review` is
  the confirmed starting set for `applies_to` values.
- Should the placeholder content files include real (even if minimal) architecture
  content for the team's specific platform, or remain purely structural stubs with TODO
  markers? Current assumption: structural stubs only (per Out of Scope).
- Is `hayesgb/agent-architecture-context` the desired repo name/namespace, or should this live
  under an organization account instead of a personal namespace?

---
*Generated by the `prd-author` skill. Do not modify section headings — they are parsed by downstream tooling.*
