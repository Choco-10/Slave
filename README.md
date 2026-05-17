# lave

`slave` is a local code-generation CLI that turns natural language tasks into project files using an agent workflow.

## What It Does

- Accepts a task like "create one file with a hello world program"
- Runs a multi-step graph: planner -> scaffolder -> writer -> critic
- Writes generated files to disk

## Project Structure

- `server/`: CLI entry point
- `slave_agent/`: generation workflow and file-writing logic
- `pyproject.toml`: package metadata and console script definition

## Requirements

- Python 3.10+
- [Ollama](https://ollama.com/) running locally
- Required local models (default in code):
  - `qwen2.5:7b`
  - `deepseek-coder:6.7b`

Pull models (example):

```powershell
ollama pull qwen2.5:7b
ollama pull deepseek-coder:6.7b
```

## Install

### Option 1: pipx (recommended for CLI usage)

`pipx` installs `slave` in an isolated environment automatically, so this option keeps your system Python clean.

```powershell
# run from the repository root
py -m pipx install --force .
```

### Option 2: editable install in an already active environment

```powershell
py -m pip install -e .
```

## Usage

### CLI

Generate from prompt:

```powershell
slave create one file containing a hello world program
```

With explicit language hints:

```powershell
slave --stack python create a script that renames files in a folder
```

`--stack` is passed to the model as a programming-language hint (free-form). Common examples:

- `python`
- `javascript`
- `typescript`
- `go`
- `rust`
- `java`
- `cpp`
- `bash`
- `sql`
- `auto` to let the model choose based on the task

Example:

```powershell
slave --stack typescript create a command-line todo manager
```

Choose output root explicitly:

```powershell
slave create a small command-line utility --output-root .\output
```

## Notes

- By default, generated files are written to the current directory unless `--output-root` is provided.
- The manager loop has a bounded retry iteration count (`MAX_ITER`) in `slave_agent/graph.py`.
