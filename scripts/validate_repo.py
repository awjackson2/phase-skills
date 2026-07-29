#!/usr/bin/env python3
"""Validate phase-skills mirrors and OKF-native scaffold invariants."""

from __future__ import annotations

import json
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


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def validate_skill(skill: str, errors: list[str]) -> None:
    source_dir = ROOT / skill
    mirror_dir = ROOT / ".agents" / "skills" / skill
    source = source_dir / "SKILL.md"
    mirror = mirror_dir / "SKILL.md"
    require(source.is_file(), f"{source.relative_to(ROOT)} is missing", errors)
    require(mirror.is_file(), f"{mirror.relative_to(ROOT)} is missing", errors)
    if not source.is_file() or not mirror.is_file():
        return

    source_files = {
        path.relative_to(source_dir)
        for path in source_dir.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    }
    mirror_files = {
        path.relative_to(mirror_dir)
        for path in mirror_dir.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    }
    require(
        source_files == mirror_files,
        f"{skill}: root and .agents file trees differ",
        errors,
    )
    for relative in sorted(source_files & mirror_files):
        require(
            (source_dir / relative).read_bytes()
            == (mirror_dir / relative).read_bytes(),
            f"{skill}: mirror differs at {relative}",
            errors,
        )

    source_bytes = source.read_bytes()
    require(
        source_bytes == mirror.read_bytes(),
        f"{skill}: root and .agents skill mirrors differ",
        errors,
    )
    text = source_bytes.decode("utf-8")
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


def main() -> int:
    errors: list[str] = []

    for skill in SKILLS:
        validate_skill(skill, errors)

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
        ".okfignore",
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
    schema_assets = ROOT / "phase-project-init" / "assets" / "scripts" / "okf"
    for relative in ("manage_bundle.py", "profile.md"):
        require(
            (schema_assets / relative).is_file(),
            f"phase-project-init asset missing: scripts/okf/{relative}",
            errors,
        )
    require(
        not (ASSETS / "OKF").exists(),
        "development/OKF/ is superseded: the schema layer lives in scripts/okf/",
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
        # would make this validator stricter than manage_bundle.py, and the two
        # disagreeing is worse than either rule alone.
        require(
            "wrapper" in design_text.lower() and "copy" in design_text.lower(),
            "design template must prohibit wrappers and copied bodies",
            errors,
        )

    plugin_path = ROOT / ".claude-plugin" / "plugin.json"
    plugin = json.loads(plugin_path.read_text(encoding="utf-8"))
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
        f"{len(SKILLS)} exact skill mirrors, 3 exact agent guides, "
        f"{len(required_assets) + 1} scaffold files"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
