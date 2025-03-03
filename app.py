
import json
import requests
import streamlit as st
from openai import OpenAI

client = OpenAI(api_key=st.secrets["OpenAI_KEY"])

def generate_gpt_response(query, context):
    system_prompt = f"""
You are a data assistant for the Task Force Data Hub, helping users find relevant
datasets from our CKAN Catalog based on their queries.

Below are datasets from our CKAN Catalog that may be relevant:
{context}

Instructions:

- Identify and return all relevant dataset titles based on the user's query. Do not 
  limit your response to just one or two datasets—return all that are relevant.

- Consider geographic relevance. If a user queries about a specific location 
  (e.g., Los Angeles), suggest datasets covering that region, even if they do 
  not explicitly mention it. For example, if the user asks for Los Angeles data, 
  datasets covering Southern California may still be relevant.

- Filter out unrelated datasets. If no datasets match the query, provide a clear
  response indicating that no relevant datasets were found.

- Special Handling for Data Collections:
  The collection "California Interagency Treatment Tracking System" contains 
  datasets on vegetation treatments in California. The collection "Boundary Datasets" 
  contains datasets on administrative or management area boundaries. If the user asks 
  for datasets on a specific topic (e.g., wildfires), do not include any datasets in 
  the collection "California Interagency Treatment Tracking System" or the 
  collection "Boundary Datasets".

- Our CKAN Catalog currently contains 201 datasets.

Response Format:
- Use Markdown for better readability.
- Provide dataset titles in a bulleted list with any additional relevant metadata (if applicable).
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
    # st.code(context)
        
    with st.spinner("Thinking ..."):
        llm_response = generate_gpt_response(prompt, context)    
        st.session_state.messages.append({"role": "assistant", "content": llm_response})
        st.chat_message("assistant").write(llm_response)












