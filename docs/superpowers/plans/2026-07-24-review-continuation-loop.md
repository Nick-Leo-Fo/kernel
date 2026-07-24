---
title: Reviewer Continuation Loop Implementation Plan
date: 2026-07-24
status: in-progress
---

# Implementation Plan

1. Extend the existing RED contract with durable project-review and feedback
   writer assertions.
2. Add a concise `review-continuation.md` reference and an unavoidable
   continuation rule in `project-review/SKILL.md`.
3. Add `write_framing_feedback.py` and deterministic tests.
4. Extend the RPT Review Procedure with request repair, owner adjudication,
   size-based clearance, and next-stage continuation.
5. Update equity-timesfm Case 001 plan and handoff to use the new gate.
6. Run project-review tests, both skill validators, the 37-case RPT suite,
   automation tests, and equity-timesfm tests.
