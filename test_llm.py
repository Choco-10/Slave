import ollama

response = ollama.chat(
    model="qwen2.5:7b",
    messages=[
        {"role": "user", "content": "Write a Python function to add two numbers"}
    ]
)

print(response["message"]["content"])