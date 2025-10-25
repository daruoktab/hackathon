import marimo

__generated_with = "0.17.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _():
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import sqlite3
    from datetime import datetime, timedelta
    import os
    return datetime, go, make_subplots, os, pd, px, sqlite3, timedelta


@app.cell
def _(mo):
    mo.md(
        """
        # 📊 Invoice Analysis Dashboard
        
        Interactive dashboard for exploring your invoice data. Use the filters below to customize your view.
        """
    )
    return


@app.cell
def _(mo):
    weeks_slider = mo.ui.slider(
        start=1, 
        stop=52, 
        value=8, 
        label="Weeks to Analyze",
        step=1
    )
    
    refresh_button = mo.ui.run_button(label="🔄 Refresh Data")
    
    mo.hstack([weeks_slider, refresh_button], justify="start")
    return refresh_button, weeks_slider


@app.cell
def _(datetime, os, pd, sqlite3, timedelta, weeks_slider):
    def get_db_path():
        """Get the database path - looks in current working directory"""
        # When run from marimo_server, the DB is copied to the temp dir (cwd)
        return 'invoices.db'

    def load_invoice_data(weeks_back):
        """Load invoice data from database"""
        db_path = get_db_path()
        
        if not os.path.exists(db_path):
            print(f"Database not found at: {os.path.abspath(db_path)}")
            return pd.DataFrame()
        
        print(f"Loading data from: {os.path.abspath(db_path)}")
        conn = sqlite3.connect(db_path)
        
        end_date = datetime.now()
        start_date = end_date - timedelta(weeks=weeks_back)
        
        query = """
            SELECT 
                i.id,
                i.shop_name,
                i.invoice_date,
                i.total_amount,
                i.transaction_type,
                i.processed_at,
                COUNT(ii.id) as item_count
            FROM invoices i
            LEFT JOIN invoice_items ii ON i.id = ii.invoice_id
            WHERE i.invoice_date >= ?
            GROUP BY i.id
            ORDER BY i.invoice_date DESC
        """
        
        df = pd.read_sql_query(query, conn, params=(start_date.strftime('%Y-%m-%d'),))
        conn.close()
        
        print(f"Loaded {len(df)} invoices")
        
        if not df.empty:
            df['invoice_date'] = pd.to_datetime(df['invoice_date'])
            df['processed_at'] = pd.to_datetime(df['processed_at'])
        
        return df

    invoices_df = load_invoice_data(weeks_slider.value)
    return (invoices_df,)


@app.cell
def _(invoices_df, mo):
    if invoices_df.empty:
        mo.md(
            """
            ## ⚠️ No Data Available
            
            No invoices found in the selected time period. Try:
            - Increasing the number of weeks
            - Uploading more invoices
            """
        )
    return


@app.cell
def _(invoices_df, mo):
    mo.stop(invoices_df.empty)

    total_spent = invoices_df['total_amount'].sum()
    avg_amount = invoices_df['total_amount'].mean()
    total_invoices = len(invoices_df)
    unique_shops = invoices_df['shop_name'].nunique()

    mo.hstack([
        mo.md(f"""
        ### 💰 Total Spent
        **Rp {total_spent:,.0f}**
        """),
        mo.md(f"""
        ### 📄 Invoices
        **{total_invoices}**
        """),
        mo.md(f"""
        ### 📊 Avg Amount
        **Rp {avg_amount:,.0f}**
        """),
        mo.md(f"""
        ### 🏪 Shops
        **{unique_shops}**
        """)
    ], justify="space-around", gap=2)
    return


@app.cell
def _(invoices_df, mo):
    transaction_type_selector = mo.ui.dropdown(
        options=["All"] + sorted(invoices_df['transaction_type'].dropna().unique().tolist()),
        value="All",
        label="Filter by Transaction Type"
    )
    
    shop_selector = mo.ui.dropdown(
        options=["All"] + sorted(invoices_df['shop_name'].dropna().unique().tolist()[:20]),
        value="All",
        label="Filter by Shop"
    )
    
    mo.hstack([transaction_type_selector, shop_selector], justify="start")
    return shop_selector, transaction_type_selector


@app.cell
def _(invoices_df, shop_selector, transaction_type_selector):
    filtered_df = invoices_df.copy()
    
    if transaction_type_selector.value != "All":
        filtered_df = filtered_df[filtered_df['transaction_type'] == transaction_type_selector.value]
    
    if shop_selector.value != "All":
        filtered_df = filtered_df[filtered_df['shop_name'] == shop_selector.value]
    return (filtered_df,)


@app.cell
def _(filtered_df, mo, px):
    mo.md("## 📈 Spending Over Time")
    
    daily_spending = filtered_df.groupby(filtered_df['invoice_date'].dt.date)['total_amount'].sum().reset_index()
    daily_spending.columns = ['Date', 'Total']
    
    fig_timeline = px.line(
        daily_spending, 
        x='Date', 
        y='Total',
        title='Daily Spending Trend',
        labels={'Total': 'Amount (Rp)', 'Date': 'Date'}
    )
    
    fig_timeline.update_traces(
        line_color='#8E44AD',
        line_width=3,
        mode='lines+markers'
    )
    
    fig_timeline.update_layout(
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    mo.ui.plotly(fig_timeline)
    return


@app.cell
def _(filtered_df, go, make_subplots, mo):
    mo.md("## 🏪 Top Vendors & Transaction Types")
    
    top_vendors = filtered_df.groupby('shop_name')['total_amount'].agg(['sum', 'count']).reset_index()
    top_vendors.columns = ['Shop', 'Total', 'Count']
    top_vendors = top_vendors.sort_values('Total', ascending=False).head(10)
    
    transaction_types = filtered_df.groupby('transaction_type')['total_amount'].sum().reset_index()
    transaction_types.columns = ['Type', 'Total']
    
    fig_combined = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Top 10 Vendors by Spending', 'Transaction Type Distribution'),
        specs=[[{"type": "bar"}, {"type": "pie"}]]
    )
    
    fig_combined.add_trace(
        go.Bar(
            x=top_vendors['Shop'],
            y=top_vendors['Total'],
            marker_color='#3498DB',
            hovertemplate='<b>%{x}</b><br>Total: Rp %{y:,.0f}<extra></extra>'
        ),
        row=1, col=1
    )
    
    fig_combined.add_trace(
        go.Pie(
            labels=transaction_types['Type'],
            values=transaction_types['Total'],
            marker_colors=['#E74C3C', '#2ECC71', '#F39C12']
        ),
        row=1, col=2
    )
    
    fig_combined.update_layout(
        showlegend=True,
        height=400,
        hovermode='closest'
    )
    
    fig_combined.update_xaxes(tickangle=-45, row=1, col=1)
    
    mo.ui.plotly(fig_combined)
    return


@app.cell
def _(filtered_df, mo, px):
    mo.md("## 💳 Spending Distribution")
    
    fig_histogram = px.histogram(
        filtered_df,
        x='total_amount',
        nbins=30,
        title='Distribution of Transaction Amounts',
        labels={'total_amount': 'Amount (Rp)'},
        color_discrete_sequence=['#9B59B6']
    )
    
    fig_histogram.update_layout(
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    mo.ui.plotly(fig_histogram)
    return


@app.cell
def _(filtered_df, mo):
    mo.md("## 📋 Interactive Data Explorer")
    
    display_df = filtered_df[['invoice_date', 'shop_name', 'total_amount', 'transaction_type']].copy()
    display_df.columns = ['Date', 'Shop', 'Amount (Rp)', 'Type']
    display_df['Amount (Rp)'] = display_df['Amount (Rp)'].round(0).astype(int)
    
    mo.ui.table(
        display_df,
        selection=None,
        label="All Transactions"
    )
    return


@app.cell
def _(filtered_df, mo):
    mo.md("## 📊 Weekly Analysis")
    
    weekly_data = filtered_df.copy()
    weekly_data['Week'] = weekly_data['invoice_date'].dt.to_period('W').astype(str)
    
    weekly_summary = weekly_data.groupby('Week').agg({
        'total_amount': ['sum', 'mean', 'count'],
        'shop_name': 'nunique'
    }).reset_index()
    
    weekly_summary.columns = ['Week', 'Total Spent', 'Avg Amount', 'Transactions', 'Unique Shops']
    weekly_summary['Total Spent'] = weekly_summary['Total Spent'].round(0).astype(int)
    weekly_summary['Avg Amount'] = weekly_summary['Avg Amount'].round(0).astype(int)
    
    mo.ui.table(
        weekly_summary,
        selection=None,
        label="Weekly Summary"
    )
    return


@app.cell
def _(mo):
    mo.md(
        """
        ---
        
        ### 💡 Tips
        - Use the **Weeks slider** at the top to adjust the time period
        - **Filter** by transaction type or shop to focus on specific data
        - Hover over charts for detailed information
        - Click and drag on charts to zoom
        - Double-click to reset zoom
        
        *Dashboard updates automatically when you change filters*
        """
    )
    return


if __name__ == "__main__":
    app.run()
