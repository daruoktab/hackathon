import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.ticker import FuncFormatter
import os
from matplotlib.patches import Rectangle
from io import BytesIO
import sys
from pathlib import Path
import numpy as np
from datetime import datetime
from src.analysis import (
    analyze_invoices,
    calculate_weekly_averages,
    analyze_spending_trends,
    analyze_transaction_types,
    parse_invoice_date
)

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def get_spending_pattern_plot(weeks_back: int = 8) -> BytesIO:
    """Generate spending pattern visualization."""
    # Get data
    weekly_data = calculate_weekly_averages(weeks_back=weeks_back)
    
    # Create figure
    plt.figure(figsize=(10, 6))
    weekly_totals = weekly_data['weekly_breakdown']
    
    # Convert data to plottable format
    dates = list(weekly_totals.keys())
    amounts = list(weekly_totals.values())
    
    # Plot
    plt.plot(dates, amounts, marker='o', linewidth=2)
    plt.title(f'Weekly Spending Pattern (Last {weeks_back} Weeks)')
    plt.xlabel('Week')
    plt.ylabel('Amount (Rp)')
    plt.xticks(rotation=45)
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # Format y-axis labels to show millions
    plt.gca().yaxis.set_major_formatter(
        FuncFormatter(lambda x, p: f'{int(x/1000000)}M' if x >= 1000000 else f'{int(x/1000):,}K')
    )
    
    plt.tight_layout()
    
    # Save to bytes
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
    plt.close()
    buf.seek(0)
    return buf

def get_top_vendors_plot(weeks_back: int | None = None) -> BytesIO:
    """Generate top vendors visualization."""
    # Get data
    analysis = analyze_invoices(weeks_back=weeks_back)
    vendors = analysis['top_vendors'][:5]  # Top 5 vendors
    
    # Create figure
    plt.figure(figsize=(10, 6))
    
    # Extract data
    names = [v['name'] for v in vendors]
    totals = [v['total'] for v in vendors]
    
    # Create bar plot
    bars = plt.bar(names, totals)
    title_period = f'(Last {weeks_back} Weeks)' if weeks_back else '(All Time)'
    plt.title(f'Top 5 Vendors by Spending {title_period}', pad=20)
    plt.xlabel('Vendor')
    plt.ylabel('Total Spending (Rp)')
    plt.xticks(rotation=45, ha='right')
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height/1000):,}K',
                ha='center', va='bottom')
    
    plt.tight_layout()
    
    # Save to bytes
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
    plt.close()
    buf.seek(0)
    return buf

def get_transaction_types_plot(weeks_back: int = 8) -> BytesIO:
    """Generate transaction types visualization."""
    # Get data
    analysis = analyze_transaction_types(weeks_back=weeks_back)
    by_type = analysis['by_type']
    
    # Create figure
    plt.figure(figsize=(10, 6))
    
    # Extract data - fixed the key from 'type' to 'transaction_type'
    types = [t['transaction_type'] for t in by_type]
    amounts = [t['total_amount'] for t in by_type]
    
    # Create pie chart
    plt.pie(amounts, labels=types, autopct='%1.1f%%', startangle=90)
    plt.title(f'Transaction Types Distribution (Last {weeks_back} Weeks)', pad=20)
    
    plt.axis('equal')
    plt.tight_layout()
    
    # Save to bytes
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
    plt.close()
    buf.seek(0)
    return buf

def get_daily_pattern_plot(weeks_back: int = 8) -> BytesIO:
    """Generate daily spending pattern visualization."""
    # Get data
    weekly_data = calculate_weekly_averages(weeks_back=weeks_back)
    trends = analyze_spending_trends(weeks_back=weeks_back)
    
    plt.figure(figsize=(10, 6))
    
    # Extract daily averages
    daily_avg = weekly_data['daily_average']
    days = range(7)
    daily_amounts = [daily_avg] * 7  # Simple representation
    
    # Plot
    plt.bar(days, daily_amounts)
    plt.title(f'Average Daily Spending Pattern (Last {weeks_back} Weeks)', pad=20)
    plt.xlabel('Day of Week')
    plt.ylabel('Average Amount (Rp)')
    
    # Format y-axis labels
    plt.gca().yaxis.set_major_formatter(
        FuncFormatter(lambda x, p: f'{int(x/1000):,}K')
    )
    
    # Add trend information
    trend_text = f"Trend: {trends['trend']} ({trends['trend_percentage']:+.1f}%)"
    plt.figtext(0.02, 0.02, trend_text, fontsize=8)
    
    plt.tight_layout()
    
    # Save to bytes
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
    plt.close()
    buf.seek(0)
    return buf

def create_summary_visualization(weeks_back: int | None = None) -> BytesIO:
    """Create a visualization of the invoice summary."""
    # Get data from analyze_invoices
    analysis = analyze_invoices(weeks_back=weeks_back)
    
    # Create figure with subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 12), height_ratios=[1, 2])
    title_period = f'(Last {weeks_back} Weeks)' if weeks_back else '(All Time)'
    fig.suptitle(f'Invoice Analysis Summary {title_period}', fontsize=16, y=0.95)
    
    # Plot 1: Summary metrics
    summary_data = {
        'Total Invoices': analysis['total_invoices'],
        'Avg Amount (K)': analysis['average_amount'] / 1000,
        'Total Spent (M)': analysis['total_spent'] / 1000000
    }
    
    colors = ['#2ecc71', '#3498db', '#e74c3c']
    bars = ax1.bar(summary_data.keys(), summary_data.values(), color=colors)
    ax1.set_title('Key Metrics', pad=20)
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:,.1f}',
                ha='center', va='bottom')
    
    # Plot 2: Top Vendors
    vendor_names = [v['name'] for v in analysis['top_vendors']]
    vendor_totals = [v['total'] / 1000000 for v in analysis['top_vendors']]  # Convert to millions
    
    bars = ax2.bar(vendor_names, vendor_totals, color='#9b59b6')
    ax2.set_title('Top Vendors by Spending', pad=20)
    ax2.set_xlabel('Vendor')
    ax2.set_ylabel('Total Spent (Million Rp)')
    
    # Rotate vendor names for better readability
    ax2.set_xticklabels(vendor_names, rotation=45, ha='right')
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:,.1f}M',
                ha='center', va='bottom')
    
    plt.tight_layout()
    
    # Save to bytes
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
    plt.close()
    buf.seek(0)
    return buf

def create_comprehensive_dashboard(weeks_back: int = 8) -> BytesIO:
    """Create a comprehensive dashboard with all invoice data in one intuitive image."""
    # Get all necessary data
    analysis = analyze_invoices(weeks_back=weeks_back)
    weekly_data = calculate_weekly_averages(weeks_back=weeks_back)
    trends = analyze_spending_trends(weeks_back=weeks_back)
    transaction_types = analyze_transaction_types(weeks_back=weeks_back)
    
    # Get recent invoices for the transactions table
    from src.database import get_db_session, Invoice
    # Get the 5 most recent invoices from the database (not filtered by time)
    session = get_db_session()
    recent_invoices_query = session.query(Invoice).order_by(Invoice.processed_at.desc()).limit(5).all()
    recent_invoices = []
    for inv in recent_invoices_query:
        recent_invoices.append({
            'shop_name': inv.shop_name,
            'invoice_date': inv.invoice_date,
            'total_amount': inv.total_amount
        })
    session.close()
    
    # Set up the figure with a clean style
    plt.style.use('default')
    
    # Add a font that supports emojis
    font_path = 'C:/Windows/Fonts/seguiemj.ttf'  # Path to Segoe UI Emoji font
    if os.path.exists(font_path):
        fm.fontManager.addfont(font_path)
        plt.rcParams['font.family'] = 'Segoe UI Emoji'
    
    fig = plt.figure(figsize=(16, 10), facecolor='#EAF2F8')
    
    # Create main title
    title_period = f'(Last {weeks_back} Weeks)' if weeks_back else '(All Time)'
    fig.suptitle(f'📊 Analysis Summary {title_period}', fontsize=22, fontweight='bold', y=0.98, color='#17202A')
    
    # Create grid for better layout control
    gs = fig.add_gridspec(3, 3, height_ratios=[0.8, 1.2, 1], width_ratios=[1.5, 1.5, 1],
                         hspace=0.4, wspace=0.3, left=0.06, right=0.94, top=0.92, bottom=0.08)
    
    # ============== 1. KEY METRICS CARDS (Top row) ==============
    # Create 3 metric cards
    metrics_data = [
        ('Total Spent', f'Rp {analysis["total_spent"]/1000000:.1f}M', '#E74C3C'),
        ('Invoices', f'{analysis["total_invoices"]}', '#3498DB'),
        ('Avg Amount', f'Rp {analysis["average_amount"]/1000:.0f}K', '#2ECC71')
    ]
    
    for i, (title, value, color) in enumerate(metrics_data):
        ax = fig.add_subplot(gs[0, i])
        ax.axis('off')
        
        # Create card-like appearance
        rect = Rectangle((0.1, 0.2), 0.8, 0.6, transform=ax.transAxes,
                            facecolor=color, alpha=0.1, edgecolor=color, linewidth=2)
        ax.add_patch(rect)
        
        # Add text
        ax.text(0.5, 0.65, title, transform=ax.transAxes, ha='center', fontsize=12,
               fontweight='bold', color='#2C3E50')
        ax.text(0.5, 0.35, value, transform=ax.transAxes, ha='center', fontsize=18,
               fontweight='bold', color=color)
    
    # ============== 2. WEEKLY SPENDING TREND (Middle left) ==============
    ax_trend = fig.add_subplot(gs[1, :2])
    weekly_totals = weekly_data['weekly_breakdown']
    
    if weekly_totals:
        sorted_weeks = sorted(weekly_totals.items())[-weeks_back:]
        dates = [item[0] for item in sorted_weeks]
        amounts = [item[1]['total'] for item in sorted_weeks]
        ranges = [item[1]['range'] for item in sorted_weeks]
        
        # Create LINE chart with markers (as requested)
        ax_trend.plot(range(len(dates)), amounts, marker='o', linewidth=2.5,
                     markersize=8, color='#8E44AD', markerfacecolor='#9B59B6',
                     markeredgewidth=2, markeredgecolor='white')
        
        # Add grid for better readability
        ax_trend.grid(True, alpha=0.3, linestyle='--')
        
        # Fill area under the line
        ax_trend.fill_between(range(len(dates)), amounts, alpha=0.1, color='#8E44AD')
        
        ax_trend.set_title('Weekly Spending Trend', fontsize=14, fontweight='bold', pad=15, color='#2C3E50')
        ax_trend.set_xlabel('Week', fontsize=11, color='#2C3E50')
        ax_trend.set_ylabel('Amount (Rp)', fontsize=11, color='#2C3E50')
        ax_trend.set_xticks(range(len(dates)))
        ax_trend.set_xticklabels([f'W{i+1}\n({ranges[i]})' for i in range(len(dates))], fontsize=8)
        
        # Format y-axis
        ax_trend.yaxis.set_major_formatter(
            FuncFormatter(lambda x, p: f'{int(x/1000000)}M' if x >= 1000000 else f'{int(x/1000)}K')
        )
        
        # Add trend badge
        trend_color = '#E74C3C' if trends['trend'] == 'increasing' else '#2ECC71' if trends['trend'] == 'decreasing' else '#F1C40F'
        trend_text = f"📊 {trends['trend'].upper()}\n{trends['trend_percentage']:+.1f}%"
        ax_trend.text(0.02, 0.98, trend_text, transform=ax_trend.transAxes,
                     fontsize=10, bbox=dict(boxstyle='round,pad=0.5',
                     facecolor=trend_color, alpha=0.9, edgecolor='white', linewidth=2),
                     verticalalignment='top', color='white', fontweight='bold')
    
    # ============== 3. TOP VENDORS (Middle right) ==============
    ax_vendors = fig.add_subplot(gs[1, 2])
    vendors = analysis['top_vendors'][:5]  # Top 5 vendors
    
    if vendors:
        vendor_names = [v['name'][:12] + '..' if len(v['name']) > 12 else v['name'] for v in vendors]
        vendor_totals = [v['total']/1000000 for v in vendors]  # Convert to millions
        
        # Create horizontal bar chart with gradient colors
        colors = plt.cm.get_cmap('cool')(np.linspace(0.3, 0.8, len(vendor_names)))
        bars = ax_vendors.barh(vendor_names, vendor_totals, color=colors, height=0.6)
        
        # Add value labels
        for bar, vendor in zip(bars, vendors):
            width = bar.get_width()
            ax_vendors.text(width + 0.05, bar.get_y() + bar.get_height()/2,
                          f'{width:.1f}M', ha='left', va='center', fontsize=8,
                          fontweight='bold')
        
        ax_vendors.set_title('Top Vendors', fontsize=14, fontweight='bold', pad=15, color='#2C3E50')
        ax_vendors.set_xlabel('Spending (Million Rp)', fontsize=11, color='#2C3E50')
        ax_vendors.grid(True, axis='x', alpha=0.3, linestyle='--')
    
    # ============== 4. CATEGORY DISTRIBUTION - DONUT CHART (Bottom left) ==============
    ax_donut = fig.add_subplot(gs[2, 0])
    by_type = transaction_types['by_type']
    
    if by_type:
        # Prepare data for donut chart
        types = [t['transaction_type'].title() for t in by_type[:4]]
        amounts = [t['total_amount'] for t in by_type[:4]]
        
        # Add "Others" if needed
        if len(by_type) > 4:
            others_amount = sum(t['total_amount'] for t in by_type[4:])
            types.append('Others')
            amounts.append(others_amount)
        
        # Create donut chart
        colors_pie = ['#3498DB', '#E74C3C', '#2ECC71', '#F1C40F', '#9B59B6'][:len(types)]
        pie_result = ax_donut.pie(amounts, labels=types, autopct='%1.0f%%',
                                  startangle=90, colors=colors_pie,
                                  pctdistance=0.85)
        
        # Handle pie chart return values
        if len(pie_result) == 3:
            wedges, texts, autotexts = pie_result
            # Style the text
            for text in texts:
                text.set_color('#2C3E50')
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(9)
        
        ax_donut.set_title('Category Distribution', fontsize=14, fontweight='bold', pad=15, color='#17202A')
    
    # ============== 5. RECENT TRANSACTIONS TABLE (Bottom right) ==============
    ax_table = fig.add_subplot(gs[2, 1:])
    ax_table.axis('off')
    
    # Prepare table data
    table_data = []
    headers = ['Date', 'Vendor', 'Amount']
    
    if recent_invoices:
        for inv in recent_invoices[:5]:
            date_to_use = parse_invoice_date(inv['invoice_date'])
            date_str = date_to_use.strftime('%d/%m') if date_to_use else 'N/A'
            vendor = (inv['shop_name'][:15] + '..') if inv['shop_name'] and len(inv['shop_name']) > 15 else (inv['shop_name'] or 'Unknown')
            amount = f'Rp {inv["total_amount"]/1000:.0f}K'
            table_data.append([date_str, vendor, amount])
    else:
        table_data = [['No data', 'No data', 'No data']]
    
    # Create the table
    table = ax_table.table(cellText=table_data, colLabels=headers,
                           cellLoc='center', loc='center',
                           colWidths=[0.2, 0.5, 0.3])
    
    # Style the table
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.8)
    
    # Style header row
    for i in range(len(headers)):
        table[(0, i)].set_facecolor('#8E44AD')
        table[(0, i)].set_text_props(weight='bold', color='white')
        table[(0, i)].set_height(0.15)
    
    # Style data rows with alternating colors
    for i in range(1, len(table_data) + 1):
        for j in range(len(headers)):
            if i % 2 == 0:
                table[(i, j)].set_facecolor('#F5F5F5')
            table[(i, j)].set_height(0.12)
    
    ax_table.set_title('Recent Transactions', fontsize=14, fontweight='bold', pad=15, color='#2C3E50')
    
    # ============== 6. INSIGHTS FOOTER ==============
    insights_text = "💡 Key Insights: "
    if trends['trend'] == 'increasing':
        insights_text += f"Spending ↑ {trends['trend_percentage']:.0f}% "
    elif trends['trend'] == 'decreasing':
        insights_text += f"Spending ↓ {abs(trends['trend_percentage']):.0f}% "
    else:
        insights_text += "Spending stable "
    
    insights_text += f"| Weekly avg: Rp {weekly_data['weekly_average']/1000000:.1f}M "
    insights_text += f"| Daily avg: Rp {weekly_data['daily_average']/1000:.0f}K"
    
    if vendors:
        insights_text += f" | Top vendor: {vendors[0]['name']}"
    
    fig.text(0.5, 0.02, insights_text, ha='center', fontsize=10,
            bbox=dict(boxstyle='round,pad=0.5', facecolor='#FFFACD', alpha=0.8, edgecolor='#FFD700', linewidth=1))
    
    # Add timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    fig.text(0.98, 0.01, f"Generated: {timestamp}", ha='right', fontsize=9, alpha=0.6)
    
    # Save to bytes
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close()
    buf.seek(0)
    return buf

# Update the get_visualization function to use the new dashboard
def get_visualization(keyword: str | None = None, weeks_back: int = 8) -> BytesIO:
    """Get the visualization based on keyword."""
    if keyword == "dashboard" or keyword is None:
        return create_comprehensive_dashboard(weeks_back=weeks_back)
    elif keyword == "summary":
        return create_summary_visualization(weeks_back=weeks_back)
    elif keyword == "spending":
        return get_spending_pattern_plot(weeks_back=weeks_back)
    elif keyword == "vendors":
        return get_top_vendors_plot(weeks_back=weeks_back)
    elif keyword == "types":
        return get_transaction_types_plot(weeks_back=weeks_back)
    elif keyword == "daily":
        return get_daily_pattern_plot(weeks_back=weeks_back)
    else:
        # Default to comprehensive dashboard
        return create_comprehensive_dashboard(weeks_back=weeks_back)

def get_available_visualizations() -> list:
    """Return list of available visualization keywords."""
    return ["dashboard", "summary", "spending", "vendors", "types", "daily"]
