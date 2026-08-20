# Your first project

Walkthrough start to finish. Terms: `CONCEPTS.md`. Template health: `VALIDATION.md`.

## Before you start

Claude Code installed. The template is markdown — no app build. Optional Python in
`tooling/` maintains the framework (CI uses it).

## 1. Clone and initialise

```bash
git clone https://github.com/<your-user>/cato-ai-framework my-project
cd my-project
./setup.sh
```

Provide a name, stack, and **master prompt** (what you're building, for whom,
uncertainties). Or in Claude Code:

```
/init-project "a tool that watches public tender feeds and alerts small firms about relevant ones"
```

Use `--dry-run` first if you want the plan without writes. Use `--interview` if
you want gaps asked before generation.

## 2. Approve once, then build

After generation, read the MVP cut (especially out of scope), then:

1. Move genesis `DESIGN.md` (and any listed artifacts) to `APPROVED` in
   `PLANNING.md`.
2. Fill `tests/README.md` (fast + full commands, or "no tests yet").
3. Fill `.claude/claude-brand-style.md` if there is user-facing UI/copy.
4. Say:

```
Build PLANNING.md Now; work in a loop until the first milestone ships.
```

That is the whole loop: one prompt, one approval gate, then agents build under
autonomy rules (hard stops only). Details: `.claude/process.md`.

## 3. Expect to be argued with

`strategist` cuts scope. Notifications + dashboard + mobile + API often become one
MVP slice and the rest V2/FUTURE — with reasons. Disagreement is fine; argue with
a line in `specs/`, not with the void. Parked work is not deleted.

## 4. What init wrote

- **`specs/0001-*.md`** — in / out of scope, success criteria
- **`DESIGN.md`** — technical shape
- **`PLANNING.md`** — concrete `Now`
- **`memory/adr/0001-*.md`** — genesis decision

Nothing application-coded yet. Deliberate.

## 5. While it builds

You will see HANDOFFs. Surprises that are working as designed:

- **`BLOCKED` on ambiguity** instead of a silent guess
- **`reviewer` rejecting `qa: PASS`** — tests ≠ judgment; over-building counts
- **Stops for hard rules** (secrets, merge, new deps, pending approvals)

Loop mode raises the QA bar each round and exits on identical failures (spec/design
problem, not "one more try").

## 6. Later approvals

New structural design, mockups, or deployment changes go to `PENDING_APPROVAL`
again. Only you clear them.

## 7. Close the session

```
Let's wrap up
```

Orchestrator writes `memory/session-log.md` and appends `memory/agent-log.md`.
Optionally:

```bash
python tooling/trust_score.py --write
```

## 8. After a few real sessions

```
/calibrate
```

Proposals edit `.claude/config.md` only after your approval. Shipped numbers are
guesses until then.

## Common friction

| Complaint | Likely cause |
|---|---|
| Too many questions | Thin spec — invest in `specs/` |
| Won't build what I asked | Check out-of-scope; overturn with a reason |
| Slower than raw Claude Code | Expected on one-file tasks; if slow on hard work too, run `benchmarks/` |
| One agent always wrong | Read `trust-score.md`, then rewrite that agent's `.md` |

## Optional later

- Notes in `domain/` as language firms up
- Reusable workflows under `.claude/skills/`
- Fair comparison results under `benchmarks/results/`
