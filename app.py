
import json
import requests
import streamlit as st
from openai import OpenAI

client = OpenAI(api_key=st.secrets["OpenAI_KEY"])

def generate_gpt_response(query, context):
    system_prompt = f"""You're a data assistant of the Task Force Data Hub.
    The following is the datasets in our CKAN Catalog:
    {context}

    In these datasets, if there are datasets that are relevant to the user's query, 
    return titles for all relevant datasets. if there are no relevant ones, then 
    you are free to answer.
    
    Always respond in Markdown
    """
    
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
    # st.code(json.dumps(datasets, indent=4))

    context = ""
    for dataset in datasets:
        context += f"""
                   Title: {dataset['title']}
                   Description: {dataset['notes']}
                   ID: {dataset['id']}
                   
                   """
    # st.markdown(context)
        
    with st.spinner("Thinking ..."):
        llm_response = generate_gpt_response(prompt, context)    
        st.session_state.messages.append({"role": "assistant", "content": llm_response})
        st.chat_message("assistant").write(llm_response)












