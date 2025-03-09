import os
from moralis import sol_api
from dotenv import load_dotenv
from llm import ToolCallingLLM
from functions import *

load_dotenv()

class App:
    def __init__(self):
        self.huggingface_api_key = os.getenv('HYPERBOLIC_XYZ_KEY')
        self.llm = ToolCallingLLM(api_key=self.huggingface_api_key)
        self._register_functions()
        self.messages = []
    
    def reset(self):
        self.messages = []

    def _register_functions(self):
        """Register all available functions with the LLM."""
        self.llm.register_function(
            func=get_account_balance,
            description="Get the balance of an account on a given network.",
            parameters={
                "type": "object", 
                "properties": {
                    "address": {"type": "string", "description": "Address of the account"},
                    "network": {"type": "string", "description": "Name of the solana network", "default": "mainnet"}
                },
                "required": ["address"]
            }
        )

        self.llm.register_function(
            func=get_account_nfts,
            description="Get the NFTs owned by an account on a given network.",
            parameters={
                "type": "object",
                "properties": {
                    "address": {"type": "string", "description": "Address of the account"},
                    "network": {"type": "string", "description": "Name of the solana network", "default": "mainnet"}
                },
                "required": ["address"]
            }
        )

        self.llm.register_function(
            func=get_account_portfolio,
            description="Get the portfolio for a given network and address.",
            parameters={
                "type": "object",
                "properties": {
                    "address": {"type": "string", "description": "Address of the account"},
                    "network": {"type": "string", "description": "Name of the solana network", "default": "mainnet"}
                },
                "required": ["address"]
            }
        )

        self.llm.register_function(
            func=get_account_spl,
            description="Get the token balances owned by a given network and address.",
            parameters={
                "type": "object",
                "properties": {
                    "address": {"type": "string", "description": "Address of the account"},
                    "network": {"type": "string", "description": "Name of the solana network", "default": "mainnet"}
                },
                "required": ["address"]
            }
        )

        self.llm.register_function(
            func=get_nft_metadata,
            description="Get the global NFT metadata for a given network and contract.",
            parameters={
                "type": "object",
                "properties": {
                    "contract_address": {"type": "string", "description": "Address of the NFT contract"},
                    "network": {"type": "string", "description": "Name of the solana network", "default": "mainnet"}
                },
                "required": ["contract_address"]
            }
        )

        self.llm.register_function(
            func=get_token_price,
            description="Get the token price (usd and native) for a given contract address and network.",
            parameters={
                "type": "object",
                "properties": {
                    "contract_address": {"type": "string", "description": "Address of the token contract"},
                    "network": {"type": "string", "description": "Name of the solana network", "default": "mainnet"}
                },
                "required": ["contract_address"]
            }
        )

        self.llm.register_function(
            func=get_token_metadata,
            description="Get the global token metadata for a given network and contract.",
            parameters={
                "type": "object",
                "properties": {
                    "contract_address": {"type": "string", "description": "Address of the token contract"},
                    "network": {"type": "string", "description": "Name of the solana network", "default": "mainnet"}
                },
                "required": ["contract_address"]
            }
        )


        self.llm.register_function(
            func=get_whale_analysis,
            description="Analyze whale holders of a token and their potential market impact.",
            parameters={
                "type": "object",
                "properties": {
                    "token_address": {"type": "string", "description": "Address of the token contract to analyze"},
                    "prompt": {
                        "type": "string", 
                        "description": "Analysis prompt/question about the whale holders",
                        # "default": "Analyze the top 3 holders of this token and their potential market impact"
                    }
                },
                "required": ["token_address", "prompt"]
            }
        )

        # self.llm.register_function(
        #     func=search_arxiv_papers,
        #     description="Search for academic papers on arXiv.",
        #     parameters={
        #         "type": "object",
        #         "properties": {
        #             "query": {"type": "string", "description": "Search query"},
        #             "max_results": {"type": "integer", "description": "Maximum number of results"}
        #         },
        #         "required": ["query"]
        #     }
        # )

        # self.llm.register_function(
        #     func=get_weather,
        #     description="Get the current weather for a city.",
        #     parameters={
        #         "type": "object",
        #         "properties": {
        #             "city": {"type": "string", "description": "Name of the city"}
        #         },
        #         "required": ["city"]
        #     }
        
        

    def get_messages(self):
        """Return the current message history."""
        return self.messages

    def add_message(self, message):
        """Add a new message to the conversation history."""
        self.messages.append(message)

    def generate_response(self):
        """Generate a response using the LLM."""
        return self.llm.generate_response(messages=self.messages)

# Initialize app
# app = App()

# message = {"role": "user", "content": "What's the weather in New York?"}
# message = {"role": "user", "content": "What's the balance of the account x01234567890123456789012345678901234567890 on the solana network?"}
# message = {"role": "user", "content": "Find 3 papers on quantum computing."}
# message = {"role": "user", "content": "Who is George Weah?"}

# app.add_message(message)
# response = app.generate_response()
# print(response)



# get_token_price
# get_token_metadata
# get_native_balance
# get_token_balances
# get_portfolio
# get_swaps_by_pair
# get_swaps_by_token
# get_swaps_by_wallet
# get_token_pairs
# get_pair_stats
# get_coin_history
# get_wallet_portfolio