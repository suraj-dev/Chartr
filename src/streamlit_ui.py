import os
import sys
# Ensure project root is on PYTHONPATH so that `src` is importable
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import streamlit as st
from src.workflow import run_workflow

st.set_page_config(page_title="Chartr Chat", layout="wide")
st.title("🗨️ Chartr: NL → SQL → Chart")

if "history" not in st.session_state:
    st.session_state.history = []


# Chat‐style input
user_input = st.chat_input("Ask me a question about your data…")

# Render the chat messages on app rerun
for role, content in st.session_state.history:
    if role == "user":
        st.chat_message("user").write(content)
    else:
        st.chat_message("assistant").plotly_chart(content, use_container_width=True)

if user_input:
    with st.chat_message("user"):
        st.write(user_input)
        st.session_state.history.append(("user", user_input))
    with st.spinner("Fetching your results…"):
        # This will execute convert → SQL → exec → recommend → visualize
        chart = run_workflow(user_input)
        st.chat_message("assistant").plotly_chart(chart, use_container_width=True)
        st.session_state.history.append(("assistant", chart))
