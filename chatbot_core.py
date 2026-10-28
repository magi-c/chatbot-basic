"""Shared logic for the terminal (chat.py) and web (app.py) chatbots.

The model itself has no memory. "Memory" is the conversation history that we
send with every request, so most of this module is about managing that list.
"""
import json
from datetime import datetime
from pathlib import Path

from ollama import chat

# --- Configuration --------------------------------------------------------
MODEL = "llama3.2"
OPTIONS = {
    "num_ctx": 8192,      # context window in tokens (input + answer must fit)
    "num_predict": 1000,  # max length of a single answer
}
MAX_MESSAGES = 20         # how many recent messages are sent to the model
HISTORY_DIR = Path(__file__).parent / "history"

SYSTEM_PROMPT = """You are a patient Python tutor for beginners.
Answer in English, briefly (max. 5 sentences).
When you show code, add one sentence explaining it.
If the question is not about programming, politely steer back to the topic."""


# --- Building the request -------------------------------------------------
def trim_history(history, max_messages=MAX_MESSAGES):
    """Sliding window: keep the last `max_messages` messages,
    making sure the list starts with a user message."""
    if len(history) <= max_messages:
        return history
    trimmed = history[-max_messages:]
    while trimmed and trimmed[0]["role"] != "user":
        trimmed = trimmed[1:]
    return trimmed


def build_messages(history, system_prompt=SYSTEM_PROMPT):
    """Prepend the system prompt on every call, so trimming never removes it."""
    return [{"role": "system", "content": system_prompt}] + trim_history(history)


def stream_chat(history, model=MODEL, options=OPTIONS):
    """Send the conversation to Ollama and yield response chunks as they arrive.
    The last chunk has `done == True` and carries token statistics."""
    return chat(model=model, messages=build_messages(history),
                options=options, stream=True)


def format_stats(chunk):
    """Human-readable token stats from the final chunk, or None if unavailable."""
    if chunk and chunk.eval_count and chunk.eval_duration:
        tokens_per_sec = chunk.eval_count / chunk.eval_duration * 1e9
        return (f"input: {chunk.prompt_eval_count} tokens | "
                f"output: {chunk.eval_count} tokens | {tokens_per_sec:.1f} tokens/s")
    return None


# --- Saving conversations -------------------------------------------------
def new_conversation_name():
    """Timestamp-based name, e.g. 2026-10-28_12-55-03."""
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def save_conversation(name, history):
    HISTORY_DIR.mkdir(exist_ok=True)
    path = HISTORY_DIR / f"{name}.json"
    path.write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")


def load_conversation(name):
    path = HISTORY_DIR / f"{name}.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return []


def list_conversations():
    """Names of saved conversations, newest first."""
    if not HISTORY_DIR.exists():
        return []
    return sorted((p.stem for p in HISTORY_DIR.glob("*.json")), reverse=True)
