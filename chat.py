"""Terminal chatbot with conversation memory.

Run:  python chat.py
Commands:  /new  start a fresh conversation
           exit  quit
"""

from ollama import chat

from chatbot_core import (MODEL, format_stats, new_conversation_name,
                          save_conversation, stream_chat)

EXIT_COMMANDS = ("exit", "quit")
NEW_COMMAND = "/new"

def read_user_input():
    try:
        user_input = input("You: ").strip()
    except (KeyboardInterrupt, EOFError):   # Ctrl+C / Ctrl+Z
        return None
    if user_input.lower() in EXIT_COMMANDS:
        return None
    return user_input

def stream_answer(history):
    print("Bot: ", end="", flush=True)
    answer = ""
    last_chunk = None
    for chunk in stream_chat(history):
        text = chunk.message.content
        print(text, end="", flush=True)   # flush: show text immediately
        answer += text
        if chunk.done:
            last_chunk = chunk
    print()   # end the streamed line
    return answer, last_chunk

def print_stats(last_chunk):
    stats = format_stats(last_chunk)
    if stats:
        print(f"[{stats}]")
    print()

def ask_bot(history, conversation):
    """Get the bot's reply to the last user message, then save the conversation."""
    try:
        answer, last_chunk = stream_answer(history)
    except Exception as e:
        print(f"\n[Error: {e}]\n")
        history.pop()   # drop the question that got no answer
        return
    print_stats(last_chunk)
    history.append({"role": "assistant", "content": answer})
    save_conversation(conversation, history)

def main():
    history = []
    conversation = new_conversation_name()
    print(f"Chat with {MODEL}. Type {NEW_COMMAND} for a new conversation, 'exit' to quit.\n")

    while (user_input := read_user_input()) is not None:
            if user_input == NEW_COMMAND:
                history = []
                conversation = new_conversation_name()
                print("[Started a new conversation]\n")
            elif user_input:
                history.append({"role": "user", "content": user_input})
                ask_bot(history, conversation)

    print("Goodbye!")

if __name__ == "__main__":
    main()