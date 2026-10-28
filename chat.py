from ollama import chat

MODEL = "llama3.2"
OPTIONS = {"num_ctx": 8192, "num_predict": 500}   # context window and response limit
MAX_MESSAGES = 20                                   # how many last messages we keep

SYSTEM_PROMPT = """You are a patient Python tutor.
Please reply in English, brief answer (max. 3 sentences).
When showing code, add a brief explanation.
If a question is not about programming, steer poitely the discussion back on topic."""

def build_messages(history):
    """System prompt prepended to every call."""
    return [{"role": "system", "content": SYSTEM_PROMPT}] + history

def trim_history(history):
    """Sliding window: last MAX_MESSAGES messages, starting with 'user'."""
    if len(history) <= MAX_MESSAGES:
        return history
    trimmed = history[-MAX_MESSAGES:]
    while trimmed and trimmed[0]["role"] != "user":
        trimmed = trimmed[1:]
    return trimmed

history = []
history = trim_history(history)

while True:
    user_input = input("Ty: ").strip()
    if user_input.lower() in ("exit", "quit"):
        break
    if not user_input:
        continue

    history.append({"role": "user", "content": user_input})

    response = chat(
        model=MODEL,
        messages=build_messages(history),
        options=OPTIONS
    )

    answer = response.message.content

    print("Bot: ", end="", flush=True)
    answer = ""

    for chunk in chat(model=MODEL, messages=build_messages(history), stream=True):
        text =chunk.message.content
        print(text, end="", flush=True)
        answer += text
        if chunk.done: # stats
            last_stats = chunk
        
    print("\n")
    history.append({"role": "assistant", "content": answer})
