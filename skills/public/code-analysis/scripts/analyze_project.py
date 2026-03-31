#!/usr/bin/env python3
"""
Code project analysis script for the DeerFlow code-analysis skill.

Walks a project directory and collects metrics including:
- File counts and language distribution
- Lines of code (total, blank, comment)
- Dependency manifests
- TODO/FIXME counts
- Directory structure
- Largest files
"""

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Language detection
# ---------------------------------------------------------------------------

LANGUAGE_MAP: dict[str, str] = {
    ".py": "Python",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".go": "Go",
    ".java": "Java",
    ".kt": "Kotlin",
    ".swift": "Swift",
    ".rs": "Rust",
    ".c": "C",
    ".cpp": "C++",
    ".cc": "C++",
    ".cxx": "C++",
    ".h": "C/C++ Header",
    ".hpp": "C/C++ Header",
    ".cs": "C#",
    ".rb": "Ruby",
    ".php": "PHP",
    ".sh": "Shell",
    ".bash": "Shell",
    ".zsh": "Shell",
    ".fish": "Shell",
    ".html": "HTML",
    ".htm": "HTML",
    ".css": "CSS",
    ".scss": "SCSS",
    ".sass": "SASS",
    ".less": "LESS",
    ".vue": "Vue",
    ".svelte": "Svelte",
    ".json": "JSON",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".toml": "TOML",
    ".ini": "INI",
    ".cfg": "Config",
    ".conf": "Config",
    ".md": "Markdown",
    ".rst": "reStructuredText",
    ".txt": "Text",
    ".sql": "SQL",
    ".graphql": "GraphQL",
    ".gql": "GraphQL",
    ".proto": "Protobuf",
    ".tf": "Terraform",
    ".dockerfile": "Dockerfile",
    ".r": "R",
    ".R": "R",
    ".scala": "Scala",
    ".lua": "Lua",
    ".dart": "Dart",
    ".ex": "Elixir",
    ".exs": "Elixir",
    ".erl": "Erlang",
    ".hrl": "Erlang",
    ".hs": "Haskell",
    ".clj": "Clojure",
    ".groovy": "Groovy",
    ".m": "MATLAB/Objective-C",
    ".xml": "XML",
    ".xsl": "XSL",
}

COMMENT_PATTERNS: dict[str, list[str]] = {
    "Python": ["#"],
    "JavaScript": ["//", "/*"],
    "TypeScript": ["//", "/*"],
    "Go": ["//", "/*"],
    "Java": ["//", "/*"],
    "Kotlin": ["//", "/*"],
    "Swift": ["//", "/*"],
    "Rust": ["//", "/*"],
    "C": ["//", "/*"],
    "C++": ["//", "/*"],
    "C/C++ Header": ["//", "/*"],
    "C#": ["//", "/*"],
    "Ruby": ["#"],
    "PHP": ["//", "#", "/*"],
    "Shell": ["#"],
    "SCSS": ["//", "/*"],
    "CSS": ["/*"],
    "SQL": ["--", "/*"],
    "R": ["#"],
    "Scala": ["//", "/*"],
    "Lua": ["--"],
    "Elixir": ["#"],
    "Erlang": ["%"],
    "Haskell": ["--", "{-"],
}

# ---------------------------------------------------------------------------
# Default exclusion patterns
# ---------------------------------------------------------------------------

DEFAULT_EXCLUDE_PATTERNS: list[str] = [
    ".git",
    ".svn",
    ".hg",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".venv",
    "venv",
    "env",
    ".env",
    "dist",
    "build",
    ".next",
    ".nuxt",
    "out",
    "target",
    ".idea",
    ".vscode",
    "*.egg-info",
    ".DS_Store",
    "coverage",
    ".nyc_output",
    "*.min.js",
    "*.min.css",
    "*.map",
    "*.lock",
    "vendor",
    "site-packages",
    "*.pyc",
    "*.pyo",
    "*.class",
    "*.o",
    "*.a",
    "*.so",
    "*.dylib",
    "*.dll",
    "*.exe",
    "*.bin",
    "*.log",
]

DEPENDENCY_FILES: list[str] = [
    "requirements.txt",
    "requirements-dev.txt",
    "requirements-test.txt",
    "pyproject.toml",
    "setup.py",
    "setup.cfg",
    "Pipfile",
    "package.json",
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "go.mod",
    "go.sum",
    "Cargo.toml",
    "Cargo.lock",
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    "Gemfile",
    "Gemfile.lock",
    "composer.json",
    "composer.lock",
    "mix.exs",
    "rebar.config",
    "stack.yaml",
    "cabal.project",
    "pubspec.yaml",
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def should_exclude(name: str, exclude_patterns: list[str]) -> bool:
    """Return True if the file/dir name matches any exclusion pattern."""
    for pattern in exclude_patterns:
        if pattern.startswith("*"):
            if name.endswith(pattern[1:]):
                return True
        elif name == pattern:
            return True
    return False


def detect_language(filepath: str) -> str:
    """Return the language name for a given file path."""
    path = Path(filepath)
    # Special cases for files without extensions
    basename = path.name.lower()
    if basename == "dockerfile":
        return "Dockerfile"
    if basename in ("makefile", "gnumakefile"):
        return "Makefile"
    if basename in (".gitignore", ".dockerignore"):
        return "Ignore file"
    suffix = path.suffix.lower()
    return LANGUAGE_MAP.get(suffix, "Other")


def count_lines(filepath: str, language: str) -> dict[str, int]:
    """Count total, blank, and comment lines in a file."""
    comment_starters = COMMENT_PATTERNS.get(language, [])
    total = 0
    blank = 0
    comment = 0
    try:
        with open(filepath, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                total += 1
                stripped = line.strip()
                if not stripped:
                    blank += 1
                elif comment_starters and any(
                    stripped.startswith(c) for c in comment_starters
                ):
                    comment += 1
    except (OSError, PermissionError):
        pass
    return {"total": total, "blank": blank, "comment": comment}


def scan_todos(filepath: str) -> int:
    """Count TODO/FIXME/HACK/XXX occurrences in a file."""
    todo_pattern = re.compile(r"\b(TODO|FIXME|HACK|XXX)\b", re.IGNORECASE)
    count = 0
    try:
        with open(filepath, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                count += len(todo_pattern.findall(line))
    except (OSError, PermissionError):
        pass
    return count


def read_dependency_file(filepath: str) -> list[str] | None:
    """Read a dependency file and return a list of dependency strings (up to 50)."""
    try:
        with open(filepath, encoding="utf-8", errors="replace") as fh:
            # Read up to 8KB — sufficient for most dependency manifests while
            # avoiding excessive memory use on unusually large lock files.
            content = fh.read(8192)
        lines = [line.strip() for line in content.splitlines()]
        # Filter out blank lines and pure comments
        deps = [ln for ln in lines if ln and not ln.startswith("#")]
        return deps[:50]
    except (OSError, PermissionError):
        return None


# ---------------------------------------------------------------------------
# Main analysis
# ---------------------------------------------------------------------------


def analyze_project(
    root_path: str,
    max_depth: int = 6,
    exclude_patterns: list[str] | None = None,
    top_files: int = 10,
) -> dict[str, Any]:
    """
    Walk *root_path* and collect comprehensive project metrics.

    Returns a dict with:
    - summary: high-level counts
    - languages: per-language file/line counts
    - directory_tree: nested dict representing the directory structure
    - largest_files: list of (path, lines) sorted descending
    - dependency_files: dict of found dependency files and their content
    - todo_count: total TODO/FIXME occurrences
    - file_type_counts: counts by extension
    """
    if exclude_patterns is None:
        exclude_patterns = DEFAULT_EXCLUDE_PATTERNS

    root = Path(root_path).resolve()
    if not root.exists():
        return {"error": f"Path does not exist: {root_path}"}
    if not root.is_dir():
        return {"error": f"Path is not a directory: {root_path}"}

    # Accumulators
    language_stats: dict[str, dict[str, int]] = defaultdict(
        lambda: {"files": 0, "total": 0, "blank": 0, "comment": 0, "code": 0}
    )
    file_sizes: list[tuple[int, str]] = []  # (line_count, relative_path)
    dependency_files_found: dict[str, list[str] | None] = {}
    total_todos = 0
    total_files = 0
    total_dirs = 0
    directory_tree: dict[str, Any] = {}

    def _build_tree(
        current_dir: Path, tree_node: dict, current_depth: int
    ) -> None:
        nonlocal total_files, total_dirs, total_todos

        if current_depth > max_depth:
            return

        try:
            entries = list(current_dir.iterdir())
            # Sort: directories first (alphabetically), then files (alphabetically)
            entries.sort(key=lambda p: (not p.is_dir(), p.name.lower()))
        except PermissionError:
            return

        for entry in entries:
            if should_exclude(entry.name, exclude_patterns):
                continue

            rel = str(entry.relative_to(root))

            if entry.is_dir():
                total_dirs += 1
                subtree: dict[str, Any] = {}
                tree_node[entry.name + "/"] = subtree
                _build_tree(entry, subtree, current_depth + 1)

            elif entry.is_file():
                total_files += 1
                lang = detect_language(str(entry))
                counts = count_lines(str(entry), lang)

                lang_entry = language_stats[lang]
                lang_entry["files"] += 1
                lang_entry["total"] += counts["total"]
                lang_entry["blank"] += counts["blank"]
                lang_entry["comment"] += counts["comment"]
                lang_entry["code"] += (
                    counts["total"] - counts["blank"] - counts["comment"]
                )

                file_sizes.append((counts["total"], rel))

                # Check for dependency files
                if entry.name in DEPENDENCY_FILES:
                    dependency_files_found[rel] = read_dependency_file(str(entry))

                # Scan for TODOs
                total_todos += scan_todos(str(entry))

                tree_node[entry.name] = counts["total"]

    _build_tree(root, directory_tree, 0)

    # Top N largest files
    file_sizes.sort(reverse=True)
    largest = [{"path": p, "lines": n} for n, p in file_sizes[:top_files]]

    # Sort languages by code lines descending
    sorted_languages = dict(
        sorted(language_stats.items(), key=lambda x: x[1]["code"], reverse=True)
    )

    # Compute totals
    grand_total = sum(v["total"] for v in language_stats.values())
    grand_code = sum(v["code"] for v in language_stats.values())
    grand_blank = sum(v["blank"] for v in language_stats.values())
    grand_comment = sum(v["comment"] for v in language_stats.values())

    # Comment ratio
    comment_ratio = round(grand_comment / grand_total * 100, 1) if grand_total else 0

    summary = {
        "root_path": str(root),
        "total_files": total_files,
        "total_directories": total_dirs,
        "total_lines": grand_total,
        "code_lines": grand_code,
        "blank_lines": grand_blank,
        "comment_lines": grand_comment,
        "comment_ratio_percent": comment_ratio,
        "todo_count": total_todos,
        "dependency_files_found": list(dependency_files_found.keys()),
        "unique_languages": len(language_stats),
    }

    return {
        "summary": summary,
        "languages": sorted_languages,
        "directory_tree": directory_tree,
        "largest_files": largest,
        "dependency_files": dependency_files_found,
        "todo_count": total_todos,
    }


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze a code project and output metrics as JSON.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python analyze_project.py --path /workspace/my-app
  python analyze_project.py --path /workspace/my-app --output /tmp/report.json
  python analyze_project.py --path /workspace/my-app --max-depth 4 --top-files 20
  python analyze_project.py --path /workspace/my-app --exclude ".git,node_modules,dist"
""",
    )
    parser.add_argument(
        "--path",
        required=True,
        help="Root path of the project to analyze",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output file path for JSON results (default: stdout)",
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=6,
        help="Maximum directory traversal depth (default: 6)",
    )
    parser.add_argument(
        "--exclude",
        default=None,
        help="Comma-separated list of directory/file patterns to exclude (replaces defaults)",
    )
    parser.add_argument(
        "--top-files",
        type=int,
        default=10,
        help="Number of largest files to include in report (default: 10)",
    )

    args = parser.parse_args()

    exclude = DEFAULT_EXCLUDE_PATTERNS
    if args.exclude:
        exclude = [p.strip() for p in args.exclude.split(",") if p.strip()]

    result = analyze_project(
        root_path=args.path,
        max_depth=args.max_depth,
        exclude_patterns=exclude,
        top_files=args.top_files,
    )

    output_json = json.dumps(result, indent=2, ensure_ascii=False)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output_json, encoding="utf-8")
        print(f"Analysis written to: {args.output}", file=sys.stderr)
    else:
        print(output_json)


if __name__ == "__main__":
    main()
