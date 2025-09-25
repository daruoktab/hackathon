from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import os
from dotenv import load_dotenv
import sys
import asyncio
from pathlib import Path
from src.processor import process_invoice
from src.analysis import analyze_invoices
from src.database import get_db_session, Invoice
from telegram_bot.visualizations import get_visualization
from telegram_bot.spending_limits import (
    init_spending_limits_table,
    set_monthly_limit,
    get_monthly_limit,
    check_spending_limit
)

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

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
        ['/recent_invoices', '/visualizations'],
        ['/set_limit', '/check_limit'],
        ['/help']
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
        "/visualizations - View spending analysis graphs\n"
        "/set_limit - Set your monthly spending limit\n"
        "/check_limit - Check your spending against limit\n"
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
            
            # Check spending limit
            amount = invoice_data.get('total_amount', 0)
            status = check_spending_limit(update.effective_user.id, amount)
            
            # Send response
            response = (
                f"✅ Invoice processed successfully!\n\n"
                f"📅 Date: {invoice_data.get('invoice_date', 'Unknown')}\n"
                f"🏢 Vendor: {invoice_data.get('shop_name', 'Unknown')}\n"
                f"💰 Total Amount: Rp {amount:,.2f}\n"
                f"📝 Items: {len(invoice_data.get('items', []))} items\n\n"
                f"Use /view_summary to see your invoice analysis."
            )
            await update.message.reply_text(response)
            
            # Send spending limit warning if necessary
            if status['has_limit']:
                if status['exceeds_limit']:
                    warning = (
                        "⚠️ WARNING: This purchase exceeds your monthly spending limit!\n\n"
                        f"{status['message']}"
                    )
                    await update.message.reply_text(warning)
                elif status['percentage_used'] >= 90:
                    warning = (
                        "⚡ ALERT: You're approaching your monthly spending limit!\n\n"
                        f"{status['message']}"
                    )
                    await update.message.reply_text(warning)
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
    if not update.message or not update.message.text:
        return
        
    await update.message.reply_text(
        "Please send me an invoice image to process it, or use the commands below:\n"
        "/upload_invoice - Upload an invoice\n"
        "/view_summary - View analysis\n"
        "/visualizations - View spending analysis graphs\n"
        "/help - Get help"
    )

async def visualizations_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the visualizations command."""
    if not update.message:
        return
    
    try:
        # Generate and send visualization
        buf = get_visualization()
        await update.message.reply_text("📊 Generating invoice summary visualization...")
        await update.message.reply_photo(buf)
    except Exception as e:
        await update.message.reply_text(f"❌ Error generating visualization: {str(e)}")

async def set_limit_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the set limit command."""
    if not update.message or not update.effective_user:
        return
        
    if not context.args:
        await update.message.reply_text(
            "Please provide your monthly spending limit in Rupiah.\n"
            "Example: /set_limit 5000000 (for Rp 5,000,000)"
        )
        return
        
    try:
        limit = float(context.args[0])
        if limit <= 0:
            await update.message.reply_text("❌ Spending limit must be greater than 0.")
            return
            
        if set_monthly_limit(update.effective_user.id, limit):
            await update.message.reply_text(
                f"✅ Monthly spending limit set to Rp {limit:,.2f}\n\n"
                f"You'll be notified when your spending approaches or exceeds this limit."
            )
        else:
            await update.message.reply_text("❌ Failed to set spending limit. Please try again.")
            
    except ValueError:
        await update.message.reply_text("❌ Please provide a valid number for the spending limit.")

async def check_limit_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the check limit command."""
    if not update.message or not update.effective_user:
        return
    
    # Get monthly limit
    monthly_limit = get_monthly_limit(update.effective_user.id)
    if not monthly_limit:
        await update.message.reply_text("No spending limit set. Use /set_limit to set one.")
        return
    
    # Get total spent from analyze_invoices
    try:
        analysis = analyze_invoices()
        total_spent = analysis['total_spent']
        
        # Calculate percentage and remaining
        percentage_used = (total_spent / monthly_limit) * 100
        remaining = monthly_limit - total_spent
        
        # Determine status indicator
        if percentage_used >= 100:
            indicator = "🚫"  # Red cross for over limit
        elif percentage_used >= 90:
            indicator = "⚠️"  # Warning for near limit
        elif percentage_used >= 75:
            indicator = "⚡"  # Getting close
        else:
            indicator = "✅"  # Good standing
        
        # Format message
        message = (
            f"{indicator} Monthly Spending Status\n\n"
            f"Monthly Limit: Rp {monthly_limit:,.2f}\n"
            f"Total Spent: Rp {total_spent:,.2f}\n"
            f"Remaining: Rp {remaining:,.2f}\n"
            f"Usage: {percentage_used:.1f}%"
        )
        
        await update.message.reply_text(message)
        
    except Exception as e:
        await update.message.reply_text(f"❌ Error checking limit: {str(e)}")

async def main() -> None:
    """Start the bot."""
    print("Starting bot...")
    
    if not TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN not found in environment variables")
        return
    
    # Initialize spending limits table
    init_spending_limits_table()
        
    # Create the Application and pass it your bot's token
    application = Application.builder().token(TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("view_summary", view_summary))
    application.add_handler(CommandHandler("recent_invoices", recent_invoices))
    application.add_handler(CommandHandler("upload_invoice", upload_invoice))
    application.add_handler(CommandHandler("visualizations", visualizations_command))
    application.add_handler(CommandHandler("set_limit", set_limit_command))
    application.add_handler(CommandHandler("check_limit", check_limit_command))
    
    # Handle photo messages (invoice images)
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    # Handle other messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is ready to serve!")
    print("Press Ctrl-C to stop the bot")
    
    # Start the Bot with proper shutdown handling
    try:
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except (KeyboardInterrupt, SystemExit):
        print("\nBot is shutting down...")
    finally:
        print("Cleanup complete. Bot stopped.")

if __name__ == "__main__":
    asyncio.run(main())
