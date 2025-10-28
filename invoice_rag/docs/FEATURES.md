# 🎯 UrFinance Telegram Bot - Final Key Features

**Your Personal AI-Powered Finance Assistant on Telegram**

Track spending effortlessly with AI-powered receipt scanning, instant insights, smart budget alerts, and professional spreadsheet exports - all from your phone.

---

## 🆕 Latest Features (October 2025)

### 📊 **Spreadsheet Export Integration** (NEW!)
- **📥 Excel Export**: Download your analysis as a professional Excel file with 4 comprehensive sheets
- **🌐 Google Sheets Export**: Create live, shareable spreadsheets with auto-permissions
- **🎛️ Interactive Buttons**: Export directly from `/analysis` command with inline keyboard
- **📈 4 Data Sheets**: Summary, Top Vendors, Weekly Breakdown, and All Invoices
- **☁️ Cloud Integration**: Full Google Sheets API integration with service account

### 🎨 **Adaptive Dashboard Intelligence** (NEW!)
- **📅 Smart Time Granularity**: Automatically switches between daily/weekly views based on data
- **💳 Budget Status Cards**: Color-coded budget tracking (Green/Orange/Red)
- **📊 Enhanced Visualizations**: Professional charts with proper formatting and labels
- **🎯 Contextual Insights**: AI-generated observations tailored to your spending patterns

### 🤖 **Advanced Chat Features** (NEW!)
- **💬 Chat Mode Toggle**: Switch between one-off queries and continuous conversation
- **🔄 Multi-turn Function Calling**: Bot remembers context across conversations
- **💰 Cost Optimization**: Chat mode OFF by default to save API costs
- **📝 Smart History**: Maintains last 10 exchanges with automatic truncation

---

## 🌟 Core Features

### 1. 📸 Instant Receipt Processing

**Snap, Send, Done!**

- **📷 One-Tap Upload**: Just take a photo and send - no commands needed
- **🤖 AI-Powered Extraction**: Automatically reads and extracts all receipt details
- **⚡ Fast Processing**: Get results in 5-10 seconds
- **✅ Smart Validation**: Handles various formats, dates, and currencies
- **🏷️ Auto-Categorization**: Detects transaction type (Bank/Retail/E-commerce)

**What Gets Extracted:**
- 📅 Date of purchase
- 🏢 Store/vendor name
- 💰 Total amount
- 📝 Individual line items with quantities and prices
- 💳 Transaction type

**Example:**
```
You: [Send photo of Alfamart receipt]
Bot: ✅ Invoice processed successfully!
     
     📅 Date: 2025-10-22
     🏢 Vendor: Alfamart
     💰 Total Amount: Rp 125,500
     📝 Items: 3 items
     
     Use /analysis to see your invoice analysis.
```

---

### 2. 📊 Beautiful Visual Dashboards

**See Your Money Story at a Glance**

Get comprehensive visual analysis with the `/analysis` command:

#### 4-Panel KPI Dashboard
1. **💰 Total Spending** - Your complete expense summary
2. **📊 Weekly Average** - How much you spend per week
3. **🏪 Top Vendor** - Where most of your money goes
4. **💳 Budget Status** - Color-coded budget tracker (🟢 Safe / 🟠 Warning / 🔴 Over)

#### Interactive Charts
- **📈 Spending Trend Line** - See how your spending changes over time
- **🏬 Top 5 Vendors Bar Chart** - Your most frequented shops ranked
- **💳 Transaction Type Pie Chart** - Bank vs Retail vs E-commerce breakdown
- **📅 Daily Spending Bars** - Track your daily expense patterns

#### AI-Generated Insights
- Smart observations about your spending habits
- Budget status warnings and recommendations
- Trend analysis and pattern detection

**Example Output:**
```
Bot: 📊 Invoice Summary
     
     Total Invoices: 25
     Total Spent: Rp 5,234,500
     Average Amount: Rp 209,380
     
     Top Vendors:
     • Alfamart: Rp 1,250,000
     • Indomaret: Rp 890,000
     • Shopee: Rp 650,000
     
     📊 Generating dashboard...
     [Sends beautiful visual dashboard image]
```

---

### 3. 💰 Smart Budget Management

**Stay in Control with Intelligent Alerts**

#### Budget Setting
- **Easy Setup**: `/set_limit 5000000` (for Rp 5,000,000/month)
- **Flexible Adjustments**: Change anytime as your needs evolve
- **Per-User Tracking**: Each user has their own budget

#### Automatic Monitoring
The bot continuously watches your spending and alerts you:

| Spending Level | Status | Action |
|---------------|--------|--------|
| Under 75% | ✅ Safe Zone | No alerts - you're doing great! |
| 75-89% | ⚡ Getting Close | Heads up - monitor your spending |
| 90-99% | ⚠️ Warning | Alert sent - approaching limit |
| 100%+ | 🚫 Over Budget | Alert sent - limit exceeded |

#### Real-Time Alerts
```
When you reach 93% of budget:

Bot: ⚡ ALERT: You're approaching your monthly spending limit!
     
     Monthly Limit: Rp 5,000,000
     Total Spent: Rp 4,650,000
     Remaining: Rp 350,000
     Usage: 93.0%
```

#### Budget Checking
```
You: /check_limit
Bot: ✅ Monthly Spending Status
     
     Monthly Limit: Rp 5,000,000
     Total Spent: Rp 3,456,780
     Remaining: Rp 1,543,220
     Usage: 69.1%
```

---

### 4. 🤖 AI Chat Assistant

**Ask Anything About Your Finances**

Powered by Groq AI (Meta-Llama models), the bot can answer complex questions about your spending:

#### Two Chat Modes

**1. One-Off Queries** (Default - Saves API Costs)
```
You: /chat How much did I spend at Alfamart this month?
Bot: 🤔 Thinking...
     Based on your data, you spent Rp 1,250,000 at Alfamart
     this month across 8 transactions. Your average purchase
     was Rp 156,250.
```

**2. Continuous Conversation Mode**
```
You: /chatmode on
Bot: ✅ Chat mode enabled!
     I'll now respond to all your messages.

You: What's my biggest expense?
Bot: Your biggest single expense was Rp 850,000 at
     Electronic City on Oct 15, 2025.

You: Should I be worried?
Bot: That's 17% of your monthly budget. As long as it's
     a planned purchase, you're still on track...
```

#### Smart Queries You Can Ask
- 💬 **Spending Analysis**: "How much did I spend this week?"
- 🏪 **Vendor Insights**: "Which store do I shop at most?"
- 📊 **Comparisons**: "Am I spending more than last month?"
- 🎯 **Budget Help**: "How much can I still spend this month?"
- 💡 **Recommendations**: "Where can I cut costs?"
- 📈 **Trends**: "What's my spending trend looking like?"

#### Chat History Management
- **Context Memory**: Bot remembers your conversation
- **Clear History**: `/clear` to start fresh
- **Smart Limits**: Keeps last 10 exchanges (prevents token overflow)

---

### 5. 📋 Quick Access Features

#### Recent Invoices
```
You: /recent_invoices
Bot: 🧾 Your Recent Invoices:
     
     📅 2025-10-20
     🏢 Alfamart
     💰 Rp 125,500
     ───────────────
     📅 2025-10-19
     🏢 Shopee
     💰 Rp 450,000
     ───────────────
     [Shows last 5 transactions]
```

#### Command Menu
Simple keyboard interface with all commands:
- 💰 Budget: `/set_limit`, `/check_limit`
- 📊 Analysis: `/analysis`, `/recent_invoices`
- 💬 AI Chat: `/chat`, `/chatmode`, `/clear`
- ℹ️ Help: `/help`, `/start`

#### Context-Aware Help
```
You: /help
Bot: [Shows comprehensive command guide with examples]
     
     • Organized by category
     • Usage examples for each command
     • Quick tips and best practices
```

---

## 🎨 User Experience Highlights

### ✨ Intuitive Design
- **No Learning Curve**: Send photos like you'd send to a friend
- **Visual Feedback**: Emojis and formatting make data easy to scan
- **Smart Defaults**: Chat mode OFF to save costs, only enable when needed
- **Helpful Prompts**: Bot guides you at every step

### ⚡ Performance
- **Fast Processing**: 5-10 seconds from photo to saved data
- **Reliable**: Handles network issues gracefully
- **Scalable**: Works with hundreds of invoices
- **Efficient**: Smart caching and database optimization

### 🔒 Data Privacy
- **Local Storage**: All data stored in your own SQLite database
- **No Cloud Upload**: Images processed then deleted
- **Per-User Isolation**: Each user's data is completely separate
- **Transparent**: Open source code you can audit

---

## 💡 Smart Capabilities

### Intelligent Data Processing
- **Multi-Format Support**: JPG, JPEG, PNG images
- **Various Receipt Types**: Paper receipts, digital invoices, e-receipts
- **Flexible Date Parsing**: Handles DD/MM/YYYY, YYYY-MM-DD, etc.
- **Currency Flexibility**: Parses Rp, IDR, with/without dots/commas
- **Error Recovery**: Retries and fallbacks for unclear images

### Advanced Analysis
- **Trend Detection**: Identifies spending patterns over time
- **Vendor Ranking**: Shows where you spend most frequently
- **Category Breakdown**: Analyzes by transaction type
- **Time-Based Insights**: Daily, weekly, monthly aggregations
- **Budget Compliance**: Tracks against your set limits

### AI-Powered Features
- **Natural Language Understanding**: Ask questions in plain language
- **Context-Aware Responses**: Remembers conversation history
- **Intelligent Insights**: Provides actionable recommendations
- **Pattern Recognition**: Spots unusual spending behaviors
- **Predictive Warnings**: Alerts before you exceed budget

---

## 🚀 Getting Started

### Quick Setup (2 Minutes)

1. **Find the Bot on Telegram**
   - Search for your bot username
   - Or click your bot's t.me link

2. **Initialize**
   ```
   You: /start
   Bot: [Shows welcome message with menu]
   ```

3. **Set Your Budget**
   ```
   You: /set_limit 5000000
   Bot: ✅ Monthly spending limit set to Rp 5,000,000
   ```

4. **Upload First Receipt**
   - Take photo of any receipt
   - Send it to the bot
   - Get instant confirmation!

5. **Explore**
   ```
   /analysis - See your first dashboard
   /chat How much have I spent? - Try AI chat
   /help - Learn all features
   ```

---

## � Spreadsheet Export Features (NEW!)

### Excel Export
**Instant Download with Comprehensive Data**

When you click "📥 Export to Excel" after `/analysis`:

**4 Professional Sheets:**
1. **Summary Sheet**
   - Total Spent, Total Invoices, Average Amount
   - Trend analysis (Increasing/Decreasing/Stable)
   - Trend percentage change
   - Weekly and Daily averages

2. **Top Vendors Sheet**
   - Vendor name and total spending
   - Transaction count per vendor
   - Average spending per vendor

3. **Weekly Breakdown Sheet**
   - Week-by-week analysis
   - Date ranges for each week
   - Total spent, transaction count, and average per week

4. **All Invoices Sheet**
   - Complete transaction history (last 50 invoices)
   - Date, Vendor, Amount, Transaction Type
   - Processing timestamp

**Example:**
```
You: /analysis
Bot: [Sends dashboard]
     📋 Do you want to export this analysis to a spreadsheet?
     [📥 Export to Excel] [📊 Export to Google Sheets] [❌ No, thanks]

You: [Click "📥 Export to Excel"]
Bot: 📥 Generating Excel file...
     [Sends: UrFinance_Analysis_2025-10-22_12-30.xlsx]
     ✅ Excel file generated successfully!
```

### Google Sheets Export
**Live, Shareable Spreadsheets in the Cloud**

When you click "📊 Export to Google Sheets":

**Features:**
- 📊 Creates new Google Spreadsheet in your account
- 🔗 Auto-sharing with view/edit permissions
- ☁️ Accessible from anywhere
- 📱 Works on mobile, tablet, desktop
- 🔄 Can be updated and shared with others

**Sheets Created:**
1. Summary with key metrics
2. Top Vendors ranking
3. Weekly breakdown with trends
4. Complete invoice list

**Example:**
```
You: /analysis
Bot: [Sends dashboard with export options]

You: [Click "📊 Export to Google Sheets"]
Bot: 📊 Creating Google Spreadsheet...
     
     ✅ Spreadsheet created successfully!
     📊 Title: UrFinance Analysis - 2025-10-22 12:30
     🔗 Link: https://docs.google.com/spreadsheets/d/...
     
     You can view and edit this spreadsheet online!
```

**Setup Required:**
- Google Cloud Project with Sheets API enabled
- Service Account credentials
- See [GOOGLE_SHEETS_SETUP.md](GOOGLE_SHEETS_SETUP.md) for details

---

## 🎨 Adaptive Dashboard Intelligence (NEW!)

### Smart Time Granularity

**Automatically Adjusts Based on Your Data**

The dashboard intelligently switches between daily and weekly views:

**Daily View** (Short-term data):
- Used when: Less than 14 days of data or fewer than 2 weeks
- Shows: Day-by-day spending breakdown
- Charts: Daily spending bars with specific dates
- Perfect for: Recent tracking, new users

**Weekly View** (Long-term data):
- Used when: 14+ days of data with 2+ weeks
- Shows: Week-by-week spending trends
- Charts: Weekly aggregations with date ranges
- Perfect for: Established users, pattern analysis

**Adaptive Insights:**
```
Short-term data:
"📊 Insights: Spending ↑ 15% | Daily avg: Rp 150K | Budget: 45% used"

Long-term data:
"📊 Insights: Spending stable | Weekly avg: Rp 1.2M | Daily avg: Rp 171K | Budget: 68% used"
```

### Enhanced Budget Cards

**Color-Coded Visual Indicators**

The 4th KPI card shows your budget status with smart colors:

- **🟢 Green (Under 75%)**: "Safe Zone" - You're doing great!
- **🟠 Orange (75-99%)**: "Warning Zone" - Watch your spending
- **🔴 Red (100%+)**: "Over Budget" - Exceeded limit
- **⚪ Gray**: "Not Set" - No budget configured

**Example Dashboard:**
```
┌─────────────┬─────────────┬─────────────┬─────────────┐
│ Total Spent │  Invoices   │ Avg Amount  │   Budget    │
│  Rp 3.5M    │     25      │  Rp 140K    │ 🟢 70% Used │
└─────────────┴─────────────┴─────────────┴─────────────┘
```

### Professional Formatting

**Beautiful, Readable Numbers**

All amounts now use smart formatting:
- **Millions**: Rp 5.2M (instead of Rp 5,200,000)
- **Thousands**: Rp 850K (instead of Rp 850,000)
- **Small amounts**: Rp 125 (exact value)

**Applied everywhere:**
- Dashboard KPI cards
- Chart axis labels
- Excel exports
- AI insights footer

---

## 💬 Advanced Chat System (NEW!)

### Chat Mode Management

**Two Modes for Different Needs**

**Default Mode (Chat OFF):**
- Saves API costs
- Use `/chat <question>` for one-time queries
- Bot only responds to commands
- Perfect for daily use

**Continuous Mode (Chat ON):**
- Enable with `/chatmode on`
- All messages get AI responses
- Full conversation context
- Great for deep analysis sessions

**Example Usage:**
```
Checking Status:
You: /chatmode
Bot: 💬 Chat Mode Status: OFF ❌
     
     Usage:
     • /chatmode on - Enable continuous chat
     • /chatmode off - Disable (save API costs)
     • /chat <message> - One-off AI query (works anytime)

Enabling Chat Mode:
You: /chatmode on
Bot: ✅ Chat mode enabled!
     
     I'll now respond to all your messages. Just type naturally.
     Use /chatmode off to disable.

Continuous Conversation:
You: How much did I spend this week?
Bot: Based on your data, you spent Rp 1,250,000 this week...

You: Is that more than last week?
Bot: Yes, that's 15% more than last week's Rp 1,087,000...

You: What can I do to reduce it?
Bot: Here are some suggestions based on your patterns...

Disabling:
You: /chatmode off
Bot: ❌ Chat mode disabled.
     
     I'll only respond to commands now.
     Use /chat <message> for one-off AI queries.
```

### Multi-turn Function Calling

**Intelligent Context Management**

The bot now maintains conversation context:
- Remembers last 10 exchanges (20 messages)
- Understands follow-up questions
- Links queries to previous answers
- Automatic context cleanup to prevent token overflow

**Smart Features:**
- Context window management
- Automatic history truncation
- User-specific conversation storage
- `/clear` command to reset

---

## �📱 Use Cases

### Daily Shopper
"I shop almost every day at local stores. The bot automatically tracks everything so I don't have to remember or keep paper receipts."

**Perfect For:**
- Grocery shopping tracking
- Daily expense monitoring
- Impulse purchase awareness

### Budget-Conscious User
"I set a monthly limit and the bot warns me when I'm getting close. It's like having a personal finance advisor!"

**Perfect For:**
- Living within a budget
- Saving goals
- Expense discipline

### Small Business Owner
"I track business expenses by uploading supplier receipts. The dashboard shows me spending trends and top vendors. The Excel export makes monthly reports easy!"

**Perfect For:**
- Business expense tracking
- Vendor spending analysis
- Tax preparation documentation
- Monthly financial reports

### Family Finance Manager
"Each family member has their own bot instance. We can track who's spending what and stay within our household budget. Google Sheets export lets us share reports!"

**Perfect For:**
- Family budget management
- Teaching kids about spending
- Shared expense tracking
- Collaborative financial planning

---

## 🎯 Key Benefits

### For Users
- ⏱️ **Saves Time**: No manual entry - just snap and forget
- 💰 **Saves Money**: Budget alerts prevent overspending
- 📊 **Provides Clarity**: Visual dashboards show where money goes
- 🤖 **AI Assistance**: Get instant answers about your finances
- 📱 **Always Accessible**: Your finance assistant in your pocket

### Technical Excellence
- 🚀 **State-of-the-Art AI**: Uses latest Groq LLM technology
- 🎨 **Beautiful Visualizations**: Professional matplotlib charts
- 💾 **Reliable Storage**: Robust SQLite database
- 🔄 **Continuous Updates**: Active development and improvements
- 📖 **Well Documented**: Comprehensive user guides

---

## 🏆 Why Choose UrFinance Bot?

1. **🎯 Simplicity**: No complex interfaces - just send photos
2. **🤖 Intelligence**: AI understands your receipts and questions
3. **📊 Insights**: Beautiful dashboards reveal spending patterns
4. **💰 Control**: Budget alerts keep you on track
5. **⚡ Speed**: Process receipts in seconds
6. **🔒 Privacy**: Your data stays with you
7. **📱 Convenience**: Works in Telegram - no app to install
8. **💪 Powerful**: Advanced features when you need them
9. **🆓 Cost-Effective**: Minimal API costs with smart features
10. **📚 Supported**: Clear documentation and active updates
11. **📥 Professional Exports**: Excel & Google Sheets integration (NEW!)
12. **🎨 Adaptive Interface**: Smart dashboards adjust to your data (NEW!)
13. **💬 Flexible Chat**: Toggle between cost-saving and conversation modes (NEW!)

---

## 📊 Feature Comparison

| Feature | UrFinance Bot | Traditional Apps |
|---------|--------------|------------------|
| **Receipt Scanning** | ✅ AI-powered, instant | ⚠️ Manual or slow |
| **Setup Time** | ✅ 2 minutes | ❌ 10+ minutes |
| **AI Chat** | ✅ Natural language | ❌ Not available |
| **Budget Alerts** | ✅ Real-time, automatic | ⚠️ Manual checking |
| **Visual Dashboards** | ✅ Comprehensive + Adaptive | ⚠️ Basic charts |
| **Spreadsheet Export** | ✅ Excel + Google Sheets | ⚠️ CSV only |
| **Chat Mode Control** | ✅ Toggle ON/OFF | ❌ Always on |
| **Platform** | ✅ Telegram (no install) | ❌ Separate app |
| **Data Privacy** | ✅ Your database | ❌ Cloud storage |
| **Batch Processing** | ✅ CLI available | ❌ Not available |
| **Cost** | ✅ Free (API costs only) | ⚠️ Subscription |
| **Open Source** | ✅ Yes | ❌ Proprietary |

---

## 🎓 Advanced Tips

### Optimize API Costs
- Keep chat mode OFF by default (saves money!)
- Use `/chat` for one-off questions
- Only enable `/chatmode on` for deep analysis sessions
- Disable with `/chatmode off` when done
- Clear history with `/clear` to start fresh

### Best Photo Practices
- Use natural lighting when possible
- Hold phone steady and parallel
- Ensure all text is readable
- Avoid shadows and glare
- Capture full receipt including totals

### Maximize Insights
- Review `/analysis` weekly for patterns
- Set realistic budgets with `/set_limit`
- Use AI chat to understand spending trends
- Export to Excel for detailed analysis
- Share Google Sheets with accountant/family

### Professional Reporting
- Export to Excel for offline analysis
- Use Google Sheets for collaborative review
- Monthly exports for record-keeping
- Share spreadsheets with team/family
- Keep exports organized by date

### Batch Historical Data
- Save old receipts
- Process all at once via CLI: `python run.py`
- View complete history in dashboard
- Export to spreadsheet for comprehensive review

---

## 📞 Support & Documentation

- **User Guide**: [USER_WORKFLOWS.md](USER_WORKFLOWS.md) - Step-by-step workflows
- **Technical Docs**: [WORKFLOW_OVERVIEW.md](WORKFLOW_OVERVIEW.md) - System architecture
- **Quick Reference**: `/help` command in bot
- **Dashboard Guide**: [DASHBOARD_QUICK_GUIDE.md](DASHBOARD_QUICK_GUIDE.md)
- **Export Setup**: [GOOGLE_SHEETS_SETUP.md](GOOGLE_SHEETS_SETUP.md) - Google Sheets integration
- **Export Features**: [SPREADSHEET_EXPORT_IMPLEMENTATION.md](SPREADSHEET_EXPORT_IMPLEMENTATION.md) - Technical details

---

## 🎉 Start Tracking Today!

**Ready to take control of your finances?**

1. Open Telegram
2. Find UrFinance bot
3. Send `/start`
4. Upload your first receipt
5. Watch the magic happen! ✨

**Your personal AI finance assistant is waiting!** 💰📱

---

## 🎯 Complete Feature List

### 📸 Receipt Processing
- ✅ AI-powered OCR with Groq LLM
- ✅ Multi-format support (JPG, JPEG, PNG)
- ✅ Auto-extraction of dates, vendors, amounts, items
- ✅ Smart validation and standardization
- ✅ Auto-categorization (Bank/Retail/E-commerce)
- ✅ 5-10 second processing time

### 📊 Analysis & Visualization
- ✅ 4-panel KPI dashboard
- ✅ Adaptive time granularity (daily/weekly)
- ✅ Color-coded budget status
- ✅ Spending trend line charts
- ✅ Top vendors bar charts
- ✅ Transaction type pie charts
- ✅ Daily spending breakdown
- ✅ Recent transactions table
- ✅ AI-generated insights
- ✅ Professional number formatting (K/M suffixes)

### 💰 Budget Management
- ✅ Monthly spending limits
- ✅ Automatic threshold alerts (90%, 100%)
- ✅ Real-time budget tracking
- ✅ Color-coded status indicators
- ✅ Percentage usage display
- ✅ Remaining amount calculator

### 🤖 AI Chat Assistant
- ✅ Natural language queries
- ✅ Two-mode system (one-off/continuous)
- ✅ Chat mode toggle (`/chatmode on/off`)
- ✅ Multi-turn conversation support
- ✅ Context memory (last 10 exchanges)
- ✅ Cost optimization (default OFF)
- ✅ Smart history management
- ✅ `/clear` command for reset

### 📥 Spreadsheet Export
- ✅ Excel file generation (.xlsx)
- ✅ Google Sheets integration
- ✅ 4 comprehensive data sheets
- ✅ Summary, Vendors, Weekly, All Invoices
- ✅ Interactive inline keyboard
- ✅ Auto-sharing with permissions
- ✅ Downloadable files
- ✅ Cloud-accessible spreadsheets

### 📋 Quick Access
- ✅ Recent invoices view (last 5)
- ✅ Command keyboard menu
- ✅ Interactive buttons
- ✅ Context-aware help
- ✅ Error handling & recovery

### 💻 Developer Features
- ✅ CLI batch processing
- ✅ SQLite database
- ✅ Python-based architecture
- ✅ Modular design
- ✅ Comprehensive logging
- ✅ Error tracking
- ✅ Open source code

### 🔒 Security & Privacy
- ✅ Local data storage
- ✅ No cloud upload (images deleted after processing)
- ✅ Per-user isolation
- ✅ Service account authentication (Google)
- ✅ Transparent operations

---

## 📈 Version History

**Version 2.1** (October 22, 2025)
- ✅ Spreadsheet export (Excel + Google Sheets)
- ✅ Adaptive dashboard with smart time granularity
- ✅ Chat mode toggle system
- ✅ Multi-turn conversation support
- ✅ Enhanced budget tracking with color-coding
- ✅ Professional number formatting

**Version 2.0** (October 2025)
- ✅ Core AI receipt processing
- ✅ Visual dashboard with KPIs
- ✅ Budget management system
- ✅ AI chat assistant
- ✅ Telegram bot interface
- ✅ CLI batch processing

---

**UrFinance Telegram Bot**  
*Smart Finance Tracking, Simplified*

**Version 2.1** | October 2025 | Built with ❤️ using AI  
**Latest Update**: Spreadsheet Export & Adaptive Dashboard Intelligence
