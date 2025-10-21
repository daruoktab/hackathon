"""
Database inspection and validation script
Compares database contents with the visualization
"""
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from src.database import get_db_session, Invoice, InvoiceItem  # noqa: E402

def format_currency(amount):
    """Format amount as Indonesian Rupiah"""
    if amount >= 1_000_000:
        return f"Rp {amount/1_000_000:.1f}M"
    elif amount >= 1_000:
        return f"Rp {amount/1_000:.0f}K"
    else:
        return f"Rp {amount:,.0f}"

def check_database():
    """Check database contents and compare with visualization"""
    print("=" * 70)
    print("DATABASE INSPECTION & VALIDATION")
    print("=" * 70)
    print()
    
    # Get database path
    from src.database import get_default_db_path
    db_path = get_default_db_path()
    print(f"📁 Database Location: {db_path}")
    
    if not os.path.exists(db_path):
        print("❌ Database file does not exist!")
        return
    
    # Get file size
    file_size = os.path.getsize(db_path)
    print(f"📊 Database Size: {file_size:,} bytes ({file_size/1024:.2f} KB)")
    print()
    
    # Get session
    session = get_db_session()
    
    # Count records
    total_invoices = session.query(Invoice).count()
    total_items = session.query(InvoiceItem).count()
    
    print("=" * 70)
    print("BASIC STATISTICS")
    print("=" * 70)
    print(f"Total Invoices: {total_invoices}")
    print(f"Total Items: {total_items}")
    print()
    
    if total_invoices == 0:
        print("❌ No invoices found in database!")
        session.close()
        return
    
    # Get all invoices
    invoices = session.query(Invoice).order_by(Invoice.processed_at.desc()).all()
    
    # Calculate totals - SQLAlchemy returns actual float values at runtime
    total_spent: float = sum(float(inv.total_amount) for inv in invoices)  # type: ignore[arg-type]
    avg_amount: float = total_spent / len(invoices) if invoices else 0.0
    
    print("=" * 70)
    print("FINANCIAL SUMMARY")
    print("=" * 70)
    print(f"💰 Total Spent: {format_currency(total_spent)} (Rp {total_spent:,.2f})")
    print(f"📊 Average Amount: {format_currency(avg_amount)} (Rp {avg_amount:,.2f})")
    print()
    
    # Compare with image
    print("=" * 70)
    print("COMPARISON WITH VISUALIZATION (from image)")
    print("=" * 70)
    
    # Expected values from the image
    expected_total = 0.8e6  # Rp 0.8M
    expected_count = 5
    expected_avg = 163e3  # Rp 163K
    
    # Check total spent
    print("Total Spent:")
    print(f"  Expected: {format_currency(expected_total)}")
    print(f"  Actual:   {format_currency(total_spent)}")
    if abs(total_spent - expected_total) < 1000:  # Within 1K tolerance
        print("  Status:   ✅ MATCH")
    else:
        diff = total_spent - expected_total
        print(f"  Status:   ⚠️  DIFFERENCE: {format_currency(abs(diff))} ({'more' if diff > 0 else 'less'})")
    print()
    
    # Check invoice count
    print("Invoice Count:")
    print(f"  Expected: {expected_count}")
    print(f"  Actual:   {total_invoices}")
    if total_invoices == expected_count:
        print("  Status:   ✅ MATCH")
    else:
        print(f"  Status:   ⚠️  DIFFERENCE: {abs(total_invoices - expected_count)} {'more' if total_invoices > expected_count else 'fewer'}")
    print()
    
    # Check average
    print("Average Amount:")
    print(f"  Expected: {format_currency(expected_avg)}")
    print(f"  Actual:   {format_currency(avg_amount)}")
    if abs(avg_amount - expected_avg) < 1000:  # Within 1K tolerance
        print("  Status:   ✅ MATCH")
    else:
        diff = avg_amount - expected_avg
        print(f"  Status:   ⚠️  DIFFERENCE: {format_currency(abs(diff))} ({'higher' if diff > 0 else 'lower'})")
    print()
    
    # Top vendors from image
    print("=" * 70)
    print("TOP VENDORS COMPARISON")
    print("=" * 70)
    
    expected_vendors = {
        "Harafan Jaya": 0.44e6,  # Rp 0.44M
        "PRIMA ATK": 0.2e6,      # Rp 0.2M
        "Metropolitan": 0.2e6,    # Rp 0.2M (approximately)
        "Cafe futur": 0.0e6,      # Rp 0.0M (shown but minimal)
    }
    
    # Get actual vendors
    from collections import defaultdict
    vendor_totals: dict[str, float] = defaultdict(float)
    for inv in invoices:
        # Type ignore for SQLAlchemy column access - returns str at runtime
        vendor_name = str(inv.shop_name) if inv.shop_name is not None else ""  # type: ignore[arg-type]
        vendor_totals[vendor_name] += float(inv.total_amount)  # type: ignore[arg-type]
    
    # Sort by amount
    sorted_vendors = sorted(vendor_totals.items(), key=lambda x: x[1], reverse=True)
    
    print("\nExpected (from image):")
    for vendor, amount in expected_vendors.items():
        print(f"  {vendor}: {format_currency(amount)}")
    
    print("\nActual (from database):")
    for vendor, amount in sorted_vendors:
        print(f"  {vendor}: {format_currency(amount)} (Rp {amount:,.2f})")
    
    # Check if top vendor matches
    print()
    if sorted_vendors:
        actual_top = sorted_vendors[0][0]
        expected_top = "Harafan Jaya"
        if actual_top.lower() == expected_top.lower() or expected_top.lower() in actual_top.lower():
            print(f"✅ Top vendor matches: {actual_top}")
        else:
            print("⚠️  Top vendor mismatch:")
            print(f"   Expected: {expected_top}")
            print(f"   Actual:   {actual_top}")
    
    print()
    print("=" * 70)
    print("DETAILED INVOICE LIST")
    print("=" * 70)
    print()
    
    for i, inv in enumerate(invoices, 1):
        print(f"#{i} - ID: {inv.id}")
        print(f"   📅 Date: {inv.invoice_date or 'Unknown'}")
        print(f"   🏢 Vendor: {inv.shop_name}")
        print(f"   💰 Amount: {format_currency(inv.total_amount)} (Rp {inv.total_amount:,.2f})")
        print(f"   🔖 Type: {inv.transaction_type or 'Unknown'}")
        print(f"   📸 Image: {inv.image_path or 'None'}")
        print(f"   ⏰ Processed: {inv.processed_at}")
        
        # Show items
        if inv.items:
            print(f"   📦 Items ({len(inv.items)}):")
            for item in inv.items:
                item_detail = f"      • {item.item_name}: {format_currency(item.total_price)}"
                if item.quantity:
                    item_detail += f" ({item.quantity}x"
                    if item.unit_price:
                        item_detail += f" @ {format_currency(item.unit_price)}"
                    item_detail += ")"
                print(item_detail)
        print()
    
    # Date range analysis
    print("=" * 70)
    print("DATE RANGE ANALYSIS")
    print("=" * 70)
    
    # Type ignore for SQLAlchemy column access - returns str | None at runtime
    dates_with_data = [inv for inv in invoices if inv.invoice_date is not None]  # type: ignore[arg-type]
    if dates_with_data:
        try:
            invoice_dates = [datetime.strptime(str(inv.invoice_date), "%Y-%m-%d") for inv in dates_with_data]  # type: ignore[arg-type]
            oldest = min(invoice_dates)
            newest = max(invoice_dates)
            date_range = (newest - oldest).days
            
            print("📅 Date Range:")
            print(f"   Oldest: {oldest.strftime('%Y-%m-%d')}")
            print(f"   Newest: {newest.strftime('%Y-%m-%d')}")
            print(f"   Span: {date_range} days")
            
            # Check if within last 8 weeks (56 days)
            weeks_8_ago = datetime.now() - timedelta(weeks=8)
            in_range = [d for d in invoice_dates if d >= weeks_8_ago]
            print(f"\n   Within Last 8 Weeks: {len(in_range)}/{len(invoice_dates)} invoices")
            
            if len(in_range) != len(invoice_dates):
                print(f"   ⚠️  Note: {len(invoice_dates) - len(in_range)} invoice(s) are older than 8 weeks")
        except ValueError as e:
            print(f"⚠️  Could not parse dates: {e}")
    else:
        print("⚠️  No invoices have date information")
    
    print()
    print("=" * 70)
    print("CATEGORY ANALYSIS")
    print("=" * 70)
    
    # Category distribution - type ignore for SQLAlchemy column access
    from collections import Counter
    categories = Counter(str(inv.transaction_type) for inv in invoices if inv.transaction_type is not None)  # type: ignore[arg-type]
    
    if categories:
        print("\nTransaction Types:")
        for cat, count in categories.most_common():
            percentage = (count / total_invoices) * 100
            print(f"  {cat.capitalize()}: {count} ({percentage:.1f}%)")
        
        # From image: 100% Retail
        retail_count = categories.get('retail', 0)
        if retail_count == total_invoices:
            print("\n✅ Matches image: 100% Retail")
        else:
            print("\n⚠️  Image shows 100% Retail, but actual distribution differs")
    else:
        print("⚠️  No transaction type information available")
    
    print()
    print("=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    print()
    
    issues = []
    
    if abs(total_spent - expected_total) >= 1000:
        issues.append(f"Total spent differs by {format_currency(abs(total_spent - expected_total))}")
    
    if total_invoices != expected_count:
        issues.append(f"Invoice count differs by {abs(total_invoices - expected_count)}")
    
    if abs(avg_amount - expected_avg) >= 1000:
        issues.append(f"Average amount differs by {format_currency(abs(avg_amount - expected_avg))}")
    
    if issues:
        print("⚠️  VALIDATION ISSUES FOUND:")
        for issue in issues:
            print(f"   • {issue}")
    else:
        print("✅ DATABASE MATCHES VISUALIZATION!")
        print("   All key metrics align with the analysis summary image.")
    
    print()
    session.close()

def main():
    """Main function"""
    try:
        check_database()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
