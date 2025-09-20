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
from pydantic import BaseModel, Field, field_validator
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class InvoiceItem(BaseModel):
    """Invoice item with validation."""
    name: str = Field(description="Name of the item")
    quantity: Optional[int] = Field(default=1, description="Quantity of the item")
    unit_price: Optional[float] = Field(default=None, description="Unit price of the item")
    total_price: float = Field(description="Total price for this item")

class RobustInvoice(BaseModel):
    """Robust invoice model with standardized date/time format."""
    shop_name: str = Field(description="Name of the shop/store")
    shop_address: Optional[str] = Field(default=None, description="Address of the shop")
    invoice_date: Optional[str] = Field(default=None, description="Date in YYYY-MM-DD format")
    invoice_time: Optional[str] = Field(default=None, description="Time in HH:MM format (24-hour)")
    invoice_number: Optional[str] = Field(default=None, description="Invoice number")
    total_amount: float = Field(description="Total amount of the invoice")
    subtotal: Optional[float] = Field(default=None, description="Subtotal amount")
    tax: Optional[float] = Field(default=None, description="Tax amount")
    discount: Optional[float] = Field(default=None, description="Discount amount")
    payment_method: Optional[str] = Field(default=None, description="Payment method used")
    cashier: Optional[str] = Field(default=None, description="Cashier name")
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

    @field_validator('invoice_time')
    @classmethod
    def validate_time_format(cls, v):
        """Validate and standardize time format to HH:MM."""
        if not v:
            return None
        
        # Common time patterns
        patterns = [
            r'(\d{1,2}):(\d{2}):(\d{2})',    # HH:MM:SS
            r'(\d{1,2}):(\d{2})',            # HH:MM
            r'(\d{1,2})\.(\d{2})',           # HH.MM
            r'(\d{1,2})\s*:\s*(\d{2})',      # HH : MM with spaces
        ]
        
        for pattern in patterns:
            match = re.search(pattern, str(v))
            if match:
                parts = match.groups()
                if len(parts) >= 2:
                    hour, minute = int(parts[0]), int(parts[1])
                    if 0 <= hour <= 23 and 0 <= minute <= 59:
                        return f"{hour:02d}:{minute:02d}"
        
        return v  # Return original if no pattern matches

def encode_image(image_path):
    """Encode image to base64."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

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
  "shop_address": "address of the shop",
  "invoice_date": "date in YYYY-MM-DD format (e.g., 2024-12-25)",
  "invoice_time": "time in HH:MM format (e.g., 14:30, no seconds)",
  "invoice_number": "invoice/receipt number",
  "total_amount": 0.0,
  "subtotal": 0.0,
  "tax": 0.0,
  "discount": 0.0,
  "payment_method": "payment method used",
  "cashier": "cashier name",
  "items": [
    {
      "name": "item name",
      "quantity": 1,
      "unit_price": 0.0,
      "total_price": 0.0
    }
  ]
}

CRITICAL FORMATTING RULES:
- dates: ALWAYS use YYYY-MM-DD format (e.g., 2025-01-15)
- times: ALWAYS use HH:MM format (e.g., 09:30, 14:45) - NO SECONDS
- numbers: use decimal format (e.g., 15000.0, not 15,000)
- if date/time unclear, use best guess in correct format

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
    
    # Create invoices table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shop_name TEXT,
            shop_address TEXT,
            invoice_date TEXT,
            invoice_time TEXT,
            invoice_number TEXT,
            total_amount REAL,
            subtotal REAL,
            tax REAL,
            discount REAL,
            payment_method TEXT,
            cashier TEXT,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            image_path TEXT
        )
    ''')
    
    # Create invoice_items table
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

        # Insert invoice
        cursor.execute('''
            INSERT INTO invoices (
                shop_name, shop_address, invoice_date, invoice_time, invoice_number,
                total_amount, subtotal, tax, discount, payment_method, cashier, image_path
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            invoice_data.get('shop_name'),
            invoice_data.get('shop_address'),
            invoice_data.get('invoice_date'),
            invoice_data.get('invoice_time'),
            invoice_data.get('invoice_number'),
            invoice_data.get('total_amount', 0),
            invoice_data.get('subtotal'),
            invoice_data.get('tax'),
            invoice_data.get('discount'),
            invoice_data.get('payment_method'),
            invoice_data.get('cashier'),
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
