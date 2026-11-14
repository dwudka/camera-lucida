"""Lint a PR's title, body and commits against the repo's commit rules.

Reads PR_TITLE, PR_BODY, BASE and HEAD from the environment (BASE and HEAD
are commit SHAs). With no BASE/HEAD it lints only the title and body.
Run locally:  BASE=origin/main HEAD=HEAD python3 .github/scripts/commit_lint.py
"""
from __future__ import annotations

import os
import re
import subprocess
import sys

TYPES = "feat|fix|docs|test|ci|chore|refactor|perf|style|build|revert"
SUBJECT = re.compile(rf"^({TYPES})(\([a-z0-9][a-z0-9-]*\))?!?: [^A-Z\s].*[^.\s]$")
# File paths such as CLAUDE.md and .claude/ are allowed; attribution is not.
ATTRIBUTION = re.compile(
    r"co-authored-by:.*(claude|anthropic|copilot|gpt|gemini|\bai\b)"
    r"|generated (with|by)\b.*(claude|anthropic|ai\b|copilot|gpt|gemini)"
    r"|\U0001F916"
    r"|\bclaude code\b|\banthropic\b"
    r"|(?<![./\w])claude(?!\.md|/|-)\b",
    re.I,
)


def problems(kind: str, subject: str, body: str = "") -> list[str]:
    out = []
    if subject.startswith(("Merge ", "Revert \"")):
        return out
    if not SUBJECT.match(subject):
        out.append(f"{kind}: subject is not `type(scope): summary` (lower-case start, no trailing period): {subject!r}")
    if len(subject) > 72:
        out.append(f"{kind}: subject is {len(subject)} characters (limit 72): {subject!r}")
    for line in (subject + "\n" + body).splitlines():
        if ATTRIBUTION.search(line):
            out.append(f"{kind}: names an AI assistant as author or tool: {line.strip()!r}")
    return out


def main() -> int:
    found: list[str] = []
    title = os.environ.get("PR_TITLE", "")
    if title:
        found += problems("PR title", title, os.environ.get("PR_BODY", ""))
    base, head = os.environ.get("BASE"), os.environ.get("HEAD")
    if base and head:
        log = subprocess.run(["git", "log", "--format=%H%x1f%s%x1f%b%x1e", f"{base}..{head}"],
                             capture_output=True, text=True, check=True).stdout
        for rec in filter(None, (r.strip("\n") for r in log.split("\x1e"))):
            sha, subject, body = rec.split("\x1f")
            found += problems(f"commit {sha[:7]}", subject, body)
    for f in found:
        print(f"::error::{f}")
    print(f"{len(found)} problem(s)")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
