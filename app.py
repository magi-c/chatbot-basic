from pathlib import Path

import streamlit as st

from chatbot_core import (MODEL, format_stats, list_conversations,
                          load_conversation, new_conversation_name,
                          save_conversation, stream_chat)

st.set_page_config(page_title="Local Chatbot", page_icon="💬")

# --- Glass styling ----------------------------------------------------------
CSS_FILE = Path(__file__).parent / "styles.css"
st.markdown(f"<style>{CSS_FILE.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)
st.title("My local chatbot")

# session_state will persist across script restarts by Streamlit
if "history" not in st.session_state:
    st.session_state.history = []
    st.session_state.conversation = new_conversation_name()

# --- Sidebar: conversations -------------------------------------------------
with st.sidebar:
    st.header("Conversations")

    if st.button("New chat", use_container_width=True):
        st.session_state.history = []
        st.session_state.conversation = new_conversation_name()
        st.session_state.picker = None   # reset the selectbox below
        st.rerun()

    saved = list_conversations()
    if saved:
        choice = st.selectbox("Open a saved conversation", saved, index=None,
                              placeholder="Choose...", key="picker")
        if choice and choice != st.session_state.conversation:
            st.session_state.history = load_conversation(choice)
            st.session_state.conversation = choice
            st.rerun()

    st.divider()
    st.caption(f"Model: {MODEL}")
    st.caption(f"Current conversation: {st.session_state.conversation}")

# --- Conversation so far ----------------------------------------------------
for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- New message ------------------------------------------------------------
if prompt := st.chat_input("Type your message"):
    st.session_state.history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # stream the response
    with st.chat_message("assistant"):
        stats = {}

        def generate():
            for chunk in stream_chat(st.session_state.history):
                if chunk.done:
                    stats["last"] = chunk
                yield chunk.message.content

        try:
            answer = st.write_stream(generate())
        except Exception as e:
            st.error(f"Could not reach the model: {e}")
            st.session_state.history.pop()   # drop the unanswered question
            st.stop()

        stats_text = format_stats(stats.get("last"))
        if stats_text:
            st.caption(stats_text)

    st.session_state.history.append({"role": "assistant", "content": answer})
    save_conversation(st.session_state.conversation, st.session_state.history)
