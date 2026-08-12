# Versioning

Canonical release-versioning policy for this authoring repository. When a skill
or guide disagrees with this file, this file wins.

## One version for the whole suite

The suite ships as a single unit, so it carries a **single version**. Every
skill in a release is stamped with that same version, whether or not that skill
changed in the release. There are no independent per-skill versions.

This is deliberate: a user installs `phase-tracker` and `phase-recap` together
and needs to know their conventions agree. A shared version answers that; eight
drifting versions do not.

## Suite version vs phase numbers

These are two different numbering systems and must never be conflated:

| | Format | Meaning | Lives in |
|---|---|---|---|
| **Suite version** | `MAJOR.MINOR.PATCH` (SemVer) | A release of these skills | this repo only |
| **Phase number** | `MAJOR.MINOR.PATCH` | A unit of work in a project *using* these skills | installed projects' `development/phase_log/` |

A phase number is never a version, and the suite version never appears in a
phase plan, phase log, or index. See `TERMINOLOGY.md` for the phase hierarchy.

## What a bump means

Semantic Versioning, read against a workflow-conventions package rather than a
code library. The contract is the **conventions installed projects rely on** —
the knowledge-bundle layout, the phase-record front matter, the numbering
grammar, and the record shape the phase templates define.

- **MAJOR** — a breaking convention change: existing phase records, indexes, or
  `development/` bundles produced by the previous version would no longer
  validate or would need migration. Example: changing the phase-number grammar,
  renaming `development/phase_log/`, or removing a required front-matter key.
- **MINOR** — backward-compatible growth: a new skill, a new response banner, a
  new optional template section, a new asset. Projects on the previous version
  keep working untouched.
- **PATCH** — corrections that change no convention: wording, typos, clearer
  trigger descriptions, validation fixes, README edits.

When a change is arguably MINOR or MAJOR, choose MAJOR. A user finding out that
their existing phase history no longer validates is worse than a version number
that moved further than it strictly had to.

## Where the version lives

Four places, and they must agree exactly:

1. `.claude-plugin/plugin.json` — `version`
2. `.claude-plugin/marketplace.json` — the `phase-workflow` plugin's `version`
3. Every `SKILL.md` frontmatter — `version`, in all eight root skills and their
   exact `.agents/skills/` and `.claude/skills/` mirrors
4. `CHANGELOG.md` — the topmost released heading

`scripts/validate_repo.py` enforces all four. Bumping one by hand fails
validation until the rest follow.

## Release procedure

1. On a short-lived `chore/` or `docs/` branch, bump the version in
   `plugin.json` and `marketplace.json`, and in every root `SKILL.md`
   frontmatter.
2. Refresh the exact `.agents/skills/` and `.claude/skills/` mirrors
   mechanically.
3. Move `CHANGELOG.md`'s `Unreleased` entries under a new version heading with
   the release date.
4. Run:

   ```bash
   python3 scripts/validate_repo.py
   git diff --check
   ```

5. Commit with actual contributor trailers, push, and open an attributed PR.
6. **After the PR merges**, tag the merge commit on `main` and push the tag:

   ```bash
   git tag -a vX.Y.Z -m "phase-skills vX.Y.Z — <headline>"
   git push origin vX.Y.Z
   ```

Tags are always annotated, always prefixed `v`, and always point at a commit
reachable from `main`. Never tag an unmerged branch tip — a squash merge would
leave the tag pointing at a commit that is not in the released history.
