import plotly
from langchain_core.messages import AIMessage
import streamlit as st


async def invoke_our_graph(graph_runnable, st_messages, st_placeholder):
    """
    Asynchronously processes a stream of events from the graph_runnable and updates the Streamlit interface.

    Args:
        graph_runnable: The LangGraph runnable
        st_messages (list): List of messages to be sent to the graph_runnable.
        st_placeholder (st.beta_container): Streamlit placeholder used to display updates and statuses.

    Returns:
        AIMessage: An AIMessage object containing the final aggregated text content from the events.
    """
    # Set up placeholders for displaying updates in the Streamlit app
    container = st_placeholder  # This container will hold the dynamic Streamlit UI components
    thoughts_placeholder = container.container()  # Container for displaying status messages
    image_placeholder = container.empty()  # Container for showing an image
    token_placeholder = container.empty()  # Placeholder for displaying progressive token updates
    final_text = ""  # Will store the accumulated text from the model's response

    artifact = None
    # Stream events from the graph_runnable asynchronously
    async for event in graph_runnable.astream_events({"messages": st_messages}):
        kind = event["event"]  # Determine the type of event received

        if kind == "on_chat_model_stream":
            if  event["metadata"]["langgraph_node"] == "agent":
                # The event corresponding to a stream of new content (tokens or chunks of text)
                addition = event["data"]["chunk"].content  # Extract the new content chunk
                final_text += addition  # Append the new content to the accumulated text
                if addition:
                    token_placeholder.write(final_text)  # Update the st placeholder with the progressive response

        elif kind == "on_tool_start":
            # The event signals that a tool is about to be called
            with thoughts_placeholder:
                status_placeholder = st.empty()  # Placeholder to show the tool's status
                with status_placeholder.status(f"Using Tool {event['name']}", expanded=False) as s:
                    st.write("Called ", event['name'])  # Show which tool is being called
                    st.write("Tool input: ")
                    st.code(event['data'].get('input'))  # Display the input data sent to the tool
                    st.write("Tool output: ")
                    output_placeholder = st.empty()  # Placeholder for tool output that will be updated later below

        elif kind == "on_tool_end":
            # The event signals the completion of a tool's execution
            with thoughts_placeholder:
                if 'output' in event['data'].keys():
                    # We assume that `on_tool_end` comes after `on_tool_start`, meaning output_placeholder exists
                    event_output = event['data'].get('output')
                    if 'output_placeholder' in locals():
                        if hasattr(event_output, "content"):
                            output_placeholder.code(event_output.content)  # Display the tool's output
                        else:
                            output_placeholder.code(event_output)  # Display the tool's output

                    if hasattr(event_output, "artifact") and event_output.artifact is not None:
                        artifact = event_output.artifact
                        with image_placeholder:
                            fig = plotly.io.from_json(artifact)
                            st.plotly_chart(
                                fig,
                                key=f"plotly_chart_temporary",
                                use_container_width=True,
                                config={'displayModeBar': False})

    # Return the final aggregated message after all events have been processed
    return AIMessage(content=final_text) if artifact is None else AIMessage(content=final_text, artifact=artifact)