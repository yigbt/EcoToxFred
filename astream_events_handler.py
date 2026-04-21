import plotly
from langchain_core.messages import AIMessage, SystemMessage
import streamlit as st
from prompts import Prompts
from todo_parsing import parse_write_todos_result, format_todos_for_display

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
    todo_list_container = container.empty()  # Use empty() so we can clear and replace it
    thoughts_placeholder = container.container()  # Container for displaying status messages
    image_placeholder = container.empty()  # Container for showing an image
    token_placeholder = container.empty()  # Placeholder for displaying progressive token updates
    final_text = ""  # Will store the accumulated text from the model's response
    from prompts import Prompts
    system_prompt = Prompts.agent.prompt
    #st_messages = [SystemMessage(content=system_prompt)] + st_messages
    artifact = None

    # Dictionary to track tool placeholders by tool call ID for parallel execution
    tool_placeholders = {}

    # Stream events from the graph_runnable asynchronously
    async for event in graph_runnable.astream_events({"messages": st_messages}):
        kind = event["event"]  # Determine the type of event received
        if kind == "on_chat_model_stream":
            if  event["metadata"]["langgraph_node"] == "model":
                # The event corresponding to a stream of new content (tokens or chunks of text)
                addition = event["data"]["chunk"].content  # Extract the new content chunk
                final_text += addition  # Append the new content to the accumulated text
                if addition:
                    token_placeholder.write(final_text)  # Update the st placeholder with the progressive response

        elif kind == "on_tool_start":
            # The event signals that a tool is about to be called
            tool_call_id = event.get("run_id")  # Get unique identifier for this tool call
            tool_name = event['name']

            # Check if this is a write_todos tool call
            if tool_name == "write_todos":
                # Store reference to the todo container for this tool call
                tool_placeholders[tool_call_id] = {
                    "type": "todo",
                    "container": todo_list_container
                }
            else:
                # Regular tool - create status container
                with thoughts_placeholder:
                    status_placeholder = st.empty()  # Placeholder to show the tool's status
                    with status_placeholder.status(f"Using Tool {tool_name}", expanded=False) as s:
                        st.write("Called ", tool_name)  # Show which tool is being called
                        st.write("Tool input: ")
                        st.code(event['data'].get('input'))  # Display the input data sent to the tool
                        st.write("Tool output: ")
                        output_placeholder = st.empty()  # Placeholder for tool output that will be updated later

                # Store placeholders indexed by tool call ID
                tool_placeholders[tool_call_id] = {
                    "type": "regular",
                    "output_placeholder": output_placeholder,
                    "status_placeholder": status_placeholder
                }

        elif kind == "on_tool_end":
            # The event signals the completion of a tool's execution
            tool_call_id = event.get("run_id")
            tool_name = event.get('name')

            if tool_call_id in tool_placeholders:
                tool_info = tool_placeholders[tool_call_id]

                if tool_info["type"] == "todo":
                    # Handle write_todos tool output
                    if 'output' in event['data'].keys():
                        event_output = event['data'].get('output')

                        # Parse and display the todo list
                        if hasattr(event_output, "content"):
                            todo_content = event_output.content
                        else:
                            todo_content = event_output
                        parsed_todos = parse_write_todos_result(todo_content)
                        todo_output = format_todos_for_display(parsed_todos)
                        # Clear the container and redraw with new content
                        with tool_info["container"].container():
                            st.info("📋 **Agenda**")
                            st.markdown(todo_output)

                elif tool_info["type"] == "regular":
                    # Handle regular tool output
                    if 'output' in event['data'].keys():
                        event_output = event['data'].get('output')
                        output_placeholder = tool_info["output_placeholder"]

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