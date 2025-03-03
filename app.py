
import streamlit as st

st.markdown("### Chat with The Task Force Data Hub Catalog")

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []


# Chat interface
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])


