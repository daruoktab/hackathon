
import argparse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .database import Invoice

def search_invoices(session, search_term, search_by):
    """Searches for invoices in the database."""
    if search_by == 'number':
        return session.query(Invoice).filter(Invoice.invoice_number.ilike(f'%{search_term}%')).all()
    elif search_by == 'date':
        return session.query(Invoice).filter(Invoice.invoice_date.ilike(f'%{search_term}%')).all()
    elif search_by == 'keyword':
        # This is a simple keyword search. For a more advanced search,
        # you would need to use a full-text search engine or a vector database.
        return session.query(Invoice).filter(
            (Invoice.invoice_number.ilike(f'%{search_term}%')) |
            (Invoice.invoice_date.ilike(f'%{search_term}%')) |
            (Invoice.total_amount.ilike(f'%{search_term}%'))
        ).all()
    else:
        return []

def main():
    """Main function to search for invoices."""
    parser = argparse.ArgumentParser(description='Search for invoices in the database.')
    parser.add_argument('search_term', type=str, help='The term to search for.')
    parser.add_argument('--by', type=str, choices=['number', 'date', 'keyword'], default='keyword',
                        help='The field to search by (number, date, or keyword).')
    args = parser.parse_args()

    engine = create_engine('sqlite:///..\\invoices.db')
    Session = sessionmaker(bind=engine)
    session = Session()

    invoices = search_invoices(session, args.search_term, args.by)

    if invoices:
        print(f"Found {len(invoices)} invoice(s):")
        for invoice in invoices:
            print(f"  - Invoice Number: {invoice.invoice_number}")
            print(f"    Invoice Date: {invoice.invoice_date}")
            print(f"    Total Amount: {invoice.total_amount}")
            print(f"    Image Path: {invoice.image_path}")
    else:
        print("No invoices found.")

if __name__ == '__main__':
    main()
