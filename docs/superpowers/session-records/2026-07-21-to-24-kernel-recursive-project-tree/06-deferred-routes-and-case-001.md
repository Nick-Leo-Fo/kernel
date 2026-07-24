# 06 — Deferred Routes and Case 001

## Decision

Do not optimize the framework again from hypothetical discomfort. Run one real
project through the current V1, preserve the evidence, then decide which
runtime road is justified.

## Candidate roads

| Candidate | Distinct problem | Evidence needed before adoption |
|---|---|---|
| `PRIME` | Agent enters or resumes without loading the minimum live context | Repeated missing/wrong context despite the entry manifest and explicit reference routing |
| `READY` | Agent cannot identify the next unblocked responsibility | Measured time or errors caused by manual dependency/readiness discovery |
| `CLAIM` | Two executors work the same responsibility or writer ownership races | A real duplicate-work or ownership-conflict incident not adequately handled by current single-writer recovery |
| `PATROL` | Drift or blockage persists because no event-driven supervisor notices it | A live node remains stale, blocked, orphaned, or unreturned despite normal execution and validation |
| Formula → instance | Fixed Procedures are repeatedly re-expanded inconsistently | Two or more real executions needing the same executable Procedure instantiation |
| Git Town-style stack | Nested branches cannot return or synchronize reliably using existing workspace bindings | A real stacked-branch case with measurable manual sync/undo pain |
| Gerrit-style stable review ID | Review identity is lost across rebases or cherry-picks | A real review subject whose lineage cannot be correlated by current packet/candidate digests |
| Rich trajectory log | Debugging requires non-Guard tool/action/observation replay | A real incident where canonical ledgers plus Guard audit cannot explain the failure |

These candidates are not mutually exclusive, but none should be installed
because another mature project uses it.

## Case 001 protocol

Select one real development responsibility with:

- a clear parent objective;
- at least one bounded child or Procedure switch;
- real code/workspace evidence;
- one acceptance and return decision;
- enough duration to include interruption or resumption if it occurs naturally.

During the case:

1. Use current Project/Work Node templates and Local Guard without adding
   lifecycle hooks.
2. Route supported protocol mutations through Guard.
3. Preserve canonical ledgers, Return Packets, recovery artifacts, and
   `observability/events/`.
4. Record direct filesystem or external actions in the normal Attempt
   `observe` payload when they affect acceptance.
5. Do not manufacture failure, concurrency, or branch complexity merely to
   exercise a candidate.

## Post-case questions

### Context and attention

- Did the Agent read the correct references?
- If not, was the cause missing routing, compaction loss, a stale projection,
  or deliberate bypass?
- Would PRIME have prevented the specific failure?

### Planning and readiness

- Was the next ready Subgoal discoverable from current files?
- Did blocked dependencies cause search or duplicated planning?
- Would READY reduce measured work rather than add another status layer?

### Ownership

- Did two writers overlap or did responsibility become ambiguous?
- Did existing writer records and recovery resolve it?
- Would CLAIM add prevention at a boundary that is actually enforceable?

### Drift and supervision

- Did a branch, child, or Return remain stale without detection?
- Which observable event should have triggered intervention?
- Would PATROL act on evidence, or merely poll and duplicate validation?

### Logging

- Can a reviewer reconstruct why each important decision was made?
- Are any acceptance-relevant actions missing from Attempts and Guard audit?
- Is the missing evidence inside the Guard's feasible boundary or does it
  require a lifecycle/provider integration?
- Which fields were never used and can be removed?

### Cost and redundancy

- Which files or steps were repeatedly maintained but never influenced a
  decision, recovery, acceptance, or integration?
- Which candidate removes more work than it introduces?
- Can the problem be solved by strengthening one existing interface rather
  than adding another subsystem?

## Selection rule

Adopt a candidate only when Case 001 supplies:

1. a concrete repeated failure or material cost;
2. a mechanism whose enforcement boundary reaches that failure;
3. a smaller or equal-complexity integration path;
4. a testable success condition;
5. no existing V1 component that already owns the same responsibility.

Otherwise retain the candidate in this file and leave V1 unchanged.
