import json
from typing import Dict, Callable, List
from openai import OpenAI
from datetime import datetime
from tools import ToolManager


HYPERBOLIC_ENDPOINT_URL = "https://api.hyperbolic.xyz/v1"
HF_ENDPOINT_URL = "https://huggingface.co/api/inference-proxy/together"

ENDPOINT_URL = HYPERBOLIC_ENDPOINT_URL

MODEL_NAME = "meta-llama/Llama-3.3-70B-Instruct"
# MODEL_NAME = "meta-llama/Llama-3.3-70B-Instruct-Turbo"


current_date = datetime.now()
formatted_date = current_date.strftime("%d %B %Y")



class ToolCallingLLM:
    def __init__(self, api_key: str, model_name: str = MODEL_NAME):
        """
        Initialize the LLM with the API key and model name.
        """
        self.api_key = api_key
        self.model_name = model_name
        self.client = OpenAI(base_url=ENDPOINT_URL,api_key=self.api_key)
        self.registered_functions = {}  # Stores registered functions and their metadata   
        self.tool_manager = ToolManager()

    def register_function(self, func: Callable, description: str, parameters: Dict):
        """
        Register a function with its description and parameters.
        
        Args:
            func: The function to register.
            description: A description of what the function does.
            parameters: A dictionary describing the function's parameters.
                       Example: {
                           "type": "object",
                           "properties": {
                               "param1": {"type": "string", "description": "Description of param1"},
                               "param2": {"type": "integer", "description": "Description of param2"},
                           },
                           "required": ["param1"]
                       }
        """
        self.registered_functions[func.__name__] = {
            "function": func,
            "description": description,
            "parameters": parameters,
            "strict": True
        }

        self.tool_manager.store_tool_embeddings(
            {
                "function": func.__name__,
                "description": description,
                "parameters": parameters
            }
        )


    def _generate_function_list(self, query: str):
        """
        Generate a list of relevant functions in the format expected by the LLM.
        """
        tool_names = self.tool_manager.select_tools(query)

        return [
            {
                "type": "function",
                "function": {
                    "name": name,
                    "description": self.registered_functions[name]["description"],
                    "parameters": self.registered_functions[name]["parameters"]
                }
            }
            for name in tool_names if name in self.registered_functions
        ]
    
    def _call_function(self, function_name: str, parameters: Dict):
        """
        Call a registered function with the provided parameters.
        """
        if function_name not in self.registered_functions:
            raise ValueError(f"Function '{function_name}' is not registered.")
        
        func = self.registered_functions[function_name]["function"]
        return func(**parameters)

    def _get_system_prompt_with_tools(self, query: str):
        """
        Get the system prompt.
        """
        # Construct the system prompt with available functions
        functions_list = self._generate_function_list(query)
        system_prompt = f"""
Environment: ipython
Cutting Knowledge Date: December 2023
Today Date: {formatted_date}
You are a helpful assistant with tool calling capabilities.
You have access to the following functions (in JSON format):
{json.dumps(functions_list, indent=4)}
If the user's request requires calling a function:
    1. Check if the function requires a prompt.
    2. If the function requires a prompt, assign the user's request as the prompt parameter of the function.
    3. Check if all the required parameters are provided in the user's request.
    4. If all the required parameters are provided, proceed as follows:
        - Respond with a JSON object in the format:
        {{"name": "function_name", "parameters": {{"param1": "value1", "param2": "value2"}}}}. 
        - Make sure not to add any extra information.
        - Return only an instance of the JSON, NOT the schema itself.
    5. If some of the required parameters are missing, proceed as follows:
        - Ask the user for the required parameters that are missing only.
        - Make sure not to fill in a required parameter yourself.  
        - Fill in the optional parameters with their default values.
        - Make sure not to ask the user for parameters that are optional. 
        - Do not share your thoughts and reasoning process.
        - Examples of valid responses:
            - "I need more information to proceed. Could you please provide the token address?"
            - "For which account do you want to get the balance?"
        - Be very creative, use variations of the examples above.
        - Examples of invalid responses:
            - "To answer the query, I need to call a function: {{"name": "function_name", "parameters": {{"param1": "value1", "param2": "value2"}}}}"
            (reason for invalidity: response contains the reasoning process)
            - "<|python_tag|>{{"name": "function_name", "parameters": {{"param1": "value1", "param2": "value2"}}}}"
            (reason for invalidity: response contains extra information like <|python_tag|>)
    6. If the function call returns an error, proceed as follows:
        - Respond with a friendly non technical message to explain the error
        - Analyze the error and guide the user to try again with the correct parameters.
        - Make sure not to share the error message with the user.
If the user request does not necessitate a function call, simply respond to the user's query directly.
""".strip()
        return system_prompt, functions_list 
    
    
    def _extract_json_from_text(self, text: str) -> str:
        """
        Extract valid JSON from text that might contain additional markers or text.
        """
        # Find the first '{' and last '}' in the text
        start = text.find('{')
        end = text.rfind('}')
        
        if start != -1 and end != -1 and end > start:
            potential_json = text[start:end + 1]
            try:
                # Validate that it's proper JSON
                json.loads(potential_json)
                return potential_json
            except json.JSONDecodeError:
                return None
        return None

    def generate_response(self, messages: List[Dict], temperature: float = 0.6, max_tokens: int = 512):
        """
        Generate a response from the LLM, handling function calls if necessary.
        This method is recursive and will re-call the LLM with the tool result when a tool is called.

        Args:
            messages: The conversation history as a list of messages.
            temperature: Sampling temperature for the LLM.
            max_tokens: Maximum number of tokens to generate.

        Returns:
            The LLM's response content.
        """

        if len(messages) == 0:
            return "No messages provided."
        
        print(f"#### Messages:\n {messages[-1]['content']} \n####")
        # breakpoint()
        system_prompt, functions_list = self._get_system_prompt_with_tools(messages[-1]["content"])

        # Ensure the system prompt is included in the messages
        if not any(msg["role"] == "system" for msg in messages):
            messages.insert(0, {"role": "system", "content": system_prompt})
        else:
            messages[0]["content"] = system_prompt

        print(f"#### Conversation history:\n {json.dumps(messages, indent=4)} \n####")
        # breakpoint()

        # Generate the LLM response
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=functions_list,
            tool_choice="auto"
        )

        print(f"#### LLM raw response:\n {response} \n####")
        # breakpoint()

        # Get the response content
        response_content = response.choices[0].message.content
        
        # Try to parse as JSON if it looks like it might contain JSON
        if response_content and ('{' in response_content) and ('}' in response_content):
            # Try to extract clean JSON from the response
            clean_json = self._extract_json_from_text(response_content)
            if clean_json:
                try:
                    json_response = json.loads(clean_json)
                    # Check if it matches our expected function call format
                    if isinstance(json_response, dict) and "name" in json_response and "parameters" in json_response:
                        function_name = json_response["name"]
                        parameters = json_response["parameters"]
                        
                        # Add the function call to messages
                        messages.append({
                            "role": "assistant",
                            "content": json.dumps({"name": function_name, "parameters": parameters})
                        })

                        # Call the function and add result to messages
                        try:
                            function_result = self._call_function(function_name, parameters)
                            messages.append({
                                "role": "ipython",
                                "content": json.dumps(function_result)
                            })
                        except Exception as e:
                            # function call error
                            print(f"#### Error: {e} \n####")
                            messages.append({
                                "role": "ipython",
                                "content": str(e)
                            })
                        # Recursive call with updated messages
                        return self.generate_response(messages)
                except json.JSONDecodeError:
                    # Not a valid JSON, treat as regular text response
                    pass
                except Exception as e:
                    # Unhandled error
                    print(f"#### Error: {e} \n####")
                    response_content = "I'm sorry, I'm not able to process your request. Please, verify the details are accurate and try again. Make sure to provide all the details."
                    messages.append({
                        "role": "assistant",
                        "content": response_content
                    })
                    return response_content
                    # return self.generate_response(messages)
        # If we reach here, it's a regular text response
        messages.append({
            "role": "assistant",
            "content": response_content
        })
        return response_content


        

        