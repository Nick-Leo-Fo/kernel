# Recursive Project Tree — Audit Log Validation

**Date:** 2026-07-24 (Asia/Shanghai)

**Updated Skill:** `/Users/evan/.codex/skills/recursive-project-tree`

**39-file sorted manifest digest:** `c521737dd048cdf01b449886f87cd692573c251170c46467c1a7eab4cfa57113`

This is additive evidence for the audit-log change. It does not rewrite the
2026-07-23 certification, whose claims remain bound to its earlier Skill
manifest.

## RED

The first run used the unchanged installed Skill plus new Fixture 35:

- 36 PASS / 1 FAIL;
- both initialization ledger events had
  `created_at: 1970-01-01T00:00:00Z`;
- zero `observability/events/*.json` files existed;
- all pre-existing checks passed.

Evidence result:
`/private/tmp/recursive-project-tree-fixtures-audit-red-bVJ0ds/results.json`.

## GREEN on isolated Skill copy

After the minimal implementation, the isolated Skill copy produced:

- 37 PASS / 0 FAIL;
- real UTC ledger recording times;
- one audit event each for `init-project`, refused `append-record`, and
  successful `validate-node`;
- stable canonical protocol digest across detective validation;
- valid result digests.

Evidence result:
`/private/tmp/rpt-audit-green2-RmoMnt/results.json`.

## Installed-surface verification

Fresh command:

```text
python3 docs/superpowers/evidence/recursive-project-tree-v1/run_fixtures.py \
  --skill-root /Users/evan/.codex/skills/recursive-project-tree \
  --fixture-root /private/tmp/recursive-project-tree-fixtures-O881NT \
  --output /private/tmp/rpt-audit-final-O881NT/results.json
```

Observed:

```json
{"fail_count":0,"pass_count":37}
```

Fixture 35 observed exactly three distinct `rpt-audit-event-v1` files with
operations:

```text
init-project
append-record
validate-node
```

The refused append returned exit code 2 and `status: refused`; validation
returned exit code 0 and `status: pass`; the canonical protocol digest was
unchanged by validation; all stored result digests matched.

Official Skill structure validation:

```text
Skill is valid!
```

Full result:
`/private/tmp/rpt-audit-final-O881NT/results.json`.

## Honest boundary

The new stream is complete only for supported Guard results after an
initialized Project root can be resolved. It is non-authoritative, locally
bypassable, and detective. It does not observe arbitrary model, shell, OS,
network, or direct-filesystem activity.
