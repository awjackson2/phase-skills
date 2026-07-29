# OKF-Native Phase Knowledge

These skills treat Open Knowledge Format as the **creation** format for phase
tracking, not as an export or a later migration target. A project installed by
`phase-project-init` writes conforming records from its first phase onward, so
there is never a normalization pass to schedule.

## Bundle shape

```text
development/            the bundle — concepts only
├── index.md            reserved: bundle root index
├── log.md              reserved: dated bundle change log
├── .okfignore          reserved: inclusion boundary
├── design/             curated current state
│   ├── index.md
│   └── _element_template.md
└── phase_log/          phase history
    ├── phase_index.md
    ├── phase_plan_template.md
    └── phase_log_template.md

scripts/okf/            the schema and its validator, beside each other
├── manage_bundle.py
└── profile.md
```

Two properties of that shape carry most of the value.

**`development/` holds only concepts.** Evidence — audits, triage notes, scratch
research, meeting records — lives elsewhere in the repository. It may support a
claim but never becomes current-state authority, so it sits outside the bundle
by construction rather than by an exclusion rule. The validator refuses strays,
which is what lets a reader understand the directory without opening
`.okfignore`.

**The schema lives outside the bundle it describes.** `scripts/okf/` holds the
profile and the validator next to each other, so the rule and its enforcement
move together. A rule that lives only in prose drifts away from the rule that is
actually checked.

## What a concept is

Every concept carries YAML front matter:

| Field | Applies to | Notes |
|---|---|---|
| `type`, `title`, `description`, `tags` | all concepts | `tags` is a non-empty list |
| `phase` | phase records | must equal the number in the filename |
| `phase_status` | phase records | `planned` · `active` · `paused` · `completed` · `stopped` · `abandoned` |
| `delivery_status` | phase records | `none` · `partial` · `complete` · `unknown` |
| `recorded_on` | phase records | quoted ISO date |

Phase records also end with exactly one `## OKF relationships` footer using
controlled labels — `Builds on`, `Plan`, `Intended design impact`,
`Verified design impact`, `Evidence`, and their siblings. Relationships are
ordinary relative Markdown links, so they are navigable documentation and graph
edges at the same time.

## Rules worth knowing before you hit them

**Writing a log also edits its plan.** A plan and its log must agree on `phase`,
`phase_status`, and `delivery_status`. Because the log is written last, closing a
phase updates the plan's front matter to the reviewed outcome. The plan's
*narrative* still reads "Status: Planned" — that is deliberate, preserving the
state in which it was authored.

**Only the footer is link-checked on phase records.** A narrative legitimately
references source paths and prior states that later move or disappear; failing a
record for that would turn history into a maintenance burden. Design concepts are
checked in full.

## Running it

```bash
python3 scripts/okf/manage_bundle.py validate    # enforce the contract
python3 scripts/okf/manage_bundle.py build       # regenerate the graph
python3 scripts/okf/manage_bundle.py inventory   # what is and is not a concept
```

The validator is **stdlib only** by design: a freshly bootstrapped project must
be able to run it before installing anything, so it ships a small front-matter
parser rather than depending on a YAML library.

If your CI skips tests for documentation-only changes, gate the validator on its
own paths (`development/**`, `scripts/okf/**`) rather than on the code-changed
signal. Otherwise the one change shape most likely to break the bundle — a
phase-record-only pull request — is the one shape that never gets checked.

## Scope

There is no migration manifest, review ledger, narrative digest, or born-native
boundary here. Those mechanisms exist to protect history that predates the
format; a project that starts OKF-native has none, so the contract stays small
enough to read in one sitting.
