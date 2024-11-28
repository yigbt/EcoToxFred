import streamlit as st

import agent
from llm import llm
from utils import write_message, get_version

# Page Config
st.set_page_config(page_title="EcoToxFred", page_icon="figures/assistant.png",
    layout='centered',
    menu_items={
        'about': f'''**EcoToxFred v{get_version()}**        
        A Neo4j-backed Chatbot discussing environmental monitoring data
        contact: Jana Schor jana.schor@ufz.de, Patrick Scheibe pscheibe@cbs.mpg.de'''
    }
)

example_questions = [
    "What is Diuron and where has it been measured?",
    "What is Triclosan? Has it been measured in European freshwater?",
    "Find the 10 most frequent driver chemicals above a driver importance of 0.6",
    "For Citalopram, provide the name of the sampling site and the measurement time point as a table?",
    "Show the distribution of the summarized toxic unit (sumTU) for algae since 2010."
]

# Set up the session state and initialize the LLM agent
if "initialized" not in st.session_state:
    st.session_state.initialized = True
    my_chat = agent.create_chemical_chat_chain()
    tools = agent.create_toolset(general_chat=my_chat)
    st.session_state.chat_agent = agent.create_agent(current_llm=llm, toolset=tools)
    st.session_state.messages = [
        {"role": "assistant",
         "content": "Hi, I'm EcoToxFred!  How can I help you?",
         "avatar": "figures/assistant.png"},
    ]


def generate_response(prompt):
    """
    Generate a response for the given prompt using the agent.
    We can try to stream the agent's work and give some intermediate feedback to the user.

    :param prompt: The input prompt for generating a response.
    :return: The generated response.
    """
    from streamlit.runtime.scriptrunner import get_script_run_ctx
    response = None
    for s in st.session_state.chat_agent.stream(
            {'input': prompt},
            {"configurable": {"session_id": get_script_run_ctx().session_id}}
    ):
        if "actions" in s.keys():
            for act in s["actions"]:
                st.toast(act.log)
        response = s
    return response["output"]


def add_question_to_messages(text):
    st.session_state.messages.append({
        "role": "user",
        "content": text,
        "avatar": "figures/user.png"
    })


with st.sidebar:
    st.image("figures/UFZ_MPG_Logo.svg")
    st.header(f"EcoToxFred (v{get_version()})", divider=True)
    st.markdown(
        "A Chatbot for discussing environmental monitoring "
        "data collected in a large knowledge graph and stored in a Neo4j Graph Database."
    )
    st.header("Example Questions", divider=True)
    for index, example_question in enumerate(example_questions):
        st.button(
            example_question,
            key=f"example_question_{index}",
            on_click=add_question_to_messages,
            args=[example_question]
        )

# Display messages in Session State
for message in st.session_state.messages:
    write_message(message, save=False)

# Handle any user input
if question := st.chat_input("What do you want to know?"):
    write_message({
        "role": "user",
        "content": question,
        "avatar": "figures/user.png"
    })

if st.session_state.messages[-1]["role"] != "assistant":
    message = st.session_state.messages[-1]
    with st.spinner("Thinking..."):
        # TODO: Try catch
        generated_response = generate_response(st.session_state.messages[-1]["content"])
        write_message({
            "role": "assistant",
            "content": generated_response,
            "avatar": "figures/assistant.png"
        })
