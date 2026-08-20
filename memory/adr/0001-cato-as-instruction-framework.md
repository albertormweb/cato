# ADR 0001 — Cato as an instruction framework

- **Status:** Accepted
- **Date:** 2026-08-20

## Context

We need an internal way to ship products quickly with Claude Code while keeping
scope, verification, and human veto. Selling a hosted runtime is out of scope.

## Decision

Ship Cato as a **markdown + optional Python tooling** template: Claude Code
orchestrates eight specialists; a master prompt bootstraps MVP design; one human
approval gate; then autonomous build with hard stops. Tool frontmatter must match
write responsibilities. Tuneable numbers live in `config.md`; constraints in
`rules-hard.md`; modes in `process.md`.

## Consequences

- Pros: portable, inspectable, calibratable; no app runtime to maintain for the
  framework itself; honesty about unmeasured claims is easy to keep.
- Cons: budgets and approval labels are not filesystem locks; non-Claude-Code
  hosts degrade to rules-only; product value stays unproven until a real E2E run.

## Alternatives considered

- Single mega-prompt — rejected (no role separation, weak audit).
- Heavy custom runtime / agent framework package — rejected (overkill for
  internal bootstrap; binds stack).
