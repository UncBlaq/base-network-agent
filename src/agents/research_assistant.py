import os
from datetime import datetime
from typing import Literal
import requests

from langchain_community.tools import DuckDuckGoSearchResults
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, SystemMessage
from langchain_core.runnables import RunnableConfig, RunnableLambda, RunnableSerializable
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, MessagesState, StateGraph
from langgraph.managed import IsLastStep
from langgraph.prebuilt import ToolNode

from agents.llama_guard import LlamaGuard, LlamaGuardOutput, SafetyAssessment
from agents.models import models
from agents.tools import calculator

import requests

class DevBotTools:
    @staticmethod
    def base_network_info(query: str) -> dict:
        """
        Perform a general internet search to retrieve information about the Base network.
        
        Parameters:
        - query (str): The query or topic about the Base network.

        Returns:
        - dict: A dictionary containing the search results or a helpful error message.
        """
        # Updated to use DuckDuckGo Search API with better error handling
        search_url = "https://api.duckduckgo.com/"
        params = {
            "q": f"Base network {query}",  # Add specificity to the query
            "format": "json",
            "no_html": 1,
            "skip_disambig": 1,
        }
        try:
            response = requests.get(search_url, params=params, timeout=10)
            response.raise_for_status()
            search_results = response.json()
            results = search_results.get("RelatedTopics", [])
            
            # Process and format results
            if results:
                processed_results = [
                    {"title": item.get("Text"), "url": item.get("FirstURL")}
                    for item in results
                    if "Text" in item and "FirstURL" in item
                ]
                return {"results": processed_results[:5]}  # Return the top 5 results
            
            return {"message": "No relevant results found for your query."}
        except requests.Timeout:
            return {"error": "Timeout Error", "message": "The search request timed out. Please try again."}
        except requests.RequestException as e:
            return {"error": "Network Error", "message": str(e)}
        
        
    @staticmethod
    def crypto_price(query: str) -> dict:
        """
        Fetch current cryptocurrency prices.

        Parameters:
        - query (str): The cryptocurrency name or symbol (e.g., BTC, ETH, Bitcoin).

        Returns:
        - dict: A dictionary containing the current price in USD or an error message.
        """
        url = "https://api.coingecko.com/api/v3/simple/price"
        # Format the query to ensure it's compatible with CoinGecko's API
        params = {"ids": query.lower(), "vs_currencies": "usd"}
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            # Parse response
            data = response.json()
            if query.lower() in data:
                price = data[query.lower()]["usd"]
                return {"message": f"The current price of {query.upper()} is ${price:.2f} USD."}
            else:
                return {"message": f"Unable to retrieve the price for '{query}'. Please check the cryptocurrency name or symbol."}
        except requests.Timeout:
            return {"error": "Timeout Error", "message": "The request to CoinGecko timed out. Please try again later."}
        except requests.RequestException as e:
            return {"error": "Network Error", "message": str(e)}


    


web_search = DuckDuckGoSearchResults(name="WebSearch")
python_repl = calculator  # Repurpose calculator for code and math execution
tools = [web_search, python_repl]

# Add tools specific to blockchain and Base network
tools.append(DevBotTools.base_network_info)
tools.append(DevBotTools.crypto_price)

# Define system instructions for DevBot
current_date = datetime.now().strftime("%B %d, %Y")
instructions = f"""
    You are DevBot, an assistant designed for blockchain developers working on the Base network. 
    Today's date is {current_date}.

    A few things to remember:
    - Always confirm the developer's requirements before providing code examples or blockchain resources.
    - Provide concise, accurate answers to coding, blockchain, or cryptocurrency queries.
    - Use the Base Network Info tool to fetch Base-specific information, and the Crypto Price tool for real-time cryptocurrency data.
    - Use markdown-formatted links for any citations or documentation references.
    - For coding tasks, generate examples with detailed explanations.
    """


def wrap_model(model: BaseChatModel) -> RunnableSerializable[MessagesState, AIMessage]:
    model = model.bind_tools(tools)
    preprocessor = RunnableLambda(
        lambda state: [SystemMessage(content=instructions)] + state["messages"],
        name="StateModifier",
    )
    return preprocessor | model


def format_safety_message(safety: LlamaGuardOutput) -> AIMessage:
    content = (
        f"This conversation was flagged for unsafe content: {', '.join(safety.unsafe_categories)}"
    )
    return AIMessage(content=content)


async def acall_model(state: MessagesState, config: RunnableConfig) -> MessagesState:
    m = models[config["configurable"].get("model", "gpt-4o-mini")]
    model_runnable = wrap_model(m)
    response = await model_runnable.ainvoke(state, config)

    # Run LlamaGuard safety check
    llama_guard = LlamaGuard()
    safety_output = await llama_guard.ainvoke("Agent", state["messages"] + [response])
    if safety_output.safety_assessment == SafetyAssessment.UNSAFE:
        return {"messages": [format_safety_message(safety_output)], "safety": safety_output}
    
    if "is_last_step" not in state:
        state["is_last_step"] = False

    if state ["is_last_step"] and response.tool_calls:
        return {
            "messages": [
                AIMessage(
                    id=response.id,
                    content="Sorry, need more steps to process this request.",
                )
            ]
        }
    return {"messages": [response]}


async def llama_guard_input(state: MessagesState, config: RunnableConfig) -> MessagesState:
    llama_guard = LlamaGuard()
    safety_output = await llama_guard.ainvoke("User", state["messages"])
    return {"safety": safety_output, "messages": state["messages"]}


async def block_unsafe_content(state: MessagesState, config: RunnableConfig) -> MessagesState:
    safety: LlamaGuardOutput = state["safety"]
    return {"messages": [format_safety_message(safety)]}


# Define the graph
agent = StateGraph(MessagesState)
agent.add_node("model", acall_model)
agent.add_node("tools", ToolNode(tools))
agent.add_node("guard_input", llama_guard_input)
agent.add_node("block_unsafe_content", block_unsafe_content)
agent.set_entry_point("guard_input")


# Check for unsafe input and block further processing if found
def check_safety(state: MessagesState) -> Literal["unsafe", "safe"]:
    safety: LlamaGuardOutput = state["safety"]
    match safety.safety_assessment:
        case SafetyAssessment.UNSAFE:
            return "unsafe"
        case _:
            return "safe"


agent.add_conditional_edges(
    "guard_input", check_safety, {"unsafe": "block_unsafe_content", "safe": "model"}
)

# Always END after blocking unsafe content
agent.add_edge("block_unsafe_content", END)

# Always run "model" after "tools"
agent.add_edge("tools", "model")


# After "model", if there are tool calls, run "tools". Otherwise END.
def pending_tool_calls(state: MessagesState) -> Literal["tools", "done"]:
    last_message = state["messages"][-1]
    if not isinstance(last_message, AIMessage):
        raise TypeError(f"Expected AIMessage, got {type(last_message)}")
    if last_message.tool_calls:
        return "tools"
    return "done"


agent.add_conditional_edges("model", pending_tool_calls, {"tools": "tools", "done": END})

research_assistant = agent.compile(
    checkpointer=MemorySaver(),
)