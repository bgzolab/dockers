# AGENTS.md

## What this is

- ~30 independent Docker Compose stacks, one directory per self-hosted service, deployed to one LAN host (`192.168.31.20`). No application code, tests, lint, or CI.
- `README.md` is also the GitHub Pages dashboard (rendered via `jekyll-readme-index`); `_config.yml` configures that build.
- `audionotes/`, `archive-box/`, `code/`, `code-server/` are gitignored local-only stacks. `docker-embyhack/` is retired (struck through in README).

## Commands

Run from a service directory:

```shell
docker compose --env-file ../.env config -q   # validate without deploying
docker compose --env-file ../.env up -d       # deploy/update on the host
docker compose --env-file ../.env logs -f
```

- Compose filenames vary (`compose.yml`, `docker-compose.yml`, `compose.yaml`). `docker compose` auto-detects them inside the directory; from the repo root pass the exact file: `docker compose -f gitea/docker-compose.yml --env-file .env up -d`.
- Always pass `--env-file`. Compose run inside a service directory does not find the root `.env` and silently expands `${...}` to empty values (wrong bind paths/ports).
- This repo controls live services. Do not `up`, `down`, or `restart` unless the task asks; `config -q` is the safe verification.
- No test suite exists. Validate every edited compose file with `config -q`; it resolves all `${...}` variables.

## Configuration

- `.env` at the root is untracked and holds the LAN IP, host paths, PUID/PGID, and all passwords/tokens. Compose files must reference `${VAR}`, never inline values.
- `.env` defines `WORKSPACE`, `DOCUMENTS`, `VIDEOS`, `MUSIC`, `DOWNLOAD`; stacks bind media/config paths from them. Make sure they point at real host paths before deploying (e.g. komga binds `${WORKSPACE}/komga/config`).
- A few stacks hardcode host-specific paths/hardware: `jellyfin` and `windows` (disks), `motrix` (downloads), `dockge` (`/opt/stacks` → this repo). They only work on this host.
- Runtime state lives in ignored per-service directories (`data/`, `config/`, `*.db`, sessions). Never commit it.
- New service directory: add the directory to `_config.yml` `exclude:` and run `python3 scripts/nav.py`; the README row is generated from the compose file.

## Git hook

```shell
git config core.hooksPath .githooks   # once per clone
```

- `.githooks/pre-commit` blocks staged secrets. Use `git commit --no-verify` only for confirmed false positives.

## Docs preview

- `bundle install` then `bundle exec jekyll serve` (or `build`). On a populated host the build fails on unreadable root-owned stack data unless its directory is in `_config.yml` `exclude:`; that is expected.
