from typing import TextIO

import streamlit as st
import yaml
# from streamlit.runtime.scriptrunner.script_run_context import get_script_run_ctx
from streamlit.runtime.scriptrunner.script_runner import get_script_run_ctx


def get_version() -> str:
    try:
        with open("values.yaml") as f:
            data = yaml.safe_load(f)
            return data["ecotoxfred"]["image"]["tag"]
    except FileNotFoundError:
        print("Error: File 'values.yaml' not found.")
    except Exception as e:
        print(f"Unexpected error: {e}")
    return "no version info"

def get_langsmith_API_keys():
    return {
        "LANGSCHAIN_API_KEY": st.secrets["LANGCHAIN_API_KEY"],
        "LANGCHAIN_ENDPOINT": st.secrets["LANGCHAIN_ENDPOINT"],
        "LANGCHAIN_PROJECT": st.secrets["LANGCHAIN_PROJECT"],
        "LANGCHAIN_TRACING_V2": st.secrets["LANGCHAIN_TRACING_V2"]
    }

# tag::write_message[]
def write_message(message, save=True):
    """
    This is a helper function that saves a message to the
     session state and then writes a message to the UI
    """
    # Append to session state
    if save:
        st.session_state.messages.append(message)

    # Write to UI
    with st.chat_message(message["role"], avatar=message["avatar"]):
        st.markdown(message["content"])
# end::write_message[]

# tag::get_session_id[]
def get_session_id():
    return get_script_run_ctx().session_id
# end::get_session_id[]

# TODO: Rework the handling of images and other output
# # Submit handler
# def handle_submit(submitted_message):
#     """
#     Submit handler:
#
#     You will modify this method to talk with an LLM and provide
#     context using data from Neo4j.
#     """
#
#     # Handle the response
#     with st.spinner('Generating response ...'):
#         response = agent.generate_response(st.session_state.chat_agent, submitted_message)
#         find_str = 'figures/plot.png'
#         pattern = re.compile(r'\b\w*' + re.escape(find_str) + r'\w*\b')
#         matches = pattern.findall(response['output'])
#         final_content: str
#         if len(matches) > 0:
#             for match in matches:
#                 response['output'] = response['output'].replace(match, "")
#             final_content = response['output']
#             st.image("figures/plot.png", caption="Image generated with matplotlib from graph db cypher query result.")
#         else:
#             write_message('assistant', response['output'])
#         st.session_state.messages.append({
#             "role": "assistant",
#             "content": "Hi, I'm EcoToxFred!  How can I help you?",
#             "avatar": "figures/simple_avatar.png"
#         })

