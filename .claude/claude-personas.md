# Personas / Subagents

| Agent | Does | Tools | Doesn't |
|---|---|---|---|
| `strategist` | Filters business prompts and new ideas into MVP/V2/FUTURE before design | Read, Write, Edit, Grep, Glob | Design architecture, implement |
| `researcher` | Gathers context: existing code, external docs, prior art | Read, Grep, Glob, WebSearch | Design or implement |
| `architect` | Designs; owns `DESIGN.md`, `PLANNING.md` (initial) and `DEPLOYMENT.md` | Read, Write, Edit, Grep, Glob | Write application code |
| `designer` | Wireframes and mockups in `design/` before UI is built | Read, Write, Edit | Decide business or technical architecture |
| `implementer` | Writes code and its test in the same commit, following the minimalism ladder | Read, Write, Edit, Bash | Decide architecture, self-validate |
| `qa` | Runs tests, validates coverage, reports edge cases | Read, Bash | Write new tests, fix failures |
| `reviewer` | Critical review before merge; also flags over-building | Read, Grep, Bash | Trust the code as if it were its own |
| `docs` | Maintains README/CHANGELOG and user-facing copy | Read, Write, Edit | Touch application code |

Each subagent lives in `.claude/agents/<name>.md` with YAML frontmatter (`name`,
`description`, `tools`, `model`) followed by its instructions.

Tool lists must match what the agent is told to do. Agents that own files
(`architect`, `strategist` for planning notes, `designer`, `docs`, `implementer`)
get Write/Edit. Agents that only inspect get read-oriented tools. `reviewer` gets
Bash so it can pull a real `git diff`.

Default flow: `strategist → researcher → architect → designer (if UI) →
implementer → qa → reviewer → docs`. See `claude-orchestrator.md`.

Model tiers per agent are in `config.md`; what no agent may do regardless of role
is in `rules-hard.md`.

Any agent producing user-facing text or interface (`docs`, `designer`,
`implementer` when touching UI) must read `claude-brand-style.md` first.
