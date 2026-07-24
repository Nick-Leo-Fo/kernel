# 04 — V1 Design, Implementation, and Verification

## Delivery decision

**Approved:** the canonical system remains a pure-file protocol. V1 also ships
a default Local Guard. Git hooks and CI are optional adapters.

The session corrected an important wording problem:

- **advisory** describes guidance or semantic judgment;
- **detective** describes mechanical observation of non-compliance;
- **preventive** describes a refusal only at the exact controlled command or
  external enforcement boundary.

Text instructions are not hard constraints. A same-authority process with raw
filesystem access can bypass the Local Guard. Local JSON cannot authenticate a
non-bypassable external CI authority.

## Stable automation rule

The user observed that long, repeated shell fragments should not be rewritten
by each Agent. The accepted rule promotes a command into a parameterized script
when it is reusable, mechanically stable, and error-prone to reproduce. Folder
initialization and other fixed protocol mutations therefore belong in durable
scripts rather than prose command sequences.

This became both:

- a reusable command-promotion rule in the Build Procedure; and
- stable Skill tooling for initialization and Git-adapter installation.

## Implemented V1 shape

The global Skill contains:

- a concise `SKILL.md` entrypoint;
- domain, lifecycle, file, operation, recovery, validation, executor, and
  provenance references;
- six Procedure references;
- Project and Work Node templates;
- deterministic Local Guard;
- optional Git adapter;
- bootstrap automation.

Canonical node history remains:

```text
ledger/decisions.jsonl
ledger/approvals.jsonl
ledger/attempts.jsonl
```

All three share one contiguous per-node sequence. Frozen contracts, mutable
projections, immutable Return Packets, writer ownership, workspace evidence,
and recovery artifacts have separate roles.

## Review decisions

Multiple independent reviewers were used during the long design audit because
the user explicitly requested attacks on:

1. whether the process was sufficient and robust enough for the intended
   effect; and
2. whether duplicated or unnecessary process could be removed safely.

Reviewer findings were treated as evidence, not commands. Accepted corrections
included honest enforcement boundaries, subject-bound adjudication wording,
and deterministic evidence labels. A demand for full operation-wide
transactions was not made a V1 release blocker because the design explicitly
uses fail-closed recovery artifacts rather than promising rollback.

## Certified baseline

The 2026-07-23 certification recorded:

- 39 Skill files;
- standard-library/POSIX runtime only;
- 36 deterministic checks passing;
- 9 fresh-context behavior checks passing;
- removable installation;
- 21 accepted V1 criteria;
- no claim of adoption before two real project users.

The audit-log change in this session adds one deterministic fixture. The
historical certification file remains evidence for the prior frozen subject;
new validation evidence must identify the updated Skill digest rather than
rewriting the old claim.

## Residual V1 limits

- Raw same-authority writes remain possible.
- Semantic truth is not mechanically proved.
- Multi-file mutation recovery is not transaction rollback.
- Git integration and cleanup are not automatic.
- Hooks remain bypassable.
- External CI prevention must be established outside local JSON.
- Real adoption and process value remain unproven until live cases exist.
