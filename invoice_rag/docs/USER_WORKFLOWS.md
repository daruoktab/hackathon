# 📱 How to Use Your Invoice Bot

This guide shows you exactly how to use the Invoice Bot on Telegram to track your spending effortlessly.

---

## 🎯 What This Bot Does

**Simply put:** Take a photo of any receipt, send it to the bot, and it automatically tracks your spending!

**You get:**
- 📸 Automatic expense tracking from photos
- 📊 Beautiful spending dashboards
- 💰 Budget alerts to keep you on track
- 🤖 AI assistant to answer money questions

---

## 📱 Getting Started (First Time)

### Step 1: Start the Bot

1. Open Telegram
2. Search for your bot (ask your admin for the bot name)
3. Click **Start** or send `/start`
4. You'll see a welcome message with menu buttons

### Step 2: Set Your Budget (Optional but Recommended)

Set how much you want to spend per month:

```
You: /set_limit 5000000
Bot: ✅ Monthly spending limit set to Rp 5,000,000
     You'll be notified when your spending approaches this limit.
```

**That's it! You're ready to start tracking.**

---

## 📸 Daily Use: Tracking Your Expenses

### How to Add an Invoice

**Super Easy - Just 3 Steps:**

1. **Take a photo** of your receipt (at the shop, restaurant, etc.)
2. **Send the photo** to the bot (just like sending to a friend)
3. **Wait 5-10 seconds** - Done!

**Example:**

**Example:**

```
You: [Send photo of receipt]
Bot: Processing your invoice... Please wait.

Bot: ✅ Invoice processed successfully!
     
     📅 Date: 2025-10-22
     🏢 Vendor: Alfamart
     💰 Total Amount: Rp 125,500
     📝 Items: 3 items
     
     Use /analysis to see your invoice analysis.
```

**What the Bot Extracts Automatically:**
- 📅 Date of purchase
- 🏢 Store/shop name
- 💰 Total amount you paid
- 📝 Items you bought

**No commands needed - just send the photo!**

### If You're Near Your Budget Limit

The bot will automatically warn you:

```
Bot: ⚡ ALERT: You're approaching your monthly spending limit!
     
     Monthly Limit: Rp 5,000,000
     Total Spent: Rp 4,650,000
     Remaining: Rp 350,000
     Usage: 93.0%
```

---

## 📊 Checking Your Spending

### See Your Overview

**Quick Summary:**
```
You: /analysis
Bot: 📊 Invoice Summary
     Total Invoices: 25
     Total Spent: Rp 5,234,500
     Average Amount: Rp 209,380
     
     Top Vendors:
     • Alfamart: Rp 1,250,000
     • Indomaret: Rp 890,000
     • Shopee: Rp 650,000
     
     📊 Generating dashboard...
     [Bot sends a beautiful visual dashboard with charts]
```

**The dashboard shows you:**
- 💰 How much you've spent total
- 📊 Your weekly average
- 🏪 Which stores you shop at most
- 💳 Your budget status (with color: green = good, red = over)
- 📈 Spending trends over time
- 📅 Daily breakdown

### See Recent Transactions

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
     [Shows your last 5 purchases]
```

### Check Your Budget Status

```
You: /check_limit
Bot: ✅ Monthly Spending Status
     
     Monthly Limit: Rp 5,000,000
     Total Spent: Rp 3,456,780
     Remaining: Rp 1,543,220
     Usage: 69.1%
```

---

## 🤖 Ask Questions to the AI

The bot has an AI assistant that can answer questions about your spending!

### One-Time Questions (Saves Your Credits)

**Default mode - best for most people:**

```
You: /chat How much did I spend at Alfamart this month?
Bot: 🤔 Thinking...
     Based on your data, you spent Rp 1,250,000 at Alfamart
     this month across 8 transactions. Your average purchase
     was Rp 156,250.
```

**More examples:**
- `/chat What's my biggest expense?`
- `/chat How much did I spend this week?`
- `/chat Which store do I visit most?`
- `/chat Am I spending more than last month?`

### Conversation Mode (For Deep Analysis)

If you want to have a back-and-forth conversation:

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

You: /chatmode off
Bot: ❌ Chat mode disabled.
```

**💡 Tip:** Use chat mode OFF by default to save money. Only turn it ON when you need detailed analysis.

---

## 💰 Managing Your Budget

### Setting Your Monthly Limit

```
You: /set_limit 5000000
Bot: ✅ Monthly spending limit set to Rp 5,000,000
     You'll be notified when your spending approaches
     or exceeds this limit.
```

### How Alerts Work

The bot automatically watches your spending:

| Your Spending | What Happens |
|--------------|--------------|
| Under 75% | ✅ All good - no alerts |
| 75-89% | ⚡ Getting close (no alert yet) |
| 90-99% | ⚠️ **Warning alert sent** |
| 100%+ | 🚫 **Over budget alert sent** |

**Example warning at 93%:**
```
Bot: ⚡ ALERT: You're approaching your monthly spending limit!
     
     Monthly Limit: Rp 5,000,000
     Total Spent: Rp 4,650,000
     Remaining: Rp 350,000
     Usage: 93.0%
```

### Changing Your Budget Anytime

You can update your budget whenever you want:

```
You: /set_limit 6000000
Bot: ✅ Monthly spending limit updated to Rp 6,000,000
```

---

## � All Available Commands

| Command | What It Does |
|---------|-------------|
| `/start` | Start the bot & show main menu |
| `/help` | Show help message |
| **Tracking** |
| Send photo | Add a new invoice (no command needed!) |
| `/recent_invoices` | See your last 5 purchases |
| **Analysis** |
| `/analysis` | See dashboard with charts & insights |
| `/check_limit` | Check your budget status |
| **Budget** |
| `/set_limit <amount>` | Set monthly spending limit |
| **AI Chat** |
| `/chat <question>` | Ask a one-time question |
| `/chatmode on/off` | Turn continuous chat ON or OFF |
| `/clear` | Clear chat history |

---

## � Tips for Best Results

### 📸 Taking Good Photos

✅ **DO:**
- Use good lighting (daylight is best)
- Keep your phone steady
- Make sure all text is visible
- Capture the whole receipt

❌ **DON'T:**
- Take photos in dim light
- Cut off parts of the receipt
- Include glare or shadows
- Use blurry photos

### 🎯 Smart Budget Tracking

1. **Set realistic budgets** - Don't set it too low or too high
2. **Check weekly** - Use `/analysis` every weekend to stay aware
3. **Act on alerts** - When you get a warning, review your spending
4. **Adjust as needed** - Change your budget if your situation changes

### 💬 Using the AI Chat Wisely

- **Keep chat mode OFF** by default (saves API costs)
- **Use `/chat`** for quick questions
- **Turn ON chat mode** only for detailed analysis sessions
- **Clear history** with `/clear` when you're done

---

## � Your Weekly Routine

**Here's how most people use the bot:**

**Monday - Friday:**
```
1. Buy something → Take photo → Send to bot
2. Get instant confirmation
3. Continue with your day
```

**Weekend:**
```
1. Send /analysis to see the week's spending
2. Review the dashboard
3. Ask AI if you have questions:
   - "Where did most of my money go?"
   - "How does this week compare to last week?"
4. Adjust next week's habits if needed
```

**End of Month:**
```
1. Final /analysis check
2. Screenshot the dashboard for records
3. Check /check_limit
4. Set next month's budget if you want to adjust
```

---

## ❓ Common Questions

**Q: Can I send multiple photos at once?**
A: Yes! Send them one by one, the bot processes each separately.

**Q: What if the photo is unclear?**
A: The bot will tell you it failed. Just retake with better lighting and try again.

**Q: Can I delete an invoice I added by mistake?**
A: Not directly in the bot. Ask your admin to help remove it from the database.

**Q: How much does chat mode cost?**
A: It uses API credits. That's why we recommend keeping it OFF and using `/chat` for single questions.

**Q: Can I use this with my family?**
A: Each person needs their own Telegram account and will have their own separate budget tracking.

**Q: How long does it keep my data?**
A: All your invoices are stored permanently until you ask to delete them.

---

## 🆘 Need Help?

**If something doesn't work:**
1. Try `/start` to restart the bot
2. Check if your photo is clear enough
3. Make sure you're connected to internet
4. Ask your admin for help

**For more technical details:**
- See [WORKFLOW_OVERVIEW.md](WORKFLOW_OVERVIEW.md) for system architecture
- See [README.md](../README.md) for developer documentation

---

**Ready to start? Send `/start` to your bot and take control of your spending! 🎉**
