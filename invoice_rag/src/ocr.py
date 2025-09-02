import os
import re
import json
import pytesseract
from PIL import Image
from pdf2image import convert_from_path

# If Tesseract is not in your PATH, include the following line
# pytesseract.pytesseract.tesseract_cmd = r'<full_path_to_your_tesseract_executable>'
# Example for Windows:
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def pdf_to_images(pdf_path):
    """Converts a PDF file to a list of PIL Images."""
    try:
        return convert_from_path(pdf_path)
    except Exception as e:
        print(f"Error converting PDF to images: {e}")
        return None


def extract_invoice_data_from_image(image):
    """Extracts invoice data from a single image using Tesseract OCR."""
    try:
        # Use Tesseract to extract text from the image
        text = pytesseract.image_to_string(image)

        # Use regular expressions to find invoice details
        invoice_number_match = re.search(r'(?i)invoice\s*no[:\s#]*\s*([a-z0-9\-]+)', text)
        invoice_date_match = re.search(r'(?i)date[:\s]*\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})', text)
        total_amount_match = re.search(r'(?i)total\s*amount[:\s\$]*\s*([\d,]+\.\d{2})', text)

        invoice_data = {
            "invoice_number": invoice_number_match.group(1) if invoice_number_match else None,
            "invoice_date": invoice_date_match.group(1) if invoice_date_match else None,
            "total_amount": total_amount_match.group(1).replace(',', '') if total_amount_match else None,
        }

        return json.dumps(invoice_data, indent=4)

    except Exception as e:
        print(f"Error during OCR processing: {e}")
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
        # Process the first page of the PDF.
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