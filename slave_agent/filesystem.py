import os


def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def safe_join(base_dir: str, user_path: str) -> str:
    base_dir = os.path.abspath(base_dir)
    user_path = user_path.lstrip("/\\")
    full = os.path.abspath(os.path.join(base_dir, user_path))

    if not full.startswith(base_dir):
        raise ValueError(f"Blocked unsafe path: {user_path}")

    return full


def write_file(base_dir: str, relative_path: str, content: str):
    path = safe_join(base_dir, relative_path)

    ensure_dir(os.path.dirname(path))

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)