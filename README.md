# Invoice RAG System

A powerful Invoice Retrieval-Augmented Generation (RAG) system that uses OCR and AI to extract, process, and query invoice data efficiently.

## Features

- **PDF & Image Processing**: Supports both PDF invoices and image files (JPG, JPEG, PNG).
- **Tesseract OCR**: Uses Tesseract for invoice data extraction.
- **AI-Powered Financial Analysis**: Leverages Groq and Llama 3 to generate financial suggestions and reports.
- **Structured Data Extraction**: Automatically extracts key invoice information:
  - Invoice Number
  - Invoice Date
  - Total Amount
- **Database Storage**: SQLite database for storing and querying invoice data.
- **Command-Line Search**: A command-line interface to search for invoices.

## Prerequisites

- Python 3.8+
- Groq API key
- Tesseract OCR engine

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/daruoktab/hackathon.git
   cd hackathon/invoice_rag
   ```

2. **Install Tesseract:**
   Follow the installation instructions for your operating system from the [official Tesseract documentation](https://tesseract-ocr.github.io/tessdoc/Installation.html).

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   Create a `.env` file in the `invoice_rag` directory:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```

## Usage

### Processing Invoices and Generating Reports

The `main.py` script is the primary entry point for processing invoices and generating financial analysis. When you run it, it will:

1.  Scan the `invoice_rag/invoices` directory for new invoice files.
2.  Process each invoice using Tesseract OCR to extract key data.
3.  Store the extracted data in the `invoices.db` SQLite database.
4.  Use the Groq API and Llama 3 to generate:
    -   Financial suggestions based on the invoice data.
    -   A monthly financial report.

To run the main application:

```bash
python src/main.py
```

### Searching for Invoices

The `query.py` script provides a command-line interface to search for invoices in the database.

**Search by keyword (default):**

```bash
python src/query.py "search term"
```

**Search by invoice number:**

```bash
python src/query.py "INV-001" --by number
```

**Search by date:**

```bash
python src/query.py "2025-09-04" --by date
```

## Project Structure

```
invoice_rag/
├── src/
│   ├── __init__.py
│   ├── main.py          # Main application entry point
│   ├── ocr.py           # OCR and invoice processing
│   ├── database.py      # Database operations
│   └── query.py         # Command-line search interface
├── invoices/            # Directory for invoice files
├── invoices.db          # SQLite database
├── requirements.txt     # Python dependencies
└── .env                 # Environment variables (create this)
```

## API Reference

### `process_invoice(file_path)`

Processes an invoice file and extracts structured data using Tesseract OCR.

**Parameters:**
- `file_path` (str): Path to the invoice file (PDF or image)

**Returns:**
- JSON string containing extracted invoice data or None if processing fails.

**Supported Formats:**
- PDF files (.pdf)
- Image files (.jpg, .jpeg, .png)

### `extract_invoice_data_from_image(image)`

Extracts invoice data from a PIL Image using Tesseract OCR.

**Parameters:**
- `image` (PIL.Image): Image object to process

**Returns:**
- JSON string with extracted invoice information.

## Configuration

### Environment Variables

- `GROQ_API_KEY`: Your Groq API key (required).

## Dependencies

- `groq`: Groq API integration
- `python-dotenv`: Environment variable management
- `Pillow`: Image processing
- `pdf2image`: PDF to image conversion
- `SQLAlchemy`: Database ORM
- `pytesseract`: Python wrapper for Tesseract OCR

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source and available under the [MIT License](LICENSE).

## Support

For issues and questions, please open an issue on the GitHub repository.

## Roadmap

- [ ] Support for more invoice formats
- [ ] Enhanced data extraction capabilities
- [ ] Web interface
- [ ] Batch processing
- [ ] Export functionality
- [ ] Advanced querying features
