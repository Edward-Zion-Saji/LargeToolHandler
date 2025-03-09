from moralis import sol_api
from dotenv import load_dotenv
import os
import requests

load_dotenv()

MORALIS_API_KEY = os.getenv('MORALIS_API_KEY')

# def search_arxiv_papers(query: str, max_results: int = 5):
#     """Searches for papers on arxiv."""
#     print(f"Searching for papers on {query}")
#     return [f"Paper {i} on {query}" for i in range(max_results)]

# def get_weather(city: str):
#     """Gets the weather for a given city."""
#     print(f"Getting weather for {city}")
#     return 25

# Account API

def get_account_balance(address: str, network: str = "mainnet"):
    """Gets the native balance owned by solana network and address."""
    params = {
        "network": network, 
        "address": address, 
    }
    result = sol_api.account.balance(
        api_key=MORALIS_API_KEY,
        params=params,
    )
    return result

def get_account_nfts(address: str, network: str = "mainnet"):
    """Gets NFTs owned by a given network and address."""
    params = {
        "network": network,
        "address": address,
    }
    result = sol_api.account.get_nfts(
        api_key=MORALIS_API_KEY,
        params=params,
    )
    return result

def get_account_portfolio(address: str, network: str = "mainnet"):
    """Gets the portfolio for a given network and address."""
    params = {
        "network": network,
        "address": address,
    }
    result = sol_api.account.get_portfolio(
        api_key=MORALIS_API_KEY,
        params=params,
    )
    return result

def get_account_spl(address: str, network: str = "mainnet"):
    """Gets the token balances owned by a given network and address."""
    params = {
        "network": network,
        "address": address,
    }
    result = sol_api.account.get_spl(
        api_key=MORALIS_API_KEY,
        params=params,
    )
    return result

# NFT API

def get_nft_metadata(contract_address: str, network: str = "mainnet"):
    """Get the global NFT metadata for a given network and contract (mint, standard, name, symbol, metaplex)."""
    params = {
        "network": network,
        "address": contract_address
    }
    result = sol_api.nft.get_nft_metadata(
        api_key=MORALIS_API_KEY,
        params=params,
    )
    return result

# Token API

def get_token_price(contract_address: str, network: str = "mainnet"):
    """Gets the token price (usd and native) for a given contract address and network."""
    params = {
        "network": network,
        "address": contract_address 
    }
    result = sol_api.token.get_token_price(
        api_key=MORALIS_API_KEY,
        params=params,
    )
    return result

def get_token_metadata(contract_address: str, network: str = "mainnet"):
    """Get the global token metadata for a given network and contract (mint, standard, name, symbol, metaplex)."""
    params = {
        "network": network,
        "address": contract_address
    }
    result = sol_api.token.get_token_metadata(
        api_key=MORALIS_API_KEY,
        params=params,
    )
    return result



# Whale Analysis API
def get_whale_analysis(token_address: str, prompt: str) -> dict:
    """
    Queries the whale analysis API to analyze token holders.
    
    Args:
        token_address (str): The token contract address to analyze
        prompt (str): The analysis prompt/question
        
    Returns:
        dict: The analysis response from the API
    """
    
    url = "http://35.172.214.184:5000/api/whale-analysis"
    payload = {
        "token_address": token_address,
        "prompt": prompt
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx, 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to get whale analysis: {str(e)}")
    
    # http://35.172.214.184:5000/api/whale-analysis

    # {
    #     "token_address": "6p6xgHyF7AeE6TZkSmFsko444wqoP15icUSqi2jfGiPN",
    #     "prompt": "Analyze the top 3 holders of this token and their potential market impact"
    # }
    # get_whale_wallets

    # http://18.212.23.37:5000/api/crypto/query

    # this the endpoint and sample payload is 

    # {
    #     "query": "get_token_price 6p6xgHyF7AeE6TZkSmFsko444wqoP15icUSqi2jfGiPN",
    #     "chat_history": [
    #         ["What is the price of SRM?", "The current price of SRM token is..."],
    #         ["Show me the metadata", "Here is the token metadata..."]
    #     ]
    # }

    # use this for the these tools 

    # 1. get_wallet_info
    # 2. get_specific_details_about_token