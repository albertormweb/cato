# The minimalism ladder

Before writing code, stop at the first rung that holds:

```
1. Does this need to exist?      → no: skip it
2. Already in this codebase?     → reuse it, don't rewrite
3. Does the stdlib do it?        → use it
4. Native platform feature?      → use it
5. Already-installed dependency? → use it
6. Fits in one line?             → one line
7. Only then: the minimum that works
```

The ladder runs *after* you understand the problem, not instead of it. Read the
code your change touches and trace the real flow before picking a rung. Lazy about
the solution, never about reading.

Lazy is not negligent: validation at trust boundaries, error handling, security
and accessibility are never on the chopping block. Code ends up small because
it's what the task needs, not because it's golfed.

`implementer` walks it before writing. `reviewer` checks it was walked — a simpler
rung that would have worked is a finding, same as a bug.

## Deferred shortcuts

When a shortcut is taken deliberately, mark it inline with a `SHORTCUT:` comment
saying what was deferred and why:

```python
# SHORTCUT: no pagination — fine under ~200 rows, revisit if the table grows
```

`/harvest-debt` collects these into `TECH-DEBT.md` so "later" doesn't quietly
become "never". Don't use the marker to excuse skipping validation or error
handling — those aren't shortcuts, they're omissions, and `/harvest-debt` reports
them separately.
