import sqlite3
import os
from datetime import datetime, timedelta

# Database path - same as used in other modules
def get_db_path():
    """Get the database path"""
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(current_dir, 'invoices.db')

def get_db_connection():
    """Get database connection - supports both SQLite and Supabase"""
    try:
        from src.db_config import get_raw_connection
        return get_raw_connection()
    except ImportError:
        # Fallback to SQLite
        return sqlite3.connect(get_db_path())

def get_placeholder():
    """Get SQL parameter placeholder for current database"""
    try:
        from src.db_config import USE_SUPABASE
        return "%s" if USE_SUPABASE else "?"
    except ImportError:
        return "?"

def analyze_invoices(weeks_back: int | None = None):
    """Analyze invoices and return summary statistics for a given period."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        params = []
        where_clause = ""
        placeholder = get_placeholder()
        
        if weeks_back is not None and weeks_back > 0:
            end_date = datetime.now()
            start_date = end_date - timedelta(weeks=weeks_back)
            where_clause = f"WHERE invoice_date >= {placeholder}"
            params.append(start_date.strftime('%Y-%m-%d'))

        # Get basic stats
        query = f"""
            SELECT 
                COUNT(*) as total_invoices,
                SUM(total_amount) as total_spent,
                AVG(total_amount) as average_amount
            FROM invoices
            {where_clause}
        """
        cursor.execute(query, params)
        
        result = cursor.fetchone()
        if not result or result[0] == 0:
            return {
                'total_invoices': 0,
                'total_spent': 0.0,
                'average_amount': 0.0,
                'top_vendors': []
            }
        
        total_invoices, total_spent, average_amount = result
        
        # Calculate top vendors (shops)
        vendor_where_clause = "WHERE shop_name IS NOT NULL"
        if where_clause:
            vendor_where_clause = f"{where_clause} AND shop_name IS NOT NULL"

        query = f"""
            SELECT 
                shop_name,
                SUM(total_amount) as total,
                COUNT(*) as transaction_count
            FROM invoices 
            {vendor_where_clause}
            GROUP BY shop_name 
            ORDER BY total DESC
            LIMIT 10
        """
        cursor.execute(query, params)
        
        top_vendors = []
        for row in cursor.fetchall():
            top_vendors.append({
                'name': row[0],
                'total': row[1],
                'transaction_count': row[2]
            })
        
        return {
            'total_invoices': total_invoices or 0,
            'total_spent': total_spent or 0.0,
            'average_amount': average_amount or 0.0,
            'top_vendors': top_vendors
        }
    
    finally:
        conn.close()

def parse_invoice_date(date_str):
    """Parse various date formats from Indonesian invoices."""
    if not date_str:
        return None
    
    # Common date formats
    formats = [
        "%d/%m/%Y",
        "%d-%m-%Y", 
        "%d.%m.%Y",
        "%Y-%m-%d",
        "%d/%m/%y",
        "%d-%m-%y"
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    return None

def get_weekly_data(weeks_back=4):
    """Get invoice data for the last N weeks."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        placeholder = get_placeholder()
        
        end_date = datetime.now()
        start_date = end_date - timedelta(weeks=weeks_back)
        
        # Get invoices from the last N weeks
        cursor.execute(f"""
            SELECT id, shop_name, invoice_date, total_amount, transaction_type, processed_at, image_path
            FROM invoices
            WHERE invoice_date >= {placeholder}
            ORDER BY invoice_date DESC
        """, (start_date.strftime('%Y-%m-%d'),))
        
        weekly_invoices = []
        for row in cursor.fetchall():
            weekly_invoices.append({
                'id': row[0],
                'shop_name': row[1],
                'invoice_date': row[2],
                'total_amount': row[3],
                'transaction_type': row[4],
                'processed_at': datetime.fromisoformat(row[5]) if row[5] else None,
                'image_path': row[6]
            })
        
        return weekly_invoices
    
    finally:
        conn.close()

def calculate_daily_totals(weeks_back=4):
    """Calculate daily spending totals."""
    invoices = get_weekly_data(weeks_back)
    
    if not invoices:
        return {
            'total_days': weeks_back * 7,
            'daily_average': 0,
            'total_spent': 0,
            'transaction_count': 0,
            'daily_breakdown': {}
        }
    
    # Group by day
    daily_totals = {}
    
    for invoice in invoices:
        date_to_use = parse_invoice_date(invoice['invoice_date'])
        if date_to_use:
            day_key = date_to_use.strftime("%Y-%m-%d")
            
            if day_key not in daily_totals:
                daily_totals[day_key] = {
                    'total': 0,
                    'count': 0,
                    'date': date_to_use,
                    'label': date_to_use.strftime('%d/%m')
                }
                
            daily_totals[day_key]['total'] += invoice['total_amount']
            daily_totals[day_key]['count'] += 1
    
    total_spent = sum(invoice['total_amount'] for invoice in invoices)
    transaction_count = len(invoices)
    
    days_with_data = len(daily_totals)
    daily_average = total_spent / max(days_with_data, 1) if days_with_data > 0 else 0
    
    return {
        'total_days': weeks_back * 7,
        'days_with_data': days_with_data,
        'daily_average': daily_average,
        'total_spent': total_spent,
        'transaction_count': transaction_count,
        'daily_breakdown': daily_totals
    }

def calculate_weekly_averages(weeks_back=4):
    """Calculate weekly spending averages."""
    invoices = get_weekly_data(weeks_back)
    
    if not invoices:
        return {
            'total_weeks': weeks_back,
            'weekly_average': 0,
            'daily_average': 0,
            'total_spent': 0,
            'transaction_count': 0,
            'weekly_breakdown': {},
            'weekly_transaction_counts': {}
        }
    
    # Group by week
    weekly_totals = {}
    weekly_counts = {}
    
    for invoice in invoices:
        date_to_use = parse_invoice_date(invoice['invoice_date'])
        if date_to_use:
            # Use invoice_date for week calculation
            week_start = date_to_use - timedelta(days=date_to_use.weekday())
            week_end = week_start + timedelta(days=6)
            week_key = week_start.strftime("%Y-%W")
            
            if week_key not in weekly_totals:
                weekly_totals[week_key] = {
                    'total': 0,
                    'count': 0,
                    'range': f"{week_start.strftime('%d/%m')}-{week_end.strftime('%d/%m')}"
                }
                
            weekly_totals[week_key]['total'] += invoice['total_amount']
            weekly_totals[week_key]['count'] += 1
    
    total_spent = sum(invoice['total_amount'] for invoice in invoices)
    transaction_count = len(invoices)
    
    weeks_with_data = len(weekly_totals)
    weekly_average = total_spent / max(weeks_with_data, 1)
    daily_average = total_spent / (weeks_back * 7)
    
    return {
        'total_weeks': weeks_back,
        'weeks_with_data': weeks_with_data,
        'weekly_average': weekly_average,
        'daily_average': daily_average,
        'total_spent': total_spent,
        'transaction_count': transaction_count,
        'weekly_breakdown': weekly_totals,
        'weekly_transaction_counts': weekly_counts
    }

def determine_time_granularity(weeks_back=4):
    """
    Determine the appropriate time granularity (daily or weekly) based on available data.
    
    Returns:
        dict with keys: 'granularity' ('daily' or 'weekly'), 'reason', 'data_range_days'
    """
    invoices = get_weekly_data(weeks_back)
    
    if not invoices:
        return {
            'granularity': 'daily',
            'reason': 'no_data',
            'data_range_days': 0,
            'sufficient_for_trend': False
        }
    
    # Find date range
    dates = []
    for invoice in invoices:
        date_to_use = parse_invoice_date(invoice['invoice_date'])
        if date_to_use:
            dates.append(date_to_use)
    
    if not dates:
        return {
            'granularity': 'daily',
            'reason': 'no_valid_dates',
            'data_range_days': 0,
            'sufficient_for_trend': False
        }
    
    date_range_days = (max(dates) - min(dates)).days + 1
    unique_weeks = len(set(d.strftime("%Y-%W") for d in dates))
    unique_days = len(set(d.strftime("%Y-%m-%d") for d in dates))
    
    # Decision logic
    if date_range_days < 14 or unique_weeks < 2:
        # Use daily granularity for short ranges
        return {
            'granularity': 'daily',
            'reason': 'short_range',
            'data_range_days': date_range_days,
            'unique_days': unique_days,
            'sufficient_for_trend': unique_days >= 3
        }
    else:
        # Use weekly granularity for longer ranges
        return {
            'granularity': 'weekly',
            'reason': 'sufficient_range',
            'data_range_days': date_range_days,
            'unique_weeks': unique_weeks,
            'sufficient_for_trend': unique_weeks >= 2
        }

def analyze_daily_trends(weeks_back=4):
    """Analyze spending trends on a daily basis."""
    daily_data = calculate_daily_totals(weeks_back)
    daily_breakdown = daily_data['daily_breakdown']
    
    if len(daily_breakdown) < 2:
        return {
            'trend': 'insufficient_data',
            'trend_percentage': 0,
            'granularity': 'daily',
            'message': 'Need at least 2 days of data for trend analysis'
        }
    
    # Sort days chronologically
    sorted_days = sorted(daily_breakdown.items())
    
    # Calculate trend using last 2 data points
    if len(sorted_days) >= 2:
        recent_days = sorted_days[-2:]  # Last 2 days
        old_avg = recent_days[0][1]['total']
        new_avg = recent_days[1][1]['total']
        
        if old_avg > 0:
            trend_percentage = ((new_avg - old_avg) / old_avg) * 100
        else:
            trend_percentage = 0
        
        if trend_percentage > 10:
            trend = 'increasing'
        elif trend_percentage < -10:
            trend = 'decreasing'
        else:
            trend = 'stable'
    else:
        trend = 'stable'
        trend_percentage = 0
    
    return {
        'trend': trend,
        'trend_percentage': trend_percentage,
        'granularity': 'daily',
        'daily_data': sorted_days,
        'message': f'Spending is {trend} ({trend_percentage:+.1f}% change)'
    }

def analyze_spending_trends(weeks_back=4):
    """Analyze spending trends over time."""
    weekly_data = calculate_weekly_averages(weeks_back)
    weekly_breakdown = weekly_data['weekly_breakdown']
    
    if len(weekly_breakdown) < 2:
        return {
            'trend': 'insufficient_data',
            'trend_percentage': 0,
            'granularity': 'weekly',
            'message': 'Need at least 2 weeks of data for trend analysis'
        }
    
    # Sort weeks chronologically
    sorted_weeks = sorted(weekly_breakdown.items())
    
    # Calculate trend
    if len(sorted_weeks) >= 2:
        recent_weeks = sorted_weeks[-2:]  # Last 2 weeks
        old_avg = recent_weeks[0][1]['total']
        new_avg = recent_weeks[1][1]['total']
        
        if old_avg > 0:
            trend_percentage = ((new_avg - old_avg) / old_avg) * 100
        else:
            trend_percentage = 0
        
        if trend_percentage > 10:
            trend = 'increasing'
        elif trend_percentage < -10:
            trend = 'decreasing'
        else:
            trend = 'stable'
    else:
        trend = 'stable'
        trend_percentage = 0
    
    return {
        'trend': trend,
        'trend_percentage': trend_percentage,
        'granularity': 'weekly',
        'weekly_data': sorted_weeks,
        'message': f'Spending is {trend} ({trend_percentage:+.1f}% change)'
    }

def find_biggest_spending_categories(weeks_back=4):
    """Find biggest spending by shop/category."""
    invoices = get_weekly_data(weeks_back)
    
    if not invoices:
        return {
            'by_shop': [],
            'by_amount': [],
            'highest_single_transaction': None
        }
    
    # Group by shop
    shop_totals = {}
    
    for invoice in invoices:
        shop_name = invoice['shop_name'] or 'Unknown'
        if shop_name not in shop_totals:
            shop_totals[shop_name] = {
                'total': 0,
                'count': 0,
                'invoices': []
            }
        
        shop_totals[shop_name]['total'] += invoice['total_amount']
        shop_totals[shop_name]['count'] += 1
        shop_totals[shop_name]['invoices'].append(invoice)
    
    # Sort by total spending
    by_shop = []
    for shop, data in shop_totals.items():
        by_shop.append({
            'shop_name': shop,
            'total_amount': data['total'],
            'transaction_count': data['count'],
            'average_per_transaction': data['total'] / data['count']
        })
    
    by_shop.sort(key=lambda x: x['total_amount'], reverse=True)
    
    # Sort all transactions by amount
    by_amount = []
    for invoice in invoices:
        by_amount.append({
            'shop_name': invoice['shop_name'] or 'Unknown',
            'amount': invoice['total_amount'],
            'date': invoice['invoice_date'] or 'Unknown',
            'invoice_date': invoice['invoice_date'] or 'Unknown'
        })
    
    by_amount.sort(key=lambda x: x['amount'], reverse=True)
    
    highest_single = by_amount[0] if by_amount else None
    
    return {
        'by_shop': by_shop,
        'by_amount': by_amount[:10],  # Top 10 transactions
        'highest_single_transaction': highest_single
    }

def analyze_item_spending(weeks_back=4):
    """Analyze spending by individual items."""
    invoices = get_weekly_data(weeks_back)
    
    if not invoices:
        return {
            'top_items': [],
            'total_items': 0
        }
    
    # Get items for all invoices in the period
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Get all items for invoices in the time period
        invoice_ids = [str(inv['id']) for inv in invoices]
        if not invoice_ids:
            return {
                'top_items': [],
                'total_items': 0
            }
        
        placeholders = ','.join(['?'] * len(invoice_ids))
        cursor.execute(f"""
            SELECT 
                ii.item_name,
                ii.quantity,
                ii.unit_price,
                ii.total_price,
                i.shop_name
            FROM invoice_items ii
            JOIN invoices i ON ii.invoice_id = i.id
            WHERE ii.invoice_id IN ({placeholders})
        """, invoice_ids)
        
        item_totals = {}
        
        for row in cursor.fetchall():
            item_name, quantity, unit_price, total_price, shop_name = row
            
            if item_name not in item_totals:
                item_totals[item_name] = {
                    'total': 0,
                    'count': 0,
                    'shops': set()
                }
            
            item_totals[item_name]['total'] += total_price or 0
            item_totals[item_name]['count'] += quantity or 1
            item_totals[item_name]['shops'].add(shop_name or 'Unknown')
        
        # Convert to list and sort
        top_items = []
        for item_name, data in item_totals.items():
            avg_price = data['total'] / data['count'] if data['count'] > 0 else 0
            top_items.append({
                'item_name': item_name,
                'total_spent': data['total'],
                'quantity_bought': data['count'],
                'average_price': avg_price,
                'shops_bought_from': list(data['shops'])
            })
        
        top_items.sort(key=lambda x: x['total_spent'], reverse=True)
        
        return {
            'top_items': top_items[:20],  # Top 20 items
            'total_unique_items': len(item_totals)
        }
    
    finally:
        conn.close()

def analyze_transaction_types(weeks_back=4):
    """Analyze spending by transaction type (bank, retail, e-commerce)."""
    invoices = get_weekly_data(weeks_back)
    
    if not invoices:
        return {
            'by_type': [],
            'total_by_type': {}
        }
    
    type_totals = {}
    type_counts = {}
    
    for invoice in invoices:
        trans_type = invoice['transaction_type'] or 'unknown'
        
        if trans_type not in type_totals:
            type_totals[trans_type] = 0
            type_counts[trans_type] = 0
            
        type_totals[trans_type] += invoice['total_amount']
        type_counts[trans_type] += 1
    
    # Convert to list format
    by_type = []
    for trans_type, total in type_totals.items():
        count = type_counts[trans_type]
        by_type.append({
            'transaction_type': trans_type,
            'total_amount': total,
            'transaction_count': count,
            'average_per_transaction': total / count if count > 0 else 0
        })
    
    by_type.sort(key=lambda x: x['total_amount'], reverse=True)
    
    return {
        'by_type': by_type,
        'total_by_type': type_totals
    }

def generate_comprehensive_analysis(weeks_back=4):
    """Generate a comprehensive financial analysis."""
    weekly_avg = calculate_weekly_averages(weeks_back)
    trends = analyze_spending_trends(weeks_back)
    spending_cats = find_biggest_spending_categories(weeks_back)
    item_analysis = analyze_item_spending(weeks_back)
    transaction_types = analyze_transaction_types(weeks_back)
    
    return {
        'period': f'Last {weeks_back} weeks',
        'summary': {
            'total_spent': weekly_avg['total_spent'],
            'weekly_average': weekly_avg['weekly_average'],
            'daily_average': weekly_avg['daily_average'],
            'transaction_count': weekly_avg['transaction_count']
        },
        'trends': trends,
        'top_spending': spending_cats,
        'item_analysis': item_analysis,
        'transaction_types': transaction_types,
        'insights': generate_insights(weekly_avg, trends, spending_cats, item_analysis, transaction_types)
    }

def generate_insights(weekly_avg, trends, spending_cats, item_analysis, transaction_types=None):
    """Generate key insights from the analysis."""
    insights = []
    
    # Spending level insights
    if weekly_avg['weekly_average'] > 1000000:  # 1 million rupiah
        insights.append("Your weekly spending is quite high (>Rp 1M/week)")
    elif weekly_avg['weekly_average'] < 200000:  # 200k rupiah
        insights.append("You have relatively low weekly spending (<Rp 200K/week)")
    
    # Trend insights
    if trends['trend'] == 'increasing':
        insights.append(f"Your spending is increasing by {trends['trend_percentage']:.1f}%")
    elif trends['trend'] == 'decreasing':
        insights.append(f"Good news! Your spending is decreasing by {abs(trends['trend_percentage']):.1f}%")
    
    # Top shop insights
    if spending_cats['by_shop']:
        top_shop = spending_cats['by_shop'][0]
        insights.append(f"Most spending at: {top_shop['shop_name']} (Rp {top_shop['total_amount']:,.0f})")
    
    # Transaction frequency insights
    if weekly_avg['transaction_count'] > 20:
        insights.append("You shop frequently (>20 transactions recently)")
    elif weekly_avg['transaction_count'] < 5:
        insights.append("You shop infrequently (<5 transactions recently)")
    
    # Transaction type insights
    if transaction_types and transaction_types['by_type']:
        top_type = transaction_types['by_type'][0]
        insights.append(f"Most spending via: {top_type['transaction_type']} (Rp {top_type['total_amount']:,.0f})")
    
    return insights
