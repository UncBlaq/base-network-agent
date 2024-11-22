from fastapi import APIRouter, status
from schema import (
    ChatMessage,
    UserInput,
)
from agent_services import ainvoke


user_router = APIRouter(prefix="/user", tags=["User"])


@user_router.post("/invoke")
async def invoke(user_input: UserInput) -> ChatMessage:
    """
    Invoke the default agent with user input to retrieve a final response.

    Use thread_id to persist and continue a multi-turn conversation. run_id kwarg
    is also attached to messages for recording feedback.
    """
    return await ainvoke(user_input=user_input)
