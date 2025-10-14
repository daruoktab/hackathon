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

from src.processor import process_invoice  # noqa: E402
from src.database import get_db_session, Invoice  # noqa: E402
from src.chatbot import run_conversation  # noqa: E402
from src.analysis import analyze_invoices  # noqa: E402
from telegram_bot.spending_limits import (  # noqa: E402
    init_spending_limits_table,
    set_monthly_limit,
    get_monthly_limit,
    check_spending_limit,
)
from telegram_bot.visualizations import get_visualization  # noqa: E402

# Ensure imports are recognized by Pylance
__all__ = [
    'process_invoice',
    'get_db_session', 
    'Invoice',
    'run_conversation',
    'analyze_invoices',
    'init_spending_limits_table',
    'set_monthly_limit',
    'get_monthly_limit',
    'check_spending_limit',
    'get_visualization'
]

# Load environment variables from .env file
load_dotenv()

# Get the bot token from environment variables
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# In-memory chat history storage
chat_histories = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message when the command /start is issued."""
    if not update.message:
        return

    keyboard = [
        ['/upload_invoice', '/analysis'],
        ['/recent_invoices', '/visualizations'],
        ['/set_limit', '/check_limit'],
        ['/help']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    welcome_text = (
        "👋 Halo! Saya Asisten Keuangan Anda.\n\n"
        "Saya dapat membantu Anda dengan dua cara:\n\n"
        "🤖 **Chat dengan AI**\n"
        "Tanyakan apa saja tentang pengeluaran Anda dalam Bahasa Indonesia:\n"
        "• Berapa total pengeluaranku bulan ini?\n"
        "• Tunjukkan toko dengan pengeluaran terbesar\n"
        "• Bagaimana tren pengeluaranku?\n\n"
        "📋 **Perintah Cepat**\n"
        "Gunakan tombol di bawah untuk akses fitur:\n"
        "• 📸 Upload invoice\n"
        "• 📊 Lihat analisis & visualisasi\n"
        "• 🧾 Invoice terbaru\n"
        "• 💰 Kelola budget\n\n"
        "Ketik /help untuk bantuan lengkap!"
    )
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    if not update.message:
        return
        
    help_text = (
        "📱 **Bantuan Asisten Keuangan**\n\n"
        "**🤖 Chat dengan AI (Fitur Baru!)**\n"
        "Tanyakan apa saja tentang pengeluaran Anda dalam Bahasa Indonesia:\n"
        "• Berapa total pengeluaranku?\n"
        "• Toko mana yang paling boros?\n"
        "• Bagaimana tren pengeluaranku?\n"
        "• Buatkan analisis lengkap!\n\n"
        "**📋 Perintah yang Tersedia:**\n\n"
        "📸 **Kelola Invoice:**\n"
        "• /upload_invoice - Panduan upload invoice\n"
        "• Kirim foto langsung - Proses otomatis\n\n"
        "📊 **Analisis & Laporan:**\n"
        "• /analysis - Ringkasan pengeluaran\n"
        "• /visualizations - Dashboard grafik\n"
        "• /recent_invoices - 5 invoice terbaru\n\n"
        "💰 **Budget Management:**\n"
        "• /set_limit [jumlah] - Set budget bulanan\n"
        "• /check_limit - Cek status budget\n\n"
        "🔧 **Lainnya:**\n"
        "• /start - Menu utama\n"
        "• /help - Panduan ini\n"
        "• /clear - Hapus riwayat chat\n\n"
        "💡 **Tip:** Gabungkan chat AI dengan perintah untuk pengalaman terbaik!"
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
                f"Use /analysis to see your invoice analysis."
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

async def analysis_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show invoice summary and analysis, then send visualization."""
    if not update.message:
        return
        
    try:
        # Send text summary first
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

        # Then, generate and send the visualization
        await update.message.reply_text("📊 Generating your comprehensive analysis dashboard...")
        buf = get_visualization()
        await update.message.reply_photo(buf)
        
    except Exception as e:
        await update.message.reply_text(f"❌ Error getting summary or visualization: {str(e)}")

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
        "📸 How to Upload Invoice:\n\n"
        "1. Make sure the invoice image is clear\n"
        "2. Take a photo or scan your invoice\n"
        "3. Send the image directly to this bot\n"
        "4. Wait for the analysis to complete\n\n"
        "Tips:\n"
        "• Ensure the image is bright and not blurry\n"
        "• All important information must be readable\n"
        "• Supported formats: JPG, PNG\n\n"
        "Please send your invoice image now! 📸"
    )
    await update.message.reply_text(guide)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle text messages from users and respond using the chatbot."""
    if not update.message or not update.message.text or not update.effective_user:
        return

    message = update.message
    user_id = update.effective_user.id
    user_message = message.text
    
    # Ensure user_message is not None
    if not user_message:
        return

    # Get or create chat history for the user
    if user_id not in chat_histories:
        chat_histories[user_id] = []

    chat_history = chat_histories[user_id]

    # Get chatbot response
    sent_message = await message.reply_text("🤔 Mengetik...", parse_mode='Markdown')
    response_text = run_conversation(user_message, chat_history)
    
    # Update the "Typing..." message with the actual response
    if sent_message and sent_message.message_id:
        try:
            # Edit the "Typing..." message with the final response
            await context.bot.edit_message_text(
                chat_id=message.chat_id,
                message_id=sent_message.message_id, # The "Typing..." message
                text=response_text
            )
        except Exception:
             # Fallback to sending a new message if editing fails
            await message.reply_text(response_text)
    else:
        await message.reply_text(response_text)

    # Update chat history
    chat_history.append({"role": "user", "content": user_message})
    chat_history.append({"role": "assistant", "content": response_text})
    chat_histories[user_id] = chat_history  # Save back to main dict

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

async def visualizations_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send visualization dashboard to user."""
    if not update.message:
        return
        
    try:
        await update.message.reply_text("📊 Generating your comprehensive analysis dashboard...")
        buf = get_visualization()
        await update.message.reply_photo(buf)
    except Exception as e:
        await update.message.reply_text(f"❌ Error generating visualization: {str(e)}")

async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clears the user's chat history."""
    if not update.effective_user or not update.message:
        return
    
    user_id = update.effective_user.id
    if user_id in chat_histories:
        chat_histories[user_id] = []
        await update.message.reply_text("Riwayat percakapan Anda telah dihapus.")
    else:
        await update.message.reply_text("Tidak ada riwayat percakapan untuk dihapus.")

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
    application.add_handler(CommandHandler("analysis", analysis_command))
    application.add_handler(CommandHandler("recent_invoices", recent_invoices))
    application.add_handler(CommandHandler("upload_invoice", upload_invoice))
    application.add_handler(CommandHandler("visualizations", visualizations_command))
    application.add_handler(CommandHandler("set_limit", set_limit_command))
    application.add_handler(CommandHandler("check_limit", check_limit_command))
    application.add_handler(CommandHandler("clear", clear_command))
    
    # Handle photo messages (invoice images)
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    # Handle all other text messages with the chatbot
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
