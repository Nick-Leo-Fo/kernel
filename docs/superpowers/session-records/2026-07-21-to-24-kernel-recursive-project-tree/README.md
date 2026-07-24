# Kernel → Recursive Project Tree Session Record

**Conversation window:** 2026-07-21 through 2026-07-24

**Purpose:** Preserve the reasoning, approved decisions, corrections, implementation evidence, and deferred options from one long exploration-and-build session.

This is a classified decision record, not a verbatim transcript. Statements are
labelled by state:

- **Implemented:** exists in the referenced files or verified runtime.
- **Approved:** the user accepted the design or decision.
- **Proposed:** discussed but not approved for implementation.
- **Deferred:** intentionally awaits a real operating case.
- **Superseded:** an earlier interpretation or proposal was corrected.

## Reading order

1. [Kernel evaluation and takeaways](01-kernel-evaluation-and-takeaways.md)
2. [Provenance Core and TimesFM transfer](02-provenance-core-timesfm-transfer.md)
3. [Recursive Project Tree requirements](03-recursive-project-tree-requirements.md)
4. [V1 design, implementation, and verification](04-v1-design-implementation-and-verification.md)
5. [Attention, logging, and external research](05-attention-logging-and-external-research.md)
6. [Deferred routes and Case 001](06-deferred-routes-and-case-001.md)

## Current decision

Use Recursive Project Tree V1 as the baseline pure-file protocol plus Local
Guard. Run one real project case before selecting additional lifecycle
injection, ready-work discovery, claim leasing, patrol automation, or stacked
branch management. The new Guard audit stream records the case without
pretending to observe activity outside the Guard boundary.

## Primary evidence

- `docs/evaluations/kernel-investment-evaluation-2026-07-21.md`
- `docs/evaluations/kernel-module-absorption-guide-2026-07-21.md`
- `docs/evaluations/kbot-finance-cross-project-takeaways-2026-07-21.md`
- `docs/evaluations/kernel-future-absorption-backlog-2026-07-22.md`
- `docs/superpowers/specs/2026-07-22-recursive-project-tree-design.md`
- `docs/superpowers/plans/2026-07-23-recursive-project-tree-v1.md`
- `docs/superpowers/evidence/recursive-project-tree-v1/`

The evaluation directory was pre-existing and user-owned during the logging
change; this session record links to it but does not rewrite it.
