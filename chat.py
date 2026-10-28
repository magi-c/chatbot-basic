"""Terminal chatbot with conversation memory.

Run:  python chat.py
Commands:  /new  start a fresh conversation
           exit  quit
"""

from ollama import chat

from chatbot_core import (MODEL, OPTIONS, build_messages, format_stats, new_conversation_name,
                          save_conversation, stream_chat)

def main():
    history = []
    conversation = new_conversation_name()
    print(f"Chat with {MODEL}. Type '/new' for a new conversation, 'exit' to quit.\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):   # Ctrl+C / Ctrl+Z
            break
        if user_input.lower() in ("exit", "quit"):
            break
        if user_input.lower() == "/new":
            history = []
            conversation = new_conversation_name()
            print(f"\nNew conversation: {conversation}\n")
        if not user_input:
            continue

        history.append({"role": "user", "content": user_input})

        print("Bot: ", end="", flush=True)
        answer = ""
        last_chunk = None
        try:
            for chunk in stream_chat(history):
                text =chunk.message.content
                print(text, end="", flush=True)
                answer += text
                if chunk.done: # stats
                    last_chunk = chunk
        except Exception as e:
            print(f"\n[Error: {e}]\n")
            history.pop()   # remove the question that got no answer
            continue

        print()
        stats = format_stats(last_chunk)
        if stats:
            print(f"[{stats}]\n")
        print()

        history.append({"role": "assistant", "content": answer})
        save_conversation(conversation, history)

    print("Goodbye!")

if __name__ == "__main__":
    main()