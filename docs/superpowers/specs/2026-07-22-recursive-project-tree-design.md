# Recursive Project Tree — Design

**Date:** 2026-07-22

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
| `packages/agent-os/src/spawn.ts` and `acap.ts` | Parent identity, purpose, child budget, child limit, downscope helper | Parent/child identity and non-escalation rule | Current spawn path does not fully enforce all capability-subset guarantees; v1 uses explicit file validation |
| Hierarchical planner types | Goal → Phase → Action → ToolCall and revise-action/phase/goal verdict vocabulary | Full versus light node concepts and escalation ladder | Planner is feature-gated Phase-1 scaffolding and is not adopted as a runtime |
| `kbot-finance` governance/provenance | Request identity, subject-bound approval shape, rule reports, audit reference | Bind approval to an exact node, contract revision, candidate, or return packet | No production HMAC approval system is required for local v1 |

The resulting system is a new composition at a filesystem seam. It is not a claim that Kernel already ships this directory system.

## 5. Domain model

### 5.1 Project Node

A long-lived, independently governed project or subproject. It owns a roadmap, domain context, architecture, multiple stages, and its own child tree.

### 5.2 Work Node

A bounded execution node. Its `work_kind` is one of:

```text
stage | task | debug | review | design | experiment | integration
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

## 7. Directory structures

### 7.1 Project Node

```text
<project-node>/
├── NODE.md
├── CONTRACT.md
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
current_attempt: 2
consecutive_no_progress: 1
current_failing_gate: integration-test
active_children:
  - 01M...
last_decision_id: dec_01N...
last_event_at: 2026-07-22T12:00:00+08:00
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

From cycle 2 onward, `plan` must include `responds_to_attempt_id` and `change_from_previous`. `observe` records commands, exit status, failing gate, evidence, and comparison with the previous attempt. An unrun check is unverified, never passing.

`decide` is one of:

```text
continue | spawn_child | ready_to_return | blocked |
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

### 18.4 Ledger

- Attempt phases are ordered.
- Later attempts respond to prior feedback.
- Record IDs and references resolve.
- Corrections append rather than rewrite history.
- `STATUS.md` agrees with the latest ledger state.
- Evidence references exist.

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

## 19. Failure handling

The system fails closed for parent acceptance and Git integration when:

- JSONL is malformed;
- contract or parent approval is missing;
- parent identity is inconsistent;
- evidence is missing;
- acceptance criteria lack verdicts;
- an active descendant is undisclosed;
- work continues after the no-progress cap;
- recorded and measured Git states disagree;
- contract-external files changed;
- the parent advanced without renewed combination verification.

Malformed history is corrected by appending a correction or supersession record. Records are not deleted merely to make validation pass.

## 20. Minimal interface

The logical interface is intentionally small:

```text
init-project
spawn-child
record-decision
record-attempt
submit-return
adjudicate-return
validate-node
validate-tree
```

V1 implements these as skill-guided file operations using templates and read-only checks. A later CLI may automate them without changing the file contracts.

## 21. V1 global skill layout

Planned installation:

```text
~/.codex/skills/recursive-project-tree/
├── SKILL.md
├── references/
│   ├── domain-model.md
│   ├── file-contracts.md
│   ├── lifecycle.md
│   ├── operations.md
│   ├── validation.md
│   └── kernel-lineage.md
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

## 22. V1 scope and deferred work

### V1

- Global skill instructions.
- Full and light node templates.
- English file contracts and record examples.
- Guided root initialization and child spawn.
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

## 23. Test and acceptance scenarios

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

## 24. Acceptance criteria for V1

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
