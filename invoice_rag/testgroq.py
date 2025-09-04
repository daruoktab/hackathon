from groq import Groq
import os
import base64
import json
from datetime import datetime
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List, Optional

# Load environment variables from .env file
load_dotenv()

# Define Pydantic schemas for Indonesian invoice/receipt extraction
class InvoiceItem(BaseModel):
    name: str
    quantity: Optional[int]
    unit_price: Optional[float]
    total_price: float

class IndonesianInvoice(BaseModel):
    shop_name: str
    shop_address: Optional[str]
    invoice_date: Optional[str]  # Date from the invoice itself
    invoice_time: Optional[str]  # Time from the invoice itself
    invoice_number: Optional[str]
    items: List[InvoiceItem]
    subtotal: Optional[float]
    tax: Optional[float]
    discount: Optional[float]
    total_amount: float
    payment_method: Optional[str]
    cashier: Optional[str]

# Function to encode image to base64
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Function to process a single image
def process_invoice_image(image_path, image_name):
    print(f"\n{'='*60}")
    print(f"🖼️  PROCESSING: {image_name}")
    print(f"{'='*60}")
    
    try:
        # Get the base64 string of the image
        base64_image = encode_image(image_path)
        
        # Get current timestamp for processing
        current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        completion = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Please analyze this Indonesian shopping receipt/invoice and extract all the information according to the schema. Pay special attention to shop name, total amount, and date/time information."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            temperature=0.1,  # Lower temperature for more consistent structured output
            max_completion_tokens=1024,
            top_p=1,
            stream=False,
            stop=None,
        )

        # Parse the response
        response_content = completion.choices[0].message.content
        print("Raw response:")
        print(response_content)
        print("\n" + "="*50 + "\n")

        # Display current processing timestamp
        print(f"Processing Timestamp: {current_timestamp}")
        print("="*50)

        # Try to parse as JSON and validate with Pydantic
        try:
            if response_content is None:
                raise ValueError("Response content is None")
                
            # Extract JSON from response - look for the actual data, not the schema
            json_blocks = []
            if "```json" in response_content:
                # Find all JSON blocks
                start_pos = 0
                while True:
                    json_start = response_content.find("```json", start_pos)
                    if json_start == -1:
                        break
                    json_start += 7
                    json_end = response_content.find("```", json_start)
                    if json_end == -1:
                        break
                    json_content = response_content[json_start:json_end].strip()
                    json_blocks.append(json_content)
                    start_pos = json_end + 3
            else:
                json_blocks.append(response_content.strip())
            
            # Try to find the actual data (not the schema)
            invoice = None
            for json_content in json_blocks:
                try:
                    parsed_data = json.loads(json_content)
                    # Check if this looks like actual data (has shop_name field at top level)
                    if isinstance(parsed_data, dict) and "shop_name" in parsed_data:
                        invoice = IndonesianInvoice.model_validate(parsed_data)
                        break
                except (json.JSONDecodeError, Exception):
                    continue
            
            if invoice is None:
                raise ValueError("Could not find valid invoice data in the response")
            
            print("📋 INDONESIAN INVOICE ANALYSIS")
            print("="*50)
            print(f"🏪 Shop Name: {invoice.shop_name}")
            print(f"📍 Shop Address: {invoice.shop_address or 'Not found'}")
            print(f"📅 Invoice Date: {invoice.invoice_date or 'Not found'}")
            print(f"🕐 Invoice Time: {invoice.invoice_time or 'Not found'}")
            print(f"🧾 Invoice Number: {invoice.invoice_number or 'Not found'}")
            print(f"💰 Total Amount: Rp {invoice.total_amount:,.2f}")
            print(f"💳 Payment Method: {invoice.payment_method or 'Not specified'}")
            print(f"👤 Cashier: {invoice.cashier or 'Not found'}")
            
            if invoice.subtotal:
                print(f"📊 Subtotal: Rp {invoice.subtotal:,.2f}")
            if invoice.tax:
                print(f"🏛️ Tax: Rp {invoice.tax:,.2f}")
            if invoice.discount:
                print(f"🎟️ Discount: Rp {invoice.discount:,.2f}")
            
            print(f"\n🛒 Items ({len(invoice.items)} total):")
            print("-" * 50)
            for i, item in enumerate(invoice.items, 1):
                print(f"{i}. {item.name}")
                if item.quantity:
                    print(f"   Qty: {item.quantity}")
                if item.unit_price:
                    print(f"   Unit Price: Rp {item.unit_price:,.2f}")
                print(f"   Total: Rp {item.total_price:,.2f}")
                print()
            
            print("="*50)
            print(f"🕒 Processed at: {current_timestamp}")
            return invoice
                
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse JSON: {e}")
            print("Raw response was not valid JSON")
            return None
        except Exception as e:
            print(f"❌ Failed to validate with Pydantic: {e}")
            print("Response didn't match expected schema")
            return None
            
    except Exception as e:
        print(f"❌ Error processing {image_name}: {e}")
        return None

# List of images to process (one level up from current directory)
image_files = ["../test1.jpg", "../test2.jpg", "../test3.jpg", "../test4.jpg"]
image_names = ["test1.jpg", "test2.jpg", "test3.jpg", "test4.jpg"]

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Create a system prompt for Indonesian invoice analysis
system_prompt = f"""You are an expert at extracting information from Indonesian shopping receipts and invoices. 
Analyze the provided image and extract all relevant information in the following JSON format:
{IndonesianInvoice.model_json_schema()}

Important guidelines:
- Look for shop/store names in Indonesian (like "Toko", "Warung", "Supermarket", etc.)
- Extract dates in any format you find (DD/MM/YYYY, DD-MM-YYYY, etc.)
- Look for total amounts in Indonesian Rupiah (Rp, IDR)
- Extract all items with their prices if visible
- If multiple totals exist, use the final/grand total
- Look for common Indonesian terms like "Total", "Jumlah", "Bayar", "Kembalian"
- Be thorough and accurate in your extraction"""

# Main execution - process all images
print("🚀 Starting Indonesian Invoice Analysis for Multiple Images")
print("="*70)

results = []
for image_path, image_name in zip(image_files, image_names):
    try:
        # Check if image file exists
        if not os.path.exists(image_path):
            print(f"❌ Image not found: {image_path}")
            continue
            
        result = process_invoice_image(image_path, image_name)
        if result:
            results.append((image_name, result))
        
        # Add separator between images
        print("\n" + "🔄" * 20 + " NEXT IMAGE " + "🔄" * 20 + "\n")
        
    except Exception as e:
        print(f"❌ Error processing {image_name}: {e}")
        continue

# Summary of all processed invoices
print("\n" + "="*70)
print("� SUMMARY OF ALL PROCESSED INVOICES")
print("="*70)

if results:
    total_amount_sum = 0
    for image_name, invoice in results:
        print(f"\n� {image_name}:")
        print(f"   🏪 Shop: {invoice.shop_name}")
        print(f"   📅 Date: {invoice.invoice_date or 'Not found'}")
        print(f"   💰 Total: Rp {invoice.total_amount:,.2f}")
        print(f"   � Items: {len(invoice.items)}")
        total_amount_sum += invoice.total_amount
    
    print(f"\n💯 GRAND TOTAL ALL INVOICES: Rp {total_amount_sum:,.2f}")
    print(f"📈 Successfully processed {len(results)} out of {len(image_files)} images")
else:
    print("❌ No invoices were successfully processed")

print("\n" + "="*70)
print("✅ Analysis Complete!")
print("="*70)
