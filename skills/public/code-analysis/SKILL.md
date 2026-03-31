---
name: code-analysis
description: Use this skill when the user asks to analyze, review, or understand any code project or repository. Triggers on phrases like "analyze this project", "analyze the codebase", "code review", "project structure analysis", "分析本项目", "分析代码", "代码分析", "项目分析". Produces a comprehensive structured report covering architecture, language distribution, code metrics, dependencies, and actionable insights.
---

# Code Analysis Skill

## Overview

This skill performs a comprehensive analysis of a code project or repository, producing a structured report that covers:

1. **Project Structure** — Directory tree, file organization, and module layout
2. **Language Distribution** — File counts and line counts per language
3. **Code Metrics** — Total lines of code, comment density, file sizes
4. **Dependencies** — Key dependency files (requirements.txt, package.json, go.mod, etc.)
5. **Documentation** — README quality, inline comments, docstrings
6. **Key Findings** — TODOs, FIXMEs, anti-patterns, and improvement opportunities
7. **Architectural Summary** — High-level architecture and component relationships

## When to Use This Skill

**Always load this skill when:**

- User asks to "analyze this project", "review the codebase", "understand the code structure"
- User says "分析本项目", "分析代码库", "代码分析", "项目分析"
- User wants a summary or overview of a repository's architecture
- User asks "how is this project organized?" or "what does this codebase do?"
- User wants to understand dependencies, tech stack, or code quality

## Workflow

### Step 1: Identify the Project Path

Determine the root path of the project to analyze:
- If user references "this project" or "本项目", use the current working project directory
- If user provides a path, use that path
- For DeerFlow itself, the project root is typically `/home/runner/work/deer-flow/deer-flow` or the mounted workspace

### Step 2: Run the Analysis Script

Use the `analyze_project.py` script to collect metrics:

```bash
python /mnt/skills/public/code-analysis/scripts/analyze_project.py \
  --path /path/to/project \
  --output /mnt/user-data/outputs/project-analysis.json
```

#### Available options:

| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| `--path` | Yes | — | Root path of the project to analyze |
| `--output` | No | stdout | Path to write JSON results |
| `--max-depth` | No | 6 | Maximum directory traversal depth |
| `--exclude` | No | (built-in list) | Comma-separated patterns to exclude |
| `--top-files` | No | 10 | Number of largest files to report |

The script outputs a JSON document containing all collected metrics.

### Step 3: Supplement with Direct Code Reading

After running the script, read key files for deeper understanding:

1. **README** — `read_file()` on README.md/README.rst for project purpose
2. **Entry points** — Main scripts, `__init__.py`, `index.ts`, `main.py`, `app.py`
3. **Config files** — `pyproject.toml`, `package.json`, `Makefile`, `Dockerfile`
4. **Architecture docs** — Any `ARCHITECTURE.md`, `DESIGN.md`, or `docs/` files

### Step 4: Generate the Report

Produce a comprehensive Markdown report following the structure below.

---

## Report Structure

### 1. Executive Summary
- Project name and description (1-2 sentences)
- Primary language and tech stack
- Scale: total files, total lines of code, number of contributors (if determinable)
- One-paragraph assessment of the codebase quality and purpose

### 2. Project Structure
- Annotated directory tree (top 2-3 levels)
- Description of each major directory's responsibility
- Entry points and main modules

### 3. Technology Stack
- Languages used with percentages
- Key frameworks and libraries
- Build tools, package managers, CI/CD setup

### 4. Architecture Overview
- High-level component diagram (use Mermaid if helpful)
- Data flow between components
- Key design patterns identified

### 5. Code Metrics
- Total lines of code (LOC) excluding blanks and comments
- Comment ratio (comments / total lines)
- Largest files (potential complexity hotspots)
- Dependency count

### 6. Dependencies Analysis
- Direct dependencies list (from manifest files)
- Outdated or notable dependencies
- Security considerations if visible

### 7. Documentation Quality
- README completeness (setup, usage, contributing sections)
- Inline comment density
- API documentation presence

### 8. Key Findings & Recommendations
- Strengths of the codebase
- Areas for improvement (TODOs, FIXMEs, missing tests, etc.)
- Specific actionable recommendations

---

## Output Language

Match the report language to the user's request language:
- If user wrote in Chinese (分析本项目), write the report in **Chinese**
- If user wrote in English, write the report in **English**

---

## Example Usage

**User**: 分析本项目

**Agent actions**:
1. Load this skill
2. Identify project path (e.g., current workspace or DeerFlow root)
3. Run `analyze_project.py --path /project/root --output /mnt/user-data/outputs/analysis.json`
4. Read README.md, key config files, and main entry points
5. Generate comprehensive report in Chinese

**User**: Analyze the codebase at /workspace/my-app

**Agent actions**:
1. Load this skill
2. Run `analyze_project.py --path /workspace/my-app --output /mnt/user-data/outputs/analysis.json`
3. Read README.md and key source files
4. Generate comprehensive report in English
