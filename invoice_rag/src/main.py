
import os
import json
import base64
from . import database
from . import analysis
from .models import IndonesianInvoice
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Configure the Groq API
groq_api_key = os.environ.get("GROQ_API_KEY")
client = None

if not groq_api_key or groq_api_key == "YOUR_GROQ_API_KEY":
    print("Please set the GROQ_API_KEY environment variable in your .env file.")
else:
    try:
        client = Groq(api_key=groq_api_key)
    except Exception as e:
        print(f"Error initializing Groq client: {e}")

def encode_image(image_path):
    """Encode image to base64."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def extract_invoice_data_with_llm(image_path):
    """Extract invoice data using Groq LLM with vision."""
    if not client:
        return None
    
    try:
        base64_image = encode_image(image_path)
        
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
        - Be thorough and accurate in your extraction
        
        Return ONLY valid JSON that matches the schema."""
        
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
                            "text": "Please analyze this Indonesian shopping receipt/invoice and extract all the information according to the schema."
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
            temperature=0.1,
            max_completion_tokens=1024,
        )

        response_content = completion.choices[0].message.content
        
        if not response_content:
            raise ValueError("No response content received")
        
        # Extract JSON from response
        if "```json" in response_content:
            json_start = response_content.find("```json") + 7
            json_end = response_content.find("```", json_start)
            json_content = response_content[json_start:json_end].strip()
        else:
            json_content = response_content.strip()
        
        # Parse and validate with Pydantic
        parsed_data = json.loads(json_content)
        invoice = IndonesianInvoice.model_validate(parsed_data)
        
        return invoice
        
    except Exception as e:
        print(f"Error extracting invoice data: {e}")
        return None

def generate_financial_advice(analysis_data):
    """Generate comprehensive financial advice based on analysis."""
    if not client:
        return "Groq client not initialized. Please check your API key."

    try:
        prompt = f"""
        Based on the following comprehensive financial analysis, provide detailed and actionable financial advice for an Indonesian consumer.
        
        Analysis Data:
        {json.dumps(analysis_data, indent=2, default=str)}
        
        Please provide advice in the following areas:
        1. Budgeting recommendations
        2. Spending optimization suggestions
        3. Savings opportunities
        4. Financial habits improvement
        5. Long-term financial planning
        
        Consider the Indonesian context, common spending patterns, and provide practical advice that can be implemented immediately.
        
        Format your response as clear, actionable advice with specific recommendations and action items.
        """
        
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama3-8b-8192",
            temperature=0.7,
            max_completion_tokens=2048,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Error during financial advice generation: {e}"

def process_single_invoice(image_path, db_session):
    """Process a single invoice image and save to database."""
    print(f"Processing invoice: {os.path.basename(image_path)}")
    
    # Extract data using LLM
    invoice_data = extract_invoice_data_with_llm(image_path)
    
    if invoice_data:
        # Save to database
        invoice_id = database.insert_invoice_data(db_session, invoice_data, image_path)
        if invoice_id is not None:
            print(f"✅ Successfully processed: {invoice_data.shop_name} - Rp {invoice_data.total_amount:,.2f}")
            return invoice_data
        else:
            print("❌ Failed to save invoice to database")
    else:
        print(f"❌ Failed to extract data from {os.path.basename(image_path)}")
    
    return None

def generate_comprehensive_report(db_session, weeks_back=4):
    """Generate comprehensive financial report with analysis and advice."""
    print(f"\n{'='*60}")
    print("📊 GENERATING COMPREHENSIVE FINANCIAL REPORT")
    print(f"{'='*60}")
    
    # Get comprehensive analysis
    analysis_data = analysis.generate_comprehensive_analysis(db_session, weeks_back)
    
    # Display analysis
    print("\n📈 FINANCIAL ANALYSIS - " + analysis_data['period'])
    print("-" * 50)
    
    summary = analysis_data['summary']
    print(f"💰 Total Spent: Rp {summary['total_spent']:,.2f}")
    print(f"📅 Weekly Average: Rp {summary['weekly_average']:,.2f}")
    print(f"📊 Daily Average: Rp {summary['daily_average']:,.2f}")
    print(f"🧾 Total Transactions: {summary['transaction_count']}")
    
    # Trends
    trends = analysis_data['trends']
    print("\n📈 SPENDING TRENDS")
    print("-" * 30)
    print(f"Trend: {trends['message']}")
    
    # Top spending
    top_spending = analysis_data['top_spending']
    print("\n🏪 TOP SPENDING BY SHOP")
    print("-" * 30)
    for i, shop in enumerate(top_spending['by_shop'][:5], 1):
        print(f"{i}. {shop['shop_name']}: Rp {shop['total_amount']:,.2f} ({shop['transaction_count']} transactions)")
    
    # Insights
    print("\n💡 KEY INSIGHTS")
    print("-" * 20)
    for insight in analysis_data['insights']:
        print(f"• {insight}")
    
    # Generate AI advice
    print("\n🤖 AI FINANCIAL ADVISOR")
    print("=" * 40)
    advice = generate_financial_advice(analysis_data)
    print(advice)
    
    return analysis_data

def main():
    """Main function to process invoices and generate financial analysis."""
    # Initialize database
    db_path = os.path.join('invoice_rag', 'invoices.db')
    db_session = database.get_db_session(db_path)
    
    # Process any new invoices in the invoices directory
    invoice_dir = os.path.join('invoice_rag', 'invoices')
    if os.path.exists(invoice_dir):
        print(f"🔍 Scanning for invoices in: {invoice_dir}")
        processed_count = 0
        
        for filename in os.listdir(invoice_dir):
            file_path = os.path.join(invoice_dir, filename)
            if os.path.isfile(file_path) and filename.lower().endswith(('.jpg', '.jpeg', '.png', '.pdf')):
                result = process_single_invoice(file_path, db_session)
                if result:
                    processed_count += 1
        
        print(f"✅ Processed {processed_count} new invoices")
    
    # Generate comprehensive report
    generate_comprehensive_report(db_session, weeks_back=4)
    
    # Close database session
    db_session.close()

def process_single_image(image_path):
    """Process a single image file (for external use)."""
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        return None
    
    # Initialize database
    db_path = os.path.join('invoice_rag', 'invoices.db')
    db_session = database.get_db_session(db_path)
    
    # Process the image
    result = process_single_invoice(image_path, db_session)
    
    # Generate updated report
    if result:
        generate_comprehensive_report(db_session, weeks_back=4)
    
    db_session.close()
    return result

if __name__ == '__main__':
    main()

