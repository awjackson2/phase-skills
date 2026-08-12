#!/usr/bin/env python3
"""Validate phase-skills mirrors and OKF-native scaffold invariants."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = (
    "phase-tracker",
    "phase-recap",
    "phase-project-init",
    "phase-adopt",
    "phase-decompose",
    "phase-loop",
    "phase-audit",
    "phase-amend",
)
SHIPPED_SKILLS = SKILLS[:-1]
ASSETS = ROOT / "phase-project-init" / "assets" / "development"
# Mirror roots that must be byte-exact copies of the root skill directories:
# the ChatGPT/Codex export, and the copies this repo's own agent runtime loads.
MIRRORS = (".agents", ".claude")
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def frontmatter(text: str) -> str:
    """Return the YAML frontmatter block, or an empty string if absent."""
    if not text.startswith("---\n"):
        return ""
    end = text.find("\n---\n", 3)
    return text[4:end] if end != -1 else ""


def skill_files(directory: Path) -> set[Path]:
    return {
        path.relative_to(directory)
        for path in directory.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    }


def validate_mirror(skill: str, source_dir: Path, label: str, errors: list[str]) -> None:
    """One mirror root must be a byte-exact copy of the root skill directory."""
    mirror_dir = ROOT / label / "skills" / skill
    mirror = mirror_dir / "SKILL.md"
    require(mirror.is_file(), f"{mirror.relative_to(ROOT)} is missing", errors)
    if not mirror.is_file():
        return

    source_files = skill_files(source_dir)
    mirror_files = skill_files(mirror_dir)
    require(
        source_files == mirror_files,
        f"{skill}: root and {label} file trees differ",
        errors,
    )
    for relative in sorted(source_files & mirror_files):
        require(
            (source_dir / relative).read_bytes()
            == (mirror_dir / relative).read_bytes(),
            f"{skill}: {label} mirror differs at {relative}",
            errors,
        )


def validate_skill(skill: str, version: str | None, errors: list[str]) -> None:
    source_dir = ROOT / skill
    source = source_dir / "SKILL.md"
    require(source.is_file(), f"{source.relative_to(ROOT)} is missing", errors)
    if not source.is_file():
        return

    for label in MIRRORS:
        validate_mirror(skill, source_dir, label, errors)

    text = source.read_text(encoding="utf-8")
    require(text.startswith("---\n"), f"{skill}: missing YAML frontmatter", errors)
    require(
        f"\nname: {skill}\n" in text,
        f"{skill}: frontmatter name does not match directory",
        errors,
    )
    require(
        "\ndescription:" in text.split("\n---\n", 1)[0],
        f"{skill}: missing trigger description",
        errors,
    )
    if version is not None:
        require(
            f"\nversion: {version}\n" in f"\n{frontmatter(text)}\n",
            f"{skill}: frontmatter version is not {version} (the suite version)",
            errors,
        )
    require(
        ".claude/worktrees" not in text,
        f"{skill}: provider-specific worktree path remains",
        errors,
    )


def validate_phase_template(
    path: Path,
    *,
    concept_type: str,
    relationship_label: str,
    errors: list[str],
) -> None:
    text = path.read_text(encoding="utf-8")
    relative = path.relative_to(ROOT)
    require(text.startswith("---\n"), f"{relative}: missing frontmatter", errors)
    for expected in (
        f"type: {concept_type}",
        'phase: "X.Y.Z"',
        "phase_status:",
        "delivery_status:",
        'recorded_on: "YYYY-MM-DD"',
    ):
        require(expected in text, f"{relative}: missing {expected}", errors)
    require(
        text.count("## OKF relationships") == 1,
        f"{relative}: expected one relationship footer",
        errors,
    )
    require(
        relationship_label in text,
        f"{relative}: missing {relationship_label}",
        errors,
    )


def validate_versioning(version: str | None, errors: list[str]) -> None:
    """The suite version must agree across the manifests and the changelog."""
    require(
        version is not None and bool(SEMVER.match(version)),
        "plugin.json version is missing or is not MAJOR.MINOR.PATCH",
        errors,
    )

    marketplace_path = ROOT / ".claude-plugin" / "marketplace.json"
    if marketplace_path.is_file():
        marketplace = json.loads(marketplace_path.read_text(encoding="utf-8"))
        listed = {
            entry.get("name"): entry.get("version")
            for entry in marketplace.get("plugins", [])
        }
        require(
            listed.get("phase-workflow") == version,
            "marketplace.json phase-workflow version differs from plugin.json",
            errors,
        )
    else:
        errors.append(".claude-plugin/marketplace.json is missing")

    require((ROOT / "VERSIONING.md").is_file(), "VERSIONING.md is missing", errors)

    changelog = ROOT / "CHANGELOG.md"
    require(changelog.is_file(), "CHANGELOG.md is missing", errors)
    if changelog.is_file() and version is not None:
        text = changelog.read_text(encoding="utf-8")
        require(
            "## [Unreleased]" in text,
            "CHANGELOG.md has no Unreleased section",
            errors,
        )
        released = re.findall(r"^## \[(\d+\.\d+\.\d+)\]", text, flags=re.MULTILINE)
        require(
            bool(released) and released[0] == version,
            f"CHANGELOG.md's newest release heading is not [{version}]",
            errors,
        )


def main() -> int:
    errors: list[str] = []

    plugin_path = ROOT / ".claude-plugin" / "plugin.json"
    plugin = json.loads(plugin_path.read_text(encoding="utf-8"))
    version = plugin.get("version")
    if not isinstance(version, str) or not SEMVER.match(version):
        version = None

    validate_versioning(version, errors)

    for skill in SKILLS:
        validate_skill(skill, version, errors)

    guide = ROOT / "CLAUDE.md"
    for mirror_name in ("AGENTS.md", "AGENT.md"):
        mirror = ROOT / mirror_name
        require(mirror.is_file(), f"{mirror_name} is missing", errors)
        if guide.is_file() and mirror.is_file():
            require(
                guide.read_bytes() == mirror.read_bytes(),
                f"CLAUDE.md and {mirror_name} differ",
                errors,
            )

    required_assets = (
        "index.md",
        "log.md",
        "design/index.md",
        "design/_element_template.md",
        "phase_log/phase_index.md",
        "phase_log/phase_plan_template.md",
        "phase_log/phase_log_template.md",
    )
    for relative in required_assets:
        require(
            (ASSETS / relative).is_file(),
            f"phase-project-init asset missing: development/{relative}",
            errors,
        )
    # The OKF format is the bundle's native shape, but it is not packaged
    # separately: no OKF.md doc, no scripts/okf/ schema or validator shipped.
    require(
        not (ROOT / "OKF.md").exists(),
        "OKF.md is superseded: the format lives inline in the docs and templates",
        errors,
    )
    require(
        not (ROOT / "phase-project-init" / "assets" / "scripts").exists(),
        "assets/scripts/ is superseded: no validator or schema ships to projects",
        errors,
    )
    require(
        not (ASSETS / ".okfignore").exists(),
        ".okfignore is superseded: the bundle boundary is prose, not tooling",
        errors,
    )

    pr_template = (
        ROOT
        / "phase-project-init"
        / "assets"
        / ".github"
        / "pull_request_template.md"
    )
    require(pr_template.is_file(), "project PR template asset is missing", errors)
    if pr_template.is_file():
        require(
            "## Agent signatures" in pr_template.read_text(encoding="utf-8"),
            "project PR template lacks Agent signatures",
            errors,
        )
        repository_pr_template = ROOT / ".github" / "pull_request_template.md"
        require(
            repository_pr_template.is_file()
            and repository_pr_template.read_bytes() == pr_template.read_bytes(),
            "repository and installed PR templates differ",
            errors,
        )

    validate_phase_template(
        ASSETS / "phase_log" / "phase_plan_template.md",
        concept_type="Phase Plan",
        relationship_label="Intended design impact",
        errors=errors,
    )
    validate_phase_template(
        ASSETS / "phase_log" / "phase_log_template.md",
        concept_type="Phase Log",
        relationship_label="Verified design impact",
        errors=errors,
    )

    design_template = ASSETS / "design" / "_element_template.md"
    if design_template.is_file():
        design_text = design_template.read_text(encoding="utf-8")
        require(
            design_text.count("```markdown") == 1,
            "design template must contain one copyable Markdown concept",
            errors,
        )
        require(
            "type: Design Concept" in design_text,
            "design template example lacks Design Concept frontmatter",
            errors,
        )
        # The project contract requires a relationship footer on phase records
        # only; design concepts link freely in prose. Asserting a footer here
        # would make this validator stricter than the contract the skills state.
        require(
            "wrapper" in design_text.lower() and "copy" in design_text.lower(),
            "design template must prohibit wrappers and copied bodies",
            errors,
        )

    plugin_skills = tuple(
        str(value).removeprefix("./") for value in plugin.get("skills", [])
    )
    require(
        len(plugin_skills) == len(SHIPPED_SKILLS)
        and set(plugin_skills) == set(SHIPPED_SKILLS),
        "plugin skill list differs from the seven shipped skills",
        errors,
    )

    charter = (ROOT / "phase_project.md").read_text(encoding="utf-8")
    for expected in (
        "## OKF relationships",
        "## Agent signatures",
        ".worktrees/",
        # "history_origin: born-native" — migration-era field; not part of the
        #   generic contract, which has no legacy history to protect.
    ):
        require(expected in charter, f"phase_project.md missing {expected}", errors)

    if errors:
        print("\n".join(f"ERROR: {error}" for error in errors))
        return 1

    print(
        "Phase skills validation passed: "
        f"{len(SKILLS)} skills at version {version} across "
        f"{len(MIRRORS)} exact mirror roots, 3 exact agent guides, "
        f"{len(required_assets) + 1} scaffold files"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
