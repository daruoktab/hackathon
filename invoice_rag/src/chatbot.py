import os
import json
from groq import Groq
from dotenv import load_dotenv
from typing import List, Dict, Any, Callable

# Load environment variables
load_dotenv()

# Import analysis functions
from src.analysis import (
    analyze_invoices,
    calculate_weekly_averages,
    analyze_spending_trends,
    find_biggest_spending_categories,
    analyze_item_spending,
    analyze_transaction_types,
    generate_comprehensive_analysis,
)

# Initialize Groq client
groq_api_key = os.environ.get("GROQ_API_KEY")
if not groq_api_key:
    raise ValueError("GROQ_API_KEY not found in environment variables")

client = Groq(api_key=groq_api_key)

# --- System Prompt in Bahasa Indonesia ---
SYSTEM_PROMPT = """
Anda adalah "Asisten Keuangan", chatbot AI yang ramah dan membantu. Tujuan Anda adalah membantu pengguna memahami pengeluaran mereka dengan menganalisis data invoice mereka.

PERATURAN UTAMA:
1.  **Selalu Berbahasa Indonesia**: Berkomunikasi secara eksklusif dalam Bahasa Indonesia yang alami dan sopan.
2.  **Fokus pada Data**: Jawaban Anda harus didasarkan pada fungsi yang tersedia. Jangan membuat informasi atau memberikan saran keuangan di luar data yang diberikan.
3.  **Gunakan Fungsi yang Ada**: Untuk menjawab pertanyaan pengguna, panggil fungsi yang relevan. Jangan menjawab jika tidak ada fungsi yang sesuai.
4.  **Sapa Pengguna**: Mulai setiap percakapan dengan sapaan ramah, misalnya, "Halo! Ada yang bisa saya bantu terkait pengeluaran Anda?"
5.  **Klarifikasi jika Perlu**: Jika permintaan pengguna tidak jelas, ajukan pertanyaan untuk klarifikasi. Contoh: "Untuk periode berapa lama Anda ingin melihat ringkasan pengeluaran?"
6.  **Ringkas dan Jelas**: Sajikan data dalam format yang mudah dibaca. Gunakan daftar (bullet points) atau ringkasan singkat.
7.  **Jangan Memberi Nasihat Finansial**: Anda hanya seorang analis data, bukan penasihat keuangan. Hindari memberikan rekomendasi atau nasihat.
"""

# --- Tools Definition (Function Calling) ---
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_invoice_summary",
            "description": "Dapatkan ringkasan umum dari semua invoice, seperti total pengeluaran dan jumlah invoice.",
            "parameters": {
                "type": "object",
                "properties": {
                    "weeks_back": {
                        "type": "integer",
                        "description": "Jumlah minggu ke belakang untuk dianalisis (misal: 4 untuk 1 bulan terakhir). Jika tidak diisi, akan menganalisis semua data.",
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
            "description": "Analisis tren pengeluaran selama beberapa minggu terakhir untuk melihat apakah pengeluaran naik, turun, atau stabil.",
            "parameters": {
                "type": "object",
                "properties": {
                    "weeks_back": {
                        "type": "integer",
                        "default": 4,
                        "description": "Jumlah minggu untuk dianalisis, defaultnya 4.",
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
            "description": "Cari tahu di mana pengguna paling banyak menghabiskan uang, diurutkan berdasarkan toko atau vendor.",
            "parameters": {
                "type": "object",
                "properties": {
                    "weeks_back": {
                        "type": "integer",
                        "description": "Jumlah minggu ke belakang untuk dianalisis. Jika tidak diisi, akan menganalisis semua data.",
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
            "description": "Dapatkan laporan analisis keuangan yang lengkap dan komprehensif untuk periode waktu tertentu.",
            "parameters": {
                "type": "object",
                "properties": {
                    "weeks_back": {
                        "type": "integer",
                        "default": 4,
                        "description": "Jumlah minggu untuk dianalisis, defaultnya 4.",
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


def run_conversation(user_message: str, chat_history: List[Dict[str, str]] = None) -> str:
    """
    Runs a conversation with the LLM, including function calling.
    """
    if chat_history is None:
        chat_history = []

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(chat_history)
    messages.append({"role": "user", "content": user_message})

    try:
        # First API call to get the tool choice
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )

        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        # If the model wants to call a function
        if tool_calls:
            messages.append(response_message)  # Extend conversation with assistant's reply

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
                messages=messages,
            )

            return final_response.choices[0].message.content
        else:
            # If no tool is called, return the direct response
            return response_message.content

    except Exception as e:
        print(f"An error occurred: {e}")
        return "Maaf, terjadi kesalahan saat memproses permintaan Anda. Silakan coba lagi."


# Example of how to use it
if __name__ == "__main__":
    # Simulate a conversation
    chat_history = []

    print("Chatbot: Halo! Ada yang bisa saya bantu terkait pengeluaran Anda?")

    # User asks a question
    user_input = "Berapa total pengeluaranku selama ini?"
    print(f"User: {user_input}")

    # Get chatbot response
    response_text = run_conversation(user_input, chat_history)
    print(f"Chatbot: {response_text}")

    # Update history
    chat_history.append({"role": "user", "content": user_input})
    chat_history.append({"role": "assistant", "content": response_text})

    # User asks another question
    user_input = "Tunjukkan tren pengeluaranku selama 4 minggu terakhir."
    print(f"User: {user_input}")

    response_text = run_conversation(user_input, chat_history)
    print(f"Chatbot: {response_text}")
