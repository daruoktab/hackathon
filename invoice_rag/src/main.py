

import os
import json
from . import ocr
from . import database
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Configure the Groq API
groq_api_key = os.environ.get("GROQ_API_KEY")
client = None

if not groq_api_key or groq_api_key == "YOUR_GROQ_API_KEY":
    print("Please set the GROQ_API_KEY environment variable in your .env file.")
else:
    try:
        client = Groq(api_key=groq_api_key)
    except Exception as e:
        print(f"Error initializing Groq client: {e}")


def generate_response(prompt):
    """Generates a response from the Llama 4 model on Groq."""
    if not client:
        return "Groq client not initialized. Please check your API key."

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama3-8b-8192", # Or another Llama 4 model when available
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Error during Groq API call: {e}"

def get_financial_suggestions(invoice_data):
    """Generates financial suggestions based on invoice data."""
    prompt = f"""
    Based on the following invoice data, provide some financial suggestions.
    The data is a list of dictionaries, where each dictionary represents an invoice.
    Data: {invoice_data}

    Suggestions:
    """
    return generate_response(prompt)

def generate_report(invoice_data, period="monthly"):
    """Generates a financial report based on invoice data."""
    prompt = f"""
    Based on the following invoice data, generate a {period} financial report.
    The data is a list of dictionaries, where each dictionary represents an invoice.
    Data: {invoice_data}

    Report:
    """
    return generate_response(prompt)

def main():
    """Main function to process invoices and store data."""
    invoice_dir = os.path.join('invoice_rag', 'invoices')
    db_path = os.path.join('invoice_rag', 'invoices.db')
    db_session = database.get_db_session(db_path)

    for filename in os.listdir(invoice_dir):
        file_path = os.path.join(invoice_dir, filename)
        if os.path.isfile(file_path):
            print(f"Processing invoice: {filename}")
            extracted_data_str = ocr.process_invoice(file_path)

            if extracted_data_str:
                try:
                    # The output from Tesseract is a JSON string
                    extracted_data = json.loads(extracted_data_str)
                    database.insert_invoice_data(db_session, extracted_data, file_path)
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON from Tesseract response: {e}")
                    print(f"Raw response:\n{extracted_data_str}")
            else:
                print(f"Could not extract data from {filename}")

    # Get all invoices from the database
    all_invoices = database.get_all_invoices(db_session)
    invoice_data_for_llm = [
        {
            "invoice_number": inv.invoice_number,
            "invoice_date": inv.invoice_date,
            "total_amount": inv.total_amount,
        }
        for inv in all_invoices
    ]

    if invoice_data_for_llm:
        print("\n--- Generating Financial Suggestions ---")
        suggestions = get_financial_suggestions(invoice_data_for_llm)
        print(suggestions)

        print("\n--- Generating Monthly Report ---")
        report = generate_report(invoice_data_for_llm)
        print(report)
    else:
        print("\nNo invoice data to process for suggestions and reports.")


if __name__ == '__main__':
    main()

