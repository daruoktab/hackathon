# 🔄 Invoice Processing System - Complete Workflow Overview

This document provides a comprehensive visual overview of how the Invoice Processing System works from start to finish.

---

## 🎯 System Overview

```mermaid
graph TB
    subgraph "👤 Users"
        U1[Daily User with Phone]
        U2[Power User with Computer]
    end
    
    subgraph "📥 Input Methods"
        T[Telegram Bot<br/>Interactive]
        C[CLI Script<br/>Batch Processing]
    end
    
    subgraph "🧠 Processing Core"
        P[Invoice Processor]
        AI[Groq AI/LLM]
        V[Data Validator]
    end
    
    subgraph "💾 Data Layer"
        DB[(SQLite Database)]
    end
    
    subgraph "📊 Analysis Layer"
        A[Financial Analyzer]
        VIS[Visualization Engine]
        CHAT[AI Chat Assistant]
    end
    
    subgraph "📤 Output"
        R1[Text Reports]
        R2[Visual Dashboards]
        R3[AI Insights]
    end
    
    U1 --> T
    U2 --> C
    
    T --> P
    C --> P
    
    P --> AI
    AI --> V
    V --> DB
    
    DB --> A
    A --> VIS
    A --> CHAT
    
    VIS --> R2
    A --> R1
    CHAT --> R3
    
    R1 --> T
    R2 --> T
    R3 --> T
    
    style U1 fill:#e3f2fd
    style U2 fill:#e3f2fd
    style AI fill:#fff9c4
    style DB fill:#c8e6c9
    style R2 fill:#c8e6c9
```

---

## 📱 Telegram Bot User Journey

### Complete Daily Workflow

```mermaid
graph TD
    START[User Starts Day] --> SHOP[Makes a Purchase]
    SHOP --> RECEIPT[Gets Receipt]
    RECEIPT --> PHOTO[Takes Photo]
    PHOTO --> SEND[Sends to Bot]
    
    SEND --> PROCESS[Bot: Processing...]
    PROCESS --> EXTRACT[AI Extracts Data]
    EXTRACT --> VALIDATE[Validates Info]
    VALIDATE --> SAVE[Saves to Database]
    
    SAVE --> CHECK{Check Budget}
    CHECK -->|Under Budget| OK[✅ Confirmation]
    CHECK -->|Near Limit| WARN[⚡ Warning]
    CHECK -->|Over Limit| ALERT[🚫 Alert]
    
    OK --> DONE[Invoice Saved]
    WARN --> DONE
    ALERT --> DONE
    
    DONE --> NEXT{User Action}
    
    NEXT -->|Continue Shopping| SHOP
    NEXT -->|Check Analysis| ANALYSIS[/analysis]
    NEXT -->|Ask Question| CHAT[/chat]
    NEXT -->|Check Budget| BUDGET[/check_limit]
    NEXT -->|Done| END[End]
    
    ANALYSIS --> DASH[📊 Dashboard Sent]
    CHAT --> AI_RESP[🤖 AI Response]
    BUDGET --> BUDGET_STATUS[💰 Budget Status]
    
    DASH --> END
    AI_RESP --> END
    BUDGET_STATUS --> END
    
    style START fill:#e3f2fd
    style PHOTO fill:#fff9c4
    style EXTRACT fill:#fff9c4
    style OK fill:#c8e6c9
    style WARN fill:#ffeb3b
    style ALERT fill:#ffccbc
    style DASH fill:#c8e6c9
```

---

## 💻 CLI Batch Processing Workflow

### Bulk Invoice Import

```mermaid
graph TD
    START[User Has Many Receipts] --> COLLECT[Collect All Photos]
    COLLECT --> FOLDER[Place in invoices/ Folder]
    FOLDER --> TERMINAL[Open Terminal]
    TERMINAL --> RUN[Run: python run.py]
    
    RUN --> SCAN[Scan Folder]
    SCAN --> LOOP[Process Each Image]
    
    LOOP --> IMG1[Image 1]
    LOOP --> IMG2[Image 2]
    LOOP --> IMG3[Image N...]
    
    IMG1 --> AI1[AI Extract]
    IMG2 --> AI2[AI Extract]
    IMG3 --> AI3[AI Extract]
    
    AI1 --> SAVE1[Save to DB]
    AI2 --> SAVE2[Save to DB]
    AI3 --> SAVE3[Save to DB]
    
    SAVE1 --> COMPLETE{All Done?}
    SAVE2 --> COMPLETE
    SAVE3 --> COMPLETE
    
    COMPLETE -->|Yes| SUMMARY[Show Summary]
    COMPLETE -->|No| LOOP
    
    SUMMARY --> REPORT[Report:<br/>✅ 25/25 Processed<br/>💰 Total: Rp 5.2M]
    REPORT --> VIEW[View in Telegram Bot]
    VIEW --> END[Complete]
    
    style START fill:#e3f2fd
    style RUN fill:#fff9c4
    style REPORT fill:#c8e6c9
    style VIEW fill:#c8e6c9
```

---

## 🤖 AI Processing Pipeline

### How Invoice Data is Extracted

```mermaid
graph LR
    subgraph "Step 1 - Input"
        IMG[📸 Invoice Photo]
    end
    
    subgraph "Step 2 - Encoding"
        B64[Base64 Encode]
    end
    
    subgraph "Step 3 - AI Extraction"
        LLM[Groq LLM]
        PROMPT[Extraction Prompt]
    end
    
    subgraph "Step 4 - AI Response"
        JSON[JSON Data:<br/>- Shop Name<br/>- Date<br/>- Total<br/>- Items]
    end
    
    subgraph "Step 5 - Validation"
        V1[Date Format]
        V2[Currency Parse]
        V3[Type Detection]
    end
    
    subgraph "Step 6 - Storage"
        DB[(Database)]
    end
    
    IMG --> B64
    B64 --> PROMPT
    PROMPT --> LLM
    LLM --> JSON
    
    JSON --> V1
    JSON --> V2
    JSON --> V3
    
    V1 --> DB
    V2 --> DB
    V3 --> DB
    
    style IMG fill:#e3f2fd
    style LLM fill:#fff9c4
    style JSON fill:#fff9c4
    style DB fill:#c8e6c9
```

**What AI Extracts:**
- 🏢 **Shop Name**: "Alfamart", "Indomaret", etc.
- 📅 **Date**: Standardized to YYYY-MM-DD
- 💰 **Total Amount**: Parsed from various formats
- 📝 **Line Items**: Individual products/services
- 🏷️ **Transaction Type**: Bank/Retail/E-commerce (auto-detected)

---

## 📊 Analysis & Visualization Flow

### From Data to Dashboard

```mermaid
graph TD
    subgraph "📊 User Request"
        CMD[User: /analysis]
    end
    
    subgraph "🔍 Data Query"
        Q1[Get All Invoices]
        Q2[Calculate Totals]
        Q3[Find Top Vendors]
        Q4[Analyze Trends]
        Q5[Check Budget]
    end
    
    subgraph "📈 Visualization"
        KPI[Create 4 KPI Cards]
        TREND[Spending Trend Chart]
        VENDOR[Top Vendors Bar Chart]
        TYPE[Transaction Type Pie]
        DAILY[Daily Spending Bars]
    end
    
    subgraph "🎨 Assembly"
        LAYOUT[Combine into Dashboard]
        INSIGHTS[Add AI Insights]
    end
    
    subgraph "📤 Delivery"
        SEND[Send to User]
    end
    
    CMD --> Q1
    Q1 --> Q2
    Q2 --> Q3
    Q3 --> Q4
    Q4 --> Q5
    
    Q2 --> KPI
    Q4 --> TREND
    Q3 --> VENDOR
    Q3 --> TYPE
    Q2 --> DAILY
    Q5 --> KPI
    
    KPI --> LAYOUT
    TREND --> LAYOUT
    VENDOR --> LAYOUT
    TYPE --> LAYOUT
    DAILY --> LAYOUT
    
    LAYOUT --> INSIGHTS
    INSIGHTS --> SEND
    
    style CMD fill:#e3f2fd
    style LAYOUT fill:#fff9c4
    style SEND fill:#c8e6c9
```

---

## 🤖 AI Chat Interaction Flow

### Conversational Finance Assistant

```mermaid
graph TD
    subgraph "💬 User Query"
        U[User: /chat How much<br/>did I spend this week?]
    end
    
    subgraph "🧠 Processing"
        P1[Parse Question]
        P2[Query Database]
        P3[Get Relevant Data]
    end
    
    subgraph "🤖 AI Generation"
        CONTEXT[Build Context:<br/>Question + Data]
        LLM[Groq LLM]
        RESPONSE[Generate Human-like<br/>Response]
    end
    
    subgraph "📤 Response"
        SEND[Bot: Based on your data,<br/>you spent Rp 1.2M this<br/>week across 12 transactions.]
    end
    
    U --> P1
    P1 --> P2
    P2 --> P3
    
    P3 --> CONTEXT
    CONTEXT --> LLM
    LLM --> RESPONSE
    
    RESPONSE --> SEND
    
    style U fill:#e3f2fd
    style LLM fill:#fff9c4
    style SEND fill:#c8e6c9
```

**Chat Capabilities:**
- 📊 Spending queries: "How much did I spend?"
- 🏪 Vendor analysis: "Which shop do I visit most?"
- 📅 Time comparisons: "Compare this week to last week"
- 💡 Insights: "Where can I cut costs?"
- 🎯 Budget help: "Am I on track with my budget?"

---

## 💰 Budget Alert System

### Automatic Spending Monitoring

```mermaid
graph TD
    subgraph "💳 New Purchase"
        INVOICE[User Uploads Invoice]
    end
    
    subgraph "💾 Save & Calculate"
        SAVE[Save to Database]
        CALC[Calculate Total Spending]
    end
    
    subgraph "🎯 Check Budget"
        BUDGET{Has Budget Set?}
        COMPARE{Compare Spending}
    end
    
    subgraph "📊 Status Levels"
        SAFE[< 75%<br/>✅ Safe]
        CLOSE[75-89%<br/>⚡ Getting Close]
        NEAR[90-99%<br/>⚠️ Near Limit]
        OVER[≥ 100%<br/>🚫 Over Budget]
    end
    
    subgraph "📤 Actions"
        NO_ALERT[No Alert]
        WARN_MSG[Warning Message]
        ALERT_MSG[Alert Message]
    end
    
    INVOICE --> SAVE
    SAVE --> CALC
    CALC --> BUDGET
    
    BUDGET -->|No| NO_ALERT
    BUDGET -->|Yes| COMPARE
    
    COMPARE -->|< 75%| SAFE
    COMPARE -->|75-89%| CLOSE
    COMPARE -->|90-99%| NEAR
    COMPARE -->|≥ 100%| OVER
    
    SAFE --> NO_ALERT
    CLOSE --> NO_ALERT
    NEAR --> WARN_MSG
    OVER --> ALERT_MSG
    
    style INVOICE fill:#e3f2fd
    style SAFE fill:#c8e6c9
    style CLOSE fill:#fff9c4
    style NEAR fill:#ffccbc
    style OVER fill:#ef9a9a
    style WARN_MSG fill:#ffeb3b
    style ALERT_MSG fill:#f44336
```

---

## 🗄️ Database Schema

### How Data is Stored

```mermaid
erDiagram
    INVOICES ||--o{ INVOICE_ITEMS : contains
    INVOICES ||--o| SPENDING_LIMITS : has
    
    INVOICES {
        int id PK
        text shop_name
        text invoice_date
        real total_amount
        text transaction_type
        timestamp processed_at
        text image_path
    }
    
    INVOICE_ITEMS {
        int id PK
        int invoice_id FK
        text item_name
        int quantity
        real unit_price
        real total_price
    }
    
    SPENDING_LIMITS {
        int id PK
        int user_id
        real monthly_limit
        timestamp created_at
        timestamp updated_at
    }
```

---

## 🔄 Complete System Data Flow

### End-to-End Process

```mermaid
graph TB
    subgraph "👤 User Actions"
        A1[Take Photo]
        A2[Send to Bot]
        A3[Request Analysis]
        A4[Ask Questions]
    end
    
    subgraph "📥 Input Layer"
        I1[Telegram Bot API]
        I2[CLI Script]
    end
    
    subgraph "🧠 Processing Layer"
        P1[Invoice Processor]
        P2[AI Extractor]
        P3[Validator]
    end
    
    subgraph "💾 Data Layer"
        D1[(SQLite DB)]
    end
    
    subgraph "📊 Analysis Layer"
        AN1[Financial Analyzer]
        AN2[Trend Analyzer]
        AN3[Budget Checker]
    end
    
    subgraph "🎨 Presentation Layer"
        PR1[Visualization Engine]
        PR2[AI Chat Engine]
        PR3[Report Generator]
    end
    
    subgraph "📤 Output Layer"
        O1[Text Messages]
        O2[Dashboard Images]
        O3[AI Responses]
        O4[Alerts]
    end
    
    A1 --> A2
    A2 --> I1
    I1 --> P1
    I2 --> P1
    
    P1 --> P2
    P2 --> P3
    P3 --> D1
    
    A3 --> I1
    A4 --> I1
    
    D1 --> AN1
    D1 --> AN2
    D1 --> AN3
    
    AN1 --> PR1
    AN1 --> PR3
    AN2 --> PR1
    AN3 --> O4
    
    A4 --> PR2
    D1 --> PR2
    
    PR1 --> O2
    PR2 --> O3
    PR3 --> O1
    
    O1 --> I1
    O2 --> I1
    O3 --> I1
    O4 --> I1
    
    I1 --> A1
    
    style A1 fill:#e3f2fd
    style P2 fill:#fff9c4
    style D1 fill:#c8e6c9
    style O2 fill:#c8e6c9
```

---

## 📈 Typical Usage Patterns

### Daily User

```
Morning:
┌─────────────────────┐
│ 1. Buy breakfast    │
│ 2. Take photo       │
│ 3. Send to bot      │ → ✅ Saved
│ 4. Get confirmation │
└─────────────────────┘

Evening:
┌─────────────────────┐
│ 1. Grocery shopping │
│ 2. Send receipt     │ → ⚡ 85% budget warning
│ 3. Check /analysis  │
└─────────────────────┘

Weekend:
┌─────────────────────┐
│ 1. Review dashboard │
│ 2. Ask AI insights  │
│ 3. Adjust budget    │
└─────────────────────┘
```

### Power User

```
Monthly Setup:
┌────────────────────────┐
│ 1. Collect old receipts│
│ 2. Batch process CLI   │ → 50 invoices processed
│ 3. Set monthly budget  │
│ 4. Review dashboard    │
└────────────────────────┘

Ongoing:
┌────────────────────────┐
│ • Upload as you shop   │
│ • Weekly analysis      │
│ • AI trend questions   │
│ • Budget adjustments   │
└────────────────────────┘
```

---

## 🎯 Success Metrics

**What Users Achieve:**
- 📊 **100% Transaction Tracking**: Never miss an expense
- ⏱️ **30 Second Processing**: From photo to saved data
- 💰 **Budget Compliance**: Stay within limits with alerts
- 📈 **Pattern Recognition**: Understand spending habits
- 💡 **Actionable Insights**: AI-powered recommendations

---

## 🔗 Related Documentation

- **[README.md](../README.md)** - Main project documentation
- **[USER_WORKFLOWS.md](USER_WORKFLOWS.md)** - Detailed user guides
- **[DASHBOARD_QUICK_GUIDE.md](DASHBOARD_QUICK_GUIDE.md)** - Dashboard features
- **[.env.example](.env.example)** - Configuration template

---

**Ready to track your spending?** Start with `python run_bot.py` 🚀
