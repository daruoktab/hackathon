

import os
import json
from . import ocr
from . import database

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
                    # The output from Gemini might be in a markdown format
                    # like ```json\n...\n```, so we need to clean it up.
                    if extracted_data_str.startswith("```json"):
                        extracted_data_str = extracted_data_str[7:-3].strip()

                    extracted_data = json.loads(extracted_data_str)
                    database.insert_invoice_data(db_session, extracted_data, file_path)
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON from Gemini response: {e}")
                    print(f"Raw response:\n{extracted_data_str}")
            else:
                print(f"Could not extract data from {filename}")

if __name__ == '__main__':
    main()

