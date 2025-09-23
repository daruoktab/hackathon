#!/usr/bin/env python3
"""
Invoice Processor - Main invoice processing with standardized date/time format
"""

import os
import json
import base64
import sqlite3
import re
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, ValidationError
from enum import Enum
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class TransactionType(str, Enum):
    """Transaction type enum for validation."""
    BANK = "bank"
    RETAIL = "retail" 
    E_COMMERCE = "e-commerce"

class InvoiceItem(BaseModel):
    """Invoice item with validation."""
    name: str = Field(description="Name of the item")
    quantity: Optional[int] = Field(default=1, description="Quantity of the item")
    unit_price: Optional[float] = Field(default=None, description="Unit price of the item")
    total_price: float = Field(description="Total price for this item")

class RobustInvoice(BaseModel):
    """Simplified invoice model with transaction type validation."""
    shop_name: str = Field(description="Name of the shop/store")
    invoice_date: Optional[str] = Field(default=None, description="Date in YYYY-MM-DD format")
    total_amount: float = Field(description="Total amount of the invoice")
    transaction_type: Optional[TransactionType] = Field(default=None, description="Type of transaction: bank, retail, or e-commerce")
    items: List[InvoiceItem] = Field(default=[], description="List of items in the invoice")

    @field_validator('invoice_date')
    @classmethod
    def validate_date_format(cls, v):
        """Validate and standardize date format to YYYY-MM-DD."""
        if not v:
            return None
        
        # Common date patterns
        patterns = [
            r'(\d{4})-(\d{2})-(\d{2})',      # YYYY-MM-DD
            r'(\d{2})-(\d{2})-(\d{4})',      # DD-MM-YYYY
            r'(\d{2})/(\d{2})/(\d{4})',      # DD/MM/YYYY
            r'(\d{4})/(\d{2})/(\d{2})',      # YYYY/MM/DD
            r'(\d{2})\.(\d{2})\.(\d{4})',    # DD.MM.YYYY
        ]
        
        for pattern in patterns:
            match = re.search(pattern, str(v))
            if match:
                parts = match.groups()
                if len(parts) == 3:
                    # Determine if it's YYYY-MM-DD or DD-MM-YYYY format
                    if len(parts[0]) == 4:  # YYYY-MM-DD or YYYY/MM/DD
                        year, month, day = parts
                    else:  # DD-MM-YYYY, DD/MM/YYYY, DD.MM.YYYY
                        day, month, year = parts
                    
                    # Validate and format
                    try:
                        year, month, day = int(year), int(month), int(day)
                        if 1 <= month <= 12 and 1 <= day <= 31:
                            return f"{year:04d}-{month:02d}-{day:02d}"
                    except ValueError:
                        pass
        
        return v  # Return original if no pattern matches
    
    @field_validator('transaction_type', mode='before')
    @classmethod
    def determine_transaction_type(cls, v, info):
        """Auto-determine transaction type based on shop name if not provided."""
        if v is not None:
            # If explicitly provided, validate it
            if isinstance(v, str):
                v = v.lower().replace("-", "_").replace(" ", "_")
                if v in ["bank", "retail", "e_commerce", "ecommerce"]:
                    return v.replace("_", "-") if "commerce" in v else v
            return v
        
        # Auto-determine based on shop name
        shop_name = info.data.get('shop_name', '').lower() if info.data else ''
        
        # Bank indicators
        bank_keywords = ['bank', 'atm', 'bri', 'mandiri', 'bca', 'bni', 'transfer']
        if any(keyword in shop_name for keyword in bank_keywords):
            return TransactionType.BANK
        
        # E-commerce indicators  
        ecommerce_keywords = ['shopee', 'tokopedia', 'bukalapak', 'lazada', 'blibli', 'online']
        if any(keyword in shop_name for keyword in ecommerce_keywords):
            return TransactionType.E_COMMERCE
        
        # Default to retail for physical stores
        return TransactionType.RETAIL

def encode_image(image_path):
    """Encode image to base64."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def parse_indonesian_currency(value_str):
    """Parse Indonesian currency format to float.
    
    Indonesian format examples:
    - "59.385" -> 59385.0 (dots as thousands separator)
    - "6.000.000" -> 6000000.0 (multiple dots as thousands separators)
    - "25,500" -> 25500.0 (comma as decimal separator)
    - "59.385,50" -> 59385.5 (dots for thousands, comma for decimal)
    - "RP 500,000.00" -> 500000.0 (with currency prefix)
    - "Rp136.000" -> 136000.0 (various currency formats)
    
    NOTE: Rejects invalid range formats like "-20000-60000"
    """
    if not value_str:
        return 0.0
    
    # Convert to string and clean
    value_str = str(value_str).strip()
    
    # Handle edge cases that might cause errors
    if not value_str or value_str.lower() in ['null', 'none', '-', '']:
        return 0.0
    
    # VALIDATION: Reject obvious invalid formats
    original_value = value_str
    
    # Remove currency symbols more thoroughly
    # First remove common currency patterns
    value_str = re.sub(r'\b[Rp]+\b', '', value_str, flags=re.IGNORECASE)
    value_str = re.sub(r'\s+', '', value_str)  # Remove all spaces
    
    # STRICT VALIDATION: Check for suspicious range patterns
    # Count dashes and numbers to detect invalid ranges
    if '-' in value_str:
        dash_count = value_str.count('-')
        # If multiple dashes or complex patterns, it might be invalid
        parts = [p for p in value_str.split('-') if p and p.strip()]
        
        # If we have multiple numeric parts separated by dashes, this is suspicious
        if len(parts) > 2:
            print(f"[WARNING] Suspicious range format detected: '{original_value}' - rejecting")
            return 0.0
            
        # If we have exactly 2 parts and both are purely numeric (no dots/commas)
        # this is likely an invalid range format
        if len(parts) == 2 and all(p.isdigit() for p in parts):
            print(f"[WARNING] Invalid range format detected: '{original_value}' - rejecting")
            return 0.0
        
        # Handle legitimate cases like negative numbers
        if dash_count >= 2 or (dash_count == 1 and not (value_str.startswith('-') and len(value_str.split('-')) == 2)):
            # This might be a range, take the last number only if it's reasonable
            if len(parts) > 1:
                value_str = parts[-1]  # Take the last non-empty part
    
    # Remove any remaining non-numeric characters except dots and commas
    value_str = re.sub(r'[^\d.,]', '', value_str)  # Remove the \- from regex since we handled ranges
    
    if not value_str:
        return 0.0
    
    # Check if it has both dots and comma (Indonesian full format)
    if '.' in value_str and ',' in value_str:
        # Determine which is decimal separator
        # In Indonesian: dots for thousands, comma for decimal
        # But also handle English format: comma for thousands, dot for decimal
        
        # Find last dot and comma positions
        last_dot = value_str.rfind('.')
        last_comma = value_str.rfind(',')
        
        if last_comma > last_dot:
            # Comma comes after dot: "59.385,50" (Indonesian format)
            parts = value_str.split(',')
            integer_part = parts[0].replace('.', '')  # Remove thousand separators
            decimal_part = parts[1] if len(parts) > 1 else '0'
            try:
                return float(f"{integer_part}.{decimal_part}")
            except ValueError:
                return 0.0
        else:
            # Dot comes after comma: "500,000.00" (English format)
            parts = value_str.split('.')
            integer_part = parts[0].replace(',', '')  # Remove thousand separators
            decimal_part = parts[1] if len(parts) > 1 else '0'
            try:
                return float(f"{integer_part}.{decimal_part}")
            except ValueError:
                return 0.0
    
    # Check if it only has comma (could be decimal or thousands)
    elif ',' in value_str and value_str.count(',') == 1:
        # Could be decimal or thousands separator
        parts = value_str.split(',')
        if len(parts) == 2:
            # If the part after comma has 3 digits, it's thousands
            if len(parts[1]) == 3 and parts[1].isdigit():
                try:
                    return float(value_str.replace(',', ''))
                except ValueError:
                    return 0.0
            # Otherwise it's decimal
            else:
                try:
                    return float(value_str.replace(',', '.'))
                except ValueError:
                    return 0.0
    
    # Check if it only has dots
    elif '.' in value_str:
        dot_count = value_str.count('.')
        if dot_count > 1:
            # Multiple dots = thousands separators, e.g., "6.000.000"
            try:
                return float(value_str.replace('.', ''))
            except ValueError:
                return 0.0
        else:
            # Single dot - check context to determine if thousands or decimal
            parts = value_str.split('.')
            if len(parts) == 2:
                # If last part has exactly 3 digits, likely thousands separator
                if len(parts[1]) == 3 and parts[1].isdigit() and len(parts[0]) <= 3:
                    try:
                        return float(value_str.replace('.', ''))
                    except ValueError:
                        return 0.0
                else:
                    # Otherwise treat as decimal separator
                    try:
                        return float(value_str)
                    except ValueError:
                        return 0.0
    
    # No special characters, just convert
    try:
        return float(value_str)
    except ValueError:
        return 0.0

def process_invoice_with_llm(image_path):
    """Process invoice using Groq LLM with enhanced prompting."""
    
    # Get API key
    groq_api_key = os.environ.get("GROQ_API_KEY")
    if not groq_api_key:
        print("Please set the GROQ_API_KEY environment variable")
        return None
    
    client = Groq(api_key=groq_api_key)
    
    try:
        # Encode image
        base64_image = encode_image(image_path)
        
        # Enhanced prompt for consistent formatting
        prompt = '''Extract invoice data from this image and return ONLY a JSON object with this exact structure:

{
  "shop_name": "name of the shop/store",
  "invoice_date": "date in YYYY-MM-DD format (e.g., 2024-12-25)",
  "total_amount": "SINGLE FINAL AMOUNT ONLY - the main total to pay",
  "transaction_type": "bank|retail|e-commerce (optional, will be auto-determined)",
  "items": [
    {
      "name": "item name",
      "quantity": 1,
      "unit_price": "unit price for this item",
      "total_price": "total price for this item"
    }
  ]
}

CRITICAL FORMATTING RULES:
- dates: ALWAYS use YYYY-MM-DD format (e.g., 2025-01-15)
- MONEY VALUES: Keep the EXACT format as written on the invoice
  * If invoice shows "59.385" -> use "59.385" (Indonesian format with dots as thousands)
  * If invoice shows "6.000.000" -> use "6.000.000" 
  * If invoice shows "25,500" -> use "25,500"
  * DO NOT convert to decimal format like 59385.0
  * PRESERVE the original formatting exactly as it appears
- TOTAL AMOUNT: Must be a SINGLE VALUE, never a range or multiple values
  * Look for words like "Total", "Total Bayar", "Grand Total", "Amount Due"
  * If you see multiple amounts, choose the final amount to be paid
  * NEVER use formats like "20000-60000" or ranges
- TRANSACTION TYPE: 
  * "bank" for bank transfers, ATM transactions, BRI/BCA/Mandiri/BNI
  * "retail" for physical stores, restaurants, retail shops
  * "e-commerce" for online platforms like Shopee, Tokopedia, Bukalapak
  * Leave empty if unclear - will be auto-determined from shop name
- if date unclear, use best guess in correct format

Return ONLY the JSON, no explanations.'''

        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            temperature=0.1,
            max_completion_tokens=2000
        )
        
        content = response.choices[0].message.content
        if content is None:
            raise ValueError("LLM returned empty response")
        
        content = content.strip()
        print(f"LLM Response: {content[:200]}...")
        
        # Clean the response
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        # Parse JSON
        try:
            invoice_data = json.loads(content)
            
            # Log suspicious values before processing
            currency_fields = ['total_amount']
            for field in currency_fields:
                if field in invoice_data and invoice_data[field] is not None:
                    original_value = invoice_data[field]
                    if isinstance(original_value, str) and '-' in original_value:
                        parts = [p for p in original_value.split('-') if p and p.strip()]
                        if len(parts) >= 2 and all(p.replace('.', '').replace(',', '').isdigit() for p in parts):
                            print(f"[SUSPICIOUS] LLM returned range format for {field}: '{original_value}'")
                            print("[INFO] This suggests LLM misread the invoice. Check image quality or add more specific instructions.")
            
            # Convert Indonesian currency formats to float for total_amount
            if 'total_amount' in invoice_data and invoice_data['total_amount'] is not None:
                original_value = invoice_data['total_amount']
                parsed_value = parse_indonesian_currency(original_value)
                invoice_data['total_amount'] = parsed_value
                
                # Log if parsing returned 0 due to validation
                if parsed_value == 0.0 and original_value:
                    print(f"[VALIDATION] Rejected invalid total_amount value: '{original_value}' -> 0.0")
            
            # Convert item prices
            if 'items' in invoice_data and isinstance(invoice_data['items'], list):
                for item in invoice_data['items']:
                    if 'unit_price' in item and item['unit_price'] is not None:
                        item['unit_price'] = parse_indonesian_currency(item['unit_price'])
                    if 'total_price' in item and item['total_price'] is not None:
                        item['total_price'] = parse_indonesian_currency(item['total_price'])
            
            # Validate with Pydantic
            try:
                validated_invoice = RobustInvoice(**invoice_data)
                return validated_invoice.model_dump()
            except Exception as e:
                print(f"[ERROR] Pydantic validation error: {e}")
                return None
        except json.JSONDecodeError:
            print("[ERROR] No JSON found in response")
            print(f"Response content: {content}")
            return None
            
    except Exception as e:
        print(f"[ERROR] Error calling LLM: {e}")
        return None

def create_tables():
    """Create database tables if they don't exist."""
    # Import the centralized database path function
    from .database import get_default_db_path

    db_path = get_default_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create simplified invoices table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shop_name TEXT NOT NULL,
            invoice_date TEXT,
            total_amount REAL NOT NULL,
            transaction_type TEXT,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            image_path TEXT
        )
    ''')
    
    # Create invoice_items table (unchanged)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invoice_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id INTEGER,
            item_name TEXT,
            quantity INTEGER,
            unit_price REAL,
            total_price REAL,
            FOREIGN KEY (invoice_id) REFERENCES invoices (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def save_to_database_robust(invoice_data, image_path):
    """Save invoice data to database with robust error handling."""
    try:
        create_tables()
        # Import the centralized database path function
        from .database import get_default_db_path

        db_path = get_default_db_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Insert simplified invoice
        cursor.execute('''
            INSERT INTO invoices (
                shop_name, invoice_date, total_amount, transaction_type, image_path
            ) VALUES (?, ?, ?, ?, ?)
        ''', (
            invoice_data.get('shop_name'),
            invoice_data.get('invoice_date'),
            invoice_data.get('total_amount', 0),
            invoice_data.get('transaction_type'),
            image_path
        ))
        
        invoice_id = cursor.lastrowid
        
        # Insert items
        items = invoice_data.get('items', [])
        for item in items:
            cursor.execute('''
                INSERT INTO invoice_items (invoice_id, item_name, quantity, unit_price, total_price)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                invoice_id,
                item.get('name'),
                item.get('quantity', 1),
                item.get('unit_price'),
                item.get('total_price', 0)
            ))
        
        conn.commit()
        conn.close()
        return invoice_id
        
    except Exception as e:
        print(f"[ERROR] Database error: {e}")
        return None

def process_invoice(image_path):
    """Process a single invoice image."""
    print(f"\nProcessing: {os.path.basename(image_path)}")
    
    if not os.path.exists(image_path):
        print(f"[ERROR] File not found: {image_path}")
        return None
    
    # Process with LLM
    invoice_data = process_invoice_with_llm(image_path)
    
    if invoice_data:
        print(f"   [SUCCESS] Extracted: {invoice_data.get('shop_name', 'Unknown')} - Rp {invoice_data.get('total_amount', 0):,.2f}")
        return invoice_data
    else:
        print("   [ERROR] Failed to extract data")
        return None

def main():
    """Main function to process invoices."""
    
    print("INVOICE PROCESSOR")
    print("=" * 50)
    print("Processing invoice images with robust date/time formatting...")
    
    # Check for API key
    if not os.environ.get("GROQ_API_KEY"):
        print("[ERROR] GROQ_API_KEY not found in environment variables")
        print("Please set up your .env file with GROQ_API_KEY=your_key_here")
        return
    
    # Get image paths - check multiple locations
    print(f"Current working directory: {os.getcwd()}")
    
    # Try invoices subdirectory first
    image_paths = []
    image_dir = "invoices"
    print(f"Looking for images in: {image_dir}")
    
    if os.path.exists(image_dir):
        image_paths = [
            os.path.join(image_dir, f) for f in os.listdir(image_dir)
            if f.lower().endswith(('.jpg', '.jpeg', '.png'))
        ]
        print(f"Found in invoices/: {image_paths}")
    
    # If no images in invoices/, check root directory
    if not image_paths:
        root_images = [f for f in os.listdir(".") if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        if root_images:
            image_paths = root_images
            print(f"Found in root: {image_paths}")
    
    # If still no images, check parent directory
    if not image_paths:
        try:
            parent_images = [f for f in os.listdir("..") if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            if parent_images:
                image_paths = [os.path.join("..", f) for f in parent_images]
                print(f"Found in parent: {image_paths}")
        except Exception:
            pass
    
    if not image_paths:
        print("[ERROR] No image files found!")
        print("Checked: invoices/, current directory, and parent directory")
        return
    
    print(f"Found {len(image_paths)} images to process")
    
    # Process each image
    successful_count = 0
    total_amount = 0
    
    for image_path in image_paths:
        invoice_data = process_invoice(image_path)
        if invoice_data:
            invoice_id = save_to_database_robust(invoice_data, image_path)
            if invoice_id:
                print(f"   [SUCCESS] Saved to database with ID: {invoice_id}")
                total_amount += invoice_data.get('total_amount', 0)
                successful_count += 1
            else:
                print("   [ERROR] Failed to save to database")
        else:
            print(f"[ERROR] Failed to extract data from {os.path.basename(image_path)}")
    
    print("\nPROCESSING COMPLETE!")
    print(f"Processed {successful_count}/{len(image_paths)} invoices successfully")
    print(f"Total amount: Rp {total_amount:,.2f}")
    print("All dates standardized to YYYY-MM-DD format")
    print("All times standardized to HH:MM format")
    
    if successful_count > 0:
        print("\nView results: python view_database.py")

if __name__ == "__main__":
    print("Starting invoice processor...")
    main()
    print("Processor finished.")
