# 📁 Invoices Input Directory

This folder is used for **automatic invoice processing**.

## 🔄 How it works:

1. **Drop invoice images here**: Place your invoice images (JPG, PNG) in this folder
2. **Automatic processing**: The system will scan this folder for new images
3. **Data extraction**: LLM processes each image and extracts structured data
4. **Database storage**: Processed data is saved to the database
5. **Analysis ready**: Data becomes available for financial analysis

## 📷 Supported formats:
- `.jpg` / `.jpeg`
- `.png`

## 💡 Usage example:

```bash
# Copy invoice images to this folder
cp my_invoice.jpg invoice_rag/invoices/

# Run the processing system
cd invoice_rag
python -c "from src.main import process_invoice_directory; process_invoice_directory()"

# Or process individual files
python -c "from src.main import process_single_image; process_single_image('invoices/my_invoice.jpg')"
```

## 📊 After processing:
- View results: `python view_database.py`
- Search data: Use the query interface in `src/query.py`
- Get analysis: Financial insights available through `src/analysis.py`

---
**💡 Tip:** Keep the original invoice images here for record-keeping and reprocessing if needed.
