
import streamlit as st

st.markdown("### Chat with The Task Force Data Hub Catalog")
st.markdown("""Pose a question related to California Landscape Metrics. 
               Search The Task Force Data Hub Catalog to find the desired datasets.
            """)

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "Ask me about available raster datasets! I can help you find and visualize spatial data."
    }]
