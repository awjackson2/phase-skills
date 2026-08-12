# Changelog

All notable changes to this suite are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the suite follows
[Semantic Versioning](https://semver.org/spec/v2.0.0.html) as interpreted in
[`VERSIONING.md`](VERSIONING.md).

The suite ships one version for all eight skills. Phase numbers used inside
projects are a separate numbering system and never appear here.

## [Unreleased]

## [1.2.1] — 2026-08-11

### Fixed

- The portable workflow charter now ships as a skill asset
  (`phase-project-init/assets/phase_project.md`), so init/adopt can seed the
  project's agent guide in every install. Previously the charter existed only
  at the authoring-repo root, which never ships with the skills — a standalone
  install (plugin, copied folders, or `.agents/skills/` for Codex/Copilot)
  could not complete the guide-seeding step and produced no `AGENTS.md`.
  `validate_repo.py` enforces that the asset stays byte-identical to the root
  charter.
- Init and adopt now name the agent guide file(s) to seed — `CLAUDE.md`,
  `AGENTS.md`, or both — instead of assuming `CLAUDE.md`.
- The shipped PR-template asset is now actually installed: init copies it in
  git projects that expect PRs, and adopt copies it (or offers to merge it into
  an existing template). Previously it shipped but no step referenced it.

## [1.2.0] — 2026-08-11

### Changed

- **Git is optional.** `phase-project-init` now asks whether the project should
  use git instead of assuming it; declining skips every branch / worktree /
  commit / PR step while plans, logs, and the index work unchanged. Adding git
  later is a documented one-step upgrade. `phase-tracker`, `phase-audit`,
  `phase-loop`, `phase-adopt`, the charter, and `TERMINOLOGY.md` carry the rule.
- The OKF format is no longer packaged separately. The `development/` bundle
  keeps its shape — YAML front matter on every concept, one
  `## OKF relationships` footer per phase record, evidence outside — but the
  phase templates are now the contract, and the agent upholds it:
  `phase-tracker` re-checks records before closing a phase, and `phase-audit`
  check 11 is a manual read-through.

### Removed

- `OKF.md`, the shipped `scripts/okf/manage_bundle.py` validator and
  `scripts/okf/profile.md` schema, and the `.okfignore` boundary file.
  `scripts/validate_repo.py` now fails if any of them reappear.

## [1.1.0] — 2026-07-30

### Added

- `development/` is now a **knowledge bundle**: everything inside it is a
  Concept with YAML front matter, and phase records end with one
  `## OKF relationships` footer. Evidence such as audits and scratch notes
  stays outside the bundle.
- `scripts/okf/manage_bundle.py` — a stdlib-only validator, so it runs in a
  project that has installed nothing — plus the contract it enforces in
  `scripts/okf/profile.md`. Both ship as `phase-project-init` assets.
- `OKF.md` — the canonical concept, relationship, and attribution profile.
- Exact ChatGPT/Codex skill mirrors under `.agents/skills/` for all eight
  skills, and matching exact copies under `.claude/skills/`.
- `AGENTS.md` and `AGENT.md` as byte-for-byte mirrors of `CLAUDE.md`.
- Agent-attribution conventions: per-agent `Co-Authored-By` commit trailers and
  an `## Agent signatures` PR section, with a repository PR template matching
  the one installed into projects.
- `scripts/validate_repo.py` and a CI workflow enforcing mirror equality,
  scaffold completeness, and template invariants.
- Release versioning: this changelog, [`VERSIONING.md`](VERSIONING.md), a
  `version` key in every skill's frontmatter, and validation that the plugin
  manifests, skill frontmatter, and changelog all agree.

### Changed

- Skills and guides are agent-neutral. Provider names appear only where a real
  interface or a stable attribution identity is discussed.
- Local phase worktrees moved from a provider-specific path to `.worktrees/`.
- `phase-tracker` authors records that conform to the bundle contract,
  `phase-audit` runs the validator, and `phase-recap` reads front matter
  instead of parsing prose.
- `phase-amend`'s sync surface records the knowledge-bundle convention, both
  mirror roots, and the versioning locations.

## [1.0.0] — 2026-07-02

### Added

- Initial public release of the phase-driven development workflow.
- Seven shipped skills: `phase-tracker`, `phase-recap`, `phase-decompose`,
  `phase-loop`, `phase-project-init`, `phase-adopt`, `phase-audit`, plus the
  `phase-amend` repository-maintenance skill.
- Canonical conventions: `TERMINOLOGY.md`, `templates/recap_template.md`,
  `templates/response_templates.md`, and the portable `phase_project.md`
  charter.
- Packaging for skill directories and the Claude Code plugin marketplace via
  `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`.
- MIT license and README covering both install routes.

[Unreleased]: https://github.com/awjackson2/phase-skills/compare/v1.2.1...HEAD
[1.2.1]: https://github.com/awjackson2/phase-skills/compare/v1.2.0...v1.2.1
[1.2.0]: https://github.com/awjackson2/phase-skills/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/awjackson2/phase-skills/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/awjackson2/phase-skills/releases/tag/v1.0.0
