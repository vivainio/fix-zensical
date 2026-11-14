#!/usr/bin/env python3
"""Install or check the zensical-publishing reading tools in a repository's books.

For every Zensical config (zensical.toml, zensical.<name>.toml) this:
  1. puts reading-tools.css/.js into <docs_dir>/assets/reading-tools/ (copy, or
     per-file symlinks into a shared folder with --shared),
  2. registers them in extra_css / extra_javascript, appending to existing lists,
  3. reports whether the publish workflow's `paths:` filter covers the files.

Idempotent. Meant for build time: configs are re-serialized, so comments and
formatting in them are not kept. Python 3.11+, no dependencies (tomli-w is vendored).

  fix-zensical                      install/update in ./ (all zensical*.toml)
  fix-zensical --shared docs-shared symlink every book to one shared copy
  fix-zensical --check              change nothing; exit 1 if anything is stale
  fix-zensical --dry-run            show what would change
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import tomllib
from pathlib import Path

from ._vendor import tomli_w

ASSETS = Path(__file__).resolve().parent / "assets"
SUBDIR = "assets/reading-tools"
REGISTER = {"extra_css": "reading-tools.css", "extra_javascript": "reading-tools.js"}


# --- file sync ----------------------------------------------------------------


def same(a: Path, b: Path) -> bool:
    return a.exists() and b.exists() and a.read_bytes() == b.read_bytes()


def sync_copy(src: Path, dest: Path, apply: bool) -> str:
    if dest.is_file() and not dest.is_symlink() and same(src, dest):
        return "ok"
    status = "updated" if dest.exists() or dest.is_symlink() else "created"
    if apply:
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.is_symlink():
            dest.unlink()
        dest.write_bytes(src.read_bytes())
    return status


def sync_link(target: Path, dest: Path, apply: bool) -> str:
    rel = os.path.relpath(target, dest.parent)
    if dest.is_symlink() and os.readlink(dest) == rel:
        return "ok"
    status = "updated" if dest.exists() or dest.is_symlink() else "created"
    if apply:
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists() or dest.is_symlink():
            dest.unlink()
        dest.symlink_to(rel)
    return status


# --- workflow paths filter ------------------------------------------------------


def glob_match(pattern: str, path: str) -> bool:
    rx = re.escape(pattern).replace(r"\*\*", ".*").replace(r"\*", "[^/]*").replace(r"\?", "[^/]")
    return re.fullmatch(rx, path) is not None


def workflow_problems(repo: Path, files: list[str]) -> list[str]:
    out = []
    wf_dir = repo / ".github" / "workflows"
    for wf in sorted(wf_dir.glob("*.y*ml")) if wf_dir.is_dir() else []:
        text = wf.read_text()
        if "zensical" not in text:
            continue
        patterns: list[str] = []
        lines = text.splitlines()
        for i, line in enumerate(lines):
            if re.match(r"^\s*paths:\s*$", line):
                for item in lines[i + 1:]:
                    m = re.match(r"""^\s*-\s*["']?([^"'#]+?)["']?\s*(#.*)?$""", item)
                    if m:
                        patterns.append(m.group(1))
                    elif item.strip():
                        break
        patterns = [p for p in patterns if not p.startswith("!")]
        if not patterns:
            continue  # no paths filter: every push builds
        for f in files:
            if not any(glob_match(p, f) for p in patterns):
                out.append(f"{wf.relative_to(repo)}: `paths:` does not cover {f}")
    return out


# --- driver --------------------------------------------------------------------


def process(cfg: Path, repo: Path, shared: Path | None, apply: bool) -> tuple[list[str], list[str]]:
    """Returns (report lines, problems)."""
    report: list[str] = []
    problems: list[str] = []
    text = cfg.read_text()
    data = tomllib.loads(text)
    proj = data["project"] if isinstance(data.get("project"), dict) else data
    docs_dir = cfg.parent / proj.get("docs_dir", "docs")
    dest_dir = docs_dir / SUBDIR
    touched: list[str] = []

    for name in REGISTER.values():
        src = ASSETS / name
        dest = dest_dir / name
        if shared is not None:
            st = sync_copy(src, shared / name, apply)
            touched.append((shared / name).relative_to(repo).as_posix())
            if st != "ok":
                report.append(f"  {st:8} {(shared / name).relative_to(repo)}")
                problems.append(f"{shared / name}: {st}")
            st = sync_link(shared / name, dest, apply)
        else:
            st = sync_copy(src, dest, apply)
        touched.append(dest.relative_to(repo).as_posix())
        report.append(f"  {st:8} {dest.relative_to(repo)}")
        if st != "ok":
            problems.append(f"{dest}: {st}")

    changed = False
    for key, name in REGISTER.items():
        entry = f"{SUBDIR}/{name}"
        if entry in proj.get(key, []):
            report.append(f"  ok       {key} has {entry}")
            continue
        proj.setdefault(key, []).append(entry)
        changed = True
        report.append(f"  {'added' if apply else 'missing':8} {key} += {entry}")
        problems.append(f"{cfg.name}: {key} lacks {entry}")
    if changed and apply:
        cfg.write_text(tomli_w.dumps(data))

    for p in workflow_problems(repo, touched):
        report.append(f"  WARN     {p}")
        problems.append(p)
    return report, problems


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", default=".", help="repository root (default: .)")
    ap.add_argument("--config", action="append", help="config file (repeatable; default: all zensical*.toml)")
    ap.add_argument("--shared", help="shared folder (relative to repo): keep one copy there, symlink each book to it")
    ap.add_argument("--check", action="store_true", help="change nothing; exit 1 if anything is missing or stale")
    ap.add_argument("--dry-run", action="store_true", help="show what would change, change nothing")
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    cfgs = [repo / c for c in args.config] if args.config else sorted(
        {*repo.glob("zensical.toml"), *repo.glob("zensical.*.toml")}
    )
    if not cfgs:
        print("no zensical*.toml found", file=sys.stderr)
        return 2
    shared = repo / args.shared if args.shared else None
    apply = not (args.check or args.dry_run)

    all_problems = 0
    for cfg in cfgs:
        print(cfg.relative_to(repo))
        report, problems = process(cfg, repo, shared, apply)
        print("\n".join(report))
        all_problems += len(problems)
    if args.check and all_problems:
        print(f"\n{all_problems} problem(s). Run without --check to fix.", file=sys.stderr)
        return 1
    if args.dry_run and all_problems:
        print("\ndry run: nothing changed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
