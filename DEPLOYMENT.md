# Deployment

> For **generated products**, `architect` fills this after kickoff (or a future
> `ops` agent). Production-affecting changes need `PENDING_APPROVAL` in
> `PLANNING.md`.
>
> This template repository itself has no app deployment — only optional GitHub
> Actions for framework integrity (`.github/workflows/tests.yml`).

## Environments

| Environment | Where it lives | URL | Notes |
|---|---|---|---|
| Local | developer machine | - | Claude Code + optional Python for `tooling/` |
| CI | GitHub Actions | - | `pytest tooling/` + `sync_rules.py` |
| Staging | <product-specific> | <fill in> | |
| Production | <product-specific> | <fill in> | |

## Infrastructure

- Hosting: <fill in per product>
- Domain / DNS: <fill in>
- Database: <fill in>
- Asset storage: <fill in>

## Deployment process

<template: none — product clones fill this>

## Secrets management

Never store secrets in this repo. Product clones: document where secrets live and
how they rotate.

## Rollback

<template / product-specific>
