---
title: Reviewer Continuation Loop Design
date: 2026-07-24
status: approved
scope:
  - /Users/evan/.codex/skills/project-review
  - /Users/evan/.codex/skills/recursive-project-tree
---

# Reviewer Continuation Loop

## Problem

The current reviewer runner returns a structured result, but the caller often
treats that tool return as a human-intervention boundary. This breaks Goal
Pursuit even when the node contract authorizes request repair, finding
adjudication, bounded fixes, re-review, and phase continuation.

`project-review` also requires an immediate stop on a remaining runner failure,
while RPT does not define how many independent clearances are required by task
size. The two contracts therefore cannot produce a deterministic review gate.

## Decision

A reviewer invocation is not a turn boundary. It is one event inside the
active node's Review Procedure.

The owner follows this controller:

```text
preflight request
→ invoke reviewer
→ runner failure?
    yes → preserve result → self-audit framing → rebuild once → retry
          → second failure → write framing feedback → stop
    no  → independently adjudicate every finding
          → apply authorized necessary fixes
          → materially changed subject? refreeze and re-review
          → clearance threshold met? continue next authorized stage
          → otherwise invoke the next required independent reviewer
```

Existing permission and `--no-proxy` recovery remains inside one invocation
attempt. A substantive `BLOCKED` verdict is not a framing failure.

## Request repair boundary

The retry preserves role, target identity, stated intent, evidence authority,
model, timeout, and claim coverage. It may:

- remove unrelated cross-role material;
- replace caller summaries with exact evidence;
- identify the target and dependency boundary precisely;
- make claim-to-evidence mappings local and explicit;
- separate unavailable evidence and exclusions.

It may not change the reviewed claim, hide adverse evidence, narrow required
coverage, add unsupported evidence, or steer toward a desired verdict.

After a second failed runner result, stop and write one durable diagnostic
under `/Users/evan/dev/DOCS/reviewer_framing_feedback`. The diagnostic records
both request identities and failure envelopes, the repair delta, the caller's
causal diagnosis, and uncertainty. It must not claim framing caused an opaque
backend failure without evidence.

## Clearance policy

Task size is frozen before review:

- `small`: one independent reviewer clearance;
- `medium_or_large`: two independent reviewer clearances.

When uncertain, use `medium_or_large`. Two clearances require distinct
independent reviewer executions against the final frozen subject. They are
assurance requirements, not majority votes.

One reviewer clearance exists when the owner records that:

- the review completed successfully and is bound to the current subject;
- no accepted or unresolved `BLOCKER`, `HIGH`, `IMPORTANT`, or equivalent
  material finding remains;
- every finding has an evidence-backed disposition;
- any necessary authorized non-material correction was applied;
- any material subject change was re-reviewed.

The owner may reject a nitpick, irrelevant concern, or severity inflation with
an evidence-backed reason and still issue clearance. A design or architecture
finding may not be skipped: it must be resolved, disproven with direct
evidence, or escalated to the authority that owns the disputed decision.

`ACCEPTABLE_WITH_FIXES` can contribute clearance only after the above
conditions hold. `BLOCKED` is not automatically binding, but overriding it
requires the same complete disposition record and cannot bypass a design or
architecture dispute.

## Automation boundary

The runner remains a single-review, read-only adapter. Semantic request repair,
finding adjudication, and authorized target changes remain with the node owner.
A small feedback writer automates only durable failure reporting.

The file protocol remains advisory, validation and clearance checks are
detective, and Local Guard is preventive only for Guard-routed protocol
mutations.

## Acceptance

1. A contract test fails against the old skills and passes after the change.
2. `project-review` explicitly states that reviewer invocation is not a turn
   boundary and routes to the continuation contract.
3. RPT Review defines task-size clearance, retry, owner adjudication, re-review,
   and automatic continuation.
4. A deterministic script refuses successful results, records two failures
   atomically, and preserves request hashes, sizes, and the caller diagnosis.
5. Existing project-review tests, RPT fixtures, and both skill validators pass.
