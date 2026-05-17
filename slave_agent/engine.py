import os
import re
from typing import Dict, Generator, List
from slave_agent.graph import app
from slave_agent.filesystem import write_file, ensure_dir


# ---------------- CLEAN OUTPUT ----------------
def clean_code(text: str) -> str:
    fenced = re.search(r"```[a-zA-Z0-9_-]*\n(.*?)\n```", text, re.S)
    if fenced:
        text = fenced.group(1)

    return text.strip() + "\n"


def infer_single_file_path(filetree: str):
    root_dir = None
    file_name = None

    for line in filetree.splitlines():
        stripped = line.strip()

        if not stripped:
            continue

        if stripped.endswith("/"):
            if root_dir is None:
                root_dir = stripped.rstrip("/")
            continue

        file_name = stripped

    if root_dir and file_name:
        return f"{root_dir}/{file_name}"

    return file_name


def parse_files(blob: str):
    files = {}
    current = None
    buffer = []

    for line in blob.splitlines():
        if line.startswith("=== FILE:"):
            current = line.split("=== FILE:")[1].replace("===", "").strip()
            buffer = []

        elif line.startswith("=== END FILE"):
            if current:
                files[current] = clean_code("\n".join(buffer))
            current = None

        elif current:
            buffer.append(line)

    return files


def _write_generated_files(output_dir: str, blob: str, filetree: str = "") -> List[str]:
    files = parse_files(blob)

    if not files:
        fallback_path = infer_single_file_path(filetree)

        if fallback_path:
            files = {fallback_path: clean_code(blob)}

    # If all files share a single top-level directory (e.g. "project/")
    # and the caller asked to write to the current working directory,
    # strip that top-level prefix so files are created directly in root.
    if files:
        top_dirs = {p.split('/')[0] for p in files.keys() if '/' in p}
        cwd = os.path.abspath('.')
        if len(top_dirs) == 1 and output_dir == cwd:
            prefix = next(iter(top_dirs))
            new_files = {}
            for p, content in files.items():
                if p.startswith(prefix + '/'):
                    new_p = p[len(prefix) + 1 :]
                else:
                    new_p = p
                new_files[new_p] = content
            files = new_files

    for path, content in files.items():
        write_file(output_dir, path, content)

    return list(files.keys())


def stream_task(task: str, stack: str, output_root=".") -> Generator[Dict, None, None]:
    # write generated files directly into the given output_root (project root by default)
    output_dir = os.path.abspath(output_root)
    ensure_dir(output_dir)

    state = {
        "task": task,
        "stack": stack,
        "plan": "",
        "filetree": "",
        "files_blob": "",
        "review": "",
        "iterations": 0,
        "next": ""
    }

    yield {
        "stage": "start",
        "message": "Starting build",
        "output_dir": output_dir
    }

    written_files: List[str] = []

    for update in app.stream(state, stream_mode="updates"):
        for node_name, node_update in update.items():
            if node_name == "planner" and node_update.get("plan"):
                state["plan"] = node_update["plan"]
                yield {
                    "stage": "planner",
                    "message": "Plan generated",
                    "plan": state["plan"]
                }

            elif node_name == "scaffolder" and node_update.get("filetree"):
                state["filetree"] = node_update["filetree"]
                yield {
                    "stage": "scaffolder",
                    "message": "File tree generated",
                    "filetree": state["filetree"]
                }

            elif node_name == "writer" and node_update.get("files_blob"):
                state["files_blob"] = node_update["files_blob"]
                written_files = _write_generated_files(output_dir, state["files_blob"], state["filetree"])
                yield {
                    "stage": "writer",
                    "message": "Files written",
                    "files": written_files
                }

            elif node_name == "critic" and node_update.get("review"):
                state["review"] = node_update["review"]
                yield {
                    "stage": "critic",
                    "message": "Review completed",
                    "review": state["review"]
                }

    yield {
        "stage": "done",
        "message": "Build complete",
        "plan": state.get("plan", ""),
        "filetree": state.get("filetree", ""),
        "review": state.get("review", ""),
        "output_dir": output_dir,
        "files": written_files
    }


# ---------------- CORE ENGINE ----------------
def run_task(task: str, stack: str, output_root="."):
    final_result = None

    for event in stream_task(task, stack, output_root=output_root):
        final_result = event

    return {
        "plan": final_result.get("plan", "") if final_result else "",
        "filetree": final_result.get("filetree", "") if final_result else "",
        "review": final_result.get("review", "") if final_result else "",
        "output_dir": final_result.get("output_dir", "") if final_result else "",
        "files": final_result.get("files", []) if final_result else []
    }