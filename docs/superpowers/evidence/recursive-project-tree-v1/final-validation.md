# Recursive Project Tree V1 — Final Validation

**Spec:** `14b9adb3`  
**Skill subject:** `/Users/evan/.codex/skills/recursive-project-tree`; 39-file
sorted SHA-256 manifest digest
`2e1cb379f54b63359f83895e6520e7414bc33e91746ae28c41e9956f1cb79495`  
**Validation date:** `2026-07-23` (Asia/Shanghai)  
**Evidence revision:** `76716469`

## Packaging

- Official quick validation: `Skill is valid!`
- Skill file manifest: 39 files; per-file digests are retained at
  `/private/tmp/rpt-final-manifest.sha256`.
- Runtime dependencies: Python standard library and POSIX shell only. No
  database, daemon, service, or third-party runtime package.
- Deterministic final run:
  `/private/tmp/recursive-project-tree-final-20260723d.json`, 36 PASS / 0 FAIL;
  fixture root `/private/tmp/recursive-project-tree-fixtures-final-20260723d`.
- Fresh-context behavior: [forward-tests.md](forward-tests.md), 9 PASS / 0 FAIL.

## Acceptance summary

Mechanical Guard tests and advisory/adjudicative protocol conformance scenarios
are distinguished in [coverage-matrix.md](coverage-matrix.md).

| Criterion | Evidence | Result |
|---|---|---|
| V1-AC-01 | Fixtures 1, 7; bootstrap and Guard initialization | PASS |
| V1-AC-02 | Fixtures 2, 10; TRANSFER-01 | PASS |
| V1-AC-03 | Fixtures 3, 31; GUARD-03/04 | PASS |
| V1-AC-04 | Fixtures 4, 30; GREEN-BASE-02 | PASS |
| V1-AC-05 | Fixtures 5, 27; GREEN-BASE-03; adjudication is explicitly parent-declared | PASS |
| V1-AC-06 | Fixtures 7–11, 24; TRANSFER-03 | PASS |
| V1-AC-07 | Fixtures 12–19, 31–32; Guard read-only drift checks | PASS |
| V1-AC-08 | 39-file package; standard-library imports; official quick validation | PASS |
| V1-AC-09 | Fixtures 26–28; Goal Pursuit and nearest-authority routing | PASS |
| V1-AC-10 | Independent temporary removal check below | PASS |
| V1-AC-11 | Fixtures 17–21, 24, 30; TRANSFER-02 | PASS |
| V1-AC-12 | Fixtures 2, 12–14; child/Subgoal boundary contract | PASS |
| V1-AC-13 | Fixtures 18–19, 29; Procedure stack conformance | PASS |
| V1-AC-14 | Fixtures 22–26; six Procedure contracts; forward tests | PASS |
| V1-AC-15 | Fixtures 22–23; GREEN-BASE-06 | PASS |
| V1-AC-16 | Fixtures 17–21, 24; GREEN-BASE-04; TRANSFER-02 | PASS |
| V1-AC-17 | Fixtures 26–28; authority matrix and human-boundary tests | PASS |
| V1-AC-18 | Fixtures 12–16; contiguous amendment validation | PASS |
| V1-AC-19 | Fixtures 17, 31–32; GUARD-08/09; stated same-authority limit | PASS |
| V1-AC-20 | Fixtures 1–21, 31–32; Guard mutation/refusal evidence | PASS |
| V1-AC-21 | Fixtures 31–34; local JSON remains detective; GUARD-12 superseded | PASS |

## Independent review

- Reviewer identity and independence: `/root/final_review`, fresh
  `fork_turns="none"`, read-only, given the frozen subject and spec but not
  owner reasoning or the implementation plan.
- Initial verdict: `BLOCKED`.
- Final changed-surface verdict: `ACCEPTABLE_WITH_FIXES`; the requested evidence
  fixes were then applied and re-run.
- Accepted finding: executor-writable JSON cannot authenticate external CI.
  Guard now reports it as detective with
  `external_evidence_authenticated:false`.
- Accepted finding: parent acceptance is an adjudicative declaration. Guard
  proves identity, packet digest, authority, and criterion-set mechanics, but
  does not claim semantic proof.
- Accepted finding: deterministic scenario rows must be named protocol
  conformance evidence rather than mechanical enforcement.
- Accepted finding: old GUARD-12 evidence was misleading; it is explicitly
  superseded.
- Rejected as release blocker: multi-file operations are not transactional.
  This is a documented recovery boundary: post-write failure returns
  `incomplete_operation`, preserves partial canonical state, and emits recovery
  evidence; V1 does not promise rollback.
- Rejected as release blocker: the six-command Guard does not mechanically
  implement semantic amendment, replay, research, or review judgment. These are
  intentionally advisory/adjudicative file-protocol procedures.

## Removal check

- Temporary install: `/private/tmp/rpt-removal-hQBUZZ/recursive-project-tree`,
  removed successfully.
- Separate target repository tree before:
  `0e2cbb61fa766144bf931b2839d8dcbc8760a991`.
- Target repository tree after: identical.
- Target Git status before and after: clean.
- Installed global skill remained present.

## Residual limitations

- No arbitrary same-authority filesystem-writer prevention.
- No automatic semantic proof.
- No operation-wide transactional rollback after a partial multi-file write;
  recovery evidence and fail-closed resumption are used instead.
- No automatic Git integration or cleanup.
- Hooks remain bypassable.
- Local evidence cannot establish preventive CI. CI prevents integration only
  when an actual external authority requires the check and the executor cannot
  bypass or reconfigure it; V1 contains no authenticator for that boundary.
- Several deterministic rows are protocol conformance scenarios, while the
  Guard and fresh-context rows are executable behavior evidence.
- No claim of adoption before two real project users.

## Release verdict

**APPROVED for V1 within its declared boundary:** a removable pure-file
responsibility protocol with advisory semantic procedures and a bounded Local
Guard for named mechanical operations. It is not an unbypassable workflow
engine, semantic verifier, transaction manager, or authenticated CI authority.
