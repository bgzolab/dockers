#!/usr/bin/env python3
"""Regenerate the README navigation table from the top-level stack directories.

Each compose file starts with two metadata lines:

    # short description
    # project URL

Ports come from `docker compose config`, so they cannot drift from the compose
files. The table is always rewritten from those two sources; --check verifies
it without writing.
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


def build() -> tuple[str, list[list[str]], list[str]]:
    problems: list[str] = []
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
        desc, url = read_meta(compose_file(stack))
        if not desc:
            problems.append(f"{stack.name}: missing description on line 1")
        if not url:
            problems.append(f"{stack.name}: missing URL on line 2")
        elif not re.match(r"https?://", url):
            problems.append(f"{stack.name}: line 2 is not an http(s) URL: {url!r}")

        name_cell = f"[{stack.name}]({url})" if url else f"[{stack.name}](./{stack.name}/)"
        output.append(
            [
                f"`{port}`" if port is not None else "--",
                name_cell,
                desc.replace("|", r"\|"),
                f"[↗](http://{lan}:{port})" if port is not None else "",
            ]
        )

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


def read_meta(config: Path | None) -> tuple[str, str]:
    """First line is the description, second line is the project URL."""
    if config is None:
        return "", ""
    lines = config.read_text(encoding="utf-8").splitlines()

    def field(index: int) -> str:
        if index >= len(lines):
            return ""
        line = lines[index].strip()
        return line.lstrip("#").strip() if line.startswith("#") else ""

    return field(0), field(1)


def signature(rows: list[list[str]]) -> list[tuple[str, ...]]:
    return [tuple(row) for row in rows]


def row_key(row: list[str]) -> tuple[str, int | None]:
    return (name_from_cell(row[1]).lower(), port_from_cell(row[0]))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="only check; do not write README")
    args = parser.parse_args()

    if not ENV_FILE.is_file():
        print(f"missing {ENV_FILE}", file=sys.stderr)
        return 2

    text = README.read_text(encoding="utf-8")
    block, generated, problems = build()

    for problem in problems:
        print(f"warning: {problem}", file=sys.stderr)

    if args.check:
        rows = read_rows(text)
        if signature(rows) != signature(generated):
            print("navigation is out of date; run: ./scripts/nav.py", file=sys.stderr)
            current_keys = {row_key(row) for row in rows}
            wanted_keys = {row_key(row) for row in generated}
            for item in sorted(wanted_keys - current_keys, key=str):
                print(f"  missing: {item[0]} ({item[1]})", file=sys.stderr)
            for item in sorted(current_keys - wanted_keys, key=str):
                print(f"  stale:   {item[0]} ({item[1]})", file=sys.stderr)
            if current_keys == wanted_keys:
                print("  row content or order changed; run the generator to normalize", file=sys.stderr)
            return 1
        return 1 if problems else 0

    match = re.search(re.escape(BEGIN) + r"\n(.*?)\n" + re.escape(END), text, re.S)
    assert match is not None
    # Blank lines around the table keep kramdown (GitHub Pages) from parsing the
    # markers and the table as one paragraph, which renders the table as text.
    expected = "\n" + block + "\n"
    current_block = match.group(1)
    if current_block != expected:
        README.write_text(
            text[: match.start(1)] + expected + text[match.end(1) :],
            encoding="utf-8",
        )
        print(f"updated {README}")
    else:
        print("navigation is up to date")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
