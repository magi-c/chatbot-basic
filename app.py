import streamlit as st
from ollama import chat

MODEL = "llama3.2"
SYSTEM_PROMPT = "You are a helpful assistant."
OPTIONS = {"num_ctx": 8192, "num_predict": 1000}

st.title("My local chatbot")

# session_state will persist across script restarts by Streamlit
if "history" not in st.session_state:
    st.session_state.history = []

with st.sidebar:
    if st.button("New chat"):
        st.session_state.history = []
        st.rerun()

for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Type your message"):
    st.session_state.history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # build messages with system prompt and history
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state.history[-21:]

    # stream the response
    with st.chat_message("assistant"):
        def generate():
            for chunk in chat(model=MODEL, messages=messages, options=OPTIONS, stream=True):
                yield chunk.message.content
        answer = st.write_stream(generate())
    
    st.session_state.history.append({"role": "assistant", "content": answer})
               