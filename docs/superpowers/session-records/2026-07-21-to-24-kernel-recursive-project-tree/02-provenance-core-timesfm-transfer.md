# 02 — Provenance Core and TimesFM Transfer

## Approved shared seam

The session proposed a thin logical `provenance-core` rather than importing
Kernel's complete Agent runtime. Its five objects were:

```text
RequestEnvelope
ArtifactManifest
RuleReport
DecisionRecord
OutcomeRecord
```

Their responsibility is to state:

1. what exact operation was requested;
2. which input, data, code, model, configuration, and policy identities it used;
3. what artifact was produced and how it is addressed;
4. which complete rule set passed, failed, or remained unknown;
5. who decided what about which exact subject;
6. what later observable outcome should be linked back to the request.

This shared seam records observations and lineage. It does not own the domain's
Bayesian model.

## Three Bayesian domains kept separate

The conversation explicitly separated:

- research-claim belief updates;
- Agent or skill reliability updates;
- financial forecast uncertainty and calibration.

They may consume common provenance objects but must not share one global
posterior. The shared contract says “what was observed”; each domain decides
how that observation changes belief.

## First trial selection

The user approved trying Provenance Core first in the TimesFM volatility work
and chose the name `equity-timesfm` because the implementation should begin
with equities while remaining portable to additional markets.

The approved working discipline was:

- preserve the original provenance objective during review;
- self-review first;
- use `ai-reviewer` and then `spec-reviewer` only at important milestones,
  disagreements, and completion;
- independently evaluate reviewer findings rather than accepting them
  mechanically;
- execute an approved slice without repeated permission prompts;
- write a handoff so the remaining implementation could continue inside the
  target repository.

## Why this trial mattered

TimesFM was a suitable first consumer because model and data identity,
as-of/available-at time, input snapshot, deterministic configuration, output
artifact, gate evidence, approval, and realized forecast outcome are all
material. A provenance seam can add traceability without taking ownership of
forecasting, covariance, or market-specific research logic.

## Boundary of this record

This Kernel repository retains the design rationale and cross-project takeaway.
The target repository owns its live implementation status. No completion claim
about `equity-timesfm` should be inferred from this session record without
checking that repository's current Git and handoff files.
