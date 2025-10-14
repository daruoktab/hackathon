import os
import json
from groq import Groq
from dotenv import load_dotenv
from typing import List, Dict, Any, cast, Iterable
from groq.types.chat.chat_completion_message_param import ChatCompletionMessageParam
from groq.types.chat.chat_completion_tool_param import ChatCompletionToolParam
from src.analysis import (
    analyze_invoices,
    analyze_spending_trends,
    find_biggest_spending_categories,
    generate_comprehensive_analysis,
)

# Load environment variables
load_dotenv()

# Initialize Groq client
groq_api_key = os.environ.get("GROQ_API_KEY")
if not groq_api_key:
    raise ValueError("GROQ_API_KEY not found in environment variables")

client = Groq(api_key=groq_api_key)

# --- System Prompt in English ---
SYSTEM_PROMPT = """
You are a "Financial Assistant", a friendly and helpful AI chatbot. Your goal is to help users understand their spending by analyzing their invoice data.

MAIN RULES:
1.  **Always Speak in English**: Communicate exclusively in natural and polite English.
2.  **Focus on Data**: Your answers should be based on available functions. Don't make up information or provide financial advice beyond the given data.
3.  **Use Available Functions**: To answer user questions, call relevant functions. Don't answer if there's no suitable function.
4.  **Greet Users**: Start each conversation with a friendly greeting, for example, "Hello! How can I help you with your spending today?"
5.  **Clarify if Needed**: If the user's request is unclear, ask clarifying questions. Example: "For what time period would you like to see your spending summary?"
6.  **Be Concise and Clear**: Present data in an easy-to-read format. Use bullet points or brief summaries.
7.  **Don't Give Financial Advice**: You are a data analyst, not a financial advisor. Avoid making recommendations or giving advice.
"""

# --- Tools Definition (Function Calling) ---
tools: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "get_invoice_summary",
            "description": "Get a general summary of all invoices, including total spending and number of invoices.",
            "parameters": {
                "type": "object",
                "properties": {
                    "weeks_back": {
                        "type": "integer",
                        "description": "Number of weeks back to analyze (e.g., 4 for last month). If not specified, will analyze all data.",
                    }
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_spending_trends",
            "description": "Analyze spending trends over recent weeks to see if spending is increasing, decreasing, or stable.",
            "parameters": {
                "type": "object",
                "properties": {
                    "weeks_back": {
                        "type": "integer",
                        "default": 4,
                        "description": "Number of weeks to analyze, default is 4.",
                    }
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_top_spending_categories",
            "description": "Find out where the user spends the most money, sorted by store or vendor.",
            "parameters": {
                "type": "object",
                "properties": {
                    "weeks_back": {
                        "type": "integer",
                        "description": "Number of weeks back to analyze. If not specified, will analyze all data.",
                    }
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_comprehensive_analysis",
            "description": "Get a complete and comprehensive financial analysis report for a specific time period.",
            "parameters": {
                "type": "object",
                "properties": {
                    "weeks_back": {
                        "type": "integer",
                        "default": 4,
                        "description": "Number of weeks to analyze, default is 4.",
                    }
                },
                "required": [],
            },
        },
    },
]

# --- Function Mapping ---
AVAILABLE_FUNCTIONS = {
    "get_invoice_summary": analyze_invoices,
    "get_spending_trends": analyze_spending_trends,
    "get_top_spending_categories": find_biggest_spending_categories,
    "get_comprehensive_analysis": generate_comprehensive_analysis,
}


def run_conversation(user_message: str, chat_history: List[Dict[str, Any]] | None = None) -> str:
    """
    Runs a conversation with the LLM, including function calling.
    """
    if chat_history is None:
        chat_history = []

    messages: List[Dict[str, Any]] = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(chat_history)
    messages.append({"role": "user", "content": user_message})

    try:
        # First API call to get the tool choice
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=cast(Iterable[ChatCompletionMessageParam], messages),
            tools=cast(Iterable[ChatCompletionToolParam], tools),
            tool_choice="auto",
        )

        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        # If the model wants to call a function
        if tool_calls:
            messages.append(response_message.model_dump(exclude_unset=True))  # Extend conversation with assistant's reply

            # Execute all tool calls
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_to_call = AVAILABLE_FUNCTIONS.get(function_name)

                if function_to_call:
                    function_args = json.loads(tool_call.function.arguments)

                    # Call the function with arguments
                    function_response = function_to_call(**function_args)

                    # Append the function response to the conversation
                    messages.append(
                        {
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": json.dumps(function_response, indent=2),
                        }
                    )
                else:
                    # Handle case where function is not found
                    messages.append(
                        {
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": f'{{"error": "Function {function_name} not found."}}',
                        }
                    )

            # Second API call to get the final response
            final_response = client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=cast(Iterable[ChatCompletionMessageParam], messages),
            )

            return final_response.choices[0].message.content or ""
        else:
            # If no tool is called, return the direct response
            return response_message.content or ""

    except Exception as e:
        print(f"An error occurred: {e}")
        return "Maaf, terjadi kesalahan saat memproses permintaan Anda. Silakan coba lagi."


# Example of how to use it
if __name__ == "__main__":
    # Simulate a conversation
    chat_history: List[Dict[str, Any]] = []

    print("Chatbot: Halo! Ada yang bisa saya bantu terkait pengeluaran Anda?")

    # User asks a question
    user_input = "Berapa total pengeluaranku selama ini?"
    print(f"User: {user_input}")

    # Get chatbot response
    response_text = run_conversation(user_input, chat_history)
    print(f"Chatbot: {response_text}")

    # Update history
    chat_history.append({"role": "user", "content": user_input})
    if response_text:
        chat_history.append({"role": "assistant", "content": response_text})

    # User asks another question
    user_input = "Tunjukkan tren pengeluaranku selama 4 minggu terakhir."
    print(f"User: {user_input}")

    response_text = run_conversation(user_input, chat_history)
    print(f"Chatbot: {response_text}")
