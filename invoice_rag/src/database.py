
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Invoice(Base):
    __tablename__ = 'invoices'

    id = Column(Integer, primary_key=True)
    invoice_number = Column(String)
    invoice_date = Column(String)
    total_amount = Column(Float)
    image_path = Column(String)

    def __repr__(self):
        return f"<Invoice(invoice_number='{self.invoice_number}', invoice_date='{self.invoice_date}', total_amount='{self.total_amount}')>"

def get_db_session(db_path='invoices.db'):
    """Initializes the database and returns a session."""
    engine = create_engine(f'sqlite:///{db_path}')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

def insert_invoice_data(session, invoice_data, image_path):
    """Inserts extracted invoice data into the database."""
    try:
        invoice = Invoice(
            invoice_number=invoice_data.get('invoice_number'),
            invoice_date=invoice_data.get('invoice_date'),
            total_amount=float(invoice_data.get('total_amount')),
            image_path=image_path
        )
        session.add(invoice)
        session.commit()
        print(f"Successfully inserted invoice: {invoice.invoice_number}")
    except Exception as e:
        print(f"Error inserting invoice data: {e}")
        session.rollback()

def get_all_invoices(session):
    """Retrieves all invoices from the database."""
    return session.query(Invoice).all()

