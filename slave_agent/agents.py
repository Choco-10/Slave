import ollama

PLANNER_MODEL = "qwen2.5:7b"
SCAFFOLD_MODEL = "qwen2.5:7b"
WRITER_MODEL = "deepseek-coder:6.7b"
CRITIC_MODEL = "qwen2.5:7b"


def planner(state):
    res = ollama.chat(
        model=PLANNER_MODEL,
        messages=[{
            "role": "user",
            "content": f"""
Task: {state['task']}
Target: {state['stack']}

Return a short step-by-step plan only.
"""
        }]
    )
    return {"plan": res["message"]["content"]}


def scaffolder(state):
    res = ollama.chat(
        model=SCAFFOLD_MODEL,
        messages=[{
            "role": "user",
            "content": f"""
Task: {state['task']}
Target: {state['stack']}
Plan:
{state['plan']}

Output ONLY file tree. No explanation.

Example:
workspace/
    file_one.ext
    file_two.ext
"""
        }]
    )
    return {"filetree": res["message"]["content"]}


def writer(state):
    res = ollama.chat(
        model=WRITER_MODEL,
        messages=[{
            "role": "user",
            "content": f"""
Task: {state['task']}
Target: {state['stack']}

File tree:
{state['filetree']}

RULES:
- NO markdown
- NO ``` blocks
- NO language tags
- Output EXACT format:

=== FILE: path ===
content
=== END FILE ===
"""
        }]
    )
    return {"files_blob": res["message"]["content"]}


def critic(state):
    res = ollama.chat(
        model=CRITIC_MODEL,
        messages=[{
            "role": "user",
            "content": f"""
Task: {state['task']}
Target: {state['stack']}

File tree:
{state['filetree']}

Check completeness of generated code.

Return ONLY:
OK
or
FIX
"""
        }]
    )

    return {
        "review": res["message"]["content"].strip().upper()
    }