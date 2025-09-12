import marimo

__generated_with = "0.9.14"
app = marimo.App(width="medium")


@app.cell
def __():
    import marimo as mo
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go
    import os
    import sys
    from datetime import datetime, timedelta
    from pathlib import Path

    # Add src directory to Python path
    sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

    return datetime, mo, os, pd, px, go, sys, timedelta, Path


@app.cell
def __(mo):
    mo.md("""
    # 🧾 Invoice Analysis Dashboard
    Interactive system for processing and analyzing invoice data using AI
    """)
    return


@app.cell
def __(mo):
    # Import project modules
    try:
        from src.processor import process_invoice_with_llm, RobustInvoice
        from src.database import get_db_session, insert_invoice_data, Invoice, InvoiceItem
        from src.analysis import calculate_weekly_averages, analyze_spending_trends
        mo.md("✅ Successfully imported project modules")
    except ImportError as e:
        mo.md(f"❌ Failed to import modules: {e}")

    return Invoice, InvoiceItem, RobustInvoice, analyze_spending_trends, calculate_weekly_averages, get_db_session, insert_invoice_data, process_invoice_with_llm


@app.cell
def __(get_db_session, mo):
    # Database connection
    try:
        db_session = get_db_session('invoices.db')
        mo.md("✅ Database connection established")
    except Exception as e:
        mo.md(f"❌ Database connection failed: {e}")
        db_session = None
    return db_session,


@app.cell
def __(mo):
    # Main navigation tabs
    tab_selection = mo.ui.tabs({
        "🔍 Process Invoice": "process",
        "📊 Dashboard": "dashboard",
        "📋 Invoice List": "list",
        "📈 Analytics": "analytics"
    })
    tab_selection
    return tab_selection,


@app.cell
def __(mo, tab_selection):
    # Invoice Processing Section
    if tab_selection.value == "process":
        mo.md("## 📤 Upload and Process Invoice")

        # File uploader
        uploaded_file = mo.ui.file(
            label="Choose an invoice image (JPG, PNG, JPEG)",
            multiple=False,
            full_width=True
        )

        process_button = mo.ui.run_button(label="🚀 Process Invoice", kind="primary")

        mo.vstack([uploaded_file, process_button])
    else:
        uploaded_file = None
        process_button = None
    return process_button, uploaded_file


@app.cell
def __(datetime, db_session, insert_invoice_data, mo, os, pd, process_button, process_invoice_with_llm, uploaded_file):
    # Process invoice when button is clicked
    if process_button and process_button.value and uploaded_file and uploaded_file.value:
        try:
            # Save uploaded file temporarily
            file_data = uploaded_file.value[0]
            temp_path = f"temp_invoice_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"

            with open(temp_path, "wb") as f:
                f.write(file_data.contents)

            mo.md("🔄 Processing invoice with AI...")

            # Process with LLM
            invoice_data = process_invoice_with_llm(temp_path)

            if invoice_data and db_session:
                # Insert into database
                invoice_id = insert_invoice_data(db_session, invoice_data, temp_path)

                if invoice_id:
                    mo.md(f"✅ Invoice processed successfully! ID: {invoice_id}")

                    # Display extracted data
                    invoice_df = pd.DataFrame([{
                        'Shop': invoice_data.shop_name,
                        'Date': invoice_data.invoice_date,
                        'Time': invoice_data.invoice_time,
                        'Total Amount': f"Rp {invoice_data.total_amount:,.2f}",
                        'Payment Method': invoice_data.payment_method or 'N/A'
                    }])

                    mo.ui.table(invoice_df, label="📋 Extracted Invoice Data")
                else:
                    mo.md("❌ Failed to save invoice to database")
            else:
                mo.md("❌ Failed to process invoice")

            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)

        except Exception as e:
            mo.md(f"❌ Error processing invoice: {str(e)}")
    elif process_button and process_button.value:
        mo.md("⚠️ Please upload an invoice image first")
    return


@app.cell
def __(Invoice, datetime, db_session, mo, pd, tab_selection, timedelta):
    # Dashboard Section
    if tab_selection.value == "dashboard" and db_session:
        mo.md("## 📊 Spending Dashboard")

        # Get dashboard data
        try:
            all_invoices = db_session.query(Invoice).all()

            if all_invoices:
                # Create dashboard metrics
                total_invoices = len(all_invoices)
                total_spent = sum(inv.total_amount for inv in all_invoices)
                avg_transaction = total_spent / total_invoices if total_invoices > 0 else 0

                # Recent activity (last 7 days)
                week_ago = datetime.now() - timedelta(days=7)
                recent_invoices = [inv for inv in all_invoices if inv.processed_at >= week_ago]
                recent_spending = sum(inv.total_amount for inv in recent_invoices)

                # Create metrics cards
                metrics_df = pd.DataFrame([
                    {'Metric': '🧾 Total Invoices', 'Value': f"{total_invoices:,}"},
                    {'Metric': '💰 Total Spent', 'Value': f"Rp {total_spent:,.2f}"},
                    {'Metric': '📊 Avg Transaction', 'Value': f"Rp {avg_transaction:,.2f}"},
                    {'Metric': '📅 Last 7 Days', 'Value': f"Rp {recent_spending:,.2f}"}
                ])

                mo.ui.table(metrics_df, label="📈 Key Metrics")

            else:
                mo.md("📭 No invoices found. Upload some invoices to see dashboard data!")

        except Exception as e:
            mo.md(f"❌ Error loading dashboard: {str(e)}")
    return


@app.cell
def __(Invoice, db_session, mo, pd, tab_selection):
    # Invoice List Section
    if tab_selection.value == "list" and db_session:
        mo.md("## 📋 Invoice List")

        try:
            # Get all invoices with items
            invoices = db_session.query(Invoice).order_by(Invoice.processed_at.desc()).all()

            if invoices:
                # Create invoice list dataframe
                invoice_list = []
                for inv in invoices:
                    invoice_list.append({
                        'ID': inv.id,
                        'Shop': inv.shop_name,
                        'Date': inv.invoice_date or 'N/A',
                        'Time': inv.invoice_time or 'N/A',
                        'Total': f"Rp {inv.total_amount:,.2f}",
                        'Items': len(inv.items),
                        'Payment': inv.payment_method or 'N/A',
                        'Processed': inv.processed_at.strftime('%Y-%m-%d %H:%M') if inv.processed_at else 'N/A'
                    })

                list_invoice_df = pd.DataFrame(invoice_list)
                invoice_table = mo.ui.table(
                    list_invoice_df,
                    label="💳 All Invoices",
                    sortable=True,
                    filterable=True
                )
                invoice_table
            else:
                mo.md("📭 No invoices found in database")

        except Exception as e:
            mo.md(f"❌ Error loading invoice list: {str(e)}")
    return


@app.cell
def __(db_session, mo, tab_selection):
    # Analytics Section
    if tab_selection.value == "analytics" and db_session:
        mo.md("## 📈 Spending Analytics")

        # Time period selector
        weeks_selector = mo.ui.slider(
            start=1,
            stop=12,
            value=4,
            label="📅 Analysis Period (weeks)",
            step=1
        )

        weeks_selector
    else:
        weeks_selector = None
    return weeks_selector,


@app.cell
def __(Invoice, analyze_spending_trends, calculate_weekly_averages, datetime, db_session, mo, pd, px, tab_selection, timedelta, weeks_selector):
    # Analytics visualizations based on selected time period
    if tab_selection.value == "analytics" and weeks_selector and db_session:
        try:
            # Get analytics data
            weekly_data = calculate_weekly_averages(db_session, weeks_selector.value)
            trends = analyze_spending_trends(db_session, weeks_selector.value)

            if weekly_data['transaction_count'] > 0:
                # Weekly spending trend chart
                weekly_breakdown = weekly_data['weekly_breakdown']
                if weekly_breakdown:
                    weeks_df = pd.DataFrame([
                        {'Week': week, 'Amount': amount}
                        for week, amount in weekly_breakdown.items()
                    ])

                    fig_weekly = px.line(
                        weeks_df,
                        x='Week',
                        y='Amount',
                        title=f'📊 Weekly Spending Trend ({weeks_selector.value} weeks)',
                        labels={'Amount': 'Amount (Rp)', 'Week': 'Week'}
                    )
                    fig_weekly.update_traces(mode='markers+lines')
                    fig_weekly.update_layout(
                        xaxis_title="Week",
                        yaxis_title="Amount (Rp)",
                        height=400
                    )

                    mo.ui.plotly(fig_weekly)

                # Summary statistics
                summary_df = pd.DataFrame([
                    {'Metric': '📅 Analysis Period', 'Value': f"{weeks_selector.value} weeks"},
                    {'Metric': '💰 Total Spent', 'Value': f"Rp {weekly_data['total_spent']:,.2f}"},
                    {'Metric': '📊 Weekly Average', 'Value': f"Rp {weekly_data['weekly_average']:,.2f}"},
                    {'Metric': '📈 Daily Average', 'Value': f"Rp {weekly_data['daily_average']:,.2f}"},
                    {'Metric': '🧾 Total Transactions', 'Value': f"{weekly_data['transaction_count']:,}"},
                    {'Metric': '📈 Trend', 'Value': trends.get('trend', 'N/A').replace('_', ' ').title()}
                ])

                mo.ui.table(summary_df, label="📈 Analytics Summary")

                # Shop spending breakdown
                analytics_invoices = db_session.query(Invoice).all()
                analytics_recent = [
                    analytics_inv for analytics_inv in analytics_invoices
                    if analytics_inv.processed_at >= datetime.now() - timedelta(weeks=weeks_selector.value)
                ]

                if analytics_recent:
                    # Group by shop
                    shop_spending = {}
                    for analytics_inv in analytics_recent:
                        shop = analytics_inv.shop_name
                        shop_spending[shop] = shop_spending.get(shop, 0) + analytics_inv.total_amount

                    if shop_spending:
                        shops_df = pd.DataFrame([
                            {'Shop': shop, 'Amount': amount}
                            for shop, amount in sorted(shop_spending.items(), key=lambda x: x[1], reverse=True)
                        ])

                        # Top shops pie chart
                        fig_shops = px.pie(
                            shops_df.head(10),  # Top 10 shops
                            values='Amount',
                            names='Shop',
                            title=f'🏪 Top Shops by Spending ({weeks_selector.value} weeks)'
                        )
                        fig_shops.update_layout(height=500)

                        mo.ui.plotly(fig_shops)
            else:
                mo.md(f"📭 No transaction data found for the last {weeks_selector.value} weeks")

        except Exception as e:
            mo.md(f"❌ Error generating analytics: {str(e)}")
    return


@app.cell
def __(db_session, mo):
    # Handle cases where database is not connected
    if not db_session:
        mo.md("❌ Database not connected. Please check your database configuration.")
    else:
        mo.md("👆 Select a tab above to get started!")
    return


if __name__ == "__main__":
    app.run()
