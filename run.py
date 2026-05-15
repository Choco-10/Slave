from graph import app


def run(task, language):
    result = app.invoke({
        "task": task,
        "language": language,
        "plan": "",
        "code": "",
        "review": ""
    })

    print("\n===== FINAL CODE =====\n")
    print(result["code"])

    print("\n===== REVIEW =====\n")
    print(result["review"])


if __name__ == "__main__":
    run(
        task="Build a REST API for a todo app",
        language="Go"
    )