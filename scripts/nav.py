#!/usr/bin/env python3
"""Regenerate the README navigation table from the top-level stack directories.

Ports come from `docker compose config`, so they cannot drift from the compose
files. Existing rows keep their name/description/icon; a new stack directory
gets a default row. Run with --check to verify the table is current without
writing it.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
ENV_FILE = ROOT / ".env"
BEGIN = "<!-- BEGIN NAV -->"
END = "<!-- END NAV -->"
COMPOSE_NAMES = (
    "compose.yml",
    "compose.yaml",
    "docker-compose.yml",
    "docker-compose.yaml",
)


def compose_file(stack: Path) -> Path | None:
    for name in COMPOSE_NAMES:
        path = stack / name
        if path.is_file():
            return path
    return None


def is_ignored(path: Path) -> bool:
    """Local-only stacks (audionotes/, code/, archive-box/) are gitignored."""
    try:
        result = subprocess.run(
            ["git", "-C", str(ROOT), "check-ignore", "-q", path.name],
            capture_output=True,
        )
    except FileNotFoundError:
        return False
    return result.returncode == 0


def stacks() -> list[Path]:
    return sorted(
        (
            path
            for path in ROOT.iterdir()
            if path.is_dir()
            and not path.name.startswith(".")
            and compose_file(path)
            and not is_ignored(path)
        ),
        key=lambda path: path.name,
    )


def lan_ip() -> str:
    if ENV_FILE.is_file():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            match = re.match(r"^\s*LAN\s*=\s*(.+?)\s*$", line)
            if match:
                return match.group(1).strip("'\"")
    return "127.0.0.1"


def published_ports(stack: Path) -> list[int]:
    config = compose_file(stack)
    if config is None:
        return []

    command = [
        "docker",
        "compose",
        "--env-file",
        str(ENV_FILE),
        "-f",
        str(config),
        "config",
        "--format",
        "json",
    ]
    try:
        env = os.environ.copy()
        env["PWD"] = str(stack)
        result = subprocess.run(command, cwd=stack, env=env, text=True, capture_output=True)
    except FileNotFoundError:
        raise SystemExit("docker not found") from None
    if result.returncode != 0:
        raise SystemExit(f"{stack.name}: docker compose config failed\n{result.stderr.strip()}")

    data = json.loads(result.stdout)
    ports: set[int] = set()
    for service in data.get("services", {}).values():
        for mapping in service.get("ports") or []:
            published = mapping.get("published")
            if published in (None, "", 0, "0"):
                continue
            text = str(published)
            span = re.fullmatch(r"(\d+)-(\d+)", text)
            if span:
                start, end = (int(part) for part in span.groups())
                ports.update(range(start, end + 1))
            else:
                digits = re.match(r"\d+", text)
                if digits:
                    ports.add(int(digits.group()))
    return sorted(ports)


def pick_port(ports: list[int]) -> int | None:
    """Prefer the Web UI range; otherwise accept a single published port."""
    web = [port for port in ports if 8001 <= port <= 8999]
    if web:
        return min(web)
    return ports[0] if len(ports) == 1 else None


def split_row(line: str) -> list[str] | None:
    line = line.strip()
    if not line.startswith("|") or not line.endswith("|"):
        return None
    return [cell.strip() for cell in line[1:-1].split("|")]


def port_from_cell(cell: str) -> int | None:
    match = re.search(r"\d+", cell)
    return int(match.group()) if match else None


def name_from_cell(cell: str) -> str:
    match = re.match(r"\[([^\]]+)\]", cell)
    return (match.group(1) if match else cell).strip()


def read_rows(text: str) -> list[list[str]]:
    match = re.search(re.escape(BEGIN) + r"\n(.*?)\n" + re.escape(END), text, re.S)
    if not match:
        raise SystemExit(f"{README}: missing {BEGIN} / {END} markers")

    rows = []
    for line in match.group(1).splitlines():
        cells = split_row(line)
        if not cells or len(cells) != 4:
            continue
        if cells[0].lower() == "port":
            continue
        if all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
            continue
        rows.append(cells)
    return rows


def build(rows: list[list[str]]) -> tuple[str, list[list[str]], list[str]]:
    existing: dict[str, list[str]] = {}
    problems: list[str] = []
    for row in rows:
        key = name_from_cell(row[1]).lower()
        if key in existing:
            problems.append(f"duplicate navigation row: {key}")
        existing[key] = row

    lan = lan_ip()
    output: list[list[str]] = []
    seen: dict[int, str] = {}

    for stack in stacks():
        ports = published_ports(stack)
        for port in ports:
            if port in seen:
                problems.append(f"duplicate host port {port}: {seen[port]} and {stack.name}")
            else:
                seen[port] = stack.name

        port = pick_port(ports)
        row = existing.pop(stack.name.lower(), None)
        if row:
            row = list(row)
            old_port = port_from_cell(row[0])
            row[0] = f"`{port}`" if port is not None else "--"
            if old_port and port and old_port != port:
                row[3] = row[3].replace(f":{old_port}", f":{port}")
            elif old_port is None and port is not None and row[3] in ("", "--"):
                row[3] = f"[↗](http://{lan}:{port})"
        else:
            row = [
                f"`{port}`" if port is not None else "--",
                f"[{stack.name}](./{stack.name}/)",
                "",
                f"[↗](http://{lan}:{port})" if port is not None else "--",
            ]
        output.append(row)

    for name in existing:
        problems.append(f"navigation row without a stack directory: {name}")

    output.sort(
        key=lambda row: (
            port_from_cell(row[0]) is not None,
            port_from_cell(row[0]) or 0,
            name_from_cell(row[1]).lower(),
        )
    )

    lines = [
        "| Port | Name | Desc | Nav |",
        "| ---- | ---- | ---- | ---- |",
    ]
    lines += ["| " + " | ".join(row) + " |" for row in output]
    return "\n".join(lines), output, problems


def signature(rows: list[list[str]]) -> list[tuple[str, int | None]]:
    return [(name_from_cell(row[1]).lower(), port_from_cell(row[0])) for row in rows]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="only check; do not write README")
    args = parser.parse_args()

    if not ENV_FILE.is_file():
        print(f"missing {ENV_FILE}", file=sys.stderr)
        return 2

    text = README.read_text(encoding="utf-8")
    rows = read_rows(text)
    block, generated, problems = build(rows)

    for problem in problems:
        print(f"warning: {problem}", file=sys.stderr)

    if args.check:
        current = signature(rows)
        wanted = signature(generated)
        if current != wanted:
            print("navigation is out of date; run: python3 scripts/nav.py", file=sys.stderr)
            for item in wanted:
                if item not in current:
                    print(f"  missing: {item[0]} ({item[1]})", file=sys.stderr)
            for item in current:
                if item not in wanted:
                    print(f"  stale:   {item[0]} ({item[1]})", file=sys.stderr)
            return 1
        return 1 if problems else 0

    match = re.search(re.escape(BEGIN) + r"\n(.*?)\n" + re.escape(END), text, re.S)
    assert match is not None
    current_block = match.group(1)
    if current_block.strip("\n") != block:
        README.write_text(
            text[: match.start(1)] + block + text[match.end(1) :],
            encoding="utf-8",
        )
        print(f"updated {README}")
    else:
        print("navigation is up to date")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
