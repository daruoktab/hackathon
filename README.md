# 🧾 AI Invoice Processing System

A comprehensive AI-powered invoice processing system that extracts structured data from invoice images, stores it in a database, performs financial analysis, and provides both web UI and programmatic interfaces.

## 🚀 Features

### Core Processing
- **🤖 AI-Powered OCR**: Extract structured data from invoice images using Groq LLM (Meta-Llama models)
- **✅ Data Validation**: Pydantic v2 models with robust date/time formatting and field validation
- **🔄 Batch Processing**: Process individual invoices or entire directories
- **📷 Multi-Format Support**: JPG, JPEG, PNG image formats

### Data Management
- **💾 SQLite Database**: Relational schema with invoices and invoice_items tables
- **🔍 Advanced Search**: Filter by shop, date range, amount, and text search
- **📊 Data Export**: CSV and JSON export capabilities
- **🛠️ Database Tools**: Cleanup, backup, and maintenance utilities

### Analytics & Insights
- **📈 Financial Analytics**: Weekly/monthly spending analysis and trends
- **🧠 AI Financial Advisor**: Personalized budget recommendations and insights
- **📊 Visual Dashboards**: Interactive charts and spending patterns
- **🏪 Shop Analysis**: Visit frequency, spending patterns, and comparisons

### User Interfaces
- **🌐 Streamlit Web App**: Full-featured web interface with multiple pages
- **💻 Command Line**: Direct Python API and CLI tools
- **📱 Responsive Design**: Works on desktop and mobile devices

## 📁 Project Structure

```
hackathon/
├── README.md                      # This comprehensive guide
├── .gitignore                     # Git ignore rules
├── .vscode/                       # VS Code settings
└── invoice_rag/                   # Main application directory
    ├── 📋 Core System
    │   ├── src/
    │   │   ├── processor.py       # 🤖 Main invoice processing engine
    │   │   ├── database.py        # 💾 Database models and utilities
    │   │   ├── analysis.py        # 📊 Financial analysis engine
    │   │   └── __init__.py        # Package initialization
    │   ├── requirements.txt       # 📦 Python dependencies
    │   ├── .env.example          # 🔧 Environment template
    │   └── invoices.db           # 💽 SQLite database
    │
    ├── 🌐 Web Interface
    │   └── streamlit/
    │       └── app.py            # Full-featured Streamlit web app
    │
    ├── 🛠️ Utilities
    │   ├── run.py                # 🏃 Simple runner script
    │   ├── cleanup.py            # 🧹 Database cleanup tool
    │   ├── testgroq.py          # 🧪 Groq API testing
    │   └── view_database.py      # 👀 Database viewer (ASCII output)
    │
    └── 📂 Data
        └── invoices/             # 📁 Input directory for invoice images
            ├── test1.jpg         # 🖼️ Sample invoice images
            ├── test2.jpg
            ├── test3.jpg
            └── test4.jpg
```

## 🛠️ Installation & Setup

### 1. Clone & Navigate
```bash
git clone <your-repo-url>
cd hackathon/invoice_rag
```

### 2. Install Dependencies
```bash
# Using pip
pip install -r requirements.txt

# Using uv (faster)
uv pip install -r requirements.txt

# Using conda
conda create -n invoice_ai python=3.12
conda activate invoice_ai
pip install -r requirements.txt
```

### 3. Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API key
echo "GROQ_API_KEY=your_groq_api_key_here" > .env
```

### 4. Get Groq API Key
1. Visit [Groq Console](https://console.groq.com/)
2. Create account and generate API key
3. Add key to `.env` file

## 🚀 Quick Start

### Web Interface (Recommended)
```bash
streamlit run streamlit/app.py
```
Access at: `http://localhost:8501`

**Web App Features:**
- 📤 **Upload & Process**: Drag-drop invoice images for instant processing
- 📊 **Dashboard**: Overview metrics and spending analytics  
- 📋 **View Invoices**: Enhanced table, card, and detail views with pagination
- 🔍 **Search & Filter**: Advanced filtering by shop, date, amount, and text
- 📈 **Data Analytics**: Interactive charts, spending patterns, item analysis
- ⚙️ **Data Management**: Database maintenance, export, and quality checks

### Command Line Processing
```python
# Process single invoice
from src.processor import process_invoice_with_llm, save_to_database_robust
invoice_data = process_invoice_with_llm('path/to/invoice.jpg')
save_to_database_robust(invoice_data, 'path/to/invoice.jpg')

# View database contents
python view_database.py

# Test Groq API connection
python testgroq.py
```

### Batch Processing
```bash
# Process all images in invoices/ directory
python run.py

# Or programmatically
from src.processor import process_invoice_directory
process_invoice_directory('invoices/')
```

## 📊 Database Schema

### Invoices Table
| Field | Type | Description |
|-------|------|-------------|
| `id` | INTEGER | Primary key |
| `shop_name` | TEXT | Store name |
| `shop_address` | TEXT | Store address |
| `invoice_number` | TEXT | Invoice number |
| `invoice_date` | TEXT | Date (YYYY-MM-DD format) |
| `invoice_time` | TEXT | Time (HH:MM format, 24-hour) |
| `total_amount` | REAL | Total amount |
| `subtotal` | REAL | Subtotal amount |
| `tax` | REAL | Tax amount |
| `discount` | REAL | Discount amount |
| `payment_method` | TEXT | Payment method |
| `cashier` | TEXT | Cashier name |
| `image_path` | TEXT | Original image path |
| `processed_at` | TEXT | Processing timestamp |

### Invoice Items Table
| Field | Type | Description |
|-------|------|-------------|
| `id` | INTEGER | Primary key |
| `invoice_id` | INTEGER | Foreign key to invoices |
| `item_name` | TEXT | Item name |
| `quantity` | INTEGER | Item quantity |
| `unit_price` | REAL | Price per unit |
| `total_price` | REAL | Total price for item |

## 🤖 AI Processing Pipeline

```mermaid
graph LR
    A[Invoice Image] --> B[Base64 Encoding]
    B --> C[Groq LLM Processing]
    C --> D[JSON Extraction]
    D --> E[Pydantic Validation]
    E --> F[Date/Time Standardization]
    F --> G[SQLite Storage]
    G --> H[Financial Analysis]
    H --> I[Web Interface / API]
```

**Processing Features:**
- **Smart Date/Time Parsing**: Handles various Indonesian date formats
- **Robust Validation**: Pydantic v2 with field validators
- **Error Recovery**: Graceful handling of parsing failures
- **Standardization**: Consistent YYYY-MM-DD and HH:MM formats

## 📈 Analytics & Insights

### Financial Analysis
- **📊 Spending Trends**: Daily, weekly, monthly analysis
- **🏪 Shop Insights**: Frequency vs. spending analysis
- **🛒 Item Analysis**: Most purchased items and spending patterns
- **📅 Time Patterns**: Weekday vs. weekend, hourly shopping patterns

### AI-Powered Insights
- **💡 Budget Recommendations**: Based on spending patterns
- **⚠️ Anomaly Detection**: Unusual spending alerts  
- **📈 Trend Predictions**: Spending forecast and trends
- **🎯 Goal Tracking**: Budget vs. actual spending analysis

## 🔧 Advanced Usage

### Custom Processing
```python
from src.processor import RobustInvoice, process_invoice_with_llm
from src.database import create_tables, get_db_connection

# Initialize database
create_tables()

# Process with custom validation
invoice_data = process_invoice_with_llm('invoice.jpg')
validated_invoice = RobustInvoice(**invoice_data)

# Custom database operations
conn = get_db_connection()
# Your custom queries here
```

### API Integration
```python
# Search invoices
from src.database import search_invoices
results = search_invoices(
    shop_name="Indomaret",
    date_range=("2024-01-01", "2024-12-31"),
    amount_range=(10000, 100000)
)

# Financial analysis
from src.analysis import analyze_spending_patterns
analysis = analyze_spending_patterns(weeks_back=8)
```

## 🛠️ Maintenance & Utilities

### Database Management
```bash
# View all invoices (clean ASCII output)
python view_database.py

# Clean up database
python cleanup.py

# Test API connection
python testgroq.py
```

### Web App Features
- **📱 Responsive Design**: Works on desktop and mobile
- **🔄 Real-time Updates**: Live data refresh and processing
- **📥 Data Export**: CSV and JSON download capabilities
- **🛡️ Error Handling**: Graceful error management and user feedback

## 📦 Dependencies

### Core Processing
- `groq>=0.4.0` - LLM API client
- `pydantic>=2.0.0` - Data validation and parsing
- `pillow>=9.5.0` - Image processing
- `python-dotenv>=1.0.0` - Environment variables

### Database
- `sqlalchemy>=2.0.0` - Database ORM
- `sqlite3` (built-in) - Database engine

### Web Interface  
- `streamlit>=1.28.0` - Web application framework
- `pandas>=2.0.0` - Data manipulation
- `plotly>=5.15.0` - Interactive charts
- `numpy>=1.24.0` - Numerical computing

### Additional
- `opencv-python>=4.8.0` - Advanced image processing
- `requests>=2.31.0` - HTTP requests

## 🌐 Environment Configuration

### Required Environment Variables
```bash
GROQ_API_KEY=your_groq_api_key_here
```

### Optional Configuration
```bash
DATABASE_PATH=invoices.db          # Custom database path
MAX_IMAGE_SIZE=10485760           # Max image size (10MB)
BATCH_SIZE=10                     # Batch processing size
DEBUG_MODE=false                  # Enable debug logging
```

## 🧪 Testing & Development

### Test API Connection
```bash
python testgroq.py
```

### Development Mode
```bash
# Run with auto-reload
streamlit run streamlit/app.py --server.runOnSave true

# Debug mode
STREAMLIT_LOGGER_LEVEL=debug streamlit run streamlit/app.py
```

## 📊 Current Status

✅ **Production Ready System**
- 4 sample invoices processed
- Complete web interface
- Financial analysis pipeline
- Data export capabilities
- Robust error handling

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)  
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support & Troubleshooting

### Common Issues

**Import Errors**
```bash
# Ensure you're in the correct directory
cd invoice_rag
python -c "from src.processor import process_invoice_with_llm; print('✅ Imports working')"
```

**Database Issues**
```bash
# Reinitialize database
python -c "from src.database import create_tables; create_tables(); print('✅ Database initialized')"
```

**Streamlit Issues**
```bash
# Clear cache and restart
streamlit cache clear
streamlit run streamlit/app.py
```

### Getting Help
- 📖 Check this README thoroughly
- 🐛 Open an issue for bugs
- 💡 Submit feature requests
- 📧 Contact maintainers for support

---

**🎉 Happy Invoice Processing!** 📄✨
