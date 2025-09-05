from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class InvoiceItem(BaseModel):
    name: str = Field(description="Name of the item")
    quantity: Optional[int] = Field(default=None, description="Quantity of the item")
    unit_price: Optional[float] = Field(default=None, description="Unit price of the item")
    total_price: float = Field(description="Total price for this item")

class IndonesianInvoice(BaseModel):
    shop_name: str = Field(description="Name of the shop/store")
    shop_address: Optional[str] = Field(default=None, description="Address of the shop")
    invoice_date: Optional[str] = Field(default=None, description="Date from the invoice")
    invoice_time: Optional[str] = Field(default=None, description="Time from the invoice")
    invoice_number: Optional[str] = Field(default=None, description="Invoice number")
    items: List[InvoiceItem] = Field(description="List of items in the invoice")
    subtotal: Optional[float] = Field(default=None, description="Subtotal amount")
    tax: Optional[float] = Field(default=None, description="Tax amount")
    discount: Optional[float] = Field(default=None, description="Discount amount")
    total_amount: float = Field(description="Total amount of the invoice")
    payment_method: Optional[str] = Field(default=None, description="Payment method used")
    cashier: Optional[str] = Field(default=None, description="Cashier name")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class FinancialAnalysis(BaseModel):
    period: str = Field(description="Analysis period")
    summary: dict = Field(description="Summary statistics")
    trends: dict = Field(description="Spending trends")
    top_spending: dict = Field(description="Top spending categories")
    item_analysis: dict = Field(description="Item-level analysis")
    insights: List[str] = Field(description="Key insights")

class FinancialAdvice(BaseModel):
    advice_type: str = Field(description="Type of advice (budgeting, saving, etc.)")
    title: str = Field(description="Title of the advice")
    description: str = Field(description="Detailed advice description")
    priority: str = Field(description="Priority level (high, medium, low)")
    action_items: List[str] = Field(description="Specific action items")
