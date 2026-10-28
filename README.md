# Chatbot with Conversation Memory

A local chatbot that remembers the conversation, streams answers word by word,
and saves chats to disk. It runs entirely on local machine with
[Ollama](https://ollama.com): no API keys, no costs.

It comes in two versions sharing the same logic:

- **`chat.py`**: a chat in the terminal
- **`app.py`**: a web UI built with Streamlit

## Requirements

- Python 3.10+
- Ollama, with the `llama3.2` model (~2 GB; runs on 8 GB RAM, no GPU needed)

## Setup (Windows, PowerShell)

```powershell
# 1. Download the model (Ollama must be installed and running)
ollama pull llama3.2

# 2. Create and activate a virtual environment
cd C:\priv\nauka\python-nauka\chatbot-memory
python -m venv .venv
.venv\Scripts\activate

# 3. Install the dependencies
pip install -r requirements.txt
```

On macOS/Linux, activate with `source .venv/bin/activate`.

## Running

```powershell
python hello.py                   # quick check that Ollama answers
python chat.py                    # terminal chat
python -m streamlit run app.py    # web UI at http://localhost:8501
```

In the terminal chat, type `/new` to start a new conversation and `exit` to quit.
In the web UI, use the sidebar to start a new conversation or reopen a saved one.

## Project structure

| File | Purpose |
| --- | --- |
| `chatbot_core.py` | Shared logic: history trimming, system prompt, streaming, saving |
| `hello.py` | Minimal single-question test of the Ollama connection |
| `chat.py` | Terminal chatbot |
| `app.py` | Streamlit web chatbot |
| `history/` | Saved conversations as JSON (created automatically, git-ignored) |

## Design decisions

- **Sliding window of 20 messages.** Older messages are dropped so requests stay
  fast and within the context window. The full history is still shown and saved.
- **`num_ctx = 8192`.** Ollama's default context window is small, and when it
  overflows Ollama silently cuts the start of the conversation. 8192 tokens fits
  20 messages plus the system prompt and a 1000-token answer.
- **Streaming.** Text appears as it is generated, which shortens the time to the
  first word (what users perceive as speed).
- **Shared module.** Both interfaces use `chatbot_core.py`, so changing the model
  or prompt happens in one place.
