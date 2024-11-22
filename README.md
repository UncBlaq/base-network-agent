# BASE BOT

This repository provides a blueprint and full toolkit for a LangGraph-based agent service architecture. It includes a [LangGraph](https://langchain-ai.github.io/langgraph/) agent, a [FastAPI](https://fastapi.tiangolo.com/) service to serve it, a client to interact with the service, and a [Streamlit](https://streamlit.io/) app that uses the client to provide a chat interface.

This project offers a template for you to easily build and run your own agents using the LangGraph framework. It demonstrates a complete setup from agent definition to user interface, making it easier to get started with LangGraph-based projects by providing a full, robust toolkit.



## Overview



### Quickstart

Run directly in python

```sh
# An OPENAI_API_KEY is required
echo 'OPENAI_API_KEY=your_openai_api_key' >> .env

# uv is recommended but "pip install ." also works
pip install uv
uv sync --frozen

# edit(comment either of the two) code in to choose if you want test with streamlit or swagger docs

# "uv sync" creates .venv automatically
source .venv/bin/activate
python src/run_service.py

# In another shell
source .venv/bin/activate
streamlit run src/streamlit_app.py
```

### Architecture Diagram

<img src="media/agent_architecture.png" width="600">

### Key Features

1. **LangGraph Agent**: A customizable agent built using the LangGraph framework.
1. **FastAPI Service**: Serves the agent with both streaming and non-streaming endpoints.
1. **Advanced Streaming**: A novel approach to support both token-based and message-based streaming.
1. **Streamlit Interface**: Provides a user-friendly chat interface for interacting with the agent.
1. **Multiple Agent Support**: Run multiple agents in the service and call by URL path
1. **Asynchronous Design**: Utilizes async/await for efficient handling of concurrent requests.
1. **Feedback Mechanism**: Includes a star-based feedback system integrated with LangSmith.

### Key Files

The repository is structured as follows:

- `src/agents/research_assistant.py`: Defines the main LangGraph agent
- `src/agents/models.py`: Configures available models based on ENV
- `src/agents/agents.py`: Mapping of all agents provided by the service
- `src/schema/schema.py`: Defines the protocol schema
- `src/service/service.py`: FastAPI service to serve the agents
- `src/client/client.py`: Client to interact with the agent service
- `src/streamlit_app.py`: Streamlit app providing a chat interface

## Why LangGraph?

AI agents are increasingly being built with more explicitly structured and tightly controlled [Compound AI Systems](https://bair.berkeley.edu/blog/2024/02/18/compound-ai-systems/), with careful attention to the [cognitive architecture](https://blog.langchain.dev/what-is-a-cognitive-architecture/). At the time of this repo's creation, LangGraph seems like the most advanced open source framework for building such systems, with a high degree of control as well as support for features like concurrent execution, cycles in the graph, streaming results, built-in observability, and the rich ecosystem around LangChain.



## Setup and Usage

1. Clone the repository:

   ```sh
   git clone https://github.com/abeenoch/base-network-agent.git
   cd base-network-agent
   ```

2. Set up environment variables:
   Create a `.env` file in the root directory and add the following:

   ```sh
   # Provide at least one LLM API key to enable the agent service

   # Optional, to enable OpenAI gpt-4o-mini
   OPENAI_API_KEY=your_openai_api_key

   # Optional, to enable LlamaGuard and Llama 3.1
   GROQ_API_KEY=your_groq_api_key

   # Optional, to enable Gemini 1.5 Flash
   # See: https://ai.google.dev/gemini-api/docs/api-key
   GOOGLE_API_KEY=your_gemini_key

   # Optional, to enable Claude 3 Haiku
   # See: https://docs.anthropic.com/en/api/getting-started
   ANTHROPIC_API_KEY=your_anthropic_key

   # Optional, to enable AWS Bedrock models Haiku
   # See: https://docs.aws.amazon.com/bedrock/latest/userguide/setting-up.html
   USE_AWS_BEDROCK=true

   # Optional, to enable simple header-based auth on the service
   AUTH_SECRET=any_string_you_choose

   # Optional, to enable OpenWeatherMap
   OPENWEATHERMAP_API_KEY=your_openweathermap_api_key

   # Optional, to enable LangSmith tracing
   LANGCHAIN_TRACING_V2=true
   LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
   LANGCHAIN_API_KEY=your_langchain_api_key
   LANGCHAIN_PROJECT=your_project

   # Optional, if MODE=dev, uvicorn will reload the server on file changes
   MODE=
   ```

3. You can now run the agent service and the Streamlit app locally, either with Docker or just using Python. The Docker setup is recommended for simpler environment setup and immediate reloading of the services when you make changes to your code.




You can also run the agent service and the Streamlit app locally without Docker, just using a Python virtual environment.

1. Create a virtual environment and install dependencies:

   ```sh
   pip install uv
   uv sync --frozen --extra dev
   source .venv/bin/activate
   ```

2. Run the FastAPI server:

   ```sh
   python src/run_service.py
   ```

3. In a separate terminal, run the Streamlit app:

   ```sh
   streamlit run src/streamlit_app.py
   ```

4. Open your browser and navigate to the URL provided by Streamlit (usually `http://localhost:8501`).


## Customization

To customize the agent for your own use case:

1. Add your new agent to the `src/agents` directory. You can copy `research_assistant.py` or `chatbot.py` and modify it to change the agent's behavior and tools.
1. Import and add your new agent to the `agents` dictionary in `src/agents/agents.py`. Your agent can be called by `/<your_agent_name>/invoke` or `/<your_agent_name>/stream`.
1. Adjust the Streamlit interface in `src/streamlit_app.py` to match your agent's capabilities.


