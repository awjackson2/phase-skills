#!/usr/bin/env python3
"""Validate and render the project's knowledge bundle.

The bundle root is ``development/``. Everything inside it is a concept:

    development/
      index.md        reserved  bundle root index
      log.md          reserved  dated bundle change log
      .okfignore      reserved  inclusion boundary
      design/         curated current-state concepts
      phase_log/      phase plan and log concepts

Evidence and analysis — audits, triage notes, scratch research — live OUTSIDE
the bundle so the directory needs no ignore file to be understood. This file
and the schema it enforces live beside it in ``scripts/okf/`` rather than
inside the bundle they describe.

Stdlib only, on purpose: a freshly bootstrapped project should be able to run
`python3 scripts/okf/manage_bundle.py validate` before installing anything.

Commands:
    validate    check every concept against the contract (exit 1 on any error)
    build       regenerate scripts/okf/graph.json from the authored links
    inventory   report what is and is not currently a concept
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = Path(__file__).resolve().parent
DEVELOPMENT = ROOT / "development"
DESIGN = DEVELOPMENT / "design"
PHASE_LOG = DEVELOPMENT / "phase_log"
ROOT_INDEX = DEVELOPMENT / "index.md"
ROOT_LOG = DEVELOPMENT / "log.md"
IGNORE_FILE = DEVELOPMENT / ".okfignore"
GRAPH = SCHEMA / "graph.json"

RESERVED_MARKDOWN = {"index.md", "log.md"}
REQUIRED_FRONTMATTER = ("type", "title", "description", "tags")

PHASE_FILE_RE = re.compile(
    r"^phase_(?P<number>\d+(?:\.\d+)*)_(?P<kind>plan|log)\.md$"
)
MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

PHASE_STATUSES = frozenset(
    {"planned", "active", "paused", "completed", "stopped", "abandoned"}
)
DELIVERY_STATUSES = frozenset({"none", "partial", "complete", "unknown"})

RELATIONSHIP_HEADING = "## OKF relationships"
PLAN_LABELS = frozenset(
    {"Builds on", "Superseded by", "Continued by",
     "Intended design impact", "Intended knowledge impact", "Evidence"}
)
LOG_LABELS = frozenset(
    {"Plan", "Builds on", "Supersedes", "Superseded by", "Continued by",
     "Verified design impact", "Verified knowledge impact", "Evidence"}
)
PLAN_IMPACT = {"Intended design impact", "Intended knowledge impact"}
LOG_IMPACT = {"Verified design impact", "Verified knowledge impact"}

# Placeholder links inside the shipped templates. They are illustrative, not
# broken — the template is not a real concept until it is copied and filled in.
TEMPLATE_PLACEHOLDER_LINKS = {
    "phase_X.Y.Z_plan.md",
    "phase_A.B.C_log.md",
    "../design/example.md",
    "../../scripts/okf/profile.md",
}

IGNORE_RULES = (
    "*",
    "!index.md",
    "!log.md",
    "!.okfignore",
    "!design/",
    "!design/**",
    "!phase_log/",
    "phase_log/*",
    "!phase_log/phase_*_plan.md",
    "!phase_log/phase_*_log.md",
)


@dataclass(frozen=True)
class Concept:
    concept_id: str
    path: Path
    metadata: dict
    body: str


@dataclass
class Report:
    errors: list[str] = field(default_factory=list)

    def add(self, path: Path, message: str) -> None:
        try:
            where = path.relative_to(ROOT).as_posix()
        except ValueError:
            where = str(path)
        self.errors.append(f"{where}: {message}")


# --------------------------------------------------------------------------
# Front matter
# --------------------------------------------------------------------------

def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Parse the small YAML subset the contract needs.

    Supported: `key: scalar`, `key: [a, b]`, and block lists of `- item`.
    Quotes are stripped. Anything more exotic is a deliberate non-goal — keep
    front matter boring so it stays diffable and stdlib-parseable.
    """

    if not text.startswith("---\n"):
        raise ValueError("missing YAML front matter")
    try:
        _, raw, body = text.split("---\n", 2)
    except ValueError as exc:
        raise ValueError("unterminated YAML front matter") from exc

    data: dict = {}
    key: str | None = None
    for line in raw.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith(("  - ", "- ")):
            if key is None:
                raise ValueError("list item before any key")
            data.setdefault(key, [])
            if not isinstance(data[key], list):
                raise ValueError(f"{key}: mixes a scalar and a list")
            data[key].append(_scalar(line.split("- ", 1)[1]))
            continue
        if ":" not in line:
            raise ValueError(f"cannot parse front-matter line: {line!r}")
        key, _, value = line.partition(":")
        key, value = key.strip(), value.strip()
        if not value:
            data[key] = []
        elif value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            data[key] = [_scalar(p) for p in inner.split(",")] if inner else []
        else:
            data[key] = _scalar(value)
    return data, body


def _scalar(value: str):
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


# --------------------------------------------------------------------------
# Bundle boundary and discovery
# --------------------------------------------------------------------------

def in_bundle(path: Path) -> bool:
    """Mirror the `.okfignore` inclusion boundary."""

    resolved = path.resolve()
    if not resolved.is_relative_to(DEVELOPMENT.resolve()):
        return False
    rel = resolved.relative_to(DEVELOPMENT.resolve())
    if len(rel.parts) == 1:
        return rel.name in {"index.md", "log.md", ".okfignore"}
    if rel.parts[0] == "design":
        return True
    if rel.parts[0] == "phase_log" and len(rel.parts) == 2:
        return bool(PHASE_FILE_RE.fullmatch(rel.name))
    return False


def bundle_markdown() -> list[Path]:
    if not DEVELOPMENT.is_dir():
        return []
    return sorted(p for p in DEVELOPMENT.rglob("*.md") if in_bundle(p))


def schema_markdown() -> list[Path]:
    """Schema concepts living beside this validator, outside the bundle."""

    return sorted(
        p for p in SCHEMA.glob("*.md") if p.name.lower() not in RESERVED_MARKDOWN
    )


def concept_id_for(path: Path) -> str:
    resolved = path.resolve()
    if resolved.is_relative_to(SCHEMA):
        return f"okf/{resolved.relative_to(SCHEMA).with_suffix('').as_posix()}"
    return resolved.relative_to(DEVELOPMENT.resolve()).with_suffix("").as_posix()


def discover(report: Report | None = None) -> list[Concept]:
    concepts: list[Concept] = []
    for path in [*bundle_markdown(), *schema_markdown()]:
        if path.name.lower() in RESERVED_MARKDOWN:
            continue
        try:
            metadata, body = parse_frontmatter(path.read_text(encoding="utf-8"))
        except ValueError as exc:
            if report is None:
                raise
            report.add(path, str(exc))
            continue
        concepts.append(Concept(concept_id_for(path), path, metadata, body))
    return concepts


# --------------------------------------------------------------------------
# Relationship footer
# --------------------------------------------------------------------------

def _heading_offsets(text: str) -> list[int]:
    """Offsets of the relationship heading, ignoring fenced code blocks.

    Templates and plans legitimately *show* an example footer inside a fence;
    splitting on a naive substring match would treat the example as the real
    footer and corrupt the record.
    """

    offsets: list[int] = []
    fence: tuple[str, int] | None = None
    offset = 0
    for line in text.splitlines(keepends=True):
        content = line.rstrip("\r\n")
        opened = re.match(r"^[ \t]{0,3}(`{3,}|~{3,})", content)
        if opened:
            token = opened.group(1)
            if fence is None:
                fence = (token[0], len(token))
            elif token[0] == fence[0] and len(token) >= fence[1]:
                fence = None
        elif fence is None and content.strip() == RELATIONSHIP_HEADING:
            offsets.append(offset)
        offset += len(line)
    return offsets


def split_footer(path: Path) -> tuple[str, str]:
    """Return (narrative, footer) for a phase record, from the raw file text."""

    text = path.read_text(encoding="utf-8")
    offsets = _heading_offsets(text)
    if len(offsets) != 1:
        raise ValueError(
            f"expected exactly one final {RELATIONSHIP_HEADING!r} section, "
            f"found {len(offsets)}"
        )
    return text[: offsets[0]], text[offsets[0]:]


def footer_labels(footer: str) -> list[str]:
    return [
        m.group(1).strip()
        for m in re.finditer(r"(?m)^-\s+([^:]+):", footer)
    ]


# --------------------------------------------------------------------------
# Link checking
# --------------------------------------------------------------------------

def _link_target(source: Path, raw: str) -> Path | None:
    target = raw.strip().split(maxsplit=1)[0].strip("<>")
    if not target or target.startswith(("#", "http://", "https://", "mailto:")):
        return None
    target = unquote(target.split("#", 1)[0].split("?", 1)[0])
    return (source.parent / target).resolve() if target else None


def broken_links(path: Path, text: str) -> list[str]:
    broken = []
    for raw in MARKDOWN_LINK_RE.findall(text):
        if raw in TEMPLATE_PLACEHOLDER_LINKS:
            continue
        target = _link_target(path, raw)
        if target is not None and not target.exists():
            broken.append(raw)
    return broken


# --------------------------------------------------------------------------
# Validation
# --------------------------------------------------------------------------

def _validate_common(concept: Concept, report: Report) -> None:
    for field_name in REQUIRED_FRONTMATTER:
        value = concept.metadata.get(field_name)
        if field_name == "tags":
            if not isinstance(value, list) or not value:
                report.add(concept.path, "tags must be a non-empty list")
        elif not isinstance(value, str) or not value.strip():
            report.add(concept.path, f"missing required {field_name}")


def _validate_phase(concept: Concept, report: Report) -> None:
    match = PHASE_FILE_RE.fullmatch(concept.path.name)
    if not match:
        return
    kind = match.group("kind")
    expected_type = "Phase Plan" if kind == "plan" else "Phase Log"
    meta = concept.metadata

    if meta.get("type") != expected_type:
        report.add(concept.path, f"type must be {expected_type!r}")
    if meta.get("phase") != match.group("number"):
        report.add(
            concept.path,
            f"phase must match the filename value {match.group('number')!r}",
        )
    if meta.get("phase_status") not in PHASE_STATUSES:
        report.add(
            concept.path,
            "phase_status must be one of " + ", ".join(sorted(PHASE_STATUSES)),
        )
    if meta.get("delivery_status") not in DELIVERY_STATUSES:
        report.add(
            concept.path,
            "delivery_status must be one of "
            + ", ".join(sorted(DELIVERY_STATUSES)),
        )
    recorded = meta.get("recorded_on")
    if not isinstance(recorded, str) or not ISO_DATE_RE.fullmatch(recorded):
        report.add(concept.path, "recorded_on must be a quoted ISO date")

    try:
        _, footer = split_footer(concept.path)
    except ValueError as exc:
        report.add(concept.path, str(exc))
        return

    labels = set(footer_labels(footer))
    allowed = PLAN_LABELS if kind == "plan" else LOG_LABELS
    for label in sorted(labels - allowed):
        report.add(concept.path, f"unknown relationship label {label!r}")
    if not labels & (PLAN_IMPACT if kind == "plan" else LOG_IMPACT):
        report.add(
            concept.path,
            f"relationship footer requires an "
            f"{'intended' if kind == 'plan' else 'verified'} impact label",
        )
    if not MARKDOWN_LINK_RE.search(footer):
        report.add(concept.path, "relationship footer must contain a link")

    # Only the footer is link-checked. A narrative legitimately references
    # source paths and prior states that move or disappear over time; failing a
    # record for that would make history a maintenance burden.
    for raw in broken_links(concept.path, footer):
        report.add(concept.path, f"broken local link {raw}")

    paired = concept.path.with_name(
        f"phase_{match.group('number')}_{'log' if kind == 'plan' else 'plan'}.md"
    )
    if kind == "log":
        if not paired.is_file():
            report.add(concept.path, "a log requires its plan to exist")
        else:
            linked = {
                _link_target(concept.path, raw)
                for raw in MARKDOWN_LINK_RE.findall(footer)
            }
            if paired.resolve() not in linked or "Plan" not in labels:
                report.add(
                    concept.path,
                    "log footer must link its plan with the Plan label",
                )


def _validate_pairs(concepts: list[Concept], report: Report) -> None:
    by_path = {c.path.resolve(): c for c in concepts}
    seen: set[frozenset[Path]] = set()
    for path, concept in by_path.items():
        match = PHASE_FILE_RE.fullmatch(path.name)
        if not match:
            continue
        other = path.with_name(
            f"phase_{match.group('number')}_"
            f"{'log' if match.group('kind') == 'plan' else 'plan'}.md"
        )
        if other not in by_path:
            continue
        key = frozenset({path, other})
        if key in seen:
            continue
        seen.add(key)
        for name in ("phase", "phase_status", "delivery_status"):
            if concept.metadata.get(name) != by_path[other].metadata.get(name):
                report.add(path, f"paired {name} disagrees with its counterpart")


def _validate_structure(report: Report) -> None:
    if not DEVELOPMENT.is_dir():
        report.errors.append("development/: bundle root is missing")
        return
    for required in (ROOT_INDEX, ROOT_LOG, IGNORE_FILE):
        if not required.is_file():
            report.add(required, "reserved bundle file is missing")
    if DESIGN.is_dir() and not (DESIGN / "index.md").is_file():
        report.add(DESIGN / "index.md", "design index is missing")

    strays = sorted(
        p for p in DEVELOPMENT.iterdir()
        if p.name not in {"index.md", "log.md", ".okfignore", "design", "phase_log"}
    )
    for stray in strays:
        report.add(
            stray,
            "development/ holds only concepts — move evidence, notes, and "
            "tooling outside the bundle",
        )

    if IGNORE_FILE.is_file():
        active = tuple(
            line.strip()
            for line in IGNORE_FILE.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        )
        if active != IGNORE_RULES:
            report.add(IGNORE_FILE, "active rules do not match the bundle boundary")


def validate() -> int:
    report = Report()
    _validate_structure(report)
    concepts = discover(report)

    ids: set[str] = set()
    for concept in concepts:
        if concept.concept_id in ids:
            report.add(concept.path, f"duplicate concept id {concept.concept_id!r}")
        ids.add(concept.concept_id)
        _validate_common(concept, report)
        if PHASE_FILE_RE.fullmatch(concept.path.name):
            _validate_phase(concept, report)
        else:
            for raw in broken_links(
                concept.path, concept.path.read_text(encoding="utf-8")
            ):
                report.add(concept.path, f"broken local link {raw}")
    _validate_pairs(concepts, report)

    if report.errors:
        print("\n".join(report.errors))
        return 1

    phases = sum(bool(PHASE_FILE_RE.fullmatch(c.path.name)) for c in concepts)
    designs = sum(c.path.parent == DESIGN for c in concepts)
    print(
        f"Knowledge bundle valid: {len(concepts)} concepts "
        f"({designs} design, {phases} phase)"
    )
    return 0


# --------------------------------------------------------------------------
# Graph
# --------------------------------------------------------------------------

def edges(concepts: list[Concept]) -> list[tuple[str, str]]:
    by_path = {c.path.resolve(): c.concept_id for c in concepts}
    found: list[tuple[str, str]] = []
    for concept in concepts:
        text = concept.path.read_text(encoding="utf-8")
        for raw in MARKDOWN_LINK_RE.findall(text):
            target = _link_target(concept.path, raw)
            if target is not None and target in by_path:
                pair = (concept.concept_id, by_path[target])
                if pair[0] != pair[1] and pair not in found:
                    found.append(pair)
    return found


def build() -> int:
    report = Report()
    concepts = discover(report)
    if report.errors:
        print("\n".join(report.errors))
        return 1
    payload = {
        "nodes": [
            {
                "id": c.concept_id,
                "type": c.metadata.get("type", ""),
                "title": c.metadata.get("title", ""),
                "path": c.path.relative_to(ROOT).as_posix(),
            }
            for c in sorted(concepts, key=lambda c: c.concept_id)
        ],
        "edges": [
            {"source": s, "target": t} for s, t in sorted(edges(concepts))
        ],
    }
    GRAPH.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(
        f"Graph refreshed: {len(payload['nodes'])} concepts, "
        f"{len(payload['edges'])} relationships"
    )
    return 0


def inventory() -> int:
    inside = bundle_markdown() + schema_markdown()
    print(f"In the bundle ({len(inside)}):")
    for path in inside:
        print(f"  {path.relative_to(ROOT).as_posix()}")
    if DEVELOPMENT.is_dir():
        outside = sorted(
            p for p in DEVELOPMENT.rglob("*.md") if not in_bundle(p)
        )
        if outside:
            print(f"\nInside development/ but NOT concepts ({len(outside)}):")
            for path in outside:
                print(f"  {path.relative_to(ROOT).as_posix()}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate", help="check every concept against the contract")
    sub.add_parser("build", help="regenerate the graph")
    sub.add_parser("inventory", help="report concept coverage")
    args = parser.parse_args(argv)
    return {"validate": validate, "build": build, "inventory": inventory}[
        args.command
    ]()


if __name__ == "__main__":
    sys.exit(main())
