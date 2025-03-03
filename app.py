
import json
import requests
import streamlit as st

def generate_gpt_response(query, context):
    system_prompt = f"""You're a data assistant of the Task Force Data Hub.
    The following is the datasets in our CKAN Catalog:
    {context}

    - Use these datasets to answer the user query
    - Always respond in Markdown
    - Be concise but informative"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI service error: {str(e)}"

st.markdown("### Chat with The Task Force Data Hub Catalog")

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Chat interface
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("What can I help you with?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    response = requests.get(f"https://sparcal.sdsc.edu/api/v1/Utility/clm?search_terms={prompt}")
    datasets = json.loads(response.text)
    st.code(json.dumps(datasets, indent=4))

    llm_response = generate_gpt_response(prompt, json.dumps(datasets, indent=4))    
    
    with st.spinner("Thinking ..."):
        st.session_state.messages.append({"role": "assistant", "content": prompt})
        st.chat_message("assistant").write(prompt)












