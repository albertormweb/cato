# Decision ledger

Undeliberated choices made while building — places where the spec was silent and
someone (usually `implementer`) picked an answer anyway. Tests can still pass and
review can still look clean; these entries exist so the human can see what was
assumed.

**How to read:** entries are ranked **least-confident first**. Start at the top;
stop when the remaining items feel settled enough. Ranking is the filter — there
is no entry cap.

**What this is not:** ADRs in `memory/adr/` are deliberate decisions. Do not
duplicate them here. This ledger never blocks work and never triggers a fix on
its own — it only reports.

## Entry format

```markdown
### <short title>
- confidence: low | medium | high  (sort: low first)
- decided: <what was chosen>
- spec said: <usually "nothing" / quote if anything>
- alternatives: <what else was plausible>
- reverse cost: <cheap | moderate | expensive — and why>
- lives in: <paths or symbols>
- session: <YYYY-MM-DD>
```

## Ledger

<!-- New session blocks append below. Within a session, order by confidence
     ascending (least sure at the top of that block). -->
