# kernel Portfolio Evaluation System

**Date:** 2026-07-21

**Status:** Approved design

**Purpose:** Decide whether each independently useful part of the repository is worth continued investment and guide internal iteration priority.

## 1. Decision contract

This evaluation treats the repository as a portfolio rather than a single product. Each independently deliverable unit is evaluated on its own merits, then the active units are aggregated into a portfolio conclusion.

The evaluation answers:

1. Is this unit valuable enough to justify continued investment?
2. Is that judgment supported by evidence or still a hypothesis?
3. Can the unit stand alone, and what verified value does it contribute to the portfolio?
4. What is the highest-information next action?

There is no fixed resource ceiling. A valuable unit may receive resources even when another unit also deserves investment. The framework therefore ranks value and evidence; it does not force a single winner.

## 2. Evaluation units

The initial full evaluation covers the five core units:

- `kbot`
- `kernel.chat`
- `agent-os`
- `kbot-finance`
- `kbot-orchestrator`

All other packages and deliverables receive an independence screen. Any unit that passes the identity and delivery gates enters the same full evaluation. Units that do not pass are classified as incubating, internal-only, historical, or unowned rather than silently omitted.

Each unit is assigned an archetype before scoring:

- product
- content/media
- infrastructure/library
- workflow
- experiment

All archetypes use the same dimensions and weights. The evidence accepted for each dimension is interpreted according to the archetype. A library does not need a user interface, but it does need a stable consumption interface, integration evidence, and a real caller.

## 3. Scoring model

Each unit receives a raw value score from 0 to 100.

| Dimension | Weight | Decision question |
|---|---:|---|
| User and problem value | 25 | Does it solve an important, recurring problem whose outcome matters? |
| Practical utility | 20 | Can the intended user complete the target job reliably and with acceptable adoption cost? |
| Verified completion | 15 | Is the core loop runnable, tested, released, and maintainable? |
| Leadership and differentiation | 15 | Does it provide a meaningful, durable advantage over current alternatives? |
| Engineering and operational sustainability | 15 | Can it evolve safely without disproportionate maintenance or operating cost? |
| Strategic leverage | 10 | Can it stand alone while creating verified reusable value for the portfolio? |

Every subcriterion is scored on a 0-5 anchored scale:

- **0:** absent or contradicted by evidence
- **1:** concept, documentation, or non-reproducible demonstration only
- **2:** partial implementation; core loop is incomplete
- **3:** core loop works; external value remains weakly validated
- **4:** reliable use evidence and a clear advantage
- **5:** sustained use, quantified value, and competitively tested advantage

Each subcriterion contributes `anchor score / 5 * available points`. The weighted score is calculated from the subcriteria below. Weights are frozen before evidence collection and cannot be changed to improve a unit's result.

### 3.1 User and problem value: 25

| Subcriterion | Points |
|---|---:|
| Importance and frequency of the problem | 8 |
| Clarity of target user and use case | 4 |
| Magnitude of outcome improvement | 7 |
| Adoption, repeat-use, or willingness-to-pay evidence | 6 |

### 3.2 Practical utility: 20

| Subcriterion | Points |
|---|---:|
| Core-task success and output quality | 7 |
| Installation, onboarding, and time to first value | 5 |
| Reliability, recovery, and predictability | 4 |
| Workflow compatibility and migration cost | 4 |

### 3.3 Verified completion: 15

| Subcriterion | Points |
|---|---:|
| Core-loop completeness | 5 |
| Test, build, and release reliability | 4 |
| Documentation, examples, and onboarding | 3 |
| Production monitoring, maintenance, and upgrade path | 3 |

### 3.4 Leadership and differentiation: 15

| Subcriterion | Points |
|---|---:|
| Measurable advantage over current alternatives | 5 |
| Unique and meaningful capability combination | 4 |
| Technical, data, ecosystem, or brand defensibility | 3 |
| Fit with the direction of future demand | 3 |

Feature count alone is not leadership. A capability earns leadership points only when it improves results, cost, trust, or adoption for the target job.

### 3.5 Engineering and operational sustainability: 15

| Subcriterion | Points |
|---|---:|
| Module boundaries and architectural evolvability | 4 |
| Security, privacy, compliance, and permission controls | 4 |
| Maintenance complexity, duplication, and technical debt | 4 |
| Operating cost, release cost, and failure radius | 3 |

### 3.6 Strategic leverage: 10

| Subcriterion | Points |
|---|---:|
| Independent delivery and independent value | 3 |
| Verified capability or distribution reuse | 3 |
| Standard interfaces and composability | 2 |
| Data, learning, community, or content flywheel | 2 |

## 4. Evidence confidence

Evidence confidence is reported separately from value. It is not multiplied into the raw score because doing so would collapse a high-potential hypothesis and a well-disproven product into similar numbers.

| Grade | Evidence standard |
|---|---|
| A | Production operation, real users, revenue/retention, or independent third-party validation |
| B | Reproducible testing, complete test evidence, published artifacts, or reliable use records |
| C | Current source and internal demonstrations support the claim, but real adoption evidence is absent |
| D | The claim is supported mainly by README text, plans, or unverified statements |

Evidence precedence is:

1. real adoption, revenue, retention, or repeated use
2. reproducible production records
3. published packages, integration tests, and end-to-end tests
4. unit tests and current source
5. runnable demonstrations
6. plans and design documents
7. README claims

Every material score records supporting evidence, counterevidence or missing evidence, evidence date, reproduction command or source, and uncertainty.

## 5. Gates and score caps

### 5.1 Identity gate

The target user, core problem, deliverable, and exclusions must be explicit. A unit that fails is classified as exploration rather than an investable product.

### 5.2 Core-loop gate

The core job must be repeatable end to end without undocumented manual repair.

### 5.3 Independent-delivery gate

The unit must be installable, accessible, or callable through a documented interface. Independence does not require a separate UI or repository.

### 5.4 Risk gate

An unresolved material security, legal, privacy, financial, or false-claim risk produces a `BLOCKED` decision regardless of score. Remediation work may continue, but feature expansion is not recommended while blocked.

### 5.5 Caps

- Concept or documentation without a runnable artifact: maximum 39.
- Implementation without a reproducible core loop: maximum 54.
- Working core loop without external-use evidence: maximum 74.
- Material mismatch between documentation and current implementation: evidence grade cannot exceed C until reconciled.
- Lack of standalone delivery does not cap an internal component when it has a verified caller, but independent value must be scored accordingly.

## 6. Unit decisions

| Condition | Decision |
|---|---|
| 80-100, confidence A/B, no blocker | Scale investment |
| 65-79, confidence A/B, no blocker | Continue investment and close explicit gaps |
| 65 or higher, confidence C/D | Validate before expanding the feature surface |
| 50-64 | Maintain within limits; fund only high-information experiments |
| 0-49 | Pause new features; archive or merge unless cheap evidence could reverse the decision |
| Any score with a failed risk gate | `BLOCKED`; remediate before expansion |

For a high-value, low-confidence unit, the next action must reduce the largest uncertainty. Examples include measuring task completion, benchmarking against an alternative, measuring installation success and time to first value, finding the first independent caller, or demonstrating repeat use.

## 7. Independent and portfolio value

Each unit reports four separate portfolio properties:

- **Independent value:** whether it remains worth maintaining outside this repository.
- **Synergy contribution:** verified capability, users, data, distribution, or trust supplied to other units.
- **Synergy dependence:** coupling that prevents independent evolution.
- **Separability:** feasibility of maintaining it as a separate package, service, site, or product.

Architecture diagrams and shared branding are not synergy evidence. Synergy requires a real dependency, shared user path, distribution path, or reproducible cross-unit workflow.

The active portfolio score is:

```text
portfolio score =
  mean value of active units * 65%
  + verified synergy value * 20%
  + portfolio governance quality * 15%
```

All three components are expressed on a 0-100 scale. Verified synergy and portfolio governance reuse the 0-5 anchor definitions before conversion. Lifecycle classification is frozen before unit scoring and cannot be changed afterward merely to remove a low-scoring unit from the active mean.

Inactive, archived, and explicitly incubating work is excluded from the active-unit mean. An unclassified or implicitly maintained experiment counts against portfolio governance rather than silently disappearing.

Portfolio governance evaluates lifecycle clarity, duplicated capability, documentation currency, release/test/security consistency, ability to stop low-value work, and whether the monorepo reduces coordination cost.

Portfolio classifications are:

- focused expansion
- core plus satellites
- separable portfolio
- validation portfolio
- project sprawl
- contraction portfolio

The portfolio score never overrides a unit decision.

## 8. Evaluation procedure

1. **Inventory units.** Use the current Git commit, manifests, public entrypoints, build configuration, and deployment entrypoints. Assign lifecycle and archetype.
2. **Reconcile claims.** Check versions, feature counts, integration relationships, production claims, and lifecycle status against current source and external state.
3. **Verify runnability.** Run proportionate build, test, typecheck, CLI smoke, installation/import, and core-path checks for every full-score unit.
4. **Collect external-value evidence.** Check current package publication, adoption signals, public user feedback, live-site behavior, and repository activity. Private analytics, revenue, or retention that cannot be accessed are `UNKNOWN`.
5. **Benchmark leadership.** Select two to four current alternatives per unit. Use official primary sources and reproducible task comparisons rather than broad feature tables.
6. **Score evidence first.** Record evidence and counterevidence before assigning a number. Do not change weights after scoring begins.
7. **Seek disconfirmation.** Look for unwired modules, failing tests, unusable installation paths, unique but unused features, maintenance overload, and material risk.
8. **Review independently.** An `evidence-reviewer` checks whether supplied artifacts support completion and scoring claims. Add a `proportionality-reviewer` only when complexity appears materially unjustified.
9. **Run sensitivity analysis.** Move each dimension weight up and down by five percentage points, redistributing the difference proportionally across the other dimensions so the total remains 100. A unit is conclusion-sensitive when this changes its decision class or moves it into or out of the portfolio's top-three priority set.

## 9. Evaluation report

The report is written to `docs/evaluations/2026-07-21-kernel-portfolio-evaluation.md` and contains, for each unit:

- role and target user
- gate status
- dimension and subcriterion scores
- total score and evidence confidence
- independent and synergy value
- strongest supporting evidence
- material counterevidence and unknowns
- investment decision
- three highest-information next actions
- rescore triggers

The portfolio section contains:

- complete unit ranking
- scale, validate, maintain, pause, and blocked lists
- portfolio score and classification
- verified synergies
- sprawl, duplication, and documentation drift
- internal iteration priority
- 90-day rescore triggers

## 10. Quality controls

- The framework is frozen before unit scoring begins.
- Missing private business data is reported as unknown, not zero and not inferred.
- A published artifact is evidence of completion, not automatically evidence of utility or value.
- Tests support runnability claims but cannot prove user demand.
- Competitive leadership uses current external evidence and must identify the comparison date.
- Every high score includes the strongest known counterargument.
- Reviewer infrastructure failure is reported as an infrastructure failure and never converted into a substantive verdict.
