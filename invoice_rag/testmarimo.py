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
    mo.md("# 📊 Invoice Analysis Dashboard")
    return


@app.cell
def _(datetime, os, pd, sqlite3, timedelta):
    def get_db_path():
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(current_dir, 'invoices.db')

    def load_data(weeks_back=8):
        db_path = get_db_path()
        if not os.path.exists(db_path):
            return pd.DataFrame()
    
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
                i.processed_at
            FROM invoices i
            WHERE i.invoice_date >= ?
            ORDER BY i.invoice_date DESC
        """
    
        df = pd.read_sql_query(query, conn, params=(start_date.strftime('%Y-%m-%d'),))
        conn.close()
    
        if not df.empty:
            df['invoice_date'] = pd.to_datetime(df['invoice_date'])
            df['processed_at'] = pd.to_datetime(df['processed_at'])
    
        return df

    df = load_data(weeks_back=8)
    return (df,)


@app.cell
def _(df):
    if not df.empty:
        total_spent = df['total_amount'].sum()
        avg_amount = df['total_amount'].mean()
        total_invoices = len(df)
        unique_shops = df['shop_name'].nunique()
    
        # In Marimo: use mo.hstack with mo.md for each metric
        print(f"Total Spent: Rp {total_spent:,.0f}")
        print(f"Invoices: {total_invoices}")
        print(f"Avg Amount: Rp {avg_amount:,.0f}")
        print(f"Unique Shops: {unique_shops}")

    return


@app.cell
def _(df, px):
    if not df.empty:
        daily_spending = df.groupby(df['invoice_date'].dt.date)['total_amount'].sum().reset_index()
        daily_spending.columns = ['Date', 'Total']
    
        fig1 = px.line(
            daily_spending,
            x='Date',
            y='Total',
            title='Daily Spending Trend',
            labels={'Total': 'Amount (Rp)', 'Date': 'Date'}
        )
    
        fig1.update_traces(
            line_color='#8E44AD',
            line_width=3,
            mode='lines+markers'
        )
    
        fig1.update_layout(
            hovermode='x unified',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
    
        # In Marimo: mo.ui.plotly(fig1)
        fig1.show()
    return


@app.cell
def _(df, go, make_subplots):
    if not df.empty:
        # Top vendors
        top_vendors = df.groupby('shop_name')['total_amount'].agg(['sum', 'count']).reset_index()
        top_vendors.columns = ['Shop', 'Total', 'Count']
        top_vendors = top_vendors.sort_values('Total', ascending=False).head(10)
    
        # Transaction types
        transaction_types = df.groupby('transaction_type')['total_amount'].sum().reset_index()
        transaction_types.columns = ['Type', 'Total']
    
        # Combined chart
        fig2 = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Top 10 Vendors', 'Transaction Types'),
            specs=[[{"type": "bar"}, {"type": "pie"}]]
        )
    
        fig2.add_trace(
            go.Bar(
                x=top_vendors['Shop'],
                y=top_vendors['Total'],
                marker_color='#3498DB',
                hovertemplate='<b>%{x}</b><br>Total: Rp %{y:,.0f}<extra></extra>'
            ),
            row=1, col=1
        )
    
        fig2.add_trace(
            go.Pie(
                labels=transaction_types['Type'],
                values=transaction_types['Total'],
                marker_colors=['#E74C3C', '#2ECC71', '#F39C12']
            ),
            row=1, col=2
        )
    
        fig2.update_layout(
            showlegend=True,
            height=400,
            hovermode='closest'
        )
    
        fig2.update_xaxes(tickangle=-45, row=1, col=1)
    
        # In Marimo: mo.ui.plotly(fig2)
        fig2.show()
    return


@app.cell
def _(df, px):
    if not df.empty:
        fig3 = px.histogram(
            df,
            x='total_amount',
            nbins=30,
            title='Distribution of Transaction Amounts',
            labels={'total_amount': 'Amount (Rp)'},
            color_discrete_sequence=['#9B59B6']
        )
    
        fig3.update_layout(
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
    
        # In Marimo: mo.ui.plotly(fig3)
        fig3.show()
    return


@app.cell
def _(df):
    if not df.empty:
        display_df = df[['invoice_date', 'shop_name', 'total_amount', 'transaction_type']].copy()
        display_df.columns = ['Date', 'Shop', 'Amount (Rp)', 'Type']
        display_df['Amount (Rp)'] = display_df['Amount (Rp)'].round(0).astype(int)
    
        # In Marimo: mo.ui.table(display_df, selection=None, label="All Transactions")
        print("\nTransaction Table:")
        print(display_df.head(10))
    return


@app.cell
def _(df):
    if not df.empty:
        weekly_data = df.copy()
        weekly_data['Week'] = weekly_data['invoice_date'].dt.to_period('W').astype(str)
    
        weekly_summary = weekly_data.groupby('Week').agg({
            'total_amount': ['sum', 'mean', 'count'],
            'shop_name': 'nunique'
        }).reset_index()
    
        weekly_summary.columns = ['Week', 'Total Spent', 'Avg Amount', 'Transactions', 'Unique Shops']
        weekly_summary['Total Spent'] = weekly_summary['Total Spent'].round(0).astype(int)
        weekly_summary['Avg Amount'] = weekly_summary['Avg Amount'].round(0).astype(int)
    
        # In Marimo: mo.ui.table(weekly_summary, selection=None, label="Weekly Summary")
        print("\nWeekly Summary:")
        print(weekly_summary)
    return


if __name__ == "__main__":
    app.run()
