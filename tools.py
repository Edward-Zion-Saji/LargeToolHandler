from typing import Dict
from sklearn.metrics.pairwise import cosine_similarity
from openai import OpenAI
from sentence_transformers import SentenceTransformer

class ToolManager:
    """
    Manage all tools for the LLM. 
    It is used to select the best tools to send to the LLM for a given user query.
    """
    def __init__(self):
        self.tool_embeddings = {} # tool embeddings dictionary

    def store_tool_embeddings(self, tool: Dict):
        """
        compute and store the embeddings of a tool description.

        Args:
            tool: A dictionary with the following structure:
                {
                    "function": "tool_name",
                    "description": "tool_description",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "param1": {"type": "string", "description": "Description of param1"},
                            "param2": {"type": "integer", "description": "Description of param2"},
                        },
                        "required": ["param1"]
                    }
                }

        Returns:
            A dictionary where keys are function names and values are their embeddings.
        """
        tool_name = tool["function"]
        function_embedding = self.get_embedding(str(tool))
        self.tool_embeddings[tool_name] = function_embedding # store the embedding for the tool in the tool_embeddings dictionary

    
    def get_embedding(self, text, model_name="all-MiniLM-L6-v2"):
        """
        Get the embedding for a given text using SentenceTransformer.
        """
        model = SentenceTransformer(model_name)
        return model.encode(text)
    
    def select_tools(self, user_input, top_n=5, similarity_threshold=0.2):
        """
        Select the most relevant tools based on user input.
        
        Args:
            user_input: The user's query text
            top_n: Maximum number of tools to return
            similarity_threshold: Minimum similarity score (0-1) for a tool to be included
        
        Returns:
            List of tool names that meet the similarity threshold, ordered by relevance
        """
        user_embedding = self.get_embedding(user_input) 
        similarities = {}

        # Are there any tool embeddings?
        if not self.tool_embeddings:
            print("Warning: No tool embeddings found!")
            return []

        for tool_name, tool_embedding in self.tool_embeddings.items():
            similarity = cosine_similarity([user_embedding], [tool_embedding])[0][0]
            # Only include tools that meet the threshold
            if similarity >= similarity_threshold:
                similarities[tool_name] = similarity
        
        # Select the top N functions with the highest similarity scores
        sorted_functions = sorted(similarities.items(), key=lambda x: x[1], reverse=True)
        print(f"#### Sorted functions:\n {sorted_functions} \n####")
        
        top_n = min(top_n, len(sorted_functions))
        return [tool for tool, score in sorted_functions[:top_n]]
