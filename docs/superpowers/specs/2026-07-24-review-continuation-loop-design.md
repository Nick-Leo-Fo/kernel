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
local preflight
→ local invocation/input/config valid?
    no  → correct locally before any external reviewer call, or stop as a
          local setup failure
    yes → external reviewer call 1
          → substantive completed review?
              yes → owner adjudication
              no  → invocation failure or framing-inconclusive
                    → preserve result → self-audit framing → rebuild once
                    → external reviewer call 2
                    → substantive completed review?
                        yes → owner adjudication
                        no  → preserve both results
                              → both status:failed?
                                  yes → write framing feedback → stop
                                  no  → report unresolved mixed gap → stop
owner adjudication
→ accepted or unresolved material finding?
    yes → pause current stage → record disposition → resolve or escalate
    no  → apply authorized necessary fixes
          → materially changed subject? refreeze and re-review
          → clearance threshold met? continue next authorized stage
          → otherwise invoke the next required independent reviewer
```

Existing permission and `--no-proxy` recovery remains inside one invocation
attempt. A substantive `BLOCKED` verdict is not a framing failure.

One review round has one shared retry budget. At most two controller-level
external reviewer calls are permitted in one review round: the initial request
and one rebuilt-request retry. A framing-inconclusive outcome consumes the same
retry as an invocation failure. A local preflight failure is not a reviewer
invocation and cannot be used to add external calls.

### Observable result classification

The runner result is classified before any semantic adjudication:

- `status: success` plus exactly one valid verdict is a substantive review.
  `BLOCKED` remains a substantive verdict and enters owner adjudication.
- A completed review is framing-inconclusive only when it cannot answer the
  selected role's decision because the decision is ambiguous or role-mismatched,
  target identity is unclear, or authorized available evidence was omitted.
  It consumes the one shared retry budget rather than entering adjudication.
- No structured result, or `status: failed` after permitted permission/proxy
  recovery, is an invocation failure with no verdict.
- A correctable local invocation, input, or configuration error is found and
  repaired during preflight, before the first external reviewer call.
- If local preflight cannot establish a valid invocation, the owner stops with
  a local setup failure; it does not consume or expand the two-call sequence.

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

After the second non-substantive outcome, stop without a third call. When both
results have `status: failed`, write one durable diagnostic under
`/Users/evan/dev/DOCS/reviewer_framing_feedback`. It records both request
identities and failure envelopes, the repair delta, the caller's causal
diagnosis, and uncertainty. For a mixed framing-inconclusive/runner-failure
sequence, preserve both complete results and report the unresolved gap; do not
misclassify the successful result to satisfy the two-failed-result writer. No
diagnostic may claim framing caused an opaque backend failure without evidence.

## Clearance policy

For this contract:

- **preflight** means local validation of the five required request sections,
  readable evidence paths, selected role, runner arguments, and local
  configuration before an external reviewer process is started;
- **request framing** means the structural composition and claim-to-evidence
  mapping of those five sections, without changing claim substance;
- **direct parent** means the immediate owning node that accepts or rejects the
  current node's return;
- **acceptance set** means the named completion conditions plus the review-gate
  facts—task size, required clearances, roles, and independence—that must hold
  for the current subject;
- **Local Guard** means RPT's local preventive command for protocol mutations;
  a Guard-routed mutation is one submitted through that command rather than a
  direct file edit.

The active node owner assigns and freezes task size before the first review.
The direct parent may reject the assignment during acceptance. Task-size
rejection invalidates the current review gate because task size belongs to the
acceptance set. The owner records the reason, freezes the corrected task size
and subject, and obtains the full required clearance count again. A task is
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
Any accepted or unresolved material finding pauses the current stage until it
is resolved, disproved, or escalated to the owning authority. Additional
reviewer calls cannot resolve an accepted material finding and must not be used
as votes to bypass it.

### RPT verdict translation

Raw `project-review` verdicts and findings remain immutable evidence. The RPT
owner appends finding dispositions and computes the final RPT lifecycle verdict;
it never rewrites the external result. No RPT verdict follows from
`ACCEPTABLE`, `ACCEPTABLE_WITH_FIXES`, or `BLOCKED` alone.

- `ACCEPTABLE` can become `approved` only when every RPT exit condition holds,
  or `approved_with_nonblocking_findings` when only recorded nonblocking
  findings remain.
- `ACCEPTABLE_WITH_FIXES` is `changes_required` while an accepted correction
  remains. After verified repair and required re-review, the final result is
  recomputed from the current subject.
- `BLOCKED` is `changes_required` when the owner accepts an actionable material
  correction within current authority. It is `inconclusive` with
  `needs_parent` when evidence, independence, subject identity, or deciding
  authority is missing or disputed. Override requires the complete record
  below plus every ordinary RPT exit condition.
- Missing acceptance evidence, unavailable required independence, or a changed
  or unverifiable subject always produces `inconclusive` with `needs_parent`,
  regardless of the external verdict.

The RPT Review Procedure owns the exact finding-status translation and final
mapping table.

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
4. A deterministic script refuses each result unless its `status` is `failed`,
   atomically writes one feedback artifact containing both failure envelopes,
   and preserves request hashes, sizes, and the caller diagnosis.
5. Existing project-review tests, RPT fixtures, and both skill validators pass.
