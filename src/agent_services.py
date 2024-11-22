from typing import Any
from uuid import uuid4
import logging

from fastapi import HTTPException

from langgraph.graph.state import CompiledStateGraph
from langchain_core.messages import AnyMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from schema import UserInput, ChatMessage
from agents import DEFAULT_AGENT, agents

from agent_utils import (
    convert_message_content_to_string,
    langchain_to_chat_message,
    remove_tool_calls,
)

logger = logging.getLogger(__name__)

def _parse_input(user_input: UserInput) -> tuple[dict[str, Any], str]:
    run_id = uuid4()
    thread_id = user_input.thread_id or str(uuid4())
    kwargs = {
        "input": {"messages": [HumanMessage(content=user_input.message)]},
        "config": RunnableConfig(
            configurable={"thread_id": thread_id, "model": user_input.model}, run_id=run_id
        ),
    }
    return kwargs, run_id

async def ainvoke(user_input: UserInput, agent_id: str = DEFAULT_AGENT) -> ChatMessage:
    agent: CompiledStateGraph = agents[agent_id]
    kwargs, run_id = _parse_input(user_input)
    try:
        response = await agent.ainvoke(**kwargs)
        output = langchain_to_chat_message(response["messages"][-1])
        output.run_id = str(run_id)
        return output
    except Exception as e:
        logger.error(f"An exception occurred: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error")
