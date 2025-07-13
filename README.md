
# ToolHandler

A Python library for interacting with LLMs (Large Language Models) and function calling capabilities.

## Features

- Integration with OpenAI-compatible LLM APIs, especially llama-3.3
- Function registration and tool calling system
- Optimization of the tool calling process with the selection of the relevant top N functions to be fed into the LLM prompt
- Support for conversation history and recursive function calls

## Prerequisites

- Python 3.10+
- OpenAI API key
- Moralis API key

Create a `.env` file in the root directory and add your API keys. Look at the `.env.example` file for reference.

## Directory Structure

- `chat.py`: Main file for the chat interface based on gradio
- `llm.py`: File for the Generic Tool Calling LLM class that enables tool registration and tool calling
- `tools.py`: File for the `Tool Manager` class that stores tool embeddings and select the top N tools to be fed into the LLM prompt related to the user query
- `functions.py`: File for the definition of the functions available for the LLM to call. It contains the actual functions that interact with the Moralis Solana API
- `app.py`: File for the initialization of the tool calling LLM and its integration with the Moralis Solana API
- `requirements.txt`: File for the dependencies
- `.env.example`: Reference file to create the `.env` file for the environment variables
- `README.md`: This file.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python chat.py
```
This will start the chat interface. Copy the URL of the interface and paste it in your browser (e.g.,  http://127.0.0.1:7860). 
Look at `functions.py` to formulate your queries based on the list of available functions.

Sample queries:
- "What is the balance of the account [account_address] on mainnet?"
- "What is the balance of the account [account_address]?" (Default network is mainnet)
- "What is the token price of [token_address]?"
- "I want to know the global token metadata for the contract [contract_address]"
- "What are the latest news on [topic]?" (Should not call any function)

***Note**: You can take a look at the terminal output to see the tool selection process (similarity scores, top N functions), tool calls, message history, raw outputs, etc.*

## Limitations

The focus is now on tool calling, the integration with the Moralis Solana API has just started.
