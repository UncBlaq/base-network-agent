import asyncio
import os
from collections.abc import AsyncGenerator

import streamlit as st
from pydantic import ValidationError
from streamlit.runtime.scriptrunner import get_script_run_ctx

from client import AgentClient
from schema import ChatHistory, ChatMessage
from schema.task_data import TaskData, TaskDataStatus

APP_TITLE = "Base bot"
APP_ICON = "🧰"


async def main() -> None:
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon=APP_ICON,
        layout="centered",  # Center the layout for a clean look
    )

    # Initialize the AgentClient
    if "agent_client" not in st.session_state:
        agent_url = os.getenv("AGENT_URL", "http://localhost")  # Ensure correct FastAPI URL
        st.session_state.agent_client = AgentClient(agent_url)
    agent_client: AgentClient = st.session_state.agent_client

    # Set up thread ID and session state for messages
    if "thread_id" not in st.session_state:
        thread_id = get_script_run_ctx().session_id
        st.session_state.thread_id = thread_id
        st.session_state.messages = []

    messages: list[ChatMessage] = st.session_state.messages

    # Display a welcome message for new sessions
    if len(messages) == 0:
        WELCOME = "Welcome! Ask me anything about the Base network or related topics!"
        with st.chat_message("ai"):
            st.write(WELCOME)

    # Replay existing messages
    async def amessage_iter() -> AsyncGenerator[ChatMessage, None]:
        for message in messages:
            yield message

    await draw_messages(amessage_iter())

    # Handle user input
    if user_input := st.chat_input():
        # Save user input to session state
        messages.append(ChatMessage(type="human", content=user_input))
        st.chat_message("human").write(user_input)

        try:
            # Stream response from FastAPI
            stream = agent_client.astream(
                message=user_input,
                thread_id=st.session_state.thread_id,
            )
            await draw_messages(stream, is_new=True)
        except Exception as e:
            st.error(f"Error: {str(e)}")
        st.rerun()  # Refresh the app state to display new messages


async def draw_messages(
    messages_agen: AsyncGenerator[ChatMessage | str, None],
    is_new: bool = False,
) -> None:
    """
    Render chat messages in the interface, handling streaming updates.

    Args:
        messages_agen: An async generator of messages or streaming tokens.
        is_new: Boolean indicating whether the messages are new.
    """
    last_message_type = None
    st.session_state.last_message = None

    # Placeholder for streaming content
    streaming_placeholder = None
    streaming_content = ""

    # Process each message from the async generator
    while msg := await anext(messages_agen, None):
        if isinstance(msg, str):  # Handle streaming tokens
            if not streaming_placeholder:
                if last_message_type != "ai":
                    last_message_type = "ai"
                    st.session_state.last_message = st.chat_message("ai")
                with st.session_state.last_message:
                    streaming_placeholder = st.empty()
            streaming_content += msg
            streaming_placeholder.write(streaming_content)
            continue

        if not isinstance(msg, ChatMessage):
            st.error(f"Unexpected message type: {type(msg)}")
            st.stop()

        match msg.type:
            case "human":
                st.chat_message("human").write(msg.content)
                last_message_type = "human"
            case "ai":
                if is_new:
                    st.session_state.messages.append(msg)

                if last_message_type != "ai":
                    last_message_type = "ai"
                    st.session_state.last_message = st.chat_message("ai")

                with st.session_state.last_message:
                    if msg.content:
                        if streaming_placeholder:
                            streaming_placeholder.write(msg.content)
                            streaming_placeholder = None
                            streaming_content = ""
                        else:
                            st.write(msg.content)
            case "custom":
                try:
                    task_data: TaskData = TaskData.model_validate(msg.custom_data)
                    draw_task_data(task_data)
                except ValidationError:
                    st.error("Unexpected custom data in message")
                    st.write(msg.custom_data)


def draw_task_data(task_data: TaskData) -> None:
    """
    Draws task data updates using TaskDataStatus.
    """
    if "task_status" not in st.session_state:
        st.session_state.task_status = TaskDataStatus()

    task_status: TaskDataStatus = st.session_state.task_status
    task_status.add_and_draw_task_data(task_data)


if __name__ == "__main__":
    asyncio.run(main())
