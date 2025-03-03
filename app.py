
import json
import requests
import streamlit as st
from openai import OpenAI

client = OpenAI(api_key=st.secrets["OpenAI_KEY"])

def generate_gpt_response(query, context):
    system_prompt = f"""
You are a data assistant for the Task Force Data Hub, helping users find relevant
datasets from our CKAN Catalog based on their queries and return your answer in the
JSON format. 

Below are datasets from our CKAN Catalog that may be relevant:
{context}

Instructions:

You must return a JSON object with the following fields:
   - "answer" (string, required): A concise text response. If no dataset is relevant, return this field with an appropriate explanation.
   - "datasets" (list, optional): A list of relevant datasets, where each dataset is represented as an object with the following fields:
        -- "id" (string): The unique identifier of the dataset.
        -- "title" (string): The title of the dataset.
        -- "description" (string): A brief description of the dataset.
    - "additional" (string, optional): A description of further possibilities or additional context, if applicable.
Ensure the response is well-structured and free of unnecessary information. If no datasets are relevant, exclude the "datasets" and "additional" fields and return only the "answer" field.

Identify and return all relevant dataset titles based on the user's query. Do not limit your response to just one or two datasets—return all that are relevant.

Consider geographic relevance. For example, if a user queries "Do you have any datasets for wildfire in San Diego?", you can return datasets related to wildfire in California or Southern California.

Filter out unrelated datasets. If no datasets match the query, provide a clear response indicating that no relevant datasets were found.

All datasets in the collection "California Landscape Metrics" cover California.

- Special Handling for Data Collections:
  The collection "California Interagency Treatment Tracking System" contains 
  datasets on vegetation treatments in California. The collection "Boundary Datasets" 
  contains datasets on administrative or management area boundaries. If the user asks 
  for datasets on a specific topic (e.g., wildfires), do not include any datasets in 
  the collection "California Interagency Treatment Tracking System" or the 
  collection "Boundary Datasets".

- Our CKAN Catalog currently contains 201 datasets.

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
    if msg["role"] == 'user':
        st.chat_message(msg["role"]).write(msg["content"])
    else:
        with st.chat_message("assistant"):
            data = msg["content"]
            st.markdown(f"{data['answer']}\n")
            markdown_text = ""
            if "datasets" in data.keys():
                for dataset in data["datasets"]:
                    markdown_text += f"- **{dataset['title']}**\n\n{dataset['description']}\n"
                st.markdown(markdown_text)
            if "additional" in data.keys():
                st.markdown(f"{data['additional']}\n")

if prompt := st.chat_input("What can I help you with?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Searching ..."):
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
                
        with st.spinner("Summarizing ..."):
            llm_response = generate_gpt_response(prompt, context)    
            st.code(llm_response)

            try:
                data = json.loads(llm_response)
                st.session_state.messages.append({"role": "assistant", "content": data})
            except:
                pass
            
            st.markdown(f"{data['answer']}\n")
            if "datasets" in data.keys():
                markdown_text = ""
                for dataset in data["datasets"]:
                    markdown_text += f"- **{dataset['title']}**\n\n{dataset['description']}\n"
                st.markdown(markdown_text)
            if "additional" in data.keys():
                st.markdown(f"{data['additional']}\n")
    
    st.rerun()











