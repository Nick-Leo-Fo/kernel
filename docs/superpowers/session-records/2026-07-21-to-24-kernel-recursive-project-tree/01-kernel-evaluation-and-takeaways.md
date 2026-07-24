# 01 — Kernel Evaluation and Takeaways

## Original decision question

The session began by indexing the current Kernel branch and evaluating both the
whole repository and independently usable parts. The evaluation system had to
score completion, usefulness, value, and technical lead, while primarily
guiding internal iteration priority without an artificial resource ceiling.
The user required:

- component-level scores before a portfolio summary;
- explicit treatment of parts that can be used independently;
- current branch and latest commit as the first observation boundary;
- an approved evaluation contract before judgment;
- dangerous access choices shown explicitly, with ordinary read-only access
  otherwise allowed;
- a reusable evaluation workflow written in English under
  `~/.codex/skills`, while conversation remained Chinese.

## Result

**Implemented evaluation verdict:** Kernel is valuable as a mechanism library,
not as a system to merge wholesale. The evaluated active composition scored
52.5/100 and was classified as project sprawl. This did not mean its modules
were valueless; it meant repository-level breadth, wiring, and evidence did not
justify adopting the complete product as one framework.

The distinction that governed later work was:

```text
module value ≠ whole-project fit ≠ current integration priority
```

High-value mechanisms included:

- tool registry and middleware separation;
- UI adapter boundaries;
- context budgeting and compaction;
- content-addressed request identity;
- append-only decision and attempt records;
- outcome wrappers;
- structured approvals bound to exact subjects;
- execution-loop and no-progress feedback ideas.

Conditional or low-priority parts were retained in a future absorption backlog
rather than discarded. This preserves future option value when another project
develops the missing conditions.

## Corrected interpretation of `kbot-finance`

**Superseded:** “kbot-finance is conventional finance functionality.”

**Accepted correction:** its important reusable role is governance around an
AI-to-engine request: normalize what was requested, bind versions and input
identity, apply rules and approval, record the result, and make cost/outcome
auditable. Finance is the original domain wrapper; the transferable value is
provenance and controlled execution.

It is therefore closer to an Agent request-accounting and provenance layer
than to a portfolio, pricing, or trading engine.

## Integration principle

Do not force every useful Kernel module into an existing repository. When the
current framework lacks a shared role, define a small new shared contract
instead. The highest-value initial gap was not “another Agent loop”; it was a
common language for request, artifact, rule evaluation, decision, and outcome.

## Evidence boundary

The detailed module scores, implementation maturity scale, and source-level
findings remain in the four files under `docs/evaluations/`. This record
captures the decisions that caused the later Provenance Core and Recursive
Project Tree work; it does not duplicate every score.
