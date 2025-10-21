# Dashboard Enhancement - Visual Architecture

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Telegram Bot                              │
│  (telegram_bot/bot.py)                                           │
└────────────┬────────────────────────────────────────────────────┘
             │
             │ /analysis or /visualizations command
             │ passes user_id
             ▼
┌─────────────────────────────────────────────────────────────────┐
│           get_visualization(user_id=...)                         │
│  (telegram_bot/visualizations.py)                               │
└────────────┬────────────────────────────────────────────────────┘
             │
             │ delegates to
             ▼
┌─────────────────────────────────────────────────────────────────┐
│    create_comprehensive_dashboard(weeks_back, user_id)          │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  1. Fetch budget_status (if user_id provided)           │   │
│  │     ↓ check_spending_limit(user_id)                     │   │
│  │  2. Fetch invoice data                                   │   │
│  │     ↓ analyze_invoices(weeks_back)                      │   │
│  │  3. Calculate trends                                     │   │
│  │     ↓ analyze_spending_trends(weeks_back)               │   │
│  │  4. Get transaction types                                │   │
│  │     ↓ analyze_transaction_types(weeks_back)             │   │
│  │  5. Generate visualization                               │   │
│  │     ↓ matplotlib plotting                                │   │
│  │  6. Return BytesIO buffer                                │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

```
User Types Command
       │
       ▼
┌──────────────┐
│ Telegram Bot │ ─────┐
└──────────────┘      │
                      │ user_id
                      ▼
              ┌───────────────┐
              │ Visualization │
              │    Engine     │
              └───────┬───────┘
                      │
       ┌──────────────┼──────────────┐
       │              │              │
       ▼              ▼              ▼
┌──────────┐  ┌─────────────┐  ┌──────────┐
│ Budget   │  │   Invoice   │  │  Trend   │
│  Data    │  │    Data     │  │   Data   │
└──────────┘  └─────────────┘  └──────────┘
       │              │              │
       └──────────────┼──────────────┘
                      │
                      ▼
              ┌───────────────┐
              │  Dashboard    │
              │     Image     │
              └───────┬───────┘
                      │
                      ▼
              ┌───────────────┐
              │ User receives │
              │  visualization│
              └───────────────┘
```

## Dashboard Layout Structure

### Before Enhancement

```
┌─────────────────────────────────────────────────────────────────┐
│                    📊 Analysis Summary                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐               │
│  │Total Spent │  │  Invoices  │  │ Avg Amount │               │
│  │  Rp 2.5M   │  │     45     │  │  Rp 56K    │               │
│  └────────────┘  └────────────┘  └────────────┘               │
│                                                                  │
├──────────────────────────────────────────────┬──────────────────┤
│                                              │                  │
│  Weekly Spending Trend                       │  Top Vendors     │
│  ┌────────────────────────────────────┐     │  ┌────────────┐ │
│  │                                    │     │  │  Vendor 1  │ │
│  │    [Line Chart]                    │     │  │  Vendor 2  │ │
│  │                                    │     │  │  Vendor 3  │ │
│  └────────────────────────────────────┘     │  └────────────┘ │
│                                              │                  │
├───────────────────┬──────────────────────────┴──────────────────┤
│                   │                                             │
│ Category Dist.    │  Recent Transactions                        │
│ ┌───────────────┐ │  ┌─────────────────────────────────────┐  │
│ │               │ │  │ Date  │ Vendor      │ Amount        │  │
│ │  [Pie Chart]  │ │  ├───────┼─────────────┼───────────────┤  │
│ │               │ │  │ 01/10 │ Tokopedia   │ Rp 250K       │  │
│ └───────────────┘ │  │ 05/10 │ Shopee      │ Rp 180K       │  │
│                   │  └─────────────────────────────────────┘  │
└───────────────────┴──────────────────────────────────────────────┘
│  💡 Insights: Spending ↑ 15% | Weekly avg: Rp 2.5M ...        │
└─────────────────────────────────────────────────────────────────┘
```

### After Enhancement

```
┌─────────────────────────────────────────────────────────────────┐
│                    📊 Analysis Summary (Last 8 Weeks)           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌─────────────────┐  │
│  │  Total   │ │Invoices  │ │   Avg    │ │ Budget Status   │  │
│  │  Spent   │ │          │ │  Amount  │ │                 │  │
│  │ Rp 2.5M  │ │    45    │ │ Rp 56K   │ │   65% Used 🟢   │  │
│  └──────────┘ └──────────┘ └──────────┘ └─────────────────┘  │
│                                                                  │
├───────────────────────────────────────────────────┬─────────────┤
│                                                   │             │
│  Weekly Spending Trend                            │Top Vendors  │
│  ┌──────────────────────────────────────────┐    │┌──────────┐│
│  │ 📊 INCREASING                            │    ││Vendor 1  ││
│  │ +15%                                     │    ││Vendor 2  ││
│  │                                          │    ││Vendor 3  ││
│  │    [Line Chart with fill]                │    ││Vendor 4  ││
│  │                                          │    ││Vendor 5  ││
│  │    Rp 3M ─────                           │    │└──────────┘│
│  │    Rp 2M ─────                           │    │             │
│  │    Rp 1M ─────                           │    │  Rp 1.2M   │
│  │    Rp 0K ─────                           │    │  Rp 850K   │
│  │         W1  W2  W3  W4  W5  W6  W7  W8   │    │  Rp 600K   │
│  └──────────────────────────────────────────┘    │  Rp 450K   │
│                                                   │  Rp 300K   │
│                                                   │             │
├─────────────────────────────┬─────────────────────┴─────────────┤
│                             │                                   │
│ Category Distribution       │  Recent Transactions              │
│ ┌─────────────────────────┐ │  ┌─────────────────────────────┐│
│ │                         │ │  │Date│Vendor       │Amount    ││
│ │      [Pie Chart]        │ │  ├────┼─────────────┼──────────┤│
│ │                         │ │  │01/10│Tokopedia   │Rp 250K   ││
│ │  Shopping     40%       │ │  │05/10│Shopee      │Rp 180K   ││
│ │  Food         30%       │ │  │08/10│Grab Food   │Rp 85K    ││
│ │  Transport    20%       │ │  │12/10│Indomaret   │Rp 120K   ││
│ │  Others       10%       │ │  │15/10│Gojek       │Rp 45K    ││
│ └─────────────────────────┘ │  └─────────────────────────────┘│
│                             │                                   │
└─────────────────────────────┴───────────────────────────────────┘
│ 💡 Insights: Spending ↑ 15% | Weekly avg: Rp 2.5M |           │
│   Daily avg: Rp 350K | Budget: 65% used | Top: Tokopedia      │
└─────────────────────────────────────────────────────────────────┘
```

## Component Breakdown

### 1. KPI Cards (Top Row)

```
┌─────────────────────┐
│   Total Spent       │  COLOR: Red (#E74C3C)
│                     │
│     Rp 2.5M         │  FORMAT: format_rp(2500000)
└─────────────────────┘

┌─────────────────────┐
│   Invoices          │  COLOR: Blue (#3498DB)
│                     │
│       45            │  FORMAT: {count}
└─────────────────────┘

┌─────────────────────┐
│   Avg Amount        │  COLOR: Green (#2ECC71)
│                     │
│     Rp 56K          │  FORMAT: format_rp(56000)
└─────────────────────┘

┌─────────────────────┐
│ Budget Status  🆕   │  COLOR: Conditional
│                     │    < 80%: Green (#2ECC71)
│   65% Used    🟢    │    80-99%: Orange (#F39C12)
└─────────────────────┘    ≥100%: Red (#E74C3C)
                           Not Set: Gray (#95A5A6)
```

### 2. Weekly Trend Chart

**With Sufficient Data (≥3 weeks):**
```
┌────────────────────────────────────┐
│ 📊 INCREASING                      │  Trend Badge
│ +15%                               │  (Conditional)
│                                    │
│      ●─────●─────●─────●          │  Line Chart
│    ●                     ●         │  with markers
│  ●                         ●       │
│                              ●─    │  Fill under
│ [Shaded area]                      │
│                                    │
│  W1   W2   W3   W4   W5   W6   W7  W8│
│ (Date Range)                       │
└────────────────────────────────────┘
  Y-axis: format_rp values
```

**With Insufficient Data (<3 weeks):**
```
┌────────────────────────────────────┐
│                                    │
│  📊 More data needed for           │
│     trend analysis                 │
│                                    │
│  Upload more invoices to see       │
│  spending trends over time         │
│                                    │
└────────────────────────────────────┘
  [No axes shown]
```

### 3. Budget Status Logic

```python
if user_id is not None:
    budget_status = check_spending_limit(user_id)
    
    if budget_status['has_limit']:
        percentage = budget_status['percentage_used']
        
        if percentage >= 100:
            color = COLOR_BUDGET_OVER    # 🔴 Red
            message = "Over Budget!"
        elif percentage >= 80:
            color = COLOR_BUDGET_WARN    # 🟡 Orange
            message = "Approaching Limit"
        else:
            color = COLOR_BUDGET_OK      # 🟢 Green
            message = "On Track"
        
        value = f"{percentage:.0f}% Used"
    else:
        color = COLOR_BUDGET_NONE        # ⚪ Gray
        value = "Not Set"
else:
    # No user context
    color = COLOR_BUDGET_NONE
    value = "Not Set"
```

## Currency Formatting Pipeline

```
Input: 2,500,000
       │
       ▼
  format_rp(2500000)
       │
       ├─ Check: >= 1,000,000? → YES
       │    └─ Return: "Rp 2.5M"
       │
       ├─ Check: >= 1,000? → NO (skipped)
       │
       └─ Check: else → NO (skipped)

Output: "Rp 2.5M"

───────────────────────────────────

Input: 56,000
       │
       ▼
  format_rp(56000)
       │
       ├─ Check: >= 1,000,000? → NO
       │
       ├─ Check: >= 1,000? → YES
       │    └─ Return: "Rp 56K"
       │
       └─ Check: else → NO (skipped)

Output: "Rp 56K"

───────────────────────────────────

Input: 500
       │
       ▼
  format_rp(500)
       │
       ├─ Check: >= 1,000,000? → NO
       │
       ├─ Check: >= 1,000? → NO
       │
       └─ else
            └─ Return: "Rp 500"

Output: "Rp 500"
```

## State Diagram - Dashboard Generation

```
          START
            │
            ▼
   ┌────────────────┐
   │ Check user_id  │
   │ provided?      │
   └────┬───────────┘
        │
    ┌───┴───┐
    │       │
   YES     NO
    │       │
    ▼       ▼
┌─────┐  [Skip budget]
│Fetch│      │
│Budget│     │
└──┬──┘     │
   │        │
   └────┬───┘
        │
        ▼
   ┌────────────┐
   │Fetch Invoice│
   │   Data      │
   └──────┬─────┘
          │
          ▼
   ┌────────────┐
   │Create 4 KPI│
   │   Cards    │
   └──────┬─────┘
          │
    ┌─────┴─────┐
    │ Budget    │
    │ Card      │
    │ Color?    │
    └─────┬─────┘
          │
    ┌─────┼─────┬─────┐
    │     │     │     │
  <80%  80-99% ≥100% None
    │     │     │     │
   🟢    🟡    🔴    ⚪
    │     │     │     │
    └─────┴─────┴─────┘
          │
          ▼
   ┌─────────────┐
   │Check Trend  │
   │   Data      │
   └──────┬──────┘
          │
    ┌─────┴─────┐
    │ Weeks ≥ 3?│
    └─────┬─────┘
          │
      ┌───┴───┐
      │       │
     YES     NO
      │       │
      ▼       ▼
  [Show   [Show
   Trend]  Message]
      │       │
      └───┬───┘
          │
          ▼
   ┌─────────────┐
   │Format All   │
   │Currency     │
   │with format_rp│
   └──────┬──────┘
          │
          ▼
   ┌─────────────┐
   │Build Insights│
   │   Footer    │
   └──────┬──────┘
          │
          ▼
   ┌─────────────┐
   │  Generate   │
   │   PNG       │
   └──────┬──────┘
          │
          ▼
        RETURN
      BytesIO
```

## Color Palette

```
BACKGROUND:
  #EAF2F8 ░░░░░░░░░░ Light Blue-Gray

TITLES:
  #17202A ██████████ Very Dark Blue
  #2C3E50 ▓▓▓▓▓▓▓▓▓▓ Dark Blue-Gray

KPI CARDS:
  #E74C3C ■■■■■■■■■■ Red (Total Spent)
  #3498DB ■■■■■■■■■■ Blue (Invoices)
  #2ECC71 ■■■■■■■■■■ Green (Avg Amount)

BUDGET STATUS:
  #2ECC71 ●●●●●●●●●● Green (< 80%)
  #F39C12 ●●●●●●●●●● Orange (80-99%)
  #E74C3C ●●●●●●●●●● Red (≥ 100%)
  #95A5A6 ○○○○○○○○○○ Gray (Not Set)

TRENDS:
  #8E44AD ▬▬▬▬▬▬▬▬▬▬ Purple (Line)
  #E74C3C ▲▲▲▲▲▲▲▲▲▲ Red (Increasing)
  #2ECC71 ▼▼▼▼▼▼▼▼▼▼ Green (Decreasing)
  #F1C40F ━━━━━━━━━━ Yellow (Stable)
```

## File Structure

```
invoice_rag/
│
├── telegram_bot/
│   ├── __init__.py
│   ├── bot.py ✨ (Modified)
│   │   └── Functions:
│   │       ├── analysis_command() ✨ (passes user_id)
│   │       └── visualizations_command() ✨ (passes user_id)
│   │
│   ├── visualizations.py ✨ (Major Refactor)
│   │   └── Functions:
│   │       ├── format_rp() 🆕 (Helper)
│   │       ├── create_comprehensive_dashboard() ✨ (Enhanced)
│   │       ├── get_visualization() ✨ (Updated signature)
│   │       └── [Other visualization functions]
│   │
│   └── spending_limits.py
│       └── Functions:
│           └── check_spending_limit() (Used by dashboard)
│
├── test_enhanced_dashboard.py 🆕 (Test Suite)
│
├── dashboard_output/ 🆕 (Test Images)
│   ├── test_dashboard_no_user.png
│   ├── test_dashboard_user_12345.png
│   └── test_dashboard_limited_data.png
│
└── Documentation: 🆕
    ├── DASHBOARD_ENHANCEMENT_SUMMARY.md
    ├── DASHBOARD_QUICK_GUIDE.md
    ├── DASHBOARD_BEFORE_AFTER.md
    ├── DASHBOARD_VISUAL_ARCHITECTURE.md (This file)
    └── README_ENHANCEMENT.md
```

---

**Visual Architecture Complete** ✅  
**All diagrams showing enhanced dashboard structure** 📊
