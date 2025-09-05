# 🧾 Invoice Processing System

An AI-powered invoice processing system that extracts data from invoice images, stores it in a database, performs financial analysis, and provides AI-generated financial advice.

## 🚀 Features

- **📷 Image Processing**: Extract structured data from invoice images using Groq LLM
- **✅ Data Validation**: Pydantic models ensure data quality and type safety
- **💾 Database Storage**: SQLite database with relational schema for invoices and items
- **📊 Financial Analysis**: Weekly spending analysis, trends, and category breakdowns
- **🧠 AI Advisor**: Personalized financial advice based on spending patterns
- **🔍 Search & Query**: Advanced search capabilities for stored invoices

## 🔄 System Flow

```
Invoice Image → LLM Processing → Pydantic Validation → Database Storage → Analysis → AI Advice
```

## 📁 Project Structure

```
invoice_rag/
├── src/
│   ├── main.py          # Core processing pipeline
│   ├── database.py      # SQLAlchemy ORM models
│   ├── models.py        # Pydantic validation schemas
│   ├── analysis.py      # Financial analysis engine
│   ├── query.py         # Search interface
│   ├── ocr.py          # Text extraction utilities
│   └── __init__.py
├── view_database.py     # Database viewer script
├── requirements.txt     # Python dependencies
├── testgroq.py         # Original prototype (Groq LLM testing)
├── invoices.db         # SQLite database
├── .env.example        # Environment variables template
└── README.md           # This file
```

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd invoice_rag
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your GROQ_API_KEY
   ```

## 💻 Usage

### Process Invoice Images

```python
from src.main import process_single_image

# Process a single invoice
result = process_single_image('path/to/invoice.jpg')
```

### View Database Contents

```bash
python view_database.py
```

### Search Invoices

```python
from src.query import InvoiceSearcher
from src.database import get_db_session

session = get_db_session()
searcher = InvoiceSearcher(session)

# Search by shop name
results = searcher.search_invoices(shop_name="Indomaret")
```

### Financial Analysis

```python
from src.analysis import analyze_weekly_spending
from src.database import get_db_session

session = get_db_session()
analysis = analyze_weekly_spending(session)
```

## 📊 Database Schema

### Invoices Table
- `id` - Primary key
- `shop_name` - Store name
- `shop_address` - Store address
- `invoice_number` - Invoice number
- `invoice_date` - Transaction date
- `invoice_time` - Transaction time
- `total_amount` - Total amount
- `subtotal` - Subtotal
- `tax` - Tax amount
- `discount` - Discount amount
- `payment_method` - Payment method
- `cashier` - Cashier name
- `image_path` - Original image path
- `processed_at` - Processing timestamp

### Invoice Items Table
- `id` - Primary key
- `invoice_id` - Foreign key to invoices
- `name` - Item name
- `quantity` - Item quantity
- `unit_price` - Price per unit
- `total_price` - Total price for item

## 🧠 AI Features

- **Weekly Analysis**: Calculate spending averages and trends
- **Category Insights**: Identify biggest spending categories
- **Financial Advice**: AI-generated budget recommendations
- **Pattern Recognition**: Detect shopping frequency patterns

## 🔧 Configuration

### Environment Variables
- `GROQ_API_KEY` - Required for LLM processing

### Supported Image Formats
- JPG/JPEG
- PNG

## 📦 Dependencies

- `groq` - LLM API client
- `pydantic` - Data validation
- `sqlalchemy` - ORM
- `pillow` - Image processing
- `python-dotenv` - Environment variables

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions, please open an issue in the repository.
