# Recursive Project Tree — Design

**Date:** 2026-07-22

**Last amended:** 2026-07-23

**Status:** Approved design; implementation not started

**Source project:** Kernel at `main@7dcf0a6a1bb2d21a176b36241bcc97a002e5f456`

**Planned delivery:** Global Codex skill at `~/.codex/skills/recursive-project-tree/`

**Planned skill language:** English

## 1. Problem

Large projects drift during development. A branch created to solve a bounded problem can acquire new objectives, spawn additional work, and remain indefinitely detached from its intended parent. The project may retain code but lose the answers to more important questions:

- Why was this branch or stage created?
- What exact parent state did it start from?
- What was it authorized to change?
- Which acceptance criteria determine whether it worked?
- Which decisions were made, what alternatives were rejected, and why?
- Did repeated failures produce new information, or did the same approach merely repeat?
- Can the result return to the current parent branch, rather than only pass in isolation?
- Who has authority to accept, revise, reject, redesign, or integrate it?

The desired system is a pure filesystem governance model. It must remain human-readable and usable without a database or daemon. Git branches and worktrees are optional external adapters; they are not the source of project authority.

## 2. Goals

1. Represent a project as a recursive tree of accountable work nodes.
2. Give every node a frozen purpose, scope, acceptance contract, authority, and direct parent.
3. Allow a node only two forms of divergence: create a bounded child or return to its parent.
4. Preserve decisions, approvals, attempts, evidence, and outcomes for later review.
5. Detect repeated no-progress cycles and force a structured return for redesign.
6. Separate task completion, parent acceptance, and Git integration.
7. Make unbound branches, orphaned worktrees, stale candidates, and hidden active descendants visible.
8. Support a full project form and a lighter stage/task/debug form.
9. Begin as a global Codex skill plus file templates; defer a standalone CLI until real use proves the interface.
10. Let an executor pursue an approved goal without routine permission prompts while preserving explicit material gates.
11. Make Build, Debug, Review, Research, Design, and Integration repeatable evidence-producing Procedures.
12. Recover the same responsibility, attempts, Subgoals, and Procedure stack after interruption or executor replacement.

## 3. Non-goals

- Replacing Git, worktrees, CI, tests, or domain-specific promotion engines.
- Building a central project database or universal orchestration runtime.
- Automatically merging, deleting, rebasing, or pushing branches.
- Giving every routine action a human approval gate.
- Treating an append-only JSONL file as WORM storage.
- Copying Kernel's monolithic agent loop, hierarchical planner runtime, or agent-os runtime wholesale.
- Making a child responsible directly to every ancestor.
- Allowing a successful isolated branch test to imply successful parent integration.

## 4. Kernel evidence and extraction boundary

This design combines mechanisms that exist in Kernel, while preserving their actual maturity and limitations.

| Kernel source | Verified implemented shape | Extracted role | Required correction |
|---|---|---|---|
| `packages/kbot/src/engineering-loop.ts` | `plan → act → observe → reflect → decide`, checkpoint, verify gate, no-progress handback, tests | Per-node attempt lifecycle | Replace generic handback with structured parent return and `redesign_required` |
| `packages/kbot/src/decision-journal.ts` | Append-only daily JSONL containing decision, reasoning, alternatives, confidence, evidence, and optional outcome | Decision record vocabulary | Add stable IDs, node links, subject revisions, supersession, and separate outcome records |
| `packages/kbot/src/task-ledger.ts` | Facts, hypotheses, plan, progress, cost, failure-based replan, atomic checkpoint | Distinguish task knowledge from execution progress | Use append-only attempt events; do not rely on a mutable in-memory ledger as history |
| `packages/agent-os/src/outcomes.ts` | Rubric evaluation, revision feedback, bounded attempts, abort handling, history | Structured evaluate/revise loop | Parent acceptance and design escalation remain separate responsibilities |
| `packages/kbot/src/planner/hierarchical/types.ts` and `DESIGN.md` | Goals, phases, actions, acceptance and exit criteria, plus a revise-action/phase/goal/abort ladder | Escalate from the cheapest local correction to contract-level reconsideration | The hierarchical runtime is feature-gated scaffolding; adopt the decision ladder, not a claim of production orchestration |
| `packages/kbot/src/planner/hierarchical/dag.ts` | Scoped context from a subgoal and its ancestor summaries, dependency readiness, topological ordering, and cycle detection | Give a node only the context required for its responsibility | The helper is not wired as a runtime, and this design preserves a single-parent governance tree rather than importing a general DAG |
| `packages/kbot/src/marketplace.ts` bundled Code Reviewer and Debugger | Review categories and reproduce/hypothesize/bisect/verify debugging prompts | Seed fixed review and debug Procedures | These are prompt configurations, not a unified auditable workflow |
| `packages/kbot/src/critic-taxonomy.ts` | Typed evidence, contradiction, belief-update, repetition, and resume failures; three-identical-call detection | Failure classification and repetition safeguards | Count causal progress, not only identical tool calls |
| `packages/kbot/src/reasoning.ts` | Abductive hypotheses, test actions, counterfactuals, and meta-planning | Research and debug evidence discipline | Treat it as a reasoning reference, not a production controller |
| `packages/kbot/src/handoffs.ts` | Handoff depth and cycle checks | Guard against unbounded delegation | Filesystem parentage and Return Packets remain authoritative |
| `packages/agent-os/src/spawn.ts` and `acap.ts` | Parent identity, purpose, child budget, child limit, downscope helper | Parent/child identity and non-escalation rule | Current spawn path does not fully enforce all capability-subset guarantees; v1 uses explicit file validation |
| `kbot-finance` governance/provenance | Request identity, subject-bound approval shape, rule reports, audit reference | Bind approval to an exact node, contract revision, candidate, or return packet | No production HMAC approval system is required for local v1 |

The resulting system is a new composition at a filesystem seam. It is not a claim that Kernel already ships this directory system.

## 5. Domain model

### 5.1 Project Node

A long-lived, independently governed project or subproject. It owns a roadmap, domain context, architecture, multiple stages, and its own child tree.

### 5.2 Work Node

A bounded execution node. Its `work_kind` is one of:

```text
stage | task | debug | review | research | design | experiment | integration
```

A Work Node may create Work Node children. It must yield to a Project Node when it gains a long-lived independent objective, multiple stages, an independent roadmap, architecture ownership, or a separate maintenance lifecycle. This is not an in-place type change: the Work Node returns, its parent creates a successor Project Node, and the successor contract cites the original node and Return Packet.

`work_kind` is advisory navigation metadata. It helps humans distinguish stages, tasks, and specialized work, and may seed a default primary Procedure, but it does not grant authority, change lifecycle semantics, or constrain later bounded Procedure switches.

### 5.3 Parent Contract

The context, objective, scope, exclusions, authority, acceptance criteria, workspace binding, and return rules that the direct parent injects when creating a child.

### 5.4 Attempt

One `plan → act → observe → reflect → decide` cycle inside a Work Node.

### 5.5 Return Packet

The structured statement by which a child reports completion, blockage, redesign need, or termination to its direct parent.

### 5.6 Parent Adjudication

The direct parent's decision to accept, request revision, require redesign, or reject a returned child.

### 5.7 Workspace Binding

An optional reference from a node to an external repository, branch, worktree, baseline commit, candidate commit, and expected return ref.

### 5.8 Goal Pursuit

The single execution controller for an active node. It enters the node, orients from persisted facts, maintains the adaptive plan, selects a ready Subgoal, runs the applicable Procedure, verifies evidence, reviews according to risk, and decides whether to continue, delegate, return, or escalate.

### 5.9 Subgoal

An adaptive plan item inside one node. It becomes a child Work Node only when responsibility, context, authority, failure history, review, or acceptance must be isolated. A Subgoal is not automatically a node.

### 5.10 Procedure

A reusable policy for how a class of work is executed and evidenced. V1 defines `build`, `debug`, `review`, `research`, `design`, and `integration`. Procedure is orthogonal to `work_kind`: a task may primarily build, temporarily debug, and invoke review without changing node identity.

### 5.11 Procedure Frame

One entry on the active Procedure stack. It records why the Procedure was invoked, the Subgoal it serves, its exit condition, and the exact point to which control must return.

### 5.12 Executor Adapter

The role that performs a Procedure: the current agent, a child agent, an independent reviewer, or a human authority. Executor choice does not create or erase filesystem responsibility. A node persists when its executor or session changes.

### 5.13 Local Satisfaction

The Goal Pursuit result that every node-local acceptance criterion has verified evidence. For a non-root node, local satisfaction authorizes only submission of a Return Packet and transition to `ready_to_return`; it is never parent acceptance.

### 5.14 Materiality

Materiality classifies decisions that require structured adjudication rather than routine plan adaptation. A change is material when it affects contract objective, acceptance, outward scope, exclusions, authority, resource category or ceiling, external effects, risk ceiling, or integration target. Adjudicating a high-severity unresolved finding is also material. Materiality does not by itself mean the adjudicator must be human.

## 6. Core invariants

1. The filesystem responsibility tree is authoritative; Git is an adapter.
2. Every node has one stable `node_id` and immutable node type; directory names and paths may change.
3. Every non-root node has exactly one direct `parent_id`.
4. A child may narrow but never silently expand its parent's scope, authority, or budget.
5. A child returns only to its direct parent.
6. A child may declare `ready_to_return`; it may not declare itself accepted or integrated.
7. A node may either create a bounded child or return upward when its current contract no longer contains the work.
8. One node has at most one active writer. Parallel work requires child nodes.
9. Historical ledger entries are append-only; corrections are new records.
10. Three consecutive no-progress attempts force `redesign_required`; a fourth attempt is forbidden.
11. A parent cannot accept a child with undisclosed active descendants.
12. Node completion, parent acceptance, integration verification, and actual merge remain distinct facts.
13. The Parent Contract is frozen authority; `PLAN.md` is adaptive execution strategy and may not amend the contract.
14. Every temporary Procedure switch declares an exit condition and `return_to`; a switch without a return target is scope drift.
15. Required verification is fail-closed. A warning, skipped check, or Reviewer opinion cannot turn failed or missing evidence into acceptance.
16. Node identity, attempt history, no-progress count, and descendants survive agent, model, process, and session replacement.
17. Self-review and independent review are distinct facts; unavailable independence is reported as inconclusive, never simulated.
18. Every projection field required for recovery is reconstructable from frozen contracts, append-only records, immutable Return Packets, and live measurement.
19. Every append-only record in one node carries the next contiguous `node_sequence`, giving records across separate ledgers one recoverable total order and exposing missing events.

## 7. Directory structures

### 7.1 Project Node

```text
<project-node>/
├── NODE.md
├── CONTRACT.md
├── PLAN.md
├── STATUS.md
├── ROADMAP.md
├── CONTEXT.md
├── ARCHITECTURE.md
├── ledger/
│   ├── decisions.jsonl
│   ├── approvals.jsonl
│   └── attempts.jsonl
├── evidence/
├── returns/
├── children/
└── RETURN.md
```

### 7.2 Work Node

```text
<work-node>/
├── NODE.md
├── CONTRACT.md
├── PLAN.md
├── STATUS.md
├── ledger/
│   ├── decisions.jsonl
│   ├── approvals.jsonl
│   └── attempts.jsonl
├── evidence/
├── returns/
├── children/
└── RETURN.md
```

Every listed file and directory exists from node creation. An empty ledger is an empty file, not a missing file. `evidence/`, `returns/`, and `children/` may be empty. A root Project Node marks `RETURN.md` as `not_applicable`; every non-root node maintains a current Return Packet projection and preserves submitted packets in `returns/`.

Project Nodes must maintain `ROADMAP.md`, `CONTEXT.md`, and `ARCHITECTURE.md`. Work Nodes inherit the relevant frozen context through `CONTRACT.md` and do not create parallel top-level governance documents.

Contract amendment proposals are added as `AMENDMENT-0001.md`, `AMENDMENT-0002.md`, and so on. They do not silently overwrite the original contract. Each proposal names one contiguous `from_revision` and `to_revision`, declares structured field changes, includes the resulting effective contract summary, and receives subject-bound adjudication. Revision gaps, forks among approved amendments, and two approved amendments claiming the same `to_revision` are invalid. Rejected proposals remain historical but do not enter the effective chain or reserve a revision number.

## 8. File responsibilities

| File | Responsibility | Mutability |
|---|---|---|
| `NODE.md` | Stable identity, node type, work kind, parent, creation rationale, and navigation | Identity fields immutable; path references may be repaired |
| `CONTRACT.md` | Frozen revision-1 parent contract: objective, acceptance, scope, exclusions, authority, resources, and workspace binding | Frozen after activation; later revisions are append-only amendment files |
| `PLAN.md` | Current Goal Pursuit orientation, Subgoals, dependencies, Procedure stack, verification, review, and return target | Adaptive; may change inside the contract but never amend it |
| `STATUS.md` | Current execution, parent-verdict, integration, blocking, and next-action projection | Mutable and required to remain current |
| `ROADMAP.md` | Project-stage structure and priority | Project Nodes only |
| `CONTEXT.md` | Stable domain terminology and relationships | Project Nodes only; no plans or implementation details |
| `ARCHITECTURE.md` | Modules, interfaces, seams, dependencies, and invariants | Project Nodes only |
| `decisions.jsonl` | Decisions, rationale, alternatives, evidence, confidence, and later outcome links | Append-only |
| `approvals.jsonl` | Subject-bound creation, amendment, authority, return, and integration decisions | Append-only |
| `attempts.jsonl` | Plan, act, observe, reflect, and decide events | Append-only |
| `evidence/` | Test reports, review findings, manifests, diff summaries, and other verification artifacts | Additive; replacement requires explicit supersession |
| `returns/` | Immutable submitted packets named `RETURN-0001.md`, `RETURN-0002.md`, and so on | Append-only; exact packet IDs and digests are approval subjects |
| `children/` | Direct children only | Managed through `spawn-child` semantics |
| `RETURN.md` | Current child-authored Return Packet projection and pointer to the latest immutable submitted packet | Mutable by the child before the next submission; never rewritten by the parent |

## 9. Node identity

`NODE.md` begins with YAML frontmatter:

```yaml
schema_version: 1
node_id: 01K...
node_type: project
work_kind: null
parent_id: null
created_at: 2026-07-22T00:00:00+08:00
```

Use a stable ULID-like identifier. Human-readable directory names are labels, not identity. Moving or archiving a node does not change `node_id`.

`CONTRACT.md` begins with:

```yaml
schema_version: 1
contract_id: ctr_01K...
node_id: 01K...
revision: 1
supersedes_revision: null
parent_contract_id: ctr_01J...
parent_contract_revision: 3
created_at: 2026-07-22T00:00:00+08:00
```

A root contract sets both parent-contract fields to `null`.

Revision 1 is the frozen file. An amendment begins with:

```yaml
schema_version: 1
amendment_id: amd_01K...
contract_id: ctr_01K...
from_revision: 1
to_revision: 2
created_at: 2026-07-23T00:00:00+08:00
changes:
  acceptance: [add AC-03]
effective:
  objective: Preserve the approved objective
  acceptance_criterion_ids: [AC-01, AC-02, AC-03]
  reads: [src/]
  writes: [src/adapter.ts, tests/adapter.test.ts]
  effect_classes: [local_filesystem]
  authority: delegated_implementation
  resource_ceiling: parent_defined
  risk_ceiling: medium
```

The active contract revision is the highest contiguous approved revision starting from 1. Its effective digest is SHA-256 over a UTF-8 manifest containing, in order, the literal relative filename and SHA-256 file digest of `CONTRACT.md` and each approved amendment, one `filename digest` pair per LF-terminated line. The approval record for that highest approved contract subject is the canonical active-revision fact; rejected proposals do not advance it or enter the digest manifest. `STATUS.md` only projects that revision and digest. Review subjects, Return Packets, and integration approvals bind both values.

Every amendment is compared cumulatively with revision 1 and with the direct parent's current authority. A semantic project-purpose change cannot be disguised as a sequence of individually small amendments; it requires return and a successor node.

## 10. Lifecycle model

Do not compress completion into one status. `STATUS.md` maintains three axes.

### 10.1 Execution status

```text
proposed → approved → active
                      ↕
                    blocked
active | blocked → ready_to_return
ready_to_return → active | closed
active → redesign_required | aborted
```

`blocked` may return to `active` only when the named external condition changes, or move to `ready_to_return` when the child hands the blocked route back to its parent. `redesign_required` and `aborted` are terminal for the current node execution contract.

### 10.2 Parent verdict

```text
not_submitted | pending | accepted | revision_requested | rejected
```

### 10.3 Git integration status

```text
unbound | working | candidate | integration_verified | integrated |
superseded | abandoned
```

Examples:

```yaml
execution_status: closed
parent_verdict: accepted
integration_status: candidate
```

The work was accepted but has not yet been verified against and merged into the current parent ref.

### 10.4 Required status projection

`STATUS.md` begins with the current projection:

```yaml
schema_version: 1
node_id: 01K...
execution_status: active
parent_verdict: not_submitted
integration_status: working
contract_id: ctr_01K...
contract_revision: 1
effective_contract_digest: sha256:...
active_writer:
  kind: agent
  id: agent_01K...
executor_mode: self
current_attempt: 2
current_attempt_phase: observe
active_subgoal: SG-03
primary_procedure: build
procedure_stack:
  - procedure: debug
    invoked_by: SG-03
    reason: Baseline test fails intermittently
    return_to: build/SG-03
    exit_condition: Root cause demonstrated and regression test passes
consecutive_no_progress: 1
progress_scope_id: pgs_01K...
current_failing_gate: integration-test
active_children:
  - 01M...
last_decision_id: dec_01N...
last_event_at: 2026-07-22T12:00:00+08:00
last_checkpoint_at: 2026-07-22T12:00:00+08:00
last_node_sequence: 42
next_action: Test adapter serialization independently
```

The prose body explains the current blocker, evidence, and next action. It does not reproduce historical ledger entries. Update it after contract approval, every completed attempt, child creation or return, blocker changes, Return Packet submission, parent adjudication, measured Git changes, integration, and before ending a work session.

`STATUS.md` is a projection, not a historical authority. If it conflicts with append-only ledgers or live Git, record the discrepancy and repair the projection; do not rewrite the evidence to match the status summary.

### 10.5 Normative transition mapping

Goal Pursuit and parent adjudication update the three axes as follows:

| Event | Execution status | Parent verdict | Integration status |
|---|---|---|---|
| Contract approved | `approved`, then `active` on entry | `not_submitted` | `working` or `unbound` |
| Local satisfaction or bounded parent decision needed | `ready_to_return` | `not_submitted` | `candidate` or unchanged |
| Named external condition prevents work | `blocked` | unchanged | unchanged |
| Return Packet submitted | unchanged and no new acts allowed | `pending` | unchanged |
| Parent accepts a completed or handed-back blocked Return Packet | `closed` | `accepted` | unchanged until separate integration |
| Parent accepts `successor_required` | `closed` | `accepted` | `superseded` after the successor contract is approved |
| Parent requests bounded revision and the contract remains valid | `active` | `revision_requested` | `working` or `unbound`; the prior packet remains historical |
| Revised Return Packet submitted | `ready_to_return` | `pending` | `candidate` or unchanged |
| Parent rejects and terminates the route | `closed` | `rejected` | `abandoned` |
| Goal Pursuit requires redesign | `redesign_required` | `not_submitted`, then `pending` on submission | unchanged |
| Goal Pursuit aborts | `aborted` | `not_submitted`, then `pending` on submission | `abandoned` unless explicitly retained |
| Parent accepts a redesign or abort report | remains terminal | `accepted` | unchanged |
| Accepted candidate passes current-parent combination verification | unchanged | `accepted` | `integration_verified` |
| Authorized integration completes and post-checks pass | unchanged | `accepted` | `integrated` |

`revision_requested` is corrective continuation, not rejection. It is illegal for `redesign_required` or `aborted` without a separately approved terminal-node reopening; the ordinary route is a cited successor node. A new Return submission changes `revision_requested` to `pending` and binds a new immutable packet.

## 11. Parent-child protocol

### 11.0 Root initialization

The root Project Node receives a user-approved charter rather than a parent contract. Its `parent_id` is `null`; the user or explicitly named external authority approves revision 1. The charter still freezes objective, acceptance, scope, exclusions, authority, resources, and optional workspace binding. The root may not silently expand these fields merely because it has no parent; material changes require a new user approval and amendment.

### 11.1 Spawn

The direct parent:

1. allocates the stable child ID, target path, and proposed contract digest;
2. appends a `spawn_intent` decision before creating the directory;
3. creates the complete child directory in `proposed` state and writes the Child Contract;
4. validates child identity, parent identity, structure, and contract digest against the intent;
5. records subject-bound contract approval and a `spawn_activated` decision;
6. changes the child to `approved`, then allows entry as `active`.

Spawn is recoverable rather than assumed atomic. An intent without a directory may be completed or explicitly abandoned. A directory without a matching parent intent is an orphan and cannot activate. Validation is bidirectional: every direct child has exactly one parent `spawn_intent`, and every non-abandoned intent resolves to exactly one child with the allocated ID. Recovery never creates a second node merely because activation was interrupted.

`spawn_intent` records `child_id`, relative path, node type, advisory work kind, `contract_id`, revision, proposed digest, and creation reason. `spawn_activated` references that intent, the measured child identity and contract digest, and the approval ID. `spawn_abandoned` references the intent and reason and never reuses its child ID.

The Child Contract injects:

- parent node and contract revision;
- creation reason and question to answer;
- frozen context summary;
- relevant source paths, digests, and decision IDs;
- objective and acceptance criteria with stable criterion IDs;
- permitted semantic scope, explicit exclusions, structured read/write paths, and effect classes;
- authority, resource ceiling, and risk ceiling;
- inherited decisions and invariants;
- required review and executor-independence level;
- optional Git workspace binding;
- return and failure rules.

References provide provenance; the frozen summary provides independent comprehensibility. A child must not require scanning every ancestor document to understand its task.

### 11.2 Downscope

A child may narrow inherited scope, authority, resources, and external effects. Expansion requires return to the parent and an approved amendment or a new node. If the change alters project purpose rather than clarifying execution, create a new node.

### 11.3 Direct-parent responsibility

A child may understand ancestor constraints but modifies and returns only to its direct parent. Evidence about an ancestor design problem travels upward one parent at a time.

## 12. Legal divergence

An active node has two legal ways to handle work outside its immediate next action.

### 12.1 Spawn downward

Create a child when the new problem remains inside the current contract, has independent acceptance criteria, and can return a bounded result.

### 12.2 Return upward

Return when the contract is complete, blocked, invalid, requires redesign, has lost value, or needs broader scope, authority, resources, or external effects.

Forbidden alternatives include silent scope expansion, undeclared branches, ancestor modification, bypassing the direct parent, and repeated unrecorded retries.

## 13. Decision, approval, and attempt ledgers

### 13.0 Common record envelope

Every JSONL record begins with:

```json
{
  "schema_version": 1,
  "record_type": "...",
  "event_id": "evt_01K...",
  "node_id": "01K...",
  "node_sequence": 42,
  "created_by": { "kind": "agent", "id": "..." },
  "created_at": "..."
}
```

`node_sequence` increases contiguously across all three ledgers, not separately per file. Duplicate, missing, or non-monotonic sequence values fail validation. This total order is the canonical source for reconstructing `STATUS.md`, active Subgoal, failing gate, Procedure stack, executor takeover, and no-progress state. Every record that changes a recovery-critical projection includes a structured `state_delta`; activation and writer ownership use decision records, while Subgoal, gate, and Procedure changes normally use Attempt `decide` records.

### 13.1 Decision record

```json
{
  "schema_version": 1,
  "record_type": "decision",
  "event_id": "evt_01K...",
  "decision_id": "dec_01K...",
  "node_id": "01K...",
  "node_sequence": 42,
  "question": "How should the failing integration gate be addressed?",
  "decision_type": "implementation",
  "decision": "Replace the adapter seam instead of patching the caller",
  "reasoning": ["The mismatch appears in two callers"],
  "alternatives": [
    {
      "option": "Patch caller A only",
      "rejected_because": "It preserves duplicated conversion rules"
    }
  ],
  "evidence_refs": ["evidence/test-failure-02.md"],
  "confidence": 0.72,
  "expected_outcome": "Both callers pass the same interface test",
  "supersedes": null,
  "created_by": { "kind": "agent", "id": "..." },
  "created_at": "..."
}
```

Observed results are appended separately:

```json
{
  "schema_version": 1,
  "record_type": "decision_outcome",
  "event_id": "evt_01M...",
  "node_id": "01K...",
  "node_sequence": 43,
  "decision_id": "dec_01K...",
  "observed_outcome": "Caller A passed; caller B still failed",
  "assessment": "mixed",
  "evidence_refs": ["evidence/test-report-03.md"],
  "created_by": { "kind": "agent", "id": "..." },
  "created_at": "..."
}
```

### 13.2 Approval record

```json
{
  "schema_version": 1,
  "record_type": "approval",
  "event_id": "evt_01N...",
  "approval_id": "apr_01K...",
  "node_id": "01K...",
  "node_sequence": 44,
  "subject": {
    "kind": "contract",
    "id": "ctr_01K...",
    "revision": 1,
    "effective_digest": "sha256:..."
  },
  "decision": "approved",
  "conditions": [],
  "reason": "Scope and acceptance remain within the parent contract",
  "authority": { "kind": "parent_node", "id": "01J..." },
  "state_delta": {
    "contract_revision": { "from": null, "to": 1 },
    "execution_status": { "from": "proposed", "to": "approved" }
  },
  "evidence_refs": [],
  "created_by": { "kind": "agent", "id": "..." },
  "created_at": "..."
}
```

Structured approval is required for child activation, contract amendment, authority/scope/resource expansion, return adjudication, Git integration authorization, terminal-node reopening, and parent-goal changes. Routine in-contract implementation and verification decisions do not require approval.

### 13.3 Attempt events

Every attempt uses one `attempt_id` and appends five ordered phase records:

```text
plan → act → observe → reflect → decide
```

In addition to the common envelope, the phases have these required fields:

| Phase | Required payload |
|---|---|
| `plan` | `attempt_id`, `progress_scope_id`, `subgoal_id`, active `procedure_frame`, acceptance criterion and failing gate being advanced, planned action, planned verification, and from cycle 2 `responds_to_attempt_id` plus `change_from_previous` |
| `act` | `attempt_id`, unique `action_id`, intended action, expected effect, permitted footprint, effect classification, idempotency basis, reconciliation check, partial-effect check, safe replay preconditions, rollback or compensation, and required prior approval |
| `observe` | `attempt_id`, `action_id`, actual commands or operations, exit status, measured effect, `partial_effect_status`, evidence references, failing-gate result, and comparison with the prior Attempt |
| `reflect` | `attempt_id`, causal assessment, belief update, eliminated and remaining hypotheses, contract relevance of information gained, risk update, and proposed progress assessment |
| `decide` | `attempt_id`, decision, verified progress assessment, no-progress reasons and count, next action, and a structured `state_delta` for Subgoal, failing-gate, Procedure-stack, blocker, or executor changes |

`act` is an intent checkpoint written before execution. Its effect classification is one of `verified_idempotent`, `reversible`, `irreversible`, or `unknown`. `verified_idempotent` requires a stated basis and a concrete reconciliation check; the executor's label alone is not proof. `partial_effect_check` must distinguish `none`, `partial`, `complete`, and `ambiguous` where the underlying system permits that distinction. Unknown or ambiguous external effects are not replayed.

`state_delta` in the node's ordered records is the append-only source for recovery-critical projection changes. Procedure operations are `push`, `pop`, or `none` and include the complete affected frame. Subgoal transitions record previous and next state. Failing-gate changes record previous and next gate. Executor takeover records the previous executor, evidence it is no longer writing, the new executor, and the deciding authority.

An unrun check is unverified, never passing. If execution stops before `observe`, the next executor uses the recorded reconciliation and partial-effect checks before deciding whether the action is safe to resume, compensate, or return upward.

`decide` is one of:

```text
continue | revise_subgoal | replan_node | switch_procedure |
spawn_child | request_amendment | ready_to_return | blocked |
redesign_required | abort
```

## 14. No-progress and redesign rule

Progress is evaluated against one stable progress-scope record:

```yaml
progress_scope_id: pgs_01K...
subgoal_id: SG-03
acceptance_criterion_id: AC-02
failing_gate_id: integration-test
inherits_attempt_history_from: null
```

An Attempt is `advanced` only if it moves that failing gate, eliminates a plausible cause relevant to that gate, obtains new verifiable evidence that changes the next decision for that scope, narrows its validation space, satisfies its acceptance criterion, or demonstrates that the containing contract/design is invalid.

Code volume, model replacement, agent replacement, Procedure switching, wording changes, identical command reruns, and materially equivalent fixes are not progress by themselves. Work on another Subgoal does not reset the current scope's count. Rewrapping the same objective in a new Subgoal, child, node, or Procedure inherits the prior `progress_scope_id` and count.

Each `decide` event records:

```json
{
  "progress_scope_id": "pgs_01K...",
  "acceptance_criterion_id": "AC-02",
  "failing_gate_id": "integration-test",
  "progress_assessment": "advanced",
  "contract_relevance": "Eliminated the only remaining serialization cause for AC-02",
  "no_progress_reasons": [],
  "consecutive_no_progress": 0
}
```

When one progress scope reaches three consecutive no-progress Attempts:

1. execution becomes `redesign_required`;
2. the node writes a Return Packet;
3. no fourth `plan` event for that scope is legal under the current node contract;
4. the direct parent may approve a redesigned contract, create a new design/debug/integration child, modify its own design, terminate the route, or create a cited sibling node;
5. the failed node and eliminated hypotheses remain preserved and referenced.

A successor or sibling that still advances the same acceptance criterion and failing gate inherits the original `progress_scope_id` and no-progress history. Resetting the counter requires an approved redesign that changes the causal route or invalidates the old progress scope; renaming, relocating, or repackaging the work is insufficient.

## 15. Return Packet and parent adjudication

`RETURN.md` answers:

1. Which `contract_id`, active revision, effective digest, and parent contract were executed?
2. Is the disposition `completed`, `blocked`, `redesign_required`, `successor_required`, or `aborted`?
3. What deliverables exist?
4. What is the verdict for every acceptance criterion?
5. What evidence supports each verdict?
6. What important decisions were made?
7. Which hypotheses were disproved?
8. Which risks and unknowns remain?
9. How was every direct child disposed?
10. What are the Git baseline, candidate, worktree, and dirty states?
11. What exact parent action is requested?

The requested action is one of:

```text
accept | request_revision | redesign | create_successor_project |
terminate | integrate
```

Before `ready_to_return`, every direct child must be terminal and its latest Return Packet adjudicated. V1 does not re-parent active descendants. If work must continue at another level, the current child is closed or terminated and the responsible parent creates a cited successor. Hidden or transferred follow-up work is invalid.

On submission, the child copies the complete current projection to the next immutable `returns/RETURN-NNNN.md`, records its packet ID and digest, and updates `RETURN.md` to point to it. The direct parent adjudicates that exact immutable subject. A revision request preserves the old packet and the child later submits a new packet.

Parent adjudication must:

1. verify the packet binds the child's active contract revision and effective digest;
2. resolve every evidence reference and confirm it binds the reviewed artifact or live state;
3. record for every acceptance criterion a verification method of `reproduced`, `inspected`, or `trusted_external`, plus freshness and evidence;
4. independently reproduce deterministic material checks when authorized and practical;
5. verify descendant disposition, current workspace identity, disclosed risk, and requested action;
6. append a subject-bound approval record and apply the Section 10.5 transition.

An evidence reference that merely exists is `declared`, not verified. A parent may not accept a passing criterion until its adjudication record says how the evidence was verified. `trusted_external` requires the contract to name the authority whose attestation is acceptable.

While `parent_verdict: pending`, the child appends no acts and the direct parent is the authorized adjudication writer for the child's next `node_sequence`. The parent appends the authoritative verdict to the child's `approvals.jsonl`; it may record a cross-reference in its own decision ledger. On `revision_requested`, execution ownership returns to the child through an ordered writer state change.

The parent never edits a submitted packet. Its approval record binds:

```yaml
subject:
  kind: return_packet
  id: ret_01K...
  digest: sha256:...
  contract_id: ctr_01K...
  contract_revision: 2
  effective_contract_digest: sha256:...
decision: accepted
state_delta:
  execution_status: {from: ready_to_return, to: closed}
  parent_verdict: {from: pending, to: accepted}
criterion_verifications:
  - criterion_id: AC-01
    method: reproduced
    freshness: current
    evidence_refs: [evidence/test-report-05.md]
```

`revision_requested` and `rejected` records use the corresponding Section 10.5 state delta.

For Work-to-Project succession, the Work Node returns with `successor_required` and requests `create_successor_project`. After parent acceptance, the Work Node closes with integration status `superseded`; the new Project Node receives a new contract that cites the immutable packet, prior attempts, decisions, and retained artifacts.

## 16. Git workspace adapter

A node may declare:

```yaml
workspace:
  mode: external
  repository: /absolute/path/to/repo
  baseline_ref: main
  baseline_commit: abc123
  branch: feat/example
  worktree: /absolute/path/to/worktree
  expected_return_ref: main
```

At return, the child reports a measured candidate commit, dirty state, diff summary, and verification evidence. It cannot declare itself mergeable.

The parent verifies:

1. candidate identity and worktree truth;
2. original baseline and current parent ref;
3. child-local acceptance evidence;
4. contract-scope compliance;
5. combination with the current parent state;
6. descendant closure;
7. migration and rollback needs.

Only successful combination verification yields `integration_verified`. Actual merge plus post-merge verification yields `integrated`.

If a candidate is valid alone but not against the current parent, the parent creates a bounded `integration` or `debug` Work Node. The original child does not expand indefinitely.

## 17. Drift detection

Tree validation classifies Git state as:

```text
managed branch
integrated branch
unbound branch
orphaned node
stale candidate
```

- **Managed branch:** bound to an active or returned node.
- **Integrated branch:** has an accepted Return Packet and integration evidence.
- **Unbound branch:** exists in Git but has no node.
- **Orphaned node:** claims active Git work whose branch or worktree no longer exists.
- **Stale candidate:** was measured against an old parent state and lacks current combination verification.

V1 reports these conditions. It never deletes branches or worktrees.

## 18. Validation layers

Each check is classified by the future implementation as `mechanical` or `adjudicative`. Mechanical checks compare structured fields, identities, digests, paths, transitions, and measured state. Adjudicative checks evaluate semantic purpose, evidence meaning, risk, or whether a plan remains inside a natural-language objective. V1 may guide and record both, but it must never claim that a mechanical validator proved an adjudicative judgment.

### 18.1 Structure

- Required files and directories exist.
- JSONL lines parse.
- Node IDs are unique.
- Parent IDs match the physical direct parent.
- Node type matches its template.
- Every child directory has one matching parent `spawn_intent`; every active intent resolves to one child.
- Immutable packet names and the current `RETURN.md` pointer agree.
- `PLAN.md` has a goal, primary Procedure, review policy, and return target.

### 18.2 Contract

- Revision 1, amendments, active revision, and effective digest form one contiguous approved chain without forks.
- Return, Review, Status, and approval subjects bind the same active revision and digest.
- Structured scope, authority, resources, paths, effect classes, and risk ceilings do not expand silently.
- Acceptance is non-empty.
- Workspace baseline is exact when Git-bound.
- The responsible adjudicator compares cumulative amendment meaning with revision 1 and the parent contract; this project-purpose check is adjudicative.

### 18.3 Lifecycle

- State transitions are legal.
- Controller and parent events follow the Section 10.5 mapping.
- Proposed nodes cannot execute.
- Ready-to-return nodes cannot append acts.
- Redesign-required nodes cannot begin a fourth cycle.
- Terminal nodes cannot reopen without approval.
- Parent verdicts have approval evidence.
- An active Procedure Frame has `invoked_by`, `return_to`, and an exit condition.
- An accepted Subgoal has evidence and accepted dependencies.
- A delegated Subgoal binds to a disclosed direct child.
- A known writer conflict blocks acceptance and integration; concurrency prevention itself is outside the V1 guarantee.

### 18.4 Ledger

- Common envelopes parse, IDs are unique, and `node_sequence` is contiguous and increasing across all ledgers.
- Attempt phases and referenced actions are ordered.
- `act` intent precedes the effect it describes.
- An Attempt with `act` but no `observe` is classified as incomplete and reconciled before replay.
- Every required phase field is present, and every recovery-critical state change has a valid `state_delta`.
- Later attempts respond to prior feedback.
- Record IDs and references resolve.
- Corrections append rather than rewrite history.
- `PLAN.md` and `STATUS.md` can be reconstructed from frozen facts, ordered records, and live measurement.
- Evidence references exist.
- Executor takeover preserves Attempt numbers, findings, hypotheses, progress-scope identity, and no-progress count.

### 18.5 Return

- Every immutable packet has a unique ID, digest, contract revision, and effective digest.
- Every acceptance criterion has a verdict and parent verification method.
- Passing evidence resolves, is fresh for the subject, and was reproduced, inspected, or accepted from a contract-authorized external authority.
- Direct descendants are terminal and adjudicated; V1 contains no active-child transfer.
- Risks and requested parent action are explicit.
- Redesign returns preserve attempts and eliminated hypotheses.

### 18.6 Git

- Repository, branch, and worktree exist when claimed.
- Measured commit and dirty state are truthful.
- Diff stays inside contract scope.
- Candidate verification evidence exists.
- Parent ref is freshly measured.
- Integration verification uses current parent state.

### 18.7 Goal Pursuit, Procedure, and review

- Contract acceptance maps to necessary Subgoals and evidence.
- Structured `PLAN.md` reads, writes, effects, authority, resources, and risk remain subsets of the approved contract.
- Semantic objective containment is adjudicative and its decision is recorded.
- Procedure selection satisfies its entry conditions.
- Procedure switches preserve scope and have a return target.
- Required closing verification passed; skipped or warning-only gates are not accepted.
- Review findings bind to a frozen subject and every material finding is adjudicated.
- Claimed independence matches the actual executor context and model.

### 18.8 Recovery

- Resume reconstructs authority, history, live state, descendants, and projections.
- An incomplete effect uses its recorded reconciliation and partial-effect checks before replay.
- Unknown, partial without compensation, and ambiguous external effects block replay.
- Irreversible effects have prior approval and a unique action ID.
- Procedure-stack, Subgoal, failing-gate, progress-scope, executor, and Return Packet continuity are backed by ordered records and survive session replacement.
- Parent advancement invalidates stale combination verification without rewriting child history.

## 19. Failure handling

The system fails closed for parent acceptance and Git integration when:

- JSONL is malformed;
- contract or parent approval is missing;
- parent identity is inconsistent;
- evidence is missing;
- parent adjudication records only evidence existence without a verification method;
- acceptance criteria lack verdicts;
- an active descendant is undisclosed;
- a child directory and parent spawn records do not match bidirectionally;
- contract revisions contain gaps, forks, or digest disagreement;
- work continues after the no-progress cap;
- a replacement executor resets attempt or no-progress history;
- a Procedure switch lacks a return target;
- required independent review is mislabeled or unavailable;
- required verification failed, was skipped, or is only a warning;
- an incomplete or ambiguous effect is replayed without reconciliation;
- a detected writer conflict is unresolved;
- a recovery-critical projection cannot be reconstructed;
- recorded and measured Git states disagree;
- contract-external files changed;
- the parent advanced without renewed combination verification.

Parseable but semantically wrong history is corrected by appending a correction or supersession record. A syntactically malformed JSONL ledger cannot be repaired merely by appending another line: it remains fail-closed until an authorized recovery preserves the original bytes as evidence, writes a clean replacement ledger with an explicit repair manifest, and records the replacement in the parent decision ledger. Records are not silently deleted merely to make validation pass.

## 20. Goal Pursuit controller

Goal Pursuit is the single logical execution interface:

```text
pursue(node_contract, procedure, context)
  → locally_satisfied
  → needs_parent
  → redesign_required
  → aborted
```

`locally_satisfied` means the controller found every local acceptance criterion satisfied. It maps to `execution_status: ready_to_return` and does not change `parent_verdict`. Only direct-parent adjudication can produce `parent_verdict: accepted`.

`needs_parent` maps to `ready_to_return` when the node can submit a decision request, or to `blocked` when it is waiting on a named external condition. `redesign_required` and `aborted` map to their existing terminal execution states; the controller does not introduce a fourth lifecycle axis.

The controller owns this loop:

```text
ENTER → ORIENT → PLAN → SELECT → EXECUTE
      → VERIFY → REVIEW → DECIDE → repeat or return
```

### 20.1 Enter gates

Before acting, Goal Pursuit verifies:

- execution is approved and active;
- the accepted contract revision exists and has non-empty acceptance;
- authorized reads, writes, external effects, and permissions are explicit;
- the node has at most one active writer;
- the live workspace agrees with its binding, or any discrepancy is recorded;
- no contract amendment is pending;
- the active Procedure and any Procedure Frame are known;
- previous status, attempts, descendants, and incomplete effects have been reconciled.

Missing objectives, acceptance, authority, or material permissions return to the direct parent. The executor does not invent them.

The same canonical Entry Manifest is used by interactive skill entry, Resume, and any future CLI:

```yaml
entry_manifest:
  operation:
  responsibility_tree_root:
  target_node_or_parent:
  node_type:
  work_kind:
  purpose:
  acceptance_criterion_ids:
  authorized_writes:
  authorized_effects:
  workspace_binding:
  approval_subject:
```

Fields not applicable to an operation are explicitly `not_applicable`, not omitted. This manifest is an orientation and validation input, not an additional approval gate.

### 20.2 Orientation and context scope

Orientation writes or refreshes these facts in `PLAN.md`:

- goal and why it matters;
- deliverables and acceptance;
- exclusions and allowed actions;
- inherited decisions and invariants;
- evidence already available;
- unknowns and assumptions;
- primary Procedure and active Procedure stack;
- review requirements;
- exact return target.

An executor receives the node contract, a frozen parent summary, relevant ancestor outcome summaries, accepted dependency results, and authorized tools and paths. It does not receive unrelated sibling histories by default. This adopts Kernel's scoped-context principle without changing the single-parent responsibility tree into a DAG.

## 21. Adaptive Subgoal plan

`CONTRACT.md` freezes why and what. `PLAN.md` records the current how. `STATUS.md` projects the present position. Attempt ledgers preserve history. `RETURN.md` reports upward.

`PLAN.md` begins with:

```yaml
schema_version: 1
node_id: 01K...
goal: Deliver the contract acceptance set
primary_procedure: build
active_subgoal: SG-03
procedure_stack: []
review_requirements:
  deterministic_verification: always
  self_review: always
  independent_review: risk_based
return_target:
  parent_id: 01J...
  requested_action: accept
```

For a root Project Node, `return_target` names the human or external root authority rather than a parent node.

Each Subgoal records:

```yaml
- subgoal_id: SG-03
  objective: Make adapter serialization satisfy the contract
  deliverable: Verified adapter change
  acceptance_criterion_ids: [AC-02]
  failing_gate_id: integration-test
  progress_scope_id: pgs_01K...
  acceptance:
    - AC-02 interface test passes
  depends_on: [SG-01]
  reads: [src/adapter.ts]
  writes: [src/adapter.ts, tests/adapter.test.ts]
  risk: medium
  review_level: self
  procedure: build
  status: active
```

Legal Subgoal states are:

```text
proposed → ready → active → verifying → reviewing → accepted
                         ↘ delegated
                         ↘ blocked
                         ↘ failed
                         ↘ superseded
```

Rules:

1. A Subgoal becomes ready only after its dependencies are accepted.
2. Accepted requires direct evidence for every Subgoal acceptance condition.
3. Delegated binds to one child node; the child must return and be accepted before the Subgoal can be accepted.
4. Failed triggers attribution and replanning. It does not disappear.
5. Superseded preserves the previous plan item and the reason for replacement.
6. Every Subgoal receives deterministic verification and self-review.
7. Independent review is required only by the risk policy: architecture, security, permissions, data semantics, formal conclusions, material final returns, or unresolved disagreement.

Promote a Subgoal to a child Work Node when it needs one or more of:

- an independently adjudicated contract and Return Packet;
- isolated permissions, workspace, or write scope;
- its own no-progress budget or Reviewer;
- long-running or multi-session execution;
- internal Subgoals or parallel work;
- independent acceptance or rejection;
- isolated debug, design, research, or integration responsibility;
- a reusable outcome that should not be buried in the parent attempt history.

Node-local completion requires all contract acceptance to be evidenced, necessary Subgoals to be accepted, required reviews to pass, descendants to be disposed, the live workspace to be freshly measured, Procedure closing checks to pass, and remaining risks to be explicit.

## 22. Procedure contract and switching

Every Procedure satisfies one interface:

```yaml
procedure:
  name:
  purpose:
  entry_conditions:
  required_steps:
  required_evidence:
  verification:
  review_policy:
  local_recovery:
  exit_conditions:
  escalation_conditions:
```

V1 realizes this as skill instructions and files rather than runtime classes. Goal Pursuit remains the external seam; Procedure details stay inside it.

A node selects a `primary_procedure`. A Subgoal may select another Procedure. Temporary switches use a stack:

```yaml
procedure_frame:
  procedure: debug
  invoked_by: SG-03
  reason: Baseline test fails intermittently
  return_to: build/SG-03
  exit_condition: Root cause demonstrated and regression test passes
```

An executor may switch Procedure without approval only when the same objective, deliverable, acceptance, authority, write scope, side effects, risk ceiling, and `progress_scope_id` remain intact. The switch is recorded as a decision and as an append-only Procedure `push` or `pop` in the Attempt `state_delta`. A separate child is required when the work gains independent responsibility, context, permissions, failure budget, review, duration, parallelism, or acceptance.

The decision ladder is:

```text
continue
→ revise_subgoal
→ replan_node
→ switch_procedure
→ spawn_child
→ request_amendment
→ ready_to_return
→ abort
```

Use the cheapest action that can address the evidence. A contract amendment cannot be self-approved. Required verification failure is fatal to acceptance; it is not downgraded to a warning.

## 23. Standard Procedures

### 23.1 Build

Purpose: turn an approved design or bounded task into a verified artifact without changing its contract.

Required flow:

```text
reconcile context → establish baseline → plan smallest useful slice
→ define verification → implement → verify slice
→ observe and update plan → repeat
→ verify complete acceptance set → self-review
→ risk-based independent review → freeze outcome
```

The executor measures pre-existing failures before changing files. It divides work into the smallest useful vertical slices and defines each slice's verification before implementation. Test-first behavior is preferred where observable; otherwise the plan defines a measurement, inspection, or human acceptance method first.

A failed slice enters Debug rather than triggering un-attributed edits. Local recovery may revise or replace a Subgoal, but expanded authority or purpose requires a child or amendment. Evidence includes baseline, changed artifact identity, per-slice checks, final acceptance mapping, key decisions, review dispositions, and measured Git state.

Build exits successfully only when the complete acceptance set passes. “Code written,” partial tests, or Reviewer confidence are insufficient.

### 23.2 Debug

Purpose: explain an observed deviation, prove its root cause, and remove it with the smallest justified fix.

Required flow:

```text
freeze symptom → reproduce or instrument → establish failing baseline
→ propose and rank 2–3 falsifiable hypotheses
→ run the smallest discriminating experiment → update beliefs
→ prove root cause → create regression evidence
→ apply minimal fix → verify original symptom
→ run broader regression → record prevention
```

If the symptom is not reproducible, the first task is observation or capture, not speculative editing. Each diagnostic Attempt records:

```yaml
symptom:
hypothesis:
expected_observation:
action:
actual_observation:
belief_update:
information_gained:
next_decision:
```

A root-cause claim must explain the symptom, distinguish itself from material alternatives, predict the observed change after control or repair, and leave regression evidence. “The test passed after this edit” proves correlation unless the causal link is otherwise demonstrated.

No progress means no hypothesis relevant to the active `progress_scope_id` was eliminated, no decision-changing evidence appeared, no key uncertainty on that route narrowed, or the same causal strategy was repeated with superficial changes. Agent, model, tool, Procedure, wording, Subgoal wrapper, or node-name changes do not reset the scope's counter. After two no-progress Attempts, an independent diagnosis should be sought before a third Attempt when available. The third consecutive no-progress Attempt forces `redesign_required`.

Small debugging stays on the current Procedure stack. Create a Debug child only for isolated context, authority, long-running investigation, parallel experiments, independent acceptance, or a root cause outside the node's responsibility.

### 23.3 Review

Purpose: independently judge whether a frozen subject satisfies its contract and produce findings that can be adjudicated.

Self-review is a mandatory reflective pass by the current executor. It is meaningful as a check against the contract, diff, tests, and evidence, but it provides no independence claim. The Review Procedure is separate and uses an independent execution context when the risk policy requires independent assurance.

The review subject freezes:

```yaml
node_id:
contract_revision:
git_identity:
scope:
acceptance_criteria:
evidence_locations:
review_risk:
```

Required flow:

```text
freeze subject → verify baseline claims → inspect by risk rubric
→ produce evidence-backed findings → issue provisional verdict
→ owner adjudicates findings → apply authorized changes
→ re-review material changes → issue final verdict
```

Risk-selected categories include contract compliance, correctness, evidence, security, permissions, data semantics, external effects, error handling, performance, maintainability, tests, and documentation truth.

Every finding records:

```yaml
finding_id:
claim:
evidence:
location:
severity:
contract_impact:
reasoning:
recommended_action:
status:
disposition_reason:
```

Finding status is `open`, `accepted`, `rejected`, `deferred`, or `resolved`. The Reviewer is read-only unless separately authorized to enter Build. The owner adjudicates each finding; rejection and deferral require reasons.

Verdicts are `approved`, `approved_with_nonblocking_findings`, `changes_required`, or `inconclusive`. Missing acceptance evidence, unresolved high-severity findings, changed review subjects, and material unresolved disagreement block approval. Disagreement is preserved and escalated; it is not erased by a vote.

### 23.4 Research

Purpose: answer a decision-relevant question rather than accumulate undirected information.

Entry declares the question, consuming decision, competing hypotheses, required evidence, source and freshness policy, stopping condition, and material uncertainty.

Required flow:

```text
frame decision-relevant question → identify competing hypotheses
→ define discriminating evidence → collect evidence and provenance
→ seek counterevidence → separate observation from inference
→ update confidence → test decision sensitivity
→ report conclusion and residual uncertainty
```

Each material item records its claim, source, provenance, observed fact, inference, supporting or contradicting role, reliability, freshness, and confidence effect. Legal outcomes are `supported`, `rejected`, `mixed`, `insufficient_evidence`, and `decision_not_sensitive`.

Parallel agents may gather independent evidence. The node owner synthesizes the result; a material conclusion may receive independent counter-review. Research returns current confidence, strongest counterevidence, unresolved unknowns, evidence that would change the conclusion, and the implication for its consumer.

### 23.5 Design

Purpose: convert an accepted problem and constraints into an executable, reviewable design.

Required flow:

```text
reconcile current truth → define invariants and failure modes
→ identify seams and responsibilities
→ propose 2–3 materially different approaches
→ compare trade-offs → stress-test concrete scenarios
→ select recommendation → define contracts and acceptance
→ assess migration and rollback → review material decisions
→ obtain required approval
```

The output states current facts, goals, non-goals, invariants, Modules and Interfaces, alternatives, failure handling, recommendation, acceptance, implementation stages, risks, and future extension points. An ADR is created only for a hard-to-reverse, surprising, genuine trade-off; ordinary local decisions stay in the decision ledger.

Build cannot begin until the design's acceptance, permissions, effects, review, and appropriate approval are explicit. A parent agent may approve local design inside delegated authority. Project-level purpose, architecture, risk assumption, or resource-direction change returns to the responsible human or parent authority.

### 23.6 Integration

Purpose: decide whether a child result can safely return into its direct parent and incorporate it without corrupting the parent route. Git merge is an optional Adapter, not the definition of integration.

Required flow:

```text
verify child acceptance → inspect Return Packet and risks
→ freeze child and parent identities → compare with parent contract
→ detect scope drift → dry-run integration → analyse conflicts
→ verify combined behavior → obtain appropriate approval
→ apply integration → run post-integration verification
→ record provenance → close or retain child
```

The Return Packet supplies contract revision, deliverables, acceptance evidence, changed artifacts, Git identity, decisions, risks, rejected or deferred work, integration instructions, and rollback.

A direct parent agent may accept and integrate an internal child inside delegated scope. Section 26 is the sole authority matrix for further escalation; Integration does not maintain a second gate list.

On integration failure, preserve the parent state and evidence. Create a bounded Integration or Debug Subgoal, return responsibility to the child, or create a cited successor. Do not patch the parent opportunistically merely to force a merge.

## 24. Executor model

Procedure and executor topology are separate seams. The default is a hybrid policy:

| Situation | Default executor |
|---|---|
| Planning, ordinary Build, verification, and bounded Debug | Current node owner |
| Independent Work Node | Child agent when available, otherwise sequential execution by the current agent |
| Parallel Work Nodes | Separate child agents |
| Routine self-review | Current node owner |
| Material independent review | Independent Reviewer context |
| High-risk or disputed judgment | Independent Reviewer; a different model is preferred when available |
| Material authority decision | The adjudicator selected by the Section 26 authority matrix |

A child agent provides responsibility and context isolation but may use the same model, so it does not automatically provide epistemic diversity. A different model can reduce shared bias but does not create governance authority. Model diversity is advisory in V1 because runtime model selection may be unavailable. Human authority carries only the decisions reserved for people by Section 26.

Execution requirements live in `PLAN.md`; the active executor binding is projected in `STATUS.md`:

```yaml
execution:
  owner:
    kind: agent
    id: agent_01K...
  executor_mode: self
  reviewer_mode: risk_based
  required_independence: none
```

Executor modes are `self`, `child_agent`, `independent_reviewer`, and `human`. Independence levels are `none`, `context`, and `model`.

`context` independence requires a separate executor session or process that receives only the frozen review subject, contract, acceptance, supplied evidence, and explicit exclusions; it does not inherit the owner's hidden reasoning or full chat history. `model` independence additionally requires a different model family. A new prompt in the owner's same continuing context is still self-review.

When a child agent is used, it receives the child contract, frozen parent context, allowed paths and tools, inherited decisions, acceptance, and Return Packet destination. The filesystem node, not the chat thread, is the responsibility record.

If independent review is required but no independent executor is available, the verdict is `inconclusive` and the controller returns `needs_parent`. A second self-review cannot be labeled independent.

## 25. Checkpoint, interruption, and recovery

### 25.1 Persisted truth

Recovery reconstructs four distinct kinds of fact:

- authorization from contracts, amendments, and approvals;
- history from append-only ledgers, evidence, and Return Packets;
- current material state from live files, Git, worktrees, tests, and external systems;
- execution projections from `PLAN.md` and `STATUS.md`.

Chat history is advisory only. Contracts decide authority, ledgers preserve history, live measurement determines present physical state, and mutable projections are repaired to agree with them. History is never rewritten to make a stale projection appear correct.

### 25.2 Checkpoint order

Each Attempt:

1. appends `plan`;
2. appends the `act` intent before the effect;
3. performs the action;
4. measures and appends `observe`;
5. appends `reflect` and `decide`;
6. refreshes `PLAN.md` and `STATUS.md`.

An Attempt with `act` but no `observe` is incomplete, not failed and not safe to repeat automatically. The next executor compares intended effects with live state first.

`STATUS.md` is updated after each completed Attempt, child creation or return, blocker change, Procedure switch, review verdict, measured workspace change, integration, and graceful session end. An abnormal exit may leave it stale; the ledger and live state make recovery possible.

### 25.3 Resume Procedure

```text
locate node → verify identity → read contract and approvals
→ reconstruct ledgers → inspect descendants
→ measure live filesystem/Git/external state
→ reconcile incomplete Attempt and intended effects
→ repair PLAN/STATUS → establish single writer
→ continue Goal Pursuit
```

Resume results are:

```text
resume_current_attempt | start_next_attempt | wait_for_child |
blocked | needs_parent | redesign_required | ready_to_return
```

Resume never resets Attempt numbers, `progress_scope_id`, no-progress count, Procedure stack, findings, eliminated hypotheses, descendants, or contract revision.

For an incomplete effect:

- run the recorded reconciliation and partial-effect checks before choosing any action;
- replay only when verified idempotency, live measurement, and safe replay preconditions all hold;
- compensate or roll back a reversible partial effect before continuation;
- require prior approval and a unique `action_id` if irreversible;
- return `blocked` or `needs_parent` if occurrence or partial completion cannot be determined;
- never repeat an ambiguous external effect merely because output is missing.

### 25.4 Executor replacement and writer conflict

Node identity outlives its executor. If a child agent disappears, the parent keeps the same Child Node, measures its history and artifacts, records executor takeover, and lets another child agent or the parent continue it. Creating an equivalent node to discard failure history is illegal.

V1's supported execution model is serialized ownership coordinated by the current parent or orchestrating agent. It does not guarantee prevention of arbitrary concurrent filesystem writers. When a writer conflict is detected, both footprints are measured, a writer-conflict decision and its evidence are appended after serialization is restored, and acceptance and integration fail closed until Recovery or Integration resolves the state. Multi-process prevention and atomic locking remain deferred.

Procedure push and pop operations, Subgoal changes, failing-gate changes, and executor takeover are reconstructed from ordered `state_delta` records before mutable projections are trusted. An interrupted Procedure stack resumes at its top frame. A node interrupted inside `debug` must satisfy that frame's exit condition and return to its recorded Build Subgoal; a new session does not flatten the stack.

### 25.5 Review and parent recovery

Review binds to node ID, contract revision, subject digest or Git identity, acceptance set, and evidence set. A material subject change preserves the old verdict but invalidates it for the new subject; only the changed surface and affected regressions need re-review.

On parent resume, inspect active descendants, submitted but unadjudicated Return Packets, accepted but unintegrated candidates, and the current parent baseline. A parent advance makes the candidate stale until renewed combination verification; it does not falsify the child's historical completion.

## 26. Human intervention

Goal Pursuit continues autonomously inside delegated authority. A material decision pauses the current node for structured adjudication, but a request first travels to the nearest authority able to decide; reaching a parent is not automatically a human interruption.

| Decision class | Default deciding authority | Escalate further when |
|---|---|---|
| Routine in-contract plan, Subgoal, Procedure, verification, or reversible effect already authorized | Current node owner | Evidence shows the action is outside the contract or risk ceiling |
| Objective, deliverable, acceptance, or exclusion ambiguity that can change the result | Direct parent owner | The ambiguity exists in the parent's own contract or root charter |
| Child activation, bounded contract amendment, Return adjudication, or internal integration inside the parent's own contract | Direct parent owner | The decision would expand the parent's authority or alter its purpose |
| Scope, authority, resource, permission, risk, or external-effect expansion beyond the direct parent's contract | Next ancestor that owns the requested authority | No ancestor below the root owns it |
| Project-level purpose, architecture ownership, maintenance lifecycle, or resource-direction change | Project Node owner | The root charter reserves it for the user or it changes the root charter |
| Reversible external effect not already delegated | Authority that owns the affected system and rollback risk | The effect is production-facing, crosses a reserved boundary, or lacks reliable rollback |
| Destructive, irreversible, security-sensitive, legal, credential-release, or production mutation | Human or explicitly named external human authority | Never self-approved by an agent |
| Material Owner/Reviewer disagreement | Authority that owns the disputed acceptance or risk | Human when it concerns the root, security, legal, irreversible, or production risk |
| Three no-progress Attempts or evidence invalidating a child design | Direct parent owner | The parent goal or root design is implicated |
| Unavailable external data, tool, credential, or prerequisite | Authority or provider that controls it | Return `blocked` when no authorized actor can supply it |
| Root result entering a real mainline, production system, or external irreversible action | Human | Always |
| User-requested stop or checkpoint | User | Always |

Do not pause for:

- internal planning or Subgoal reordering;
- in-contract Subgoal creation, replacement, or supersession;
- bounded Procedure switches;
- tests, experiments, deterministic verification, and self-review;
- status, evidence, and ledger updates;
- child creation inside delegated authority;
- internal child adjudication and integration inside delegated scope;
- ordinary failures followed by a causally different, evidence-producing Attempt.

The authority route is:

```text
child executor → direct parent → project-node owner → human
```

## 27. Minimal interface

The logical interface is intentionally small:

```text
init-project
enter-node
pursue-node
resume-node
spawn-child
record-decision
record-attempt
submit-return
adjudicate-return
validate-node
validate-tree
```

The six Procedures are hidden behind `pursue-node`; they are not six unrelated public commands. V1 implements the interface as skill-guided file operations using templates and read-only checks. A later CLI may automate it without changing the file contracts.

## 28. V1 global skill layout

Planned installation:

```text
~/.codex/skills/recursive-project-tree/
├── SKILL.md
├── references/
│   ├── domain-model.md
│   ├── file-contracts.md
│   ├── lifecycle.md
│   ├── operations.md
│   ├── goal-pursuit.md
│   ├── executor-model.md
│   ├── recovery.md
│   ├── validation.md
│   └── kernel-lineage.md
├── references/procedures/
│   ├── build.md
│   ├── debug.md
│   ├── review.md
│   ├── research.md
│   ├── design.md
│   └── integration.md
└── templates/
    ├── project-node/
    │   └── ...
    └── work-node/
        └── ...
```

The skill and all installed templates are written in English. Conversation with the user may be Chinese.

Before mutating a tree, the skill completes the canonical Section 20.1 Entry Manifest and evaluates the same Enter gates. It does not maintain a second pre-mutation checklist.

It must not require repeated permission for ordinary in-contract file updates. Material contract, authority, return, and integration decisions remain explicit gates.

The skill does not require subagents or an external model. It uses the current agent by default, may bind a child agent to a Child Node when the runtime supports it, and invokes an independent Reviewer only when the contract or risk policy requires one. It records the actual independence level truthfully.

## 29. V1 scope and deferred work

### V1

- Global skill instructions.
- Full and light node templates.
- English file contracts and record examples.
- Guided root initialization and recoverable two-phase child spawn.
- Goal Pursuit orientation, Subgoal planning, and Procedure-stack guidance.
- Six standard Procedure references behind one execution interface.
- Hybrid executor selection with truthful independence labeling.
- Checkpoint, interruption reconciliation, and Resume Procedure guidance.
- Guided ordered decision, approval, Attempt, state-delta, immutable Return, and adjudication updates.
- Serialized single-writer coordination; detected unsynchronized conflicts block acceptance but arbitrary concurrent writers are not prevented.
- Read-only validation that labels mechanical results separately from adjudicative judgments.
- No external dependencies.

### Deferred until real adoption

- Standalone CLI.
- JSON Schema package.
- Automatic ULID/digest generation helper.
- Hash-chained ledgers and signed checkpoints.
- Multi-process locking.
- Generated Markdown projections.
- Automatic branch/worktree cleanup.
- Central portfolio registry.
- Database or daemon.

Two real project adopters and a stable file contract are required before extracting a standalone package or service.

## 30. Test and acceptance scenarios

Section 31 is the binding acceptance contract. The implementation plan must verify these mandatory fixtures and record the cited criterion IDs; the fixtures do not define separate semantics.

1. A root Project Node initializes and a normal Stage completes, submits an immutable packet, is verified by its parent, and returns. [V1-AC-01, V1-AC-03, V1-AC-05]
2. Spawn stops after `spawn_intent` or directory creation; Resume completes or abandons the same child ID without duplication. [V1-AC-02, V1-AC-11]
3. Three repeated no-progress Attempts for one progress scope force redesign. [V1-AC-04]
4. Relevant evidence advances a failing gate, while Procedure switching or irrelevant hypothesis elimination does not reset its counter. [V1-AC-04]
5. A bounded revision produces a new immutable Return Packet; an authority-expanding request travels upward rather than changing the plan silently. [V1-AC-05, V1-AC-17]
6. A node tries to return with an active descendant or transfer it upward; validation rejects the return. [V1-AC-05, V1-AC-12]
7. A candidate passes locally but fails against the latest parent branch. [V1-AC-06]
8. Git contains an unbound branch. [V1-AC-07]
9. A node references a deleted worktree. [V1-AC-07]
10. JSONL contains malformed data, duplicate IDs, or missing/non-monotonic `node_sequence`. [V1-AC-03, V1-AC-07]
11. A terminal node is reopened without approval. [V1-AC-07, V1-AC-17]
12. A Work Node returns `successor_required` and a Project Node succeeds it without losing lineage. [V1-AC-02, V1-AC-05]
13. A decision is contradicted by its later outcome without rewriting history. [V1-AC-03]
14. A valid amendment clarifies execution; revision gaps, forks, digest disagreement, and cumulative purpose drift are rejected. [V1-AC-18]
15. An executor stops after `act` but before `observe`. [V1-AC-16]
16. A replacement executor reconciles none, partial, complete, and ambiguous effects before deciding replay or compensation. [V1-AC-11, V1-AC-16]
17. Agent, model, Procedure, Subgoal wrapper, or node replacement does not reset a progress-scope counter. [V1-AC-04, V1-AC-11]
18. Debug completes and pops its frame, interruption occurs before projection refresh, and Resume reconstructs the Build return target from ordered records. [V1-AC-11, V1-AC-13]
19. A child agent disappears and an authorized replacement takes over the same Child Node without losing history. [V1-AC-11, V1-AC-15]
20. An unsynchronized writer conflict is detected; acceptance and integration remain blocked until recovery, without claiming V1 prevented the race. [V1-AC-07, V1-AC-19]
21. A self-labelled idempotent effect lacks a valid reconciliation check, or an external effect is ambiguous; replay is rejected. [V1-AC-16]
22. An independent review subject changes after its verdict. [V1-AC-14, V1-AC-15]
23. Required independent review is unavailable and the node cannot claim local satisfaction. [V1-AC-14, V1-AC-15]
24. A child completes, the parent ref advances, and the candidate becomes stale pending renewed combination verification. [V1-AC-06, V1-AC-16]
25. Research returns `insufficient_evidence` without fabricating certainty. [V1-AC-14]
26. Build is prevented from starting before required Design approval. [V1-AC-14, V1-AC-17]
27. A parent verifies an internal child's evidence without human interruption; an existing but non-proving evidence reference is rejected. [V1-AC-05, V1-AC-09]
28. Root or real-mainline integration triggers human confirmation. [V1-AC-17]
29. A Procedure switch without `return_to` or an ordered stack event is rejected as drift. [V1-AC-13]
30. A replacement node cannot be used to evade the three-attempt redesign rule. [V1-AC-04, V1-AC-11]

`V1-AC-08` and `V1-AC-10` are verified by installation, dependency, and removal checks rather than responsibility-tree fixtures.

## 31. Acceptance criteria for V1

V1 is acceptable when:

1. **V1-AC-01:** A user can initialize a Project Node from the global skill.
2. **V1-AC-02:** Project and Work children are created through recoverable intent/activation with complete parent context and no duplicate or orphan activation.
3. **V1-AC-03:** Ordered append-only records preserve decisions, Attempt phases, state deltas, and later outcomes without ambiguous history.
4. **V1-AC-04:** The third no-progress Attempt for one progress scope produces a redesign Return Packet, prevents a fourth, and cannot be reset by repackaging the same work.
5. **V1-AC-05:** A parent verifies every accepted criterion, adjudicates an immutable Return Packet without editing child history, and follows the normative lifecycle transition.
6. **V1-AC-06:** A Git-bound local candidate, current-parent combination verification, and actual integration remain distinct.
7. **V1-AC-07:** Read-only validation identifies structural, revision, ledger, lifecycle, descendant, writer-conflict, Return, and Git drift failures and labels mechanical versus adjudicative results truthfully.
8. **V1-AC-08:** No database, background service, project-specific runtime, or automatic multi-process lock is required.
9. **V1-AC-09:** Routine in-scope work continues without repeated approval prompts, while the authority matrix routes material decisions.
10. **V1-AC-10:** The system can be removed without modifying referenced source repositories.
11. **V1-AC-11:** A fresh executor reconstructs contracts, progress scope, Subgoals, Procedure stack, attempts, findings, descendants, and live state without relying on chat history.
12. **V1-AC-12:** A Subgoal remains internal unless isolation criteria require a Child Node, and active descendants are never re-parented to bypass return closure.
13. **V1-AC-13:** Procedure switches preserve contract and progress scope, declare `return_to`, and append recoverable push/pop events.
14. **V1-AC-14:** Build, Debug, Review, Research, Design, and Integration produce required evidence and cannot bypass failed verification.
15. **V1-AC-15:** The system distinguishes self-review, child-agent context isolation, independent Reviewer context, model independence, and human authority without overstating assurance.
16. **V1-AC-16:** Incomplete, partial, unknown, and ambiguous effects use recorded reconciliation checks and fail closed rather than silently replay.
17. **V1-AC-17:** Routine execution remains autonomous, while the authority matrix routes material ambiguity, expansion, risk, disagreement, redesign, and final integration to the nearest authorized parent or human.
18. **V1-AC-18:** Contract revision 1 and approved amendments form one contiguous, digest-bound, cumulatively reviewed effective contract.
19. **V1-AC-19:** V1 truthfully guarantees serialized coordinated ownership and blocks acceptance after detected writer conflict without claiming to prevent arbitrary concurrent writers.
