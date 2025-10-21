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
from src.database import get_db_session, Invoice
from telegram_bot.spending_limits import get_monthly_limit

# Load environment variables
load_dotenv()

# Initialize Groq client
groq_api_key = os.environ.get("GROQ_API_KEY")
if not groq_api_key:
    raise ValueError("GROQ_API_KEY not found in environment variables")

client = Groq(api_key=groq_api_key)

# Model configuration
CHAT_MODEL = os.environ.get("CHAT_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct")

# --- System Prompt in English ---
SYSTEM_PROMPT = """
You are a "UrFinance", a friendly AI chatbot expense tracker. Your goal is to help users understand their spending by analyzing their invoice data.

MAIN RULES:
1.  **Always Speak in English**: Communicate exclusively in natural and polite English.
2.  **Focus on Data**: Your answers should be based on available functions. Don't make up information or provide financial advice beyond the given data.
3.  **Use Available Functions**: To answer user questions, call relevant functions. Available functions include:
    - Invoice summaries and analysis
    - Spending trends and patterns
    - Recent invoices list
    - Budget/spending limit status
    - Visual charts and graphs (via /visualizations command)
4.  **Greet Users**: Start each conversation with a friendly greeting, for example, "Hello! How can I help you with your spending today?"
5.  **Clarify if Needed**: If the user's request is unclear, ask clarifying questions. Example: "For what time period would you like to see your spending summary?"
6.  **Be Concise and Clear**: Present data in an easy-to-read format. Use bullet points or brief summaries.
7.  **Don't Give Financial Advice**: You are a data analyst, not a financial advisor. Avoid making recommendations or giving advice.
8.  **Guide to Commands**: When users want to see visualizations/charts, or upload invoices, guide them to use the appropriate commands (/visualizations, /analysis, /upload_invoice, etc.).
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
    {
        "type": "function",
        "function": {
            "name": "get_recent_invoices_list",
            "description": "Get a list of the most recent invoices/receipts. Shows the last 5 invoices with date, shop name, and amount.",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "default": 5,
                        "description": "Number of recent invoices to retrieve, default is 5.",
                    }
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_spending_limit_status",
            "description": "Check the user's monthly spending limit status, including how much they've spent, remaining budget, and percentage used.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "integer",
                        "default": 0,
                        "description": "User ID (optional, defaults to 0 for single-user mode).",
                    }
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_visualization_available",
            "description": "Check if visual charts and graphs are available. Use this when the user asks to 'see' or 'show' charts, graphs, or visual analysis.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]

# --- Helper Functions for Bot Commands ---
def get_recent_invoices_list(limit: int = 5) -> Dict[str, Any]:
    """Get a list of recent invoices."""
    try:
        session = get_db_session()
        invoices = session.query(Invoice).order_by(Invoice.processed_at.desc()).limit(limit).all()
        
        if not invoices:
            return {"success": False, "message": "No invoices found in the database."}
        
        invoice_list = []
        for inv in invoices:
            invoice_list.append({
                "date": inv.invoice_date or "Unknown date",
                "shop": inv.shop_name,
                "amount": f"Rp {inv.total_amount:,.2f}"
            })
        
        return {"success": True, "invoices": invoice_list, "count": len(invoice_list)}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_spending_limit_status(user_id: int = 0) -> Dict[str, Any]:
    """Get the current spending limit status."""
    try:
        monthly_limit = get_monthly_limit(user_id)
        if not monthly_limit:
            return {"success": False, "message": "No spending limit set. User should use /set_limit to set one."}
        
        analysis = analyze_invoices()
        total_spent = analysis['total_spent']
        
        percentage_used = (total_spent / monthly_limit) * 100
        remaining = monthly_limit - total_spent
        
        # Determine status
        if percentage_used >= 100:
            status = "Over limit"
        elif percentage_used >= 90:
            status = "Near limit"
        elif percentage_used >= 75:
            status = "Getting close"
        else:
            status = "Good standing"
        
        return {
            "success": True,
            "monthly_limit": f"Rp {monthly_limit:,.2f}",
            "total_spent": f"Rp {total_spent:,.2f}",
            "remaining": f"Rp {remaining:,.2f}",
            "percentage_used": f"{percentage_used:.1f}%",
            "status": status
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_visualization_available() -> Dict[str, Any]:
    """Check if visualization is available and provide guidance."""
    return {
        "success": True,
        "message": "A comprehensive visual dashboard is available! Ask the user to type /visualizations or /analysis to see charts and graphs of their spending patterns.",
        "available_visualizations": [
            "Monthly spending trends",
            "Top spending categories",
            "Spending by vendor",
            "Weekly spending patterns"
        ]
    }


# --- Function Mapping ---
AVAILABLE_FUNCTIONS = {
    "get_invoice_summary": analyze_invoices,
    "get_spending_trends": analyze_spending_trends,
    "get_top_spending_categories": find_biggest_spending_categories,
    "get_comprehensive_analysis": generate_comprehensive_analysis,
    "get_recent_invoices_list": get_recent_invoices_list,
    "get_spending_limit_status": get_spending_limit_status,
    "get_visualization_available": get_visualization_available,
}


def run_conversation(user_message: str, chat_history: List[Dict[str, Any]] | None = None) -> str:
    """
    Runs a conversation with the LLM, including multi-turn function calling.
    Supports calling multiple tools sequentially for complex queries.
    """
    if chat_history is None:
        chat_history = []

    messages: List[Dict[str, Any]] = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(chat_history)
    messages.append({"role": "user", "content": user_message})

    MAX_ITERATIONS = 5  # Prevent infinite loops

    try:
        for iteration in range(MAX_ITERATIONS):
            # API call to get response (may include tool calls)
            response = client.chat.completions.create(
                model=CHAT_MODEL,
                messages=cast(Iterable[ChatCompletionMessageParam], messages),
                tools=cast(Iterable[ChatCompletionToolParam], tools),
                tool_choice="auto",
            )

            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls

            # If no tool calls, we have the final response
            if not tool_calls:
                return response_message.content or ""

            # Model wants to call functions
            messages.append(response_message.model_dump(exclude_unset=True))

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

            # Continue loop to let model process tool results

        # If we hit max iterations, return a message
        return "I apologize, but I need to break down your request into smaller parts. Could you ask about one thing at a time?"

    except Exception as e:
        print(f"An error occurred: {e}")
        return "Sorry, there was an error processing your request. Please try again."


# Example of how to use it
if __name__ == "__main__":
    # Simulate a conversation
    chat_history: List[Dict[str, Any]] = []

    print("Chatbot: Hello! How can I assist you with your expenses today?")

    # User asks a question
    user_input = "What is my total spending so far?"
    print(f"User: {user_input}")

    # Get chatbot response
    response_text = run_conversation(user_input, chat_history)
    print(f"Chatbot: {response_text}")

    # Update history
    chat_history.append({"role": "user", "content": user_input})
    if response_text:
        chat_history.append({"role": "assistant", "content": response_text})

    # User asks another question
    user_input = "Show me my spending trend for the last 4 weeks."
    print(f"User: {user_input}")

    response_text = run_conversation(user_input, chat_history)
    print(f"Chatbot: {response_text}")
