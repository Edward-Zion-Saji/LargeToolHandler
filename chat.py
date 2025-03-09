# Gradio chat interface

import gradio as gr
from app import App
from typing import Dict, Any
import uuid

# Store for managing multiple chat sessions
sessions: Dict[str, Any] = {}

def get_or_create_session(session_id: str):
    """
    Get an existing session or create a new one.
    """
    if session_id not in sessions:
        sessions[session_id] = {
            "app_instance": App(),  # Create new App instance for this session
            "chat_history": []
        }
    return sessions[session_id]

def chat_with_llm(user_input: str, session_id: str):
    """
    Handle user input and generate responses using the ToolCallingLLM.
    """
    # Get or create session
    session = get_or_create_session(session_id)
    app_instance = session["app_instance"]
    chat_history = session["chat_history"]

    # Add the user's message to the conversation history
    user_message = {"role": "user", "content": user_input.strip()}
    chat_history.append(user_message)
    app_instance.add_message(user_message)
    
    # Generate the LLM's response
    response = app_instance.generate_response()

    # Add the assistant's response to the conversation history
    assistant_message = {"role": "assistant", "content": response}
    chat_history.append(assistant_message)
    
    # Update the session's chat history
    session["chat_history"] = chat_history

    # Format the chat history for Gradio
    formatted_history = []
    for message in chat_history:
        if message["role"] == "user":
            formatted_history.append((message["content"], None))
        elif message["role"] == "assistant":
            formatted_history[-1] = (formatted_history[-1][0], message["content"])

    return formatted_history

def reset_chat(session_id: str):
    """
    Reset the chat and clear the session.
    """
    session = get_or_create_session(session_id)
    session["app_instance"].reset()
    session["chat_history"] = []
    return []

# Gradio interface
with gr.Blocks(
    css="""
    /* Keep the overall app background dark */
    .gradio-container {
        background-color: #1f1f1f !important;
    }

    /* Make all "block" containers green.
       Gradio usually wraps components in divs with the class "block" */
    .block {
        background-color: #00ff00 !important;
        padding: 1rem !important;
        border-radius: 8px !important;
    }

    /* Any titles (headings or labels) inside these blocks should be black and bold */
    .block h1, .block h2, .block h3, .block label {
        color: #000000 !important;
        font-weight: bold !important;
    }

    /* Override the input text box areas so they stay white.
       This applies both to their container and the actual input field. */
    .gr-textbox {
        background-color: #ffffff !important;
        padding: 8px !important;
        border-radius: 4px !important;
    }
    .gr-textbox input {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #cccccc !important;
        padding: 4px !important;
        border-radius: 4px !important;
    }

    /* Optionally, keep buttons green (with white text) */
    .gr-button {
        background-color: #00ff00 !important;
        color: #ffffff !important;
    }

    /* If your output textbox is also a gr-textbox and should be white: */
    .gradio-container .gr-textbox[interactive="false"] {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
"""
) as demo:
    # Remove the session ID generation from here
    session_id = gr.State()  # Initialize empty state
    
    gr.Markdown("# Tool-Calling LLM Chatbot")
    gr.Markdown("Ask questions, and the chatbot will respond using registered tools.")
    
    # Create a function to generate and display session ID
    def create_session():
        new_id = str(uuid.uuid4())
        return new_id
        # return new_id, f"Session ID: {new_id}"
    
    # session_text = gr.Markdown()  # Add markdown component for session ID display
    
    # Generate new session ID when interface loads
    demo.load(
        fn=create_session,
        outputs=[session_id],
    )

    # Rest of the interface components
    chatbot = gr.Chatbot(label="Chat History")
    with gr.Row():
        user_input = gr.Textbox(label="Your Message", placeholder="Type your question here...")
        submit_button = gr.Button("Send")

    # Handle user input
    submit_button.click(
        fn=chat_with_llm,
        inputs=[user_input, session_id],
        outputs=[chatbot],
    )

    # Clear button to reset the chat
    clear_button = gr.Button("Clear Chat")
    clear_button.click(
        fn=reset_chat,
        inputs=[session_id],
        outputs=[chatbot],
    )

# Launch the Gradio app
demo.launch(share=True, server_port=7866)