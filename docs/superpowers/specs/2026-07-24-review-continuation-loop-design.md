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

### Observable result classification

The runner result is classified before any semantic adjudication:

- `status: success` plus exactly one valid verdict is a substantive review.
  `BLOCKED` remains a substantive verdict and enters owner adjudication.
- No structured result, or `status: failed` after permitted permission/proxy
  recovery, is an invocation failure with no verdict.
- A correctable local invocation, input, or configuration error is repaired
  without changing the request and does not consume the rebuilt-request retry.
- If the unchanged invocation still fails, the owner uses the one
  rebuilt-request retry below.

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

The active node owner assigns and freezes task size before the first review.
The direct parent may reject the assignment during acceptance. A task is
`small` only when all of these are true:

- one localized artifact or behavior is reviewed;
- no architecture, public interface, persistent state, migration, permission,
  external effect, or cross-module contract changes;
- the change is reversible and its acceptance evidence is local.

Every other task is `medium_or_large`. When uncertain, use
`medium_or_large`.

The clearance threshold is:

- `small`: one independent reviewer clearance;
- `medium_or_large`: two independent reviewer clearances.

Two clearances require distinct context-independent executions against the
final frozen subject. Each reviewer runs in a separate process/session, receives
only the frozen subject and declared evidence, and does not receive another
reviewer's output. The same model may be reused unless the active contract
requires model independence. These are assurance requirements, not majority
votes.

The frozen subject is the declared artifact set plus its exact digests,
acceptance set, and evidence boundary. Any byte, artifact membership,
acceptance, or evidence-boundary change to that set creates a new subject and
invalidates every prior clearance. The new final subject must obtain the full
required clearance count. A change outside the declared subject does not
invalidate it unless it changes a supplied claim or proving evidence.

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

`IMPORTANT` is a `HIGH` alias used by external review systems. An equivalent
material finding is any label that the active reviewer contract defines as
acceptance-blocking. `MEDIUM` and `LOW` do not block clearance unless the active
acceptance contract explicitly promotes them.

`ACCEPTABLE_WITH_FIXES` can contribute clearance only after the above
conditions hold. `BLOCKED` is not automatically binding, but overriding it
requires a complete disposition record containing finding ID, reviewer
verdict, owner disposition, direct evidence, reasoning, contract impact,
resolution status, subject digest, and deciding authority. It cannot bypass a
design or architecture dispute.

## Automation boundary

The runner remains a single-review, read-only adapter. Semantic request repair,
finding adjudication, and authorized target changes remain with the node owner.
A small feedback writer automates only durable failure reporting.

`write_framing_feedback.py` accepts the role, target identity, two request
files, two failed result JSON files, one diagnosis Markdown file, and an output
directory. It refuses either result unless `status` is `failed`. It writes one
Markdown artifact named from UTC date, role, target slug, and UTC time. For
each request it records path, SHA-256, byte count, and line count; for each
failure it records the complete JSON envelope. It also records the diagnosis,
causal uncertainty, terminal reason, and required next action.

Atomicity covers creation of the one feedback artifact: write and `fsync` a
temporary file in the destination directory, then publish it with
`os.replace`. Existing final paths are never overwritten. The two original
request and result files remain separate preserved inputs.

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
