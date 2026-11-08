#!/usr/bin/env bash
# Validate every tracked top-level stack and verify the README navigation is current.
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ ! -f .env ]]; then
  echo "missing $ROOT/.env" >&2
  exit 2
fi

if ! command -v docker >/dev/null 2>&1; then
  echo "docker not found" >&2
  exit 2
fi

fail=0
count=0
shopt -s nullglob

for file in */compose.yml */compose.yaml */docker-compose.yml */docker-compose.yaml; do
  stack=${file%%/*}
  if command -v git >/dev/null 2>&1 && git check-ignore -q "$stack"; then
    continue
  fi
  count=$((count + 1))
  if (cd "$stack" && docker compose --env-file "$ROOT/.env" -f "$ROOT/$file" config -q); then
    printf 'OK   %s\n' "$stack"
  else
    printf 'FAIL %s\n' "$stack" >&2
    fail=1
  fi
done

printf '%d stack(s) checked\n' "$count"

if command -v python3 >/dev/null 2>&1 && [[ -f scripts/nav.py ]]; then
  python3 scripts/nav.py --check || fail=1
else
  echo "skip navigation check (python3 or scripts/nav.py missing)" >&2
fi

exit "$fail"
