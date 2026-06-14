---
status: draft
last_updated: "2026-06-13"
owner: hayesgb
applies_to:
  - all
---

# General Agent Guidelines

> **TODO**: Document platform-wide guidelines that all AI coding agents should follow
> when generating code or suggestions for this team's repositories.
> This file is a structural placeholder.

## Context Retrieval

Before generating code, an agent should:

1. Fetch `manifest.yaml` from this repository via the GitHub Contents API.
2. Filter guidelines by `applies_to` matching the current task type.
3. Fetch and read each relevant guideline file.
4. Apply the retrieved guidelines to the generated output.

## General Principles

*(Document overarching principles: correctness over cleverness, explicit over implicit, etc.)*

## Anti-Patterns to Avoid

*(Document common mistakes agents should not make in this codebase.)*
