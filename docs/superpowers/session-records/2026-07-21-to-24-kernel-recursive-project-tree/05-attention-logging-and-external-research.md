# 05 — Attention, Logging, and External Research

## Attention concern

The user challenged whether a long Skill can actually make an Agent read the
required references and follow the designed path. Progressive disclosure
reduces context cost but does not enforce reading. The entrypoint, operation
routing, stable scripts, Guard checks, and templates improve reliability, yet
an Agent with raw access can still skip them.

The user rejected endless local patching and requested stronger evidence from
mature projects before adding more process.

## Current logging diagnosis

Before this change, V1 already preserved:

- ordered decisions and later outcomes;
- subject-bound approvals;
- Attempt phases and actual observations;
- immutable Return Packets;
- recovery artifacts;
- optional Git/workspace evidence.

That was enough to reconstruct canonical protocol state, but not a complete
runtime event history. Confirmed gaps were:

- Guard-generated ledger events defaulted to the Unix epoch when callers did
  not supply `created_at`;
- Guard refusals were returned to stdout but not automatically persisted;
- detective Guard calls were not automatically persisted;
- reference reads, compaction, arbitrary tool calls, and session lifecycle
  were not observable at the pure-file protocol boundary;
- there was no tree-wide Guard invocation history.

## Implemented logging repair

The repair has two layers:

1. Guard now owns real UTC `created_at` for canonical ledger envelopes. A
   caller-supplied time is only a `reported_at` claim.
2. Every supported Guard result after Project-root resolution creates one
   immutable, non-authoritative `rpt-audit-event-v1` file under
   `observability/events/`.

The event records operation identity, request digest, start/end time, duration,
exit code, status, whether canonical protocol changed, full Guard result, and
result digest. This captures success, refusal, and detective validation without
creating a fourth authoritative ledger.

The honest completeness boundary is:

```text
supported Guard results after an initialized Project root can be resolved
```

It does not claim to capture arbitrary shell, model, OS, network, or direct
filesystem events. Failed initialization before a root exists has no in-tree
audit destination. Local writers can also forge or delete audit files, so the
integrity check is detective.

## External projects examined

The later research produced four genuinely different candidate mechanisms,
not generic “write better docs” advice:

### Beads

Dependency-aware work graphs, ready-work discovery, atomic claim, and reusable
formula/molecule execution patterns. Sources:
[repository](https://github.com/gastownhall/beads) and
[Molecules](https://github.com/gastownhall/beads/blob/main/docs/MOLECULES.md).

### Gas Town

Lifecycle injection at SessionStart, PreCompact, UserPromptSubmit,
PreToolUse, and Stop; provider adapter fallbacks; persistent patrol roles;
crash recovery; and a bisecting merge queue. Sources:
[repository](https://github.com/gastownhall/gastown) and
[agent-provider integration](https://github.com/gastownhall/gastown/blob/main/docs/agent-provider-integration.md).

### OpenHands and SWE-agent

OpenHands contributes explicit stuck-pattern detection and triggered repository
skills. SWE-agent contributes a precise query/action/observation trajectory,
replayable configuration, action parsing, blocklists, requery, and timeout.
Sources:
[OpenHands stuck detector](https://docs.openhands.dev/sdk/guides/agent-stuck-detector),
[OpenHands skills](https://github.com/OpenHands/OpenHands/blob/main/skills/README.md),
[SWE-agent trajectories](https://github.com/SWE-agent/SWE-agent/blob/main/docs/usage/trajectories.md), and
[SWE-agent agent reference](https://swe-agent.com/latest/reference/agent/).

### Git Town and Gerrit

Git Town contributes explicit branch hierarchy, stacked synchronization, and
undo. Gerrit contributes a stable Change-Id that survives amend, rebase, and
cherry-pick. Sources:
[Git Town stacked changes](https://www.git-town.com/stacked-changes.html),
[Git Town sync](https://www.git-town.com/commands/sync.html), and
[Gerrit Change-Id](https://gerrit-review.googlesource.com/Documentation/user-changeid.html).

### Harness and skill-loading evidence

OpenAI's Harness Engineering supports a short repository map, repository docs
as system of record, and mechanical documentation maintenance. Anthropic's
Agent Skills documentation supports progressive disclosure as context
optimization, not enforcement. Sources:
[Harness Engineering](https://openai.com/index/harness-engineering/) and
[Agent Skills overview](https://platform.claude.com/docs/de/agents-and-tools/agent-skills/overview).

## Superseded research proposal

**Superseded:** add a “Compiled Task Capsule.”

It overlapped the existing Entry Manifest and `CONTEXT.md`, adding a new name
without a distinct responsibility. It was withdrawn. The remaining candidate
mechanisms have distinct runtime roles and are deferred to a real case.
