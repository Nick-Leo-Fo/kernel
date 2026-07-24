# 03 — Recursive Project Tree Requirements

## Pain being solved

Large projects drift. A branch or side task created to solve a parent problem
can acquire new goals, spawn more work, and never return with evidence that it
actually helped the parent. The user wanted a pure folder-management system
whose structure makes responsibility and return explicit.

## Approved recursive ownership model

Every node has one direct parent and a complete injected context:

- why it exists;
- objective and bounded scope;
- acceptance criteria;
- authorized reads, writes, effects, resources, and risk;
- inherited decisions and invariants;
- workspace/Git binding when relevant;
- return target and return rules.

A node can diverge in only two legitimate ways:

1. create a bounded child that is directly responsible to it; or
2. return completion, blockage, redesign need, or termination to its parent.

A child is responsible only to its direct parent. Ancestors influence it
through inherited contracts, not direct parallel authority.

## Two node forms

**Project Node:** long-lived, independently governed, architecture- and
roadmap-owning work.

**Work Node:** bounded stage, task, debug, review, research, design,
experiment, or integration work with the smaller required structure.

A Work Node that develops a durable independent objective does not silently
grow into a project. It returns `successor_required`; its parent creates a new
Project Node that cites the predecessor and Return Packet.

## Execution controller

On entry, Goal Pursuit must reconstruct persisted truth, plan ready Subgoals,
bind acceptance and a failing gate, select the current Procedure, execute
within authority, verify, review at the required risk level, and continue until
return or a genuine material gate.

The fixed Procedures are:

- Build
- Debug
- Review
- Research
- Design
- Integration

A Procedure is not another project hierarchy. Temporary switches use a stack
frame with an exit condition and exact `return_to`, so Debug or Review cannot
become an unbounded side route.

## Attempt and failure accounting

Kernel's useful execution shape was retained:

```text
plan → act → observe → reflect → decide
```

The unit of repetition is a stable `progress_scope_id`, not an Agent, model,
branch, node label, Procedure, or renamed Subgoal. Progress must change the
failing gate or relevant decision information. At the third consecutive
no-progress Attempt:

- execution enters `redesign_required`;
- a fourth Attempt on the same route is prohibited;
- preserved attempts and hypotheses return to the parent for redesign.

This is the accounting mechanism the user connected to Debug: before trying
again, establish why the last route failed; after three causally stagnant
cycles, reject the design rather than extending the branch indefinitely.

## Acceptance and integration kept separate

The design distinguishes:

```text
node-local satisfaction
→ immutable Return submission
→ direct-parent adjudication
→ latest-parent combination verification
→ integration authorization
→ actual merge
```

Passing inside a child branch does not prove it remains useful against the
current parent. A parent cannot accept a hidden active descendant, and an
accepted child is not automatically integrated.

## Authority model

Routine in-contract execution proceeds without repeated human prompts.
Structured adjudication is required when objective, acceptance, scope,
authority, resources, effects, risk, or integration target changes. Human
intervention is reserved for the named human boundary, destructive or
irreversible effects, security/legal/credential matters, root-mainline
integration, or user-reserved choices.
