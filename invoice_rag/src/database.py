from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone
from enum import Enum
import os

Base = declarative_base()

class TransactionType(str, Enum):
    """Transaction type enum for validation."""
    BANK = "bank"
    RETAIL = "retail"
    E_COMMERCE = "e-commerce"

def get_default_db_path():
    """Get the absolute path to the main invoices.db file"""
    current_file = os.path.abspath(__file__)
    src_dir = os.path.dirname(current_file)
    invoice_rag_dir = os.path.dirname(src_dir)
    return os.path.join(invoice_rag_dir, 'invoices.db')

class Invoice(Base):
    __tablename__ = 'invoices'

    id = Column(Integer, primary_key=True)
    shop_name = Column(String, nullable=False)
    invoice_date = Column(String)  # Original date from invoice in YYYY-MM-DD format
    total_amount = Column(Float, nullable=False)
    transaction_type = Column(String)  # bank, retail, or e-commerce
    processed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    image_path = Column(String)

    # Relationship to items
    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Invoice(shop_name='{self.shop_name}', total_amount='{self.total_amount}', date='{self.invoice_date}')>"

class InvoiceItem(Base):
    __tablename__ = 'invoice_items'

    id = Column(Integer, primary_key=True)
    invoice_id = Column(Integer, ForeignKey('invoices.id'), nullable=False)
    item_name = Column(String, nullable=False)
    quantity = Column(Integer)
    unit_price = Column(Float)
    total_price = Column(Float, nullable=False)
    
    # Relationship back to invoice
    invoice = relationship("Invoice", back_populates="items")

    def __repr__(self):
        return f"<InvoiceItem(item_name='{self.item_name}', total_price='{self.total_price}')>"

def get_db_session(db_path=None):
    """Creates a database session with the specified database."""
    if db_path is None:
        db_path = get_default_db_path()
    engine = create_engine(f'sqlite:///{db_path}')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

def insert_invoice_data(session, invoice_data, image_path):
    """Inserts extracted invoice data (Pydantic model) into the database."""
    try:
        # Create invoice record
        invoice = Invoice(
            shop_name=invoice_data.shop_name,
            invoice_date=invoice_data.invoice_date,
            total_amount=float(invoice_data.total_amount),
            transaction_type=invoice_data.transaction_type,
            image_path=image_path
        )
        session.add(invoice)
        session.flush()  # This will assign an ID to the invoice
        
        # Create invoice items
        for item_data in invoice_data.items:
            item = InvoiceItem(
                invoice_id=invoice.id,
                item_name=item_data.name,
                quantity=item_data.quantity,
                unit_price=float(item_data.unit_price) if item_data.unit_price else None,
                total_price=float(item_data.total_price)
            )
            session.add(item)
        
        session.commit()
        print(f"Successfully inserted invoice from {invoice_data.shop_name}: Rp {invoice_data.total_amount:,.2f}")
        return invoice.id
    except Exception as e:
        print(f"Error inserting invoice data: {e}")
        session.rollback()
        return None

def get_all_invoices(session):
    """Retrieves all invoices from the database."""
    return session.query(Invoice).all()

def get_invoices_with_items(session):
    """Retrieves all invoices with their items."""
    invoices = session.query(Invoice).all()
    return [
        {
            'invoice': invoice,
            'items': invoice.items
        }
        for invoice in invoices
    ]
