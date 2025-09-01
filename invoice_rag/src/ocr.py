
import os
from google.generativeai.client import configure
from google.generativeai.generative_models import GenerativeModel
from dotenv import load_dotenv
from PIL import Image
from pdf2image import convert_from_path

load_dotenv()

# Configure the Gemini API
if "GEMINI_API_KEY" not in os.environ:
    print("Please set the GEMINI_API_KEY environment variable in a .env file.")
    exit(1)

configure(api_key=os.environ["GEMINI_API_KEY"])


def pdf_to_images(pdf_path):
    """Converts a PDF file to a list of PIL Images."""
    try:
        return convert_from_path(pdf_path)
    except Exception as e:
        print(f"Error converting PDF to images: {e}")
        return None


def extract_invoice_data_from_image(image):
    """Extracts invoice data from a single image using Gemini."""
    model = GenerativeModel('gemini-2.5-flash-lite')
    prompt = """
    You are an expert in invoice data extraction.
    Extract the following information from the invoice image:
    - Invoice Number
    - Invoice Date
    - Total Amount

    Return the extracted information in a JSON format.
    Example:
    {
        "invoice_number": "12345",
        "invoice_date": "2024-01-01",
        "total_amount": "100.00"
    }
    """
    try:
        response = model.generate_content([prompt, image])
        return response.text
    except Exception as e:
        print(f"Error during Gemini API call: {e}")
        return None


def process_invoice(file_path):
    """Processes an invoice file (PDF or image) and extracts data."""
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return None

    file_extension = os.path.splitext(file_path)[1].lower()

    if file_extension == '.pdf':
        images = pdf_to_images(file_path)
        if not images:
            return None
        # For simplicity, we'll only process the first page of the PDF.
        # You can loop through all images if needed.
        return extract_invoice_data_from_image(images[0])
    elif file_extension in ['.jpg', '.jpeg', '.png']:
        try:
            image = Image.open(file_path)
            return extract_invoice_data_from_image(image)
        except Exception as e:
            print(f"Error opening image file: {e}")
            return None
    else:
        print(f"Unsupported file type: {file_extension}")
        return None
