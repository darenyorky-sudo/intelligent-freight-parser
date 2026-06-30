from pydantic import BaseModel, Field, field_validator
from typing import Optional

class InvoiceData(BaseModel):
    # Only fields are allowed inside the class
    invoice_number: Optional[str] = Field(None)
    date: Optional[str] = Field(None)
    total_amount: Optional[float] = Field(None)
    currency: Optional[str] = Field("KZT")
    sender_name: Optional[str] = Field(None)
    vendor_name: Optional[str] = Field(None)

    @field_validator('total_amount')
    @classmethod
    def validate_amount(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Total amount must be greater than zero")
        return v