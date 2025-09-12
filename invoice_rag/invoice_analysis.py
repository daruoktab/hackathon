import marimo

__generated_with = "0.9.14"
app = marimo.App(width="medium")


@app.cell
def imports_and_setup():
    import marimo as mo
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go
    import os
    import sys
    import sqlite3
    import json
    from datetime import datetime, timedelta
    from pathlib import Path
    from PIL import Image

    # Add src directory to Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(current_dir, 'src')
    sys.path.insert(0, src_dir)

    return datetime, mo, os, pd, px, go, sys, timedelta, Path, sqlite3, json, Image, current_dir, src_dir


@app.cell
def header_title(mo):
    mo.md("""
    # 📄 Invoice Processing System
    Interactive system for processing and analyzing invoice data using AI
    """)


@app.cell
def check_api_key(mo, os):
    # Check API key
    if not os.getenv("GROQ_API_KEY"):
        return mo.md("⚠️ GROQ_API_KEY not found in environment variables. Please set it up.\nCreate a .env file in the project root with: GROQ_API_KEY=your_key_here")
    else:
        return mo.md("✅ GROQ_API_KEY found")


@app.cell
def import_project_modules(mo):
    # Import project modules
    try:
        from processor import process_invoice_with_llm, save_to_database_robust, create_tables
        from database import get_db_session, insert_invoice_data, Invoice, InvoiceItem
        from analysis import calculate_weekly_averages, analyze_spending_trends, find_biggest_spending_categories, analyze_item_spending, generate_comprehensive_analysis
        mo.md("✅ Successfully imported project modules")
    except ImportError as e:
        mo.md(f"❌ Failed to import modules: {e}")
        # Define dummy functions to prevent errors
        def process_invoice_with_llm(*args, **kwargs):
            return None
        def save_to_database_robust(*args, **kwargs):
            return None
        def create_tables(*args, **kwargs):
            pass

    return Invoice, InvoiceItem, analyze_item_spending, analyze_spending_trends, calculate_weekly_averages, create_tables, find_biggest_spending_categories, generate_comprehensive_analysis, get_db_session, insert_invoice_data, process_invoice_with_llm, save_to_database_robust


@app.cell
def setup_database_connection(get_db_session, mo, create_tables):
    # Database connection and initialization
    try:
        create_tables()
        db_session = get_db_session('invoices.db')
        mo.md("✅ Database connection established and tables created")
    except Exception as e:
        mo.md(f"❌ Database connection failed: {e}")
        db_session = None
    return db_session,


@app.cell
def create_navigation_tabs(mo):
    # Main navigation tabs
    tab_selection = mo.ui.tabs({
        "📤 Upload & Process": "upload",
        "📊 Dashboard": "dashboard", 
        "📋 View Invoices": "invoices",
        "🔍 Search & Filter": "search",
        "📈 Data Analytics": "analytics",
        "⚙️ Data Management": "management"
    })
    tab_selection


@app.cell
def create_upload_section(mo, tab_selection):
    # Upload and Process Invoice Section
    if tab_selection.value == "upload":
        upload_header = mo.md("## 📤 Upload & Process Invoice")
        
        uploaded_file = mo.ui.file(
            label="Choose an invoice image (JPG, PNG, JPEG)...",
            multiple=False,
            full_width=True
        )
        
        process_button = mo.ui.run_button(label="🔄 Process Invoice", kind="primary")
        
        upload_section = mo.vstack([upload_header, uploaded_file, process_button])
        return upload_section, uploaded_file, process_button
    else:
        return None, None, None


@app.cell
def show_uploaded_image(uploaded_file, Image, mo):
    # Display uploaded image if available
    if uploaded_file and uploaded_file.value:
        try:
            file_data = uploaded_file.value[0]
            image = Image.open(file_data.contents)
            return mo.image(image, caption="Uploaded Invoice", width=400)
        except Exception as e:
            return mo.md(f"❌ Error displaying image: {e}")
    else:
        return mo.md("👆 Upload an invoice image to see it here")


@app.cell
def process_invoice_handler(process_button, uploaded_file, datetime, os, process_invoice_with_llm, save_to_database_robust, mo, pd):
    # Process invoice when button is clicked
    if process_button and process_button.value and uploaded_file and uploaded_file.value:
        try:
            file_data = uploaded_file.value[0]
            temp_path = f"temp_invoice_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            
            with open(temp_path, "wb") as f:
                f.write(file_data.contents)
            
            # Process with LLM
            with mo.status.spinner(title="Processing invoice with AI..."):
                invoice_data = process_invoice_with_llm(temp_path)
            
            if invoice_data:
                # Save to database
                invoice_id = save_to_database_robust(invoice_data, temp_path)
                if invoice_id:
                    success_msg = mo.md("✅ Invoice processed and saved successfully!")
                    
                    # Display extracted data
                    extracted_data = pd.DataFrame([{
                        'Shop Name': invoice_data.get('shop_name', 'N/A'),
                        'Invoice Date': invoice_data.get('invoice_date', 'N/A'),
                        'Invoice Time': invoice_data.get('invoice_time', 'N/A'),
                        'Total Amount': f"Rp {invoice_data.get('total_amount', 0):,.2f}",
                        'Payment Method': invoice_data.get('payment_method', 'N/A'),
                        'Items Count': len(invoice_data.get('items', []))
                    }])
                    
                    extracted_table = mo.ui.table(extracted_data, label="📋 Extracted Information")
                    
                    # Display items if available
                    if invoice_data.get('items'):
                        items_df = pd.DataFrame(invoice_data['items'])
                        items_df['unit_price'] = items_df['unit_price'].apply(lambda x: f"Rp {x:,.2f}" if pd.notna(x) else "N/A")
                        items_df['total_price'] = items_df['total_price'].apply(lambda x: f"Rp {x:,.2f}")
                        items_table = mo.ui.table(items_df, label="🛒 Items")
                        
                        return mo.vstack([success_msg, extracted_table, items_table])
                    else:
                        return mo.vstack([success_msg, extracted_table])
                else:
                    return mo.md("❌ Failed to save to database")
            else:
                return mo.md("❌ Failed to extract invoice data")
            
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
        except Exception as e:
            return mo.md(f"❌ Error processing invoice: {e}")
    elif process_button and process_button.value:
        return mo.md("⚠️ Please upload an invoice image first")
    else:
        return mo.md("👆 Upload and process an invoice to see results here")


@app.cell
def get_invoice_data(db_session, pd, sqlite3):
    # Get invoice data from database
    if not db_session:
        return pd.DataFrame(), pd.DataFrame()
    
    try:
        conn = sqlite3.connect('invoices.db')
        invoices_df = pd.read_sql_query("""
            SELECT * FROM invoices 
            ORDER BY processed_at DESC
        """, conn)
        
        items_df = pd.read_sql_query("""
            SELECT ii.*, i.shop_name, i.invoice_date 
            FROM invoice_items ii
            JOIN invoices i ON ii.invoice_id = i.id
            ORDER BY i.processed_at DESC
        """, conn)
        
        conn.close()
        return invoices_df, items_df
    except Exception as e:
        return pd.DataFrame(), pd.DataFrame()


@app.cell
def create_dashboard_section(tab_selection, invoices_df, mo, pd, px, datetime, timedelta):
    # Dashboard Section
    if tab_selection.value == "dashboard":
        dashboard_header = mo.md("## 📊 Dashboard")
        
        if invoices_df.empty:
            return mo.vstack([dashboard_header, mo.md("📭 No invoice data available. Upload some invoices first!")])
        
        # Convert processed_at to datetime
        invoices_df_dashboard = invoices_df.copy()
        invoices_df_dashboard['processed_at'] = pd.to_datetime(invoices_df_dashboard['processed_at'])
        
        # Metrics
        total_invoices = len(invoices_df_dashboard)
        total_amount = invoices_df_dashboard['total_amount'].sum()
        avg_amount = invoices_df_dashboard['total_amount'].mean()
        unique_shops = invoices_df_dashboard['shop_name'].nunique()
        
        metrics_df = pd.DataFrame([
            {'Metric': 'Total Invoices', 'Value': f"{total_invoices:,}"},
            {'Metric': 'Total Amount', 'Value': f"Rp {total_amount:,.2f}"},
            {'Metric': 'Average Amount', 'Value': f"Rp {avg_amount:,.2f}"},
            {'Metric': 'Unique Shops', 'Value': f"{unique_shops:,}"}
        ])
        
        metrics_table = mo.ui.table(metrics_df, label="📈 Key Metrics")
        
        # Daily spending chart
        daily_spending = invoices_df_dashboard.groupby(invoices_df_dashboard['processed_at'].dt.date)['total_amount'].sum().reset_index()
        fig_line = px.line(
            daily_spending, 
            x='processed_at', 
            y='total_amount',
            title='Daily Spending Trend',
            labels={'total_amount': 'Amount (Rp)', 'processed_at': 'Date'}
        )
        daily_chart = mo.ui.plotly(fig_line)
        
        # Top shops chart
        top_shops = invoices_df_dashboard.groupby('shop_name')['total_amount'].sum().nlargest(10).reset_index()
        fig_bar = px.bar(
            top_shops,
            x='total_amount',
            y='shop_name',
            orientation='h',
            title='Top 10 Shops by Total Spending',
            labels={'total_amount': 'Total Amount (Rp)', 'shop_name': 'Shop Name'}
        )
        shops_chart = mo.ui.plotly(fig_bar)
        
        # Recent activity
        recent_invoices = invoices_df_dashboard.head(10)[['shop_name', 'total_amount', 'invoice_date', 'processed_at']]
        recent_table = mo.ui.table(recent_invoices, label="📅 Recent Activity")
        
        return mo.vstack([
            dashboard_header, 
            metrics_table,
            mo.hstack([daily_chart, shops_chart]),
            recent_table
        ])


@app.cell
def get_detailed_invoice_data(db_session, pd, sqlite3):
    # Get detailed invoice data with items for enhanced view
    if not db_session:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    
    try:
        conn = sqlite3.connect('invoices.db')

        # Get invoices with item counts and totals
        detailed_query = """
            SELECT 
                i.*,
                COUNT(ii.id) as item_count,
                GROUP_CONCAT(ii.item_name, ', ') as item_names_preview
            FROM invoices i
            LEFT JOIN invoice_items ii ON i.id = ii.invoice_id
            GROUP BY i.id
            ORDER BY i.processed_at DESC
        """
        invoices_detailed_df = pd.read_sql_query(detailed_query, conn)

        # Get all items with invoice details
        items_query = """
            SELECT 
                ii.*,
                i.shop_name,
                i.invoice_date,
                i.total_amount as invoice_total
            FROM invoice_items ii
            JOIN invoices i ON ii.invoice_id = i.id
            ORDER BY i.processed_at DESC, ii.id
        """
        items_detailed_df = pd.read_sql_query(items_query, conn)

        # Get summary statistics
        stats_query = """
            SELECT 
                COUNT(DISTINCT i.id) as total_invoices,
                COUNT(DISTINCT i.shop_name) as unique_shops,
                COUNT(ii.id) as total_items,
                SUM(i.total_amount) as total_spent,
                AVG(i.total_amount) as avg_invoice_amount,
                MIN(i.processed_at) as first_invoice,
                MAX(i.processed_at) as last_invoice
            FROM invoices i
            LEFT JOIN invoice_items ii ON i.id = ii.invoice_id
        """
        stats_detailed_df = pd.read_sql_query(stats_query, conn)

        conn.close()
        return invoices_detailed_df, items_detailed_df, stats_detailed_df

    except Exception as e:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()


@app.cell
def create_view_invoices_section(tab_selection, invoices_detailed_df, items_detailed_df, stats_detailed_df, mo, pd, datetime, json):
    # Enhanced view all invoices page
    if tab_selection.value == "invoices":
        invoices_header = mo.md("## 📋 Enhanced Invoice Data View")
        
        if invoices_detailed_df.empty:
            return mo.vstack([invoices_header, mo.md("📭 No invoice data available. Upload some invoices first!")])
        
        # Quick Stats Section
        if not stats_detailed_df.empty:
            stats = stats_detailed_df.iloc[0]
            stats_df = pd.DataFrame([
                {'Metric': 'Total Invoices', 'Value': f"{stats['total_invoices']:,}"},
                {'Metric': 'Unique Shops', 'Value': f"{stats['unique_shops']:,}"},
                {'Metric': 'Total Items', 'Value': f"{stats['total_items']:,}"},
                {'Metric': 'Total Spent', 'Value': f"Rp {stats['total_spent']:,.0f}"},
                {'Metric': 'Avg Invoice', 'Value': f"Rp {stats['avg_invoice_amount']:,.0f}"}
            ])
            stats_table = mo.ui.table(stats_df, label="📊 Quick Statistics")
        
        # Invoice table with enhanced columns
        display_columns = ['shop_name', 'total_amount', 'invoice_date', 'invoice_time', 'payment_method', 'item_count', 'processed_at']
        display_df = invoices_detailed_df[display_columns].copy()
        
        # Format amounts
        display_df['total_amount'] = display_df['total_amount'].apply(lambda x: f"Rp {x:,.2f}")
        
        invoice_table = mo.ui.table(
            display_df,
            label="💳 All Invoices",
            sortable=True,
            filterable=True
        )
        
        return mo.vstack([
            invoices_header,
            stats_table,
            invoice_table
        ])


@app.cell
def create_search_filter_section(tab_selection, invoices_df, mo, pd, datetime):
    # Search and filter invoices page
    if tab_selection.value == "search":
        search_header = mo.md("## 🔍 Search & Filter")
        
        if invoices_df.empty:
            return mo.vstack([search_header, mo.md("📭 No invoice data available.")])
        
        # Filters
        shop_names = ['All'] + sorted(invoices_df['shop_name'].dropna().unique().tolist())
        shop_selector = mo.ui.dropdown(
            options=shop_names,
            value="All",
            label="Filter by Shop"
        )
        
        # Date range filter - using processed_at
        invoices_df_search = invoices_df.copy()
        invoices_df_search['processed_at'] = pd.to_datetime(invoices_df_search['processed_at'])
        min_date = invoices_df_search['processed_at'].min().date()
        max_date = invoices_df_search['processed_at'].max().date()
        
        date_start = mo.ui.date(value=min_date, label="Start Date")
        date_end = mo.ui.date(value=max_date, label="End Date")
        
        # Amount range filter
        min_amount = float(invoices_df['total_amount'].min())
        max_amount = float(invoices_df['total_amount'].max())
        
        amount_slider = mo.ui.range_slider(
            start=min_amount,
            stop=max_amount,
            value=[min_amount, max_amount],
            label="Amount Range (Rp)",
            step=1000
        )
        
        # Text search
        search_text = mo.ui.text(label="Search in shop name or address", full_width=True)
        
        filters_section = mo.vstack([
            search_header,
            mo.hstack([shop_selector, date_start, date_end]),
            amount_slider,
            search_text
        ])
        
        return filters_section, shop_selector, date_start, date_end, amount_slider, search_text
    else:
        return None, None, None, None, None, None


@app.cell
def apply_search_filters(shop_selector, date_start, date_end, amount_slider, search_text, invoices_df, tab_selection, mo, pd, datetime):
    # Apply filters and show results
    if tab_selection.value == "search" and shop_selector is not None:
        filtered_df = invoices_df.copy()
        filtered_df['processed_at'] = pd.to_datetime(filtered_df['processed_at'])
        
        # Apply shop filter
        if shop_selector.value != 'All':
            filtered_df = filtered_df[filtered_df['shop_name'] == shop_selector.value]
        
        # Apply date filter
        if date_start.value and date_end.value:
            start_date = pd.to_datetime(date_start.value)
            end_date = pd.to_datetime(date_end.value)
            filtered_df = filtered_df[
                (filtered_df['processed_at'] >= start_date) &
                (filtered_df['processed_at'] <= end_date)
            ]
        
        # Apply amount filter
        if amount_slider.value:
            min_amt, max_amt = amount_slider.value
            filtered_df = filtered_df[
                (filtered_df['total_amount'] >= min_amt) &
                (filtered_df['total_amount'] <= max_amt)
            ]
        
        # Apply text search
        if search_text.value:
            mask = (
                filtered_df['shop_name'].str.contains(search_text.value, case=False, na=False) |
                filtered_df['shop_address'].str.contains(search_text.value, case=False, na=False)
            )
            filtered_df = filtered_df[mask]
        
        # Display results
        results_header = mo.md(f"### Results ({len(filtered_df)} invoices)")
        
        if not filtered_df.empty:
            # Summary metrics
            summary_df = pd.DataFrame([
                {'Metric': 'Filtered Invoices', 'Value': f"{len(filtered_df):,}"},
                {'Metric': 'Total Amount', 'Value': f"Rp {filtered_df['total_amount'].sum():,.2f}"},
                {'Metric': 'Average Amount', 'Value': f"Rp {filtered_df['total_amount'].mean():,.2f}"}
            ])
            summary_table = mo.ui.table(summary_df, label="📊 Filter Summary")
            
            # Results table
            display_columns = ['shop_name', 'total_amount', 'invoice_date', 'invoice_time', 'payment_method', 'processed_at']
            results_table = mo.ui.table(
                filtered_df[display_columns],
                label="📋 Filtered Results",
                sortable=True
            )
            
            return mo.vstack([results_header, summary_table, results_table])
        else:
            return mo.vstack([results_header, mo.md("📭 No invoices match the current filters.")])


@app.cell
def create_analytics_section(tab_selection, invoices_detailed_df, items_detailed_df, mo, pd, px, datetime):
    # Advanced data analytics page
    if tab_selection.value == "analytics":
        analytics_header = mo.md("## 📈 Advanced Data Analytics")
        
        if invoices_detailed_df.empty:
            return mo.vstack([analytics_header, mo.md("📭 No data available for analysis.")])
        
        # Convert processed_at to datetime and add time components
        invoices_analytics_df = invoices_detailed_df.copy()
        invoices_analytics_df['processed_at'] = pd.to_datetime(invoices_analytics_df['processed_at'])
        invoices_analytics_df['month'] = invoices_analytics_df['processed_at'].dt.to_period('M')
        invoices_analytics_df['weekday'] = invoices_analytics_df['processed_at'].dt.day_name()
        invoices_analytics_df['hour'] = invoices_analytics_df['processed_at'].dt.hour
        
        # Monthly spending trend
        monthly_spending = invoices_analytics_df.groupby('month')['total_amount'].agg(['sum', 'count', 'mean']).reset_index()
        monthly_spending['month_str'] = monthly_spending['month'].astype(str)
        
        fig_monthly = px.line(
            monthly_spending, 
            x='month_str', 
            y='sum',
            title="Monthly Spending Trend",
            labels={'sum': 'Total Amount (Rp)', 'month_str': 'Month'}
        )
        monthly_chart = mo.ui.plotly(fig_monthly)
        
        # Spending distribution
        fig_hist = px.histogram(
            invoices_analytics_df, 
            x='total_amount', 
            nbins=20,
            title="Spending Distribution",
            labels={'total_amount': 'Amount (Rp)', 'count': 'Frequency'}
        )
        distribution_chart = mo.ui.plotly(fig_hist)
        
        # Weekday spending pattern
        weekday_spending = invoices_analytics_df.groupby('weekday')['total_amount'].sum().reset_index()
        weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        weekday_spending['weekday'] = pd.Categorical(weekday_spending['weekday'], categories=weekday_order, ordered=True)
        weekday_spending = weekday_spending.sort_values('weekday')
        
        fig_weekday = px.bar(
            weekday_spending, 
            x='weekday', 
            y='total_amount',
            title="Spending by Day of Week",
            labels={'total_amount': 'Total Amount (Rp)', 'weekday': 'Day of Week'}
        )
        weekday_chart = mo.ui.plotly(fig_weekday)
        
        # Analytics tabs for different views
        analytics_tabs = mo.ui.tabs({
            "📊 Spending Patterns": mo.vstack([monthly_chart, distribution_chart]),
            "📅 Time Analysis": weekday_chart
        })
        
        return mo.vstack([analytics_header, analytics_tabs])


@app.cell
def create_item_analytics(tab_selection, items_detailed_df, mo, pd, px):
    # Item analysis section
    if tab_selection.value == "analytics" and not items_detailed_df.empty:
        # Top items by frequency
        top_items = items_detailed_df.groupby('item_name').agg({
            'quantity': 'sum',
            'total_price': 'sum',
            'invoice_id': 'count'
        }).reset_index()
        top_items = top_items.sort_values('invoice_id', ascending=False).head(10)
        
        fig_items = px.bar(
            top_items, 
            x='invoice_id', 
            y='item_name',
            orientation='h', 
            title="Most Frequently Purchased Items",
            labels={'invoice_id': 'Number of Purchases', 'item_name': 'Item'}
        )
        items_chart = mo.ui.plotly(fig_items)
        
        # Top items by total spending
        top_spending_items = items_detailed_df.groupby('item_name')['total_price'].sum().nlargest(10).reset_index()
        
        fig_spending = px.bar(
            top_spending_items, 
            x='total_price', 
            y='item_name',
            orientation='h', 
            title="Items by Total Spending",
            labels={'total_price': 'Total Spent (Rp)', 'item_name': 'Item'}
        )
        spending_chart = mo.ui.plotly(fig_spending)
        
        return mo.hstack([items_chart, spending_chart])


@app.cell
def create_data_management_section(tab_selection, stats_detailed_df, mo, pd, sqlite3, datetime, json):
    # Data management and maintenance page
    if tab_selection.value == "management":
        management_header = mo.md("## ⚙️ Data Management")
        
        # Database overview
        overview_section = mo.md("### 📊 Database Overview")
        
        if not stats_detailed_df.empty:
            stats = stats_detailed_df.iloc[0]
            overview_df = pd.DataFrame([
                {'Metric': 'Total Invoices', 'Value': f"{stats['total_invoices']:,}"},
                {'Metric': 'Total Items', 'Value': f"{stats['total_items']:,}"},
                {'Metric': 'Unique Shops', 'Value': f"{stats['unique_shops']:,}"},
                {'Metric': 'Total Amount', 'Value': f"Rp {stats['total_spent']:,.2f}"},
                {'Metric': 'Date Range', 'Value': f"{stats['first_invoice']} to {stats['last_invoice']}"}
            ])
            overview_table = mo.ui.table(overview_df, label="📈 Database Statistics")
        else:
            overview_table = mo.md("📭 No data available")
        
        # Database actions
        actions_section = mo.md("### 🔧 Database Actions")
        
        clear_confirm = mo.ui.checkbox(label="I confirm I want to delete ALL data")
        clear_button = mo.ui.run_button(label="🗑️ Clear All Data", kind="secondary")
        
        schema_button = mo.ui.run_button(label="📋 View Database Schema")
        
        return mo.vstack([
            management_header,
            overview_section,
            overview_table,
            actions_section,
            mo.hstack([clear_confirm, clear_button]),
            schema_button
        ]), clear_confirm, clear_button, schema_button


@app.cell
def handle_management_actions(clear_confirm, clear_button, schema_button, mo, sqlite3):
    # Handle data management actions
    if clear_button and clear_button.value and clear_confirm and clear_confirm.value:
        try:
            conn = sqlite3.connect('invoices.db')
            conn.execute("DELETE FROM invoice_items")
            conn.execute("DELETE FROM invoices")
            conn.commit()
            conn.close()
            return mo.md("✅ All data cleared successfully!")
        except Exception as e:
            return mo.md(f"❌ Error clearing data: {e}")
    
    elif schema_button and schema_button.value:
        try:
            conn = sqlite3.connect('invoices.db')
            cursor = conn.cursor()
            cursor.execute("SELECT sql FROM sqlite_master WHERE type='table'")
            schemas = cursor.fetchall()
            conn.close()
            
            schema_text = "\n\n".join([schema[0] for schema in schemas if schema[0]])
            return mo.md(f"### Database Schema\n```sql\n{schema_text}\n```")
        except Exception as e:
            return mo.md(f"❌ Error viewing schema: {e}")
    
    elif clear_button and clear_button.value:
        return mo.md("⚠️ Please confirm data deletion by checking the checkbox first")


@app.cell
def data_quality_check(invoices_df, mo, pd, datetime):
    # Data Quality Section for management page
    if not invoices_df.empty:
        quality_header = mo.md("### 🔍 Data Quality Check")
        
        # Missing data analysis
        missing_data = invoices_df.isnull().sum()
        missing_data = missing_data[missing_data > 0]
        
        if not missing_data.empty:
            missing_df = missing_data.reset_index()
            missing_df.columns = ['Column', 'Missing Count']
            missing_table = mo.ui.table(missing_df, label="📊 Missing Data")
        else:
            missing_table = mo.md("✅ No missing data found!")
        
        # Duplicate analysis
        duplicates = invoices_df.duplicated(subset=['shop_name', 'total_amount', 'invoice_date']).sum()
        duplicates_info = mo.md(f"**Potential Duplicates:** {duplicates}")
        
        # Data validation
        negative_amounts = (invoices_df['total_amount'] < 0).sum()
        zero_amounts = (invoices_df['total_amount'] == 0).sum()
        future_dates = (pd.to_datetime(invoices_df['processed_at'], errors='coerce') > datetime.now()).sum()
        
        validation_df = pd.DataFrame([
            {'Check': 'Negative amounts', 'Count': negative_amounts},
            {'Check': 'Zero amounts', 'Count': zero_amounts},
            {'Check': 'Future dates', 'Count': future_dates}
        ])
        validation_table = mo.ui.table(validation_df, label="🔍 Data Validation")
        
        return mo.vstack([
            quality_header,
            missing_table,
            duplicates_info,
            validation_table
        ])


@app.cell
def footer_info(mo):
    # Footer information
    mo.md("""
    ---
    💡 **Tips:**
    - Upload clear, well-lit invoice images for best results
    - The AI extracts shop name, items, amounts, and dates automatically
    - Use the search & filter feature to find specific invoices
    - Analytics show spending patterns and trends over time
    - Data management allows you to backup or clear your data
    """)


if __name__ == "__main__":
    app.run()
