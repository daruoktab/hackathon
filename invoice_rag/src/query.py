
import argparse
from datetime import datetime, timedelta
from sqlalchemy import or_
from .database import Invoice, InvoiceItem, get_db_session
from . import analysis

def search_invoices(session, search_term, search_by):
    """Searches for invoices in the database."""
    if search_by == 'shop':
        return session.query(Invoice).filter(Invoice.shop_name.ilike(f'%{search_term}%')).all()
    elif search_by == 'number':
        return session.query(Invoice).filter(Invoice.invoice_number.ilike(f'%{search_term}%')).all()
    elif search_by == 'date':
        return session.query(Invoice).filter(Invoice.invoice_date.ilike(f'%{search_term}%')).all()
    elif search_by == 'amount':
        try:
            amount = float(search_term)
            return session.query(Invoice).filter(Invoice.total_amount == amount).all()
        except ValueError:
            return []
    elif search_by == 'keyword':
        # Search across multiple fields
        return session.query(Invoice).filter(
            or_(
                Invoice.shop_name.ilike(f'%{search_term}%'),
                Invoice.invoice_number.ilike(f'%{search_term}%'),
                Invoice.invoice_date.ilike(f'%{search_term}%'),
                Invoice.payment_method.ilike(f'%{search_term}%'),
                Invoice.cashier.ilike(f'%{search_term}%')
            )
        ).all()
    else:
        return []

def search_items(session, item_name):
    """Search for specific items across all invoices."""
    items = session.query(InvoiceItem).filter(InvoiceItem.name.ilike(f'%{item_name}%')).all()
    
    results = []
    for item in items:
        results.append({
            'item': item,
            'invoice': item.invoice
        })
    
    return results

def get_recent_invoices(session, days=7):
    """Get invoices from the last N days."""
    cutoff_date = datetime.now() - timedelta(days=days)
    return session.query(Invoice).filter(Invoice.processed_at >= cutoff_date).all()

def get_invoices_by_amount_range(session, min_amount, max_amount):
    """Get invoices within a specific amount range."""
    return session.query(Invoice).filter(
        Invoice.total_amount >= min_amount,
        Invoice.total_amount <= max_amount
    ).all()

def get_spending_by_shop(session, weeks_back=4):
    """Get spending breakdown by shop."""
    invoices = analysis.get_weekly_data(session, weeks_back)
    
    shop_totals = {}
    for invoice in invoices:
        if invoice.shop_name not in shop_totals:
            shop_totals[invoice.shop_name] = {
                'total': 0,
                'count': 0,
                'invoices': []
            }
        shop_totals[invoice.shop_name]['total'] += invoice.total_amount
        shop_totals[invoice.shop_name]['count'] += 1
        shop_totals[invoice.shop_name]['invoices'].append(invoice)
    
    return shop_totals

def display_invoice_details(invoice):
    """Display detailed invoice information."""
    print("\n📋 Invoice Details:")
    print(f"🏪 Shop: {invoice.shop_name}")
    print(f"📍 Address: {invoice.shop_address or 'N/A'}")
    print(f"🧾 Invoice #: {invoice.invoice_number or 'N/A'}")
    print(f"📅 Date: {invoice.invoice_date or 'N/A'}")
    print(f"🕐 Time: {invoice.invoice_time or 'N/A'}")
    print(f"💰 Total: Rp {invoice.total_amount:,.2f}")
    
    if invoice.subtotal:
        print(f"📊 Subtotal: Rp {invoice.subtotal:,.2f}")
    if invoice.tax:
        print(f"🏛️ Tax: Rp {invoice.tax:,.2f}")
    if invoice.discount:
        print(f"🎟️ Discount: Rp {invoice.discount:,.2f}")
    
    print(f"💳 Payment: {invoice.payment_method or 'N/A'}")
    print(f"👤 Cashier: {invoice.cashier or 'N/A'}")
    print(f"🕒 Processed: {invoice.processed_at.strftime('%Y-%m-%d %H:%M:%S') if invoice.processed_at else 'N/A'}")
    
    if invoice.items:
        print(f"\n🛒 Items ({len(invoice.items)}):")
        for i, item in enumerate(invoice.items, 1):
            print(f"  {i}. {item.name}")
            if item.quantity:
                print(f"     Qty: {item.quantity}")
            if item.unit_price:
                print(f"     Unit Price: Rp {item.unit_price:,.2f}")
            print(f"     Total: Rp {item.total_price:,.2f}")

def main():
    """Main function to query invoices."""
    parser = argparse.ArgumentParser(description='Query invoices and analyze spending.')
    parser.add_argument('--search', type=str, help='Search term')
    parser.add_argument('--by', type=str, choices=['shop', 'number', 'date', 'amount', 'keyword'], 
                       default='keyword', help='Search by field')
    parser.add_argument('--item', type=str, help='Search for specific item')
    parser.add_argument('--recent', type=int, help='Show invoices from last N days')
    parser.add_argument('--min-amount', type=float, help='Minimum amount filter')
    parser.add_argument('--max-amount', type=float, help='Maximum amount filter')
    parser.add_argument('--analysis', action='store_true', help='Show spending analysis')
    parser.add_argument('--shops', action='store_true', help='Show spending by shops')
    
    args = parser.parse_args()

    # Get database session
    session = get_db_session()
    
    try:
        if args.search:
            # Search for invoices
            invoices = search_invoices(session, args.search, args.by)
            
            if invoices:
                print(f"Found {len(invoices)} invoice(s):")
                for invoice in invoices:
                    display_invoice_details(invoice)
                    print("-" * 50)
            else:
                print("No invoices found.")
        
        elif args.item:
            # Search for items
            results = search_items(session, args.item)
            
            if results:
                print(f"Found '{args.item}' in {len(results)} invoice(s):")
                for result in results:
                    item = result['item']
                    invoice = result['invoice']
                    print(f"\n🛒 {item.name} - Rp {item.total_price:,.2f}")
                    print(f"   From: {invoice.shop_name}")
                    print(f"   Date: {invoice.invoice_date or 'N/A'}")
                    if item.quantity:
                        print(f"   Qty: {item.quantity}")
            else:
                print(f"Item '{args.item}' not found.")
        
        elif args.recent:
            # Show recent invoices
            invoices = get_recent_invoices(session, args.recent)
            
            if invoices:
                print(f"Invoices from last {args.recent} days ({len(invoices)} found):")
                for invoice in invoices:
                    print(f"\n🏪 {invoice.shop_name}: Rp {invoice.total_amount:,.2f}")
                    print(f"   Date: {invoice.processed_at.strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                print(f"No invoices found in the last {args.recent} days.")
        
        elif args.min_amount is not None or args.max_amount is not None:
            # Filter by amount range
            min_amt = args.min_amount or 0
            max_amt = args.max_amount or float('inf')
            
            invoices = get_invoices_by_amount_range(session, min_amt, max_amt)
            
            if invoices:
                print(f"Invoices between Rp {min_amt:,.2f} and Rp {max_amt:,.2f} ({len(invoices)} found):")
                for invoice in invoices:
                    print(f"\n🏪 {invoice.shop_name}: Rp {invoice.total_amount:,.2f}")
                    print(f"   Date: {invoice.invoice_date or 'N/A'}")
            else:
                print(f"No invoices found in the amount range Rp {min_amt:,.2f} - Rp {max_amt:,.2f}")
        
        elif args.analysis:
            # Show comprehensive analysis
            analysis_data = analysis.generate_comprehensive_analysis(session)
            
            print("📊 COMPREHENSIVE FINANCIAL ANALYSIS")
            print("=" * 50)
            print(f"Period: {analysis_data['period']}")
            print(f"Total Spent: Rp {analysis_data['summary']['total_spent']:,.2f}")
            print(f"Weekly Average: Rp {analysis_data['summary']['weekly_average']:,.2f}")
            print(f"Transaction Count: {analysis_data['summary']['transaction_count']}")
            
            print(f"\nTrend: {analysis_data['trends']['message']}")
            
            print("\nTop Spending by Shop:")
            for i, shop in enumerate(analysis_data['top_spending']['by_shop'][:5], 1):
                print(f"{i}. {shop['shop_name']}: Rp {shop['total_amount']:,.2f}")
            
            print("\nKey Insights:")
            for insight in analysis_data['insights']:
                print(f"• {insight}")
        
        elif args.shops:
            # Show spending by shops
            shop_totals = get_spending_by_shop(session)
            
            if shop_totals:
                print("🏪 SPENDING BY SHOP (Last 4 weeks)")
                print("=" * 40)
                
                sorted_shops = sorted(shop_totals.items(), key=lambda x: x[1]['total'], reverse=True)
                
                for shop_name, data in sorted_shops:
                    avg_per_transaction = data['total'] / data['count']
                    print(f"\n{shop_name}")
                    print(f"  Total: Rp {data['total']:,.2f}")
                    print(f"  Transactions: {data['count']}")
                    print(f"  Average per transaction: Rp {avg_per_transaction:,.2f}")
            else:
                print("No spending data found.")
        
        else:
            # Show all invoices summary
            all_invoices = session.query(Invoice).all()
            
            if all_invoices:
                total_amount = sum(inv.total_amount for inv in all_invoices)
                shops = set(inv.shop_name for inv in all_invoices)
                
                print("📊 DATABASE SUMMARY")
                print(f"Total invoices: {len(all_invoices)}")
                print(f"Total amount: Rp {total_amount:,.2f}")
                print(f"Unique shops: {len(shops)}")
                
                print("\nUse --help to see available options for detailed queries.")
            else:
                print("No invoices found in database.")
    
    finally:
        session.close()

if __name__ == '__main__':
    main()
