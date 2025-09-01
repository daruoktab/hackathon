# Invoice RAG System

A powerful Invoice Retrieval-Augmented Generation (RAG) system that uses OCR and AI to extract, process, and query invoice data efficiently.

## Features

- **PDF & Image Processing**: Supports both PDF invoices and image files (JPG, JPEG, PNG)
- **AI-Powered OCR**: Uses Google Gemini AI for intelligent invoice data extraction
- **Structured Data Extraction**: Automatically extracts key invoice information:
  - Invoice Number
  - Invoice Date
  - Total Amount
- **Database Storage**: SQLite database for storing and querying invoice data
- **RAG Capabilities**: Advanced querying and retrieval of invoice information

## Prerequisites

- Python 3.8+
- Google Gemini API key
- Required system dependencies for PDF processing

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/daruoktab/hackathon.git
   cd hackathon/invoice_rag
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   Create a `.env` file in the `invoice_rag` directory:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

## Usage

### Basic Invoice Processing

```python
from src.ocr import process_invoice

# Process a PDF invoice
result = process_invoice("path/to/invoice.pdf")

# Process an image invoice
result = process_invoice("path/to/invoice.jpg")
```

### Database Operations

```python
from src.database import InvoiceDatabase

# Initialize database
db = InvoiceDatabase()

# Add invoice data
db.add_invoice(invoice_data)

# Query invoices
results = db.query_invoices("invoice_number = '12345'")
```

### Running the Main Application

```bash
python src/main.py
```

## Project Structure

```
invoice_rag/
├── src/
│   ├── __init__.py
│   ├── main.py          # Main application entry point
│   ├── ocr.py           # OCR and invoice processing
│   ├── database.py      # Database operations
│   └── query.py         # Query interface
├── invoices/            # Directory for invoice files
├── invoices.db          # SQLite database
├── requirements.txt     # Python dependencies
└── .env                 # Environment variables (create this)
```

## API Reference

### `process_invoice(file_path)`

Processes an invoice file and extracts structured data.

**Parameters:**
- `file_path` (str): Path to the invoice file (PDF or image)

**Returns:**
- JSON string containing extracted invoice data or None if processing fails

**Supported Formats:**
- PDF files (.pdf)
- Image files (.jpg, .jpeg, .png)

### `extract_invoice_data_from_image(image)`

Extracts invoice data from a PIL Image using Gemini AI.

**Parameters:**
- `image` (PIL.Image): Image object to process

**Returns:**
- JSON string with extracted invoice information

## Configuration

### Gemini AI Model

The system uses `gemini-2.5-flash-lite` for optimal performance and cost-effectiveness. You can modify the model in `src/ocr.py`:

```python
model = GenerativeModel('gemini-2.5-flash-lite')
```

### Environment Variables

- `GEMINI_API_KEY`: Your Google Gemini API key (required)

## Dependencies

- `google-generativeai`: Google Gemini AI integration
- `python-dotenv`: Environment variable management
- `Pillow`: Image processing
- `pdf2image`: PDF to image conversion
- `SQLAlchemy`: Database ORM

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
