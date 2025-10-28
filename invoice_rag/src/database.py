from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, BigInteger, Numeric, Boolean
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

class AccountStatus(str, Enum):
    """Account status enum for premium feature."""
    FREE = "Free"
    PREMIUM = "Premium"

class PremiumMethod(str, Enum):
    """Premium acquisition method enum."""
    PAYMENT = "payment"
    CLAIM_TOKEN = "claim token"

def get_default_db_path():
    """Get the absolute path to the main invoices.db file"""
    current_file = os.path.abspath(__file__)
    src_dir = os.path.dirname(current_file)
    invoice_rag_dir = os.path.dirname(src_dir)
    return os.path.join(invoice_rag_dir, 'invoices.db')

def is_supabase():
    """Check if using Supabase"""
    from dotenv import load_dotenv
    load_dotenv()
    return os.getenv("USE_SUPABASE", "false").lower() == "true"

class Invoice(Base):
    __tablename__ = 'invoices'

    # Use BigInteger for Supabase, Integer for SQLite
    id = Column(BigInteger if is_supabase() else Integer, primary_key=True)
    shop_name = Column(String(255), nullable=False)
    invoice_date = Column(String)  # Keep as String for compatibility
    total_amount = Column(Numeric(15, 2) if is_supabase() else Float, nullable=False)
    transaction_type = Column(String(50))
    processed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    image_path = Column(String)

    # Relationship to items
    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Invoice(shop_name='{self.shop_name}', total_amount='{self.total_amount}', date='{self.invoice_date}')>"

class InvoiceItem(Base):
    __tablename__ = 'invoice_items'

    id = Column(BigInteger if is_supabase() else Integer, primary_key=True)
    invoice_id = Column(BigInteger if is_supabase() else Integer, ForeignKey('invoices.id'), nullable=False)
    item_name = Column(String(500), nullable=False)
    quantity = Column(Integer)
    unit_price = Column(Numeric(15, 2) if is_supabase() else Float)
    total_price = Column(Numeric(15, 2) if is_supabase() else Float, nullable=False)
    
    # Relationship back to invoice
    invoice = relationship("Invoice", back_populates="items")

    def __repr__(self):
        return f"<InvoiceItem(item_name='{self.item_name}', total_price='{self.total_price}')>"

# Premium Feature Models
class User(Base):
    __tablename__ = 'user'

    id = Column(BigInteger if is_supabase() else Integer, primary_key=True)
    user_id = Column(String(255), unique=True, nullable=False)  # Telegram ID
    status_account = Column(String(20), nullable=False, default=AccountStatus.FREE)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    premium_data = relationship("PremiumData", back_populates="user", cascade="all, delete-orphan", uselist=False)

    def __repr__(self):
        return f"<User(user_id='{self.user_id}', status='{self.status_account}')>"

class PremiumData(Base):
    __tablename__ = 'premium_data'

    id = Column(BigInteger if is_supabase() else Integer, primary_key=True)
    user_id = Column(BigInteger if is_supabase() else Integer, ForeignKey('user.id'), unique=True, nullable=False)
    premium_for = Column(String(50), nullable=False)
    expired_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationship
    user = relationship("User", back_populates="premium_data")

    def __repr__(self):
        return f"<PremiumData(user_id={self.user_id}, expires={self.expired_at})>"

class Token(Base):
    __tablename__ = 'token'

    token = Column(String, primary_key=True)  # JWT string
    is_used = Column(Boolean, default=False, nullable=False)

    def __repr__(self):
        return f"<Token(used={self.is_used})>"

def get_db_session(db_path=None):
    """Creates a database session with the specified database."""
    try:
        from src.db_config import get_engine, USE_SUPABASE
        
        if db_path is not None and not USE_SUPABASE:
            # Legacy mode: specific SQLite database
            engine = create_engine(f'sqlite:///{db_path}')
        else:
            # Use unified config (supports both SQLite and Supabase)
            engine = get_engine()
        
        # Only create tables for SQLite (Supabase tables created via schema files)
        from src.db_config import USE_SUPABASE
        if not USE_SUPABASE:
            Base.metadata.create_all(engine)
        
        Session = sessionmaker(bind=engine)
        return Session()
    except ImportError:
        # Fallback to original SQLite-only behavior
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

# Premium Feature Functions

def get_or_create_user(session, telegram_user_id: str, default_status=AccountStatus.FREE):
    """
    Get existing user or create new one with Free status.
    
    Args:
        session: Database session
        telegram_user_id: Telegram user ID (as string)
        default_status: Default account status (Free or Premium)
    
    Returns:
        User object
    """
    user = session.query(User).filter_by(user_id=str(telegram_user_id)).first()
    
    if not user:
        user = User(
            user_id=str(telegram_user_id),
            status_account=default_status
        )
        session.add(user)
        session.commit()
    
    return user

def is_user_premium(session, telegram_user_id: str) -> bool:
    """
    Check if user has active premium subscription.
    
    Args:
        session: Database session
        telegram_user_id: Telegram user ID (as string)
    
    Returns:
        True if user has active premium, False otherwise
    """
    user = session.query(User).filter_by(user_id=str(telegram_user_id)).first()
    
    if not user or user.status_account != AccountStatus.PREMIUM:
        return False
    
    # Check if premium is expired
    premium_data = session.query(PremiumData).filter_by(user_id=user.id).first()
    
    if not premium_data:
        # User marked as premium but no premium_data record -> downgrade
        user.status_account = AccountStatus.FREE
        session.commit()
        return False
    
    # Check expiry
    now = datetime.now(timezone.utc)
    expired_at = premium_data.expired_at
    
    # Ensure expired_at has timezone info for comparison
    if expired_at.tzinfo is None:
        expired_at = expired_at.replace(tzinfo=timezone.utc)
    
    if now > expired_at:
        # Expired -> downgrade
        user.status_account = AccountStatus.FREE
        session.commit()
        return False
    
    return True

def activate_premium(session, telegram_user_id: str, method: str, duration_days: int):
    """
    Activate or extend premium subscription for a user.
    
    Args:
        session: Database session
        telegram_user_id: Telegram user ID (as string)
        method: 'payment' or 'claim token'
        duration_days: Number of days for premium access
    """
    # Get or create user
    user = get_or_create_user(session, telegram_user_id)
    
    # Calculate expiry date
    from datetime import timedelta
    expiry_date = datetime.now(timezone.utc) + timedelta(days=duration_days)
    
    # Upsert premium_data
    premium_data = session.query(PremiumData).filter_by(user_id=user.id).first()
    
    if premium_data:
        # Update existing
        premium_data.premium_for = method
        premium_data.expired_at = expiry_date
        premium_data.updated_at = datetime.now(timezone.utc)
    else:
        # Create new
        premium_data = PremiumData(
            user_id=user.id,
            premium_for=method,
            expired_at=expiry_date
        )
        session.add(premium_data)
    
    # Update user status to Premium
    user.status_account = AccountStatus.PREMIUM
    session.commit()

def is_token_used(session, jwt_token: str) -> bool:
    """
    Check if a JWT token has already been used.
    
    Args:
        session: Database session
        jwt_token: JWT token string
    
    Returns:
        True if token is used, False if available
    """
    token = session.query(Token).filter_by(token=jwt_token).first()
    return token.is_used if token else False

def mark_token_used(session, jwt_token: str):
    """
    Mark a JWT token as used.
    
    Args:
        session: Database session
        jwt_token: JWT token string
    """
    token = session.query(Token).filter_by(token=jwt_token).first()
    
    if token:
        token.is_used = True
    else:
        token = Token(token=jwt_token, is_used=True)
        session.add(token)
    
    session.commit()

