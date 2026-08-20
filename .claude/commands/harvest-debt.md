---
description: Collects SHORTCUT markers left in the codebase into TECH-DEBT.md, so deferred work doesn't quietly disappear.
---

Sweep the codebase for deliberately deferred shortcuts and consolidate them.

1. Search for `SHORTCUT:` markers across the project (skip `node_modules`,
   `.venv`, build output, and anything in `.gitignore`).
2. For each one, capture: file and line, what was deferred, the stated reason,
   and — where you can tell from the surrounding code — a rough sense of what it
   would take to resolve.
3. Append them to `TECH-DEBT.md` under a dated `## Harvested <YYYY-MM-DD>`
   section. Don't duplicate entries already listed there from a previous harvest;
   if a marker has since disappeared from the code, note it as resolved instead.
4. Sort by rough blast radius: things that will bite as the project grows first,
   cosmetic ones last.
5. Report a count in the HANDOFF: how many found, how many new, how many resolved
   since the last harvest.

Don't fix anything. This command only surfaces and records. Fixing goes through
the normal flow, and the human decides what's worth paying down.

If a marker is really an omission rather than a shortcut — missing validation,
absent error handling, a security gap — flag it separately and prominently. Those
aren't debt, they're defects.
