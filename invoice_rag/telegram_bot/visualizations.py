import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from io import BytesIO
import sys
from pathlib import Path
from src.analysis import (
    analyze_invoices,
    calculate_weekly_averages,
    analyze_spending_trends,
    analyze_transaction_types
)

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def get_spending_pattern_plot() -> BytesIO:
    """Generate spending pattern visualization."""
    # Get data
    weekly_data = calculate_weekly_averages(weeks_back=8)
    
    # Create figure
    plt.figure(figsize=(10, 6))
    weekly_totals = weekly_data['weekly_breakdown']
    
    # Convert data to plottable format
    dates = list(weekly_totals.keys())
    amounts = list(weekly_totals.values())
    
    # Plot
    plt.plot(dates, amounts, marker='o', linewidth=2)
    plt.title('Weekly Spending Pattern', pad=20)
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

def get_top_vendors_plot() -> BytesIO:
    """Generate top vendors visualization."""
    # Get data
    analysis = analyze_invoices()
    vendors = analysis['top_vendors'][:5]  # Top 5 vendors
    
    # Create figure
    plt.figure(figsize=(10, 6))
    
    # Extract data
    names = [v['name'] for v in vendors]
    totals = [v['total'] for v in vendors]
    
    # Create bar plot
    bars = plt.bar(names, totals)
    plt.title('Top 5 Vendors by Spending', pad=20)
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

def get_transaction_types_plot() -> BytesIO:
    """Generate transaction types visualization."""
    # Get data
    analysis = analyze_transaction_types(weeks_back=8)
    by_type = analysis['by_type']
    
    # Create figure
    plt.figure(figsize=(10, 6))
    
    # Extract data
    types = [t['type'] for t in by_type]
    amounts = [t['total_amount'] for t in by_type]
    
    # Create pie chart
    plt.pie(amounts, labels=types, autopct='%1.1f%%', startangle=90)
    plt.title('Transaction Types Distribution', pad=20)
    
    plt.axis('equal')
    plt.tight_layout()
    
    # Save to bytes
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
    plt.close()
    buf.seek(0)
    return buf

def get_daily_pattern_plot() -> BytesIO:
    """Generate daily spending pattern visualization."""
    # Get data
    weekly_data = calculate_weekly_averages(weeks_back=8)
    trends = analyze_spending_trends(weeks_back=8)
    
    plt.figure(figsize=(10, 6))
    
    # Extract daily averages
    daily_avg = weekly_data['daily_average']
    days = range(7)
    daily_amounts = [daily_avg] * 7  # Simple representation
    
    # Plot
    plt.bar(days, daily_amounts)
    plt.title('Average Daily Spending Pattern', pad=20)
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

def create_summary_visualization() -> BytesIO:
    """Create a visualization of the invoice summary."""
    # Get data from analyze_invoices
    analysis = analyze_invoices()
    
    # Create figure with subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 12), height_ratios=[1, 2])
    fig.suptitle('Invoice Analysis Summary', fontsize=16, y=0.95)
    
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

# Since we only have one visualization now, we don't need a map
def get_visualization(keyword: str | None = None) -> BytesIO:
    """Get the summary visualization."""
    return create_summary_visualization()

def get_available_visualizations() -> list:
    """Return list of available visualization keywords."""
    return ["summary"]  # We only have one visualization now