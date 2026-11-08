#!/usr/bin/env bash
# Apply compose changes in bulk: validate, optionally pull, then recreate.
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

usage() {
  cat <<'EOF'
Usage: scripts/up.sh <--all | --changed [REF] | STACK...> [--pull] [--dry-run]

  --all              every stack in the repository
  --changed [REF]    stacks touched since REF (default HEAD; after committing use HEAD~1)
  --pull             docker compose pull before up
  --dry-run          print commands without running them
  STACK...           one or more stack directories, e.g. gitea dockge

Examples:
  scripts/up.sh --changed
  scripts/up.sh --all --dry-run
  scripts/up.sh gitea dockge --pull
EOF
}

compose_file() {
  local stack=$1 name
  for name in compose.yml compose.yaml docker-compose.yml docker-compose.yaml; do
    if [[ -f "$stack/$name" ]]; then
      printf '%s\n' "$stack/$name"
      return 0
    fi
  done
  return 1
}

all_stacks() {
  local file stack
  shopt -s nullglob
  for file in */compose.yml */compose.yaml */docker-compose.yml */docker-compose.yaml; do
    stack=${file%%/*}
    if command -v git >/dev/null 2>&1 && git check-ignore -q "$stack"; then
      continue
    fi
    printf '%s\n' "$stack"
  done | sort -u
}

changed_stacks() {
  local ref=$1
  {
    git diff --name-only "$ref" -- .
    git ls-files --others --exclude-standard
  } | awk -F/ 'NF > 1 { print $1 }' | sort -u
}

run_stack() {
  local stack=$1 file
  if ! file=$(compose_file "$stack"); then
    echo "not a stack: $stack" >&2
    return 1
  fi

  local command=(docker compose --env-file "$ROOT/.env" -f "$ROOT/$file")
  if $dry_run; then
    printf 'cd %q && ' "$stack"
    printf '%q ' "${command[@]}" config -q
    printf '\n'
    if $pull; then
      printf 'cd %q && ' "$stack"
      printf '%q ' "${command[@]}" pull
      printf '\n'
    fi
    printf 'cd %q && ' "$stack"
    printf '%q ' "${command[@]}" up -d --remove-orphans
    printf '\n'
    return 0
  fi

  if ! (cd "$stack" && "${command[@]}" config -q); then
    echo "FAIL config: $stack" >&2
    return 1
  fi
  if $pull; then
    (cd "$stack" && "${command[@]}" pull) || return 1
  fi
  (cd "$stack" && "${command[@]}" up -d --remove-orphans)
}

mode=""
ref="HEAD"
pull=false
dry_run=false
targets=()

while (($#)); do
  case "$1" in
    --all)
      mode=all
      shift
      ;;
    --changed)
      mode=changed
      shift
      if (($#)) && [[ $1 != -* ]]; then
        ref=$1
        shift
      fi
      ;;
    --pull)
      pull=true
      shift
      ;;
    --dry-run)
      dry_run=true
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    --*)
      echo "unknown option: $1" >&2
      usage
      exit 2
      ;;
    *)
      targets+=("$1")
      shift
      ;;
  esac
done

if [[ -n "$mode" && ${#targets[@]} -gt 0 ]]; then
  echo "choose --all, --changed, or explicit stacks, not both" >&2
  exit 2
fi

if [[ ! -f .env ]]; then
  echo "missing $ROOT/.env" >&2
  exit 2
fi

case "$mode" in
  all)
    mapfile -t targets < <(all_stacks)
    ;;
  changed)
    if ! command -v git >/dev/null 2>&1 || ! git rev-parse --verify "$ref" >/dev/null 2>&1; then
      echo "cannot resolve git ref: $ref" >&2
      exit 2
    fi
    mapfile -t targets < <(changed_stacks "$ref")
    echo "note: .env changes are not visible to --changed; use --all or name stacks explicitly" >&2
    ;;
  "")
    if ((${#targets[@]} == 0)); then
      usage
      printf '\nStacks:\n'
      all_stacks | sed 's/^/  /'
      exit 2
    fi
    ;;
esac

valid=()
for stack in "${targets[@]}"; do
  if compose_file "$stack" >/dev/null; then
    valid+=("$stack")
  elif [[ "$mode" != changed ]]; then
    echo "not a stack: $stack" >&2
    exit 2
  fi
done
if ((${#valid[@]})); then
  targets=("${valid[@]}")
else
  targets=()
fi
if ((${#targets[@]} == 0)); then
  echo "no stacks selected"
  exit 0
fi

fail=0
for stack in "${targets[@]}"; do
  printf '==> %s\n' "$stack"
  run_stack "$stack" || fail=1
done

exit "$fail"
