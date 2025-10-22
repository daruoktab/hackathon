from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters, CallbackQueryHandler
import os
from dotenv import load_dotenv
import sys
import asyncio
from pathlib import Path
import pandas as pd
from io import BytesIO
from datetime import datetime

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.processor import process_invoice  # noqa: E402
from src.database import get_db_session, Invoice  # noqa: E402
from src.chatbot import run_conversation  # noqa: E402
from src.analysis import analyze_invoices, calculate_weekly_averages, analyze_spending_trends  # noqa: E402
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

# Chat mode state (per user) - Default: False (off) to save API costs
chat_modes = {}

# Maximum chat history to keep (prevent token overflow)
MAX_HISTORY = 10  # Keep last 10 exchanges (20 messages)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message when the command /start is issued."""
    if not update.message:
        return

    keyboard = [
        ['/set_limit', '/check_limit'],
        ['/upload_invoice', '/analysis', '/recent_invoices'],
        ['/chatmode', '/clear', '/help']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    welcome_text = (
        "👋 Hello! I'm your friendly Invoice Helper Bot!\n\n"
        "Let me help you keep track of your spending the easy way:\n"
        "📸 Send me a photo of your receipt or invoice\n"
        "📊 See where your money goes with simple charts\n"
        "💰 Set and track your monthly budget\n"
        "📋 Check your spending history\n\n"
        "💡 Just tap any button below to get started!\n"
        "🤖 Chat with AI for deep dive and quick summary\n\n"
        "Need help? Type /help for more details."
    )
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    if not update.message:
        return

    help_text = (
        "📱 Here's what I can help you with:\n\n"
        "💬 AI Chat Features:\n"
        "• /chat <message> - Ask AI one-off questions\n"
        "  Example: /chat What's my total spending?\n"
        "• /chatmode on - Enable continuous chat (uses API credits)\n"
        "• /chatmode off - Disable chat mode (save costs)\n"
        "• /chatmode - Check current status\n\n"
        "📸 Save & Process Receipts:\n"
        "• Just send me a photo of any receipt or invoice\n"
        "• Type /upload_invoice to start uploading\n\n"
        "💰 Track Your Spending:\n"
        "• /analysis - See your overall spending patterns and visualization\n"
        "• /recent_invoices - Check your latest 5 expenses\n\n"
        "🎯 Budget Management:\n"
        "• /set_limit - Set your monthly budget\n"
        "• /check_limit - See how much you've spent\n\n"
        "Other Commands:\n"
        "• /start - Return to main menu\n"
        "• /help - Show this helpful guide\n"
        "• /clear - Clear chat history\n\n"
        "💡 Quick Tips:\n"
        "• Chat mode is OFF by default (saves API costs)\n"
        "• Use /chat for quick AI questions\n"
        "• Send photos directly - no command needed!"
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

        # Then, generate and send the visualization with user_id
        await update.message.reply_text("📊 Generating your comprehensive analysis dashboard...")
        if update.effective_user and update.effective_user.id:
            buf = get_visualization(user_id=update.effective_user.id)
            await update.message.reply_photo(buf)
        
        # Ask if user wants to export to spreadsheet
        keyboard = [
            [
                InlineKeyboardButton("📥 Export to Excel", callback_data="export_excel"),
                InlineKeyboardButton("📊 Export to Google Sheets", callback_data="export_sheets")
            ],
            [InlineKeyboardButton("❌ No, thanks", callback_data="export_cancel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "📋 Do you want to export this analysis to a spreadsheet?",
            reply_markup=reply_markup
        )
        
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
    
    # Check if chat mode is enabled for this user
    chat_mode_enabled = chat_modes.get(user_id, False)
    
    if not chat_mode_enabled:
        # Chat mode is off - send helpful message without using LLM
        await message.reply_text(
            "💬 Hey! Chat mode is OFF right now.\n\n"
            "Quick options:\n"
            "• /chat <your question> - Ask me anything\n"
            "• /chatmode on - Let's have a conversation!\n"
            "• /help - See what I can do"
        )
        return

    # Get or create chat history for the user
    if user_id not in chat_histories:
        chat_histories[user_id] = []

    chat_history = chat_histories[user_id]

    # Get chatbot response
    sent_message = await message.reply_text("🤔 Typing...", parse_mode='Markdown')
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
    
    # Truncate history if too long
    if len(chat_history) > MAX_HISTORY * 2:
        chat_history = chat_history[-(MAX_HISTORY * 2):]
    
    chat_histories[user_id] = chat_history  # Save back to main dict

async def set_limit_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the set limit command."""
    if not update.message or not update.effective_user:
        return
        
    if not context.args:
        await update.message.reply_text(
            "Please provide your monthly spending limit in Rupiah.\n"
            "Example: 5000000 (for Rp 5,000,000)"
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
    if not update.message or not update.effective_user:
        return
        
    try:
        await update.message.reply_text("📊 Generating your comprehensive analysis dashboard...")
        buf = get_visualization(user_id=update.effective_user.id)
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
        await update.message.reply_text("Your chat history has been cleared.")
    else:
        await update.message.reply_text("No chat history to clear.")

async def chatmode_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Toggle chat mode on or off."""
    if not update.effective_user or not update.message:
        return
    
    user_id = update.effective_user.id
    
    # Check if user provided on/off argument
    if not context.args or len(context.args) == 0:
        # Show current status
        current_mode = chat_modes.get(user_id, False)
        status = "ON ✅" if current_mode else "OFF ❌"
        await update.message.reply_text(
            f"💬 Chat Mode Status: {status}\n\n"
            f"Usage:\n"
            f"• /chatmode on - Enable continuous chat\n"
            f"• /chatmode off - Disable (save API costs)\n"
            f"• /chat <message> - One-off AI query (works anytime)"
        )
        return
    
    mode = context.args[0].lower()
    
    if mode == "on":
        chat_modes[user_id] = True
        await update.message.reply_text(
            "✅ Chat mode enabled!\n\n"
            "I'll now respond to all your messages. Just type naturally.\n"
            "Use /chatmode off to disable."
        )
    elif mode == "off":
        chat_modes[user_id] = False
        await update.message.reply_text(
            "❌ Chat mode disabled.\n\n"
            "I'll only respond to commands now.\n"
            "Use /chat <message> for one-off AI queries."
        )
    else:
        await update.message.reply_text(
            "Invalid option. Use:\n"
            "• /chatmode on\n"
            "• /chatmode off"
        )

async def chat_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle one-off chat queries without enabling chat mode."""
    if not update.message or not update.effective_user:
        return
    
    user_id = update.effective_user.id
    
    # Check if user provided a message
    if not context.args or len(context.args) == 0:
        await update.message.reply_text(
            "Please provide a message after /chat\n\n"
            "Example: /chat What's my total spending?"
        )
        return
    
    # Join all arguments as the user message
    user_message = " ".join(context.args)
    
    # Get or create chat history
    if user_id not in chat_histories:
        chat_histories[user_id] = []
    
    chat_history = chat_histories[user_id]
    
    # Show typing indicator
    sent_message = await update.message.reply_text("🤔 Thinking...", parse_mode='Markdown')
    
    # Get chatbot response
    response_text = run_conversation(user_message, chat_history)
    
    # Update the typing message with actual response
    if sent_message and sent_message.message_id:
        try:
            await context.bot.edit_message_text(
                chat_id=update.message.chat_id,
                message_id=sent_message.message_id,
                text=response_text
            )
        except Exception:
            await update.message.reply_text(response_text)
    else:
        await update.message.reply_text(response_text)
    
    # Update chat history
    chat_history.append({"role": "user", "content": user_message})
    chat_history.append({"role": "assistant", "content": response_text})
    
    # Truncate history if too long
    if len(chat_history) > MAX_HISTORY * 2:
        chat_history = chat_history[-(MAX_HISTORY * 2):]
    
    chat_histories[user_id] = chat_history

async def export_to_excel(user_id: int, weeks_back: int = 8) -> BytesIO:
    """Generate Excel file with analysis data."""
    analysis = analyze_invoices(weeks_back=weeks_back)
    weekly_data = calculate_weekly_averages(weeks_back=weeks_back)
    trends = analyze_spending_trends(weeks_back=weeks_back)
    
    # Get recent invoices
    session = get_db_session()
    invoices = session.query(Invoice).order_by(Invoice.processed_at.desc()).limit(50).all()
    session.close()
    
    # Create Excel file in memory
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Summary sheet
        summary_df = pd.DataFrame([{
            'Total Spent (Rp)': analysis['total_spent'],
            'Total Invoices': analysis['total_invoices'],
            'Average Amount (Rp)': analysis['average_amount'],
            'Trend': trends['trend'],
            'Trend Percentage': f"{trends['trend_percentage']:.2f}%",
            'Weekly Average (Rp)': weekly_data['weekly_average'],
            'Daily Average (Rp)': weekly_data['daily_average']
        }])
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        # Top Vendors sheet
        vendors_data = []
        for vendor in analysis['top_vendors']:
            vendors_data.append({
                'Vendor': vendor['name'],
                'Total (Rp)': vendor['total'],
                'Count': vendor['transaction_count'],
                'Average (Rp)': vendor['total'] / vendor['transaction_count'] if vendor['transaction_count'] > 0 else 0
            })
        vendors_df = pd.DataFrame(vendors_data)
        vendors_df.to_excel(writer, sheet_name='Top Vendors', index=False)
        
        # Weekly Breakdown sheet
        weekly_breakdown = []
        for week, data in weekly_data['weekly_breakdown'].items():
            # Calculate average per transaction for this week
            avg_amount = data['total'] / data['count'] if data['count'] > 0 else 0
            weekly_breakdown.append({
                'Week': week,
                'Date Range': data['range'],
                'Total (Rp)': data['total'],
                'Count': data['count'],
                'Average (Rp)': avg_amount
            })
        weekly_df = pd.DataFrame(weekly_breakdown)
        weekly_df.to_excel(writer, sheet_name='Weekly Breakdown', index=False)
        
        # All Invoices sheet
        if invoices:
            invoices_data = []
            for inv in invoices:
                invoices_data.append({
                    'Date': inv.invoice_date,
                    'Vendor': inv.shop_name,
                    'Amount (Rp)': inv.total_amount,
                    'Transaction Type': inv.transaction_type,
                    'Processed At': inv.processed_at
                })
            invoices_df = pd.DataFrame(invoices_data)
            invoices_df.to_excel(writer, sheet_name='All Invoices', index=False)
    
    output.seek(0)
    return output

async def export_to_google_sheets(user_id: int, weeks_back: int = 8):
    """
    Export analysis to Google Sheets.
    This function will guide users through the Google Sheets setup.
    """
    try:
        import gspread  # type: ignore
        from oauth2client.service_account import ServiceAccountCredentials  # type: ignore
        
        # Check if credentials file exists
        credentials_path = Path(__file__).parent.parent / 'google_credentials.json'
        if not credentials_path.exists():
            return None, (
                "⚠️ Google Sheets integration is not configured.\n\n"
                "To set it up:\n"
                "1. Go to Google Cloud Console\n"
                "2. Enable Google Sheets API\n"
                "3. Create a Service Account\n"
                "4. Download credentials as 'google_credentials.json'\n"
                "5. Place it in the invoice_rag folder\n\n"
                "For now, you can use Excel export instead!"
            )
        
        # Authorize with Google Sheets
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name(str(credentials_path), scope)
        client = gspread.authorize(creds)
        
        # Create a new spreadsheet
        spreadsheet_name = f"UrFinance Analysis - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        spreadsheet = client.create(spreadsheet_name)
        
        # Get analysis data
        analysis = analyze_invoices(weeks_back=weeks_back)
        weekly_data = calculate_weekly_averages(weeks_back=weeks_back)
        trends = analyze_spending_trends(weeks_back=weeks_back)
        
        # Summary worksheet
        summary_sheet = spreadsheet.sheet1
        summary_sheet.update_title('Summary')
        summary_sheet.update('A1', [
            ['Metric', 'Value'],
            ['Total Spent (Rp)', analysis['total_spent']],
            ['Total Invoices', analysis['total_invoices']],
            ['Average Amount (Rp)', analysis['average_amount']],
            ['Trend', trends['trend']],
            ['Trend Percentage', f"{trends['trend_percentage']:.2f}%"],
            ['Weekly Average (Rp)', weekly_data['weekly_average']],
            ['Daily Average (Rp)', weekly_data['daily_average']]
        ])
        
        # Top Vendors worksheet
        vendors_sheet = spreadsheet.add_worksheet(title='Top Vendors', rows=100, cols=10)
        vendors_headers = [['Vendor', 'Total (Rp)', 'Count', 'Average (Rp)']]
        vendors_data = [[
            v['name'], 
            v['total'], 
            v['transaction_count'], 
            v['total'] / v['transaction_count'] if v['transaction_count'] > 0 else 0
        ] for v in analysis['top_vendors']]
        vendors_sheet.update('A1', vendors_headers + vendors_data)
        
        # Weekly Breakdown worksheet
        weekly_sheet = spreadsheet.add_worksheet(title='Weekly Breakdown', rows=100, cols=10)
        weekly_headers = [['Week', 'Date Range', 'Total (Rp)', 'Count', 'Average (Rp)']]
        weekly_rows = []
        for week, data in weekly_data['weekly_breakdown'].items():
            weekly_rows.append([week, data['range'], data['total'], data['count'], data['average']])
        weekly_sheet.update('A1', weekly_headers + weekly_rows)
        
        # Share with anyone who has the link (read-only access)
        spreadsheet.share('', perm_type='anyone', role='reader')
        
        return spreadsheet.url, None
        
    except ImportError:
        return None, (
            "⚠️ Google Sheets libraries not installed.\n\n"
            "To enable Google Sheets export, run:\n"
            "`pip install gspread oauth2client`\n\n"
            "For now, you can use Excel export instead!"
        )
    except Exception as e:
        error_msg = str(e)
        if "storage quota has been exceeded" in error_msg.lower():
            return None, (
                "❌ Google Drive storage is full!\n\n"
                "Solutions:\n"
                "1. Delete old files from Google Drive\n"
                "2. Empty Google Drive Trash\n"
                "3. Upgrade storage (or use another account)\n\n"
                "💡 Use Excel export instead - it works offline!"
            )
        elif "drive api" in error_msg.lower():
            return None, (
                "⚠️ Google Drive API not enabled.\n\n"
                "Enable it here:\n"
                "https://console.developers.google.com/apis/api/drive.googleapis.com\n\n"
                "Then click 'ENABLE' button.\n\n"
                "💡 Meanwhile, use Excel export!"
            )
        else:
            return None, f"❌ Error creating Google Sheet: {error_msg}\n\n💡 Try Excel export instead!"

async def handle_export_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle export button callbacks."""
    query = update.callback_query
    if not query or not update.effective_user:
        return
        
    await query.answer()
    
    if query.data == "export_cancel":
        await query.edit_message_text("👍 Export cancelled.")
        return
    
    user_id = update.effective_user.id
    
    if query.data == "export_excel":
        await query.edit_message_text("📥 Generating Excel file...")
        try:
            excel_file = await export_to_excel(user_id)
            filename = f"urfinance_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            # Type guard for message
            if query.message and hasattr(query.message, 'reply_document'):
                await query.message.reply_document(  # type: ignore
                    document=excel_file,
                    filename=filename,
                    caption="✅ Here's your spending analysis in Excel format!\n📊 Contains: Summary, Top Vendors, Weekly Breakdown, and All Invoices"
                )
            await query.edit_message_text("✅ Excel file sent successfully!")
            
        except Exception as e:
            await query.edit_message_text(f"❌ Error generating Excel file: {str(e)}")
    
    elif query.data == "export_sheets":
        await query.edit_message_text("📊 Creating Google Sheet...")
        try:
            sheet_url, error_msg = await export_to_google_sheets(user_id)
            
            if error_msg:
                await query.edit_message_text(error_msg)
            elif sheet_url:
                await query.edit_message_text(
                    f"✅ Google Sheet created successfully!\n\n"
                    f"🔗 Access your spreadsheet here:\n{sheet_url}\n\n"
                    f"📝 Note: You may need to request access if using a service account."
                )
            else:
                await query.edit_message_text("❌ Failed to create Google Sheet.")
                
        except Exception as e:
            await query.edit_message_text(f"❌ Error creating Google Sheet: {str(e)}")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors caused by Updates."""
    import logging
    import traceback
    from telegram.error import NetworkError, TimedOut, BadRequest, Forbidden
    
    # Get the logger
    logger = logging.getLogger(__name__)
    
    # Log the error
    logger.error("Exception while handling an update:", exc_info=context.error)
    
    # Get the full traceback
    if context.error:
        tb_list = traceback.format_exception(type(context.error), context.error, context.error.__traceback__)
        tb_string = "".join(tb_list)
    else:
        tb_string = "No traceback available"
    
    # Log detailed error information
    logger.error(f"Update: {update}")
    logger.error(f"Traceback:\n{tb_string}")
    
    # Handle specific error types
    error_message = None
    
    if isinstance(context.error, NetworkError):
        error_message = (
            "🔌 Network connection issue detected.\n"
            "The bot is experiencing connectivity problems. "
            "Please try again in a moment."
        )
        logger.warning("Network error occurred - bot will retry automatically")
        
    elif isinstance(context.error, TimedOut):
        error_message = (
            "⏱️ Request timed out.\n"
            "The operation took too long. Please try again."
        )
        logger.warning("Request timed out")
        
    elif isinstance(context.error, BadRequest):
        error_message = (
            "❌ Invalid request.\n"
            "Something went wrong with your request. Please try again."
        )
        logger.error(f"Bad request: {context.error}")
        
    elif isinstance(context.error, Forbidden):
        error_message = None  # User blocked the bot, can't send message
        logger.info("User has blocked the bot or chat is inaccessible")
        
    else:
        error_message = (
            "❌ An unexpected error occurred.\n"
            "The bot encountered an issue. Please try again later."
        )
        logger.error(f"Unexpected error: {type(context.error).__name__}: {context.error}")
    
    # Try to notify the user if possible
    if error_message and update and isinstance(update, Update):
        try:
            if update.effective_message:
                await update.effective_message.reply_text(error_message)
            elif update.callback_query:
                await update.callback_query.answer(error_message, show_alert=True)
        except Exception as e:
            # If we can't send the error message, just log it
            logger.error(f"Could not send error message to user: {e}")

async def main() -> None:
    """Start the bot."""
    import logging
    
    # Configure logging
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO,
        handlers=[
            logging.FileHandler('telegram_bot.log'),
            logging.StreamHandler()
        ]
    )
    
    # Set httpx logging to WARNING to reduce noise
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    
    logger = logging.getLogger(__name__)
    
    print("Starting bot...")
    logger.info("Bot initialization started")
    
    if not TOKEN:
        error_msg = "Error: TELEGRAM_BOT_TOKEN not found in environment variables"
        print(error_msg)
        logger.error(error_msg)
        return
    
    # Initialize spending limits table
    init_spending_limits_table()
        
    # Create the Application with enhanced network error handling
    application = (
        Application.builder()
        .token(TOKEN)
        .connect_timeout(30.0)  # Increased connection timeout
        .read_timeout(30.0)     # Increased read timeout
        .write_timeout(30.0)    # Increased write timeout
        .pool_timeout(30.0)     # Increased pool timeout
        .build()
    )

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("analysis", analysis_command))
    application.add_handler(CommandHandler("recent_invoices", recent_invoices))
    application.add_handler(CommandHandler("upload_invoice", upload_invoice))
    application.add_handler(CommandHandler("set_limit", set_limit_command))
    application.add_handler(CommandHandler("check_limit", check_limit_command))
    application.add_handler(CommandHandler("clear", clear_command))
    application.add_handler(CommandHandler("chat", chat_command))
    application.add_handler(CommandHandler("chatmode", chatmode_command))
    
    # Handle callback queries (for inline keyboard buttons)
    application.add_handler(CallbackQueryHandler(handle_export_callback))
    
    # Handle photo messages (invoice images)
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    # Handle all other text messages with the chatbot
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Register the error handler
    application.add_error_handler(error_handler)

    print("Bot is ready to serve!")
    print("Press Ctrl-C to stop the bot")
    logger.info("Bot started successfully - polling for updates")
    
    # Start the Bot with proper shutdown handling and network error recovery
    try:
        # Run polling with drop_pending_updates to avoid processing old updates
        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True,  # Skip pending updates on restart
            close_loop=False  # Don't close the event loop on shutdown
        )
    except KeyboardInterrupt:
        print("\nBot is shutting down...")
        logger.info("Bot shutdown requested by user")
    except SystemExit:
        print("\nBot is shutting down...")
        logger.info("Bot shutdown via system exit")
    except Exception as e:
        print(f"\nBot crashed with error: {e}")
        logger.critical(f"Bot crashed with unexpected error: {e}", exc_info=True)
    finally:
        print("Cleanup complete. Bot stopped.")
        logger.info("Bot stopped and cleaned up")

if __name__ == "__main__":
    asyncio.run(main())
