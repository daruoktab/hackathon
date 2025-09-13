#!/usr/bin/env python3
"""
Streamlit UI for Invoice Processing System
"""

import streamlit as st
import os
import sys
import sqlite3
import pandas as pd
from datetime import datetime
import plotly.express as px
from PIL import Image
import json

# Add the src directory to Python path - fix the path resolution
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(os.path.dirname(current_dir), 'src')
sys.path.insert(0, src_dir)

# Database path - use the main repo database
REPO_DB_PATH = os.path.abspath(os.path.join(current_dir, '..', 'invoices.db'))

try:
    from processor import process_invoice_with_llm, save_to_database_robust, create_tables
    from database import get_db_session, Invoice, InvoiceItem
    IMPORTS_SUCCESS = True
except ImportError as e:
    st.error(f"Import error: {e}")
    IMPORTS_SUCCESS = False
    # Define dummy functions to prevent errors
    def process_invoice_with_llm(*args, **kwargs):
        return None
    def save_to_database_robust(*args, **kwargs):
        return None
    def create_tables(*args, **kwargs):
        pass

# Page configuration
st.set_page_config(
    page_title="Invoice Processing System",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #c3e6cb;
    }
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #f5c6cb;
    }
    .data-table {
        font-size: 0.9rem;
    }
    .invoice-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #dee2e6;
        margin-bottom: 1rem;
    }
    .stat-card {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #28a745;
    }
</style>
""", unsafe_allow_html=True)

def init_database():
    """Initialize database tables"""
    try:
        create_tables()
        return True
    except Exception as e:
        st.error(f"Database initialization failed: {e}")
        return False

def get_invoice_data():
    """Get invoice data from database"""
    try:
        conn = sqlite3.connect(REPO_DB_PATH)
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
        st.error(f"Error loading data: {e}")
        return pd.DataFrame(), pd.DataFrame()

def process_uploaded_image(uploaded_file):
    """Process uploaded image and extract invoice data"""
    if uploaded_file is not None:
        # Save uploaded file temporarily
        temp_path = f"temp_{uploaded_file.name}"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        try:
            # Process with LLM
            with st.spinner("Processing invoice with AI..."):
                invoice_data = process_invoice_with_llm(temp_path)
            
            if invoice_data:
                # Save to database
                invoice_id = save_to_database_robust(invoice_data, temp_path)
                if invoice_id:
                    st.success("✅ Invoice processed and saved successfully!")
                    return invoice_data, temp_path
                else:
                    st.error("❌ Failed to save to database")
                    return None, None
            else:
                st.error("❌ Failed to extract invoice data")
                return None, None
        
        except Exception as e:
            st.error(f"❌ Error processing invoice: {e}")
            return None, None
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    return None, None

def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown('<h1 class="main-header">📄 Invoice Processing System</h1>', unsafe_allow_html=True)
    
    # Check API key
    if not os.getenv("GROQ_API_KEY"):
        st.error("⚠️ GROQ_API_KEY not found in environment variables. Please set it up.")
        st.info("Create a .env file in the project root with: GROQ_API_KEY=your_key_here")
        return
    
    # Initialize database
    if not init_database():
        return
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page",
        ["📤 Upload & Process", "📊 Dashboard", "📋 View Invoices", "🔍 Search & Filter", "📈 Data Analytics", "⚙️ Data Management"]
    )
    
    if page == "📤 Upload & Process":
        upload_and_process_page()
    elif page == "📊 Dashboard":
        dashboard_page()
    elif page == "📋 View Invoices":
        view_invoices_page()
    elif page == "🔍 Search & Filter":
        search_and_filter_page()
    elif page == "📈 Data Analytics":
        data_analytics_page()
    elif page == "⚙️ Data Management":
        data_management_page()

def upload_and_process_page():
    """Upload and process invoice page"""
    st.header("📤 Upload & Process Invoice")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Upload Invoice Image")
        uploaded_file = st.file_uploader(
            "Choose an invoice image...",
            type=['jpg', 'jpeg', 'png'],
            help="Upload a clear image of your invoice"
        )
        
        if uploaded_file is not None:
            # Display uploaded image
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Invoice", width='stretch')

            # Process button
            if st.button("🔄 Process Invoice", type="primary"):
                invoice_data, temp_path = process_uploaded_image(uploaded_file)
                
                if invoice_data:
                    st.session_state['last_processed'] = invoice_data
    
    with col2:
        st.subheader("Processing Results")
        
        if 'last_processed' in st.session_state:
            data = st.session_state['last_processed']
            
            # Display extracted data
            st.markdown("### 📋 Extracted Information")
            
            col2_1, col2_2 = st.columns(2)
            with col2_1:
                st.metric("Shop Name", data.get('shop_name', 'N/A'))
                st.metric("Invoice Date", data.get('invoice_date', 'N/A'))
                st.metric("Invoice Time", data.get('invoice_time', 'N/A'))
                st.metric("Payment Method", data.get('payment_method', 'N/A'))
            
            with col2_2:
                st.metric("Total Amount", f"Rp {data.get('total_amount', 0):,.2f}")
                st.metric("Subtotal", f"Rp {data.get('subtotal', 0):,.2f}" if data.get('subtotal') else 'N/A')
                st.metric("Tax", f"Rp {data.get('tax', 0):,.2f}" if data.get('tax') else 'N/A')
                st.metric("Discount", f"Rp {data.get('discount', 0):,.2f}" if data.get('discount') else 'N/A')
            
            # Display items
            if data.get('items'):
                st.markdown("### 🛒 Items")
                items_df = pd.DataFrame(data['items'])
                st.dataframe(items_df, width='stretch')
        else:
            st.info("👆 Upload and process an invoice to see results here")

def dashboard_page():
    """Dashboard with analytics"""
    st.header("📊 Dashboard")
    
    # Load data
    invoices_df, items_df = get_invoice_data()
    
    if invoices_df.empty:
        st.info("No invoice data available. Upload some invoices first!")
        return
    
    # Convert processed_at to datetime
    invoices_df['processed_at'] = pd.to_datetime(invoices_df['processed_at'])
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_invoices = len(invoices_df)
        st.metric("Total Invoices", total_invoices)
    
    with col2:
        total_amount = invoices_df['total_amount'].sum()
        st.metric("Total Amount", f"Rp {total_amount:,.2f}")
    
    with col3:
        avg_amount = invoices_df['total_amount'].mean()
        st.metric("Average Amount", f"Rp {avg_amount:,.2f}")
    
    with col4:
        unique_shops = invoices_df['shop_name'].nunique()
        st.metric("Unique Shops", unique_shops)
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Daily spending over time
        daily_spending = invoices_df.groupby(invoices_df['processed_at'].dt.date)['total_amount'].sum().reset_index()
        fig_line = px.line(
            daily_spending, 
            x='processed_at', 
            y='total_amount',
            title='Daily Spending Trend',
            labels={'total_amount': 'Amount (Rp)', 'processed_at': 'Date'}
        )
        st.plotly_chart(fig_line, width='stretch')

    with col2:
        # Top shops by spending
        top_shops = invoices_df.groupby('shop_name')['total_amount'].sum().nlargest(10).reset_index()
        fig_bar = px.bar(
            top_shops,
            x='total_amount',
            y='shop_name',
            orientation='h',
            title='Top 10 Shops by Total Spending',
            labels={'total_amount': 'Total Amount (Rp)', 'shop_name': 'Shop Name'}
        )
        st.plotly_chart(fig_bar, width='stretch')

    # Recent activity
    st.subheader("📅 Recent Activity")
    recent_invoices = invoices_df.head(10)[['shop_name', 'total_amount', 'invoice_date', 'processed_at']]
    st.dataframe(recent_invoices, width='stretch')

def get_detailed_invoice_data():
    """Get detailed invoice data with items for enhanced view"""
    try:
        conn = sqlite3.connect(REPO_DB_PATH)

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

        invoices_df = pd.read_sql_query(detailed_query, conn)

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

        items_df = pd.read_sql_query(items_query, conn)

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

        stats_df = pd.read_sql_query(stats_query, conn)

        conn.close()
        return invoices_df, items_df, stats_df

    except Exception as e:
        st.error(f"Error loading detailed data: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

def view_invoices_page():
    """Enhanced view all invoices page"""
    st.header("📋 Enhanced Invoice Data View")

    # Load detailed data
    invoices_df, items_df, stats_df = get_detailed_invoice_data()

    if invoices_df.empty:
        st.info("No invoice data available. Upload some invoices first!")
        return
    
    # Quick Stats Section
    if not stats_df.empty:
        stats = stats_df.iloc[0]
        st.subheader("📊 Quick Statistics")

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.markdown(f"""
            <div class="stat-card">
                <h3 style="margin:0; color: #28a745;">{stats['total_invoices']}</h3>
                <p style="margin:0; color: #6c757d;">Total Invoices</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="stat-card">
                <h3 style="margin:0; color: #17a2b8;">{stats['unique_shops']}</h3>
                <p style="margin:0; color: #6c757d;">Unique Shops</p>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="stat-card">
                <h3 style="margin:0; color: #ffc107;">{stats['total_items']}</h3>
                <p style="margin:0; color: #6c757d;">Total Items</p>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            st.markdown(f"""
            <div class="stat-card">
                <h3 style="margin:0; color: #dc3545;">Rp {stats['total_spent']:,.0f}</h3>
                <p style="margin:0; color: #6c757d;">Total Spent</p>
            </div>
            """, unsafe_allow_html=True)

        with col5:
            st.markdown(f"""
            <div class="stat-card">
                <h3 style="margin:0; color: #6f42c1;">Rp {stats['avg_invoice_amount']:,.0f}</h3>
                <p style="margin:0; color: #6c757d;">Avg Invoice</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # Display Controls
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

    with col1:
        view_mode = st.radio("View Mode", ["📋 Table View", "🗂️ Card View", "📊 Detail View"], horizontal=True)

    with col2:
        items_per_page = st.selectbox("Items per page", [10, 25, 50, 100], index=1)
    
    with col3:
        sort_by = st.selectbox("Sort by",
                              ["processed_at", "total_amount", "shop_name", "invoice_date", "item_count"])

    with col4:
        sort_order = st.selectbox("Order", ["Descending", "Ascending"])

    # Apply sorting
    ascending = sort_order == "Ascending"
    invoices_df = invoices_df.sort_values(sort_by, ascending=ascending)

    # Pagination
    total_items = len(invoices_df)
    total_pages = (total_items - 1) // items_per_page + 1
    
    if total_pages > 1:
        page_num = st.number_input("Page", min_value=1, max_value=total_pages, value=1)
        start_idx = (page_num - 1) * items_per_page
        end_idx = start_idx + items_per_page
        display_df = invoices_df.iloc[start_idx:end_idx]
        st.info(f"Showing {start_idx + 1}-{min(end_idx, total_items)} of {total_items} invoices")
    else:
        display_df = invoices_df
    
    # Display based on selected view mode
    if view_mode == "📋 Table View":
        display_table_view(display_df)
    elif view_mode == "🗂️ Card View":
        display_card_view(display_df, items_df)
    elif view_mode == "📊 Detail View":
        display_detail_view(display_df, items_df)

    # Export options
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📥 Export All Invoices to CSV"):
            csv_data = invoices_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv_data,
                file_name=f"all_invoices_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

    with col2:
        if st.button("📥 Export Items to CSV"):
            csv_data = items_df.to_csv(index=False)
            st.download_button(
                label="Download Items CSV",
                data=csv_data,
                file_name=f"all_items_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

    with col3:
        if st.button("📋 Export to JSON"):
            # Create comprehensive export
            export_data = {
                'export_date': datetime.now().isoformat(),
                'total_invoices': len(invoices_df),
                'invoices': invoices_df.to_dict('records'),
                'items': items_df.to_dict('records')
            }
            json_data = json.dumps(export_data, indent=2, default=str)
            st.download_button(
                label="Download JSON",
                data=json_data,
                file_name=f"invoice_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

def display_table_view(df):
    """Display invoices in enhanced table format"""
    st.subheader("📋 Invoice Table")

    # Select columns to display
    available_columns = df.columns.tolist()
    default_columns = ['shop_name', 'total_amount', 'invoice_date', 'invoice_time',
                      'payment_method', 'item_count', 'processed_at']

    selected_columns = st.multiselect(
        "Select columns to display:",
        available_columns,
        default=[col for col in default_columns if col in available_columns]
    )

    if selected_columns:
        display_df = df[selected_columns].copy()

        # Format numeric columns
        if 'total_amount' in display_df.columns:
            display_df['total_amount'] = display_df['total_amount'].apply(lambda x: f"Rp {x:,.2f}" if pd.notna(x) else "N/A")

        # Format datetime columns
        for col in display_df.columns:
            if 'processed_at' in col or 'date' in col.lower():
                if display_df[col].dtype == 'object':
                    try:
                        display_df[col] = pd.to_datetime(display_df[col])
                    except (ValueError, TypeError):
                        pass  # Keep original values if conversion fails

        st.dataframe(
            display_df,
            width='stretch',
            column_config={
                "total_amount": st.column_config.TextColumn("Total Amount"),
                "shop_name": st.column_config.TextColumn("Shop Name", width="medium"),
                "item_count": st.column_config.NumberColumn("Items", format="%d"),
            }
        )
    else:
        st.warning("Please select at least one column to display.")

def display_card_view(df, items_df):
    """Display invoices in card format"""
    st.subheader("🗂️ Invoice Cards")

    for idx, row in df.iterrows():
        with st.container():
            st.markdown(f"""
            <div class="invoice-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h4 style="margin: 0; color: #495057;">🏪 {row['shop_name']}</h4>
                    <span style="font-size: 1.2em; font-weight: bold; color: #28a745;">Rp {row['total_amount']:,.2f}</span>
                </div>
                <div style="margin: 0.5rem 0;">
                    <span style="color: #6c757d;">📅 {row['invoice_date']} ⏰ {row.get('invoice_time', 'N/A')}</span>
                </div>
                <div style="margin: 0.5rem 0;">
                    <span style="color: #6c757d;">🛒 {row['item_count']} items | 💳 {row.get('payment_method', 'N/A')}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Add expandable section for items
            invoice_items = items_df[items_df['invoice_id'] == row['id']]
            if not invoice_items.empty:
                with st.expander(f"View {len(invoice_items)} items"):
                    items_display = invoice_items[['item_name', 'quantity', 'unit_price', 'total_price']].copy()
                    items_display['unit_price'] = items_display['unit_price'].apply(lambda x: f"Rp {x:,.2f}")
                    items_display['total_price'] = items_display['total_price'].apply(lambda x: f"Rp {x:,.2f}")
                    st.dataframe(items_display, width='stretch', hide_index=True)

def display_detail_view(df, items_df):
    """Display invoices with full details"""
    st.subheader("📊 Detailed View")

    for idx, row in df.iterrows():
        with st.expander(f"🏪 {row['shop_name']} - Rp {row['total_amount']:,.2f} ({row['invoice_date']})", expanded=False):

            # Invoice details in columns
            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown("**📋 Invoice Info**")
                st.write(f"**Number:** {row.get('invoice_number', 'N/A')}")
                st.write(f"**Date:** {row['invoice_date']}")
                st.write(f"**Time:** {row.get('invoice_time', 'N/A')}")
                st.write(f"**Processed:** {row['processed_at']}")

            with col2:
                st.markdown("**🏪 Shop Info**")
                st.write(f"**Name:** {row['shop_name']}")
                st.write(f"**Address:** {row.get('shop_address', 'N/A')}")
                st.write(f"**Cashier:** {row.get('cashier', 'N/A')}")

            with col3:
                st.markdown("**💰 Financial Details**")
                st.write(f"**Total:** Rp {row['total_amount']:,.2f}")
                if pd.notna(row.get('subtotal')):
                    st.write(f"**Subtotal:** Rp {row['subtotal']:,.2f}")
                if pd.notna(row.get('tax')):
                    st.write(f"**Tax:** Rp {row['tax']:,.2f}")
                if pd.notna(row.get('discount')):
                    st.write(f"**Discount:** Rp {row['discount']:,.2f}")
                st.write(f"**Payment:** {row.get('payment_method', 'N/A')}")

            # Items section
            invoice_items = items_df[items_df['invoice_id'] == row['id']]
            if not invoice_items.empty:
                st.markdown("**🛒 Items Purchased**")

                # Calculate item statistics
                total_qty = invoice_items['quantity'].sum()
                avg_price = invoice_items['unit_price'].mean()

                item_col1, item_col2 = st.columns([3, 1])

                with item_col1:
                    items_display = invoice_items[['item_name', 'quantity', 'unit_price', 'total_price']].copy()
                    items_display['unit_price'] = items_display['unit_price'].apply(lambda x: f"Rp {x:,.2f}")
                    items_display['total_price'] = items_display['total_price'].apply(lambda x: f"Rp {x:,.2f}")
                    st.dataframe(items_display, use_container_width=True, hide_index=True)

                with item_col2:
                    st.metric("Total Items", f"{total_qty:.0f}")
                    st.metric("Avg Item Price", f"Rp {avg_price:,.2f}")

def data_analytics_page():
    """Advanced data analytics page"""
    st.header("📈 Advanced Data Analytics")

    # Load data
    invoices_df, items_df, stats_df = get_detailed_invoice_data()

    if invoices_df.empty:
        st.info("No data available for analysis.")
        return
    
    # Convert processed_at to datetime
    invoices_df['processed_at'] = pd.to_datetime(invoices_df['processed_at'])
    invoices_df['month'] = invoices_df['processed_at'].dt.to_period('M')
    invoices_df['weekday'] = invoices_df['processed_at'].dt.day_name()
    invoices_df['hour'] = invoices_df['processed_at'].dt.hour

    # Tabs for different analytics
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Spending Patterns", "🛒 Item Analysis", "🏪 Shop Analysis", "📅 Time Analysis"])

    with tab1:
        st.subheader("💰 Spending Patterns")

        col1, col2 = st.columns(2)

        with col1:
            # Monthly spending trend
            monthly_spending = invoices_df.groupby('month')['total_amount'].agg(['sum', 'count', 'mean']).reset_index()
            monthly_spending['month_str'] = monthly_spending['month'].astype(str)

            fig_monthly = px.line(monthly_spending, x='month_str', y='sum',
                                title="Monthly Spending Trend",
                                labels={'sum': 'Total Amount (Rp)', 'month_str': 'Month'})
            st.plotly_chart(fig_monthly, use_container_width=True)

        with col2:
            # Spending distribution
            fig_hist = px.histogram(invoices_df, x='total_amount', nbins=20,
                                  title="Spending Distribution",
                                  labels={'total_amount': 'Amount (Rp)', 'count': 'Frequency'})
            st.plotly_chart(fig_hist, use_container_width=True)

    with tab2:
        st.subheader("🛒 Item Analysis")

        if not items_df.empty:
            col1, col2 = st.columns(2)

            with col1:
                # Top items by frequency
                top_items = items_df.groupby('item_name').agg({
                    'quantity': 'sum',
                    'total_price': 'sum',
                    'invoice_id': 'count'
                }).reset_index()
                top_items = top_items.sort_values('invoice_id', ascending=False).head(10)

                fig_items = px.bar(top_items, x='invoice_id', y='item_name',
                                 orientation='h', title="Most Frequently Purchased Items",
                                 labels={'invoice_id': 'Number of Purchases', 'item_name': 'Item'})
                st.plotly_chart(fig_items, use_container_width=True)

            with col2:
                # Top items by total spending
                top_spending_items = items_df.groupby('item_name')['total_price'].sum().nlargest(10).reset_index()

                fig_spending = px.bar(top_spending_items, x='total_price', y='item_name',
                                    orientation='h', title="Items by Total Spending",
                                    labels={'total_price': 'Total Spent (Rp)', 'item_name': 'Item'})
                st.plotly_chart(fig_spending, use_container_width=True)

    with tab3:
        st.subheader("🏪 Shop Analysis")

        col1, col2 = st.columns(2)

        with col1:
            # Shop visit frequency vs spending
            shop_analysis = invoices_df.groupby('shop_name').agg({
                'total_amount': ['sum', 'mean', 'count']
            }).round(2)
            shop_analysis.columns = ['Total_Spent', 'Avg_Amount', 'Visit_Count']
            shop_analysis = shop_analysis.reset_index()

            fig_scatter = px.scatter(shop_analysis, x='Visit_Count', y='Total_Spent',
                                   size='Avg_Amount', hover_name='shop_name',
                                   title="Shop Visit Frequency vs Total Spending",
                                   labels={'Visit_Count': 'Number of Visits', 'Total_Spent': 'Total Spent (Rp)'})
            st.plotly_chart(fig_scatter, use_container_width=True)

        with col2:
            # Average spending per shop
            avg_spending = invoices_df.groupby('shop_name')['total_amount'].mean().nlargest(10).reset_index()

            fig_avg = px.bar(avg_spending, x='total_amount', y='shop_name',
                           orientation='h', title="Average Spending per Shop (Top 10)",
                           labels={'total_amount': 'Average Amount (Rp)', 'shop_name': 'Shop'})
            st.plotly_chart(fig_avg, use_container_width=True)

    with tab4:
        st.subheader("📅 Time-based Analysis")

        col1, col2 = st.columns(2)

        with col1:
            # Weekday spending pattern
            weekday_spending = invoices_df.groupby('weekday')['total_amount'].sum().reset_index()
            weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            weekday_spending['weekday'] = pd.Categorical(weekday_spending['weekday'], categories=weekday_order, ordered=True)
            weekday_spending = weekday_spending.sort_values('weekday')

            fig_weekday = px.bar(weekday_spending, x='weekday', y='total_amount',
                               title="Spending by Day of Week",
                               labels={'total_amount': 'Total Amount (Rp)', 'weekday': 'Day of Week'})
            st.plotly_chart(fig_weekday, use_container_width=True)

        with col2:
            # Shopping frequency by hour (if time data available)
            if 'hour' in invoices_df.columns:
                hourly_freq = invoices_df.groupby('hour').size().reset_index(name='count')

                fig_hourly = px.line(hourly_freq, x='hour', y='count',
                                   title="Shopping Frequency by Hour",
                                   labels={'hour': 'Hour of Day', 'count': 'Number of Purchases'})
                st.plotly_chart(fig_hourly, use_container_width=True)
            else:
                st.info("Hour-based analysis not available (no time data)")

def data_management_page():
    """Data management and maintenance page"""
    st.header("⚙️ Data Management")

    # Load data
    invoices_df, items_df, stats_df = get_detailed_invoice_data()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 Database Overview")
        if not stats_df.empty:
            stats = stats_df.iloc[0]
            st.write(f"**Total Invoices:** {stats['total_invoices'] or 0}")
            st.write(f"**Total Items:** {stats['total_items'] or 0}")
            st.write(f"**Unique Shops:** {stats['unique_shops'] or 0}")
            total_spent = stats['total_spent'] or 0
            st.write(f"**Total Amount:** Rp {total_spent:,.2f}")
            first_invoice = stats['first_invoice'] or 'N/A'
            last_invoice = stats['last_invoice'] or 'N/A'
            st.write(f"**Date Range:** {first_invoice} to {last_invoice}")

    with col2:
        st.subheader("🔧 Database Actions")

        # Initialize session state for delete confirmation
        if 'delete_confirmation' not in st.session_state:
            st.session_state.delete_confirmation = False

        if not st.session_state.delete_confirmation:
            if st.button("🗑️ Clear All Data", type="secondary"):
                st.session_state.delete_confirmation = True
                st.rerun()
        else:
            st.warning("⚠️ This will permanently delete ALL invoice data!")
            col_a, col_b = st.columns(2)

            with col_a:
                if st.button("✅ Yes, Delete All", type="primary"):
                    try:
                        conn = sqlite3.connect(REPO_DB_PATH)
                        cursor = conn.cursor()

                        # Delete in correct order (items first, then invoices)
                        cursor.execute("DELETE FROM invoice_items")
                        items_deleted = cursor.rowcount
                        cursor.execute("DELETE FROM invoices")
                        invoices_deleted = cursor.rowcount

                        # Reset auto-increment counters
                        cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('invoices', 'invoice_items')")

                        conn.commit()
                        conn.close()

                        st.success(f"✅ All data cleared successfully! Deleted {invoices_deleted} invoices and {items_deleted} items.")
                        st.session_state.delete_confirmation = False
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error clearing data: {e}")
                        st.session_state.delete_confirmation = False

            with col_b:
                if st.button("❌ Cancel"):
                    st.session_state.delete_confirmation = False
                    st.rerun()

        if st.button("📋 View Database Schema"):
            try:
                conn = sqlite3.connect(REPO_DB_PATH)
                cursor = conn.cursor()

                # Get table schemas
                cursor.execute("SELECT sql FROM sqlite_master WHERE type='table'")
                schemas = cursor.fetchall()

                for schema in schemas:
                    st.code(schema[0], language="sql")

                conn.close()
            except Exception as e:
                st.error(f"Error viewing schema: {e}")

    # Data Quality Section
    st.markdown("---")
    st.subheader("🔍 Data Quality Check")

    if not invoices_df.empty:
        col1, col2, col3 = st.columns(3)

        with col1:
            # Missing data analysis
            st.write("**Missing Data:**")
            missing_data = invoices_df.isnull().sum()
            missing_data = missing_data[missing_data > 0]
            if not missing_data.empty:
                st.dataframe(missing_data.to_frame('Missing Count'))
            else:
                st.success("No missing data found!")

        with col2:
            # Duplicate analysis
            st.write("**Potential Duplicates:**")
            duplicates = invoices_df.duplicated(subset=['shop_name', 'total_amount', 'invoice_date']).sum()
            st.metric("Potential Duplicates", duplicates)

            if duplicates > 0:
                duplicate_invoices = invoices_df[invoices_df.duplicated(subset=['shop_name', 'total_amount', 'invoice_date'], keep=False)]
                st.dataframe(duplicate_invoices[['shop_name', 'total_amount', 'invoice_date']])

        with col3:
            # Data validation
            st.write("**Data Validation:**")
            negative_amounts = (invoices_df['total_amount'] < 0).sum()
            zero_amounts = (invoices_df['total_amount'] == 0).sum()
            future_dates = (pd.to_datetime(invoices_df['processed_at']) > datetime.now()).sum()

            st.write(f"Negative amounts: {negative_amounts}")
            st.write(f"Zero amounts: {zero_amounts}")
            st.write(f"Future dates: {future_dates}")

def search_and_filter_page():
    """Search and filter invoices page"""
    st.header("🔍 Search & Filter")

    # Load data
    invoices_df, items_df = get_invoice_data()

    if invoices_df.empty:
        st.info("No invoice data available.")
        return

    # Filters
    col1, col2, col3 = st.columns(3)

    with col1:
        # Shop name filter
        shop_names = ['All'] + sorted(invoices_df['shop_name'].dropna().unique().tolist())
        selected_shop = st.selectbox("Filter by Shop", shop_names)

    with col2:
        # Date range filter
        min_date = pd.to_datetime(invoices_df['processed_at']).min().date()
        max_date = pd.to_datetime(invoices_df['processed_at']).max().date()

        date_range = st.date_input(
            "Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )

    with col3:
        # Amount range filter
        min_amount = float(invoices_df['total_amount'].min())
        max_amount = float(invoices_df['total_amount'].max())

        amount_range = st.slider(
            "Amount Range (Rp)",
            min_value=min_amount,
            max_value=max_amount,
            value=(min_amount, max_amount),
            format="%.2f"
        )

    # Text search
    search_text = st.text_input("Search in shop name, address, or invoice number")

    # Apply filters
    filtered_df = invoices_df.copy()

    # Convert processed_at to datetime for filtering
    filtered_df['processed_at'] = pd.to_datetime(filtered_df['processed_at'])

    if selected_shop != 'All':
        filtered_df = filtered_df[filtered_df['shop_name'] == selected_shop]

    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = filtered_df[
            (filtered_df['processed_at'].dt.date >= start_date) &
            (filtered_df['processed_at'].dt.date <= end_date)
        ]

    filtered_df = filtered_df[
        (filtered_df['total_amount'] >= amount_range[0]) &
        (filtered_df['total_amount'] <= amount_range[1])
    ]

    if search_text:
        mask = (
            filtered_df['shop_name'].str.contains(search_text, case=False, na=False) |
            filtered_df['shop_address'].str.contains(search_text, case=False, na=False) |
            filtered_df['invoice_number'].str.contains(search_text, case=False, na=False)
        )
        filtered_df = filtered_df[mask]

    # Display results
    st.subheader(f"Results ({len(filtered_df)} invoices)")

    if not filtered_df.empty:
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Filtered Invoices", len(filtered_df))
        with col2:
            st.metric("Total Amount", f"Rp {filtered_df['total_amount'].sum():,.2f}")
        with col3:
            st.metric("Average Amount", f"Rp {filtered_df['total_amount'].mean():,.2f}")

        # Display table
        display_columns = ['shop_name', 'total_amount', 'invoice_date', 'invoice_time', 'payment_method', 'processed_at']
        st.dataframe(filtered_df[display_columns], use_container_width=True)

        # Download filtered data
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download filtered data as CSV",
            data=csv,
            file_name=f"filtered_invoices_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.info("No invoices match the current filters.")

if __name__ == "__main__":
    main()
