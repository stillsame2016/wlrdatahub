
import json
import requests
import streamlit as st
from openai import OpenAI

client = OpenAI(api_key=st.secrets["OpenAI_KEY"])

def generate_gpt_response(query, context):
    system_prompt = f"""
You're a data assistant for the Task Force Data Hub.

Below are datasets from our CKAN Catalog relevant to the user's query:
{context}

- Identify and return the titles of all datasets that are relevant to the query.
  Please return all relevant datasets, not just one or two.
- In particular, note that if a user queries for data related to a certain region, 
  e.g., Los Angeles, a dataset covering the Los Angeles region can be returned to 
  the user as a suggestion, even though the Los Angeles dataset is not directly 
  mentioned. For example, data for Southern California.
- If no datasets are relevant, provide an appropriate response instead.
- Do not include datasets from the “Boundary datasets” collection if the user 
  doesn't explicitly ask, as they only contain administrative or management 
  area boundaries, which are not relevant to topic-based queries.
- Our CKAN Catalog currently contains 201 datasets.

Always respond in Markdown.
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
        extras = dataset['extras']
        collection_name = ''
        for extra in extras:
            if extra['key'] == 'collection_name':
                collection_name = extra['value']
        context += f"""       
- ID: {dataset['id']}
- Title: {dataset['title']}
- Collection: {collection_name}
- Description: {dataset['notes']}
                   """
    st.code(context)
        
    with st.spinner("Thinking ..."):
        llm_response = generate_gpt_response(prompt, context)    
        st.session_state.messages.append({"role": "assistant", "content": llm_response})
        st.chat_message("assistant").write(llm_response)












