# Tests

## This template repository

Framework integrity tests live in `tooling/` (not here):

```bash
python -m pytest tooling/ -c tooling/pytest.ini
```

CI runs them on push/PR. For **product clones**, replace the commands below with
your stack's suites. `qa` reads this file literally.

## Convention (generated products)

`implementer` writes the test alongside the logic, in the same change. `qa` does
not write new tests: it runs them, checks coverage minimums from
`.claude/config.md`, and reports gaps.

## Commands

- **Fast suite** (trivial/medium; loop iteration 1):
  ```bash
  python -m pytest tooling/ -c tooling/pytest.ini
  ```
- **Full suite** (large / before merge; loop iteration 2+):
  ```bash
  python -m pytest tooling/ -c tooling/pytest.ini
  python tooling/sync_rules.py
  ```

On a blank product clone with no app tests yet, replace these with your real
commands — or write explicitly: `No product tests yet.` so `qa` returns
`BLOCKED` instead of inventing `PASS`.

## Any stack

The framework does not assume a language. Fast and full must differ in cost when
you have a real app — loop mode depends on that distinction.
