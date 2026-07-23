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
├── children/
└── RETURN.md
```

Every listed file and directory exists from node creation. An empty ledger is an empty file, not a missing file. `evidence/` and `children/` may be empty. A root Project Node marks `RETURN.md` as `not_applicable`; every non-root node maintains a return packet.

Project Nodes must maintain `ROADMAP.md`, `CONTEXT.md`, and `ARCHITECTURE.md`. Work Nodes inherit the relevant frozen context through `CONTRACT.md` and do not create parallel top-level governance documents.

Contract amendments are added as `AMENDMENT-0001.md`, `AMENDMENT-0002.md`, and so on. They do not silently overwrite the original contract.

## 8. File responsibilities

| File | Responsibility | Mutability |
|---|---|---|
| `NODE.md` | Stable identity, node type, work kind, parent, creation rationale, and navigation | Identity fields immutable; path references may be repaired |
| `CONTRACT.md` | Frozen parent-injected objective, acceptance, scope, exclusions, authority, resources, and workspace binding | Frozen after activation; changed only through approved amendments |
| `PLAN.md` | Current Goal Pursuit orientation, Subgoals, dependencies, Procedure stack, verification, review, and return target | Adaptive; may change inside the contract but never amend it |
| `STATUS.md` | Current execution, parent-verdict, integration, blocking, and next-action projection | Mutable and required to remain current |
| `ROADMAP.md` | Project-stage structure and priority | Project Nodes only |
| `CONTEXT.md` | Stable domain terminology and relationships | Project Nodes only; no plans or implementation details |
| `ARCHITECTURE.md` | Modules, interfaces, seams, dependencies, and invariants | Project Nodes only |
| `decisions.jsonl` | Decisions, rationale, alternatives, evidence, confidence, and later outcome links | Append-only |
| `approvals.jsonl` | Subject-bound creation, amendment, authority, return, and integration decisions | Append-only |
| `attempts.jsonl` | Plan, act, observe, reflect, and decide events | Append-only |
| `evidence/` | Test reports, review findings, manifests, diff summaries, and other verification artifacts | Additive; replacement requires explicit supersession |
| `children/` | Direct children only | Managed through `spawn-child` semantics |
| `RETURN.md` | Child disposition, acceptance results, evidence, unresolved risks, descendants, Git state, and requested parent action | Submitted by child; adjudicated by parent; not silently rewritten by parent |

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

## 10. Lifecycle model

Do not compress completion into one status. `STATUS.md` maintains three axes.

### 10.1 Execution status

```text
proposed → approved → active → blocked → ready_to_return → closed
                              ↘ redesign_required
                              ↘ aborted
```

`blocked` may return to `active` only when the named external condition changes. `redesign_required` and `aborted` are terminal for the current node execution contract.

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
contract_revision: 1
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
current_failing_gate: integration-test
active_children:
  - 01M...
last_decision_id: dec_01N...
last_event_at: 2026-07-22T12:00:00+08:00
last_checkpoint_at: 2026-07-22T12:00:00+08:00
next_action: Test adapter serialization independently
```

The prose body explains the current blocker, evidence, and next action. It does not reproduce historical ledger entries. Update it after contract approval, every completed attempt, child creation or return, blocker changes, Return Packet submission, parent adjudication, measured Git changes, integration, and before ending a work session.

`STATUS.md` is a projection, not a historical authority. If it conflicts with append-only ledgers or live Git, record the discrepancy and repair the projection; do not rewrite the evidence to match the status summary.

## 11. Parent-child protocol

### 11.0 Root initialization

The root Project Node receives a user-approved charter rather than a parent contract. Its `parent_id` is `null`; the user or explicitly named external authority approves revision 1. The charter still freezes objective, acceptance, scope, exclusions, authority, resources, and optional workspace binding. The root may not silently expand these fields merely because it has no parent; material changes require a new user approval and amendment.

### 11.1 Spawn

The direct parent:

1. creates the complete child directory;
2. writes the Child Contract;
3. records a `spawn_child` decision;
4. records contract approval;
5. changes the child from `proposed` to `approved`;
6. allows execution to begin as `active`.

The Child Contract injects:

- parent node and contract revision;
- creation reason and question to answer;
- frozen context summary;
- relevant source paths, digests, and decision IDs;
- objective and acceptance criteria;
- permitted scope and explicit exclusions;
- authority and resource ceiling;
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

### 13.1 Decision record

```json
{
  "record_type": "decision",
  "decision_id": "dec_01K...",
  "node_id": "01K...",
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
  "record_type": "decision_outcome",
  "decision_id": "dec_01K...",
  "observed_outcome": "Caller A passed; caller B still failed",
  "assessment": "mixed",
  "evidence_refs": ["evidence/test-report-03.md"],
  "created_at": "..."
}
```

### 13.2 Approval record

```json
{
  "record_type": "approval",
  "approval_id": "apr_01K...",
  "node_id": "01K...",
  "subject": {
    "kind": "contract",
    "id": "01K...",
    "revision": 1,
    "digest": "sha256:..."
  },
  "decision": "approved",
  "conditions": [],
  "reason": "Scope and acceptance remain within the parent contract",
  "authority": { "kind": "parent_node", "id": "01J..." },
  "evidence_refs": [],
  "created_at": "..."
}
```

Structured approval is required for child creation, contract amendment, authority/scope/resource expansion, descendant transfer, return adjudication, Git integration authorization, terminal-node reopening, and parent-goal changes. Routine in-contract implementation and verification decisions do not require approval.

### 13.3 Attempt events

Every attempt uses one `attempt_id` and appends five ordered phase records:

```text
plan → act → observe → reflect → decide
```

`act` is an intent checkpoint written before execution. It records an `action_id`, intended action, expected effect, permitted footprint, idempotency, rollback, and external-side-effect classification. If execution stops before `observe`, the next executor reconciles the live state before deciding whether the action is safe to resume or repeat.

From cycle 2 onward, `plan` must include `responds_to_attempt_id` and `change_from_previous`. `observe` records commands, exit status, failing gate, evidence, and comparison with the previous attempt. An unrun check is unverified, never passing.

`decide` is one of:

```text
continue | revise_subgoal | replan_node | switch_procedure |
spawn_child | request_amendment | ready_to_return | blocked |
redesign_required | abort
```

## 14. No-progress and redesign rule

An attempt is `advanced` only if it moves the failing gate, eliminates a plausible cause, obtains new verifiable evidence, narrows the validation space, satisfies an acceptance criterion, or demonstrates that the contract/design is invalid.

Code volume, model replacement, agent replacement, wording changes, identical command reruns, and materially equivalent fixes are not progress by themselves.

Each `decide` event records:

```json
{
  "progress_assessment": "advanced",
  "no_progress_reasons": [],
  "consecutive_no_progress": 0
}
```

When `consecutive_no_progress` reaches 3:

1. execution becomes `redesign_required`;
2. the node writes a Return Packet;
3. no fourth `plan` event is legal;
4. the direct parent may create a new design/debug/integration child, modify its own design, terminate the route, or create a new sibling attempt;
5. the failed node and eliminated hypotheses remain preserved and referenced.

## 15. Return Packet and parent adjudication

`RETURN.md` answers:

1. Which parent contract was accepted?
2. Is the disposition `completed`, `blocked`, `redesign_required`, or `aborted`?
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
accept | request_revision | redesign | terminate | integrate
```

Before `ready_to_return`, every direct child must be terminal, have its own Return Packet, or be explicitly transferred through parent approval. Hidden follow-up work is invalid.

The child submits. The direct parent adjudicates. The parent may append approval and status records but may not silently rewrite the child's historical account.

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

### 18.1 Structure

- Required files and directories exist.
- JSONL lines parse.
- Node IDs are unique.
- Parent IDs match the physical direct parent.
- Node type matches its template.
- `PLAN.md` has a goal, primary Procedure, review policy, and return target.

### 18.2 Contract

- Contract revisions have parent approval.
- Child scope, authority, and resources do not expand silently.
- Acceptance is non-empty.
- Workspace baseline is exact when Git-bound.
- Amendments do not disguise a new project purpose.

### 18.3 Lifecycle

- State transitions are legal.
- Proposed nodes cannot execute.
- Ready-to-return nodes cannot append acts.
- Redesign-required nodes cannot begin a fourth cycle.
- Terminal nodes cannot reopen without approval.
- Parent verdicts have approval evidence.
- An active Procedure Frame has `invoked_by`, `return_to`, and an exit condition.
- An accepted Subgoal has evidence and accepted dependencies.
- A delegated Subgoal binds to a disclosed direct child.
- The recorded active writer is unique or the node fails closed.

### 18.4 Ledger

- Attempt phases are ordered.
- `act` intent precedes the effect it describes.
- An Attempt with `act` but no `observe` is classified as incomplete and reconciled before replay.
- Later attempts respond to prior feedback.
- Record IDs and references resolve.
- Corrections append rather than rewrite history.
- `STATUS.md` agrees with the latest ledger state.
- Evidence references exist.
- Executor takeover preserves Attempt numbers, findings, hypotheses, and no-progress count.

### 18.5 Return

- Every acceptance criterion has a verdict.
- Passing verdicts cite evidence.
- Direct descendants are disposed.
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
- `PLAN.md` changes stay inside the approved contract.
- Procedure selection satisfies its entry conditions.
- Procedure switches preserve scope and have a return target.
- Required closing verification passed; skipped or warning-only gates are not accepted.
- Review findings bind to a frozen subject and every material finding is adjudicated.
- Claimed independence matches the actual executor context and model.

### 18.8 Recovery

- Resume reconstructs authority, history, live state, descendants, and projections.
- An incomplete or ambiguous effect is measured before replay.
- Irreversible effects have prior approval and a unique action ID.
- Procedure-stack, Subgoal, and Return Packet continuity survive session replacement.
- Parent advancement invalidates stale combination verification without rewriting child history.

## 19. Failure handling

The system fails closed for parent acceptance and Git integration when:

- JSONL is malformed;
- contract or parent approval is missing;
- parent identity is inconsistent;
- evidence is missing;
- acceptance criteria lack verdicts;
- an active descendant is undisclosed;
- work continues after the no-progress cap;
- a replacement executor resets attempt or no-progress history;
- a Procedure switch lacks a return target;
- required independent review is mislabeled or unavailable;
- required verification failed, was skipped, or is only a warning;
- an incomplete or ambiguous effect is replayed without reconciliation;
- multiple active writers are unresolved;
- recorded and measured Git states disagree;
- contract-external files changed;
- the parent advanced without renewed combination verification.

Malformed history is corrected by appending a correction or supersession record. Records are not deleted merely to make validation pass.

## 20. Goal Pursuit controller

Goal Pursuit is the single logical execution interface:

```text
pursue(node_contract, procedure, context)
  → accepted
  → needs_parent
  → redesign_required
  → aborted
```

`accepted` means the controller found every local acceptance criterion satisfied. A non-root child still moves only to `ready_to_return`; it does not set its own parent verdict.

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
  acceptance:
    - Interface test passes
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

An executor may switch Procedure without approval only when the same objective, deliverable, acceptance, authority, write scope, side effects, and risk ceiling remain intact. The switch is recorded as a decision. A separate child is required when the work gains independent responsibility, context, permissions, failure budget, review, duration, parallelism, or acceptance.

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

No progress means no hypothesis was eliminated, no new verifiable evidence appeared, no key uncertainty narrowed, or the same causal strategy was repeated with superficial changes. Agent, model, tool, wording, or node-name changes do not reset the counter. After two no-progress attempts, an independent diagnosis should be sought before a third attempt when available. The third consecutive no-progress Attempt forces `redesign_required`.

Small debugging stays on the current Procedure stack. Create a Debug child only for isolated context, authority, long-running investigation, parallel experiments, independent acceptance, or a root cause outside the node's responsibility.

### 23.3 Review

Purpose: independently judge whether a frozen subject satisfies its contract and produce findings that can be adjudicated.

Self-review is mandatory inside every Procedure. The Review Procedure is separate and uses an independent execution context when the risk policy requires it.

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

A direct parent agent may accept and integrate an internal child inside delegated scope. Human confirmation is required before root-project or real-mainline integration, production or irreversible effects, project-level contract or architecture change, unresolved material review disagreement, or a value judgment about whether a completed result should be absorbed.

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
| High-risk or disputed judgment | Different model when available, then human authority if unresolved |
| Contract, permission, irreversible-effect, or project-value change | Authorized parent or human |

A child agent provides responsibility and context isolation but may use the same model, so it does not automatically provide epistemic diversity. A different model can reduce shared bias but does not create governance authority. Human authority carries the decisions explicitly reserved for people.

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

Resume never resets Attempt numbers, no-progress count, Procedure stack, findings, eliminated hypotheses, descendants, or contract revision.

For an incomplete effect:

- measure and safely replay only if it is idempotent;
- measure before rollback or continuation if reversible;
- require prior approval and a unique `action_id` if irreversible;
- return `blocked` or `needs_parent` if occurrence cannot be determined;
- never repeat an ambiguous external effect merely because output is missing.

### 25.4 Executor replacement and writer conflict

Node identity outlives its executor. If a child agent disappears, the parent keeps the same Child Node, measures its history and artifacts, records executor takeover, and lets another child agent or the parent continue it. Creating an equivalent node to discard failure history is illegal.

If two executors claim one node, new writes stop, both footprints are measured, a writer-conflict decision and its evidence are appended, and a Recovery or Integration path resolves the state before return. V1 detects and fails closed; multi-process locking remains deferred.

An interrupted Procedure stack resumes at its top frame. A node interrupted inside `debug` must satisfy that frame's exit condition and return to its recorded Build Subgoal; a new session does not flatten the stack.

### 25.5 Review and parent recovery

Review binds to node ID, contract revision, subject digest or Git identity, acceptance set, and evidence set. A material subject change preserves the old verdict but invalidates it for the new subject; only the changed surface and affected regressions need re-review.

On parent resume, inspect active descendants, submitted but unadjudicated Return Packets, accepted but unintegrated candidates, and the current parent baseline. A parent advance makes the candidate stale until renewed combination verification; it does not falsify the child's historical completion.

## 26. Human intervention

Goal Pursuit continues autonomously inside delegated authority. A request first travels to the nearest parent able to decide; reaching a parent is not automatically a human interruption.

Pause and escalate when:

- objective, deliverable, or acceptance ambiguity changes the likely result;
- scope, authority, resource category, permission, or external effect must expand;
- an action is destructive, irreversible, security-sensitive, legal, or production-facing;
- a material value trade-off has no answer in the contract;
- owner and independent Reviewer have an unresolved material disagreement;
- three consecutive no-progress Attempts force redesign;
- evidence invalidates the parent goal or design;
- an unavailable external prerequisite, credential, or authority is necessary;
- a root result is ready for real mainline or production integration;
- the user explicitly requests a stop or checkpoint.

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

The skill must declare before mutating a tree:

- operation;
- responsibility-tree root;
- target or parent node;
- node type and work kind when spawning;
- purpose and acceptance;
- authorized write scope;
- optional workspace binding;
- whether parent approval already exists or must be recorded.

It must not require repeated permission for ordinary in-contract file updates. Material contract, authority, return, and integration decisions remain explicit gates.

The skill does not require subagents or an external model. It uses the current agent by default, may bind a child agent to a Child Node when the runtime supports it, and invokes an independent Reviewer only when the contract or risk policy requires one. It records the actual independence level truthfully.

## 29. V1 scope and deferred work

### V1

- Global skill instructions.
- Full and light node templates.
- English file contracts and record examples.
- Guided root initialization and child spawn.
- Goal Pursuit orientation, Subgoal planning, and Procedure-stack guidance.
- Six standard Procedure references behind one execution interface.
- Hybrid executor selection with truthful independence labeling.
- Checkpoint, interruption reconciliation, and Resume Procedure guidance.
- Guided decision, attempt, return, and adjudication updates.
- Read-only manual validation using filesystem and live Git evidence.
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

The implementation plan must verify at least these fixture scenarios:

1. A normal Stage completes and returns.
2. A Stage creates a Debug child and aggregates its accepted result.
3. Three repeated no-progress attempts force redesign.
4. Repeated failures with advancing gates do not falsely trigger redesign.
5. A child attempts to expand parent scope.
6. A node returns with an active descendant.
7. A candidate passes locally but fails against the latest parent branch.
8. Git contains an unbound branch.
9. A node references a deleted worktree.
10. JSONL contains malformed data or duplicate IDs.
11. A terminal node is reopened without approval.
12. A Work Node is replaced by a Project Node without losing lineage.
13. A decision is contradicted by its later outcome without rewriting history.
14. A contract amendment clarifies execution without changing project purpose.
15. An executor stops after `act` but before `observe`.
16. A replacement executor resumes the same incomplete Attempt from files and live measurement.
17. Agent or model replacement does not reset the no-progress counter.
18. Build invokes Debug, interruption occurs, and Resume returns to the original Build Subgoal.
19. A child agent disappears and a replacement takes over the same Child Node.
20. Two executors claim the same node and validation fails closed on writer conflict.
21. An ambiguous external side effect is not replayed.
22. An independent review subject changes after its verdict.
23. Required independent review is unavailable and the node cannot claim acceptance.
24. A child completes, the parent ref advances, and the candidate becomes stale pending renewed combination verification.
25. Research returns `insufficient_evidence` without fabricating certainty.
26. Build is prevented from starting before required Design approval.
27. An internal child return is adjudicated by its parent agent without human interruption.
28. Root or real-mainline integration triggers human confirmation.
29. A Procedure switch without `return_to` is rejected as drift.
30. A replacement node cannot be used to evade the three-attempt redesign rule.

## 31. Acceptance criteria for V1

V1 is acceptable when:

1. A user can initialize a Project Node from the global skill.
2. The user can spawn both Project and Work children with complete parent context.
3. A Work Node can record decisions and a multi-round failure loop without ambiguous history.
4. The third no-progress attempt produces a redesign Return Packet and prevents continued execution.
5. A parent can adjudicate a return without editing child history.
6. A Git-bound candidate remains distinct from an integrated result.
7. A read-only validation pass can identify missing files, illegal lifecycle state, active descendants, and Git drift.
8. No database, background service, or project-specific runtime is required.
9. The skill does not create frequent approval prompts for routine in-scope work.
10. The system can be removed without modifying the referenced source repositories.
11. A fresh agent can orient and continue a node from `CONTRACT.md`, `PLAN.md`, `STATUS.md`, ledgers, evidence, descendants, and live workspace state without relying on chat history.
12. A Subgoal remains an internal plan item unless isolation criteria require a Child Node.
13. Procedure switches preserve contract scope and declare their return target.
14. Build, Debug, Review, Research, Design, and Integration each produce their required evidence and cannot bypass failed verification.
15. The system distinguishes current-agent execution, child-agent context isolation, model independence, and human authority.
16. Interrupted or ambiguous effects fail closed and do not silently replay.
17. Routine execution continues autonomously, while material authority, risk, disagreement, redesign, and final-integration gates reach the appropriate parent or human.
