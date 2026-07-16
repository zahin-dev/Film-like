#!/usr/bin/env python3
"""Report reproducible physical line counts for Film-like source files.

A physical line is any line returned by Python's UTF-8 ``splitlines()``
handling, including blank and comment-only lines. Totals are calculated from
the current checkout and are never embedded in this script.
"""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
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
FRONTEND_SOURCE_SUFFIXES = {
    ".css",
    ".html",
    ".js",
    ".jsx",
    ".less",
    ".sass",
    ".scss",
    ".svg",
    ".ts",
    ".tsx",
}


def _source_files(base: Path, suffixes: set[str]) -> list[Path]:
    """Return sorted source files while excluding generated/cache trees."""
    return sorted(
        path
        for path in base.rglob("*")
        if path.is_file()
        and path.suffix.casefold() in suffixes
        and not any(part.casefold() in EXCLUDED_PARTS for part in path.parts)
    )


def _physical_lines(paths: list[Path]) -> int:
    """Count physical UTF-8 lines, including blanks and comments."""
    return sum(
        len(path.read_text(encoding="utf-8").splitlines())
        for path in paths
    )


def _format_metric(label: str, paths: list[Path]) -> str:
    return f"{label:<34} {len(paths):>4} files  {_physical_lines(paths):>7} lines"


def main() -> int:
    backend_app = _source_files(ROOT / "backend" / "app", {".py"})
    backend_tests = _source_files(ROOT / "backend" / "tests", {".py"})
    migrations = _source_files(
        ROOT / "backend" / "alembic" / "versions", {".py"}
    )
    backend_total = _source_files(ROOT / "backend", {".py"})
    frontend_source = _source_files(
        ROOT / "frontend" / "src", FRONTEND_SOURCE_SUFFIXES
    )

    print("Film-like project metrics")
    print("Method: physical UTF-8 lines, including blank and comment-only lines")
    print(_format_metric("backend/app Python", backend_app))
    print(_format_metric("backend/tests Python", backend_tests))
    print(_format_metric("migration Python", migrations))
    print(_format_metric("total backend Python", backend_total))
    print(_format_metric("frontend/src source", frontend_source))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
