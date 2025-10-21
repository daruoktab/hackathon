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
from typing import Optional
from src.analysis import (
    analyze_invoices,
    calculate_weekly_averages,
    calculate_daily_totals,
    analyze_spending_trends,
    analyze_daily_trends,
    analyze_transaction_types,
    parse_invoice_date,
    determine_time_granularity
)
from telegram_bot.spending_limits import check_spending_limit

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def format_rp(value, pos=None) -> str:
    """
    Format Rupiah values with K/M suffixes for better readability.
    
    Args:
        value: Numeric value to format
        pos: Position parameter (required by FuncFormatter, can be None)
    
    Returns:
        Formatted string with Rp prefix and K/M suffix
    """
    if value is None or value == 0:
        return 'Rp 0'
    
    if value >= 1_000_000:
        return f'Rp {value/1_000_000:.1f}M'
    elif value >= 1_000:
        return f'Rp {value/1_000:.0f}K'
    else:
        return f'Rp {value:,.0f}'

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

def create_comprehensive_dashboard(weeks_back: int = 8, user_id: Optional[int] = None) -> BytesIO:
    """Create a comprehensive dashboard with all invoice data in one intuitive image."""
    # Define color constants for consistent theming
    COLOR_BG = '#EAF2F8'
    COLOR_TITLE = '#17202A'
    COLOR_SUBTITLE = '#2C3E50'
    COLOR_SPEND = '#E74C3C'
    COLOR_INVOICES = '#3498DB'
    COLOR_AVG = '#2ECC71'
    COLOR_BUDGET_OK = '#2ECC71'
    COLOR_BUDGET_WARN = '#F39C12'
    COLOR_BUDGET_OVER = '#E74C3C'
    COLOR_BUDGET_NONE = '#95A5A6'
    COLOR_TREND = '#8E44AD'
    COLOR_TREND_UP = '#E74C3C'
    COLOR_TREND_DOWN = '#2ECC71'
    COLOR_TREND_STABLE = '#F1C40F'
    
    # Fetch budget status if user_id is provided
    budget_status = None
    if user_id is not None:
        budget_status = check_spending_limit(user_id)
    
    # Get all necessary data
    analysis = analyze_invoices(weeks_back=weeks_back)
    
    # Determine time granularity adaptively
    granularity_info = determine_time_granularity(weeks_back=weeks_back)
    
    # Get data based on granularity
    if granularity_info['granularity'] == 'daily':
        time_data = calculate_daily_totals(weeks_back=weeks_back)
        trends = analyze_daily_trends(weeks_back=weeks_back)
    else:
        time_data = calculate_weekly_averages(weeks_back=weeks_back)
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
    
    fig = plt.figure(figsize=(16, 10), facecolor=COLOR_BG)
    
    # Create main title
    title_period = f'(Last {weeks_back} Weeks)' if weeks_back else '(All Time)'
    fig.suptitle(f'📊 Analysis Summary {title_period}', fontsize=22, fontweight='bold', y=0.98, color=COLOR_TITLE)
    
    # Create grid for better layout control - 4 columns for 4 KPI cards
    gs = fig.add_gridspec(3, 4, height_ratios=[0.8, 1.2, 1], width_ratios=[1, 1, 1, 1],
                         hspace=0.4, wspace=0.25, left=0.05, right=0.95, top=0.92, bottom=0.08)
    
    # ============== 1. KEY METRICS CARDS (Top row) ==============
    # Create 4 metric cards (including budget)
    metrics_data = [
        ('Total Spent', format_rp(analysis["total_spent"]), COLOR_SPEND),
        ('Invoices', f'{analysis["total_invoices"]}', COLOR_INVOICES),
        ('Avg Amount', format_rp(analysis["average_amount"]), COLOR_AVG)
    ]
    
    # Create first 3 KPI cards
    for i, (title, value, color) in enumerate(metrics_data):
        ax = fig.add_subplot(gs[0, i])
        ax.axis('off')
        
        # Create card-like appearance
        rect = Rectangle((0.1, 0.2), 0.8, 0.6, transform=ax.transAxes,
                            facecolor=color, alpha=0.1, edgecolor=color, linewidth=2)
        ax.add_patch(rect)
        
        # Add text
        ax.text(0.5, 0.65, title, transform=ax.transAxes, ha='center', fontsize=12,
               fontweight='bold', color=COLOR_SUBTITLE)
        ax.text(0.5, 0.35, value, transform=ax.transAxes, ha='center', fontsize=18,
               fontweight='bold', color=color)
    
    # ============== Budget Status Card (4th KPI) ==============
    ax_budget = fig.add_subplot(gs[0, 3])
    ax_budget.axis('off')
    
    if budget_status and budget_status['has_limit']:
        percentage = budget_status['percentage_used']
        
        # Determine color based on usage percentage
        if percentage >= 100:
            budget_color = COLOR_BUDGET_OVER
        elif percentage >= 80:
            budget_color = COLOR_BUDGET_WARN
        else:
            budget_color = COLOR_BUDGET_OK
        
        budget_value = f"{percentage:.0f}% Used"
    else:
        budget_color = COLOR_BUDGET_NONE
        budget_value = "Not Set"
    
    # Create budget card
    rect_budget = Rectangle((0.1, 0.2), 0.8, 0.6, transform=ax_budget.transAxes,
                             facecolor=budget_color, alpha=0.1, edgecolor=budget_color, linewidth=2)
    ax_budget.add_patch(rect_budget)
    
    ax_budget.text(0.5, 0.65, 'Budget Status', transform=ax_budget.transAxes, ha='center',
                   fontsize=12, fontweight='bold', color=COLOR_SUBTITLE)
    ax_budget.text(0.5, 0.35, budget_value, transform=ax_budget.transAxes, ha='center',
                   fontsize=18, fontweight='bold', color=budget_color)
    
    # ============== 2. WEEKLY SPENDING TREND (Middle left) ==============
    ax_trend = fig.add_subplot(gs[1, :3])
    
    # Adaptive rendering based on granularity
    if granularity_info['granularity'] == 'daily':
        # Daily granularity
        daily_breakdown = time_data['daily_breakdown']
        
        if daily_breakdown and granularity_info['sufficient_for_trend']:
            sorted_days = sorted(daily_breakdown.items())
            dates = [item[0] for item in sorted_days]
            amounts = [item[1]['total'] for item in sorted_days]
            labels = [item[1]['label'] for item in sorted_days]
            
            # Create LINE chart with markers
            ax_trend.plot(range(len(dates)), amounts, marker='o', linewidth=2.5,
                         markersize=8, color=COLOR_TREND, markerfacecolor='#9B59B6',
                         markeredgewidth=2, markeredgecolor='white')
            
            # Add grid for better readability
            ax_trend.grid(True, alpha=0.3, linestyle='--')
            
            # Fill area under the line
            ax_trend.fill_between(range(len(dates)), amounts, alpha=0.1, color=COLOR_TREND)
            
            ax_trend.set_title('Daily Spending Trend', fontsize=14, fontweight='bold', pad=15, color=COLOR_SUBTITLE)
            ax_trend.set_xlabel('Date', fontsize=11, color=COLOR_SUBTITLE)
            ax_trend.set_ylabel('Amount (Rp)', fontsize=11, color=COLOR_SUBTITLE)
            ax_trend.set_xticks(range(len(dates)))
            ax_trend.set_xticklabels(labels, fontsize=8, rotation=45)
            
            # Format y-axis using format_rp
            ax_trend.yaxis.set_major_formatter(FuncFormatter(format_rp))
            
            # Add trend badge if we have valid trend data
            if trends['trend'] != 'insufficient_data':
                if trends['trend'] == 'increasing':
                    trend_color = COLOR_TREND_UP
                elif trends['trend'] == 'decreasing':
                    trend_color = COLOR_TREND_DOWN
                else:
                    trend_color = COLOR_TREND_STABLE
                
                trend_text = f"📊 {trends['trend'].upper()}\n{trends['trend_percentage']:+.1f}%"
                ax_trend.text(0.02, 0.98, trend_text, transform=ax_trend.transAxes,
                             fontsize=10, bbox=dict(boxstyle='round,pad=0.5',
                             facecolor=trend_color, alpha=0.9, edgecolor='white', linewidth=2),
                             verticalalignment='top', color='white', fontweight='bold')
        else:
            # Insufficient data for daily trend
            ax_trend.text(0.5, 0.5, '📊 More data needed for trend analysis\n\n' +
                         'Upload more invoices to see spending trends over time',
                         transform=ax_trend.transAxes, ha='center', va='center',
                         fontsize=14, color=COLOR_SUBTITLE, style='italic',
                         bbox=dict(boxstyle='round,pad=1', facecolor='white', alpha=0.8))
            ax_trend.set_title('Daily Spending Trend', fontsize=14, fontweight='bold', pad=15, color=COLOR_SUBTITLE)
            ax_trend.set_xticks([])
            ax_trend.set_yticks([])
            for spine in ax_trend.spines.values():
                spine.set_visible(False)
    else:
        # Weekly granularity
        weekly_breakdown = time_data['weekly_breakdown']
        
        if weekly_breakdown and granularity_info['sufficient_for_trend']:
            sorted_weeks = sorted(weekly_breakdown.items())[-weeks_back:]
            dates = [item[0] for item in sorted_weeks]
            amounts = [item[1]['total'] for item in sorted_weeks]
            ranges = [item[1]['range'] for item in sorted_weeks]
            
            # Create LINE chart with markers
            ax_trend.plot(range(len(dates)), amounts, marker='o', linewidth=2.5,
                         markersize=8, color=COLOR_TREND, markerfacecolor='#9B59B6',
                         markeredgewidth=2, markeredgecolor='white')
            
            # Add grid for better readability
            ax_trend.grid(True, alpha=0.3, linestyle='--')
            
            # Fill area under the line
            ax_trend.fill_between(range(len(dates)), amounts, alpha=0.1, color=COLOR_TREND)
            
            ax_trend.set_title('Weekly Spending Trend', fontsize=14, fontweight='bold', pad=15, color=COLOR_SUBTITLE)
            ax_trend.set_xlabel('Week', fontsize=11, color=COLOR_SUBTITLE)
            ax_trend.set_ylabel('Amount (Rp)', fontsize=11, color=COLOR_SUBTITLE)
            ax_trend.set_xticks(range(len(dates)))
            ax_trend.set_xticklabels([f'W{i+1}\n({ranges[i]})' for i in range(len(dates))], fontsize=8)
            
            # Format y-axis using format_rp
            ax_trend.yaxis.set_major_formatter(FuncFormatter(format_rp))
            
            # Add trend badge if we have valid trend data
            if trends['trend'] != 'insufficient_data':
                if trends['trend'] == 'increasing':
                    trend_color = COLOR_TREND_UP
                elif trends['trend'] == 'decreasing':
                    trend_color = COLOR_TREND_DOWN
                else:
                    trend_color = COLOR_TREND_STABLE
                
                trend_text = f"📊 {trends['trend'].upper()}\n{trends['trend_percentage']:+.1f}%"
                ax_trend.text(0.02, 0.98, trend_text, transform=ax_trend.transAxes,
                             fontsize=10, bbox=dict(boxstyle='round,pad=0.5',
                             facecolor=trend_color, alpha=0.9, edgecolor='white', linewidth=2),
                             verticalalignment='top', color='white', fontweight='bold')
        else:
            # Insufficient data for weekly trend
            ax_trend.text(0.5, 0.5, '📊 More data needed for trend analysis\n\n' +
                         'Upload more invoices to see spending trends over time',
                         transform=ax_trend.transAxes, ha='center', va='center',
                         fontsize=14, color=COLOR_SUBTITLE, style='italic',
                         bbox=dict(boxstyle='round,pad=1', facecolor='white', alpha=0.8))
            ax_trend.set_title('Weekly Spending Trend', fontsize=14, fontweight='bold', pad=15, color=COLOR_SUBTITLE)
            ax_trend.set_xticks([])
            ax_trend.set_yticks([])
            for spine in ax_trend.spines.values():
                spine.set_visible(False)
    
    # ============== 3. TOP VENDORS (Middle right) ==============
    ax_vendors = fig.add_subplot(gs[1, 3])
    vendors = analysis['top_vendors'][:5]  # Top 5 vendors
    
    if vendors:
        vendor_names = [v['name'][:12] + '..' if len(v['name']) > 12 else v['name'] for v in vendors]
        vendor_totals = [v['total'] for v in vendors]  # Keep actual values
        
        # Create horizontal bar chart with gradient colors
        colors = plt.cm.get_cmap('cool')(np.linspace(0.3, 0.8, len(vendor_names)))
        bars = ax_vendors.barh(vendor_names, vendor_totals, color=colors, height=0.6)
        
        # Add value labels using format_rp
        for bar, vendor in zip(bars, vendors):
            width = bar.get_width()
            ax_vendors.text(width * 1.02, bar.get_y() + bar.get_height()/2,
                          format_rp(vendor['total']), ha='left', va='center', fontsize=8,
                          fontweight='bold')
        
        ax_vendors.set_title('Top Vendors', fontsize=14, fontweight='bold', pad=15, color=COLOR_SUBTITLE)
        ax_vendors.set_xlabel('Total Spending', fontsize=11, color=COLOR_SUBTITLE)
        ax_vendors.grid(True, axis='x', alpha=0.3, linestyle='--')
        
        # Format x-axis using format_rp
        ax_vendors.xaxis.set_major_formatter(FuncFormatter(format_rp))
    
    # ============== 4. CATEGORY DISTRIBUTION - DONUT CHART (Bottom left) ==============
    ax_donut = fig.add_subplot(gs[2, :2])
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
        
        # Create donut chart with defined colors
        colors_pie = [COLOR_INVOICES, COLOR_SPEND, COLOR_AVG, COLOR_TREND_STABLE, '#9B59B6'][:len(types)]
        pie_result = ax_donut.pie(amounts, labels=types, autopct='%1.0f%%',
                                  startangle=90, colors=colors_pie,
                                  pctdistance=0.85)
        
        # Handle pie chart return values
        if len(pie_result) == 3:
            wedges, texts, autotexts = pie_result
            # Style the text
            for text in texts:
                text.set_color(COLOR_SUBTITLE)
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(9)
        
        ax_donut.set_title('Category Distribution', fontsize=14, fontweight='bold', pad=15, color=COLOR_SUBTITLE)
    
    # ============== 5. RECENT TRANSACTIONS TABLE (Bottom right) ==============
    ax_table = fig.add_subplot(gs[2, 2:])
    ax_table.axis('off')
    
    # Prepare table data
    table_data = []
    headers = ['Date', 'Vendor', 'Amount']
    
    if recent_invoices:
        for inv in recent_invoices[:5]:
            date_to_use = parse_invoice_date(inv['invoice_date'])
            date_str = date_to_use.strftime('%d/%m') if date_to_use else 'N/A'
            vendor = (inv['shop_name'][:15] + '..') if inv['shop_name'] and len(inv['shop_name']) > 15 else (inv['shop_name'] or 'Unknown')
            # Use format_rp for amount
            amount = format_rp(inv["total_amount"])
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
        table[(0, i)].set_facecolor(COLOR_TREND)
        table[(0, i)].set_text_props(weight='bold', color='white')
        table[(0, i)].set_height(0.15)
    
    # Style data rows with alternating colors
    for i in range(1, len(table_data) + 1):
        for j in range(len(headers)):
            if i % 2 == 0:
                table[(i, j)].set_facecolor('#F5F5F5')
            table[(i, j)].set_height(0.12)
    
    ax_table.set_title('Recent Transactions', fontsize=14, fontweight='bold', pad=15, color=COLOR_SUBTITLE)
    
    # ============== 6. INSIGHTS FOOTER ==============
    insights_text = "💡 Insights: "
    
    # Add trend information
    if trends['trend'] == 'insufficient_data':
        insights_text += "Not enough data for trend analysis"
    elif trends['trend'] == 'increasing':
        insights_text += f"Spending ↑ {trends['trend_percentage']:.0f}%"
    elif trends['trend'] == 'decreasing':
        insights_text += f"Spending ↓ {abs(trends['trend_percentage']):.0f}%"
    else:
        insights_text += "Spending stable"
    
    # Add averages using format_rp - adapt based on granularity
    if granularity_info['granularity'] == 'daily':
        insights_text += f" | Daily avg: {format_rp(time_data['daily_average'])}"
    else:
        insights_text += f" | Weekly avg: {format_rp(time_data['weekly_average'])}"
        insights_text += f" | Daily avg: {format_rp(time_data['daily_average'])}"
    
    # Add budget status
    if budget_status and budget_status['has_limit']:
        percentage = budget_status['percentage_used']
        insights_text += f" | Budget: {percentage:.0f}% used"
    else:
        insights_text += " | No budget set"
    
    # Add top vendor
    if vendors:
        insights_text += f" | Top: {vendors[0]['name']}"
    
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
def get_visualization(keyword: Optional[str] = None, weeks_back: int = 8, user_id: Optional[int] = None) -> BytesIO:
    """Get the visualization based on keyword."""
    if keyword == "dashboard" or keyword is None:
        return create_comprehensive_dashboard(weeks_back=weeks_back, user_id=user_id)
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
        return create_comprehensive_dashboard(weeks_back=weeks_back, user_id=user_id)

def get_available_visualizations() -> list:
    """Return list of available visualization keywords."""
    return ["dashboard", "summary", "spending", "vendors", "types", "daily"]
