# 🧾 Invoice Processing System

An AI-powered invoice processing system that extracts structured data from invoice images, stores it in a database, performs financial analysis, and provides AI-generated financial advice.

## 🚀 Features

- **📷 AI Vision Processing**: Extract data from invoice images using Groq LLM
- **✅ Data Validation**: Pydantic models ensure data quality and type safety  
- **💾 Database Storage**: SQLite database with relational schema
- **📊 Financial Analysis**: Weekly spending analysis, trends, and insights
- **🧠 AI Financial Advisor**: Personalized budget recommendations
- **🔍 Advanced Search**: Query and filter stored invoices

## � Project Structure

```
hackathon/
├── invoice_rag/           # Main invoice processing system
│   ├── src/
│   │   ├── main.py        # Core processing pipeline
│   │   ├── database.py    # SQLAlchemy ORM models
│   │   ├── models.py      # Pydantic validation schemas
│   │   ├── analysis.py    # Financial analysis engine
│   │   ├── query.py       # Search interface
│   │   └── ocr.py        # Text extraction utilities
│   ├── view_database.py   # Database viewer script
│   ├── testgroq.py       # Original LLM prototype
│   ├── requirements.txt   # Dependencies
│   ├── .env.example      # Environment template
│   └── README.md         # Detailed documentation
├── test1.jpg             # Sample invoice images
├── test2.jpg
├── test3.jpg
├── test4.jpg
└── README.md             # This file
```

## 🛠️ Quick Start

1. **Navigate to the invoice system**
   ```bash
   cd invoice_rag
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment**
   ```bash
   cp .env.example .env
   # Edit .env and add your GROQ_API_KEY
   ```

4. **Process invoices**
   ```python
   from src.main import process_single_image
   result = process_single_image('../test1.jpg')
   ```

5. **View results**
   ```bash
   python view_database.py
   ```

## 🔄 System Flow

```
Invoice Image → LLM Processing → Pydantic Validation → Database Storage → Analysis → AI Advice
```

## � Usage Examples

### Process Invoice
```python
from src.main import process_single_image
result = process_single_image('path/to/invoice.jpg')
```

### View Database
```bash
python view_database.py
```

### Search Invoices
```python
from src.query import InvoiceSearcher
from src.database import get_db_session

session = get_db_session()
searcher = InvoiceSearcher(session)
results = searcher.search_invoices(shop_name="Indomaret")
```

### Financial Analysis
```python
from src.analysis import analyze_weekly_spending
analysis = analyze_weekly_spending(session)
```

## 📊 Key Features

- **AI-Powered**: Uses Groq's Meta-llama model for accurate data extraction
- **Validated Data**: Pydantic schemas ensure data quality
- **Relational Storage**: Proper database design with foreign key relationships
- **Financial Insights**: Weekly averages, trends, and spending patterns
- **Smart Advisor**: AI-generated financial advice based on spending data

## 🔧 Configuration

### Required Environment Variables
- `GROQ_API_KEY` - Your Groq API key for LLM processing

### Supported Formats
- JPG/JPEG images
- PNG images
- Indonesian invoice formats

## 📈 Analysis Capabilities

- Weekly spending averages
- Spending trend identification (increasing/decreasing)
- Biggest spending categories
- Shop frequency analysis
- Payment method preferences
- AI-powered financial advice

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## � License

This project is licensed under the MIT License.

## 📞 Support

For detailed documentation and usage examples, see the `invoice_rag/README.md` file.

For issues and questions, please open an issue in the repository.
