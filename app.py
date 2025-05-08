import streamlit as st
import asyncio
from agent import run_agent

st.set_page_config(page_title="RAG Agent", page_icon="📄")
st.title("📄 Chat with Federal Register Agent")

if st.button("🧹 Clear chat"):
    st.session_state.history = []

if "history" not in st.session_state:
    st.session_state.history = []

user_input = st.chat_input("Ask something about federal documents...")

if user_input:
    st.session_state.history.append({"role": "user", "content": user_input})

    with st.spinner("Thinking..."):
        response = asyncio.run(run_agent(user_input))
        st.session_state.history.append({"role": "assistant", "content": response})

# Always show full history
for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
