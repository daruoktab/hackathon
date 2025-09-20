from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import os
from dotenv import load_dotenv
import sys
import asyncio
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.processor import process_invoice
from src.analysis import analyze_invoices
from src.database import get_db_session, Invoice

# Load environment variables from .env file
load_dotenv()

# Get the bot token from environment variables
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    if not update.message:
        return
        
    keyboard = [
        ['/upload_invoice', '/view_summary'],
        ['/recent_invoices', '/help']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        'Hello! I am your invoice processing bot. You can:\n'
        '• Upload an invoice image for processing\n'
        '• View invoice summaries and analysis\n'
        '• Check your recent invoices\n'
        '\nUse the keyboard below or type /help for more information.',
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    if not update.message:
        return
        
    help_text = (
        "Here are all available commands:\n\n"
        "/start - Start the bot and show main menu\n"
        "/upload_invoice - Upload an invoice image for processing\n"
        "/view_summary - View summary of all your invoices\n"
        "/recent_invoices - Show your 5 most recent invoices\n"
        "/help - Show this help message\n\n"
        "To process an invoice, simply send me an image of your invoice!"
    )
    await update.message.reply_text(help_text)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle invoice photos sent by users."""
    if not update.message or not update.effective_user:
        return
        
    # Get the largest photo (best quality)
    photo = update.message.photo[-1]
    
    # Download the photo
    file = await context.bot.get_file(photo.file_id)
    temp_path = f"temp_{update.effective_user.id}.jpg"
    await file.download_to_drive(temp_path)
    
    try:
        # Process the invoice
        await update.message.reply_text("Processing your invoice... Please wait.")
        invoice_data = process_invoice(temp_path)
        
        if invoice_data:
            # Use the processor's database saving function
            from src.processor import save_to_database_robust
            save_to_database_robust(invoice_data, temp_path)
            
            # Send response
            response = (
                f"✅ Invoice processed successfully!\n\n"
                f"📅 Date: {invoice_data.get('invoice_date', 'Unknown')}\n"
                f"🏢 Vendor: {invoice_data.get('shop_name', 'Unknown')}\n"
                f"💰 Total Amount: Rp {invoice_data.get('total_amount', 0):,.2f}\n"
                f"📝 Items: {len(invoice_data.get('items', []))} items\n\n"
                f"Use /view_summary to see your invoice analysis."
            )
            await update.message.reply_text(response)
        else:
            await update.message.reply_text("❌ Failed to process invoice. Please try again with a clearer image.")
        
    except Exception as e:
        await update.message.reply_text(f"❌ Error processing invoice: {str(e)}")
    
    finally:
        # Cleanup
        if os.path.exists(temp_path):
            os.remove(temp_path)

async def view_summary(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show invoice summary and analysis."""
    if not update.message:
        return
        
    try:
        analysis = analyze_invoices()
        
        summary = (
            "📊 Invoice Summary\n\n"
            f"Total Invoices: {analysis['total_invoices']}\n"
            f"Total Spent: Rp {analysis['total_spent']:,.2f}\n"
            f"Average Amount: Rp {analysis['average_amount']:,.2f}\n\n"
            "Top Vendors:\n"
        )
        
        for vendor in analysis['top_vendors'][:3]:
            summary += f"• {vendor['name']}: Rp {vendor['total']:,.2f}\n"
        
        await update.message.reply_text(summary)
        
    except Exception as e:
        await update.message.reply_text(f"❌ Error getting summary: {str(e)}")

async def recent_invoices(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show recent invoices."""
    if not update.message:
        return
        
    try:
        session = get_db_session()
        invoices = session.query(Invoice).order_by(Invoice.processed_at.desc()).limit(5).all()
        
        if not invoices:
            await update.message.reply_text("No invoices found in the database.")
            return
            
        response = "🧾 Your Recent Invoices:\n\n"
        for inv in invoices:
            response += (
                f"📅 {inv.invoice_date or 'Unknown date'}\n"
                f"🏢 {inv.shop_name}\n"
                f"💰 Rp {inv.total_amount:,.2f}\n"
                "───────────────\n"
            )
        
        await update.message.reply_text(response)
        
    except Exception as e:
        await update.message.reply_text(f"❌ Error fetching recent invoices: {str(e)}")

async def upload_invoice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Guide users on how to upload an invoice."""
    if not update.message:
        return
        
    guide = (
        "📸 Cara Upload Invoice:\n\n"
        "1. Pastikan invoice dalam bentuk gambar yang jelas\n"
        "2. Foto atau scan invoice Anda\n"
        "3. Kirim gambar langsung ke bot ini\n"
        "4. Tunggu proses analisis selesai\n\n"
        "Tips:\n"
        "• Pastikan gambar terang dan tidak blur\n"
        "• Semua informasi penting harus terbaca\n"
        "• Format yang didukung: JPG, PNG\n\n"
        "Silakan kirim gambar invoice Anda sekarang! 📸"
    )
    await update.message.reply_text(guide)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle text messages."""
    if not update.message:
        return
        
    await update.message.reply_text(
        "Please send me an invoice image to process it, or use the commands below:\n"
        "/upload_invoice - Upload an invoice\n"
        "/view_summary - View analysis\n"
        "/help - Get help"
    )

async def main() -> None:
    """Start the bot."""
    print("Starting bot...")
    
    if not TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN not found in environment variables")
        return
        
    # Create the Application and pass it your bot's token
    application = Application.builder().token(TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("view_summary", view_summary))
    application.add_handler(CommandHandler("recent_invoices", recent_invoices))
    application.add_handler(CommandHandler("upload_invoice", upload_invoice))
    
    # Handle photo messages (invoice images)
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    # Handle other messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is ready to serve!")
    print("Press Ctrl-C to stop the bot")
    
    # Start the Bot
    await application.run_polling()  # type: ignore
