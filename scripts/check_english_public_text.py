#!/usr/bin/env python3
"""Reject Japanese characters in public docs and source comments/docstrings."""

import ast
import io
from pathlib import Path
import re
import subprocess
import tokenize
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
JAPANESE_CHARACTER = re.compile(
    r"[\u3040-\u309f\u30a0-\u30ff\u31f0-\u31ff\uff65-\uff9f"
    r"\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]"
)
URL = re.compile(r"(?:https?|mailto):[^\s)>]+", re.IGNORECASE)
MARKDOWN_SUFFIXES = {".md", ".markdown"}
PYTHON_SUFFIXES = {".py"}
C_STYLE_SUFFIXES = {
    ".css",
    ".js",
    ".jsx",
    ".less",
    ".sass",
    ".scss",
    ".ts",
    ".tsx",
}
EXCLUDED_PARTS = {
    ".git",
    ".pytest_cache",
    "__pycache__",
    "build",
    "coverage",
    "dist",
    "dist-ssr",
    "htmlcov",
    "node_modules",
    "venv",
}


def _candidate_files() -> list[Path]:
    """List tracked and not-ignored public-text candidates in the audit scope."""
    command = [
        "git",
        "-c",
        f"safe.directory={ROOT.as_posix()}",
        "ls-files",
        "--cached",
        "--others",
        "--exclude-standard",
        "--",
        "README.md",
        "docs",
        "backend/app",
        "frontend/src",
    ]
    result = subprocess.run(
        command,
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        raise RuntimeError(f"Could not list public source files: {result.stderr.strip()}")

    supported = MARKDOWN_SUFFIXES | PYTHON_SUFFIXES | C_STYLE_SUFFIXES
    return sorted(
        ROOT / relative
        for relative in result.stdout.splitlines()
        if (ROOT / relative).is_file()
        and (ROOT / relative).suffix.casefold() in supported
        and not any(
            part.casefold() in EXCLUDED_PARTS
            for part in Path(relative).parts
        )
    )


def _contains_japanese(text: str) -> bool:
    return JAPANESE_CHARACTER.search(URL.sub("", text)) is not None


def _markdown_fragments(text: str) -> Iterable[tuple[int, str]]:
    for line_number, line in enumerate(text.splitlines(), start=1):
        yield line_number, line


def _python_fragments(text: str) -> Iterable[tuple[int, str]]:
    """Yield only Python comments and recognized module/class/function docstrings."""
    reader = io.StringIO(text).readline
    for token in tokenize.generate_tokens(reader):
        if token.type == tokenize.COMMENT:
            yield token.start[0], token.string

    tree = ast.parse(text)
    lines = text.splitlines()
    documented_nodes = (
        ast.AsyncFunctionDef,
        ast.ClassDef,
        ast.FunctionDef,
        ast.Module,
    )
    for node in ast.walk(tree):
        if not isinstance(node, documented_nodes):
            continue
        body = getattr(node, "body", None)
        if not body or not isinstance(body, list):
            continue
        first = body[0]
        if not (
            isinstance(first, ast.Expr)
            and isinstance(first.value, ast.Constant)
            and isinstance(first.value.value, str)
        ):
            continue
        start = first.value.lineno
        end = first.value.end_lineno or start
        for line_number in range(start, end + 1):
            yield line_number, lines[line_number - 1]


def _c_style_fragments(text: str) -> Iterable[tuple[int, str]]:
    """Yield // and /* */ comments while skipping quoted source strings."""
    in_block = False
    quote: str | None = None
    escaped = False

    for line_number, line in enumerate(text.splitlines(), start=1):
        index = 0
        while index < len(line):
            if in_block:
                end = line.find("*/", index)
                if end == -1:
                    yield line_number, line[index:]
                    index = len(line)
                else:
                    yield line_number, line[index:end]
                    in_block = False
                    index = end + 2
                continue

            character = line[index]
            if quote is not None:
                if escaped:
                    escaped = False
                elif character == "\\":
                    escaped = True
                elif character == quote:
                    quote = None
                index += 1
                continue

            if line.startswith("//", index):
                yield line_number, line[index:]
                break
            if line.startswith("/*", index):
                in_block = True
                index += 2
                continue
            if character in {"'", '"', "`"}:
                quote = character
                escaped = False
            index += 1

        if quote in {"'", '"'}:
            quote = None
            escaped = False


def _fragments(path: Path, text: str) -> Iterable[tuple[int, str]]:
    suffix = path.suffix.casefold()
    if suffix in MARKDOWN_SUFFIXES:
        return _markdown_fragments(text)
    if suffix in PYTHON_SUFFIXES:
        return _python_fragments(text)
    return _c_style_fragments(text)


def main() -> int:
    violations: set[tuple[str, int, str]] = set()
    for path in _candidate_files():
        text = path.read_text(encoding="utf-8")
        relative = path.relative_to(ROOT).as_posix()
        for line_number, fragment in _fragments(path, text):
            if _contains_japanese(fragment):
                source_line = text.splitlines()[line_number - 1].strip()
                violations.add((relative, line_number, source_line))

    if violations:
        print("Japanese public-text characters found:")
        for relative, line_number, source_line in sorted(violations):
            print(f"{relative}:{line_number}: {source_line}")
        print(f"English public-text audit failed: {len(violations)} violation(s).")
        return 1

    print(
        "English public-text audit passed: no Hiragana, Katakana, or CJK "
        "characters found in public Markdown or source comments/docstrings."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
